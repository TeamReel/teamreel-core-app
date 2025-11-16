#!/usr/bin/env python3
"""
Spec Validator - Constitutional Compliance for Specifications

This module validates specification documents against TeamReel's constitutional
requirements, ensuring all specifications include mandatory constitutional compliance
elements before being approved for implementation planning.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import re
import yaml
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
    """Validation severity levels for specification validation"""

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


class SpecValidationCategory(Enum):
    """Categories of specification validation checks."""

    CONSTITUTIONAL_CHECKLIST = "constitutional_checklist"
    SE_PRINCIPLES = "se_principles"
    ARCHITECTURE_COMPLIANCE = "architecture_compliance"
    NAMING_CONVENTIONS = "naming_conventions"
    USER_STORY_FORMAT = "user_story_format"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    QUALITY_GATES = "quality_gates"
    TEMPLATE_STRUCTURE = "template_structure"


@dataclass
class SpecSection:
    """Represents a section of a specification document."""

    title: str
    content: str
    line_start: int
    line_end: int
    level: int  # Header level (1-6)


@dataclass
@dataclass
class SpecValidationIssue:
    """Represents a validation issue in a specification."""

    category: SpecValidationCategory
    level: ValidationLevel
    message: str
    line_number: Optional[int] = None
    section: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
@dataclass
class SpecValidationReport:
    """Complete validation report for a specification."""

    file_path: str
    issues: List[SpecValidationIssue] = field(default_factory=list)
    warnings: List[SpecValidationIssue] = field(default_factory=list)
    missing_sections: List[str] = field(default_factory=list)
    is_valid: bool = True
    constitutional_compliance_score: float = 0.0

    def add_issue(self, issue: SpecValidationIssue):
        """Add a validation issue."""
        if issue.level == ValidationLevel.ERROR:
            self.issues.append(issue)
            self.is_valid = False
        else:
            self.warnings.append(issue)


class SpecValidator:
    """Validates specification documents for constitutional compliance."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the spec validator."""
        # Use default path if None provided
        effective_config_path = config_path or ".kittify/config/se_rules.yaml"
        self.constitutional_validator = ConstitutionalValidator(effective_config_path)
        self.config = self._load_config(config_path)

        # Required sections for TeamReel specifications
        self.required_sections = {
            "Constitutional Enforcement Integration",
            "User Story",
            "Acceptance Criteria",
            "SE Principles Compliance",
            "Architecture Requirements",
            "Quality Gates",
        }

        # Constitutional checklist items that must be present
        self.required_constitutional_items = {
            "Single Responsibility Principle",
            "Open/Closed Principle",
            "Liskov Substitution Principle",
            "Interface Segregation Principle",
            "Dependency Inversion Principle",
            "DRY (Don't Repeat Yourself)",
            "YAGNI (You Aren't Gonna Need It)",
            "KISS (Keep It Simple, Stupid)",
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validation configuration."""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except (yaml.YAMLError, FileNotFoundError, PermissionError) as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")
                # Fall through to default config

        # Default configuration
        return {
            "validation": {
                "require_constitutional_checklist": True,
                "require_se_principles": True,
                "require_architecture_section": True,
                "require_user_story_format": True,
                "min_acceptance_criteria": 3,
                "block_on_missing_sections": True,
                "block_on_constitutional_violations": True,
            }
        }

    def validate_spec(self, spec_path: str) -> SpecValidationReport:
        """Validate a specification document for constitutional compliance."""
        report = SpecValidationReport(file_path=spec_path)

        try:
            content = Path(spec_path).read_text(encoding="utf-8")
            sections = self._parse_sections(content)

            # Validate template structure
            self._validate_template_structure(content, sections, report)

            # Validate constitutional compliance sections
            self._validate_constitutional_sections(content, sections, report)

            # Validate SE principles compliance
            self._validate_se_principles(content, sections, report)

            # Validate architecture compliance
            self._validate_architecture_compliance(content, sections, report)

            # Validate user story format
            self._validate_user_story_format(content, sections, report)

            # Validate acceptance criteria
            self._validate_acceptance_criteria(content, sections, report)

            # Validate naming conventions
            self._validate_naming_conventions(content, report)

            # Calculate constitutional compliance score
            report.constitutional_compliance_score = self._calculate_compliance_score(
                report
            )

        except Exception as e:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.TEMPLATE_STRUCTURE,
                    level=ValidationLevel.ERROR,
                    message=f"Failed to validate specification: {str(e)}",
                )
            )

        return report

    def _parse_sections(self, content: str) -> Dict[str, SpecSection]:
        """Parse markdown sections from specification content."""
        sections = {}
        lines = content.split("\n")
        current_section = None
        section_content = []
        section_start = 0

        for i, line in enumerate(lines):
            # Check for header
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section.title] = SpecSection(
                        title=current_section.title,
                        content="\n".join(section_content),
                        line_start=section_start,
                        line_end=i - 1,
                        level=current_section.level,
                    )

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = SpecSection(title, "", i, i, level)
                section_content = []
                section_start = i
            elif current_section:
                section_content.append(line)

        # Save final section
        if current_section:
            sections[current_section.title] = SpecSection(
                title=current_section.title,
                content="\n".join(section_content),
                line_start=section_start,
                line_end=len(lines) - 1,
                level=current_section.level,
            )

        return sections

    def _validate_template_structure(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate that the specification follows the required template structure."""
        missing_sections = []

        for required_section in self.required_sections:
            # Check for exact match or partial match
            found = False
            for section_title in sections.keys():
                if required_section.lower() in section_title.lower():
                    found = True
                    break

            if not found:
                missing_sections.append(required_section)

        if missing_sections:
            report.missing_sections = missing_sections
            if self.config["validation"]["block_on_missing_sections"]:
                for section in missing_sections:
                    report.add_issue(
                        SpecValidationIssue(
                            category=SpecValidationCategory.TEMPLATE_STRUCTURE,
                            level=ValidationLevel.ERROR,
                            message=f"Required section missing: {section}",
                            suggested_fix=f"Add section: ## {section}",
                        )
                    )

    def _validate_constitutional_sections(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate constitutional enforcement sections."""
        # Check for Constitutional Enforcement Integration section
        constitutional_section = None
        for title, section in sections.items():
            if "constitutional" in title.lower() and "enforcement" in title.lower():
                constitutional_section = section
                break

        if not constitutional_section:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.CONSTITUTIONAL_CHECKLIST,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Constitutional Enforcement Integration' section",
                    suggested_fix="Add section with constitutional compliance checklist",
                )
            )
            return

        # Validate constitutional checklist items
        missing_items = []
        for item in self.required_constitutional_items:
            if item.lower() not in constitutional_section.content.lower():
                missing_items.append(item)

        if missing_items:
            for item in missing_items:
                report.add_issue(
                    SpecValidationIssue(
                        category=SpecValidationCategory.CONSTITUTIONAL_CHECKLIST,
                        level=ValidationLevel.ERROR,
                        message=f"Missing constitutional checklist item: {item}",
                        line_number=constitutional_section.line_start,
                        section="Constitutional Enforcement Integration",
                        suggested_fix=f"Add checklist item: - [ ] **{item}**: [description]",
                    )
                )

    def _validate_se_principles(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate SE principles compliance."""
        se_section = None
        for title, section in sections.items():
            if (
                "se principles" in title.lower()
                or "software engineering" in title.lower()
            ):
                se_section = section
                break

        if not se_section:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.SE_PRINCIPLES,
                    level=ValidationLevel.ERROR,
                    message="Missing 'SE Principles Compliance' section",
                    suggested_fix="Add section documenting how the specification addresses each SE principle",
                )
            )
            return

        # Check that each SE principle is addressed
        for principle in SEPrinciple:
            principle_name = principle.value.replace("_", " ").title()
            if principle_name.lower() not in se_section.content.lower():
                report.add_issue(
                    SpecValidationIssue(
                        category=SpecValidationCategory.SE_PRINCIPLES,
                        level=ValidationLevel.WARNING,
                        message=f"SE principle not explicitly addressed: {principle_name}",
                        line_number=se_section.line_start,
                        section="SE Principles Compliance",
                        suggested_fix=f"Add discussion of how specification addresses {principle_name}",
                    )
                )

    def _validate_architecture_compliance(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate architecture compliance section."""
        arch_section = None
        for title, section in sections.items():
            if "architecture" in title.lower():
                arch_section = section
                break

        if not arch_section:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.ARCHITECTURE_COMPLIANCE,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Architecture Requirements' section",
                    suggested_fix="Add section documenting architectural patterns and compliance requirements",
                )
            )
            return

        # Check for key architectural concepts
        required_concepts = [
            "single responsibility",
            "dependency injection",
            "modular design",
            "separation of concerns",
        ]

        for concept in required_concepts:
            if concept not in arch_section.content.lower():
                report.add_issue(
                    SpecValidationIssue(
                        category=SpecValidationCategory.ARCHITECTURE_COMPLIANCE,
                        level=ValidationLevel.WARNING,
                        message=f"Architecture concept not addressed: {concept}",
                        line_number=arch_section.line_start,
                        section="Architecture Requirements",
                        suggested_fix=f"Add discussion of {concept} in architectural design",
                    )
                )

    def _validate_user_story_format(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate user story format."""
        user_story_section = None
        for title, section in sections.items():
            if "user story" in title.lower():
                user_story_section = section
                break

        if not user_story_section:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.USER_STORY_FORMAT,
                    level=ValidationLevel.ERROR,
                    message="Missing 'User Story' section",
                    suggested_fix="Add user story in format: As a [user], I want [goal] so that [benefit]",
                )
            )
            return

        # Check for proper user story format
        story_pattern = r"As a .+, I want .+ so that .+"
        if not re.search(story_pattern, user_story_section.content, re.IGNORECASE):
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.USER_STORY_FORMAT,
                    level=ValidationLevel.ERROR,
                    message="User story does not follow standard format",
                    line_number=user_story_section.line_start,
                    section="User Story",
                    suggested_fix="Use format: As a [user], I want [goal] so that [benefit]",
                )
            )

    def _validate_acceptance_criteria(
        self,
        content: str,
        sections: Dict[str, SpecSection],
        report: SpecValidationReport,
    ):
        """Validate acceptance criteria."""
        ac_section = None
        for title, section in sections.items():
            if "acceptance criteria" in title.lower():
                ac_section = section
                break

        if not ac_section:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.ACCEPTANCE_CRITERIA,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Acceptance Criteria' section",
                    suggested_fix="Add section with specific, testable acceptance criteria",
                )
            )
            return

        # Count acceptance criteria items
        criteria_count = len(
            re.findall(r"^\s*[-*]\s+", ac_section.content, re.MULTILINE)
        )
        min_criteria = self.config["validation"]["min_acceptance_criteria"]

        if criteria_count < min_criteria:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.ACCEPTANCE_CRITERIA,
                    level=ValidationLevel.WARNING,
                    message=f"Only {criteria_count} acceptance criteria found, minimum {min_criteria} recommended",
                    line_number=ac_section.line_start,
                    section="Acceptance Criteria",
                    suggested_fix=f"Add {min_criteria - criteria_count} more specific acceptance criteria",
                )
            )

    def _validate_naming_conventions(self, content: str, report: SpecValidationReport):
        """Validate that naming conventions are documented."""
        naming_patterns = [
            "snake_case",
            "camelCase",
            "kebab-case",
            "PascalCase",
            "UPPER_SNAKE_CASE",
        ]

        found_patterns = [pattern for pattern in naming_patterns if pattern in content]

        if len(found_patterns) < 2:
            report.add_issue(
                SpecValidationIssue(
                    category=SpecValidationCategory.NAMING_CONVENTIONS,
                    level=ValidationLevel.WARNING,
                    message="Specification should document naming conventions for different contexts",
                    suggested_fix="Add section documenting naming conventions (snake_case, camelCase, etc.)",
                )
            )

    def _calculate_compliance_score(self, report: SpecValidationReport) -> float:
        """Calculate constitutional compliance score (0-100)."""
        total_checks = len(self.required_sections) + len(
            self.required_constitutional_items
        )

        error_count = len(report.issues)
        warning_count = len(report.warnings)

        # Deduct more for errors than warnings
        score = 100.0 - (error_count * 10) - (warning_count * 2)

        return max(0.0, min(100.0, score))

    def validate_multiple_specs(
        self, spec_paths: List[str]
    ) -> Dict[str, SpecValidationReport]:
        """Validate multiple specification files."""
        results = {}
        for spec_path in spec_paths:
            try:
                results[spec_path] = self.validate_spec(spec_path)
            except Exception as e:
                report = SpecValidationReport(file_path=spec_path, is_valid=False)
                report.add_issue(
                    SpecValidationIssue(
                        category=SpecValidationCategory.TEMPLATE_STRUCTURE,
                        level=ValidationLevel.ERROR,
                        message=f"Failed to validate {spec_path}: {str(e)}",
                    )
                )
                results[spec_path] = report

        return results

    def format_report(
        self, report: SpecValidationReport, format_type: str = "terminal"
    ) -> str:
        """Format validation report for output."""
        if format_type == "json":
            import json

            return json.dumps(
                {
                    "file_path": report.file_path,
                    "is_valid": report.is_valid,
                    "compliance_score": report.constitutional_compliance_score,
                    "issues": [
                        {
                            "category": issue.category.value,
                            "level": issue.level.value,
                            "message": issue.message,
                            "line_number": issue.line_number,
                            "section": issue.section,
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
        output.append(f"SPECIFICATION VALIDATION REPORT")
        output.append(f"{'='*60}")
        output.append(f"File: {report.file_path}")
        output.append(f"Valid: {'✅ YES' if report.is_valid else '❌ NO'}")
        output.append(
            f"Constitutional Compliance Score: {report.constitutional_compliance_score:.1f}/100"
        )

        if report.missing_sections:
            output.append(f"\nMissing Required Sections:")
            for section in report.missing_sections:
                output.append(f"  - {section}")

        if report.issues:
            output.append(f"\n❌ ERRORS ({len(report.issues)}):")
            for issue in report.issues:
                output.append(f"  • {issue.message}")
                if issue.section:
                    output.append(f"    Section: {issue.section}")
                if issue.line_number:
                    output.append(f"    Line: {issue.line_number}")
                if issue.suggested_fix:
                    output.append(f"    Fix: {issue.suggested_fix}")
                output.append("")

        if report.warnings:
            output.append(f"\n⚠️  WARNINGS ({len(report.warnings)}):")
            for warning in report.warnings:
                output.append(f"  • {warning.message}")
                if warning.section:
                    output.append(f"    Section: {warning.section}")
                if warning.line_number:
                    output.append(f"    Line: {warning.line_number}")
                if warning.suggested_fix:
                    output.append(f"    Fix: {warning.suggested_fix}")
                output.append("")

        if report.is_valid:
            output.append(
                "✅ Specification meets constitutional compliance requirements!"
            )
        else:
            output.append(
                "❌ Specification must be fixed before proceeding to implementation planning."
            )

        return "\n".join(output)


def main():
    """CLI entry point for spec validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate specifications for constitutional compliance"
    )
    parser.add_argument("specs", nargs="+", help="Specification files to validate")
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

    validator = SpecValidator(args.config)

    all_valid = True
    for spec_path in args.specs:
        report = validator.validate_spec(spec_path)
        print(validator.format_report(report, args.format))

        if not report.is_valid:
            all_valid = False

    if args.strict and not all_valid:
        exit(1)


if __name__ == "__main__":
    main()
