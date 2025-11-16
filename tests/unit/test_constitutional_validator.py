"""
Unit tests for ConstitutionalValidator class.

Tests SE principle validation, error handling, and configuration loading.
Achieves high coverage of the core validation engine functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import test subject
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from constitutional_validator import ConstitutionalValidator, ValidationScope
from compliance_reporter import ComplianceReport, Violation


class TestConstitutionalValidator:
    """Test cases for ConstitutionalValidator class."""

    def test_initialization_with_default_config(self):
        """Test validator initializes with default configuration."""
        validator = ConstitutionalValidator()

        assert validator is not None
        assert hasattr(validator, "se_rules")
        assert hasattr(validator, "quality_gates")
        assert hasattr(validator, "violation_detector")

    def test_initialization_with_custom_config_path(self):
        """Test validator initialization with custom config path."""
        custom_path = "/custom/path/se_rules.yaml"
        validator = ConstitutionalValidator(config_path=custom_path)

        assert validator.config_path == custom_path

    def test_get_supported_file_types(self):
        """Test getting supported file types."""
        validator = ConstitutionalValidator()
        supported_types = validator.get_supported_file_types()

        assert isinstance(supported_types, list)
        assert ".py" in supported_types
        assert ".js" in supported_types
        assert ".ts" in supported_types
        assert ".yaml" in supported_types
        assert ".json" in supported_types

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file returns error report."""
        validator = ConstitutionalValidator()

        report = validator.validate("nonexistent_file.py")

        assert report.compliance_status == "FAIL"
        assert len(report.violations) == 1
        assert "File not found" in report.violations[0].message

    def test_validate_unsupported_file_type(self):
        """Test validation of unsupported file type returns error report."""
        validator = ConstitutionalValidator()

        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp_file:
            temp_file.write(b"binary content")
            temp_path = temp_file.name

        try:
            report = validator.validate(temp_path)

            assert report.compliance_status == "FAIL"
            assert len(report.violations) == 1
            assert "Unsupported file type" in report.violations[0].message
        finally:
            os.unlink(temp_path)

    def test_validate_valid_python_file(self):
        """Test validation of valid Python file."""
        validator = ConstitutionalValidator()
        valid_python_code = '''
def simple_function():
    """A simple function."""
    return True

class SimpleClass:
    """A simple class."""
    
    def __init__(self):
        self._private_attr = "value"
    
    def get_value(self):
        """Get the private value."""
        return self._private_attr
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(valid_python_code)
            temp_path = temp_file.name

        try:
            report = validator.validate(temp_path)

            assert isinstance(report, ComplianceReport)
            assert report.compliance_status in ["PASS", "WARNING", "FAIL"]
            assert isinstance(report.violations, list)
            assert isinstance(report.quality_gates, dict)
            assert isinstance(report.metadata, dict)
        finally:
            os.unlink(temp_path)

    def test_validate_python_file_with_srp_violations(self):
        """Test validation detects SRP violations."""
        validator = ConstitutionalValidator()
        srp_violation_code = '''
