#!/usr/bin/env python3
"""
Configuration Template System - T032

Manages configuration templates for constitutional enforcement rules.
Provides centralized template management and customization capabilities.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import os
import yaml
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import argparse


class TemplateType(Enum):
    """Types of configuration templates."""

    SE_RULES = "se_rules"
    QUALITY_GATES = "quality_gates"
    NAMING_CONVENTIONS = "naming_conventions"
    SECURITY_POLICIES = "security_policies"
    GITHUB_WORKFLOWS = "github_workflows"
    GIT_HOOKS = "git_hooks"
    PROJECT_CONFIG = "project_config"


@dataclass
class TemplateMetadata:
    """Metadata for configuration templates."""

    name: str
    template_type: TemplateType
    version: str
    description: str
    created: str
    modified: str
    author: str = "TeamReel Constitutional Foundation"
    constitutional_version: str = "001-sdd-constitutional-foundation"
    tags: List[str] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TemplateConfig:
    """Configuration for a specific template."""

    metadata: TemplateMetadata
    content: Dict[str, Any]
    schema_version: str = "1.0.0"
    customizable_fields: List[str] = None
    validation_rules: Dict[str, Any] = None

    def __post_init__(self):
        if self.customizable_fields is None:
            self.customizable_fields = []
        if self.validation_rules is None:
            self.validation_rules = {}


class ConfigurationTemplateManager:
    """Manages configuration templates for constitutional enforcement."""

    def __init__(self, templates_dir: Path):
        """Initialize template manager."""
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.templates_dir / "manifest.yaml"
        self.templates: Dict[str, TemplateConfig] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load template manifest from disk."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = yaml.safe_load(f)

                for template_name, template_data in manifest_data.get(
                    "templates", {}
                ).items():
                    try:
                        metadata = TemplateMetadata(**template_data["metadata"])
                        config = TemplateConfig(
                            metadata=metadata,
                            content=template_data.get("content", {}),
                            schema_version=template_data.get("schema_version", "1.0.0"),
                            customizable_fields=template_data.get(
                                "customizable_fields", []
                            ),
                            validation_rules=template_data.get("validation_rules", {}),
                        )
                        self.templates[template_name] = config
                    except Exception as e:
                        print(f"⚠️ Failed to load template {template_name}: {e}")
            except Exception as e:
                print(f"⚠️ Failed to load manifest: {e}")
                self._create_default_manifest()
        else:
            self._create_default_manifest()

    def _create_default_manifest(self) -> None:
        """Create default template manifest."""
        default_manifest = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "constitutional_version": "001-sdd-constitutional-foundation",
            },
            "templates": {},
        }

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(default_manifest, f, default_flow_style=False, indent=2)

    def save_manifest(self) -> None:
        """Save template manifest to disk."""
        manifest_data = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "constitutional_version": "001-sdd-constitutional-foundation",
            },
            "templates": {},
        }

        for template_name, template_config in self.templates.items():
            manifest_data["templates"][template_name] = {
                "metadata": asdict(template_config.metadata),
                "content": template_config.content,
                "schema_version": template_config.schema_version,
                "customizable_fields": template_config.customizable_fields,
                "validation_rules": template_config.validation_rules,
            }

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, default_flow_style=False, indent=2)

    def create_default_templates(self) -> None:
        """Create default configuration templates."""
        print("🏗️ Creating default configuration templates...")

        # SE Rules Template
        self._create_se_rules_template()

        # Quality Gates Template
        self._create_quality_gates_template()

        # Naming Conventions Template
        self._create_naming_conventions_template()

        # Security Policies Template
        self._create_security_policies_template()

        # GitHub Workflows Template
        self._create_github_workflows_template()

        # Project Configuration Template
        self._create_project_config_template()

        # Save manifest
        self.save_manifest()
        print("✅ Default templates created successfully")

    def _create_se_rules_template(self) -> None:
        """Create SE rules configuration template."""
        metadata = TemplateMetadata(
            name="se_rules_standard",
            template_type=TemplateType.SE_RULES,
            version="1.0.0",
            description="Standard Software Engineering principles configuration",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["standard", "constitutional", "se-principles"],
            dependencies=[],
        )

        content = {
            "constitutional_enforcement": {
                "version": "1.0.0",
                "strict_mode": True,
                "violation_threshold": "medium",
                "principles": {
                    "SRP": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Single Responsibility Principle - Each class/function should have one reason to change",
                        "metrics": {
                            "max_methods_per_class": 10,
                            "max_lines_per_function": 50,
                            "max_responsibilities": 1,
                        },
                    },
                    "Encapsulation": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Encapsulation - Hide internal implementation details",
                        "metrics": {
                            "min_private_ratio": 0.6,
                            "max_public_methods": 5,
                            "require_property_access": True,
                        },
                    },
                    "Loose_Coupling": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Loose Coupling - Minimize dependencies between components",
                        "metrics": {
                            "max_dependencies": 5,
                            "max_coupling_factor": 0.3,
                            "prefer_composition": True,
                        },
                    },
                    "Reusability": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Reusability - Design for reuse across contexts",
                        "metrics": {
                            "min_reuse_score": 0.7,
                            "max_duplicated_lines": 10,
                            "require_generic_design": True,
                        },
                    },
                    "Portability": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Portability - Work across different environments",
                        "metrics": {
                            "cross_platform_required": True,
                            "avoid_hardcoded_paths": True,
                            "use_environment_variables": True,
                        },
                    },
                    "Defensibility": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Defensibility - Robust error handling and validation",
                        "metrics": {
                            "min_error_coverage": 0.8,
                            "require_input_validation": True,
                            "max_exception_types": 3,
                        },
                    },
                    "Maintainability": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Maintainability - Easy to understand and modify",
                        "metrics": {
                            "max_complexity": 10,
                            "min_documentation_ratio": 0.2,
                            "require_type_hints": True,
                        },
                    },
                    "Simplicity": {
                        "enabled": True,
                        "weight": 1.0,
                        "description": "Simplicity - Prefer simple solutions over complex ones",
                        "metrics": {
                            "max_nesting_depth": 3,
                            "max_parameters": 4,
                            "avoid_premature_optimization": True,
                        },
                    },
                },
                "enforcement_levels": {
                    "strict": {
                        "fail_on_any_violation": True,
                        "require_all_principles": True,
                    },
                    "moderate": {
                        "fail_on_critical_violations": True,
                        "warning_threshold": 0.8,
                    },
                    "lenient": {"warning_only": True, "critical_only": True},
                },
            }
        }

        customizable_fields = [
            "constitutional_enforcement.strict_mode",
            "constitutional_enforcement.violation_threshold",
            "constitutional_enforcement.principles.*.enabled",
            "constitutional_enforcement.principles.*.weight",
            "constitutional_enforcement.principles.*.metrics.*",
        ]

        validation_rules = {
            "required_fields": [
                "constitutional_enforcement.version",
                "constitutional_enforcement.principles",
            ],
            "weight_range": [0.0, 2.0],
            "valid_thresholds": ["low", "medium", "high", "critical"],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["se_rules_standard"] = template_config
        print("  ✅ SE Rules template")

    def _create_quality_gates_template(self) -> None:
        """Create quality gates configuration template."""
        metadata = TemplateMetadata(
            name="quality_gates_standard",
            template_type=TemplateType.QUALITY_GATES,
            version="1.0.0",
            description="Standard quality gates configuration for TeamReel projects",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["quality", "gates", "validation"],
            dependencies=["se_rules_standard"],
        )

        content = {
            "quality_gates": {
                "version": "1.0.0",
                "enforcement_mode": "strict",
                "gates": {
                    "coverage": {
                        "enabled": True,
                        "threshold": 80.0,
                        "include_branches": True,
                        "exclude_patterns": ["test_*", "*_test.py", "conftest.py"],
                        "fail_under": True,
                        "generate_report": True,
                    },
                    "complexity": {
                        "enabled": True,
                        "max_complexity": 10,
                        "include_classes": True,
                        "include_functions": True,
                        "fail_on_violation": True,
                        "show_details": True,
                    },
                    "security": {
                        "enabled": True,
                        "severity_threshold": "high",
                        "scan_dependencies": True,
                        "scan_code": True,
                        "fail_on_critical": True,
                        "generate_report": True,
                    },
                    "naming": {
                        "enabled": True,
                        "enforce_conventions": True,
                        "fail_on_violations": True,
                        "check_all_languages": True,
                        "case_sensitivity": True,
                    },
                    "documentation": {
                        "enabled": True,
                        "min_docstring_coverage": 70.0,
                        "require_type_hints": True,
                        "check_api_docs": True,
                    },
                    "dependencies": {
                        "enabled": True,
                        "check_vulnerabilities": True,
                        "check_licenses": True,
                        "max_age_days": 365,
                        "allowed_licenses": ["MIT", "Apache-2.0", "BSD-3-Clause"],
                    },
                },
                "reporting": {
                    "format": "json",
                    "output_directory": "reports/quality_gates",
                    "include_metrics": True,
                    "generate_dashboard": True,
                },
                "integration": {
                    "pre_commit": True,
                    "ci_cd": True,
                    "ide_integration": True,
                },
            }
        }

        customizable_fields = [
            "quality_gates.enforcement_mode",
            "quality_gates.gates.*.enabled",
            "quality_gates.gates.coverage.threshold",
            "quality_gates.gates.complexity.max_complexity",
            "quality_gates.gates.security.severity_threshold",
            "quality_gates.gates.documentation.min_docstring_coverage",
        ]

        validation_rules = {
            "required_fields": ["quality_gates.version", "quality_gates.gates"],
            "threshold_range": [0.0, 100.0],
            "valid_severities": ["low", "medium", "high", "critical"],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["quality_gates_standard"] = template_config
        print("  ✅ Quality Gates template")

    def _create_naming_conventions_template(self) -> None:
        """Create naming conventions configuration template."""
        metadata = TemplateMetadata(
            name="naming_conventions_teamreel",
            template_type=TemplateType.NAMING_CONVENTIONS,
            version="1.0.0",
            description="TeamReel naming conventions for multi-language projects",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["naming", "conventions", "teamreel"],
            dependencies=[],
        )

        content = {
            "naming_conventions": {
                "version": "1.0.0",
                "enforcement_level": "strict",
                "languages": {
                    "python": {
                        "functions": "snake_case",
                        "variables": "snake_case",
                        "classes": "PascalCase",
                        "constants": "UPPER_SNAKE_CASE",
                        "modules": "snake_case",
                        "packages": "snake_case",
                        "private_prefix": "_",
                        "protected_prefix": "_",
                        "dunder_allowed": True,
                    },
                    "javascript": {
                        "functions": "camelCase",
                        "variables": "camelCase",
                        "classes": "PascalCase",
                        "constants": "UPPER_SNAKE_CASE",
                        "files": "camelCase",
                        "components": "PascalCase",
                        "props": "camelCase",
                    },
                    "typescript": {
                        "functions": "camelCase",
                        "variables": "camelCase",
                        "classes": "PascalCase",
                        "interfaces": "PascalCase",
                        "types": "PascalCase",
                        "enums": "PascalCase",
                        "constants": "UPPER_SNAKE_CASE",
                        "files": "camelCase",
                        "components": "PascalCase",
                    },
                },
                "api_endpoints": {
                    "format": "kebab-case",
                    "trailing_slash": True,
                    "resource_naming": "plural",
                    "version_prefix": "/api/v{version}/",
                    "path_parameters": "kebab-case",
                },
                "database": {
                    "tables": "snake_case",
                    "columns": "snake_case",
                    "indexes": "snake_case",
                    "constraints": "snake_case",
                    "foreign_keys": "snake_case",
                },
                "files_and_directories": {
                    "python_files": "snake_case",
                    "javascript_files": "camelCase",
                    "config_files": "kebab-case",
                    "directories": "snake_case",
                    "test_files": "test_*.py",
                    "fixture_files": "fixture_*.py",
                },
                "validation": {
                    "max_identifier_length": 50,
                    "min_identifier_length": 2,
                    "allow_abbreviations": False,
                    "reserved_words_check": True,
                    "unicode_allowed": False,
                },
            }
        }

        customizable_fields = [
            "naming_conventions.enforcement_level",
            "naming_conventions.languages.*.functions",
            "naming_conventions.languages.*.variables",
            "naming_conventions.languages.*.classes",
            "naming_conventions.api_endpoints.format",
            "naming_conventions.validation.max_identifier_length",
        ]

        validation_rules = {
            "required_fields": [
                "naming_conventions.version",
                "naming_conventions.languages",
            ],
            "valid_cases": [
                "snake_case",
                "camelCase",
                "PascalCase",
                "kebab-case",
                "UPPER_SNAKE_CASE",
            ],
            "valid_enforcement": ["strict", "moderate", "lenient"],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["naming_conventions_teamreel"] = template_config
        print("  ✅ Naming Conventions template")

    def _create_security_policies_template(self) -> None:
        """Create security policies configuration template."""
        metadata = TemplateMetadata(
            name="security_policies_standard",
            template_type=TemplateType.SECURITY_POLICIES,
            version="1.0.0",
            description="Standard security policies for TeamReel projects",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["security", "policies", "scanning"],
            dependencies=[],
        )

        content = {
            "security_policies": {
                "version": "1.0.0",
                "enforcement_level": "high",
                "code_scanning": {
                    "enabled": True,
                    "tools": ["bandit", "safety", "semgrep"],
                    "severity_threshold": "medium",
                    "fail_on_critical": True,
                    "exclude_patterns": ["test_*", "tests/*"],
                    "custom_rules": [],
                },
                "dependency_scanning": {
                    "enabled": True,
                    "vulnerability_databases": ["NVD", "PyUp", "npm-audit"],
                    "max_severity": "high",
                    "auto_fix": False,
                    "exclude_dev_dependencies": False,
                },
                "secrets_detection": {
                    "enabled": True,
                    "patterns": [
                        "aws_access_key_id",
                        "aws_secret_access_key",
                        "github_token",
                        "database_password",
                        "api_key",
                        "private_key",
                    ],
                    "exclude_files": [".gitignore", "*.md"],
                    "entropy_threshold": 4.0,
                },
                "secure_coding": {
                    "require_input_validation": True,
                    "require_output_encoding": True,
                    "require_authentication": True,
                    "require_authorization": True,
                    "require_https": True,
                    "require_csrf_protection": True,
                },
                "compliance": {
                    "frameworks": ["OWASP", "NIST"],
                    "standards": ["ISO27001", "SOC2"],
                    "audit_trail": True,
                    "privacy_controls": True,
                },
            }
        }

        customizable_fields = [
            "security_policies.enforcement_level",
            "security_policies.code_scanning.severity_threshold",
            "security_policies.dependency_scanning.max_severity",
            "security_policies.secrets_detection.entropy_threshold",
        ]

        validation_rules = {
            "required_fields": ["security_policies.version"],
            "valid_severities": ["low", "medium", "high", "critical"],
            "valid_enforcement": ["low", "medium", "high", "critical"],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["security_policies_standard"] = template_config
        print("  ✅ Security Policies template")

    def _create_github_workflows_template(self) -> None:
        """Create GitHub workflows configuration template."""
        metadata = TemplateMetadata(
            name="github_workflows_constitutional",
            template_type=TemplateType.GITHUB_WORKFLOWS,
            version="1.0.0",
            description="GitHub Actions workflows for constitutional validation",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["github", "workflows", "ci-cd"],
            dependencies=["quality_gates_standard"],
        )

        content = {
            "workflows": {
                "constitutional_validation": {
                    "name": "Constitutional Validation",
                    "triggers": ["push", "pull_request"],
                    "branches": ["main", "develop"],
                    "jobs": {
                        "validate": {
                            "runs_on": "ubuntu-latest",
                            "python_version": "3.11",
                            "steps": [
                                "checkout",
                                "setup_python",
                                "install_dependencies",
                                "run_quality_gates",
                                "upload_reports",
                            ],
                        }
                    },
                },
                "security_scan": {
                    "name": "Security Scan",
                    "triggers": ["push", "schedule"],
                    "schedule": "0 2 * * *",  # Daily at 2 AM
                    "jobs": {
                        "security": {
                            "runs_on": "ubuntu-latest",
                            "steps": ["checkout", "security_scan", "upload_sarif"],
                        }
                    },
                },
                "dependency_update": {
                    "name": "Dependency Update",
                    "triggers": ["schedule"],
                    "schedule": "0 3 * * 1",  # Weekly on Monday at 3 AM
                    "jobs": {
                        "update": {
                            "runs_on": "ubuntu-latest",
                            "steps": [
                                "checkout",
                                "update_dependencies",
                                "run_tests",
                                "create_pr",
                            ],
                        }
                    },
                },
            }
        }

        customizable_fields = [
            "workflows.*.triggers",
            "workflows.*.branches",
            "workflows.*.jobs.*.runs_on",
            "workflows.*.jobs.*.python_version",
        ]

        validation_rules = {
            "required_fields": ["workflows"],
            "valid_triggers": ["push", "pull_request", "schedule", "workflow_dispatch"],
            "valid_runners": ["ubuntu-latest", "windows-latest", "macos-latest"],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["github_workflows_constitutional"] = template_config
        print("  ✅ GitHub Workflows template")

    def _create_project_config_template(self) -> None:
        """Create project configuration template."""
        metadata = TemplateMetadata(
            name="project_config_teamreel",
            template_type=TemplateType.PROJECT_CONFIG,
            version="1.0.0",
            description="Standard TeamReel project configuration",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=["project", "config", "teamreel"],
            dependencies=[],
        )

        content = {
            "project_config": {
                "version": "1.0.0",
                "project_type": "teamreel_standard",
                "tech_stack": {
                    "frontend": "Next.js 14 + TypeScript + Tailwind CSS",
                    "backend": "Django REST Framework + Python 3.11+",
                    "ai_engine": "LangGraph + OpenAI APIs",
                    "database": "PostgreSQL (production), SQLite (tests)",
                    "storage": "AWS S3 with signed URLs",
                    "testing": "Pytest (backend), Vitest (frontend), Playwright (E2E)",
                    "linting": "Ruff (Python), ESLint + TypeScript (Frontend)",
                    "deployment": "Railway (staging + production)",
                },
                "structure": {
                    "frontend": "frontend/src/modules/{auth,dashboard,workflows,editor,templates}/",
                    "backend": "backend/apps/{users,projects,media,ai_engine,workflows,billing}/",
                    "ai": "ai/{workflows,agents,tools,schemas}/",
                    "shared": "shared/{utils,common,types}/",
                    "tests": "tests/ (mirror source structure)",
                },
                "quality_standards": {
                    "test_coverage": 80,
                    "complexity_threshold": 10,
                    "security_level": "high",
                    "naming_enforcement": True,
                    "documentation_required": True,
                },
                "development": {
                    "python_version": "3.11+",
                    "node_version": "18+",
                    "pre_commit_hooks": True,
                    "automated_testing": True,
                    "continuous_integration": True,
                },
            }
        }

        customizable_fields = [
            "project_config.project_type",
            "project_config.quality_standards.test_coverage",
            "project_config.quality_standards.complexity_threshold",
            "project_config.development.python_version",
        ]

        validation_rules = {
            "required_fields": ["project_config.version", "project_config.tech_stack"],
            "valid_project_types": [
                "teamreel_standard",
                "teamreel_minimal",
                "teamreel_enterprise",
            ],
        }

        template_config = TemplateConfig(
            metadata=metadata,
            content=content,
            customizable_fields=customizable_fields,
            validation_rules=validation_rules,
        )

        self.templates["project_config_teamreel"] = template_config
        print("  ✅ Project Configuration template")

    def get_template(self, template_name: str) -> Optional[TemplateConfig]:
        """Get a specific template by name."""
        return self.templates.get(template_name)

    def list_templates(self, template_type: Optional[TemplateType] = None) -> List[str]:
        """List available templates, optionally filtered by type."""
        if template_type:
            return [
                name
                for name, config in self.templates.items()
                if config.metadata.template_type == template_type
            ]
        return list(self.templates.keys())

    def customize_template(
        self, template_name: str, customizations: Dict[str, Any]
    ) -> TemplateConfig:
        """Apply customizations to a template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]
        customized_content = template.content.copy()

        # Apply customizations
        for field_path, value in customizations.items():
            self._set_nested_value(customized_content, field_path, value)

        # Create new template with customizations
        customized_metadata = TemplateMetadata(
            name=f"{template_name}_customized",
            template_type=template.metadata.template_type,
            version=template.metadata.version,
            description=f"{template.metadata.description} (customized)",
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            tags=template.metadata.tags + ["customized"],
        )

        return TemplateConfig(
            metadata=customized_metadata,
            content=customized_content,
            schema_version=template.schema_version,
            customizable_fields=template.customizable_fields,
            validation_rules=template.validation_rules,
        )

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested dictionary value using dot notation."""
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def export_template(
        self, template_name: str, output_path: Path, format: str = "yaml"
    ) -> None:
        """Export template to file."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        if format.lower() == "yaml":
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(template.content, f, default_flow_style=False, indent=2)
        elif format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(template.content, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"✅ Template '{template_name}' exported to {output_path}")

    def validate_template(self, template_name: str) -> List[str]:
        """Validate template against its validation rules."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]
        errors = []

        # Check required fields
        required_fields = template.validation_rules.get("required_fields", [])
        for field_path in required_fields:
            if not self._has_nested_value(template.content, field_path):
                errors.append(f"Required field missing: {field_path}")

        return errors

    def _has_nested_value(self, data: Dict[str, Any], path: str) -> bool:
        """Check if nested dictionary has value at path."""
        keys = path.split(".")
        current = data

        try:
            for key in keys:
                current = current[key]
            return True
        except (KeyError, TypeError):
            return False


def main():
    """Main CLI entry point for configuration template management."""
    parser = argparse.ArgumentParser(
        description="Manage configuration templates for TeamReel Constitutional Foundation"
    )

    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path(".kittify/templates"),
        help="Directory containing templates (default: .kittify/templates)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create default templates")

    # List command
    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument("--type", type=str, help="Filter by template type")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export template to file")
    export_parser.add_argument("template_name", help="Name of template to export")
    export_parser.add_argument("output_path", type=Path, help="Output file path")
    export_parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate template")
    validate_parser.add_argument("template_name", help="Name of template to validate")

    # Customize command
    customize_parser = subparsers.add_parser("customize", help="Customize template")
    customize_parser.add_argument("template_name", help="Name of template to customize")
    customize_parser.add_argument(
        "--customizations",
        type=str,
        required=True,
        help="JSON string of customizations",
    )
    customize_parser.add_argument(
        "--output", type=Path, help="Output path for customized template"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize template manager
    manager = ConfigurationTemplateManager(args.templates_dir)

    try:
        if args.command == "create":
            manager.create_default_templates()

        elif args.command == "list":
            template_type = None
            if args.type:
                try:
                    template_type = TemplateType(args.type)
                except ValueError:
                    print(f"❌ Invalid template type: {args.type}")
                    return

            templates = manager.list_templates(template_type)
            print(f"📋 Available templates ({len(templates)}):")
            for template_name in templates:
                template = manager.get_template(template_name)
                print(
                    f"  • {template_name} ({template.metadata.template_type.value}) - {template.metadata.description}"
                )

        elif args.command == "export":
            manager.export_template(args.template_name, args.output_path, args.format)

        elif args.command == "validate":
            errors = manager.validate_template(args.template_name)
            if errors:
                print(f"❌ Template validation failed ({len(errors)} errors):")
                for error in errors:
                    print(f"  • {error}")
            else:
                print(f"✅ Template '{args.template_name}' is valid")

        elif args.command == "customize":
            try:
                customizations = json.loads(args.customizations)
                customized_template = manager.customize_template(
                    args.template_name, customizations
                )

                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        yaml.dump(
                            customized_template.content,
                            f,
                            default_flow_style=False,
                            indent=2,
                        )
                    print(f"✅ Customized template saved to {args.output}")
                else:
                    print("📋 Customized template:")
                    print(
                        yaml.dump(
                            customized_template.content,
                            default_flow_style=False,
                            indent=2,
                        )
                    )
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in customizations: {e}")
            except Exception as e:
                print(f"❌ Customization failed: {e}")

    except Exception as e:
        print(f"❌ Command failed: {e}")


if __name__ == "__main__":
    main()
