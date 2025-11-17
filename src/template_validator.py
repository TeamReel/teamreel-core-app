#!/usr/bin/env python3
"""
Template Validation Against SE Principles

Validates templates against current constitutional requirements.
Ensures all templates comply with the 8 Software Engineering principles.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import re
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    """Template validation levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SEPrinciple(Enum):
    """Software Engineering principles for validation."""

    SRP = "Single_Responsibility_Principle"
    ENCAPSULATION = "Encapsulation"
    LOOSE_COUPLING = "Loose_Coupling"
    REUSABILITY = "Reusability"
    PORTABILITY = "Portability"
    DEFENSIBILITY = "Defensibility"
    MAINTAINABILITY = "Maintainability"
    SIMPLICITY = "Simplicity"


@dataclass
class ValidationIssue:
    """Individual template validation issue."""

    principle: SEPrinciple
    level: ValidationLevel
    description: str
    location: str  # File location or section
    line_number: Optional[int] = None
    suggestion: str = ""
    auto_fixable: bool = False
    constitutional_requirement: str = ""


@dataclass
class ValidationResult:
    """Template validation result."""

    template_path: str
    is_valid: bool
    compliance_score: float  # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    principles_checked: List[SEPrinciple] = field(default_factory=list)
    validation_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )

    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get critical validation issues."""
        return [
            issue for issue in self.issues if issue.level == ValidationLevel.CRITICAL
        ]

    @property
    def error_issues(self) -> List[ValidationIssue]:
        """Get error validation issues."""
        return [issue for issue in self.issues if issue.level == ValidationLevel.ERROR]

    @property
    def warning_issues(self) -> List[ValidationIssue]:
        """Get warning validation issues."""
        return [
            issue for issue in self.issues if issue.level == ValidationLevel.WARNING
        ]


class TemplateValidator:
    """Main template validation engine for constitutional compliance."""

    def __init__(self, manifest_path: str = ".kittify/templates/manifest.yaml"):
        """Initialize validator with manifest and constitutional rules."""
        self.manifest_path = Path(manifest_path)
        self.manifest_data = None
        self.constitutional_rules = None
        self.load_manifest()
        self.load_constitutional_rules()

    def load_manifest(self) -> None:
        """Load template manifest for validation context."""
        try:
            if not self.manifest_path.exists():
                raise FileNotFoundError(
                    f"Template manifest not found: {self.manifest_path}"
                )

            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.manifest_data = yaml.safe_load(f)

        except Exception as e:
            print(f"❌ Error loading manifest: {e}")
            sys.exit(1)

    def load_constitutional_rules(self) -> None:
        """Load constitutional validation rules."""
        rules_path = Path(".kittify/config/se_rules.yaml")

        if rules_path.exists():
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    self.constitutional_rules = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not load constitutional rules: {e}")
                self.constitutional_rules = self._get_default_rules()
        else:
            print("ℹ️ Using default constitutional validation rules")
            self.constitutional_rules = self._get_default_rules()

    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default constitutional validation rules."""
        return {
            "validation": {
                "strict_mode": True,
                "compliance_threshold": 80.0,
                "principles": {
                    "SRP": {
                        "description": "Single Responsibility Principle",
                        "rules": [
                            "template_has_single_purpose",
                            "no_mixed_responsibilities",
                            "clear_scope_definition",
                        ],
                    },
                    "Encapsulation": {
                        "description": "Information hiding and interface design",
                        "rules": [
                            "clear_public_interface",
                            "internal_details_hidden",
                            "proper_abstraction_level",
                        ],
                    },
                    "Loose_Coupling": {
                        "description": "Minimal dependencies between components",
                        "rules": [
                            "minimal_external_dependencies",
                            "interface_based_interactions",
                            "no_tight_coupling",
                        ],
                    },
                    "Reusability": {
                        "description": "Templates can be reused across contexts",
                        "rules": [
                            "parameterized_content",
                            "generic_structure",
                            "no_hardcoded_specifics",
                        ],
                    },
                    "Portability": {
                        "description": "Cross-platform compatibility",
                        "rules": [
                            "platform_agnostic_paths",
                            "standard_encoding",
                            "universal_line_endings",
                        ],
                    },
                    "Defensibility": {
                        "description": "Security and robustness",
                        "rules": [
                            "input_validation",
                            "safe_defaults",
                            "security_considerations",
                        ],
                    },
                    "Maintainability": {
                        "description": "Easy to understand and modify",
                        "rules": [
                            "clear_documentation",
                            "consistent_structure",
                            "version_tracking",
                        ],
                    },
                    "Simplicity": {
                        "description": "YAGNI - You Aren't Gonna Need It",
                        "rules": [
                            "essential_elements_only",
                            "no_premature_optimization",
                            "straightforward_implementation",
                        ],
                    },
                },
            }
        }

    def validate_srp_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Single Responsibility Principle compliance."""
        issues = []

        # Check if template has a clear single purpose
        if "purpose" not in template_config and "Purpose" not in content:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.SRP,
                    level=ValidationLevel.WARNING,
                    description="Template lacks clear purpose statement",
                    location=template_path,
                    suggestion="Add a clear purpose statement to template header",
                    constitutional_requirement="SRP requires single, well-defined responsibility",
                )
            )

        # Check for mixed responsibilities (multiple distinct sections)
        section_count = len(re.findall(r"^##?\s+", content, re.MULTILINE))
        if section_count > 7:  # Reasonable threshold for template complexity
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.SRP,
                    level=ValidationLevel.WARNING,
                    description=f"Template has {section_count} sections, may have multiple responsibilities",
                    location=template_path,
                    suggestion="Consider splitting into multiple focused templates",
                    constitutional_requirement="SRP requires single responsibility per template",
                )
            )

        return issues

    def validate_encapsulation_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Encapsulation principle compliance."""
        issues = []

        # Check for clear public interface (documented parameters/usage)
        if not re.search(r"(usage|parameters|interface)", content, re.IGNORECASE):
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.ENCAPSULATION,
                    level=ValidationLevel.INFO,
                    description="Template could benefit from clear usage/interface documentation",
                    location=template_path,
                    suggestion="Add usage instructions or parameter documentation",
                    constitutional_requirement="Encapsulation requires clear public interfaces",
                )
            )

        # Check for exposed internal implementation details
        internal_markers = ["TODO", "FIXME", "HACK", "DEBUG"]
        for marker in internal_markers:
            if marker in content:
                issues.append(
                    ValidationIssue(
                        principle=SEPrinciple.ENCAPSULATION,
                        level=ValidationLevel.WARNING,
                        description=f"Template exposes internal implementation detail: {marker}",
                        location=template_path,
                        line_number=self._find_line_number(content, marker),
                        suggestion=f"Remove or properly document {marker} markers",
                        constitutional_requirement="Encapsulation requires hiding internal details",
                    )
                )

        return issues

    def validate_loose_coupling_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Loose Coupling principle compliance."""
        issues = []

        # Check for hardcoded paths or dependencies
        hardcoded_patterns = [
            r"C:\\",  # Windows absolute paths
            r"/Users/",  # macOS user paths
            r"/home/",  # Linux user paths
            r"localhost",  # Hardcoded localhost
        ]

        for pattern in hardcoded_patterns:
            if re.search(pattern, content):
                issues.append(
                    ValidationIssue(
                        principle=SEPrinciple.LOOSE_COUPLING,
                        level=ValidationLevel.ERROR,
                        description=f"Template contains hardcoded path or dependency: {pattern}",
                        location=template_path,
                        line_number=self._find_line_number(content, pattern),
                        suggestion="Use relative paths or environment variables",
                        auto_fixable=True,
                        constitutional_requirement="Loose coupling requires parameterized dependencies",
                    )
                )

        # Check for excessive external template references
        template_refs = re.findall(r"\[.*?\]\(.*?\.md\)", content)
        if len(template_refs) > 5:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.LOOSE_COUPLING,
                    level=ValidationLevel.WARNING,
                    description=f"Template has {len(template_refs)} external references, may be tightly coupled",
                    location=template_path,
                    suggestion="Consider reducing external dependencies",
                    constitutional_requirement="Loose coupling requires minimal dependencies",
                )
            )

        return issues

    def validate_reusability_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Reusability principle compliance."""
        issues = []

        # Check for parameterization markers
        param_markers = re.findall(r"\$\{?\w+\}?|\{\{\w+\}\}|\[.*?\]", content)
        if len(param_markers) < 2 and template_path.endswith(".md"):
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.REUSABILITY,
                    level=ValidationLevel.INFO,
                    description="Template has few parameterization markers, may not be reusable",
                    location=template_path,
                    suggestion="Add parameters for customizable elements",
                    constitutional_requirement="Reusability requires parameterized templates",
                )
            )

        # Check for project-specific names or references
        specific_patterns = [
            r"project(?!.*template)",  # Project name not in template context
            r"brian@",  # Specific email
            r"my-project",  # Generic project reference
        ]

        for pattern in specific_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(
                    ValidationIssue(
                        principle=SEPrinciple.REUSABILITY,
                        level=ValidationLevel.WARNING,
                        description=f"Template contains project-specific reference: {matches[0]}",
                        location=template_path,
                        line_number=self._find_line_number(content, matches[0]),
                        suggestion="Replace with generic parameter or template variable",
                        auto_fixable=True,
                        constitutional_requirement="Reusability requires generic, parameterized content",
                    )
                )

        return issues

    def validate_portability_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Portability principle compliance."""
        issues = []

        # Check for platform-specific elements
        windows_specific = re.findall(
            r"\.bat\b|\.exe\b|powershell|cmd\.exe", content, re.IGNORECASE
        )
        unix_specific = re.findall(r"\.sh\b|/bin/bash|/usr/bin", content, re.IGNORECASE)

        if windows_specific and not unix_specific:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.PORTABILITY,
                    level=ValidationLevel.WARNING,
                    description="Template appears Windows-specific, may not be portable",
                    location=template_path,
                    suggestion="Add cross-platform alternatives or notes",
                    constitutional_requirement="Portability requires cross-platform compatibility",
                )
            )
        elif unix_specific and not windows_specific:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.PORTABILITY,
                    level=ValidationLevel.WARNING,
                    description="Template appears Unix-specific, may not be portable",
                    location=template_path,
                    suggestion="Add cross-platform alternatives or notes",
                    constitutional_requirement="Portability requires cross-platform compatibility",
                )
            )

        # Check file encoding (should be UTF-8)
        try:
            with open(template_path, "rb") as f:
                raw_content = f.read()
                if b"\xff\xfe" in raw_content[:2] or b"\xfe\xff" in raw_content[:2]:
                    issues.append(
                        ValidationIssue(
                            principle=SEPrinciple.PORTABILITY,
                            level=ValidationLevel.ERROR,
                            description="Template uses non-UTF-8 encoding",
                            location=template_path,
                            suggestion="Convert to UTF-8 encoding",
                            auto_fixable=True,
                            constitutional_requirement="Portability requires standard UTF-8 encoding",
                        )
                    )
        except Exception:
            pass

        return issues

    def validate_defensibility_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Defensibility principle compliance."""
        issues = []

        # Check for security considerations
        security_keywords = ["password", "secret", "token", "key", "credential"]
        for keyword in security_keywords:
            if keyword in content.lower() and "secure" not in content.lower():
                issues.append(
                    ValidationIssue(
                        principle=SEPrinciple.DEFENSIBILITY,
                        level=ValidationLevel.WARNING,
                        description=f"Template mentions {keyword} without security guidance",
                        location=template_path,
                        line_number=self._find_line_number(content, keyword),
                        suggestion="Add security considerations or safe handling instructions",
                        constitutional_requirement="Defensibility requires security awareness",
                    )
                )

        # Check for input validation guidance
        if "input" in content.lower() and "validat" not in content.lower():
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.DEFENSIBILITY,
                    level=ValidationLevel.INFO,
                    description="Template discusses input without validation guidance",
                    location=template_path,
                    suggestion="Add input validation recommendations",
                    constitutional_requirement="Defensibility requires input validation",
                )
            )

        return issues

    def validate_maintainability_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Maintainability principle compliance."""
        issues = []

        # Check for version tracking
        if "version" not in content.lower() and "created" not in template_config:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.MAINTAINABILITY,
                    level=ValidationLevel.WARNING,
                    description="Template lacks version or creation tracking",
                    location=template_path,
                    suggestion="Add version or timestamp information",
                    constitutional_requirement="Maintainability requires version tracking",
                )
            )

        # Check for documentation structure
        if not re.search(r"^#+ ", content, re.MULTILINE):
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.MAINTAINABILITY,
                    level=ValidationLevel.ERROR,
                    description="Template lacks structured documentation headers",
                    location=template_path,
                    suggestion="Add proper Markdown headers for structure",
                    auto_fixable=True,
                    constitutional_requirement="Maintainability requires clear documentation structure",
                )
            )

        # Check for excessive complexity (line count)
        line_count = len(content.split("\n"))
        if line_count > 500:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.MAINTAINABILITY,
                    level=ValidationLevel.WARNING,
                    description=f"Template is very long ({line_count} lines), may be hard to maintain",
                    location=template_path,
                    suggestion="Consider breaking into smaller, focused templates",
                    constitutional_requirement="Maintainability requires manageable complexity",
                )
            )

        return issues

    def validate_simplicity_compliance(
        self, template_path: str, content: str, template_config: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate Simplicity (YAGNI) principle compliance."""
        issues = []

        # Check for complexity indicators
        complexity_markers = [
            "complex",
            "complicated",
            "advanced",
            "sophisticated",
            "enterprise",
            "comprehensive",
            "extensive",
        ]

        for marker in complexity_markers:
            if marker in content.lower():
                issues.append(
                    ValidationIssue(
                        principle=SEPrinciple.SIMPLICITY,
                        level=ValidationLevel.INFO,
                        description=f"Template mentions complexity: '{marker}'",
                        location=template_path,
                        line_number=self._find_line_number(content, marker),
                        suggestion="Ensure complexity is justified and essential",
                        constitutional_requirement="Simplicity requires essential elements only (YAGNI)",
                    )
                )

        # Check for excessive optional sections
        optional_sections = re.findall(
            r"optional|if needed|advanced|extra", content, re.IGNORECASE
        )
        if len(optional_sections) > 3:
            issues.append(
                ValidationIssue(
                    principle=SEPrinciple.SIMPLICITY,
                    level=ValidationLevel.WARNING,
                    description=f"Template has {len(optional_sections)} optional elements, may violate YAGNI",
                    location=template_path,
                    suggestion="Consider removing non-essential optional elements",
                    constitutional_requirement="Simplicity requires focusing on essential needs only",
                )
            )

        return issues

    def _find_line_number(self, content: str, search_term: str) -> Optional[int]:
        """Find line number of search term in content."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if search_term.lower() in line.lower():
                return i
        return None

    def validate_template(
        self, template_path: str, template_config: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a single template against all SE principles."""
        # Read template content
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return ValidationResult(
                template_path=template_path,
                is_valid=False,
                compliance_score=0.0,
                issues=[
                    ValidationIssue(
                        principle=SEPrinciple.MAINTAINABILITY,
                        level=ValidationLevel.CRITICAL,
                        description=f"Cannot read template file: {e}",
                        location=template_path,
                        constitutional_requirement="Template must be readable",
                    )
                ],
            )

        # Run all principle validations
        all_issues = []
        principles_checked = []

        validation_methods = [
            (SEPrinciple.SRP, self.validate_srp_compliance),
            (SEPrinciple.ENCAPSULATION, self.validate_encapsulation_compliance),
            (SEPrinciple.LOOSE_COUPLING, self.validate_loose_coupling_compliance),
            (SEPrinciple.REUSABILITY, self.validate_reusability_compliance),
            (SEPrinciple.PORTABILITY, self.validate_portability_compliance),
            (SEPrinciple.DEFENSIBILITY, self.validate_defensibility_compliance),
            (SEPrinciple.MAINTAINABILITY, self.validate_maintainability_compliance),
            (SEPrinciple.SIMPLICITY, self.validate_simplicity_compliance),
        ]

        for principle, validation_method in validation_methods:
            try:
                issues = validation_method(template_path, content, template_config)
                all_issues.extend(issues)
                principles_checked.append(principle)
            except Exception as e:
                all_issues.append(
                    ValidationIssue(
                        principle=principle,
                        level=ValidationLevel.ERROR,
                        description=f"Validation error for {principle.value}: {e}",
                        location=template_path,
                        constitutional_requirement=f"{principle.value} validation required",
                    )
                )

        # Calculate compliance score
        total_possible_score = 100.0
        critical_penalty = (
            len([i for i in all_issues if i.level == ValidationLevel.CRITICAL]) * 25
        )
        error_penalty = (
            len([i for i in all_issues if i.level == ValidationLevel.ERROR]) * 15
        )
        warning_penalty = (
            len([i for i in all_issues if i.level == ValidationLevel.WARNING]) * 5
        )
        info_penalty = (
            len([i for i in all_issues if i.level == ValidationLevel.INFO]) * 1
        )

        compliance_score = max(
            0.0,
            total_possible_score
            - critical_penalty
            - error_penalty
            - warning_penalty
            - info_penalty,
        )

        # Determine if template is valid
        has_critical = any(i.level == ValidationLevel.CRITICAL for i in all_issues)
        has_errors = any(i.level == ValidationLevel.ERROR for i in all_issues)
        threshold = self.constitutional_rules.get("validation", {}).get(
            "compliance_threshold", 80.0
        )

        is_valid = not has_critical and not has_errors and compliance_score >= threshold

        return ValidationResult(
            template_path=template_path,
            is_valid=is_valid,
            compliance_score=compliance_score,
            issues=all_issues,
            principles_checked=principles_checked,
        )

    def validate_all_templates(self) -> Dict[str, ValidationResult]:
        """Validate all templates in the manifest."""
        validation_results = {}

        print("🔍 Starting constitutional template validation...")

        # Validate all template categories
        for category_name, category_templates in self.manifest_data.get(
            "templates", {}
        ).items():
            print(f"📁 Validating {category_name} templates...")

            for template_name, template_config in category_templates.items():
                template_path = template_config.get("path", "")
                if template_path and Path(template_path).exists():
                    print(f"  🔍 Validating {template_name}...")
                    result = self.validate_template(template_path, template_config)
                    validation_results[template_path] = result

                    # Print validation result
                    status_emoji = "✅" if result.is_valid else "❌"
                    score = result.compliance_score
                    issue_count = len(result.issues)
                    print(
                        f"    {status_emoji} Score: {score:.1f}% ({issue_count} issues)"
                    )

                else:
                    print(f"  ⏭️ Skipping {template_name} (file not found)")

        return validation_results

    def generate_validation_report(
        self, validation_results: Dict[str, ValidationResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        if not validation_results:
            return {
                "status": "no_templates_validated",
                "summary": "No templates were validated",
                "report_generated": datetime.utcnow().isoformat() + "Z",
            }

        # Analyze results
        total_templates = len(validation_results)
        valid_templates = len([r for r in validation_results.values() if r.is_valid])
        invalid_templates = total_templates - valid_templates

        # Calculate average compliance score
        avg_score = (
            sum(r.compliance_score for r in validation_results.values())
            / total_templates
        )

        # Count issues by level
        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.issues)

        issue_counts = {
            "critical": len(
                [i for i in all_issues if i.level == ValidationLevel.CRITICAL]
            ),
            "error": len([i for i in all_issues if i.level == ValidationLevel.ERROR]),
            "warning": len(
                [i for i in all_issues if i.level == ValidationLevel.WARNING]
            ),
            "info": len([i for i in all_issues if i.level == ValidationLevel.INFO]),
        }

        # Count issues by principle
        principle_counts = {}
        for principle in SEPrinciple:
            principle_counts[principle.value] = len(
                [i for i in all_issues if i.principle == principle]
            )

        # Determine overall status
        if issue_counts["critical"] > 0:
            overall_status = "critical_issues"
        elif issue_counts["error"] > 0:
            overall_status = "validation_errors"
        elif invalid_templates > 0:
            overall_status = "templates_invalid"
        else:
            overall_status = "all_valid"

        return {
            "status": overall_status,
            "summary": f"{valid_templates}/{total_templates} templates valid (avg score: {avg_score:.1f}%)",
            "total_templates": total_templates,
            "valid_templates": valid_templates,
            "invalid_templates": invalid_templates,
            "average_compliance_score": round(avg_score, 1),
            "total_issues": len(all_issues),
            "issue_breakdown": issue_counts,
            "principle_breakdown": principle_counts,
            "auto_fixable_issues": len([i for i in all_issues if i.auto_fixable]),
            "template_results": {
                path: {
                    "is_valid": result.is_valid,
                    "compliance_score": result.compliance_score,
                    "issue_count": len(result.issues),
                    "critical_issues": len(result.critical_issues),
                    "error_issues": len(result.error_issues),
                    "warning_issues": len(result.warning_issues),
                    "principles_checked": [p.value for p in result.principles_checked],
                }
                for path, result in validation_results.items()
            },
            "report_generated": datetime.utcnow().isoformat() + "Z",
        }

    def run_validation(self) -> Dict[str, Any]:
        """Run complete template validation process."""
        validation_results = self.validate_all_templates()
        report = self.generate_validation_report(validation_results)

        # Print summary
        status_emoji = {
            "all_valid": "✅",
            "templates_invalid": "⚠️",
            "validation_errors": "❌",
            "critical_issues": "🚨",
        }

        emoji = status_emoji.get(report["status"], "❓")
        print(f"\n{emoji} Validation Complete: {report['summary']}")

        if report["total_issues"] > 0:
            auto_fixable = report["auto_fixable_issues"]
            print(
                f"📊 Issues: {report['total_issues']} total, {auto_fixable} auto-fixable"
            )

        return report


def main():
    """Main CLI entry point for template validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Constitutional Template Validation")
    parser.add_argument(
        "--manifest",
        default=".kittify/templates/manifest.yaml",
        help="Path to template manifest file",
    )
    parser.add_argument("--template", help="Validate specific template path")
    parser.add_argument(
        "--output", help="Output file for validation report (JSON format)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed issues",
    )
    parser.add_argument(
        "--fix", action="store_true", help="Automatically fix issues where possible"
    )

    args = parser.parse_args()

    try:
        validator = TemplateValidator(args.manifest)

        if args.template:
            # Validate single template
            template_config = {}  # Would extract from manifest in real implementation
            result = validator.validate_template(args.template, template_config)

            print(f"📋 Validation Result for {args.template}:")
            print(f"  Valid: {'✅' if result.is_valid else '❌'}")
            print(f"  Score: {result.compliance_score:.1f}%")
            print(f"  Issues: {len(result.issues)}")

            if args.verbose and result.issues:
                print("\n🔍 Detailed Issues:")
                for issue in result.issues:
                    level_emoji = {
                        "critical": "🚨",
                        "error": "❌",
                        "warning": "⚠️",
                        "info": "ℹ️",
                    }
                    emoji = level_emoji.get(issue.level.value, "❓")
                    print(f"  {emoji} {issue.principle.value}: {issue.description}")
                    if issue.suggestion:
                        print(f"    💡 {issue.suggestion}")
        else:
            # Validate all templates
            report = validator.run_validation()

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"📄 Report saved to: {args.output}")

            if args.verbose:
                print("\n📋 Detailed Report:")
                print(json.dumps(report, indent=2))

        # TODO: Implement auto-fix functionality if args.fix is True

        # Exit with error code if validation failed
        if args.template:
            sys.exit(0 if result.is_valid else 1)
        else:
            sys.exit(0 if report["status"] == "all_valid" else 1)

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
