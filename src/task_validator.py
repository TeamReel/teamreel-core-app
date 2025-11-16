#!/usr/bin/env python3
"""
Task Validator - Constitutional Compliance for Task Execution

This module validates task documents and execution environment for constitutional
compliance before tasks are executed, ensuring all tasks meet TeamReel's
constitutional requirements and quality gates.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import re
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from .constitutional_validator import ConstitutionalValidator, ValidationScope
    from .compliance_reporter import ComplianceReport, Violation
    from .violation_detector import ViolationDetector, ViolationType, DetectedViolation
except ImportError:
    # Fallback for direct execution
    from constitutional_validator import ConstitutionalValidator, ValidationScope
    from compliance_reporter import ComplianceReport, Violation
    from violation_detector import ViolationDetector, ViolationType, DetectedViolation


class ValidationLevel(Enum):
    """Validation severity levels for task validation"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SEPrinciple(Enum):
    """Software Engineering Principles"""

    SRP = "single_responsibility_principle"
    ENCAPSULATION = "encapsulation"
    LOOSE_COUPLING = "loose_coupling"
    REUSABILITY = "reusability"
    PORTABILITY = "portability"
    DEFENSIBILITY = "defensibility"
    MAINTAINABILITY = "maintainability"
    SIMPLICITY = "simplicity"


class TaskValidationCategory(Enum):
    """Categories of task validation checks."""

    CONSTITUTIONAL_CHECKLIST = "constitutional_checklist"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    SE_PRINCIPLES_ADHERENCE = "se_principles_adherence"
    IMPLEMENTATION_DETAILS = "implementation_details"
    DEPENDENCY_DEFINITION = "dependency_definition"
    ERROR_HANDLING = "error_handling"
    TESTING_STRATEGY = "testing_strategy"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    QUALITY_GATES_ALIGNMENT = "quality_gates_alignment"
    TASK_STRUCTURE = "task_structure"
    QUALITY_GATES = "quality_gates"
    PRE_EXECUTION_CHECKS = "pre_execution_checks"
    ENVIRONMENT_VALIDATION = "environment_validation"
    DEPENDENCY_VERIFICATION = "dependency_verification"
    TESTING_REQUIREMENTS = "testing_requirements"
    DOCUMENTATION_REQUIREMENTS = "documentation_requirements"


@dataclass
class TaskItem:
    """Represents a single task item."""

    id: str
    title: str
    description: str
    status: str
    priority: str
    work_package: str
    is_parallel: bool = False
    dependencies: List[str] = field(default_factory=list)
    line_number: Optional[int] = None


@dataclass
@dataclass
class TaskValidationIssue:
    """Represents a validation issue in task execution."""

    category: TaskValidationCategory
    level: ValidationLevel
    message: str
    task_id: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None


@dataclass
@dataclass
class TaskValidationReport:
    """Complete validation report for task execution."""

    file_path: str
    issues: List[TaskValidationIssue] = field(default_factory=list)
    warnings: List[TaskValidationIssue] = field(default_factory=list)
    ready_tasks: List[TaskItem] = field(default_factory=list)
    blocked_tasks: List[TaskItem] = field(default_factory=list)
    is_valid: bool = True
    is_ready_for_execution: bool = True
    constitutional_compliance_score: float = 0.0
    environment_readiness_score: float = 0.0
    task_count: int = 0

    def add_issue(self, issue: TaskValidationIssue):
        """Add a validation issue."""
        if issue.level == ValidationLevel.ERROR:
            self.issues.append(issue)
            self.is_valid = False
            self.is_ready_for_execution = False
        else:
            self.warnings.append(issue)


