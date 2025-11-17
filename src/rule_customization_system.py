#!/usr/bin/env python3
"""
Rule Customization System - T033

Provides project-specific customization of constitutional enforcement rules.
Allows teams to adapt the constitutional framework to their specific needs while
maintaining core compliance requirements.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import os
import yaml
import json
import copy
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
import argparse


class CustomizationLevel(Enum):
    """Levels of rule customization allowed."""

    STRICT = "strict"  # No customization allowed
    MODERATE = "moderate"  # Limited customization within bounds
    FLEXIBLE = "flexible"  # Full customization allowed
    OVERRIDE = "override"  # Can override core requirements (admin only)


class RuleCategory(Enum):
    """Categories of constitutional rules."""

    CORE_PRINCIPLES = "core_principles"  # SE principles (SRP, etc.)
    QUALITY_GATES = "quality_gates"  # Coverage, complexity thresholds
    NAMING_CONVENTIONS = "naming_conventions"  # Code naming standards
    SECURITY_POLICIES = "security_policies"  # Security requirements
    DOCUMENTATION = "documentation"  # Documentation standards
    TESTING = "testing"  # Testing requirements
    DEPLOYMENT = "deployment"  # Deployment standards


@dataclass
class CustomizationRule:
    """Definition of what can be customized in a rule."""

    rule_path: str  # Dot notation path to rule
    category: RuleCategory  # Rule category
    customization_level: CustomizationLevel  # How much can be changed
    min_value: Optional[Union[int, float]] = None  # Minimum allowed value
    max_value: Optional[Union[int, float]] = None  # Maximum allowed value
    allowed_values: Optional[List[Any]] = None  # Specific allowed values
    description: str = ""  # Description of the customization
    justification_required: bool = False  # Requires justification for changes
    approval_required: bool = False  # Requires approval for changes

    def __post_init__(self):
        if self.allowed_values is None:
            self.allowed_values = []


@dataclass
class CustomizationRequest:
    """A request to customize a specific rule."""

    rule_path: str
    current_value: Any
    requested_value: Any
    justification: str
    requestor: str
    timestamp: str
    project_context: Dict[str, Any]
    approved: bool = False
    approver: Optional[str] = None
    approval_timestamp: Optional[str] = None


@dataclass
class ProjectCustomization:
    """Complete customization configuration for a project."""

    project_name: str
    project_type: str
    customization_level: CustomizationLevel
    base_config: Dict[str, Any]
    customizations: Dict[str, Any]
    applied_requests: List[CustomizationRequest]
    metadata: Dict[str, Any]
    created: str
    modified: str


class RuleCustomizationSystem:
    """Manages project-specific customization of constitutional rules."""

    def __init__(self, config_dir: Path):
        """Initialize rule customization system."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.customization_rules_path = self.config_dir / "customization_rules.yaml"
        self.base_configs_dir = self.config_dir / "base_configs"
        self.project_customizations_dir = self.config_dir / "project_customizations"

        # Create directories
        self.base_configs_dir.mkdir(exist_ok=True)
        self.project_customizations_dir.mkdir(exist_ok=True)

        # Load customization rules
        self.customization_rules: Dict[str, CustomizationRule] = {}
        self._load_customization_rules()

    def _load_customization_rules(self) -> None:
        """Load allowed customization rules from configuration."""
        if self.customization_rules_path.exists():
            try:
                with open(self.customization_rules_path, "r", encoding="utf-8") as f:
                    rules_data = yaml.safe_load(f)

                for rule_name, rule_config in rules_data.get(
                    "customization_rules", {}
                ).items():
                    try:
                        rule = CustomizationRule(
                            rule_path=rule_config["rule_path"],
                            category=RuleCategory(rule_config["category"]),
                            customization_level=CustomizationLevel(
                                rule_config["customization_level"]
                            ),
                            min_value=rule_config.get("min_value"),
                            max_value=rule_config.get("max_value"),
                            allowed_values=rule_config.get("allowed_values", []),
                            description=rule_config.get("description", ""),
                            justification_required=rule_config.get(
                                "justification_required", False
                            ),
                            approval_required=rule_config.get(
                                "approval_required", False
                            ),
                        )
                        self.customization_rules[rule_name] = rule
                    except Exception as e:
                        print(f"⚠️ Failed to load customization rule {rule_name}: {e}")
            except Exception as e:
                print(f"⚠️ Failed to load customization rules: {e}")
                self._create_default_customization_rules()
        else:
            self._create_default_customization_rules()

    def _create_default_customization_rules(self) -> None:
        """Create default customization rules."""
        print("🏗️ Creating default customization rules...")

        default_rules = {
            "customization_rules": {
                # Quality Gates Customizations
                "coverage_threshold": {
                    "rule_path": "quality_gates.gates.coverage.threshold",
                    "category": "quality_gates",
                    "customization_level": "moderate",
                    "min_value": 70.0,
                    "max_value": 95.0,
                    "description": "Test coverage threshold percentage",
                    "justification_required": True,
                },
                "complexity_threshold": {
                    "rule_path": "quality_gates.gates.complexity.max_complexity",
                    "category": "quality_gates",
                    "customization_level": "moderate",
                    "min_value": 8,
                    "max_value": 15,
                    "description": "Maximum cyclomatic complexity allowed",
                    "justification_required": True,
                },
                "security_severity": {
                    "rule_path": "quality_gates.gates.security.severity_threshold",
                    "category": "security_policies",
                    "customization_level": "strict",
                    "allowed_values": ["medium", "high", "critical"],
                    "description": "Minimum security severity that fails build",
                    "approval_required": True,
                },
                # SE Principles Customizations
                "srp_max_methods": {
                    "rule_path": "constitutional_enforcement.principles.SRP.metrics.max_methods_per_class",
                    "category": "core_principles",
                    "customization_level": "flexible",
                    "min_value": 5,
                    "max_value": 20,
                    "description": "Maximum methods per class for SRP compliance",
                },
                "srp_max_lines": {
                    "rule_path": "constitutional_enforcement.principles.SRP.metrics.max_lines_per_function",
                    "category": "core_principles",
                    "customization_level": "moderate",
                    "min_value": 30,
                    "max_value": 100,
                    "description": "Maximum lines per function for SRP compliance",
                },
                "coupling_max_dependencies": {
                    "rule_path": "constitutional_enforcement.principles.Loose_Coupling.metrics.max_dependencies",
                    "category": "core_principles",
                    "customization_level": "moderate",
                    "min_value": 3,
                    "max_value": 10,
                    "description": "Maximum dependencies for loose coupling",
                },
                "maintainability_complexity": {
                    "rule_path": "constitutional_enforcement.principles.Maintainability.metrics.max_complexity",
                    "category": "core_principles",
                    "customization_level": "moderate",
                    "min_value": 8,
                    "max_value": 15,
                    "description": "Maximum complexity for maintainability",
                },
                "simplicity_nesting_depth": {
                    "rule_path": "constitutional_enforcement.principles.Simplicity.metrics.max_nesting_depth",
                    "category": "core_principles",
                    "customization_level": "moderate",
                    "min_value": 2,
                    "max_value": 5,
                    "description": "Maximum nesting depth for simplicity",
                },
                # Naming Convention Customizations
                "naming_enforcement_level": {
                    "rule_path": "naming_conventions.enforcement_level",
                    "category": "naming_conventions",
                    "customization_level": "moderate",
                    "allowed_values": ["lenient", "moderate", "strict"],
                    "description": "Level of naming convention enforcement",
                },
                "identifier_max_length": {
                    "rule_path": "naming_conventions.validation.max_identifier_length",
                    "category": "naming_conventions",
                    "customization_level": "flexible",
                    "min_value": 30,
                    "max_value": 100,
                    "description": "Maximum length for identifiers",
                },
                # Documentation Requirements
                "docstring_coverage": {
                    "rule_path": "quality_gates.gates.documentation.min_docstring_coverage",
                    "category": "documentation",
                    "customization_level": "moderate",
                    "min_value": 50.0,
                    "max_value": 90.0,
                    "description": "Minimum docstring coverage percentage",
                },
                # Testing Requirements
                "test_timeout": {
                    "rule_path": "testing.max_test_duration",
                    "category": "testing",
                    "customization_level": "flexible",
                    "min_value": 30,
                    "max_value": 300,
                    "description": "Maximum test execution time in seconds",
                },
            }
        }

        with open(self.customization_rules_path, "w", encoding="utf-8") as f:
            yaml.dump(default_rules, f, default_flow_style=False, indent=2)

        # Reload the rules
        self._load_customization_rules()
        print("✅ Default customization rules created")

    def create_project_customization(
        self,
        project_name: str,
        project_type: str,
        customization_level: CustomizationLevel,
        base_config_name: str = "standard",
    ) -> ProjectCustomization:
        """Create a new project customization configuration."""
        print(f"🎯 Creating customization for project: {project_name}")

        # Load base configuration
        base_config = self._load_base_config(base_config_name)
        if not base_config:
            raise ValueError(f"Base configuration '{base_config_name}' not found")

        # Create project customization
        project_customization = ProjectCustomization(
            project_name=project_name,
            project_type=project_type,
            customization_level=customization_level,
            base_config=base_config,
            customizations={},
            applied_requests=[],
            metadata={
                "base_config": base_config_name,
                "version": "1.0.0",
                "constitutional_version": "001-sdd-constitutional-foundation",
            },
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
        )

        # Save project customization
        self._save_project_customization(project_customization)

        print(f"✅ Project customization created: {project_name}")
        return project_customization

    def _load_base_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load a base configuration."""
        base_config_path = self.base_configs_dir / f"{config_name}.yaml"

        if not base_config_path.exists():
            # Create default base config
            self._create_default_base_configs()

        if base_config_path.exists():
            try:
                with open(base_config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Failed to load base config {config_name}: {e}")

        return None

    def _create_default_base_configs(self) -> None:
        """Create default base configurations."""
        print("🏗️ Creating default base configurations...")

        # Standard configuration
        standard_config = {
            "constitutional_enforcement": {
                "version": "1.0.0",
                "strict_mode": True,
                "violation_threshold": "medium",
                "principles": {
                    "SRP": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {
                            "max_methods_per_class": 10,
                            "max_lines_per_function": 50,
                            "max_responsibilities": 1,
                        },
                    },
                    "Encapsulation": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {
                            "min_private_ratio": 0.6,
                            "max_public_methods": 5,
                            "require_property_access": True,
                        },
                    },
                    "Loose_Coupling": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {"max_dependencies": 5, "max_coupling_factor": 0.3},
                    },
                    "Maintainability": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {
                            "max_complexity": 10,
                            "min_documentation_ratio": 0.2,
                        },
                    },
                    "Simplicity": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {"max_nesting_depth": 3, "max_parameters": 4},
                    },
                },
            },
            "quality_gates": {
                "gates": {
                    "coverage": {
                        "enabled": True,
                        "threshold": 80.0,
                        "fail_under": True,
                    },
                    "complexity": {
                        "enabled": True,
                        "max_complexity": 10,
                        "fail_on_violation": True,
                    },
                    "security": {
                        "enabled": True,
                        "severity_threshold": "high",
                        "fail_on_critical": True,
                    },
                    "documentation": {"enabled": True, "min_docstring_coverage": 70.0},
                }
            },
            "naming_conventions": {
                "enforcement_level": "strict",
                "validation": {"max_identifier_length": 50, "min_identifier_length": 2},
            },
        }

        standard_path = self.base_configs_dir / "standard.yaml"
        with open(standard_path, "w", encoding="utf-8") as f:
            yaml.dump(standard_config, f, default_flow_style=False, indent=2)

        # Minimal configuration (more lenient)
        minimal_config = copy.deepcopy(standard_config)
        minimal_config["quality_gates"]["gates"]["coverage"]["threshold"] = 70.0
        minimal_config["quality_gates"]["gates"]["complexity"]["max_complexity"] = 12
        minimal_config["naming_conventions"]["enforcement_level"] = "moderate"

        minimal_path = self.base_configs_dir / "minimal.yaml"
        with open(minimal_path, "w", encoding="utf-8") as f:
            yaml.dump(minimal_config, f, default_flow_style=False, indent=2)

        # Enterprise configuration (more strict)
        enterprise_config = copy.deepcopy(standard_config)
        enterprise_config["quality_gates"]["gates"]["coverage"]["threshold"] = 90.0
        enterprise_config["quality_gates"]["gates"]["complexity"]["max_complexity"] = 8
        enterprise_config["constitutional_enforcement"]["violation_threshold"] = "low"

        enterprise_path = self.base_configs_dir / "enterprise.yaml"
        with open(enterprise_path, "w", encoding="utf-8") as f:
            yaml.dump(enterprise_config, f, default_flow_style=False, indent=2)

        print("✅ Default base configurations created")

    def request_customization(
        self,
        project_name: str,
        rule_path: str,
        requested_value: Any,
        justification: str,
        requestor: str,
    ) -> CustomizationRequest:
        """Request a customization to a specific rule."""
        print(f"📋 Processing customization request for {project_name}")

        # Load project customization
        project_customization = self._load_project_customization(project_name)
        if not project_customization:
            raise ValueError(f"Project customization not found: {project_name}")

        # Find the customization rule
        rule_name = self._find_rule_name_by_path(rule_path)
        if not rule_name:
            raise ValueError(f"No customization rule found for path: {rule_path}")

        customization_rule = self.customization_rules[rule_name]

        # Get current value
        current_value = self._get_nested_value(
            project_customization.base_config, rule_path
        )
        if current_value is None:
            # Check if it's already customized
            current_value = self._get_nested_value(
                project_customization.customizations, rule_path
            )

        # Validate the request
        validation_errors = self._validate_customization_request(
            customization_rule, current_value, requested_value, project_customization
        )

        if validation_errors:
            raise ValueError(
                f"Customization request validation failed: {'; '.join(validation_errors)}"
            )

        # Create customization request
        request = CustomizationRequest(
            rule_path=rule_path,
            current_value=current_value,
            requested_value=requested_value,
            justification=justification,
            requestor=requestor,
            timestamp=datetime.utcnow().isoformat() + "Z",
            project_context={
                "project_name": project_name,
                "project_type": project_customization.project_type,
                "customization_level": project_customization.customization_level.value,
            },
            approved=not customization_rule.approval_required,
        )

        # If approval is not required, apply immediately
        if not customization_rule.approval_required:
            request.approved = True
            request.approver = "auto-approved"
            request.approval_timestamp = request.timestamp

            # Apply the customization
            self._apply_customization_request(project_customization, request)

        # Add to project's request history
        project_customization.applied_requests.append(request)
        project_customization.modified = datetime.utcnow().isoformat() + "Z"

        # Save updated project customization
        self._save_project_customization(project_customization)

        print(
            f"✅ Customization request {'applied' if request.approved else 'created (pending approval)'}"
        )
        return request

    def approve_customization_request(
        self, project_name: str, request_index: int, approver: str
    ) -> bool:
        """Approve a pending customization request."""
        print(f"✅ Approving customization request for {project_name}")

        # Load project customization
        project_customization = self._load_project_customization(project_name)
        if not project_customization:
            raise ValueError(f"Project customization not found: {project_name}")

        if request_index >= len(project_customization.applied_requests):
            raise ValueError(f"Request index {request_index} out of range")

        request = project_customization.applied_requests[request_index]

        if request.approved:
            print("⚠️ Request already approved")
            return True

        # Approve and apply
        request.approved = True
        request.approver = approver
        request.approval_timestamp = datetime.utcnow().isoformat() + "Z"

        # Apply the customization
        self._apply_customization_request(project_customization, request)

        # Save updated project customization
        project_customization.modified = datetime.utcnow().isoformat() + "Z"
        self._save_project_customization(project_customization)

        print("✅ Customization request approved and applied")
        return True

    def _apply_customization_request(
        self, project_customization: ProjectCustomization, request: CustomizationRequest
    ) -> None:
        """Apply an approved customization request."""
        self._set_nested_value(
            project_customization.customizations,
            request.rule_path,
            request.requested_value,
        )

    def generate_final_config(self, project_name: str) -> Dict[str, Any]:
        """Generate the final merged configuration for a project."""
        project_customization = self._load_project_customization(project_name)
        if not project_customization:
            raise ValueError(f"Project customization not found: {project_name}")

        # Start with base config
        final_config = copy.deepcopy(project_customization.base_config)

        # Apply all approved customizations
        for request in project_customization.applied_requests:
            if request.approved:
                self._set_nested_value(
                    final_config, request.rule_path, request.requested_value
                )

        # Apply direct customizations
        self._merge_nested_dict(final_config, project_customization.customizations)

        return final_config

    def _validate_customization_request(
        self,
        rule: CustomizationRule,
        current_value: Any,
        requested_value: Any,
        project_customization: ProjectCustomization,
    ) -> List[str]:
        """Validate a customization request against the rule constraints."""
        errors = []

        # Check customization level permission
        if rule.customization_level == CustomizationLevel.STRICT:
            errors.append(
                f"Rule '{rule.rule_path}' does not allow customization (strict mode)"
            )
            return errors

        # Check project's customization level
        if (
            project_customization.customization_level == CustomizationLevel.STRICT
            and rule.customization_level != CustomizationLevel.OVERRIDE
        ):
            errors.append("Project is in strict mode and does not allow customizations")

        # Validate value constraints
        if rule.min_value is not None and isinstance(requested_value, (int, float)):
            if requested_value < rule.min_value:
                errors.append(
                    f"Value {requested_value} is below minimum {rule.min_value}"
                )

        if rule.max_value is not None and isinstance(requested_value, (int, float)):
            if requested_value > rule.max_value:
                errors.append(
                    f"Value {requested_value} is above maximum {rule.max_value}"
                )

        if rule.allowed_values and requested_value not in rule.allowed_values:
            errors.append(
                f"Value {requested_value} not in allowed values: {rule.allowed_values}"
            )

        return errors

    def _find_rule_name_by_path(self, rule_path: str) -> Optional[str]:
        """Find customization rule name by rule path."""
        for rule_name, rule in self.customization_rules.items():
            if rule.rule_path == rule_path:
                return rule_name
        return None

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested dictionary value using dot notation."""
        if not data:
            return None

        keys = path.split(".")
        current = data

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set nested dictionary value using dot notation."""
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _merge_nested_dict(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> None:
        """Merge nested dictionaries, with override taking precedence."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_nested_dict(base[key], value)
            else:
                base[key] = value

    def _load_project_customization(
        self, project_name: str
    ) -> Optional[ProjectCustomization]:
        """Load project customization from disk."""
        project_path = self.project_customizations_dir / f"{project_name}.yaml"

        if not project_path.exists():
            return None

        try:
            with open(project_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Reconstruct CustomizationRequest objects
            applied_requests = []
            for req_data in data.get("applied_requests", []):
                request = CustomizationRequest(**req_data)
                applied_requests.append(request)

            return ProjectCustomization(
                project_name=data["project_name"],
                project_type=data["project_type"],
                customization_level=CustomizationLevel(data["customization_level"]),
                base_config=data["base_config"],
                customizations=data["customizations"],
                applied_requests=applied_requests,
                metadata=data["metadata"],
                created=data["created"],
                modified=data["modified"],
            )
        except Exception as e:
            print(f"⚠️ Failed to load project customization {project_name}: {e}")
            return None

    def _save_project_customization(
        self, project_customization: ProjectCustomization
    ) -> None:
        """Save project customization to disk."""
        project_path = (
            self.project_customizations_dir
            / f"{project_customization.project_name}.yaml"
        )

        # Convert to dictionary for serialization
        data = {
            "project_name": project_customization.project_name,
            "project_type": project_customization.project_type,
            "customization_level": project_customization.customization_level.value,
            "base_config": project_customization.base_config,
            "customizations": project_customization.customizations,
            "applied_requests": [
                asdict(req) for req in project_customization.applied_requests
            ],
            "metadata": project_customization.metadata,
            "created": project_customization.created,
            "modified": project_customization.modified,
        }

        with open(project_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)

    def list_customization_rules(
        self, category: Optional[RuleCategory] = None
    ) -> List[str]:
        """List available customization rules."""
        if category:
            return [
                name
                for name, rule in self.customization_rules.items()
                if rule.category == category
            ]
        return list(self.customization_rules.keys())

    def get_project_summary(self, project_name: str) -> Dict[str, Any]:
        """Get summary of project customizations."""
        project_customization = self._load_project_customization(project_name)
        if not project_customization:
            return {}

        approved_count = sum(
            1 for req in project_customization.applied_requests if req.approved
        )
        pending_count = sum(
            1 for req in project_customization.applied_requests if not req.approved
        )

        return {
            "project_name": project_customization.project_name,
            "project_type": project_customization.project_type,
            "customization_level": project_customization.customization_level.value,
            "total_requests": len(project_customization.applied_requests),
            "approved_customizations": approved_count,
            "pending_approvals": pending_count,
            "last_modified": project_customization.modified,
            "base_config": project_customization.metadata.get("base_config", "unknown"),
        }


def main():
    """Main CLI entry point for rule customization system."""
    parser = argparse.ArgumentParser(
        description="Manage constitutional rule customizations for project projects"
    )

    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(".kittify/config"),
        help="Configuration directory (default: .kittify/config)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create project command
    create_parser = subparsers.add_parser(
        "create-project", help="Create project customization"
    )
    create_parser.add_argument("project_name", help="Name of the project")
    create_parser.add_argument("project_type", help="Type of the project")
    create_parser.add_argument(
        "--customization-level",
        choices=["strict", "moderate", "flexible", "override"],
        default="moderate",
        help="Customization level (default: moderate)",
    )
    create_parser.add_argument(
        "--base-config",
        default="standard",
        help="Base configuration to use (default: standard)",
    )

    # Request customization command
    request_parser = subparsers.add_parser("request", help="Request rule customization")
    request_parser.add_argument("project_name", help="Name of the project")
    request_parser.add_argument("rule_path", help="Path to the rule (dot notation)")
    request_parser.add_argument("value", help="Requested value")
    request_parser.add_argument(
        "--justification", required=True, help="Justification for change"
    )
    request_parser.add_argument(
        "--requestor", required=True, help="Person requesting change"
    )

    # Approve customization command
    approve_parser = subparsers.add_parser(
        "approve", help="Approve customization request"
    )
    approve_parser.add_argument("project_name", help="Name of the project")
    approve_parser.add_argument(
        "request_index", type=int, help="Index of request to approve"
    )
    approve_parser.add_argument(
        "--approver", required=True, help="Person approving change"
    )

    # Generate config command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate final configuration"
    )
    generate_parser.add_argument("project_name", help="Name of the project")
    generate_parser.add_argument("--output", type=Path, help="Output file path")

    # List rules command
    list_parser = subparsers.add_parser("list-rules", help="List customization rules")
    list_parser.add_argument("--category", help="Filter by category")

    # Project summary command
    summary_parser = subparsers.add_parser(
        "summary", help="Show project customization summary"
    )
    summary_parser.add_argument("project_name", help="Name of the project")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize customization system
    system = RuleCustomizationSystem(args.config_dir)

    try:
        if args.command == "create-project":
            customization_level = CustomizationLevel(args.customization_level)
            project_customization = system.create_project_customization(
                args.project_name,
                args.project_type,
                customization_level,
                args.base_config,
            )
            print(
                f"✅ Project customization created: {project_customization.project_name}"
            )

        elif args.command == "request":
            # Try to parse value as appropriate type
            value = args.value
            if value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)
            elif value.lower() in ["true", "false"]:
                value = value.lower() == "true"

            request = system.request_customization(
                args.project_name,
                args.rule_path,
                value,
                args.justification,
                args.requestor,
            )
            print(
                f"✅ Customization request created: {request.rule_path} = {request.requested_value}"
            )

        elif args.command == "approve":
            system.approve_customization_request(
                args.project_name, args.request_index, args.approver
            )

        elif args.command == "generate":
            final_config = system.generate_final_config(args.project_name)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    yaml.dump(final_config, f, default_flow_style=False, indent=2)
                print(f"✅ Final configuration saved to {args.output}")
            else:
                print("📋 Final Configuration:")
                print(yaml.dump(final_config, default_flow_style=False, indent=2))

        elif args.command == "list-rules":
            category = None
            if args.category:
                try:
                    category = RuleCategory(args.category)
                except ValueError:
                    print(f"❌ Invalid category: {args.category}")
                    return

            rules = system.list_customization_rules(category)
            print(f"📋 Available customization rules ({len(rules)}):")
            for rule_name in rules:
                rule = system.customization_rules[rule_name]
                print(f"  • {rule_name} ({rule.category.value}) - {rule.description}")

        elif args.command == "summary":
            summary = system.get_project_summary(args.project_name)
            if summary:
                print(f"📊 Project Customization Summary: {summary['project_name']}")
                print(f"  Type: {summary['project_type']}")
                print(f"  Customization Level: {summary['customization_level']}")
                print(f"  Base Config: {summary['base_config']}")
                print(f"  Total Requests: {summary['total_requests']}")
                print(f"  Approved: {summary['approved_customizations']}")
                print(f"  Pending: {summary['pending_approvals']}")
                print(f"  Last Modified: {summary['last_modified']}")
            else:
                print(f"❌ Project customization not found: {args.project_name}")

    except Exception as e:
        print(f"❌ Command failed: {e}")


if __name__ == "__main__":
    main()
