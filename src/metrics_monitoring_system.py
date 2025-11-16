#!/usr/bin/env python3
"""
Metrics Collection & Monitoring System - T040

Comprehensive metrics collection and monitoring for constitutional enforcement.
Tracks compliance metrics, performance data, and system health indicators.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import os
import sys
import asyncio
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union, NamedTuple
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from contextlib import contextmanager
from enum import Enum
import logging
import statistics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricValue(NamedTuple):
    """Metric value with metadata."""

    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = {}


@dataclass
class Metric:
    """Metric definition and current value."""

    name: str
    description: str
    metric_type: MetricType
    unit: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    values: deque = field(default_factory=lambda: deque(maxlen=1000))

    def add_value(self, value: Union[int, float], labels: Dict[str, str] = None):
        """Add a value to the metric."""
        metric_value = MetricValue(
            value=value, timestamp=datetime.utcnow(), labels=labels or {}
        )
        self.values.append(metric_value)

    def get_current_value(self) -> Optional[Union[int, float]]:
        """Get the most recent value."""
        if self.values:
            return self.values[-1].value
        return None

    def get_values_since(self, since: datetime) -> List[MetricValue]:
        """Get values since a specific timestamp."""
        return [v for v in self.values if v.timestamp >= since]


@dataclass
class Alert:
    """Alert definition."""

    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "> 80", "< 90", "== 0"
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    last_triggered: Optional[datetime] = None

    def should_trigger(self, metric_value: Union[int, float]) -> bool:
        """Check if alert should trigger."""
        if not self.enabled:
            return False

        # Check cooldown
        if self.last_triggered:
            cooldown_period = timedelta(minutes=self.cooldown_minutes)
            if datetime.utcnow() - self.last_triggered < cooldown_period:
                return False

        # Evaluate condition
        try:
            condition_met = eval(f"{metric_value} {self.condition}")
            return condition_met
        except Exception as e:
            logger.error(f"Error evaluating alert condition '{self.condition}': {e}")
            return False


@dataclass
class Dashboard:
    """Monitoring dashboard configuration."""

    name: str
    description: str
    metrics: List[str]
    refresh_interval: int = 30  # seconds
    charts: List[Dict[str, Any]] = field(default_factory=list)


class ConstitutionalMetricsCollector:
    """Main metrics collection and monitoring system."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize metrics collection system."""
        self.storage_dir = storage_dir or Path(__file__).parent.parent / "metrics"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.dashboards: Dict[str, Dashboard] = {}

        self.collection_interval = 10  # seconds
        self.collection_active = False
        self.collection_thread: Optional[threading.Thread] = None

        # Initialize built-in metrics and alerts
        self._initialize_constitutional_metrics()
        self._initialize_performance_metrics()
        self._initialize_system_metrics()
        self._initialize_alerts()
        self._initialize_dashboards()

    def _initialize_constitutional_metrics(self):
        """Initialize constitutional compliance metrics."""

        # Quality gate metrics
        self.register_metric(
            "quality_gates_total_runs",
            "Total number of quality gate runs",
            MetricType.COUNTER,
            "runs",
        )

        self.register_metric(
            "quality_gates_passed",
            "Number of quality gates that passed",
            MetricType.COUNTER,
            "runs",
        )

        self.register_metric(
            "quality_gates_failed",
            "Number of quality gates that failed",
            MetricType.COUNTER,
            "runs",
        )

        self.register_metric(
            "quality_gates_pass_rate",
            "Quality gates pass rate percentage",
            MetricType.GAUGE,
            "percent",
        )

        # Coverage metrics
        self.register_metric(
            "code_coverage_percentage",
            "Code coverage percentage",
            MetricType.GAUGE,
            "percent",
        )

        self.register_metric(
            "code_coverage_lines_covered",
            "Number of lines covered by tests",
            MetricType.GAUGE,
            "lines",
        )

        self.register_metric(
            "code_coverage_lines_total",
            "Total number of lines",
            MetricType.GAUGE,
            "lines",
        )

        # Complexity metrics
        self.register_metric(
            "code_complexity_average",
            "Average code complexity",
            MetricType.GAUGE,
            "complexity",
        )

        self.register_metric(
            "code_complexity_violations",
            "Number of complexity violations",
            MetricType.GAUGE,
            "violations",
        )

        # Security metrics
        self.register_metric(
            "security_vulnerabilities_total",
            "Total number of security vulnerabilities",
            MetricType.GAUGE,
            "vulnerabilities",
        )

        self.register_metric(
            "security_vulnerabilities_critical",
            "Number of critical security vulnerabilities",
            MetricType.GAUGE,
            "vulnerabilities",
        )

        self.register_metric(
            "security_vulnerabilities_high",
            "Number of high severity vulnerabilities",
            MetricType.GAUGE,
            "vulnerabilities",
        )

        # Constitutional principle metrics
        self.register_metric(
            "constitutional_violations_total",
            "Total constitutional principle violations",
            MetricType.GAUGE,
            "violations",
        )

        self.register_metric(
            "srp_violations",
            "Single Responsibility Principle violations",
            MetricType.GAUGE,
            "violations",
        )

        self.register_metric(
            "maintainability_violations",
            "Maintainability violations",
            MetricType.GAUGE,
            "violations",
        )

        self.register_metric(
            "constitutional_compliance_score",
            "Overall constitutional compliance score",
            MetricType.GAUGE,
            "score",
        )

        # Template sync metrics
        self.register_metric(
            "template_drift_detected",
            "Number of templates with drift detected",
            MetricType.GAUGE,
            "templates",
        )

        self.register_metric(
            "template_sync_operations",
            "Number of template sync operations",
            MetricType.COUNTER,
            "operations",
        )

        self.register_metric(
            "template_sync_conflicts",
            "Number of template sync conflicts",
            MetricType.COUNTER,
            "conflicts",
        )

    def _initialize_performance_metrics(self):
        """Initialize performance metrics."""

        # Execution time metrics
        self.register_metric(
            "quality_gate_execution_time",
            "Quality gate execution time",
            MetricType.HISTOGRAM,
            "seconds",
        )

        self.register_metric(
            "coverage_analysis_time",
            "Coverage analysis execution time",
            MetricType.HISTOGRAM,
            "seconds",
        )

        self.register_metric(
            "security_scan_time",
            "Security scan execution time",
            MetricType.HISTOGRAM,
            "seconds",
        )

        self.register_metric(
            "constitutional_validation_time",
            "Constitutional validation execution time",
            MetricType.HISTOGRAM,
            "seconds",
        )

        # Throughput metrics
        self.register_metric(
            "validations_per_minute",
            "Number of validations per minute",
            MetricType.GAUGE,
            "validations/min",
        )

        self.register_metric(
            "files_processed_per_second",
            "Files processed per second",
            MetricType.GAUGE,
            "files/sec",
        )

        # Memory usage metrics
        self.register_metric(
            "memory_usage_mb", "Memory usage in megabytes", MetricType.GAUGE, "MB"
        )

        self.register_metric(
            "memory_peak_mb", "Peak memory usage in megabytes", MetricType.GAUGE, "MB"
        )

    def _initialize_system_metrics(self):
        """Initialize system-level metrics."""

        # CPU metrics
        self.register_metric(
            "cpu_usage_percent", "CPU usage percentage", MetricType.GAUGE, "percent"
        )

        # Disk metrics
        self.register_metric(
            "disk_usage_percent", "Disk usage percentage", MetricType.GAUGE, "percent"
        )

        self.register_metric(
            "disk_free_gb", "Free disk space in gigabytes", MetricType.GAUGE, "GB"
        )

        # Process metrics
        self.register_metric(
            "active_processes",
            "Number of active constitutional processes",
            MetricType.GAUGE,
            "processes",
        )

        # Error metrics
        self.register_metric(
            "errors_total", "Total number of errors", MetricType.COUNTER, "errors"
        )

        self.register_metric(
            "errors_per_minute", "Errors per minute", MetricType.GAUGE, "errors/min"
        )

    def _initialize_alerts(self):
        """Initialize alert definitions."""

        # Performance alerts
        self.register_alert(
            "high_quality_gate_execution_time",
            "Quality gate execution time is too high",
            "quality_gate_execution_time",
            "> 2.0",
            AlertSeverity.WARNING,
        )

        self.register_alert(
            "low_code_coverage",
            "Code coverage is below threshold",
            "code_coverage_percentage",
            "< 80",
            AlertSeverity.ERROR,
        )

        self.register_alert(
            "critical_security_vulnerabilities",
            "Critical security vulnerabilities detected",
            "security_vulnerabilities_critical",
            "> 0",
            AlertSeverity.CRITICAL,
        )

        self.register_alert(
            "high_constitutional_violations",
            "High number of constitutional violations",
            "constitutional_violations_total",
            "> 10",
            AlertSeverity.WARNING,
        )

        self.register_alert(
            "low_compliance_score",
            "Constitutional compliance score is low",
            "constitutional_compliance_score",
            "< 70",
            AlertSeverity.ERROR,
        )

        # System alerts
        self.register_alert(
            "high_cpu_usage",
            "CPU usage is high",
            "cpu_usage_percent",
            "> 80",
            AlertSeverity.WARNING,
        )

        self.register_alert(
            "high_memory_usage",
            "Memory usage is high",
            "memory_usage_mb",
            "> 500",
            AlertSeverity.WARNING,
        )

        self.register_alert(
            "low_disk_space",
            "Disk space is low",
            "disk_free_gb",
            "< 5",
            AlertSeverity.ERROR,
        )

        self.register_alert(
            "high_error_rate",
            "Error rate is high",
            "errors_per_minute",
            "> 5",
            AlertSeverity.ERROR,
        )

    def _initialize_dashboards(self):
        """Initialize monitoring dashboards."""

        # Constitutional compliance dashboard
        compliance_dashboard = Dashboard(
            name="constitutional_compliance",
            description="Constitutional Compliance Monitoring",
            metrics=[
                "quality_gates_pass_rate",
                "code_coverage_percentage",
                "security_vulnerabilities_total",
                "constitutional_violations_total",
                "constitutional_compliance_score",
            ],
            charts=[
                {
                    "title": "Quality Gates Pass Rate",
                    "type": "gauge",
                    "metric": "quality_gates_pass_rate",
                    "min": 0,
                    "max": 100,
                },
                {
                    "title": "Code Coverage",
                    "type": "gauge",
                    "metric": "code_coverage_percentage",
                    "min": 0,
                    "max": 100,
                },
                {
                    "title": "Security Vulnerabilities",
                    "type": "bar",
                    "metrics": [
                        "security_vulnerabilities_critical",
                        "security_vulnerabilities_high",
                    ],
                },
                {
                    "title": "Constitutional Violations Over Time",
                    "type": "line",
                    "metric": "constitutional_violations_total",
                    "time_range": "24h",
                },
            ],
        )

        # Performance dashboard
        performance_dashboard = Dashboard(
            name="performance_monitoring",
            description="Performance Monitoring",
            metrics=[
                "quality_gate_execution_time",
                "validations_per_minute",
                "memory_usage_mb",
                "cpu_usage_percent",
            ],
            charts=[
                {
                    "title": "Execution Times",
                    "type": "histogram",
                    "metrics": [
                        "quality_gate_execution_time",
                        "coverage_analysis_time",
                        "security_scan_time",
                    ],
                },
                {
                    "title": "System Resources",
                    "type": "multi_gauge",
                    "metrics": [
                        "cpu_usage_percent",
                        "memory_usage_mb",
                        "disk_usage_percent",
                    ],
                },
                {
                    "title": "Throughput",
                    "type": "line",
                    "metric": "validations_per_minute",
                    "time_range": "1h",
                },
            ],
        )

        # System health dashboard
        health_dashboard = Dashboard(
            name="system_health",
            description="System Health Monitoring",
            metrics=[
                "active_processes",
                "errors_per_minute",
                "disk_free_gb",
                "template_drift_detected",
            ],
            charts=[
                {
                    "title": "System Health Status",
                    "type": "status_grid",
                    "metrics": [
                        "active_processes",
                        "errors_per_minute",
                        "disk_free_gb",
                    ],
                },
                {
                    "title": "Error Rate Over Time",
                    "type": "line",
                    "metric": "errors_per_minute",
                    "time_range": "6h",
                },
                {
                    "title": "Template Management",
                    "type": "bar",
                    "metrics": ["template_drift_detected", "template_sync_conflicts"],
                },
            ],
        )

        self.dashboards = {
            "constitutional_compliance": compliance_dashboard,
            "performance_monitoring": performance_dashboard,
            "system_health": health_dashboard,
        }

    def register_metric(
        self,
        name: str,
        description: str,
        metric_type: MetricType,
        unit: str = "",
        labels: Dict[str, str] = None,
    ) -> Metric:
        """Register a new metric."""
        metric = Metric(
            name=name,
            description=description,
            metric_type=metric_type,
            unit=unit,
            labels=labels or {},
        )

        self.metrics[name] = metric
        logger.info(f"📊 Registered metric: {name}")

        return metric

    def register_alert(
        self,
        name: str,
        description: str,
        metric_name: str,
        condition: str,
        severity: AlertSeverity,
        cooldown_minutes: int = 5,
    ) -> Alert:
        """Register a new alert."""
        alert = Alert(
            name=name,
            description=description,
            metric_name=metric_name,
            condition=condition,
            severity=severity,
            cooldown_minutes=cooldown_minutes,
        )

        self.alerts[name] = alert
        logger.info(f"🚨 Registered alert: {name}")

        return alert

    def record_metric(
        self, name: str, value: Union[int, float], labels: Dict[str, str] = None
    ):
        """Record a metric value."""
        if name not in self.metrics:
            logger.warning(f"Metric '{name}' not registered")
            return

        metric = self.metrics[name]
        metric.add_value(value, labels)

        # Check alerts for this metric
        self._check_alerts_for_metric(name, value)

    def increment_counter(
        self, name: str, amount: Union[int, float] = 1, labels: Dict[str, str] = None
    ):
        """Increment a counter metric."""
        if name not in self.metrics:
            logger.warning(f"Counter metric '{name}' not registered")
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.COUNTER:
            logger.warning(f"Metric '{name}' is not a counter")
            return

        current = metric.get_current_value() or 0
        new_value = current + amount
        self.record_metric(name, new_value, labels)

    def set_gauge(
        self, name: str, value: Union[int, float], labels: Dict[str, str] = None
    ):
        """Set a gauge metric value."""
        if name not in self.metrics:
            logger.warning(f"Gauge metric '{name}' not registered")
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.GAUGE:
            logger.warning(f"Metric '{name}' is not a gauge")
            return

        self.record_metric(name, value, labels)

    @contextmanager
    def timer_metric(self, name: str, labels: Dict[str, str] = None):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.record_metric(name, duration, labels)

    def _check_alerts_for_metric(self, metric_name: str, value: Union[int, float]):
        """Check alerts for a specific metric."""
        for alert_name, alert in self.alerts.items():
            if alert.metric_name == metric_name:
                if alert.should_trigger(value):
                    self._trigger_alert(alert, value)

    def _trigger_alert(self, alert: Alert, value: Union[int, float]):
        """Trigger an alert."""
        alert.last_triggered = datetime.utcnow()

        alert_data = {
            "alert_name": alert.name,
            "description": alert.description,
            "metric_name": alert.metric_name,
            "current_value": value,
            "condition": alert.condition,
            "severity": alert.severity.value,
            "timestamp": alert.last_triggered.isoformat() + "Z",
        }

        # Log the alert
        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.ERROR: "❌",
            AlertSeverity.CRITICAL: "🚨",
        }

        emoji = severity_emoji.get(alert.severity, "🔔")
        logger.warning(
            f"{emoji} ALERT: {alert.name} - {alert.description} (Value: {value})"
        )

        # Save alert to file
        self._save_alert(alert_data)

        # In a real system, this would send notifications (email, Slack, etc.)
        self._send_alert_notification(alert_data)

    def _save_alert(self, alert_data: Dict[str, Any]):
        """Save alert to file."""
        alerts_file = self.storage_dir / "alerts.jsonl"

        with open(alerts_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert_data) + "\n")

    def _send_alert_notification(self, alert_data: Dict[str, Any]):
        """Send alert notification (mock implementation)."""
        # In a real system, this would integrate with notification systems
        logger.info(f"📢 Alert notification sent: {alert_data['alert_name']}")

    def start_collection(self):
        """Start automatic metrics collection."""
        if self.collection_active:
            logger.warning("Metrics collection is already active")
            return

        self.collection_active = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, daemon=True
        )
        self.collection_thread.start()

        logger.info(
            f"📊 Started metrics collection (interval: {self.collection_interval}s)"
        )

    def stop_collection(self):
        """Stop automatic metrics collection."""
        if not self.collection_active:
            logger.warning("Metrics collection is not active")
            return

        self.collection_active = False

        if self.collection_thread:
            self.collection_thread.join(timeout=5)

        logger.info("📊 Stopped metrics collection")

    def _collection_loop(self):
        """Main metrics collection loop."""
        while self.collection_active:
            try:
                self._collect_system_metrics()
                self._collect_performance_metrics()
                self._calculate_derived_metrics()

                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval)

    def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.set_gauge("cpu_usage_percent", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            self.set_gauge("memory_usage_mb", memory_mb)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)

            self.set_gauge("disk_usage_percent", disk_percent)
            self.set_gauge("disk_free_gb", disk_free_gb)

            # Process count (mock - in real system would count actual processes)
            process_count = len(
                [
                    p
                    for p in psutil.process_iter()
                    if "constitutional" in p.name().lower()
                ]
            )
            self.set_gauge(
                "active_processes", max(process_count, 1)
            )  # At least 1 (this process)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _collect_performance_metrics(self):
        """Collect performance metrics."""
        try:
            # Calculate validations per minute based on recent activity
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)

            # Count recent quality gate runs
            qg_metric = self.metrics.get("quality_gates_total_runs")
            if qg_metric:
                recent_runs = len(qg_metric.get_values_since(minute_ago))
                self.set_gauge("validations_per_minute", recent_runs)

            # Calculate errors per minute
            error_metric = self.metrics.get("errors_total")
            if error_metric:
                recent_errors = len(error_metric.get_values_since(minute_ago))
                self.set_gauge("errors_per_minute", recent_errors)

            # Mock file processing rate
            files_per_second = 10.5  # Would be calculated from actual processing
            self.set_gauge("files_processed_per_second", files_per_second)

        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")

    def _calculate_derived_metrics(self):
        """Calculate derived metrics from base metrics."""
        try:
            # Calculate quality gates pass rate
            total_runs = (
                self.metrics["quality_gates_total_runs"].get_current_value() or 0
            )
            passed_runs = self.metrics["quality_gates_passed"].get_current_value() or 0

            if total_runs > 0:
                pass_rate = (passed_runs / total_runs) * 100
                self.set_gauge("quality_gates_pass_rate", pass_rate)

            # Calculate constitutional compliance score
            # This is a composite score based on various factors
            coverage = self.metrics["code_coverage_percentage"].get_current_value() or 0
            violations = (
                self.metrics["constitutional_violations_total"].get_current_value() or 0
            )
            security_issues = (
                self.metrics["security_vulnerabilities_total"].get_current_value() or 0
            )

            # Simple scoring algorithm (can be made more sophisticated)
            score = max(0, min(100, coverage - violations - (security_issues * 5)))
            self.set_gauge("constitutional_compliance_score", score)

        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")

    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        if name not in self.metrics:
            return {}

        metric = self.metrics[name]
        values = [v.value for v in metric.values]

        if not values:
            return {
                "name": name,
                "description": metric.description,
                "type": metric.metric_type.value,
                "unit": metric.unit,
                "count": 0,
            }

        summary = {
            "name": name,
            "description": metric.description,
            "type": metric.metric_type.value,
            "unit": metric.unit,
            "count": len(values),
            "current": values[-1],
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
        }

        if len(values) > 1:
            summary["median"] = statistics.median(values)
            summary["stdev"] = statistics.stdev(values)

        return summary

    def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get data for a specific dashboard."""
        if dashboard_name not in self.dashboards:
            return {}

        dashboard = self.dashboards[dashboard_name]

        dashboard_data = {
            "name": dashboard.name,
            "description": dashboard.description,
            "refresh_interval": dashboard.refresh_interval,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "metrics": {},
            "charts": dashboard.charts,
        }

        # Get current values for all metrics
        for metric_name in dashboard.metrics:
            if metric_name in self.metrics:
                metric = self.metrics[metric_name]
                dashboard_data["metrics"][metric_name] = {
                    "current_value": metric.get_current_value(),
                    "unit": metric.unit,
                    "description": metric.description,
                }

        return dashboard_data

    def get_all_metrics_data(self) -> Dict[str, Any]:
        """Get data for all metrics."""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {name: self.get_metric_summary(name) for name in self.metrics},
        }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        active_alerts = []

        for alert_name, alert in self.alerts.items():
            if alert.enabled and alert.metric_name in self.metrics:
                metric = self.metrics[alert.metric_name]
                current_value = metric.get_current_value()

                if current_value is not None and alert.should_trigger(current_value):
                    active_alerts.append(
                        {
                            "name": alert.name,
                            "description": alert.description,
                            "metric_name": alert.metric_name,
                            "current_value": current_value,
                            "condition": alert.condition,
                            "severity": alert.severity.value,
                            "last_triggered": (
                                alert.last_triggered.isoformat() + "Z"
                                if alert.last_triggered
                                else None
                            ),
                        }
                    )

        return active_alerts

    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        all_data = self.get_all_metrics_data()

        if format.lower() == "json":
            return json.dumps(all_data, indent=2)
        elif format.lower() == "prometheus":
            return self._export_prometheus_format()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        prometheus_lines = []

        for name, metric in self.metrics.items():
            current_value = metric.get_current_value()
            if current_value is not None:
                # Add help line
                prometheus_lines.append(f"# HELP {name} {metric.description}")

                # Add type line
                prom_type = {
                    MetricType.COUNTER: "counter",
                    MetricType.GAUGE: "gauge",
                    MetricType.HISTOGRAM: "histogram",
                    MetricType.TIMER: "histogram",
                }.get(metric.metric_type, "gauge")

                prometheus_lines.append(f"# TYPE {name} {prom_type}")

                # Add metric value
                prometheus_lines.append(f"{name} {current_value}")

        return "\n".join(prometheus_lines)

    async def save_metrics_snapshot(self):
        """Save current metrics snapshot to file."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.storage_dir / f"metrics_snapshot_{timestamp}.json"

        snapshot_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": self.get_all_metrics_data(),
            "active_alerts": self.get_active_alerts(),
            "dashboards": {
                name: self.get_dashboard_data(name) for name in self.dashboards
            },
        }

        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)

        logger.info(f"📊 Metrics snapshot saved: {snapshot_file}")

        return str(snapshot_file)

    def generate_report(self, time_range: str = "24h") -> Dict[str, Any]:
        """Generate comprehensive metrics report."""
        report_time = datetime.utcnow()

        # Parse time range
        if time_range.endswith("h"):
            hours = int(time_range[:-1])
            since = report_time - timedelta(hours=hours)
        elif time_range.endswith("d"):
            days = int(time_range[:-1])
            since = report_time - timedelta(days=days)
        else:
            since = report_time - timedelta(hours=24)  # Default to 24h

        report = {
            "report_timestamp": report_time.isoformat() + "Z",
            "time_range": time_range,
            "since_timestamp": since.isoformat() + "Z",
            "summary": {},
            "key_metrics": {},
            "alerts_summary": {},
            "recommendations": [],
        }

        # Key metrics summary
        key_metrics = [
            "constitutional_compliance_score",
            "quality_gates_pass_rate",
            "code_coverage_percentage",
            "security_vulnerabilities_total",
            "constitutional_violations_total",
        ]

        for metric_name in key_metrics:
            if metric_name in self.metrics:
                report["key_metrics"][metric_name] = self.get_metric_summary(
                    metric_name
                )

        # Alert summary
        total_alerts = len(self.alerts)
        active_alerts = self.get_active_alerts()

        report["alerts_summary"] = {
            "total_alerts_configured": total_alerts,
            "active_alerts": len(active_alerts),
            "active_alert_details": active_alerts,
        }

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()

        # Overall summary
        compliance_score = (
            self.metrics.get("constitutional_compliance_score", {}).get_current_value()
            or 0
        )
        pass_rate = (
            self.metrics.get("quality_gates_pass_rate", {}).get_current_value() or 0
        )

        report["summary"] = {
            "overall_health": (
                "good"
                if compliance_score > 80 and pass_rate > 90
                else "needs_attention"
            ),
            "compliance_score": compliance_score,
            "quality_gate_pass_rate": pass_rate,
            "active_alerts_count": len(active_alerts),
            "critical_alerts": len(
                [a for a in active_alerts if a["severity"] == "critical"]
            ),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current metrics."""
        recommendations = []

        # Coverage recommendations
        coverage = (
            self.metrics.get("code_coverage_percentage", {}).get_current_value() or 0
        )
        if coverage < 80:
            recommendations.append(
                f"Code coverage is {coverage:.1f}%. Consider adding more tests to reach 80% threshold."
            )

        # Security recommendations
        critical_vulns = (
            self.metrics.get(
                "security_vulnerabilities_critical", {}
            ).get_current_value()
            or 0
        )
        if critical_vulns > 0:
            recommendations.append(
                f"Address {critical_vulns} critical security vulnerabilities immediately."
            )

        # Performance recommendations
        avg_exec_time = self.metrics.get("quality_gate_execution_time", {})
        if avg_exec_time.values:
            recent_times = [
                v.value for v in avg_exec_time.values[-10:]
            ]  # Last 10 values
            if recent_times and statistics.mean(recent_times) > 1.0:
                recommendations.append(
                    "Quality gate execution time is high. Consider optimizing validation processes."
                )

        # Constitutional recommendations
        violations = (
            self.metrics.get("constitutional_violations_total", {}).get_current_value()
            or 0
        )
        if violations > 5:
            recommendations.append(
                f"High number of constitutional violations ({violations}). Review code for SRP and maintainability issues."
            )

        # System recommendations
        memory_usage = self.metrics.get("memory_usage_mb", {}).get_current_value() or 0
        if memory_usage > 500:
            recommendations.append(
                f"High memory usage ({memory_usage:.1f}MB). Monitor for memory leaks."
            )

        return recommendations


# Example usage and testing functions
async def simulate_constitutional_activity(collector: ConstitutionalMetricsCollector):
    """Simulate constitutional enforcement activity for demonstration."""
    logger.info("🎭 Simulating constitutional enforcement activity...")

    # Simulate quality gate runs
    for i in range(5):
        collector.increment_counter("quality_gates_total_runs")

        # 80% pass rate
        if i < 4:
            collector.increment_counter("quality_gates_passed")
        else:
            collector.increment_counter("quality_gates_failed")

        # Simulate execution time
        execution_time = 0.5 + (i * 0.1)  # Gradually increasing time
        collector.record_metric("quality_gate_execution_time", execution_time)

        await asyncio.sleep(0.1)

    # Set some gauge values
    collector.set_gauge("code_coverage_percentage", 85.5)
    collector.set_gauge("code_complexity_average", 4.2)
    collector.set_gauge("security_vulnerabilities_total", 3)
    collector.set_gauge("security_vulnerabilities_critical", 0)
    collector.set_gauge("constitutional_violations_total", 7)
    collector.set_gauge("srp_violations", 3)
    collector.set_gauge("maintainability_violations", 4)

    # Simulate template activity
    collector.set_gauge("template_drift_detected", 2)
    collector.increment_counter("template_sync_operations", 3)
    collector.increment_counter("template_sync_conflicts", 1)

    logger.info("✅ Simulation completed")


async def main():
    """Main entry point for metrics system demonstration."""
    collector = ConstitutionalMetricsCollector()

    print("📊 Constitutional Metrics Collection & Monitoring System")
    print(f"📋 Registered metrics: {len(collector.metrics)}")
    print(f"🚨 Configured alerts: {len(collector.alerts)}")
    print(f"📈 Available dashboards: {len(collector.dashboards)}")

    # Start metrics collection
    collector.start_collection()

    try:
        # Simulate some activity
        await simulate_constitutional_activity(collector)

        # Wait a bit for collection
        await asyncio.sleep(2)

        # Display some results
        print(f"\n📊 Sample Metrics:")
        key_metrics = [
            "quality_gates_pass_rate",
            "code_coverage_percentage",
            "constitutional_compliance_score",
            "cpu_usage_percent",
        ]

        for metric_name in key_metrics:
            summary = collector.get_metric_summary(metric_name)
            if summary:
                current = summary.get("current", "N/A")
                unit = summary.get("unit", "")
                print(f"  • {metric_name}: {current}{unit}")

        # Check for active alerts
        active_alerts = collector.get_active_alerts()
        if active_alerts:
            print(f"\n🚨 Active Alerts ({len(active_alerts)}):")
            for alert in active_alerts[:3]:  # Show first 3
                print(f"  • {alert['name']}: {alert['description']}")
        else:
            print("\n✅ No active alerts")

        # Generate a report
        print(f"\n📋 Generating metrics report...")
        report = collector.generate_report("1h")
        print(f"📊 Overall Health: {report['summary']['overall_health']}")
        print(f"📈 Compliance Score: {report['summary']['compliance_score']:.1f}")

        if report["recommendations"]:
            print(f"\n💡 Recommendations ({len(report['recommendations'])}):")
            for rec in report["recommendations"][:2]:  # Show first 2
                print(f"  • {rec}")

        # Save a snapshot
        snapshot_file = await collector.save_metrics_snapshot()
        print(f"\n💾 Metrics snapshot saved: {Path(snapshot_file).name}")

    finally:
        # Stop collection
        collector.stop_collection()

    print("✅ Metrics collection and monitoring system ready!")


if __name__ == "__main__":
    asyncio.run(main())
