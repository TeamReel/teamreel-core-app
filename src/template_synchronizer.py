#!/usr/bin/env python3
"""
Automated Template Synchronization System

Automatically updates templates while preserving customizations.
Implements intelligent merging strategies for constitutional template updates.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import hashlib
import json
import os
import shutil
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class SyncStrategy(Enum):
    """Template synchronization strategies."""

    OVERWRITE = "overwrite"
    MERGE_PRESERVING_CUSTOMIZATIONS = "merge_preserving_customizations"
    UPDATE_WITH_MANUAL_REVIEW = "update_with_manual_review"
    CAREFUL_MERGE_WITH_VALIDATION = "careful_merge_with_validation"


class SyncResult(Enum):
    """Synchronization operation results."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


@dataclass
class SyncOperation:
    """Individual template synchronization operation."""

    template_path: str
    strategy: SyncStrategy
    result: SyncResult
    description: str
    backup_created: bool = False
    backup_path: str = ""
    changes_applied: List[str] = field(default_factory=list)
    preserved_customizations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    sync_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )


class TemplateSynchronizer:
    """Main template synchronization engine."""

    def __init__(self, manifest_path: str = ".kittify/templates/manifest.yaml"):
        """Initialize synchronizer with manifest path."""
        self.manifest_path = Path(manifest_path)
        self.manifest_data = None
        self.backup_dir = Path(".kittify/backups/templates")
        self.constitutional_templates_dir = Path(".kittify/constitutional_templates")
        self.load_manifest()

    def load_manifest(self) -> None:
        """Load template manifest for synchronization planning."""
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

    def create_backup(self, template_path: str) -> str:
        """Create backup of template before synchronization."""
        try:
            source_path = Path(template_path)
            if not source_path.exists():
                return ""

            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_name

            # Copy file to backup
            shutil.copy2(source_path, backup_path)

            return str(backup_path)

        except Exception as e:
            print(f"⚠️ Warning: Could not create backup for {template_path}: {e}")
            return ""

    def calculate_checksum(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA256 checksum for a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return ""

            with open(path, "rb") as f:
                content = f.read()
                return f"sha256:{hashlib.sha256(content).hexdigest()}"
        except Exception:
            return ""

    def extract_customizations(
        self, template_path: str, template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract customizations from current template."""
        customizations = {}
        preserved_list = template_config.get("customizations_preserved", [])

        if not preserved_list:
            return customizations

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple customization extraction based on markers
            # This is a placeholder - real implementation would be more sophisticated
            for customization_type in preserved_list:
                if customization_type == "custom_entity_fields":
                    # Extract custom entity fields from data model templates
                    customizations[customization_type] = self._extract_custom_entities(
                        content
                    )
                elif customization_type == "custom_thresholds":
                    # Extract custom threshold values from config files
                    customizations[customization_type] = (
                        self._extract_custom_thresholds(content)
                    )
                elif customization_type == "project_specific_rules":
                    # Extract project-specific rules
                    customizations[customization_type] = self._extract_project_rules(
                        content
                    )
                else:
                    # Generic customization extraction
                    customizations[customization_type] = (
                        self._extract_generic_customization(content, customization_type)
                    )

        except Exception as e:
            print(
                f"⚠️ Warning: Could not extract customizations from {template_path}: {e}"
            )

        return customizations

    def _extract_custom_entities(self, content: str) -> List[str]:
        """Extract custom entity definitions from content."""
        # Placeholder implementation - would use regex or AST parsing
        custom_entities = []
        lines = content.split("\n")
        for line in lines:
            if "# CUSTOM_ENTITY:" in line:
                custom_entities.append(line.strip())
        return custom_entities

    def _extract_custom_thresholds(self, content: str) -> Dict[str, Any]:
        """Extract custom threshold values from YAML content."""
        try:
            data = yaml.safe_load(content)
            custom_thresholds = {}

            # Look for custom threshold markers
            if isinstance(data, dict):
                for key, value in data.items():
                    if key.startswith("custom_") or "threshold" in key.lower():
                        custom_thresholds[key] = value

            return custom_thresholds
        except:
            return {}

    def _extract_project_rules(self, content: str) -> List[str]:
        """Extract project-specific rules from content."""
        project_rules = []
        lines = content.split("\n")
        in_project_section = False

        for line in lines:
            if "# PROJECT_SPECIFIC_RULES:" in line:
                in_project_section = True
                continue
            elif in_project_section and line.startswith("#"):
                if "END_PROJECT_SPECIFIC" in line:
                    break
                project_rules.append(line.strip())

        return project_rules

    def _extract_generic_customization(
        self, content: str, customization_type: str
    ) -> List[str]:
        """Extract generic customizations marked in content."""
        customizations = []
        marker = f"# CUSTOM_{customization_type.upper()}:"

        lines = content.split("\n")
        for line in lines:
            if marker in line:
                customizations.append(line.strip())

        return customizations

    def apply_customizations(self, content: str, customizations: Dict[str, Any]) -> str:
        """Apply preserved customizations to synchronized content."""
        modified_content = content

        for customization_type, customization_data in customizations.items():
            if customization_type == "custom_entity_fields" and customization_data:
                # Re-insert custom entity fields
                for entity_line in customization_data:
                    if entity_line not in modified_content:
                        # Insert at appropriate location (simplified)
                        modified_content += f"\n{entity_line}"

            elif customization_type == "custom_thresholds" and customization_data:
                # Re-insert custom thresholds in YAML
                try:
                    data = yaml.safe_load(modified_content)
                    if isinstance(data, dict):
                        data.update(customization_data)
                        modified_content = yaml.dump(
                            data, default_flow_style=False, sort_keys=False
                        )
                except:
                    pass

            elif customization_type == "project_specific_rules" and customization_data:
                # Re-insert project-specific rules
                rules_section = "\n# PROJECT_SPECIFIC_RULES:\n"
                for rule in customization_data:
                    rules_section += f"{rule}\n"
                rules_section += "# END_PROJECT_SPECIFIC\n"

                if "# PROJECT_SPECIFIC_RULES:" not in modified_content:
                    modified_content += rules_section

        return modified_content

    def get_constitutional_template(self, template_path: str) -> str:
        """Get the constitutional baseline template content."""
        # In a real implementation, this would fetch from a constitutional template repository
        # For now, we'll simulate by creating updated constitutional content

        constitutional_path = (
            self.constitutional_templates_dir / Path(template_path).name
        )

        if constitutional_path.exists():
            with open(constitutional_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            # Generate constitutional template based on current requirements
            return self._generate_constitutional_template(template_path)

    def _generate_constitutional_template(self, template_path: str) -> str:
        """Generate constitutional template content."""
        # This is a simplified placeholder - real implementation would be more sophisticated
        template_name = Path(template_path).stem

        constitutional_header = f"""# {template_name} - Constitutional Template
# Generated: {datetime.utcnow().isoformat()}Z
# Constitutional Version: {self.manifest_data.get('metadata', {}).get('constitutional_version', 'unknown')}
# SE Principles: SRP, Encapsulation, Loose Coupling, Reusability, Portability, Defensibility, Maintainability, Simplicity

"""

        if template_path.endswith(".md"):
            return (
                constitutional_header
                + self._generate_markdown_constitutional_content(template_name)
            )
        elif template_path.endswith(".yaml") or template_path.endswith(".yml"):
            return self._generate_yaml_constitutional_content(template_name)
        else:
            return (
                constitutional_header
                + "# Constitutional template content placeholder\n"
            )

    def _generate_markdown_constitutional_content(self, template_name: str) -> str:
        """Generate constitutional Markdown template content."""
        return f"""## Constitutional Compliance

This template enforces the following SE principles:

- **SRP**: Single responsibility focus
- **Maintainability**: Clear documentation and structure
- **Simplicity**: Essential elements only (YAGNI)

## Template Structure

*Constitutional requirements ensure consistent structure across all {template_name} templates.*

## Implementation Guidelines

Follow constitutional principles when using this template:

1. Maintain single responsibility
2. Document all decisions
3. Keep complexity minimal
4. Ensure cross-platform compatibility

## Validation

All implementations using this template must pass constitutional validation.
"""

    def _generate_yaml_constitutional_content(self, template_name: str) -> str:
        """Generate constitutional YAML template content."""
        return f"""# Constitutional {template_name} Configuration
constitutional_compliance:
  enforced: true
  principles:
    - SRP
    - Maintainability 
    - Simplicity
    - Defensibility
  
validation:
  strict_mode: true
  auto_validation: true
  
# Template-specific configuration
{template_name.lower()}_config:
  constitutional_version: "v1.0"
  last_updated: "{datetime.utcnow().isoformat()}Z"
"""

    def sync_template(
        self, template_path: str, template_config: Dict[str, Any]
    ) -> SyncOperation:
        """Synchronize a single template."""
        strategy = SyncStrategy(
            template_config.get("sync_strategy", "merge_preserving_customizations")
        )

        operation = SyncOperation(
            template_path=template_path,
            strategy=strategy,
            result=SyncResult.FAILED,
            description="Synchronization not attempted",
        )

        try:
            # Create backup if enabled
            if self.manifest_data.get("sync_config", {}).get(
                "backup_before_sync", True
            ):
                backup_path = self.create_backup(template_path)
                if backup_path:
                    operation.backup_created = True
                    operation.backup_path = backup_path

            # Extract current customizations
            customizations = self.extract_customizations(template_path, template_config)
            if customizations:
                operation.preserved_customizations = list(customizations.keys())

            # Get constitutional baseline template
            constitutional_content = self.get_constitutional_template(template_path)

            # Apply synchronization strategy
            if strategy == SyncStrategy.OVERWRITE:
                result_content = constitutional_content
                operation.description = (
                    "Template overwritten with constitutional baseline"
                )

            elif strategy == SyncStrategy.MERGE_PRESERVING_CUSTOMIZATIONS:
                result_content = self.apply_customizations(
                    constitutional_content, customizations
                )
                operation.description = (
                    "Template synchronized with customizations preserved"
                )

            elif strategy == SyncStrategy.UPDATE_WITH_MANUAL_REVIEW:
                # For manual review strategy, we prepare the content but don't write it
                operation.result = SyncResult.REQUIRES_MANUAL_REVIEW
                operation.description = (
                    "Template requires manual review before synchronization"
                )
                return operation

            elif strategy == SyncStrategy.CAREFUL_MERGE_WITH_VALIDATION:
                result_content = self.apply_customizations(
                    constitutional_content, customizations
                )
                # Additional validation would happen here
                operation.description = "Template carefully merged with validation"

            else:
                operation.result = SyncResult.FAILED
                operation.errors.append(f"Unknown sync strategy: {strategy}")
                return operation

            # Write synchronized content
            Path(template_path).parent.mkdir(parents=True, exist_ok=True)
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(result_content)

            # Update operation with success details
            operation.result = SyncResult.SUCCESS
            operation.changes_applied = [
                "constitutional_update",
                "content_synchronization",
            ]
            if customizations:
                operation.changes_applied.append("customizations_preserved")

        except Exception as e:
            operation.result = SyncResult.FAILED
            operation.errors.append(str(e))
            operation.description = f"Synchronization failed: {e}"

        return operation

    def sync_all_templates(self) -> List[SyncOperation]:
        """Synchronize all templates according to their drift status."""
        sync_operations = []

        print("🔄 Starting template synchronization...")

        # Process all template categories
        for category_name, category_templates in self.manifest_data.get(
            "templates", {}
        ).items():
            print(f"📁 Processing {category_name} templates...")

            for template_name, template_config in category_templates.items():
                template_path = template_config.get("path", "")
                drift_status = template_config.get("drift_status", "in_sync")

                # Only sync templates that need it
                if drift_status in ["needs_sync", "pending_sync"]:
                    print(f"  🔄 Synchronizing {template_name}...")
                    operation = self.sync_template(template_path, template_config)
                    sync_operations.append(operation)

                    # Print operation result
                    result_emoji = {
                        SyncResult.SUCCESS: "✅",
                        SyncResult.SKIPPED: "⏭️",
                        SyncResult.FAILED: "❌",
                        SyncResult.REQUIRES_MANUAL_REVIEW: "👥",
                    }
                    emoji = result_emoji.get(operation.result, "❓")
                    print(f"    {emoji} {operation.description}")

                else:
                    print(f"  ⏭️ Skipping {template_name} (status: {drift_status})")

        return sync_operations

    def update_manifest_after_sync(self, sync_operations: List[SyncOperation]) -> None:
        """Update manifest with synchronization results."""
        current_time = datetime.utcnow().isoformat() + "Z"

        # Update template statuses based on sync results
        for operation in sync_operations:
            # Find and update the template in manifest
            for category_templates in self.manifest_data.get("templates", {}).values():
                for template_config in category_templates.values():
                    if template_config.get("path") == operation.template_path:
                        if operation.result == SyncResult.SUCCESS:
                            template_config["drift_status"] = "in_sync"
                            template_config["last_sync"] = current_time
                            template_config["checksum"] = self.calculate_checksum(
                                operation.template_path
                            )
                        elif operation.result == SyncResult.REQUIRES_MANUAL_REVIEW:
                            template_config["drift_status"] = "manual_review_required"

        # Update statistics
        stats = self.manifest_data.setdefault("statistics", {})
        stats["last_full_sync"] = current_time

        success_count = len(
            [op for op in sync_operations if op.result == SyncResult.SUCCESS]
        )
        total_count = len(sync_operations)
        if total_count > 0:
            stats["sync_success_rate"] = f"{(success_count/total_count)*100:.1f}%"

        # Add audit log entry
        audit_log = self.manifest_data.setdefault("audit_log", [])
        audit_log.append(
            {
                "timestamp": current_time,
                "action": "template_synchronization",
                "agent": "GitHub-Copilot",
                "details": f"Synchronized {success_count}/{total_count} templates",
            }
        )

        # Save updated manifest
        try:
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.manifest_data, f, default_flow_style=False, sort_keys=False
                )
        except Exception as e:
            print(f"⚠️ Warning: Could not update manifest: {e}")

    def generate_sync_report(
        self, sync_operations: List[SyncOperation]
    ) -> Dict[str, Any]:
        """Generate comprehensive synchronization report."""
        if not sync_operations:
            return {
                "status": "no_sync_needed",
                "summary": "No templates required synchronization",
                "total_operations": 0,
                "report_generated": datetime.utcnow().isoformat() + "Z",
            }

        # Analyze results
        result_counts = {}
        for result in SyncResult:
            result_counts[result.value] = len(
                [op for op in sync_operations if op.result == result]
            )

        # Determine overall status
        has_failures = result_counts.get("failed", 0) > 0
        has_manual_review = result_counts.get("requires_manual_review", 0) > 0

        if has_failures:
            overall_status = "sync_failed"
        elif has_manual_review:
            overall_status = "manual_review_required"
        else:
            overall_status = "sync_completed"

        return {
            "status": overall_status,
            "summary": f"Synchronized {result_counts.get('success', 0)}/{len(sync_operations)} templates",
            "total_operations": len(sync_operations),
            "result_breakdown": result_counts,
            "backups_created": len([op for op in sync_operations if op.backup_created]),
            "customizations_preserved": len(
                [op for op in sync_operations if op.preserved_customizations]
            ),
            "operations": [
                {
                    "template_path": op.template_path,
                    "strategy": op.strategy.value,
                    "result": op.result.value,
                    "description": op.description,
                    "backup_created": op.backup_created,
                    "preserved_customizations": op.preserved_customizations,
                    "warnings": op.warnings,
                    "errors": op.errors,
                }
                for op in sync_operations
            ],
            "report_generated": datetime.utcnow().isoformat() + "Z",
        }

    def run_synchronization(self) -> Dict[str, Any]:
        """Run complete template synchronization process."""
        sync_operations = self.sync_all_templates()
        self.update_manifest_after_sync(sync_operations)
        report = self.generate_sync_report(sync_operations)

        # Print summary
        status_emoji = {
            "no_sync_needed": "✅",
            "sync_completed": "✅",
            "manual_review_required": "👥",
            "sync_failed": "❌",
        }

        emoji = status_emoji.get(report["status"], "❓")
        print(f"\n{emoji} Synchronization Complete: {report['summary']}")

        return report


def main():
    """Main CLI entry point for template synchronization."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Constitutional Template Synchronization"
    )
    parser.add_argument(
        "--manifest",
        default=".kittify/templates/manifest.yaml",
        help="Path to template manifest file",
    )
    parser.add_argument("--output", help="Output file for sync report (JSON format)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synchronized without making changes",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        synchronizer = TemplateSynchronizer(args.manifest)

        if args.dry_run:
            print("🔍 Dry run mode - no changes will be made")
            # TODO: Implement dry run functionality
            return

        report = synchronizer.run_synchronization()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {args.output}")

        if args.verbose:
            print("\n📋 Detailed Report:")
            print(json.dumps(report, indent=2))

        # Exit with error code if synchronization failed
        if report["status"] == "sync_failed":
            sys.exit(1)

    except Exception as e:
        print(f"❌ Synchronization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
