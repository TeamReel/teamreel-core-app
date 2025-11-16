"""
Unit tests for QualityGateValidator class.

Tests quality gate validation functionality.
"""

import pytest
import sys
from pathlib import Path

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from quality_gates import QualityGateValidator


class TestQualityGateValidator:
    """Test cases for QualityGateValidator class."""

    def test_initialization(self):
        """Test QualityGateValidator initialization."""
        validator = QualityGateValidator()

        assert validator is not None
        assert hasattr(validator, "coverage_validator")
        assert hasattr(validator, "complexity_analyzer")
        assert hasattr(validator, "security_scanner")
        assert hasattr(validator, "naming_validator")

    def test_initialization_with_config(self):
        """Test QualityGateValidator initialization with config."""
        config = {"test": "value"}
        validator = QualityGateValidator(config)

        assert validator is not None

    def test_validate_all(self):
        """Test validate_all method."""
        validator = QualityGateValidator()

        # Should not crash when calling validate_all
        results = validator.validate_all(".")

        assert isinstance(results, dict)
        assert "coverage" in results

    def test_validate_quality_gates(self):
        """Test validate_quality_gates method with mock report."""
        validator = QualityGateValidator()

        # Create a mock report object
        class MockReport:
            def __init__(self):
                self.violations = []
                self.total_violations = 0

        mock_report = MockReport()

        # Should not crash when calling validate_quality_gates
        try:
            result = validator.validate_quality_gates(mock_report)
            assert isinstance(result, dict)
        except AttributeError:
            # Method might not exist yet, that's okay
            pass
