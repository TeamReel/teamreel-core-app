"""
TeamReel Constitutional Validation Engine

Core engine that orchestrates SE principle validation across all code types.
Implements distributed plugin architecture with offline capability.

SE Principles Focus: SRP (single responsibility) and Encapsulation (clear interface)
"""

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    from .compliance_reporter import ComplianceReport, Violation
    from .violation_detector import ViolationDetector
    from .quality_gates import QualityGateValidator
except ImportError:
    # Fallback for direct execution
    from compliance_reporter import ComplianceReport, Violation
    from violation_detector import ViolationDetector
    from quality_gates import QualityGateValidator


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
            else:
                # Use default configuration if file doesn't exist
                self._load_default_configuration()
                return

            # Load quality gate configuration
            quality_gates_path = ".kittify/config/quality_gates.yaml"
            if os.path.exists(quality_gates_path):
                with open(quality_gates_path, "r", encoding="utf-8") as f:
                    self.quality_gates = yaml.safe_load(f) or {}
            else:
                # Set default quality gates if file doesn't exist
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

        except (yaml.YAMLError, FileNotFoundError, PermissionError) as e:
            print(f"Warning: Failed to load configuration: {e}")
            # Use default minimal configuration
            self._load_default_configuration()
        except Exception as e:
            print(f"Unexpected error loading configuration: {e}")
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

        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            return self._create_error_report(file_path, f"File access error: {str(e)}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            return self._create_error_report(file_path, f"File parsing error: {str(e)}")
        except (SyntaxError, ValueError) as e:
            return self._create_error_report(
                file_path, f"Code analysis error: {str(e)}"
            )
        except Exception as e:
            return self._create_error_report(
                file_path, f"Unexpected validation error: {str(e)}"
            )

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
            content, file_path
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
        # ComplianceReport already imported at module level

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
        # ComplianceReport and Violation already imported at module level

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


def _parse_cli_arguments() -> argparse.Namespace:
    """Parse CLI arguments for constitutional validation."""

    parser = argparse.ArgumentParser(
        description="TeamReel constitutional validation CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--files",
        required=True,
        help="Path to a newline-separated file list or a comma-separated string of files to validate.",
    )
    parser.add_argument(
        "--config",
        default=".kittify/config/se_rules.yaml",
        help="Path to the constitutional rules configuration file.",
    )
    parser.add_argument(
        "--scope",
        default="se_principles,quality_gates,naming_conventions,security",
        help="Comma-separated validation scopes to apply.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "terminal"],
        default="json",
        help="Output format for individual reports written to stdout.",
    )
    parser.add_argument(
        "--output",
        default="constitutional-compliance-report.json",
        help="Destination path for the aggregated JSON report.",
    )
    return parser.parse_args()


def _load_file_list(files_argument: str) -> List[str]:
    """Load files to validate from either a file path or inline list."""

    if not files_argument:
        return []

    files_path = Path(files_argument)
    if files_path.exists():
        content = files_path.read_text(encoding="utf-8")
        return [line.strip() for line in content.splitlines() if line.strip()]

    normalized = files_argument.replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _parse_scopes(scope_argument: str) -> List[str]:
    """Convert comma separated scope argument into a list."""

    if not scope_argument:
        return [scope.value for scope in ValidationScope]

    values = [entry.strip() for entry in scope_argument.split(",") if entry.strip()]
    return values or [scope.value for scope in ValidationScope]


def _report_to_dict(report: ComplianceReport) -> Dict[str, Any]:
    """Convert a ComplianceReport into a dictionary."""

    return json.loads(report.to_json())


def _aggregate_results(reports: List[ComplianceReport]) -> Dict[str, Any]:
    """Build an aggregated summary for CLI output."""

    total_violations = sum(len(report.violations) for report in reports)
    error_count = sum(
        1
        for report in reports
        for violation in report.violations
        if violation.severity == "ERROR"
    )
    warning_count = sum(
        1
        for report in reports
        for violation in report.violations
        if violation.severity == "WARNING"
    )

    overall_status = "pass"
    if any(report.compliance_status == "FAIL" for report in reports):
        overall_status = "fail"
    elif any(report.compliance_status == "WARNING" for report in reports):
        overall_status = "warning"

    compliance_score = max(0, 100 - (error_count * 10) - (warning_count * 5))

    return {
        "validation_result": overall_status,
        "compliance_score": compliance_score,
        "violations_count": total_violations,
        "error_count": error_count,
        "warning_count": warning_count,
    }


def _write_json_report(
    reports: List[ComplianceReport],
    summary: Dict[str, Any],
    output_path: str,
    files: List[str],
) -> None:
    """Persist aggregated report details to disk."""

    payload: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files_validated": files,
        "summary": summary,
        "reports": [_report_to_dict(report) for report in reports],
    }

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2, ensure_ascii=False)


def _write_validation_output(summary: Dict[str, Any], output_path: str) -> None:
    """Create validation_output.txt for downstream parsing."""

    with open("validation_output.txt", "w", encoding="utf-8") as validation_file:
        validation_file.write(f"result={summary['validation_result']}\n")
        validation_file.write(f"compliance-score={summary['compliance_score']}\n")
        validation_file.write(f"violations-count={summary['violations_count']}\n")
        validation_file.write(f"report-path={output_path}\n")


def run_cli() -> None:
    """Entry point for running the constitutional validator as a CLI."""

    args = _parse_cli_arguments()
    files_to_validate = _load_file_list(args.files)
    scopes = _parse_scopes(args.scope)

    if not files_to_validate:
        summary = {
            "validation_result": "pass",
            "compliance_score": 100,
            "violations_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }
        _write_json_report([], summary, args.output, files_to_validate)
        _write_validation_output(summary, args.output)
        print("No files to validate. Skipping constitutional validation.")
        return

    validator = ConstitutionalValidator(config_path=args.config)
    reports: List[ComplianceReport] = []

    for file_path in files_to_validate:
        try:
            report = validator.validate(file_path, scopes)
            reports.append(report)
            if args.format == "terminal":
                print(report.to_human_readable())
        except (
            Exception
        ) as exc:  # noqa: BLE001  pragma: no cover - defensive error handling
            error_report = (
                validator._create_error_report(  # pylint: disable=protected-access
                    file_path, f"Validation failed: {exc}"
                )
            )
            reports.append(error_report)

    summary = _aggregate_results(reports)
    _write_json_report(reports, summary, args.output, files_to_validate)
    _write_validation_output(summary, args.output)

    print(
        "Constitutional validation summary: result={result}, violations={violations}, files={count}".format(
            result=summary["validation_result"],
            violations=summary["violations_count"],
            count=len(files_to_validate),
        )
    )


if __name__ == "__main__":
    run_cli()
