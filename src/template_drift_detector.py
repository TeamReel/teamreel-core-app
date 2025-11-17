#!/usr/bin/env python3
"""
Constitutional Drift Detection System

Detects when templates fall out of sync with constitutional requirements.
Monitors template changes, constitutional updates, and SE principle evolution.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import hashlib
import os
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class DriftSeverity(Enum):
    """Severity levels for template drift."""

    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class DriftType(Enum):
    """Types of template drift."""

    CONSTITUTIONAL_UPDATE = "constitutional_update"
    TEMPLATE_MODIFICATION = "template_modification"
    SE_PRINCIPLES_CHANGE = "se_principles_change"
    QUALITY_GATE_CHANGE = "quality_gate_change"
    CHECKSUM_MISMATCH = "checksum_mismatch"


@dataclass
class DriftDetection:
    """Individual drift detection result."""

    template_path: str
    drift_type: DriftType
    severity: DriftSeverity
    description: str
    current_version: str
    expected_version: str
    detected_at: str
    auto_fixable: bool
    recommended_action: str
    affected_requirements: List[str] = field(default_factory=list)


@dataclass
class ConstitutionalBaseline:
    """Constitutional baseline for drift comparison."""

    principles_version: str
    rules_checksum: str
    last_validation: str
    compliance_level: str
    constitutional_version: str


class TemplateDriftDetector:
    """Main drift detection engine for constitutional template synchronization."""

    def __init__(self, manifest_path: str = ".kittify/templates/manifest.yaml"):
        """Initialize drift detector with manifest path."""
        self.manifest_path = Path(manifest_path)
        self.manifest_data = None
        self.constitutional_baseline = None
        self.load_manifest()

    def load_manifest(self) -> None:
        """Load template manifest and constitutional baseline."""
        try:
            if not self.manifest_path.exists():
                raise FileNotFoundError(
                    f"Template manifest not found: {self.manifest_path}"
                )

            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.manifest_data = yaml.safe_load(f)

            # Extract constitutional baseline
            baseline_data = self.manifest_data.get("constitutional_baseline", {})
            self.constitutional_baseline = ConstitutionalBaseline(
                principles_version=baseline_data.get("principles_version", "unknown"),
                rules_checksum=baseline_data.get("rules_checksum", ""),
                last_validation=baseline_data.get("last_validation", ""),
                compliance_level=baseline_data.get("compliance_level", "strict"),
                constitutional_version=self.manifest_data.get("metadata", {}).get(
                    "constitutional_version", "unknown"
                ),
            )

        except Exception as e:
            print(f"❌ Error loading manifest: {e}")
            sys.exit(1)

    def calculate_file_checksum(self, file_path: str) -> str:
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

    def detect_template_drift(
        self, template_path: str, template_config: Dict[str, Any]
    ) -> List[DriftDetection]:
        """Detect drift for a specific template."""
        drift_detections = []

        # Check if template file exists
        if not Path(template_path).exists():
            drift_detections.append(
                DriftDetection(
                    template_path=template_path,
                    drift_type=DriftType.TEMPLATE_MODIFICATION,
                    severity=DriftSeverity.CRITICAL,
                    description=f"Template file missing: {template_path}",
                    current_version="missing",
                    expected_version=template_config.get(
                        "constitutional_version", "unknown"
                    ),
                    detected_at=datetime.utcnow().isoformat() + "Z",
                    auto_fixable=False,
                    recommended_action="Restore template from backup or regenerate from constitutional baseline",
                    affected_requirements=template_config.get(
                        "constitutional_requirements", []
                    ),
                )
            )
            return drift_detections

        # Check checksum drift
        current_checksum = self.calculate_file_checksum(template_path)
        expected_checksum = template_config.get("checksum", "")

        if (
            current_checksum != expected_checksum
            and expected_checksum != "sha256:placeholder"
        ):
            severity = (
                DriftSeverity.MINOR
                if template_config.get("customizations_preserved")
                else DriftSeverity.MAJOR
            )
            drift_detections.append(
                DriftDetection(
                    template_path=template_path,
                    drift_type=DriftType.CHECKSUM_MISMATCH,
                    severity=severity,
                    description=f"Template content has changed since last sync",
                    current_version=current_checksum,
                    expected_version=expected_checksum,
                    detected_at=datetime.utcnow().isoformat() + "Z",
                    auto_fixable=severity == DriftSeverity.MINOR,
                    recommended_action="Review changes and update manifest or sync template",
                    affected_requirements=template_config.get(
                        "constitutional_requirements", []
                    ),
                )
            )

        # Check constitutional version drift
        current_constitutional = self.constitutional_baseline.constitutional_version
        template_constitutional = template_config.get(
            "constitutional_version", "unknown"
        )

        if current_constitutional != template_constitutional:
            drift_detections.append(
                DriftDetection(
                    template_path=template_path,
                    drift_type=DriftType.CONSTITUTIONAL_UPDATE,
                    severity=DriftSeverity.MAJOR,
                    description=f"Template is based on outdated constitutional version",
                    current_version=template_constitutional,
                    expected_version=current_constitutional,
                    detected_at=datetime.utcnow().isoformat() + "Z",
                    auto_fixable=True,
                    recommended_action="Synchronize template with current constitutional requirements",
                    affected_requirements=template_config.get(
                        "constitutional_requirements", []
                    ),
                )
            )

        # Check drift status from manifest
        drift_status = template_config.get("drift_status", "unknown")
        if drift_status in ["needs_sync", "pending_sync"]:
            severity = (
                DriftSeverity.MAJOR
                if drift_status == "needs_sync"
                else DriftSeverity.MINOR
            )
            drift_detections.append(
                DriftDetection(
                    template_path=template_path,
                    drift_type=DriftType.TEMPLATE_MODIFICATION,
                    severity=severity,
                    description=f"Template marked as {drift_status} in manifest",
                    current_version=drift_status,
                    expected_version="in_sync",
                    detected_at=datetime.utcnow().isoformat() + "Z",
                    auto_fixable=True,
                    recommended_action="Run template synchronization to resolve drift",
                    affected_requirements=template_config.get(
                        "constitutional_requirements", []
                    ),
                )
            )

        return drift_detections

    def detect_all_drift(self) -> List[DriftDetection]:
        """Detect drift across all tracked templates."""
        all_drift = []

        # Check all template categories
        for category_name, category_templates in self.manifest_data.get(
            "templates", {}
        ).items():
            for template_name, template_config in category_templates.items():
                template_path = template_config.get("path", "")
                if template_path:
                    template_drift = self.detect_template_drift(
                        template_path, template_config
                    )
                    all_drift.extend(template_drift)

        return all_drift

    def generate_drift_report(
        self, drift_detections: List[DriftDetection]
    ) -> Dict[str, Any]:
        """Generate comprehensive drift report."""
        if not drift_detections:
            return {
                "status": "no_drift",
                "summary": "All templates are in sync with constitutional requirements",
                "total_templates": self._count_total_templates(),
                "drift_count": 0,
                "severity_breakdown": {"none": self._count_total_templates()},
                "report_generated": datetime.utcnow().isoformat() + "Z",
            }

        # Analyze drift by severity
        severity_counts = {}
        for severity in DriftSeverity:
            severity_counts[severity.value] = len(
                [d for d in drift_detections if d.severity == severity]
            )

        # Analyze drift by type
        type_counts = {}
        for drift_type in DriftType:
            type_counts[drift_type.value] = len(
                [d for d in drift_detections if d.drift_type == drift_type]
            )

        # Determine overall status
        has_critical = any(
            d.severity == DriftSeverity.CRITICAL for d in drift_detections
        )
        has_major = any(d.severity == DriftSeverity.MAJOR for d in drift_detections)

        if has_critical:
            overall_status = "critical_drift"
        elif has_major:
            overall_status = "major_drift"
        else:
            overall_status = "minor_drift"

        return {
            "status": overall_status,
            "summary": f"Detected {len(drift_detections)} template drift issues",
            "total_templates": self._count_total_templates(),
            "drift_count": len(drift_detections),
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "auto_fixable_count": len([d for d in drift_detections if d.auto_fixable]),
            "manual_review_count": len(
                [d for d in drift_detections if not d.auto_fixable]
            ),
            "detections": [
                {
                    "template_path": d.template_path,
                    "drift_type": d.drift_type.value,
                    "severity": d.severity.value,
                    "description": d.description,
                    "auto_fixable": d.auto_fixable,
                    "recommended_action": d.recommended_action,
                    "affected_requirements": d.affected_requirements,
                }
                for d in drift_detections
            ],
            "report_generated": datetime.utcnow().isoformat() + "Z",
        }

    def _count_total_templates(self) -> int:
        """Count total number of tracked templates."""
        total = 0
        for category_templates in self.manifest_data.get("templates", {}).values():
            total += len(category_templates)
        return total

    def run_drift_detection(self) -> Dict[str, Any]:
        """Run complete drift detection and return report."""
        print("🔍 Starting constitutional template drift detection...")

        drift_detections = self.detect_all_drift()
        report = self.generate_drift_report(drift_detections)

        # Print summary
        status_emoji = {
            "no_drift": "✅",
            "minor_drift": "⚠️",
            "major_drift": "❌",
            "critical_drift": "🚨",
        }

        emoji = status_emoji.get(report["status"], "❓")
        print(f"{emoji} Drift Detection Complete: {report['summary']}")

        if drift_detections:
            print(
                f"📊 Breakdown: {report['auto_fixable_count']} auto-fixable, {report['manual_review_count']} need manual review"
            )

        return report


def main():
    """Main CLI entry point for drift detection."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Constitutional Template Drift Detection"
    )
    parser.add_argument(
        "--manifest",
        default=".kittify/templates/manifest.yaml",
        help="Path to template manifest file",
    )
    parser.add_argument("--output", help="Output file for drift report (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        detector = TemplateDriftDetector(args.manifest)
        report = detector.run_drift_detection()

        if args.output:
            import json

            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {args.output}")

        if args.verbose:
            import json

            print("\n📋 Detailed Report:")
            print(json.dumps(report, indent=2))

        # Exit with error code if critical or major drift detected
        if report["status"] in ["critical_drift", "major_drift"]:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Drift detection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
