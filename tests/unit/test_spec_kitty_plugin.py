"""
Unit tests for SpecKittyConstitutionalPlugin.

Tests plugin integration with spec-kitty CLI workflow.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "plugins"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spec_kitty_plugin import SpecKittyConstitutionalPlugin
from constitutional_validator import ConstitutionalValidator


class TestSpecKittyConstitutionalPlugin:
    """Test cases for SpecKittyConstitutionalPlugin."""

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = SpecKittyConstitutionalPlugin()

        assert plugin is not None
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "version")
        assert plugin.name == "constitutional-validation"

    def test_plugin_metadata(self):
        """Test plugin metadata properties."""
        plugin = SpecKittyConstitutionalPlugin()

        assert plugin.name is not None
        assert plugin.version is not None
        assert plugin.description is not None
        assert "constitutional" in plugin.description.lower()

    @patch("spec_kitty_plugin.SpecValidator")
    def test_on_spec_created_valid_spec(self, mock_spec_validator):
        """Test plugin behavior when a valid spec is created."""
        # Setup mock validator
        mock_validator_instance = Mock()
        mock_validator_instance.validate_spec.return_value = Mock(
            is_valid=True, issues=[]
        )
        mock_spec_validator.return_value = mock_validator_instance

        # Create test spec file
        spec_content = """
# Feature Specification: User Authentication

## Constitutional Requirements
Feature must comply with SE principles and quality gates.

## Acceptance Criteria
- [ ] AC001: User can login with email and password
- [ ] AC002: Invalid credentials return appropriate error
- [ ] AC003: Successful login returns authentication token

## SE Principles Requirements
- Single Responsibility: Authentication logic separated from user management
- Encapsulation: Password hashing implementation hidden
- Loose Coupling: Authentication service depends on interfaces

## Quality Gates
- Unit test coverage >= 80%
- Cyclomatic complexity < 10
- Security scan passes
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_content)
            spec_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()
            result = plugin.on_spec_created(spec_path)

            # Should validate spec successfully
            assert result is not None
            mock_validator_instance.validate_spec.assert_called_once_with(spec_path)

        finally:
            os.unlink(spec_path)

    @patch("spec_kitty_plugin.SpecValidator")
    def test_on_spec_created_invalid_spec(self, mock_spec_validator):
        """Test plugin behavior when invalid spec is created."""
        # Setup mock validator with validation issues
        mock_validator_instance = Mock()
        mock_validator_instance.validate_spec.return_value = Mock(
            is_valid=False,
            issues=[
                Mock(
                    message="Missing SE Principles Requirements section",
                    severity="error",
                ),
                Mock(
                    message="Acceptance criteria not properly formatted",
                    severity="warning",
                ),
            ],
        )
        mock_spec_validator.return_value = mock_validator_instance

        invalid_spec_content = """
# Incomplete Spec

Just some basic content without constitutional requirements.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_spec_content)
            spec_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()

            # Should raise exception for invalid spec
            with pytest.raises(Exception) as exc_info:
                plugin.on_spec_created(spec_path)

            assert "constitutional validation failed" in str(exc_info.value).lower()

        finally:
            os.unlink(spec_path)

    @patch("spec_kitty_plugin.PlanValidator")
    def test_on_plan_created_valid_plan(self, mock_plan_validator):
        """Test plugin behavior when valid plan is created."""
        # Setup mock validator
        mock_validator_instance = Mock()
        mock_validator_instance.validate_plan.return_value = Mock(
            is_valid=True, issues=[]
        )
        mock_plan_validator.return_value = mock_validator_instance

        plan_content = """
# Implementation Plan: User Authentication

## Technical Architecture
System components and design

## SE Principles Architecture Compliance
Constitutional compliance details

## Quality Gates Integration
Testing and validation strategy

## Implementation Tasks
- [ ] T001: Implement authentication API
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_content)
            plan_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()
            result = plugin.on_plan_created(plan_path)

            # Should validate plan successfully
            assert result is not None
            mock_validator_instance.validate_plan.assert_called_once_with(plan_path)

        finally:
            os.unlink(plan_path)

    @patch("spec_kitty_plugin.PlanValidator")
    def test_on_plan_created_invalid_plan(self, mock_plan_validator):
        """Test plugin behavior when invalid plan is created."""
        # Setup mock validator with validation issues
        mock_validator_instance = Mock()
        mock_validator_instance.validate_plan.return_value = Mock(
            is_valid=False,
            issues=[
                Mock(
                    message="Missing Technical Architecture section", severity="error"
                ),
                Mock(
                    message="SE Principles compliance not documented", severity="error"
                ),
            ],
        )
        mock_plan_validator.return_value = mock_validator_instance

        invalid_plan_content = """
# Incomplete Plan

Just basic content without proper architecture.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_plan_content)
            plan_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()

            # Should raise exception for invalid plan
            with pytest.raises(Exception) as exc_info:
                plugin.on_plan_created(plan_path)

            assert "constitutional validation failed" in str(exc_info.value).lower()

        finally:
            os.unlink(plan_path)

    @patch("spec_kitty_plugin.TaskValidator")
    def test_on_task_created_valid_task(self, mock_task_validator):
        """Test plugin behavior when valid task is created."""
        # Setup mock validator
        mock_validator_instance = Mock()
        mock_validator_instance.validate_task.return_value = Mock(
            is_valid=True, issues=[]
        )
        mock_task_validator.return_value = mock_validator_instance

        task_content = """
# Task: T001 - Implement Authentication API

## Constitutional Compliance
SE principles adherence documented

## Technical Implementation
Implementation details provided

