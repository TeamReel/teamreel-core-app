"""
Unit tests for SpecValidator class.

Tests specification validation against constitutional requirements.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys
import yaml

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spec_validator import SpecValidator, SpecValidationCategory, ValidationLevel
from compliance_reporter import Violation


class TestSpecValidator:
    """Test cases for SpecValidator class."""

    def test_initialization(self):
        """Test SpecValidator initialization."""
        validator = SpecValidator()

        assert validator is not None
        assert hasattr(validator, "constitutional_validator")

    def test_initialization_with_config(self):
        """Test SpecValidator initialization with custom config."""
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

            validator = SpecValidator(str(config_file))
            assert validator is not None

    def test_validate_spec_with_constitutional_compliance(self):
        """Test validating a spec with proper constitutional compliance."""
        spec_content = """
# Feature Specification: User Authentication

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Login (Priority: P1)
**Independent Test**: Users can successfully log in with valid credentials

**Acceptance Scenarios**:
1. **Given** valid credentials, **When** user logs in, **Then** access is granted

## SE Principles Compliance *(mandatory)*

#### SE Principle 1: Single Responsibility Principle
- [ ] **Clear Module Purpose**: Each authentication module has single responsibility
- [ ] **Function Focus**: Each function does one specific task

#### SE Principle 2: Encapsulation
- [ ] **Data Privacy**: User credentials properly encapsulated

### Constitutional Enforcement Integration
- [ ] **Quality Gates**: Feature will be validated against coverage thresholds
- [ ] **Git Hooks**: Pre-commit hooks will enforce constitutional compliance

## Success Criteria *(mandatory)*
- **SC-001**: Users can complete login in under 30 seconds
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_content)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            assert hasattr(report, "issues")
            assert hasattr(report, "is_valid")

        finally:
            os.unlink(spec_path)

    def test_validate_spec_missing_mandatory_sections(self):
        """Test validating a spec missing mandatory sections."""
        incomplete_spec = """
# Feature Specification: Incomplete Feature

This is an incomplete specification without required sections.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(incomplete_spec)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            assert not report.is_valid
            assert len(report.issues) > 0

            # Should flag missing mandatory sections
            issue_messages = [issue.message for issue in report.issues]
            assert any("User Story" in msg for msg in issue_messages)

        finally:
            os.unlink(spec_path)

    def test_validate_spec_missing_se_principles(self):
        """Test validating a spec missing SE principles compliance."""
        spec_without_se = """
# Feature Specification: No SE Principles

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Feature (Priority: P1)
**Independent Test**: Feature works as expected

## Success Criteria *(mandatory)*
- **SC-001**: Feature meets requirements
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_without_se)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            assert not report.is_valid

            # Should flag missing SE principles section
            issue_messages = [issue.message for issue in report.issues]
            assert any("SE Principles" in msg for msg in issue_messages)

        finally:
            os.unlink(spec_path)

    def test_validate_spec_incomplete_se_principles(self):
        """Test validating a spec with incomplete SE principles."""
        spec_incomplete_se = """
# Feature Specification: Incomplete SE Principles

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Feature (Priority: P1)
**Independent Test**: Feature works as expected

## SE Principles Compliance *(mandatory)*

#### SE Principle 1: Single Responsibility Principle
- [ ] **Clear Module Purpose**: Each module has single responsibility

## Success Criteria *(mandatory)*
- **SC-001**: Feature meets requirements
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_incomplete_se)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            # Should pass basic validation but warn about incomplete SE principles

        finally:
            os.unlink(spec_path)

    def test_validate_spec_missing_acceptance_criteria(self):
        """Test validating a spec with missing acceptance criteria."""
        spec_no_acceptance = """
# Feature Specification: Missing Acceptance Criteria

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Feature (Priority: P1)
No acceptance scenarios defined

## SE Principles Compliance *(mandatory)*
Basic compliance