class TaskValidator:
    """Validates task documents and execution environment for constitutional compliance."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the task validator."""
        # Use default path if None provided
        effective_config_path = config_path or ".kittify/config/se_rules.yaml"
        self.constitutional_validator = ConstitutionalValidator(effective_config_path)
        self.config = self._load_config(config_path)

        # Required constitutional checklist items for tasks
        self.required_constitutional_checks = {
            "Single Responsibility Principle": "Each class/function has ONE clear purpose",
            "Open/Closed Principle": "Code is open for extension, closed for modification",
            "Liskov Substitution": "Derived classes are substitutable for base classes",
            "Interface Segregation": "No forced dependencies on unused interfaces",
            "Dependency Inversion": "Depend on abstractions, not concretions",
            "DRY (Don't Repeat Yourself)": "No duplicate code logic",
            "YAGNI (You Aren't Gonna Need It)": "No over-engineering or unused features",
            "KISS (Keep It Simple, Stupid)": "Solutions are as simple as possible",
        }

        # Quality gate commands that should be available
        self.required_quality_commands = {
            "spec-kitty": "spec-kitty verify",
            "pytest": "pytest --cov=. --cov-fail-under=80",
            "ruff": "ruff check .",
            "eslint": "npm run lint",  # For frontend tasks
        }

        # Environment requirements
        self.environment_requirements = {
            "python": "3.11+",
            "node": "18+",  # For frontend tasks
            "git": "2.30+",
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validation configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            "validation": {
                "require_constitutional_checklist": True,
                "require_quality_gates": True,
                "require_testing_strategy": True,
                "require_documentation": True,
                "block_on_environment_issues": True,
                "block_on_missing_dependencies": True,
                "validate_pre_execution": True,
            }
        }

    def validate_task(self, tasks_path: str) -> TaskValidationReport:
        """Validate task document and execution environment for constitutional compliance."""
        report = TaskValidationReport(file_path=tasks_path, is_ready_for_execution=True)

        try:
            content = Path(tasks_path).read_text(encoding="utf-8")
            tasks = self._parse_tasks(content)
            report.task_count = len(tasks)

            # Validate task structure and format
            self._validate_task_structure(content, tasks, report)

            # Validate constitutional checklist presence
            self._validate_constitutional_checklist(content, report)

            # Validate quality gates configuration
            self._validate_quality_gates(content, report)

            # Validate environment readiness
            self._validate_environment(report)

            # Validate dependencies
            self._validate_dependencies(tasks, report)

            # Validate testing requirements
            self._validate_testing_requirements(content, report)

            # Validate documentation requirements
            self._validate_documentation_requirements(content, report)

            # Categorize tasks by readiness
            self._categorize_tasks(tasks, report)

            # Calculate compliance scores
            report.constitutional_compliance_score = self._calculate_compliance_score(
                report
            )
            report.environment_readiness_score = self._calculate_environment_score(
                report
            )

        except Exception as e:
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TASK_STRUCTURE,
                    level=ValidationLevel.ERROR,
                    message=f"Failed to validate tasks: {str(e)}",
                )
            )

        return report

    def _parse_tasks(self, content: str) -> List[TaskItem]:
        """Parse task items from content."""
        tasks = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Look for task items: - [ ] T001 [P] Task description
            task_match = re.match(
                r"^\s*-\s*\[\s*([x\s])\s*\]\s*(T\d+)\s*(\[P\])?\s*(.+)$", line
            )
            if task_match:
                status = (
                    "completed" if task_match.group(1).lower() == "x" else "not_started"
                )
                task_id = task_match.group(2)
                is_parallel = task_match.group(3) is not None
                title = task_match.group(4).strip()

                # Extract work package from context
                work_package = "Unknown"
                for j in range(max(0, i - 10), i):
                    wp_match = re.search(r"Work Package (WP\d+)", lines[j])
                    if wp_match:
                        work_package = wp_match.group(1)
                        break

                tasks.append(
                    TaskItem(
                        id=task_id,
                        title=title,
                        description=title,
                        status=status,
                        priority="P0" if "[P]" in line else "P1",
                        work_package=work_package,
                        is_parallel=is_parallel,
                        line_number=i + 1,
                    )
                )

        return tasks

    def _validate_task_structure(
        self, content: str, tasks: List[TaskItem], report: TaskValidationReport
    ):
        """Validate task structure and format."""
        if not tasks:
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TASK_STRUCTURE,
                    level=ValidationLevel.ERROR,
                    message="No tasks found in document",
                    suggested_fix="Add tasks in format: - [ ] T001 Task description",
                )
            )
            return

        # Check for proper task ID format
        task_ids = set()
        for task in tasks:
            if not re.match(r"^T\d{3}$", task.id):
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.TASK_STRUCTURE,
                        level=ValidationLevel.WARNING,
                        message=f"Task ID format should be T### (3 digits): {task.id}",
                        task_id=task.id,
                        line_number=task.line_number,
                        suggested_fix=f"Change {task.id} to proper format (e.g., T001)",
                    )
                )

            # Check for duplicate task IDs
            if task.id in task_ids:
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.TASK_STRUCTURE,
                        level=ValidationLevel.ERROR,
                        message=f"Duplicate task ID: {task.id}",
                        task_id=task.id,
                        line_number=task.line_number,
                        suggested_fix=f"Use unique task ID for {task.id}",
                    )
                )
            task_ids.add(task.id)

        # Check for work package organization
        work_packages = set(task.work_package for task in tasks)
        if "Unknown" in work_packages:
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TASK_STRUCTURE,
                    level=ValidationLevel.WARNING,
                    message="Some tasks not properly organized under work packages",
                    suggested_fix="Ensure all tasks are under Work Package sections",
                )
            )

    def _validate_constitutional_checklist(
        self, content: str, report: TaskValidationReport
    ):
        """Validate constitutional compliance checklist is present."""
        # Check for constitutional checklist section
        if "constitutional compliance" not in content.lower():
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.CONSTITUTIONAL_CHECKLIST,
                    level=ValidationLevel.ERROR,
                    message="Missing constitutional compliance checklist section",
                    suggested_fix="Add 'Constitutional Compliance (MANDATORY - BLOCKING)' section with SE principles checklist",
                )
            )
            return

        # Check for each required constitutional check
        missing_checks = []
        for (
            check_name,
            check_description,
        ) in self.required_constitutional_checks.items():
            if check_name.lower() not in content.lower():
                missing_checks.append(check_name)

        if missing_checks:
            for check in missing_checks[:3]:  # Limit to first 3 for readability
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.CONSTITUTIONAL_CHECKLIST,
                        level=ValidationLevel.ERROR,
                        message=f"Missing constitutional check: {check}",
                        suggested_fix=f"Add checklist item: - [ ] **{check}**: {self.required_constitutional_checks[check]}",
                    )
                )

    def _validate_quality_gates(self, content: str, report: TaskValidationReport):
        """Validate quality gates and validation commands."""
        # Check for quality gate validation commands section
        if "constitutional validation commands" not in content.lower():
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.QUALITY_GATES,
                    level=ValidationLevel.WARNING,
                    message="Missing constitutional validation commands section",
                    suggested_fix="Add section with spec-kitty verify, pytest, ruff, and linting commands",
                )
            )

        # Check for specific quality gate commands
        missing_commands = []
        for command_name, command_text in self.required_quality_commands.items():
            if command_text.lower() not in content.lower():
                missing_commands.append(command_name)

        if missing_commands:
            for command in missing_commands:
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.QUALITY_GATES,
                        level=ValidationLevel.WARNING,
                        message=f"Missing quality gate command: {command}",
                        suggested_fix=f"Add command: {self.required_quality_commands[command]}",
                    )
                )

    def _validate_environment(self, report: TaskValidationReport):
        """Validate execution environment readiness."""
        # Check for required tools
        for tool, version_req in self.environment_requirements.items():
            if not self._check_tool_availability(tool):
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.ENVIRONMENT_VALIDATION,
                        level=ValidationLevel.ERROR,
                        message=f"Required tool not available: {tool} {version_req}",
                        suggested_fix=f"Install {tool} {version_req} or ensure it's in PATH",
                    )
                )

        # Check for quality gate tools
        for command_name in self.required_quality_commands.keys():
            if command_name in ["eslint"]:  # Skip frontend-specific tools for now
                continue
            if not self._check_tool_availability(command_name):
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.ENVIRONMENT_VALIDATION,
                        level=ValidationLevel.WARNING,
                        message=f"Quality gate tool not available: {command_name}",
                        suggested_fix=f"Install {command_name} or ensure it's available for quality validation",
                    )
                )

    def _check_tool_availability(self, tool: str) -> bool:
        """Check if a tool is available in the system."""
        try:
            if tool == "spec-kitty":
                # Check if spec-kitty is available
                result = subprocess.run(
                    ["spec-kitty", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.returncode == 0
            elif tool in ["python", "pytest", "ruff"]:
                result = subprocess.run(
                    [tool, "--version"], capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            elif tool == "node":
                result = subprocess.run(
                    ["node", "--version"], capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            elif tool == "git":
                result = subprocess.run(
                    ["git", "--version"], capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    [tool, "--help"], capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False

    def _validate_dependencies(
        self, tasks: List[TaskItem], report: TaskValidationReport
    ):
        """Validate task dependencies."""
        task_ids = set(task.id for task in tasks)

        for task in tasks:
            # Extract dependencies from task description
            dep_matches = re.findall(
                r"depends on (T\d+)", task.description, re.IGNORECASE
            )
            task.dependencies = dep_matches

            # Check if dependencies exist
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    report.add_issue(
                        TaskValidationIssue(
                            category=TaskValidationCategory.DEPENDENCY_VERIFICATION,
                            level=ValidationLevel.ERROR,
                            message=f"Task {task.id} depends on non-existent task: {dep_id}",
                            task_id=task.id,
                            line_number=task.line_number,
                            suggested_fix=f"Add task {dep_id} or remove dependency reference",
                        )
                    )

    def _validate_testing_requirements(
        self, content: str, report: TaskValidationReport
    ):
        """Validate testing requirements are documented."""
        testing_indicators = [
            "test",
            "coverage",
            "pytest",
            "unit test",
            "integration test",
        ]

        if not any(indicator in content.lower() for indicator in testing_indicators):
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TESTING_REQUIREMENTS,
                    level=ValidationLevel.WARNING,
                    message="Testing requirements not clearly documented",
                    suggested_fix="Add testing strategy and coverage requirements to completion checklist",
                )
            )

        # Check for specific coverage requirements
        if "80%" not in content and "coverage" in content.lower():
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TESTING_REQUIREMENTS,
                    level=ValidationLevel.WARNING,
                    message="Test coverage threshold not specified",
                    suggested_fix="Add specific coverage requirement (e.g., 80% minimum)",
                )
            )

    def _validate_documentation_requirements(
        self, content: str, report: TaskValidationReport
    ):
        """Validate documentation requirements."""
        doc_indicators = ["documentation", "docstring", "readme", "api documentation"]

        if not any(indicator in content.lower() for indicator in doc_indicators):
            report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.DOCUMENTATION_REQUIREMENTS,
                    level=ValidationLevel.WARNING,
                    message="Documentation requirements not specified",
                    suggested_fix="Add documentation requirements to completion checklist",
                )
            )

    def _categorize_tasks(self, tasks: List[TaskItem], report: TaskValidationReport):
        """Categorize tasks by execution readiness."""
        completed_tasks = set()

        for task in tasks:
            if task.status == "completed":
                completed_tasks.add(task.id)

        for task in tasks:
            if task.status == "completed":
                continue

            # Check if dependencies are met
            dependencies_met = all(dep in completed_tasks for dep in task.dependencies)

            if dependencies_met:
                report.ready_tasks.append(task)
            else:
                report.blocked_tasks.append(task)
                unmet_deps = [
                    dep for dep in task.dependencies if dep not in completed_tasks
                ]
                report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.DEPENDENCY_VERIFICATION,
                        level=ValidationLevel.INFO,
                        message=f"Task {task.id} blocked by dependencies: {', '.join(unmet_deps)}",
                        task_id=task.id,
                        line_number=task.line_number,
                        suggested_fix=f"Complete dependencies first: {', '.join(unmet_deps)}",
                    )
                )

    def _calculate_compliance_score(self, report: TaskValidationReport) -> float:
        """Calculate constitutional compliance score (0-100)."""
        total_checks = len(self.required_constitutional_checks)

        error_count = len(
            [
                issue
                for issue in report.issues
                if issue.category == TaskValidationCategory.CONSTITUTIONAL_CHECKLIST
            ]
        )
        warning_count = len(
            [
                issue
                for issue in report.warnings
                if issue.category == TaskValidationCategory.CONSTITUTIONAL_CHECKLIST
            ]
        )

        # Deduct more for errors than warnings
        score = 100.0 - (error_count * 20) - (warning_count * 5)

        return max(0.0, min(100.0, score))

    def _calculate_environment_score(self, report: TaskValidationReport) -> float:
        """Calculate environment readiness score (0-100)."""
        total_requirements = len(self.environment_requirements) + len(
            self.required_quality_commands
        )

        error_count = len(
            [
                issue
                for issue in report.issues
                if issue.category == TaskValidationCategory.ENVIRONMENT_VALIDATION
            ]
        )
        warning_count = len(
            [
                issue
                for issue in report.warnings
                if issue.category == TaskValidationCategory.ENVIRONMENT_VALIDATION
            ]
        )

        score = 100.0 - (error_count * 25) - (warning_count * 10)

        return max(0.0, min(100.0, score))

    def validate_single_task(
        self, task_id: str, tasks_path: str
    ) -> TaskValidationReport:
        """Validate a single task for execution readiness."""
        full_report = self.validate_task(tasks_path)

        # Filter for specific task
        task_report = TaskValidationReport(
            file_path=full_report.file_path, is_valid=True, is_ready_for_execution=True
        )

        # Find the specific task
        target_task = None
        for task in full_report.ready_tasks + full_report.blocked_tasks:
            if task.id == task_id:
                target_task = task
                break

        if not target_task:
            task_report.add_issue(
                TaskValidationIssue(
                    category=TaskValidationCategory.TASK_STRUCTURE,
                    level=ValidationLevel.ERROR,
                    message=f"Task {task_id} not found",
                    task_id=task_id,
                )
            )
        else:
            # Check if task is ready for execution
            if target_task in full_report.blocked_tasks:
                task_report.is_ready_for_execution = False
                task_report.add_issue(
                    TaskValidationIssue(
                        category=TaskValidationCategory.DEPENDENCY_VERIFICATION,
                        level=ValidationLevel.ERROR,
                        message=f"Task {task_id} is blocked by unmet dependencies",
                        task_id=task_id,
                    )
                )
            else:
                task_report.ready_tasks.append(target_task)

        # Include relevant issues from full report
        for issue in full_report.issues + full_report.warnings:
            if issue.task_id == task_id or issue.task_id is None:
                task_report.add_issue(issue)

        task_report.constitutional_compliance_score = (
            full_report.constitutional_compliance_score
        )
        task_report.environment_readiness_score = (
            full_report.environment_readiness_score
        )

        return task_report

    def format_report(
        self, report: TaskValidationReport, format_type: str = "terminal"
    ) -> str:
        """Format validation report for output."""
        if format_type == "json":
            import json

            return json.dumps(
                {
                    "file_path": report.file_path,
                    "is_valid": report.is_valid,
                    "is_ready_for_execution": report.is_ready_for_execution,
                    "compliance_score": report.constitutional_compliance_score,
                    "environment_score": report.environment_readiness_score,
                    "task_count": report.task_count,
                    "ready_tasks": len(report.ready_tasks),
                    "blocked_tasks": len(report.blocked_tasks),
                    "issues": [
                        {
                            "category": issue.category.value,
                            "level": issue.level.value,
                            "message": issue.message,
                            "task_id": issue.task_id,
                            "line_number": issue.line_number,
                            "suggested_fix": issue.suggested_fix,
                        }
                        for issue in report.issues + report.warnings
                    ],
                },
                indent=2,
            )

        # Terminal format
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"TASK VALIDATION REPORT")
        output.append(f"{'='*60}")
        output.append(f"File: {report.file_path}")
        output.append(f"Valid: {'✅ YES' if report.is_valid else '❌ NO'}")
        output.append(
            f"Ready for Execution: {'✅ YES' if report.is_ready_for_execution else '❌ NO'}"
        )
        output.append(
            f"Constitutional Compliance Score: {report.constitutional_compliance_score:.1f}/100"
        )
        output.append(
            f"Environment Readiness Score: {report.environment_readiness_score:.1f}/100"
        )

        if report.task_count > 0:
            output.append(f"\nTask Summary:")
            output.append(f"  Total Tasks: {report.task_count}")
            output.append(f"  Ready Tasks: {len(report.ready_tasks)}")
            output.append(f"  Blocked Tasks: {len(report.blocked_tasks)}")

        if report.ready_tasks:
            output.append(f"\n✅ READY TASKS ({len(report.ready_tasks)}):")
            for task in report.ready_tasks[:5]:  # Limit display
                output.append(f"  • {task.id}: {task.title}")

        if report.blocked_tasks:
            output.append(f"\n🚫 BLOCKED TASKS ({len(report.blocked_tasks)}):")
            for task in report.blocked_tasks[:5]:  # Limit display
                deps = ", ".join(task.dependencies) if task.dependencies else "unknown"
                output.append(f"  • {task.id}: {task.title} (depends on: {deps})")

        if report.issues:
            output.append(f"\n❌ ERRORS ({len(report.issues)}):")
            for issue in report.issues:
                output.append(f"  • {issue.message}")
                if issue.task_id:
                    output.append(f"    Task: {issue.task_id}")
                if issue.line_number:
                    output.append(f"    Line: {issue.line_number}")
                if issue.suggested_fix:
                    output.append(f"    Fix: {issue.suggested_fix}")
                output.append("")

        if report.warnings:
            output.append(f"\n⚠️  WARNINGS ({len(report.warnings)}):")
            for warning in report.warnings[:5]:  # Limit display
                output.append(f"  • {warning.message}")
                if warning.task_id:
                    output.append(f"    Task: {warning.task_id}")
                if warning.suggested_fix:
                    output.append(f"    Fix: {warning.suggested_fix}")
                output.append("")

        if report.is_ready_for_execution:
            output.append("✅ Tasks are ready for constitutional execution!")
        else:
            output.append("❌ Tasks must be fixed before execution can proceed.")

        return "\n".join(output)


def main():
    """CLI entry point for task validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate tasks for constitutional compliance and execution readiness"
    )
    parser.add_argument("tasks", help="Tasks file to validate")
    parser.add_argument("--task-id", help="Validate specific task ID")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Exit with error code if validation fails"
    )

    args = parser.parse_args()

    validator = TaskValidator(args.config)

    if args.task_id:
        report = validator.validate_single_task(args.task_id, args.tasks)
    else:
        report = validator.validate_task(args.tasks)

    print(validator.format_report(report, args.format))

    if args.strict and not report.is_ready_for_execution:
        exit(1)


if __name__ == "__main__":
    main()