## Testing Strategy
Testing approach defined

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_content)
            task_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()
            result = plugin.on_task_created(task_path)

            # Should validate task successfully
            assert result is not None
            mock_validator_instance.validate_task.assert_called_once_with(task_path)

        finally:
            os.unlink(task_path)

    @patch("spec_kitty_plugin.TaskValidator")
    def test_on_task_created_invalid_task(self, mock_task_validator):
        """Test plugin behavior when invalid task is created."""
        # Setup mock validator with validation issues
        mock_validator_instance = Mock()
        mock_validator_instance.validate_task.return_value = Mock(
            is_valid=False,
            issues=[
                Mock(
                    message="Missing Constitutional Compliance section",
                    severity="error",
                ),
                Mock(message="Technical implementation incomplete", severity="warning"),
            ],
        )
        mock_task_validator.return_value = mock_validator_instance

        invalid_task_content = """
# Incomplete Task

Just basic content without constitutional compliance.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_task_content)
            task_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()

            # Should raise exception for invalid task
            with pytest.raises(Exception) as exc_info:
                plugin.on_task_created(task_path)

            assert "constitutional validation failed" in str(exc_info.value).lower()

        finally:
            os.unlink(task_path)

    def test_plugin_hooks_registration(self):
        """Test that plugin hooks are properly registered."""
        plugin = SpecKittyConstitutionalPlugin()

        # Should have required hook methods
        assert hasattr(plugin, "on_spec_created")
        assert hasattr(plugin, "on_plan_created")
        assert hasattr(plugin, "on_task_created")
        assert callable(plugin.on_spec_created)
        assert callable(plugin.on_plan_created)
        assert callable(plugin.on_task_created)

    def test_plugin_error_handling(self):
        """Test plugin error handling with nonexistent files."""
        plugin = SpecKittyConstitutionalPlugin()

        # Should handle nonexistent files gracefully
        with pytest.raises(Exception):
            plugin.on_spec_created("/nonexistent/spec.md")

        with pytest.raises(Exception):
            plugin.on_plan_created("/nonexistent/plan.md")

        with pytest.raises(Exception):
            plugin.on_task_created("/nonexistent/task.md")

    @patch("spec_kitty_plugin.SpecValidator")
    @patch("spec_kitty_plugin.PlanValidator")
    @patch("spec_kitty_plugin.TaskValidator")
    def test_end_to_end_workflow(
        self, mock_task_validator, mock_plan_validator, mock_spec_validator
    ):
        """Test end-to-end spec-kitty workflow with constitutional validation."""
        # Setup all validators to pass
        for mock_validator in [
            mock_spec_validator,
            mock_plan_validator,
            mock_task_validator,
        ]:
            mock_instance = Mock()
            mock_instance.validate_spec.return_value = Mock(is_valid=True, issues=[])
            mock_instance.validate_plan.return_value = Mock(is_valid=True, issues=[])
            mock_instance.validate_task.return_value = Mock(is_valid=True, issues=[])
            mock_validator.return_value = mock_instance

        # Create test files
        spec_content = "# Valid Spec\n## Constitutional Requirements\n"
        plan_content = "# Valid Plan\n## Technical Architecture\n"
        task_content = "# Valid Task\n## Constitutional Compliance\n"

        spec_file = None
        plan_file = None
        task_file = None

        try:
            # Create spec file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write(spec_content)
                spec_file = f.name

            # Create plan file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write(plan_content)
                plan_file = f.name

            # Create task file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write(task_content)
                task_file = f.name

            plugin = SpecKittyConstitutionalPlugin()

            # Run through workflow
            spec_result = plugin.on_spec_created(spec_file)
            plan_result = plugin.on_plan_created(plan_file)
            task_result = plugin.on_task_created(task_file)

            # All should pass validation
            assert spec_result is not None
            assert plan_result is not None
            assert task_result is not None

        finally:
            # Cleanup
            for file_path in [spec_file, plan_file, task_file]:
                if file_path and os.path.exists(file_path):
                    os.unlink(file_path)

    def test_plugin_configuration(self):
        """Test plugin configuration and customization."""
        # Test plugin with custom configuration
        plugin = SpecKittyConstitutionalPlugin()

        # Should support configuration
        assert hasattr(plugin, "configure") or hasattr(plugin, "__init__")

    def test_plugin_logging_integration(self):
        """Test plugin logging and reporting."""
        plugin = SpecKittyConstitutionalPlugin()

        # Plugin should support logging/reporting
        # This would typically integrate with spec-kitty's logging system
        assert plugin is not None

    @patch("spec_kitty_plugin.SpecValidator")
    def test_validation_performance(self, mock_spec_validator):
        """Test plugin performance with large files."""
        # Create large spec content
        large_spec_content = (
            """
# Large Feature Specification

## Constitutional Requirements
Constitutional requirements defined.

## Acceptance Criteria
"""
            + "\n".join(
                [f"- [ ] AC{i:03d}: Acceptance criterion {i}" for i in range(1, 101)]
            )
            + """

## SE Principles Requirements
Detailed SE principles requirements.

## Quality Gates
Comprehensive quality gates defined.
"""
        )

        # Setup mock validator
        mock_validator_instance = Mock()
        mock_validator_instance.validate_spec.return_value = Mock(
            is_valid=True, issues=[]
        )
        mock_spec_validator.return_value = mock_validator_instance

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(large_spec_content)
            spec_path = f.name

        try:
            plugin = SpecKittyConstitutionalPlugin()

            # Should handle large files efficiently
            result = plugin.on_spec_created(spec_path)
            assert result is not None

        finally:
            os.unlink(spec_path)
