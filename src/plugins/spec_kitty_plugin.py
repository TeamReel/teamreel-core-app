"""
project Spec-Kitty Constitutional Validation Plugin

Integrates constitutional validation into spec-kitty CLI workflow,
providing hard-blocking constitutional enforcement at each stage.

SE Principle Focus:
- SRP: Single responsibility for spec-kitty integration
- Loose Coupling: Plugin-based integration via hooks
- Reusability: Constitutional validation reused across workflow stages
"""

import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConstitutionalValidationError(Exception):
    """Exception raised when constitutional validation fails."""

    pass


# Import validators for plugin integration
try:
    from ..spec_validator import SpecValidator
    from ..plan_validator import PlanValidator
    from ..task_validator import TaskValidator
except ImportError:
    # Fallback for testing or direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from spec_validator import SpecValidator
    from plan_validator import PlanValidator
    from task_validator import TaskValidator


class SpecKittyStage(Enum):
    """Spec-kitty workflow stages for constitutional validation"""

    SPECIFY = "specify"  # Feature specification stage
    PLAN = "plan"  # Implementation planning stage
    TASKS = "tasks"  # Task breakdown stage
    IMPLEMENT = "implement"  # Implementation stage
    REVIEW = "review"  # Review stage


class ValidationSeverity(Enum):
    """Constitutional validation severity levels"""

    BLOCKING = "blocking"  # Hard block - prevents progression
    WARNING = "warning"  # Soft warning - allows progression with notice
    INFO = "info"  # Informational - just logs


@dataclass
class ValidationResult:
    """Result of constitutional validation at a workflow stage"""

    stage: SpecKittyStage
    passed: bool
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    suggestions: List[str]
    validation_time: float
    error_message: Optional[str] = None


