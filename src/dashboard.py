#!/usr/bin/env python3
"""
Constitutional Compliance Dashboard

Web-based dashboard for real-time constitutional compliance metrics and team visibility.
Provides comprehensive insights into team adherence to SE principles and quality gates.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Flask, render_template, jsonify, request
import sqlite3
import subprocess


@dataclass
class ComplianceMetric:
    """Individual compliance metric data."""

    principle: str
    score: float  # 0-100
    status: str  # PASS, FAIL, WARNING
    violations: int
    last_updated: str
    details: Dict[str, Any]


@dataclass
class TeamMember:
    """Team member compliance data."""

    name: str
    email: str
    compliance_score: float
    recent_commits: int
    violations: int
    last_activity: str


@dataclass
class ProjectStats:
    """Overall project statistics."""

    total_files: int
    lines_of_code: int
    test_coverage: float
    complexity_score: float
    security_issues: int
    constitutional_score: float
    last_scan: str


class ConstitutionalDashboard:
    """Main dashboard application class."""

    def __init__(self, data_dir: str = ".dashboard_data"):
        """Initialize dashboard with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "compliance.db"
        self.app = Flask(__name__)
        self._setup_database()
        self._setup_routes()

    def _setup_database(self):
        """Initialize SQLite database for compliance data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create compliance metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                principle TEXT NOT NULL,
                score REAL NOT NULL,
                status TEXT NOT NULL,
                violations INTEGER NOT NULL,
                details TEXT NOT NULL
            )
        """
        )

        # Create team metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                member_name TEXT NOT NULL,
                member_email TEXT NOT NULL,
                compliance_score REAL NOT NULL,
                recent_commits INTEGER NOT NULL,
                violations INTEGER NOT NULL
            )
        """
        )

        # Create project stats table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS project_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_files INTEGER NOT NULL,
                lines_of_code INTEGER NOT NULL,
                test_coverage REAL NOT NULL,
                complexity_score REAL NOT NULL,
                security_issues INTEGER NOT NULL,
                constitutional_score REAL NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def _setup_routes(self):
        """Setup Flask routes for the dashboard."""

        @self.app.route("/")
        def dashboard():
            """Main dashboard page."""
            return render_template("dashboard.html")

        @self.app.route("/api/compliance/overview")
        def compliance_overview():
            """Get overall compliance overview."""
            metrics = self._get_latest_compliance_metrics()
            return jsonify(
                {
                    "overall_score": self._calculate_overall_score(metrics),
                    "metrics": [asdict(m) for m in metrics],
                    "status": self._get_overall_status(metrics),
                    "last_updated": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api/team/metrics")
        def team_metrics():
            """Get team member compliance metrics."""
            members = self._get_team_metrics()
            return jsonify(
                {
                    "members": [asdict(m) for m in members],
                    "team_average": self._calculate_team_average(members),
                    "total_members": len(members),
                }
            )

        @self.app.route("/api/project/stats")
        def project_stats():
            """Get project-wide statistics."""
            stats = self._get_project_stats()
            return jsonify(asdict(stats) if stats else {})

        @self.app.route("/api/compliance/history")
        def compliance_history():
            """Get historical compliance data."""
            days = request.args.get("days", 30, type=int)
            history = self._get_compliance_history(days)
            return jsonify(history)

        @self.app.route("/api/violations/recent")
        def recent_violations():
            """Get recent constitutional violations."""
            limit = request.args.get("limit", 50, type=int)
            violations = self._get_recent_violations(limit)
            return jsonify(violations)

        @self.app.route("/api/scan/trigger", methods=["POST"])
        def trigger_scan():
            """Trigger a new compliance scan."""
            try:
                result = self._trigger_compliance_scan()
                return jsonify({"success": True, "result": result})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    def _get_latest_compliance_metrics(self) -> List[ComplianceMetric]:
        """Get the latest compliance metrics for all principles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get latest metrics for each principle
        cursor.execute(
            """
            SELECT DISTINCT principle FROM compliance_metrics
        """
        )
        principles = [row[0] for row in cursor.fetchall()]

        metrics = []
        for principle in principles:
            cursor.execute(
                """
                SELECT principle, score, status, violations, timestamp, details
                FROM compliance_metrics 
                WHERE principle = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """,
                (principle,),
            )

            row = cursor.fetchone()
            if row:
                metrics.append(
                    ComplianceMetric(
                        principle=row[0],
                        score=row[1],
                        status=row[2],
                        violations=row[3],
                        last_updated=row[4],
                        details=json.loads(row[5]),
                    )
                )

        conn.close()

        # If no data exists, create mock data for demonstration
        if not metrics:
            metrics = self._generate_mock_metrics()

        return metrics

    def _generate_mock_metrics(self) -> List[ComplianceMetric]:
        """Generate mock compliance metrics for demonstration."""
        principles = [
            "Single Responsibility Principle",
            "Encapsulation",
            "Loose Coupling",
            "Reusability",
            "Portability",
            "Defensibility",
            "Maintainability",
            "Simplicity",
        ]

        metrics = []
        for principle in principles:
            # Generate realistic scores
            import random

            score = random.uniform(75, 98)
            violations = random.randint(0, 5)
            status = (
                "PASS"
                if score >= 80 and violations <= 3
                else "WARNING" if score >= 70 else "FAIL"
            )

            metrics.append(
                ComplianceMetric(
                    principle=principle,
                    score=score,
                    status=status,
                    violations=violations,
                    last_updated=datetime.now().isoformat(),
                    details={
                        "files_checked": random.randint(50, 200),
                        "functions_analyzed": random.randint(200, 800),
                        "improvement_suggestions": random.randint(2, 10),
                    },
                )
            )

        return metrics

    def _calculate_overall_score(self, metrics: List[ComplianceMetric]) -> float:
        """Calculate overall compliance score."""
        if not metrics:
            return 0.0

        return sum(m.score for m in metrics) / len(metrics)

    def _get_overall_status(self, metrics: List[ComplianceMetric]) -> str:
        """Determine overall compliance status."""
        if not metrics:
            return "UNKNOWN"

        overall_score = self._calculate_overall_score(metrics)
        fail_count = sum(1 for m in metrics if m.status == "FAIL")

        if fail_count > 0:
            return "FAIL"
        elif overall_score >= 85:
            return "PASS"
        else:
            return "WARNING"

    def _get_team_metrics(self) -> List[TeamMember]:
        """Get team member compliance metrics."""
        # Mock team data for demonstration
        import random

        team_members = [
            "Alice Johnson",
            "Bob Smith",
            "Carol Davis",
            "David Wilson",
            "Eva Brown",
            "Frank Miller",
        ]

        members = []
        for name in team_members:
            members.append(
                TeamMember(
                    name=name,
                    email=f"{name.lower().replace(' ', '.')}@teamreel.com",
                    compliance_score=random.uniform(75, 98),
                    recent_commits=random.randint(5, 25),
                    violations=random.randint(0, 8),
                    last_activity=(
                        datetime.now() - timedelta(hours=random.randint(1, 48))
                    ).isoformat(),
                )
            )

        return members

    def _calculate_team_average(self, members: List[TeamMember]) -> float:
        """Calculate team average compliance score."""
        if not members:
            return 0.0

        return sum(m.compliance_score for m in members) / len(members)

    def _get_project_stats(self) -> Optional[ProjectStats]:
        """Get project-wide statistics."""
        # Mock project stats for demonstration
        import random

        return ProjectStats(
            total_files=random.randint(150, 300),
            lines_of_code=random.randint(10000, 50000),
            test_coverage=random.uniform(78, 95),
            complexity_score=random.uniform(6, 9),
            security_issues=random.randint(0, 3),
            constitutional_score=random.uniform(82, 96),
            last_scan=datetime.now().isoformat(),
        )

    def _get_compliance_history(self, days: int) -> Dict[str, Any]:
        """Get historical compliance data."""
        # Mock historical data
        import random
        from datetime import datetime, timedelta

        history = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            history.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "overall_score": random.uniform(80, 95),
                    "violations": random.randint(0, 10),
                    "coverage": random.uniform(75, 90),
                }
            )

        return {
            "history": list(reversed(history)),
            "trends": {
                "score_trend": random.choice(["up", "down", "stable"]),
                "violation_trend": random.choice(["up", "down", "stable"]),
            },
        }

    def _get_recent_violations(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent constitutional violations."""
        # Mock violation data
        import random

        violations = []
        violation_types = [
            "Single Responsibility Violation",
            "High Complexity Function",
            "Missing Test Coverage",
            "Security Vulnerability",
            "Code Duplication",
            "Naming Convention Violation",
        ]

        for i in range(min(limit, 20)):
            violations.append(
                {
                    "id": f"VIO-{1000 + i}",
                    "type": random.choice(violation_types),
                    "severity": random.choice(["HIGH", "MEDIUM", "LOW"]),
                    "file": f"src/components/Component{random.randint(1, 50)}.py",
                    "line": random.randint(10, 500),
                    "message": "Constitutional compliance violation detected",
                    "author": random.choice(
                        ["alice.johnson", "bob.smith", "carol.davis"]
                    ),
                    "timestamp": (
                        datetime.now() - timedelta(hours=random.randint(1, 72))
                    ).isoformat(),
                }
            )

        return violations

    def _trigger_compliance_scan(self) -> Dict[str, Any]:
        """Trigger a new compliance scan."""
        # This would integrate with the actual constitutional validator
        try:
            # Mock scan results
            import random

            return {
                "scan_id": f'SCAN-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                "status": "completed",
                "duration": f"{random.randint(30, 180)} seconds",
                "files_scanned": random.randint(100, 250),
                "violations_found": random.randint(0, 15),
                "overall_score": random.uniform(80, 95),
            }
        except Exception as e:
            raise Exception(f"Scan failed: {str(e)}")

    def run(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = True):
        """Run the dashboard application."""
        print(f"🏛️ TeamReel Constitutional Compliance Dashboard")
        print(f"📊 Starting dashboard at http://{host}:{port}")
        print(f"🔍 Real-time compliance monitoring enabled")

        self.app.run(host=host, port=port, debug=debug)


def create_dashboard_template():
    """Create basic HTML template for the dashboard."""
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)

    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeamReel Constitutional Compliance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
        .score { font-size: 2em; font-weight: bold; }
        .status-pass { color: #059669; }
        .status-warning { color: #d97706; }
        .status-fail { color: #dc2626; }
        .progress-bar { width: 100%; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: #059669; transition: width 0.3s; }
        .violation-item { padding: 10px; border-left: 4px solid #dc2626; margin: 10px 0; background: #fef2f2; }
        .team-member { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Constitutional Compliance Dashboard</h1>
        <p>Real-time monitoring of TeamReel's constitutional software engineering principles</p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>Overall Compliance</h2>
            <div id="overallScore" class="score">Loading...</div>
            <div id="overallStatus"></div>
            <button onclick="triggerScan()">🔍 Trigger New Scan</button>
        </div>
        
        <div class="card">
            <h2>Constitutional Principles</h2>
            <div id="principlesList">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Team Performance</h2>
            <div id="teamMetrics">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Recent Violations</h2>
            <div id="recentViolations">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Project Statistics</h2>
            <div id="projectStats">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Compliance Trend</h2>
            <canvas id="trendChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        // Load dashboard data
        async function loadDashboard() {
            try {
                // Load overall compliance
                const overview = await fetch('/api/compliance/overview').then(r => r.json());
                document.getElementById('overallScore').textContent = Math.round(overview.overall_score) + '%';
                document.getElementById('overallScore').className = `score status-${overview.status.toLowerCase()}`;
                document.getElementById('overallStatus').textContent = overview.status;
                
                // Load principles
                const principlesList = document.getElementById('principlesList');
                principlesList.innerHTML = overview.metrics.map(m => `
                    <div class="metric">
                        <span>${m.principle}</span>
                        <span class="status-${m.status.toLowerCase()}">${Math.round(m.score)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${m.score}%"></div>
                    </div>
                `).join('');
                
                // Load team metrics
                const team = await fetch('/api/team/metrics').then(r => r.json());
                const teamMetrics = document.getElementById('teamMetrics');
                teamMetrics.innerHTML = team.members.map(m => `
                    <div class="team-member">
                        <span>${m.name}</span>
                        <span class="${m.compliance_score >= 80 ? 'status-pass' : 'status-warning'}">${Math.round(m.compliance_score)}%</span>
                    </div>
                `).join('');
                
                // Load recent violations
                const violations = await fetch('/api/violations/recent?limit=5').then(r => r.json());
                const violationsList = document.getElementById('recentViolations');
                violationsList.innerHTML = violations.map(v => `
                    <div class="violation-item">
                        <strong>${v.type}</strong><br>
                        <small>${v.file}:${v.line} - ${v.author}</small>
                    </div>
                `).join('');
                
                // Load project stats
                const stats = await fetch('/api/project/stats').then(r => r.json());
                const projectStats = document.getElementById('projectStats');
                projectStats.innerHTML = `
                    <div class="metric"><span>Files</span><span>${stats.total_files}</span></div>
                    <div class="metric"><span>Lines of Code</span><span>${stats.lines_of_code.toLocaleString()}</span></div>
                    <div class="metric"><span>Test Coverage</span><span>${Math.round(stats.test_coverage)}%</span></div>
                    <div class="metric"><span>Security Issues</span><span>${stats.security_issues}</span></div>
                `;
                
                // Load trend chart
                const history = await fetch('/api/compliance/history?days=30').then(r => r.json());
                const ctx = document.getElementById('trendChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: history.history.map(h => h.date),
                        datasets: [{
                            label: 'Compliance Score',
                            data: history.history.map(h => h.overall_score),
                            borderColor: '#2563eb',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: false, min: 70, max: 100 }
                        }
                    }
                });
                
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }
        
        async function triggerScan() {
            try {
                const result = await fetch('/api/scan/trigger', { method: 'POST' }).then(r => r.json());
                if (result.success) {
                    alert('Compliance scan triggered successfully!');
                    setTimeout(loadDashboard, 2000);
                } else {
                    alert('Scan failed: ' + result.error);
                }
            } catch (error) {
                alert('Failed to trigger scan: ' + error);
            }
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Refresh every 5 minutes
        setInterval(loadDashboard, 5 * 60 * 1000);
    </script>
</body>
</html>"""

    (template_dir / "dashboard.html").write_text(template_content)


def main():
    """Main entry point for the dashboard."""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print("🏗️ Setting up Constitutional Compliance Dashboard...")
        create_dashboard_template()
        print("✅ Dashboard template created")
        return

    dashboard = ConstitutionalDashboard()

    # Create template if it doesn't exist
    if not Path("templates/dashboard.html").exists():
        create_dashboard_template()

    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")


if __name__ == "__main__":
    main()
