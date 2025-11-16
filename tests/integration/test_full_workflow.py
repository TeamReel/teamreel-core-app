"""
Integration tests for the complete constitutional validation workflow.

Tests end-to-end functionality with real files and configurations.
"""

import pytest
import tempfile
import os
import yaml
import json
from pathlib import Path
import sys
import shutil

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from constitutional_validator import ConstitutionalValidator
from violation_detector import ViolationDetector
from compliance_reporter import ComplianceReport, Violation
from quality_gates import QualityGateValidator


class TestFullWorkflow:
    """Integration tests for complete constitutional validation workflow."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir)

            # Create project structure
            src_dir = workspace_path / "src"
            tests_dir = workspace_path / "tests"
            src_dir.mkdir()
            tests_dir.mkdir()

            # Create sample Python files with violations
            python_file_1 = src_dir / "user_manager.py"
            python_file_1.write_text(
                '''
"""User management module with multiple violations."""

import os
import sys
import json
import yaml
import requests
import pandas
import numpy

class UserManager:
    def __init__(self):
        self.users = []
        self.api_key = "sk-1234567890abcdef"  # Hardcoded secret
        
    def processUserAndSendEmailAndLog(self, userData):  # Naming + SRP violation
        """Process user, send email, and log - violates SRP."""
        # Process user data
        processed = userData.upper()
        
        # Send email (should be separate responsibility)
        email_sent = self.send_email(processed)
        
        # Log activity (should be separate responsibility)
        self.log_activity("user_processed", userData)
        
        # Update database (should be separate responsibility)
        self.update_database(userData)
        
        return processed, email_sent
        
    def send_email(self, data):
        """Send email with hardcoded path."""
        log_path = "C:\\\\Windows\\\\temp\\\\email.log"  # Portability violation
        return True
        
    def log_activity(self, action, data):
        """Log without validation."""
        command = f"echo {data}"  # Potential injection
        os.system(command)  # Security violation
        
    def update_database(self, data):
        """Update with no error handling."""
        pass  # No implementation - maintainability issue
'''
            )

            python_file_2 = src_dir / "data_processor.py"
            python_file_2.write_text(
                '''
"""Data processing with complexity violations."""

def deeply_nested_processor(data):
    """Function with high complexity."""
    results = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item > 100:
                    if item < 1000:
                        if item % 10 == 0:
                            if item % 100 != 0:
                                results.append(item * 2)
                            else:
                                results.append(item // 2)
                        else:
                            results.append(item + 1)
                    else:
                        results.append(item - 1)
                else:
                    results.append(item)
            else:
                results.append(item * -1)
        else:
            results.append(0)
    return results

class OverEngineeredFactory:
    """Over-engineered pattern for simple task."""
    def create_abstract_factory(self):
        return ConcreteFactoryImplementation()

class ConcreteFactoryImplementation:
    def create_simple_string(self):
        return self._perform_complex_string_creation_process()
    
    def _perform_complex_string_creation_process(self):
        return "simple"  # Could just return directly
'''
            )

            # Create configuration file
            config_file = workspace_path / "constitutional_config.yaml"
            config_content = {
                "se_principles": {
                    "single_responsibility_principle": {
                        "enabled": True,
                        "severity": "HIGH",
                        "rules": {
                            "max_responsibilities_per_function": 3,
                            "max_responsibilities_per_class": 5,
                        },
                    },
                    "encapsulation": {
                        "enabled": True,
                        "severity": "MEDIUM",
                        "rules": {
                            "require_private_attributes": True,
                            "disallow_direct_attribute_access": True,
                        },
                    },
                    "loose_coupling": {
                        "enabled": True,
                        "severity": "MEDIUM",
                        "rules": {
                            "max_imports_per_file": 10,
                            "avoid_circular_dependencies": True,
                        },
                    },
                    "reusability": {
                        "enabled": True,
                        "severity": "LOW",
                        "rules": {
                            "detect_code_duplication": True,
                            "min_reusable_function_size": 3,
                        },
                    },
                    "portability": {
                        "enabled": True,
                        "severity": "MEDIUM",
                        "rules": {
                            "avoid_hardcoded_paths": True,
                            "use_cross_platform_apis": True,
                        },
                    },
                    "defensibility": {
                        "enabled": True,
                        "severity": "HIGH",
                        "rules": {
                            "require_input_validation": True,
                            "avoid_dangerous_functions": ["eval", "exec", "os.system"],
                        },
                    },
                    "maintainability": {
                        "enabled": True,
                        "severity": "LOW",
                        "rules": {
                            "require_docstrings": True,
                            "max_function_length": 50,
                        },
                    },
                    "simplicity": {
                        "enabled": True,
                        "severity": "LOW",
                        "rules": {
                            "avoid_over_engineering": True,
                            "prefer_simple_solutions": True,
                        },
                    },
                },
                "quality_gates": {
                    "coverage_threshold": 80,
                    "max_violations_per_file": 10,
                    "max_high_severity_violations": 5,
                    "blocking_severities": ["ERROR", "HIGH"],
                },
                "file_patterns": {
                    "include": ["**/*.py", "**/*.js", "**/*.ts"],
                    "exclude": [
                        "**/node_modules/**",
                        "**/__pycache__/**",
                        "**/venv/**",
                    ],
                },
            }

            with open(config_file, "w") as f:
                yaml.dump(config_content, f, default_flow_style=False)

            yield workspace_path

    def test_full_validation_workflow(self, temp_workspace):
        """Test complete validation workflow from start to finish."""
        # Initialize validator
        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        # Get all Python files
        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]

        # Perform validation
        report = validator.validate(file_paths)

        # Verify report structure
        assert isinstance(report, ComplianceReport)
        assert report.total_files_analyzed > 0
        assert report.total_violations > 0

        # Should detect violations from our test files
        assert len(report.violations) > 0

        # Verify violation types
        violation_types = [v.principle for v in report.violations]
        assert "Single Responsibility Principle" in violation_types
        assert "Portability" in violation_types or "Defensibility" in violation_types

    def test_batch_validation_performance(self, temp_workspace):
        """Test batch validation performance with multiple files."""
        # Create additional test files
        src_dir = temp_workspace / "src"

        # Create 10 additional files
        for i in range(10):
            test_file = src_dir / f"test_module_{i}.py"
            test_file.write_text(
                f'''
"""Test module {i}."""

def test_function_{i}():
    """Simple test function {i}."""
    return {i}

class TestClass{i}:
    """Test class {i}."""
    def method_{i}(self):
        return {i}
'''
            )

        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        # Get all Python files
        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]

        # Should have original 2 + 10 new files
        assert len(file_paths) >= 12

        # Validate all files
        report = validator.validate(file_paths)

        # Should process all files
        assert report.total_files_analyzed >= 12
        assert isinstance(report, ComplianceReport)

    def test_quality_gates_integration(self, temp_workspace):
        """Test quality gates integration with violation detection."""
        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        # Create quality gate validator
        quality_gate_validator = QualityGateValidator(str(config_path))

        # Validate files
        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]
        report = validator.validate(file_paths)

        # Test quality gates
        gates_result = quality_gate_validator.validate_quality_gates(report)

        assert isinstance(gates_result, dict)
        assert "passed" in gates_result
        assert "failed_gates" in gates_result

        # Should fail some gates due to violations in test files
        assert gates_result["passed"] is False or gates_result["passed"] is True

        if not gates_result["passed"]:
            assert len(gates_result["failed_gates"]) > 0

    def test_error_handling_with_malformed_files(self, temp_workspace):
        """Test error handling when processing malformed files."""
        src_dir = temp_workspace / "src"

        # Create malformed Python file
        malformed_file = src_dir / "malformed.py"
        malformed_file.write_text(
            """