class SpecKittyConstitutionalPlugin:
    """Main plugin class for spec-kitty constitutional integration"""

    # Plugin metadata
    name = "constitutional-validation"
    version = "1.0.0"
    description = "Constitutional validation integration for spec-kitty workflow"

    def __init__(self, feature_dir: str = None, config_path: str = None):
        self.feature_dir = (
            Path(feature_dir) if feature_dir else self._find_feature_dir()
        )
        self.config_path = config_path or self._find_config_path()
        self.constitutional_validator = self._load_constitutional_validator()
        self.plugin_config = self._load_plugin_config()

        # Performance tracking
        self.max_validation_time = 30.0  # seconds

    def _find_feature_dir(self) -> Path:
        """Find the current feature directory (kitty-specs/feature-name)"""
        current_dir = Path.cwd()

        # Look for kitty-specs directory structure
        for parent in [current_dir] + list(current_dir.parents):
            kitty_specs = parent / "kitty-specs"
            if kitty_specs.exists():
                # Find the feature directory within kitty-specs
                for feature_dir in kitty_specs.iterdir():
                    if feature_dir.is_dir() and not feature_dir.name.startswith("."):
                        return feature_dir

        # Fallback to current directory
        return current_dir

    def _find_config_path(self) -> str:
        """Find the constitutional configuration path"""
        # Look for .kittify config in current directory or parents
        current_dir = Path.cwd()

        for parent in [current_dir] + list(current_dir.parents):
            config_dir = parent / ".kittify" / "config"
            if config_dir.exists():
                return str(config_dir)

        # Fallback
        return str(current_dir / ".kittify" / "config")

    def _load_constitutional_validator(self):
        """Load the constitutional validation engine from WP01"""
        try:
            # Import the constitutional validator from WP01
            sys.path.insert(0, str(Path.cwd() / "src"))
            from constitutional_validator import ConstitutionalValidator

            return ConstitutionalValidator()
        except ImportError as e:
            print(f"⚠️  Warning: Constitutional validator not available: {e}")
            print("💡 Make sure WP01 Constitutional Core Engine is implemented")
            return None

    def _load_plugin_config(self) -> Dict[str, Any]:
        """Load plugin-specific configuration"""
        config = {
            "validation_stages": {
                SpecKittyStage.SPECIFY: {
                    "enabled": True,
                    "blocking": True,
                    "checks": [
                        "naming_conventions",
                        "required_sections",
                        "se_principles",
                    ],
                },
                SpecKittyStage.PLAN: {
                    "enabled": True,
                    "blocking": True,
                    "checks": [
                        "architecture_compliance",
                        "quality_gates",
                        "se_principles",
                    ],
                },
                SpecKittyStage.TASKS: {
                    "enabled": True,
                    "blocking": True,
                    "checks": [
                        "task_structure",
                        "dependencies",
                        "constitutional_alignment",
                    ],
                },
                SpecKittyStage.IMPLEMENT: {
                    "enabled": True,
                    "blocking": False,  # Warnings only during implementation
                    "checks": ["code_quality", "se_principles", "quality_gates"],
                },
                SpecKittyStage.REVIEW: {
                    "enabled": True,
                    "blocking": True,
                    "checks": [
                        "completeness",
                        "quality_gates",
                        "constitutional_compliance",
                    ],
                },
            },
            "performance": {
                "max_validation_time": 30.0,
                "parallel_validation": True,
                "cache_results": True,
            },
            "reporting": {
                "format": "terminal",  # terminal, json, github
                "verbose": True,
                "show_suggestions": True,
            },
        }

        # Try to load custom config if available
        config_file = Path(self.config_path) / "spec_kitty_plugin.yaml"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    custom_config = yaml.safe_load(f)
                    config.update(custom_config)
            except Exception as e:
                print(f"⚠️  Warning: Failed to load plugin config: {e}")

        return config

    # Spec-kitty CLI Integration Hooks

    def hook_specify_validate(self, spec_file: str) -> ValidationResult:
        """Hook for spec-kitty specify command validation"""
        import time

        start_time = time.time()

        try:
            if not self.plugin_config["validation_stages"][SpecKittyStage.SPECIFY][
                "enabled"
            ]:
                return ValidationResult(
                    stage=SpecKittyStage.SPECIFY,
                    passed=True,
                    violations=[],
                    warnings=[],
                    suggestions=[],
                    validation_time=0.0,
                )

            violations = []
            warnings = []
            suggestions = []

            # Use the imported SpecValidator for validation
            try:
                spec_validator = SpecValidator()
                validation_result = spec_validator.validate_spec(spec_file)

                if hasattr(validation_result, "is_valid") and hasattr(
                    validation_result, "issues"
                ):
                    # Handle validation result - raise exception if validation fails
                    if not validation_result.is_valid:
                        error_messages = []
                        for issue in validation_result.issues:
                            if hasattr(issue, "message"):
                                error_messages.append(issue.message)
                            else:
                                error_messages.append(str(issue))

                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )
                else:
                    # Fallback validation if validator doesn't return expected format
                    self._fallback_spec_validation(
                        spec_file, violations, warnings, suggestions
                    )

                    # Check if fallback validation found violations - if so, raise exception
                    if violations:
                        error_messages = [v.get("message", str(v)) for v in violations]
                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )

            except ImportError as e:
                # Fallback to original validation logic if validator import fails
                print(
                    f"⚠️  Warning: SpecValidator import failed: {e}, using fallback validation"
                )
                self._fallback_spec_validation(
                    spec_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )
            except AttributeError as e:
                # Fallback if validator doesn't have expected methods
                print(
                    f"⚠️  Warning: SpecValidator missing methods: {e}, using fallback validation"
                )
                self._fallback_spec_validation(
                    spec_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )

            validation_time = time.time() - start_time

            # Check performance requirement
            if validation_time > self.max_validation_time:
                warnings.append(
                    {
                        "type": "performance",
                        "message": f"Specification validation took {validation_time:.2f}s (max: {self.max_validation_time}s)",
                        "severity": "LOW",
                    }
                )

            return ValidationResult(
                stage=SpecKittyStage.SPECIFY,
                passed=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=validation_time,
            )

        except ConstitutionalValidationError:
            # Let constitutional validation errors propagate up
            raise
        except Exception as e:
            return ValidationResult(
                stage=SpecKittyStage.SPECIFY,
                passed=False,
                violations=[
                    {
                        "type": "validation_error",
                        "message": f"Validation failed: {str(e)}",
                        "severity": "HIGH",
                    }
                ],
                warnings=[],
                suggestions=[],
                validation_time=time.time() - start_time,
            )

    def _fallback_spec_validation(
        self, spec_file: str, violations: list, warnings: list, suggestions: list
    ):
        """Fallback validation logic for specifications"""
        # Validate spec file exists and is readable
        if not os.path.exists(spec_file):
            violations.append(
                {
                    "type": "missing_file",
                    "message": f"Specification file not found: {spec_file}",
                    "severity": "HIGH",
                }
            )
        else:
            # Load and validate spec content
            with open(spec_file, "r", encoding="utf-8") as f:
                spec_content = f.read()

            # Check required sections
            required_sections = [
                "## Interface Contracts",
                "## SE Principles Compliance",
                "## User Stories",
                "## Success Criteria",
            ]

            for section in required_sections:
                if section not in spec_content:
                    violations.append(
                        {
                            "type": "missing_section",
                            "message": f"Required section missing: {section}",
                            "severity": "HIGH",
                            "suggestion": f"Add {section} section to specification",
                        }
                    )

            # Check SE principles compliance section
            if "## SE Principles Compliance" in spec_content:
                se_principles = [
                    "Single Responsibility Principle",
                    "Encapsulation",
                    "Loose Coupling",
                    "Reusability",
                    "Portability",
                    "Defensibility",
                    "Maintainability",
                    "Simplicity",
                ]

                for principle in se_principles:
                    if principle not in spec_content:
                        warnings.append(
                            {
                                "type": "missing_se_principle",
                                "message": f"SE principle not addressed: {principle}",
                                "severity": "MEDIUM",
                            }
                        )

            # Check naming conventions in spec
            if "kebab-case" not in spec_content or "snake_case" not in spec_content:
                suggestions.append(
                    "Include project naming convention requirements in specification"
                )

    def hook_plan_validate(self, plan_file: str) -> ValidationResult:
        """Hook for spec-kitty plan command validation"""
        import time

        start_time = time.time()

        try:
            if not self.plugin_config["validation_stages"][SpecKittyStage.PLAN][
                "enabled"
            ]:
                return ValidationResult(
                    stage=SpecKittyStage.PLAN,
                    passed=True,
                    violations=[],
                    warnings=[],
                    suggestions=[],
                    validation_time=0.0,
                )

            violations = []
            warnings = []
            suggestions = []

            # Use the imported PlanValidator for validation
            try:
                plan_validator = PlanValidator()
                validation_result = plan_validator.validate_plan(plan_file)

                if hasattr(validation_result, "is_valid") and hasattr(
                    validation_result, "issues"
                ):
                    # Handle validation result - raise exception if validation fails
                    if not validation_result.is_valid:
                        error_messages = []
                        for issue in validation_result.issues:
                            if hasattr(issue, "message"):
                                error_messages.append(issue.message)
                            else:
                                error_messages.append(str(issue))

                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )
                else:
                    # Fallback validation if validator doesn't return expected format
                    self._fallback_plan_validation(
                        plan_file, violations, warnings, suggestions
                    )

                    # Check if fallback validation found violations - if so, raise exception
                    if violations:
                        error_messages = [v.get("message", str(v)) for v in violations]
                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )

            except ImportError as e:
                # Fallback to original validation logic if validator import fails
                print(
                    f"⚠️  Warning: PlanValidator import failed: {e}, using fallback validation"
                )
                self._fallback_plan_validation(
                    plan_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )
            except AttributeError as e:
                # Fallback if validator doesn't have expected methods
                print(
                    f"⚠️  Warning: PlanValidator missing methods: {e}, using fallback validation"
                )
                self._fallback_plan_validation(
                    plan_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )

            validation_time = time.time() - start_time

            return ValidationResult(
                stage=SpecKittyStage.PLAN,
                passed=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=validation_time,
            )

        except ConstitutionalValidationError:
            # Let constitutional validation errors propagate up
            raise
        except Exception as e:
            return ValidationResult(
                stage=SpecKittyStage.PLAN,
                passed=False,
                violations=[],
                warnings=[],
                suggestions=[],
                validation_time=time.time() - start_time,
                error_message=str(e),
            )

    def _fallback_plan_validation(
        self, plan_file: str, violations: list, warnings: list, suggestions: list
    ):
        """Fallback validation logic for plans"""
        if not os.path.exists(plan_file):
            violations.append(
                {
                    "type": "missing_file",
                    "message": f"Plan file not found: {plan_file}",
                    "severity": "HIGH",
                }
            )
        else:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_content = f.read()

            # Check required plan sections
            required_sections = [
                "## Architecture",
                "## SE Principles Integration",
                "## Quality Gates",
                "## Testing Strategy",
            ]

            for section in required_sections:
                if section not in plan_content:
                    violations.append(
                        {
                            "type": "missing_section",
                            "message": f"Required plan section missing: {section}",
                            "severity": "HIGH",
                            "suggestion": f"Add {section} section to implementation plan",
                        }
                    )

            # Check for quality gate integration
            quality_gates = ["coverage", "complexity", "security", "naming"]
            missing_gates = []
            for gate in quality_gates:
                if gate not in plan_content.lower():
                    missing_gates.append(gate)

            if missing_gates:
                warnings.append(
                    {
                        "type": "missing_quality_gates",
                        "message": f"Quality gates not mentioned: {', '.join(missing_gates)}",
                        "severity": "MEDIUM",
                    }
                )

            # Check for SE principles architecture compliance
            if "distributed plugin architecture" not in plan_content.lower():
                suggestions.append(
                    "Consider distributed plugin architecture for better SE principles compliance"
                )

    def hook_tasks_validate(self, tasks_file: str) -> ValidationResult:
        """Hook for spec-kitty tasks command validation"""
        import time

        start_time = time.time()

        try:
            if not self.plugin_config["validation_stages"][SpecKittyStage.TASKS][
                "enabled"
            ]:
                return ValidationResult(
                    stage=SpecKittyStage.TASKS,
                    passed=True,
                    violations=[],
                    warnings=[],
                    suggestions=[],
                    validation_time=0.0,
                )

            violations = []
            warnings = []
            suggestions = []

            # Use the imported TaskValidator for validation
            try:
                task_validator = TaskValidator()
                validation_result = task_validator.validate_task(tasks_file)

                if hasattr(validation_result, "is_valid") and hasattr(
                    validation_result, "issues"
                ):
                    # Handle validation result - raise exception if validation fails
                    if not validation_result.is_valid:
                        error_messages = []
                        for issue in validation_result.issues:
                            if hasattr(issue, "message"):
                                error_messages.append(issue.message)
                            else:
                                error_messages.append(str(issue))

                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )
                else:
                    # Fallback validation if validator doesn't return expected format
                    self._fallback_task_validation(
                        tasks_file, violations, warnings, suggestions
                    )

                    # Check if fallback validation found violations - if so, raise exception
                    if violations:
                        error_messages = [v.get("message", str(v)) for v in violations]
                        error_summary = "; ".join(error_messages)
                        raise ConstitutionalValidationError(
                            f"Constitutional validation failed: {error_summary}"
                        )

            except ImportError as e:
                # Fallback to original validation logic if validator import fails
                print(
                    f"⚠️  Warning: TaskValidator import failed: {e}, using fallback validation"
                )
                self._fallback_task_validation(
                    tasks_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )
            except AttributeError as e:
                # Fallback if validator doesn't have expected methods
                print(
                    f"⚠️  Warning: TaskValidator missing methods: {e}, using fallback validation"
                )
                self._fallback_task_validation(
                    tasks_file, violations, warnings, suggestions
                )

                # Check if fallback validation found violations - if so, raise exception
                if violations:
                    error_messages = [v.get("message", str(v)) for v in violations]
                    error_summary = "; ".join(error_messages)
                    raise ConstitutionalValidationError(
                        f"Constitutional validation failed: {error_summary}"
                    )

            validation_time = time.time() - start_time

            return ValidationResult(
                stage=SpecKittyStage.TASKS,
                passed=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=validation_time,
            )

        except ConstitutionalValidationError:
            # Let constitutional validation errors propagate up
            raise
        except Exception as e:
            return ValidationResult(
                stage=SpecKittyStage.TASKS,
                passed=False,
                violations=[],
                warnings=[],
                suggestions=[],
                validation_time=time.time() - start_time,
                error_message=str(e),
            )

    def _fallback_task_validation(
        self, tasks_file: str, violations: list, warnings: list, suggestions: list
    ):
        """Fallback validation logic for tasks"""
        if not os.path.exists(tasks_file):
            violations.append(
                {
                    "type": "missing_file",
                    "message": f"Tasks file not found: {tasks_file}",
                    "severity": "HIGH",
                }
            )
        else:
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks_content = f.read()

            # Check for required task structure
            if "## Work Package" not in tasks_content:
                violations.append(
                    {
                        "type": "missing_structure",
                        "message": "Work package structure not found in tasks",
                        "severity": "HIGH",
                    }
                )

            # Check for constitutional compliance tasks
            constitutional_keywords = [
                "constitutional validation",
                "se principles",
                "quality gates",
                "compliance",
            ]
            missing_constitutional = []
            for keyword in constitutional_keywords:
                if keyword not in tasks_content.lower():
                    missing_constitutional.append(keyword)

            if missing_constitutional:
                warnings.append(
                    {
                        "type": "missing_constitutional_tasks",
                        "message": f"Constitutional aspects not addressed in tasks: {', '.join(missing_constitutional)}",
                        "severity": "MEDIUM",
                    }
                )

            # Check for proper task dependencies
            if "Dependencies:" not in tasks_content:
                suggestions.append(
                    "Include task dependencies for better project coordination"
                )

            # Check for test tasks
            if "test" not in tasks_content.lower():
                warnings.append(
                    {
                        "type": "missing_tests",
                        "message": "No testing tasks found in task breakdown",
                        "severity": "MEDIUM",
                    }
                )

    def hook_implement_validate(
        self, implementation_files: List[str]
    ) -> ValidationResult:
        """Hook for spec-kitty implement command validation"""
        import time

        start_time = time.time()

        try:
            if not self.plugin_config["validation_stages"][SpecKittyStage.IMPLEMENT][
                "enabled"
            ]:
                return ValidationResult(
                    stage=SpecKittyStage.IMPLEMENT,
                    passed=True,
                    violations=[],
                    warnings=[],
                    suggestions=[],
                    validation_time=0.0,
                )

            violations = []
            warnings = []
            suggestions = []

            # Use constitutional validator from WP01 if available
            if self.constitutional_validator:
                for file_path in implementation_files:
                    if os.path.exists(file_path):
                        try:
                            file_violations = (
                                self.constitutional_validator.validate_file(file_path)
                            )
                            for violation in file_violations:
                                violations.append(
                                    {
                                        "type": "constitutional_violation",
                                        "file": file_path,
                                        "message": str(violation),
                                        "severity": "HIGH",
                                    }
                                )
                        except Exception as e:
                            warnings.append(
                                {
                                    "type": "validation_error",
                                    "file": file_path,
                                    "message": f"Could not validate file: {e}",
                                    "severity": "LOW",
                                }
                            )
            else:
                suggestions.append(
                    "Constitutional validator not available - install WP01 Constitutional Core Engine"
                )

            validation_time = time.time() - start_time

            return ValidationResult(
                stage=SpecKittyStage.IMPLEMENT,
                passed=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=validation_time,
            )

        except Exception as e:
            return ValidationResult(
                stage=SpecKittyStage.IMPLEMENT,
                passed=False,
                violations=[],
                warnings=[],
                suggestions=[],
                validation_time=time.time() - start_time,
                error_message=str(e),
            )

    # Reporting and CLI Integration

    def format_validation_report(
        self, result: ValidationResult, format_type: str = "terminal"
    ) -> str:
        """Format validation result for display"""
        if format_type == "terminal":
            return self._format_terminal_report(result)
        elif format_type == "json":
            return self._format_json_report(result)
        else:
            return self._format_plain_report(result)

    def _format_terminal_report(self, result: ValidationResult) -> str:
        """Format validation result for terminal display"""
        lines = []

        # Header
        stage_name = result.stage.value.title()
        if result.passed:
            lines.append(f"✅ {stage_name} Constitutional Validation: PASSED")
        else:
            lines.append(f"❌ {stage_name} Constitutional Validation: FAILED")

        lines.append("=" * 50)

        # Violations (blocking)
        if result.violations:
            lines.append(f"\n🚨 Blocking Violations ({len(result.violations)}):")
            for i, violation in enumerate(result.violations, 1):
                lines.append(f"  {i}. {violation['message']}")
                if "suggestion" in violation:
                    lines.append(f"     💡 {violation['suggestion']}")

        # Warnings (non-blocking)
        if result.warnings:
            lines.append(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                lines.append(f"  {i}. {warning['message']}")

        # Suggestions
        if result.suggestions:
            lines.append("\n💡 Suggestions:")
            for i, suggestion in enumerate(result.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        # Performance info
        lines.append(f"\n⏱️  Validation completed in {result.validation_time:.2f}s")

        # Error message
        if result.error_message:
            lines.append(f"\n❌ Error: {result.error_message}")

        return "\n".join(lines)

    def _format_json_report(self, result: ValidationResult) -> str:
        """Format validation result as JSON"""
        return json.dumps(
            {
                "stage": result.stage.value,
                "passed": result.passed,
                "violations": result.violations,
                "warnings": result.warnings,
                "suggestions": result.suggestions,
                "validation_time": result.validation_time,
                "error_message": result.error_message,
            },
            indent=2,
        )

    def _format_plain_report(self, result: ValidationResult) -> str:
        """Format validation result as plain text"""
        lines = []
        lines.append(f"Stage: {result.stage.value}")
        lines.append(f"Status: {'PASSED' if result.passed else 'FAILED'}")
        lines.append(f"Violations: {len(result.violations)}")
        lines.append(f"Warnings: {len(result.warnings)}")
        lines.append(f"Validation Time: {result.validation_time:.2f}s")

        if result.violations:
            lines.append("\nViolations:")
            for violation in result.violations:
                lines.append(f"- {violation['message']}")

        return "\n".join(lines)

    # CLI Command Integration

    # Plugin hook methods for spec-kitty integration
    def on_spec_created(self, spec_path: str) -> ValidationResult:
        """Hook called when a new specification is created."""
        return self.hook_specify_validate(spec_path)

    def on_plan_created(self, plan_path: str) -> ValidationResult:
        """Hook called when a new implementation plan is created."""
        return self.hook_plan_validate(plan_path)

    def on_task_created(self, task_path: str) -> ValidationResult:
        """Hook called when new tasks are created."""
        return self.hook_tasks_validate(task_path)

    def cli_validate_workflow_stage(self, stage: str, file_path: str) -> int:
        """CLI entry point for workflow stage validation"""
        try:
            stage_enum = SpecKittyStage(stage.lower())
        except ValueError:
            print(f"❌ Unknown workflow stage: {stage}")
            return 1

        # Route to appropriate validation hook
        if stage_enum == SpecKittyStage.SPECIFY:
            result = self.hook_specify_validate(file_path)
        elif stage_enum == SpecKittyStage.PLAN:
            result = self.hook_plan_validate(file_path)
        elif stage_enum == SpecKittyStage.TASKS:
            result = self.hook_tasks_validate(file_path)
        elif stage_enum == SpecKittyStage.IMPLEMENT:
            # For implement, file_path should be a comma-separated list
            files = [f.strip() for f in file_path.split(",")]
            result = self.hook_implement_validate(files)
        else:
            print(f"❌ Validation not implemented for stage: {stage}")
            return 1

        # Display result
        report = self.format_validation_report(result, "terminal")
        print(report)

        # Return appropriate exit code
        if result.error_message:
            return 2  # Error
        elif not result.passed:
            return 1  # Failed validation
        else:
            return 0  # Success


# Factory functions for easy instantiation
def create_spec_kitty_plugin(feature_dir: str = None) -> SpecKittyConstitutionalPlugin:
    """Create a new spec-kitty constitutional plugin instance"""
    return SpecKittyConstitutionalPlugin(feature_dir)


# CLI interface for testing and integration
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="project Spec-Kitty Constitutional Validation Plugin"
    )
    parser.add_argument(
        "stage",
        choices=["specify", "plan", "tasks", "implement"],
        help="Workflow stage to validate",
    )
    parser.add_argument(
        "file", help="File(s) to validate (comma-separated for implement)"
    )
    parser.add_argument("--feature-dir", help="Feature directory path")
    parser.add_argument(
        "--format",
        choices=["terminal", "json", "plain"],
        default="terminal",
        help="Output format",
    )

    args = parser.parse_args()

    # Create plugin instance
    plugin = create_spec_kitty_plugin(args.feature_dir)

    # Run validation
    exit_code = plugin.cli_validate_workflow_stage(args.stage, args.file)
    sys.exit(exit_code)