## Success Criteria *(mandatory)*
- **SC-001**: Feature works
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_no_acceptance)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            # Should identify missing acceptance scenarios

        finally:
            os.unlink(spec_path)

    def test_validate_spec_nonexistent_file(self):
        """Test validating a nonexistent spec file."""
        validator = SpecValidator()
        report = validator.validate_spec("/nonexistent/file.md")

        assert report is not None
        assert not report.is_valid
        assert len(report.issues) > 0

        # Should have file access error
        assert any("file" in issue.message.lower() for issue in report.issues)

    def test_validate_spec_empty_file(self):
        """Test validating an empty spec file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            assert not report.is_valid
            assert len(report.issues) > 0

        finally:
            os.unlink(spec_path)

    def test_validate_spec_malformed_markdown(self):
        """Test validating a spec with malformed markdown."""
        malformed_spec = """
# Feature Specification: Malformed

## Unclosed section
No closing or structure

### Nested without parent
- Item without proper structure
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(malformed_spec)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            # Should handle malformed markdown gracefully
            assert report is not None

        finally:
            os.unlink(spec_path)

    def test_spec_validation_categories(self):
        """Test that all spec validation categories are defined."""
        expected_categories = [
            "constitutional_checklist",
            "se_principles",
            "architecture_compliance",
            "naming_conventions",
            "user_story_format",
            "acceptance_criteria",
            "quality_gates",
            "template_structure",
        ]

        for category in expected_categories:
            assert hasattr(SpecValidationCategory, category.upper())

    def test_validation_level_enum(self):
        """Test ValidationLevel enum values."""
        assert ValidationLevel.ERROR.value == "error"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.INFO.value == "info"

    def test_validate_spec_with_quality_gates(self):
        """Test validating a spec with quality gates section."""
        spec_with_gates = """
# Feature Specification: With Quality Gates

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Feature (Priority: P1)
**Independent Test**: Works correctly

## SE Principles Compliance *(mandatory)*
Basic compliance sections

### Constitutional Enforcement Integration
- [ ] **Quality Gates**: Coverage thresholds defined
- [ ] **Git Hooks**: Pre-commit validation enabled
- [ ] **CI/CD Integration**: GitHub Actions validation

## Success Criteria *(mandatory)*
- **SC-001**: Meets requirements
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec_with_gates)
            spec_path = f.name

        try:
            validator = SpecValidator()
            report = validator.validate_spec(spec_path)

            assert report is not None
            # Should recognize quality gates section

        finally:
            os.unlink(spec_path)

    def test_error_handling_with_corrupted_config(self):
        """Test error handling when config file is corrupted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("invalid: yaml: content: [")  # Malformed YAML

            # Should handle corrupted config gracefully
            validator = SpecValidator(str(config_file))
            assert validator is not None

    def test_batch_validation(self):
        """Test validating multiple spec files."""
        spec1_content = """
# Feature 1
## User Scenarios & Testing *(mandatory)*
### User Story 1 - Basic (Priority: P1)
**Independent Test**: Works
## SE Principles Compliance *(mandatory)*
Basic compliance
## Success Criteria *(mandatory)*
- **SC-001**: Works
"""

        spec2_content = """
# Feature 2  
## User Scenarios & Testing *(mandatory)*
### User Story 1 - Advanced (Priority: P1)
**Independent Test**: Advanced feature works
## SE Principles Compliance *(mandatory)*
Basic compliance
## Success Criteria *(mandatory)*
- **SC-001**: Advanced works
"""

        spec_files = []
        try:
            for content in [spec1_content, spec2_content]:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as f:
                    f.write(content)
                    spec_files.append(f.name)

            validator = SpecValidator()
            reports = [validator.validate_spec(path) for path in spec_files]
            assert len(reports) == 2
            assert all(report is not None for report in reports)

        finally:
            for path in spec_files:
                if os.path.exists(path):
                    os.unlink(path)
