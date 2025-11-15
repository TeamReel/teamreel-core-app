#!/usr/bin/env python3
"""
Plan Validator - Constitutional Compliance for Implementation Plans

This module validates implementation plan documents against TeamReel's constitutional
requirements, ensuring all plans include proper architectural design, SE principles
compliance, and quality gates before tasks are generated.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from constitutional_validator import (
    ConstitutionalValidator,
    ValidationResult,
    ValidationLevel,
    SEPrinciple,
)


class PlanValidationCategory(Enum):
    """Categories of plan validation checks."""

    ARCHITECTURE_DESIGN = "architecture_design"
    SE_PRINCIPLES_COMPLIANCE = "se_principles_compliance"
    QUALITY_GATES = "quality_gates"
    IMPLEMENTATION_APPROACH = "implementation_approach"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    TESTING_STRATEGY = "testing_strategy"
    RISK_MITIGATION = "risk_mitigation"
    TEMPLATE_STRUCTURE = "template_structure"


@dataclass
class PlanSection:
    """Represents a section of an implementation plan."""

    title: str
    content: str
    line_start: int
    line_end: int
    level: int  # Header level (1-6)
    subsections: List["PlanSection"] = field(default_factory=list)


@dataclass
class PlanValidationIssue:
    """Represents a validation issue in an implementation plan."""

    category: PlanValidationCategory
    level: ValidationLevel
    message: str
    line_number: Optional[int] = None
    section: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class PlanValidationReport:
    """Complete validation report for an implementation plan."""

    file_path: str
    is_valid: bool
    issues: List[PlanValidationIssue] = field(default_factory=list)
    warnings: List[PlanValidationIssue] = field(default_factory=list)
    constitutional_compliance_score: float = 0.0
    architecture_completeness_score: float = 0.0
    missing_sections: List[str] = field(default_factory=list)

    def add_issue(self, issue: PlanValidationIssue):
        """Add a validation issue."""
        if issue.level == ValidationLevel.ERROR:
            self.issues.append(issue)
            self.is_valid = False
        else:
            self.warnings.append(issue)


class PlanValidator:
    """Validates implementation plan documents for constitutional compliance."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the plan validator."""
        self.constitutional_validator = ConstitutionalValidator(config_path)
        self.config = self._load_config(config_path)

        # Required sections for TeamReel implementation plans
        self.required_sections = {
            "SE Principles Compliance",
            "Architecture Design",
            "Implementation Approach",
            "Quality Gates",
            "Testing Strategy",
            "Risk Assessment",
            "Dependencies",
        }

        # Architecture patterns that should be documented
        self.architecture_patterns = {
            "single_responsibility": "Single Responsibility Principle",
            "dependency_injection": "Dependency Injection",
            "separation_of_concerns": "Separation of Concerns",
            "modular_design": "Modular Design",
            "interface_segregation": "Interface Segregation",
            "loose_coupling": "Loose Coupling",
            "high_cohesion": "High Cohesion",
        }

        # Quality gates that should be defined
        self.required_quality_gates = {
            "Code Coverage": "80%+ test coverage",
            "Cyclomatic Complexity": "≤10 per function/method",
            "Linting": "Zero linting errors",
            "Security Scan": "No security vulnerabilities",
            "Performance": "Response time requirements",
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validation configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            "validation": {
                "require_architecture_section": True,
                "require_se_principles": True,
                "require_quality_gates": True,
                "require_testing_strategy": True,
                "require_risk_assessment": True,
                "min_quality_gates": 3,
                "block_on_missing_sections": True,
                "block_on_architectural_violations": True,
            }
        }

    def validate_plan(self, plan_path: str) -> PlanValidationReport:
        """Validate an implementation plan document for constitutional compliance."""
        report = PlanValidationReport(file_path=plan_path)

        try:
            content = Path(plan_path).read_text(encoding="utf-8")
            sections = self._parse_sections(content)

            # Validate template structure
            self._validate_template_structure(content, sections, report)

            # Validate SE principles compliance
            self._validate_se_principles_compliance(content, sections, report)

            # Validate architecture design
            self._validate_architecture_design(content, sections, report)

            # Validate implementation approach
            self._validate_implementation_approach(content, sections, report)

            # Validate quality gates
            self._validate_quality_gates(content, sections, report)

            # Validate testing strategy
            self._validate_testing_strategy(content, sections, report)

            # Validate risk assessment
            self._validate_risk_assessment(content, sections, report)

            # Validate dependency management
            self._validate_dependency_management(content, sections, report)

            # Calculate compliance scores
            report.constitutional_compliance_score = self._calculate_compliance_score(
                report
            )
            report.architecture_completeness_score = self._calculate_architecture_score(
                content, sections
            )

        except Exception as e:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.TEMPLATE_STRUCTURE,
                    level=ValidationLevel.ERROR,
                    message=f"Failed to validate plan: {str(e)}",
                )
            )

        return report

    def _parse_sections(self, content: str) -> Dict[str, PlanSection]:
        """Parse markdown sections from plan content."""
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
                    sections[current_section.title] = PlanSection(
                        title=current_section.title,
                        content="\n".join(section_content),
                        line_start=section_start,
                        line_end=i - 1,
                        level=current_section.level,
                    )

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = PlanSection(title, "", i, i, level)
                section_content = []
                section_start = i
            elif current_section:
                section_content.append(line)

        # Save final section
        if current_section:
            sections[current_section.title] = PlanSection(
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
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate that the plan follows the required template structure."""
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
                        PlanValidationIssue(
                            category=PlanValidationCategory.TEMPLATE_STRUCTURE,
                            level=ValidationLevel.ERROR,
                            message=f"Required section missing: {section}",
                            suggested_fix=f"Add section: ## {section}",
                        )
                    )

    def _validate_se_principles_compliance(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate SE principles compliance section."""
        se_section = None
        for title, section in sections.items():
            if "se principles" in title.lower() or (
                "principles" in title.lower() and "compliance" in title.lower()
            ):
                se_section = section
                break

        if not se_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.SE_PRINCIPLES_COMPLIANCE,
                    level=ValidationLevel.ERROR,
                    message="Missing 'SE Principles Compliance' section",
                    suggested_fix="Add section documenting how the implementation addresses each SE principle",
                )
            )
            return

        # Check that each SE principle is addressed with specific implementation details
        for principle in SEPrinciple:
            principle_name = principle.value.replace("_", " ").title()
            if principle_name.lower() not in se_section.content.lower():
                report.add_issue(
                    PlanValidationIssue(
                        category=PlanValidationCategory.SE_PRINCIPLES_COMPLIANCE,
                        level=ValidationLevel.WARNING,
                        message=f"SE principle not explicitly addressed in implementation: {principle_name}",
                        line_number=se_section.line_start,
                        section="SE Principles Compliance",
                        suggested_fix=f"Add specific implementation approach for {principle_name}",
                    )
                )

        # Check for concrete implementation strategies
        if (
            "how" not in se_section.content.lower()
            and "implementation" not in se_section.content.lower()
        ):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.SE_PRINCIPLES_COMPLIANCE,
                    level=ValidationLevel.WARNING,
                    message="SE principles section lacks concrete implementation strategies",
                    line_number=se_section.line_start,
                    section="SE Principles Compliance",
                    suggested_fix="Add specific implementation approaches for each principle",
                )
            )

    def _validate_architecture_design(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate architecture design section."""
        arch_section = None
        for title, section in sections.items():
            if "architecture" in title.lower() and (
                "design" in title.lower() or "overview" in title.lower()
            ):
                arch_section = section
                break

        if not arch_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.ARCHITECTURE_DESIGN,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Architecture Design' section",
                    suggested_fix="Add section documenting system architecture and design patterns",
                )
            )
            return

        # Check for key architectural concepts
        missing_patterns = []
        for pattern_key, pattern_name in self.architecture_patterns.items():
            if pattern_key.replace("_", " ") not in arch_section.content.lower():
                missing_patterns.append(pattern_name)

        if len(missing_patterns) > len(self.architecture_patterns) // 2:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.ARCHITECTURE_DESIGN,
                    level=ValidationLevel.WARNING,
                    message=f"Architecture section missing key patterns: {', '.join(missing_patterns[:3])}{'...' if len(missing_patterns) > 3 else ''}",
                    line_number=arch_section.line_start,
                    section="Architecture Design",
                    suggested_fix="Add discussion of architectural patterns and design principles",
                )
            )

        # Check for component diagrams or structural descriptions
        structure_indicators = [
            "component",
            "module",
            "layer",
            "interface",
            "class",
            "service",
        ]
        if not any(
            indicator in arch_section.content.lower()
            for indicator in structure_indicators
        ):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.ARCHITECTURE_DESIGN,
                    level=ValidationLevel.WARNING,
                    message="Architecture section lacks structural component descriptions",
                    line_number=arch_section.line_start,
                    section="Architecture Design",
                    suggested_fix="Add descriptions of key components, modules, or services",
                )
            )

    def _validate_implementation_approach(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate implementation approach section."""
        impl_section = None
        for title, section in sections.items():
            if "implementation" in title.lower() and (
                "approach" in title.lower() or "strategy" in title.lower()
            ):
                impl_section = section
                break

        if not impl_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.IMPLEMENTATION_APPROACH,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Implementation Approach' section",
                    suggested_fix="Add section documenting step-by-step implementation strategy",
                )
            )
            return

        # Check for concrete implementation steps
        if not re.search(r"^\s*\d+\.|\s*[-*]\s+", impl_section.content, re.MULTILINE):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.IMPLEMENTATION_APPROACH,
                    level=ValidationLevel.WARNING,
                    message="Implementation approach lacks concrete steps or sequence",
                    line_number=impl_section.line_start,
                    section="Implementation Approach",
                    suggested_fix="Add numbered steps or bullet points for implementation sequence",
                )
            )

        # Check for development methodology references
        methodologies = ["tdd", "test-driven", "incremental", "iterative", "agile"]
        if not any(method in impl_section.content.lower() for method in methodologies):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.IMPLEMENTATION_APPROACH,
                    level=ValidationLevel.INFO,
                    message="Consider documenting development methodology (TDD, incremental, etc.)",
                    line_number=impl_section.line_start,
                    section="Implementation Approach",
                    suggested_fix="Add reference to development methodology or approach",
                )
            )

    def _validate_quality_gates(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate quality gates section."""
        qg_section = None
        for title, section in sections.items():
            if "quality" in title.lower() and (
                "gate" in title.lower() or "criteria" in title.lower()
            ):
                qg_section = section
                break

        if not qg_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.QUALITY_GATES,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Quality Gates' section",
                    suggested_fix="Add section defining quality gates and acceptance criteria",
                )
            )
            return

        # Check for required quality gates
        missing_gates = []
        for gate_name, gate_description in self.required_quality_gates.items():
            if gate_name.lower() not in qg_section.content.lower():
                missing_gates.append(gate_name)

        if missing_gates:
            for gate in missing_gates:
                report.add_issue(
                    PlanValidationIssue(
                        category=PlanValidationCategory.QUALITY_GATES,
                        level=ValidationLevel.WARNING,
                        message=f"Quality gate not defined: {gate}",
                        line_number=qg_section.line_start,
                        section="Quality Gates",
                        suggested_fix=f"Add quality gate definition for {gate}: {self.required_quality_gates[gate]}",
                    )
                )

        # Check for measurable criteria
        if not re.search(r"\d+%|\d+\s*(ms|sec|min)|≤|>=|>", qg_section.content):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.QUALITY_GATES,
                    level=ValidationLevel.WARNING,
                    message="Quality gates lack measurable criteria",
                    line_number=qg_section.line_start,
                    section="Quality Gates",
                    suggested_fix="Add specific numeric thresholds for quality gates",
                )
            )

    def _validate_testing_strategy(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate testing strategy section."""
        test_section = None
        for title, section in sections.items():
            if "test" in title.lower() and (
                "strategy" in title.lower() or "approach" in title.lower()
            ):
                test_section = section
                break

        if not test_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.TESTING_STRATEGY,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Testing Strategy' section",
                    suggested_fix="Add section documenting testing approach and coverage",
                )
            )
            return

        # Check for different types of testing
        test_types = ["unit", "integration", "end-to-end", "performance", "security"]
        found_types = [
            test_type
            for test_type in test_types
            if test_type in test_section.content.lower()
        ]

        if len(found_types) < 2:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.TESTING_STRATEGY,
                    level=ValidationLevel.WARNING,
                    message=f"Testing strategy covers limited test types: {', '.join(found_types) if found_types else 'none specified'}",
                    line_number=test_section.line_start,
                    section="Testing Strategy",
                    suggested_fix="Consider adding unit, integration, and end-to-end testing strategies",
                )
            )

        # Check for coverage requirements
        if "coverage" not in test_section.content.lower():
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.TESTING_STRATEGY,
                    level=ValidationLevel.WARNING,
                    message="Testing strategy doesn't specify coverage requirements",
                    line_number=test_section.line_start,
                    section="Testing Strategy",
                    suggested_fix="Add test coverage requirements (e.g., 80% minimum)",
                )
            )

    def _validate_risk_assessment(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate risk assessment section."""
        risk_section = None
        for title, section in sections.items():
            if "risk" in title.lower():
                risk_section = section
                break

        if not risk_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.RISK_MITIGATION,
                    level=ValidationLevel.ERROR,
                    message="Missing 'Risk Assessment' section",
                    suggested_fix="Add section identifying implementation risks and mitigation strategies",
                )
            )
            return

        # Check for risk identification
        risk_indicators = ["risk", "challenge", "difficulty", "problem", "issue"]
        if not any(
            indicator in risk_section.content.lower() for indicator in risk_indicators
        ):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.RISK_MITIGATION,
                    level=ValidationLevel.WARNING,
                    message="Risk section lacks specific risk identification",
                    line_number=risk_section.line_start,
                    section="Risk Assessment",
                    suggested_fix="Identify specific technical and implementation risks",
                )
            )

        # Check for mitigation strategies
        mitigation_indicators = [
            "mitigation",
            "solution",
            "strategy",
            "approach",
            "plan",
        ]
        if not any(
            indicator in risk_section.content.lower()
            for indicator in mitigation_indicators
        ):
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.RISK_MITIGATION,
                    level=ValidationLevel.WARNING,
                    message="Risk section lacks mitigation strategies",
                    line_number=risk_section.line_start,
                    section="Risk Assessment",
                    suggested_fix="Add specific mitigation strategies for identified risks",
                )
            )

    def _validate_dependency_management(
        self,
        content: str,
        sections: Dict[str, PlanSection],
        report: PlanValidationReport,
    ):
        """Validate dependency management section."""
        dep_section = None
        for title, section in sections.items():
            if "depend" in title.lower():
                dep_section = section
                break

        if not dep_section:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.DEPENDENCY_MANAGEMENT,
                    level=ValidationLevel.WARNING,
                    message="Missing 'Dependencies' section",
                    suggested_fix="Add section documenting implementation dependencies",
                )
            )
            return

        # Check for different types of dependencies
        dep_types = ["technical", "external", "internal", "library", "service", "api"]
        found_types = [
            dep_type
            for dep_type in dep_types
            if dep_type in dep_section.content.lower()
        ]

        if not found_types:
            report.add_issue(
                PlanValidationIssue(
                    category=PlanValidationCategory.DEPENDENCY_MANAGEMENT,
                    level=ValidationLevel.WARNING,
                    message="Dependencies section lacks specific dependency types",
                    line_number=dep_section.line_start,
                    section="Dependencies",
                    suggested_fix="Specify technical, external, or internal dependencies",
                )
            )

    def _calculate_compliance_score(self, report: PlanValidationReport) -> float:
        """Calculate constitutional compliance score (0-100)."""
        total_checks = len(self.required_sections)

        error_count = len(report.issues)
        warning_count = len(report.warnings)

        # Deduct more for errors than warnings
        score = 100.0 - (error_count * 15) - (warning_count * 3)

        return max(0.0, min(100.0, score))

    def _calculate_architecture_score(
        self, content: str, sections: Dict[str, PlanSection]
    ) -> float:
        """Calculate architecture completeness score (0-100)."""
        score = 0.0

        # Architecture section presence (30 points)
        arch_section = None
        for title, section in sections.items():
            if "architecture" in title.lower():
                arch_section = section
                score += 30
                break

        if arch_section:
            # Architecture patterns coverage (40 points)
            pattern_coverage = 0
            for pattern_key in self.architecture_patterns.keys():
                if pattern_key.replace("_", " ") in arch_section.content.lower():
                    pattern_coverage += 1
            score += (pattern_coverage / len(self.architecture_patterns)) * 40

            # Structural descriptions (30 points)
            structure_indicators = [
                "component",
                "module",
                "layer",
                "interface",
                "class",
                "service",
            ]
            structure_count = sum(
                1
                for indicator in structure_indicators
                if indicator in arch_section.content.lower()
            )
            score += min(structure_count / len(structure_indicators), 1.0) * 30

        return min(100.0, score)

    def validate_multiple_plans(
        self, plan_paths: List[str]
    ) -> Dict[str, PlanValidationReport]:
        """Validate multiple implementation plan files."""
        results = {}
        for plan_path in plan_paths:
            try:
                results[plan_path] = self.validate_plan(plan_path)
            except Exception as e:
                report = PlanValidationReport(file_path=plan_path, is_valid=False)
                report.add_issue(
                    PlanValidationIssue(
                        category=PlanValidationCategory.TEMPLATE_STRUCTURE,
                        level=ValidationLevel.ERROR,
                        message=f"Failed to validate {plan_path}: {str(e)}",
                    )
                )
                results[plan_path] = report

        return results

    def format_report(
        self, report: PlanValidationReport, format_type: str = "terminal"
    ) -> str:
        """Format validation report for output."""
        if format_type == "json":
            import json

            return json.dumps(
                {
                    "file_path": report.file_path,
                    "is_valid": report.is_valid,
                    "compliance_score": report.constitutional_compliance_score,
                    "architecture_score": report.architecture_completeness_score,
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
        output.append(f"IMPLEMENTATION PLAN VALIDATION REPORT")
        output.append(f"{'='*60}")
        output.append(f"File: {report.file_path}")
        output.append(f"Valid: {'✅ YES' if report.is_valid else '❌ NO'}")
        output.append(
            f"Constitutional Compliance Score: {report.constitutional_compliance_score:.1f}/100"
        )
        output.append(
            f"Architecture Completeness Score: {report.architecture_completeness_score:.1f}/100"
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
                "✅ Implementation plan meets constitutional compliance requirements!"
            )
        else:
            output.append(
                "❌ Implementation plan must be fixed before proceeding to task generation."
            )

        return "\n".join(output)


def main():
    """CLI entry point for plan validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate implementation plans for constitutional compliance"
    )
    parser.add_argument(
        "plans", nargs="+", help="Implementation plan files to validate"
    )
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

    validator = PlanValidator(args.config)

    all_valid = True
    for plan_path in args.plans:
        report = validator.validate_plan(plan_path)
        print(validator.format_report(report, args.format))

        if not report.is_valid:
            all_valid = False

    if args.strict and not all_valid:
        exit(1)


if __name__ == "__main__":
    main()