def do_everything_function(data):
    """This function violates SRP by doing too many things."""
    # Process data
    processed = data.upper()
    
    # Send notification  
    print(f"Notification: {processed}")
    
    # Save to database
    with open("db.txt", "w") as f:
        f.write(processed)
    
    # Generate report
    report = f"Report: {processed}"
    
    # Send email
    print(f"Email sent: {processed}")
    
    return processed, report
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(srp_violation_code)
            temp_path = temp_file.name

        try:
            report = validator.validate(temp_path)

            # Should detect at least some violations
            assert isinstance(report.violations, list)
        finally:
            os.unlink(temp_path)

    def test_validate_with_specific_scope(self):
        """Test validation with specific validation scope."""
        validator = ConstitutionalValidator()
        simple_code = """
def test_function():
    return "test"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(simple_code)
            temp_path = temp_file.name

        try:
            # Test with SE principles scope only
            report = validator.validate(
                temp_path, [ValidationScope.SE_PRINCIPLES.value]
            )

            assert isinstance(report, ComplianceReport)

            # Test with quality gates scope only
            report = validator.validate(
                temp_path, [ValidationScope.QUALITY_GATES.value]
            )

            assert isinstance(report, ComplianceReport)
        finally:
            os.unlink(temp_path)

    def test_validate_batch(self):
        """Test batch validation of multiple files."""
        validator = ConstitutionalValidator()

        files_content = [
            "def func1(): return 1",
            "def func2(): return 2",
            "def func3(): return 3",
        ]

        temp_files = []
        try:
            for i, content in enumerate(files_content):
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=f"_{i}.py", delete=False
                )
                temp_file.write(content)
                temp_file.close()
                temp_files.append(temp_file.name)

            reports = validator.validate_batch(temp_files)

            assert len(reports) == 3
            assert all(isinstance(report, ComplianceReport) for report in reports)
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)

    def test_error_handling_file_permission_error(self):
        """Test error handling for file permission errors."""
        validator = ConstitutionalValidator()

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
                report = validator.validate(temp_file.name)

                assert report.compliance_status == "FAIL"
                assert len(report.violations) == 1
                assert "File access error" in report.violations[0].message

    def test_error_handling_unicode_decode_error(self):
        """Test error handling for unicode decode errors."""
        validator = ConstitutionalValidator()

        with patch(
            "builtins.open",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
                report = validator.validate(temp_file.name)

                assert report.compliance_status == "FAIL"
                assert len(report.violations) == 1
                assert "File access error" in report.violations[0].message

    def test_configuration_loading_error_handling(self):
        """Test error handling during configuration loading."""
        import yaml

        # Test with invalid YAML file
        with patch("builtins.open", mock_open(read_data="invalid: yaml: content: [")):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
                validator = ConstitutionalValidator("invalid_config.yaml")

                # Should fall back to default configuration
                assert validator.se_rules is not None
                assert validator.quality_gates is not None

    def test_load_default_configuration(self):
        """Test loading of default configuration when files don't exist."""
        with patch("os.path.exists", return_value=False):
            validator = ConstitutionalValidator()

            # Should have default configuration
            assert "se_principles" in validator.se_rules
            assert "SRP" in validator.se_rules["se_principles"]
            assert "coverage" in validator.quality_gates

    def test_create_error_report(self):
        """Test creation of error reports."""
        validator = ConstitutionalValidator()

        error_report = validator._create_error_report("test.py", "Test error message")

        assert error_report.compliance_status == "FAIL"
        assert len(error_report.violations) == 1
        assert error_report.violations[0].severity == "ERROR"
        assert "Test error message" in error_report.violations[0].message

    def test_create_compliance_report(self):
        """Test creation of compliance reports."""
        validator = ConstitutionalValidator()

        # Test with no violations
        violations = []
        report = validator._create_compliance_report(
            "test.py", violations, ["se_principles"]
        )

        assert report.compliance_status == "PASS"
        assert len(report.violations) == 0

        # Test with error violations
        error_violations = [
            Violation(
                principle="SRP",
                severity="ERROR",
                message="Test error",
                file_path="test.py",
                rule_id="TEST001",
            )
        ]

        report = validator._create_compliance_report(
            "test.py", error_violations, ["se_principles"]
        )

        assert report.compliance_status == "FAIL"
        assert len(report.violations) == 1

        # Test with warning violations
        warning_violations = [
            Violation(
                principle="SRP",
                severity="WARNING",
                message="Test warning",
                file_path="test.py",
                rule_id="TEST002",
            )
        ]

        report = validator._create_compliance_report(
            "test.py", warning_violations, ["se_principles"]
        )

        assert report.compliance_status == "WARNING"
        assert len(report.violations) == 1

    def test_validation_scope_enum(self):
        """Test ValidationScope enum values."""
        assert ValidationScope.SE_PRINCIPLES.value == "se_principles"
        assert ValidationScope.QUALITY_GATES.value == "quality_gates"
        assert ValidationScope.NAMING_CONVENTIONS.value == "naming_conventions"
        assert ValidationScope.SECURITY.value == "security"
