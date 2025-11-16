"""
Unit tests for ComplianceReporter and related classes.

Tests report generation, formatting, and data structures.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
import sys

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from compliance_reporter import ComplianceReport, Violation


class TestViolation:
    """Test cases for Violation dataclass."""

    def test_violation_creation(self):
        """Test creating a violation instance."""
        violation = Violation(
            principle="SRP",
            severity="ERROR",
            message="Function has too many responsibilities",
            file_path="test.py",
            line_number=10,
            suggested_fix="Split function into smaller functions",
            rule_id="SRP001",
        )

        assert violation.principle == "SRP"
        assert violation.severity == "ERROR"
        assert violation.message == "Function has too many responsibilities"
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.suggested_fix == "Split function into smaller functions"
        assert violation.rule_id == "SRP001"

    def test_violation_optional_fields(self):
        """Test violation with optional fields."""
        violation = Violation(
            principle="SRP",
            severity="WARNING",
            message="Minor issue",
            file_path="test.py",
        )

        assert violation.line_number is None
        assert violation.suggested_fix == ""
        assert violation.rule_id == ""


class TestComplianceReport:
    """Test cases for ComplianceReport class."""

    def test_compliance_report_creation(self):
        """Test creating a compliance report."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Test violation",
                file_path="test.py",
                rule_id="SRP001",
            )
        ]

        quality_gates = {"coverage": True, "complexity": False}
        metadata = {"file_path": "test.py", "timestamp": "2025-11-15"}

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates=quality_gates,
            metadata=metadata,
        )

        assert report.compliance_status == "FAIL"
        assert len(report.violations) == 1
        assert report.quality_gates == quality_gates
        assert report.metadata == metadata

    def test_to_json(self):
        """Test JSON serialization of compliance report."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Test violation",
                file_path="test.py",
                line_number=5,
                suggested_fix="Fix this",
                rule_id="SRP001",
            )
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={"coverage": True},
            metadata={"file_path": "test.py"},
        )

        json_output = report.to_json()
        parsed_json = json.loads(json_output)

        assert parsed_json["compliance_status"] == "FAIL"
        assert len(parsed_json["violations"]) == 1
        assert parsed_json["violations"][0]["principle"] == "SRP"
        assert parsed_json["violations"][0]["severity"] == "ERROR"
        assert parsed_json["quality_gates"]["coverage"] is True
        assert "timestamp" in parsed_json["metadata"]

    def test_to_human_readable_pass(self):
        """Test human-readable format for passing report."""
        report = ComplianceReport(
            compliance_status="PASS",
            violations=[],
            quality_gates={"coverage": True, "complexity": True},
            metadata={"file_path": "test.py", "constitution_version": "v1.1.0"},
        )

        readable_output = report.to_human_readable()

        assert "✅ PASS" in readable_output
        assert "TEAMREEL CONSTITUTIONAL COMPLIANCE REPORT" in readable_output
        assert "File: test.py" in readable_output
        assert "Constitution Version: v1.1.0" in readable_output
        assert "Total Violations: 0" in readable_output

    def test_to_human_readable_fail(self):
        """Test human-readable format for failing report."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Critical SRP violation",
                file_path="test.py",
                line_number=10,
                suggested_fix="Split function",
                rule_id="SRP001",
            ),
            Violation(
                principle="Encapsulation",
                severity="WARNING",
                message="Minor encapsulation issue",
                file_path="test.py",
                line_number=20,
                rule_id="ENC001",
            ),
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={"coverage": False, "complexity": True},
            metadata={"file_path": "test.py"},
        )

        readable_output = report.to_human_readable()

        assert "❌ FAIL" in readable_output
        assert "Total Violations: 2" in readable_output
        assert "Errors: 1" in readable_output
        assert "Warnings: 1" in readable_output
        assert "Critical SRP violation" in readable_output
        assert "Minor encapsulation issue" in readable_output

    def test_to_human_readable_warning(self):
        """Test human-readable format for warning report."""
        violations = [
            Violation(
                principle="Maintainability",
                severity="WARNING",
                message="Consider adding documentation",
                file_path="test.py",
                line_number=5,
                rule_id="MAINT001",
            )
        ]

        report = ComplianceReport(
            compliance_status="WARNING",
            violations=violations,
            quality_gates={"coverage": True, "complexity": True},
            metadata={"file_path": "test.py"},
        )

        readable_output = report.to_human_readable()

        assert "⚠️ WARNING" in readable_output
        assert "Total Violations: 1" in readable_output
        assert "Consider adding documentation" in readable_output

    def test_get_summary_stats(self):
        """Test summary statistics calculation."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Error 1",
                file_path="test.py",
            ),
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Error 2",
                file_path="test.py",
            ),
            Violation(
                principle="Encapsulation",
                severity="WARNING",
                message="Warning 1",
                file_path="test.py",
            ),
            Violation(
                principle="Maintainability",
                severity="INFO",
                message="Info 1",
                file_path="test.py",
            ),
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={},
            metadata={},
        )

        stats = report.get_summary_stats()

        assert stats["total_violations"] == 4
        assert stats["error_count"] == 2
        assert stats["warning_count"] == 1
        assert stats["info_count"] == 1

    def test_get_violations_by_principle(self):
        """Test getting violations grouped by SE principle."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="SRP Error",
                file_path="test.py",
            ),
            Violation(
                principle="SRP",
                severity="WARNING",
                message="SRP Warning",
                file_path="test.py",
            ),
            Violation(
                principle="Encapsulation",
                severity="ERROR",
                message="Enc Error",
                file_path="test.py",
            ),
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={},
            metadata={},
        )

        violations_by_principle = report.get_violations_by_principle()

        assert len(violations_by_principle["SRP"]) == 2
        assert len(violations_by_principle["Encapsulation"]) == 1
        assert violations_by_principle["SRP"][0].message == "SRP Error"

    def test_get_violations_by_severity(self):
        """Test getting violations grouped by severity."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Error 1",
                file_path="test.py",
            ),
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Error 2",
                file_path="test.py",
            ),
            Violation(
                principle="Encapsulation",
                severity="WARNING",
                message="Warning 1",
                file_path="test.py",
            ),
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={},
            metadata={},
        )

        violations_by_severity = report.get_violations_by_severity()

        assert len(violations_by_severity["ERROR"]) == 2
        assert len(violations_by_severity["WARNING"]) == 1
        assert violations_by_severity["ERROR"][0].message == "Error 1"

    def test_has_blocking_violations(self):
        """Test checking for blocking (ERROR severity) violations."""
        # Report with blocking violations
        error_violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Critical error",
                file_path="test.py",
            )
        ]

        error_report = ComplianceReport(
            compliance_status="FAIL",
            violations=error_violations,
            quality_gates={},
            metadata={},
        )

        assert error_report.has_blocking_violations() is True

        # Report with only warnings
        warning_violations = [
            Violation(
                principle="SRP",
                severity="WARNING",
                message="Minor warning",
                file_path="test.py",
            )
        ]

        warning_report = ComplianceReport(
            compliance_status="WARNING",
            violations=warning_violations,
            quality_gates={},
            metadata={},
        )

        assert warning_report.has_blocking_violations() is False

        # Report with no violations
        clean_report = ComplianceReport(
            compliance_status="PASS", violations=[], quality_gates={}, metadata={}
        )

        assert clean_report.has_blocking_violations() is False

    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization."""
        original_violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Test violation",
                file_path="test.py",
                line_number=10,
                suggested_fix="Fix it",
                rule_id="SRP001",
            )
        ]

        original_report = ComplianceReport(
            compliance_status="FAIL",
            violations=original_violations,
            quality_gates={"coverage": True},
            metadata={"file_path": "test.py"},
        )

        # Serialize to JSON
        json_string = original_report.to_json()

        # Parse JSON
        parsed_data = json.loads(json_string)

        # Verify data integrity
        assert parsed_data["compliance_status"] == "FAIL"
        assert len(parsed_data["violations"]) == 1
        assert parsed_data["violations"][0]["principle"] == "SRP"
        assert parsed_data["violations"][0]["severity"] == "ERROR"
        assert parsed_data["violations"][0]["line_number"] == 10

    def test_get_compliance_percentage(self):
        """Test compliance percentage calculation."""
        violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Error 1",
                file_path="test.py",
            ),
            Violation(
                principle="SRP",
                severity="WARNING",
                message="Warning 1",
                file_path="test.py",
            ),
        ]

        report = ComplianceReport(
            compliance_status="FAIL",
            violations=violations,
            quality_gates={},
            metadata={},
        )
        report.total_files_analyzed = 10  # Set after creation

        percentage = report.get_compliance_percentage()
        assert isinstance(percentage, float)
        assert 0.0 <= percentage <= 100.0

    def test_empty_report_edge_cases(self):
        """Test edge cases with empty report."""
        empty_report = ComplianceReport(
            compliance_status="PASS", violations=[], quality_gates={}, metadata={}
        )

        # Test various methods with empty data
        assert empty_report.get_summary_stats()["total_violations"] == 0
        assert empty_report.get_violations_by_principle() == {}
        assert empty_report.get_violations_by_severity() == {}
        assert not empty_report.has_blocking_violations()

        # Test JSON serialization of empty report
        json_data = empty_report.to_json()
        assert isinstance(json_data, str)

        # Test human readable format of empty report
        human_readable = empty_report.to_human_readable()
        assert "PASS" in human_readable or "✅" in human_readable

    def test_metadata_handling(self):
        """Test metadata field handling."""
        metadata = {
            "analysis_time": "2023-01-01T00:00:00Z",
            "config_version": "1.0.0",
            "environment": "test",
        }

        report = ComplianceReport(
            compliance_status="PASS",
            violations=[],
            quality_gates={"coverage": True},
            metadata=metadata,
        )

        # Test JSON serialization includes metadata
        json_data = report.to_json()
        parsed = json.loads(json_data)
        assert "metadata" in parsed
        assert parsed["metadata"]["config_version"] == "1.0.0"

        # Test human readable includes metadata
        human_readable = report.to_human_readable()
        assert isinstance(human_readable, str)

    def test_quality_gates_display(self):
        """Test quality gates display in human readable format."""
        quality_gates = {"coverage": True, "complexity": False, "security": True}

        report = ComplianceReport(
            compliance_status="WARNING",
            violations=[],
            quality_gates=quality_gates,
            metadata={},
        )

        human_readable = report.to_human_readable()

        # Should contain quality gates information
        assert "Quality Gates" in human_readable or "quality" in human_readable.lower()
        assert isinstance(human_readable, str)
        assert len(human_readable) > 0