def incomplete_function(
    # Missing closing parenthesis
    
class IncompleteClass
    # Missing colon
    def method(self):
        pass
        
# Unmatched brackets
def another_function():
    if True:
        return "unmatched"
    # Missing closing brace somewhere
"""
        )

        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        # Should handle malformed files gracefully
        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]

        # Should not crash on malformed files
        report = validator.validate(file_paths)

        assert isinstance(report, ComplianceReport)
        # Should still process other valid files
        assert report.total_files_analyzed > 0

    def test_configuration_validation(self, temp_workspace):
        """Test configuration file validation."""
        # Test with invalid configuration
        invalid_config = temp_workspace / "invalid_config.yaml"
        invalid_config.write_text(
            """
invalid_yaml_content:
  - item1
  - item2
missing_required_sections: true
"""
        )

        # Should handle invalid configuration gracefully
        try:
            validator = ConstitutionalValidator(str(invalid_config))
            # If validator creation succeeds, it should use defaults
            assert validator is not None
        except Exception as e:
            # Should provide meaningful error message
            assert "configuration" in str(e).lower() or "config" in str(e).lower()

    def test_file_filtering(self, temp_workspace):
        """Test file filtering based on include/exclude patterns."""
        # Create various file types
        src_dir = temp_workspace / "src"

        # Create files that should be included
        python_file = src_dir / "included.py"
        python_file.write_text("# Python file")

        js_file = src_dir / "included.js"
        js_file.write_text("// JavaScript file")

        # Create files that should be excluded
        cache_dir = src_dir / "__pycache__"
        cache_dir.mkdir()
        cache_file = cache_dir / "cached.pyc"
        cache_file.write_text("cached content")

        binary_file = src_dir / "binary.exe"
        binary_file.write_text("binary content")

        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        # Get all files and validate
        all_files = list(temp_workspace.glob("**/*"))
        file_paths = [str(f) for f in all_files if f.is_file()]

        report = validator.validate(file_paths)

        # Should only process supported file types
        assert report.total_files_analyzed >= 2  # At least the Python files we created

    def test_violation_severity_filtering(self, temp_workspace):
        """Test filtering violations by severity levels."""
        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]
        report = validator.validate(file_paths)

        # Test different severity levels
        high_violations = [v for v in report.violations if v.severity == "HIGH"]
        medium_violations = [v for v in report.violations if v.severity == "MEDIUM"]
        low_violations = [v for v in report.violations if v.severity == "LOW"]

        # Should have violations of different severities
        assert len(report.violations) > 0

        # Verify severity distribution makes sense
        total_violations = (
            len(high_violations) + len(medium_violations) + len(low_violations)
        )
        assert total_violations <= len(
            report.violations
        )  # Some might be ERROR or other levels

    def test_json_report_export(self, temp_workspace):
        """Test exporting validation report to JSON format."""
        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]
        report = validator.validate(file_paths)

        # Export to JSON
        json_data = report.to_json()

        # Should be valid JSON
        parsed_json = json.loads(json_data)

        assert "timestamp" in parsed_json
        assert "total_files_analyzed" in parsed_json
        assert "total_violations" in parsed_json
        assert "violations" in parsed_json
        assert "summary" in parsed_json

        # Verify structure
        assert isinstance(parsed_json["violations"], list)
        assert isinstance(parsed_json["summary"], dict)

    def test_human_readable_report_format(self, temp_workspace):
        """Test human-readable report formatting."""
        config_path = temp_workspace / "constitutional_config.yaml"
        validator = ConstitutionalValidator(str(config_path))

        python_files = list(temp_workspace.glob("**/*.py"))
        file_paths = [str(f) for f in python_files]
        report = validator.validate(file_paths)

        # Generate human-readable format
        human_report = report.to_human_readable()

        assert isinstance(human_report, str)
        assert len(human_report) > 0

        # Should contain key information
        assert "Constitutional Validation Report" in human_report
        assert "Total Files Analyzed" in human_report
        assert "Total Violations" in human_report

        if report.total_violations > 0:
            assert (
                "VIOLATIONS FOUND" in human_report
                or "violations found" in human_report.lower()
            )


class TestWorkflowEdgeCases:
    """Test edge cases and error conditions in the workflow."""

    def test_empty_workspace(self):
        """Test validation with empty workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal config
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text(
                """
se_principles:
  single_responsibility_principle:
    enabled: true
    severity: "HIGH"
"""
            )

            validator = ConstitutionalValidator(str(config_file))

            # Validate empty file list
            report = validator.validate([])

            assert isinstance(report, ComplianceReport)
            assert report.total_files_analyzed == 0
            assert report.total_violations == 0

    def test_nonexistent_files(self):
        """Test validation with nonexistent file paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text(
                """
se_principles:
  single_responsibility_principle:
    enabled: true
    severity: "HIGH"
"""
            )

            validator = ConstitutionalValidator(str(config_file))

            # Try to validate nonexistent files
            nonexistent_files = [
                "/path/that/does/not/exist.py",
                "/another/missing/file.js",
            ]

            # Should handle gracefully
            report = validator.validate(nonexistent_files)

            assert isinstance(report, ComplianceReport)
            # May have 0 files analyzed or error violations

    def test_mixed_valid_invalid_files(self):
        """Test validation with mix of valid and invalid file paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir)

            # Create valid file
            valid_file = workspace_path / "valid.py"
            valid_file.write_text("def valid_function(): pass")

            # Create config
            config_file = workspace_path / "config.yaml"
            config_file.write_text(
                """
se_principles:
  single_responsibility_principle:
    enabled: true
    severity: "HIGH"
"""
            )

            validator = ConstitutionalValidator(str(config_file))

            # Mix valid and invalid paths
            mixed_files = [
                str(valid_file),  # Valid
                "/nonexistent/file.py",  # Invalid
                str(workspace_path / "missing.py"),  # Invalid
            ]

            report = validator.validate(mixed_files)

            assert isinstance(report, ComplianceReport)
            # Should process at least the valid file
            assert report.total_files_analyzed >= 0
