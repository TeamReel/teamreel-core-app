"""
TeamReel Constitutional Validation Engine

Core engine that orchestrates SE principle validation across all code types.
Implements distributed plugin architecture with offline capability.

SE Principles Focus: SRP (single responsibility) and Encapsulation (clear interface)
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .compliance_reporter import ComplianceReport, Violation
from .violation_detector import ViolationDetector


class ValidationScope(Enum):
    """Enumeration of validation scopes."""

    SE_PRINCIPLES = "se_principles"
    QUALITY_GATES = "quality_gates"
    NAMING_CONVENTIONS = "naming_conventions"
    SECURITY = "security"


class ConstitutionalValidator:
    """
    Main constitutional validation engine.

    Single Responsibility: Orchestrate SE principle validation workflow
    Encapsulation: Hide internal validation logic behind clean public API
    """

    SUPPORTED_FILE_TYPES = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".yaml",
        ".yml",
        ".json",
        ".md",
    }

    def __init__(self, config_path: str = ".kittify/config/se_rules.yaml"):
        """
        Initialize the constitutional validator.

        Args:
            config_path: Path to SE rules configuration file
        """
        self.config_path = config_path
        self.se_rules = {}
        self.quality_gates = {}
        self.violation_detector = ViolationDetector()

        # Load configuration files
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load SE rules and quality gate configurations."""
        try:
            # Load SE principles rules
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.se_rules = yaml.safe_load(f) or {}

            # Load quality gate configuration
            quality_gates_path = ".kittify/config/quality_gates.yaml"
            if os.path.exists(quality_gates_path):
                with open(quality_gates_path, "r", encoding="utf-8") as f:
                    self.quality_gates = yaml.safe_load(f) or {}

        except Exception as e:
            print(f"Warning: Failed to load configuration: {e}")
            # Use default minimal configuration
            self._load_default_configuration()

    def _load_default_configuration(self) -> None:
        """Load minimal default configuration if files don't exist."""
        self.se_rules = {
            "se_principles": {
                "SRP": {"description": "Single Responsibility Principle"},
                "Encapsulation": {"description": "Information hiding"},
                "LooseCoupling": {"description": "Minimal dependencies"},
                "Reusability": {"description": "No code duplication"},
                "Portability": {"description": "Environment independence"},
                "Defensibility": {"description": "Input validation and security"},
                "Maintainability": {"description": "Readable and testable code"},
                "Simplicity": {"description": "KISS/DRY/YAGNI principles"},
            }
        }

        self.quality_gates = {
            "coverage": {"unit_test_threshold": 0.8},
            "complexity": {"cyclomatic_max": 10},
            "security": {"vulnerability_scan": True},
            "naming_conventions": {
                "rest_api": "kebab-case",
                "python_code": "snake_case",
                "typescript_code": "camelCase",
            },
        }

    def validate(
        self, file_path: str, validation_scope: List[str] = None
    ) -> ComplianceReport:
        """
        Validate a single file against constitutional requirements.

        Args:
            file_path: Path to file to validate
            validation_scope: List of validation scopes to apply

        Returns:
            ComplianceReport with validation results
        """
        if validation_scope is None:
            validation_scope = [scope.value for scope in ValidationScope]

        # Validate file exists and is supported
        if not os.path.exists(file_path):
            return self._create_error_report(file_path, f"File not found: {file_path}")

        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FILE_TYPES:
            return self._create_error_report(
                file_path, f"Unsupported file type: {file_ext}"
            )

        violations = []

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Run validation based on scope
            if ValidationScope.SE_PRINCIPLES.value in validation_scope:
                violations.extend(
                    self._validate_se_principles(file_path, file_content, file_ext)
                )

            if ValidationScope.QUALITY_GATES.value in validation_scope:
                violations.extend(
                    self._validate_quality_gates(file_path, file_content, file_ext)
                )

            if ValidationScope.NAMING_CONVENTIONS.value in validation_scope:
                violations.extend(
                    self._validate_naming_conventions(file_path, file_content, file_ext)
                )

            if ValidationScope.SECURITY.value in validation_scope:
                violations.extend(
                    self._validate_security(file_path, file_content, file_ext)
                )

        except Exception as e:
            return self._create_error_report(file_path, f"Validation error: {str(e)}")

        # Generate compliance report
        return self._create_compliance_report(file_path, violations, validation_scope)

    def validate_batch(
        self, file_paths: List[str], validation_scope: List[str] = None
    ) -> List[ComplianceReport]:
        """
        Validate multiple files against constitutional requirements.

        Args:
            file_paths: List of file paths to validate
            validation_scope: List of validation scopes to apply

        Returns:
            List of ComplianceReports for each file
        """
        reports = []

        for file_path in file_paths:
            report = self.validate(file_path, validation_scope)
            reports.append(report)

        return reports

    def get_supported_file_types(self) -> List[str]:
        """Return list of supported file extensions."""
        return list(self.SUPPORTED_FILE_TYPES)

    def _validate_se_principles(
        self, file_path: str, content: str, file_ext: str
    ) -> List[Violation]:
        """Validate file against all 8 SE principles."""
        violations = []

        # Use violation detector for each SE principle
        violations.extend(
            self.violation_detector.detect_srp_violations(content, file_ext, file_path)
        )
        violations.extend(
            self.violation_detector.detect_encapsulation_violations(
                content, file_ext, file_path
            )
        )
        violations.extend(
            self.violation_detector.detect_coupling_violations(file_path, content)
        )
        violations.extend(
            self.violation_detector.detect_reusability_violations(
                content, file_ext, file_path
            )
        )
        violations.extend(
            self.violation_detector.detect_portability_violations(
                content, file_ext, file_path
            )
        )
        violations.extend(
            self.violation_detector.detect_defensibility_violations(
                content, file_ext, file_path
            )
        )
        violations.extend(
            self.violation_detector.detect_maintainability_violations(
                content, file_ext, file_path
            )
        )
        violations.extend(
            self.violation_detector.detect_simplicity_violations(
                content, file_ext, file_path
            )
        )

        return violations

    def _validate_quality_gates(
        self, file_path: str, content: str, file_ext: str
    ) -> List[Violation]:
        """Validate file against quality gate requirements."""
        violations = []

        # Complexity validation
        complexity_violations = self.violation_detector.detect_complexity_violations(
            content, file_ext, file_path
        )
        violations.extend(complexity_violations)

        return violations

    def _validate_naming_conventions(
        self, file_path: str, content: str, file_ext: str
    ) -> List[Violation]:
        """Validate file against naming convention requirements."""
        violations = []

        naming_violations = self.violation_detector.detect_naming_violations(
            content, file_ext, file_path
        )
        violations.extend(naming_violations)

        return violations

    def _validate_security(
        self, file_path: str, content: str, file_ext: str
    ) -> List[Violation]:
        """Validate file against security requirements."""
        violations = []

        security_violations = self.violation_detector.detect_security_violations(
            content, file_ext, file_path
        )
        violations.extend(security_violations)

        return violations

    def _create_compliance_report(
        self, file_path: str, violations: List[Violation], validation_scope: List[str]
    ) -> ComplianceReport:
        """Create a compliance report from validation results."""
        from .compliance_reporter import ComplianceReport

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
            "coverage_threshold": error_count == 0,  # Simplified for now
            "complexity_limit": len(
                [v for v in violations if "complexity" in v.message.lower()]
            )
            == 0,
            "security_scan": len(
                [v for v in violations if v.principle == "Defensibility"]
            )
            == 0,
        }

        # Metadata
        metadata = {
            "file_path": file_path,
            "validation_scope": validation_scope,
            "total_violations": len(violations),
            "error_count": error_count,
            "warning_count": warning_count,
            "constitution_version": "1.1.0",
            "tool_version": "constitutional-validator-1.0.0",
        }

        return ComplianceReport(
            compliance_status=compliance_status,
            violations=violations,
            quality_gates=quality_gates,
            metadata=metadata,
        )

    def _create_error_report(
        self, file_path: str, error_message: str
    ) -> ComplianceReport:
        """Create an error compliance report."""
        from .compliance_reporter import ComplianceReport, Violation

        error_violation = Violation(
            principle="ValidationError",
            severity="ERROR",
            message=error_message,
            file_path=file_path,
            line_number=None,
            suggested_fix="Fix the file path or content issue",
            rule_id="VALIDATION_ERROR",
        )

        return ComplianceReport(
            compliance_status="FAIL",
            violations=[error_violation],
            quality_gates={
                "coverage_threshold": False,
                "complexity_limit": False,
                "security_scan": False,
            },
            metadata={"file_path": file_path, "error": error_message},
        )
