"""
TeamReel Constitutional Compliance Report Generator

Generate structured compliance reports with actionable violation details and remediation guidance.

SE Principles Focus: Encapsulation (clean data structures) and Simplicity (clear, focused reporting)
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Violation:
    """
    Represents a single constitutional or quality gate violation.

    Encapsulation: Clean data structure with all violation details
    """

    principle: str  # SRP, Encapsulation, LooseCoupling, Reusability, Portability, Defensibility, Maintainability, Simplicity
    severity: str  # ERROR, WARNING, INFO
    message: str  # Human-readable violation description
    file_path: str  # Path to file containing violation
    line_number: Optional[int] = None  # Specific line number (if applicable)
    suggested_fix: str = ""  # Actionable remediation guidance
    rule_id: str = ""  # Reference to specific rule that was violated


@dataclass
class ComplianceReport:
    """
    Complete constitutional compliance report for a file or feature.

    Encapsulation: All compliance information in structured format
    Simplicity: Clear, focused data structure for easy consumption
    """

    compliance_status: str  # PASS, FAIL, WARNING
    violations: List[Violation]
    quality_gates: Dict[
        str, bool
    ]  # coverage_threshold, complexity_limit, security_scan
    metadata: Dict[str, Any]  # Additional context and statistics

    def to_json(self) -> str:
        """
        Convert compliance report to JSON format for tool consumption.

        Returns:
            JSON string representation of the report
        """
        # Convert dataclass to dictionary
        report_dict = asdict(self)

        # Add timestamp if not present
        if "timestamp" not in report_dict["metadata"]:
            report_dict["metadata"]["timestamp"] = datetime.now().isoformat()

        return json.dumps(report_dict, indent=2, ensure_ascii=False)

    def to_human_readable(self) -> str:
        """
        Convert compliance report to human-readable format for developers.

        Returns:
            Formatted string report suitable for console output
        """
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("TEAMREEL CONSTITUTIONAL COMPLIANCE REPORT")
        lines.append("=" * 60)
        lines.append("")

        # Overall status
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}.get(
            self.compliance_status, "❓"
        )

        lines.append(f"Overall Status: {status_icon} {self.compliance_status}")
        lines.append("")

        # File information
        if "file_path" in self.metadata:
            lines.append(f"File: {self.metadata['file_path']}")
        if "constitution_version" in self.metadata:
            lines.append(
                f"Constitution Version: {self.metadata['constitution_version']}"
            )
        lines.append("")

        # Summary statistics
        stats = self.get_summary_stats()
        lines.append("Summary:")
        lines.append(f"  Total Violations: {stats['total_violations']}")
        lines.append(f"  Errors: {stats['error_count']}")
        lines.append(f"  Warnings: {stats['warning_count']}")
        lines.append(f"  Info: {stats['info_count']}")
        lines.append("")

        # Quality gates status
        lines.append("Quality Gates:")
        for gate, passed in self.quality_gates.items():
            gate_icon = "✅" if passed else "❌"
            gate_name = gate.replace("_", " ").title()
            lines.append(f"  {gate_icon} {gate_name}")
        lines.append("")

        # Violations by severity
        if self.violations:
            lines.append("VIOLATIONS:")
            lines.append("-" * 40)

            # Group violations by severity
            errors = [v for v in self.violations if v.severity == "ERROR"]
            warnings = [v for v in self.violations if v.severity == "WARNING"]
            infos = [v for v in self.violations if v.severity == "INFO"]

            # Report errors first
            if errors:
                lines.append("")
                lines.append("🚨 ERRORS (Must Fix):")
                for i, violation in enumerate(errors, 1):
                    lines.extend(self._format_violation(violation, i))

            # Then warnings
            if warnings:
                lines.append("")
                lines.append("⚠️  WARNINGS (Should Fix):")
                for i, violation in enumerate(warnings, 1):
                    lines.extend(self._format_violation(violation, i))

            # Finally info
            if infos:
                lines.append("")
                lines.append("ℹ️  SUGGESTIONS (Consider):")
                for i, violation in enumerate(infos, 1):
                    lines.extend(self._format_violation(violation, i))

        else:
            lines.append(
                "🎉 No violations found! Code meets all constitutional requirements."
            )

        lines.append("")
        lines.append("=" * 60)

        return "\\n".join(lines)

    def _format_violation(self, violation: Violation, index: int) -> List[str]:
        """Format a single violation for human-readable output."""
        lines = []

        # Violation header
        location = (
            f"Line {violation.line_number}"
            if violation.line_number
            else "Unknown location"
        )
        lines.append(f"  {index}. [{violation.principle}] {location}")
        lines.append(f"     {violation.message}")

        if violation.rule_id:
            lines.append(f"     Rule: {violation.rule_id}")

        if violation.suggested_fix:
            lines.append(f"     💡 Fix: {violation.suggested_fix}")

        lines.append("")
        return lines

    def get_summary_stats(self) -> Dict[str, int]:
        """
        Calculate summary statistics for the compliance report.

        Returns:
            Dictionary with violation counts by severity and totals
        """
        stats = {
            "total_violations": len(self.violations),
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "unique_principles": set(),
            "failed_quality_gates": 0,
        }

        # Count violations by severity
        for violation in self.violations:
            if violation.severity == "ERROR":
                stats["error_count"] += 1
            elif violation.severity == "WARNING":
                stats["warning_count"] += 1
            elif violation.severity == "INFO":
                stats["info_count"] += 1

            stats["unique_principles"].add(violation.principle)

        # Count failed quality gates
        stats["failed_quality_gates"] = len(
            [gate for gate, passed in self.quality_gates.items() if not passed]
        )

        # Convert set to count
        stats["unique_principles"] = len(stats["unique_principles"])

        return stats

    def has_blocking_violations(self) -> bool:
        """
        Check if report contains any blocking (ERROR level) violations.

        Returns:
            True if there are ERROR level violations that should block deployment
        """
        return any(violation.severity == "ERROR" for violation in self.violations)

    def get_violations_by_principle(self) -> Dict[str, List[Violation]]:
        """
        Group violations by SE principle.

        Returns:
            Dictionary mapping principle names to lists of violations
        """
        grouped = {}

        for violation in self.violations:
            if violation.principle not in grouped:
                grouped[violation.principle] = []
            grouped[violation.principle].append(violation)

        return grouped

    def get_compliance_percentage(self) -> float:
        """
        Calculate overall compliance percentage.

        Returns:
            Percentage of passed quality gates and non-error violations
        """
        if not self.quality_gates and not self.violations:
            return 100.0

        # Quality gates score (50% weight)
        passed_gates = sum(1 for passed in self.quality_gates.values() if passed)
        total_gates = len(self.quality_gates) if self.quality_gates else 1
        gates_score = (passed_gates / total_gates) * 50

        # Violations score (50% weight) - only ERROR violations count against compliance
        error_violations = len([v for v in self.violations if v.severity == "ERROR"])
        # Assume max 10 potential violations for scoring
        max_violations = 10
        violations_score = (
            max(0, (max_violations - error_violations) / max_violations) * 50
        )

        return min(100.0, gates_score + violations_score)


class ComplianceReportGenerator:
    """
    Factory for generating compliance reports with different formats and options.

    Single Responsibility: Generate and format compliance reports
    """

    @staticmethod
    def create_report(
        file_path: str,
        violations: List[Violation],
        validation_scope: List[str],
        constitution_version: str = "1.1.0",
    ) -> ComplianceReport:
        """
        Create a compliance report from validation results.

        Args:
            file_path: Path to validated file
            violations: List of detected violations
            validation_scope: Scopes that were validated
            constitution_version: Version of constitution used

        Returns:
            Complete ComplianceReport instance
        """
        # Determine overall compliance status
        error_count = len([v for v in violations if v.severity == "ERROR"])
        warning_count = len([v for v in violations if v.severity == "WARNING"])

        if error_count > 0:
            compliance_status = "FAIL"
        elif warning_count > 0:
            compliance_status = "WARNING"
        else:
            compliance_status = "PASS"

        # Calculate quality gates status
        quality_gates = {
            "coverage_threshold": error_count == 0,
            "complexity_limit": len(
                [v for v in violations if "complexity" in v.message.lower()]
            )
            == 0,
            "security_scan": len(
                [v for v in violations if v.principle == "Defensibility"]
            )
            == 0,
            "naming_conventions": len(
                [v for v in violations if "naming" in v.message.lower()]
            )
            == 0,
        }

        # Generate metadata
        metadata = {
            "file_path": file_path,
            "validation_scope": validation_scope,
            "constitution_version": constitution_version,
            "timestamp": datetime.now().isoformat(),
            "tool_version": "constitutional-validator-1.0.0",
            "total_violations": len(violations),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": len([v for v in violations if v.severity == "INFO"]),
        }

        return ComplianceReport(
            compliance_status=compliance_status,
            violations=violations,
            quality_gates=quality_gates,
            metadata=metadata,
        )

    @staticmethod
    def create_batch_report(reports: List[ComplianceReport]) -> ComplianceReport:
        """
        Create a summary report from multiple individual file reports.

        Args:
            reports: List of individual file compliance reports

        Returns:
            Aggregated ComplianceReport for the entire batch
        """
        all_violations = []
        all_quality_gates = {}
        file_paths = []

        # Aggregate data from all reports
        for report in reports:
            all_violations.extend(report.violations)
            file_paths.append(report.metadata.get("file_path", "unknown"))

            # Merge quality gates (all must pass for batch to pass)
            for gate, status in report.quality_gates.items():
                if gate not in all_quality_gates:
                    all_quality_gates[gate] = True
                all_quality_gates[gate] = all_quality_gates[gate] and status

        # Determine batch compliance status
        error_count = len([v for v in all_violations if v.severity == "ERROR"])
        warning_count = len([v for v in all_violations if v.severity == "WARNING"])

        if error_count > 0:
            compliance_status = "FAIL"
        elif warning_count > 0:
            compliance_status = "WARNING"
        else:
            compliance_status = "PASS"

        # Batch metadata
        metadata = {
            "batch_type": "multi_file_validation",
            "file_count": len(reports),
            "file_paths": file_paths,
            "timestamp": datetime.now().isoformat(),
            "constitution_version": "1.1.0",
            "tool_version": "constitutional-validator-1.0.0",
            "total_violations": len(all_violations),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": len([v for v in all_violations if v.severity == "INFO"]),
        }

        return ComplianceReport(
            compliance_status=compliance_status,
            violations=all_violations,
            quality_gates=all_quality_gates,
            metadata=metadata,
        )
