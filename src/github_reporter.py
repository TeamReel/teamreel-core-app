#!/usr/bin/env python3
"""
GitHub Reporter - Constitutional Compliance Reporting for GitHub Integration

This module provides GitHub-specific reporting capabilities for constitutional
compliance validation, including status checks, PR comments, and compliance
dashboard integration.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import sys
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from compliance_reporter import ComplianceReport, Violation


@dataclass
class GitHubStatusCheck:
    """Represents a GitHub status check."""

    context: str
    state: str  # success, failure, error, pending
    description: str
    target_url: Optional[str] = None


@dataclass
class GitHubPRComment:
    """Represents a GitHub PR comment."""

    title: str
    body: str
    update_existing: bool = True


@dataclass
class GitHubComplianceReport:
    """Complete GitHub compliance report."""

    pr_number: Optional[int]
    commit_sha: str
    compliance_score: float
    violations_count: int
    files_checked: int
    status_checks: List[GitHubStatusCheck] = field(default_factory=list)
    pr_comment: Optional[GitHubPRComment] = None
    workflow_summary: str = ""
    artifacts: List[str] = field(default_factory=list)


class GitHubReporter:
    """Generates GitHub-optimized compliance reports and status updates."""

    def __init__(self, repo_name: str = "", base_url: str = ""):
        """Initialize GitHub reporter."""
        self.repo_name = repo_name or os.getenv(
            "GITHUB_REPOSITORY", "TeamReel/teamreel-core-app"
        )
        self.base_url = base_url or f"https://github.com/{self.repo_name}"
        self.workflow_run_id = os.getenv("GITHUB_RUN_ID", "")
        self.workflow_run_url = (
            f"{self.base_url}/actions/runs/{self.workflow_run_id}"
            if self.workflow_run_id
            else ""
        )

        # GitHub environment info
        self.pr_number = self._get_pr_number()
        self.commit_sha = os.getenv("GITHUB_SHA", "")
        self.actor = os.getenv("GITHUB_ACTOR", "github-actions")
        self.event_name = os.getenv("GITHUB_EVENT_NAME", "unknown")

    def _get_pr_number(self) -> Optional[int]:
        """Extract PR number from GitHub environment."""
        # Try to get from event path first
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path) as f:
                    event_data = json.load(f)
                    if "pull_request" in event_data:
                        return event_data["pull_request"]["number"]
            except Exception:
                pass

        # Fallback to ref parsing
        github_ref = os.getenv("GITHUB_REF", "")
        if github_ref.startswith("refs/pull/"):
            try:
                return int(github_ref.split("/")[2])
            except (IndexError, ValueError):
                pass

        return None

    def generate_compliance_report(
        self, compliance_reports: List[ComplianceReport]
    ) -> GitHubComplianceReport:
        """Generate comprehensive GitHub compliance report from validation results."""
        # Aggregate results
        total_violations = sum(len(result.violations) for result in validation_results)
        total_files = len(validation_results)
        avg_score = (
            sum(result.compliance_score for result in validation_results) / total_files
            if total_files > 0
            else 100.0
        )

        # Overall compliance state
        overall_state = "success" if total_violations == 0 else "failure"

        report = GitHubComplianceReport(
            pr_number=self.pr_number,
            commit_sha=self.commit_sha,
            compliance_score=round(avg_score, 1),
            violations_count=total_violations,
            files_checked=total_files,
        )

        # Generate status checks
        report.status_checks = self._generate_status_checks(
            validation_results, overall_state
        )

        # Generate PR comment if in PR context
        if self.pr_number:
            report.pr_comment = self._generate_pr_comment(validation_results, report)

        # Generate workflow summary
        report.workflow_summary = self._generate_workflow_summary(
            validation_results, report
        )

        return report

    def _generate_status_checks(
        self, validation_results: List[ValidationResult], overall_state: str
    ) -> List[GitHubStatusCheck]:
        """Generate GitHub status checks for constitutional compliance."""
        status_checks = []

        # Main constitutional compliance check
        total_violations = sum(len(result.violations) for result in validation_results)
        description = (
            f"Constitutional compliance passed"
            if overall_state == "success"
            else f"{total_violations} violations found"
        )

        status_checks.append(
            GitHubStatusCheck(
                context="Constitutional Compliance",
                state=overall_state,
                description=description,
                target_url=self.workflow_run_url,
            )
        )

        # Individual SE principle checks
        principle_violations = {}
        for result in validation_results:
            for violation in result.violations:
                principle = violation.principle.value
                if principle not in principle_violations:
                    principle_violations[principle] = 0
                principle_violations[principle] += 1

        # Create status checks for each SE principle
        se_principles = [
            "single_responsibility",
            "open_closed",
            "liskov_substitution",
            "interface_segregation",
            "dependency_inversion",
            "dry",
            "yagni",
            "kiss",
        ]

        for principle in se_principles:
            violation_count = principle_violations.get(principle, 0)
            principle_name = principle.replace("_", " ").title()

            if violation_count == 0:
                state = "success"
                description = f"{principle_name} compliance passed"
            else:
                state = "failure"
                description = f"{violation_count} {principle_name} violations"

            status_checks.append(
                GitHubStatusCheck(
                    context=f"SE Principle: {principle_name}",
                    state=state,
                    description=description,
                    target_url=self.workflow_run_url,
                )
            )

        return status_checks

    def _generate_pr_comment(
        self, validation_results: List[ValidationResult], report: GitHubComplianceReport
    ) -> GitHubPRComment:
        """Generate detailed PR comment for compliance results."""
        title = "🏛️ Constitutional Compliance Report"

        # Header
        body_lines = [
            f"## {title}",
            "",
            f"**PR**: #{report.pr_number}",
            f"**Commit**: `{report.commit_sha[:8]}`",
            f"**Files Analyzed**: {report.files_checked}",
            f"**Compliance Score**: {report.compliance_score}/100",
            f"**Violations Found**: {report.violations_count}",
            "",
        ]

        if report.violations_count == 0:
            # Success case
            body_lines.extend(
                [
                    "### ✅ Constitutional Compliance: PASSED",
                    "",
                    "🎉 **Congratulations!** This PR meets all TeamReel constitutional requirements.",
                    "",
                    "**SE Principles Validated:**",
                    "- ✅ Single Responsibility Principle",
                    "- ✅ Open/Closed Principle",
                    "- ✅ Liskov Substitution Principle",
                    "- ✅ Interface Segregation Principle",
                    "- ✅ Dependency Inversion Principle",
                    "- ✅ DRY (Don't Repeat Yourself)",
                    "- ✅ YAGNI (You Aren't Gonna Need It)",
                    "- ✅ KISS (Keep It Simple, Stupid)",
                    "",
                    "This PR is **approved for merge** from a constitutional compliance perspective.",
                    "",
                ]
            )
        else:
            # Failure case
            body_lines.extend(
                [
                    "### ❌ Constitutional Compliance: FAILED",
                    "",
                    "🚫 **This PR has constitutional violations that must be fixed before merge.**",
                    "",
                    "**Action Required**: Please review the violations below and update your code to meet TeamReel's constitutional requirements.",
                    "",
                ]
            )

            # Group violations by principle
            violations_by_principle = {}
            for result in validation_results:
                for violation in result.violations:
                    principle = violation.principle.value.replace("_", " ").title()
                    if principle not in violations_by_principle:
                        violations_by_principle[principle] = []
                    violations_by_principle[principle].append(
                        {
                            "file": result.file_path,
                            "line": violation.line_number,
                            "message": violation.message,
                            "suggestion": violation.suggestion,
                        }
                    )

            # Add violations summary
            body_lines.append("### 📋 Violations by SE Principle")
            body_lines.append("")

            for principle, violations in violations_by_principle.items():
                body_lines.append(f"#### {principle} ({len(violations)} violations)")
                body_lines.append("")

                for violation in violations[:5]:  # Show first 5 per principle
                    body_lines.append(f"- **{violation['file']}:{violation['line']}**")
                    body_lines.append(f"  - {violation['message']}")
                    if violation["suggestion"]:
                        body_lines.append(f"  - 💡 *{violation['suggestion']}*")
                    body_lines.append("")

                if len(violations) > 5:
                    body_lines.append(
                        f"*... and {len(violations) - 5} more {principle} violations*"
                    )
                    body_lines.append("")

            # Add remediation guidance
            body_lines.extend(
                [
                    "### 🔧 How to Fix",
                    "",
                    "1. **Review violations**: Each violation above includes specific guidance",
                    "2. **Apply fixes**: Update your code following the suggested improvements",
                    "3. **Test locally**: Run `python src/constitutional_validator.py` to validate changes",
                    "4. **Push updates**: Commit and push to trigger re-validation",
                    "",
                    "### 📚 Resources",
                    "",
                    "- [Constitutional Foundation Guide](docs/constitutional-foundation.md)",
                    "- [SE Principles Documentation](docs/se-principles.md)",
                    "- [Quality Gates Reference](docs/quality-gates.md)",
                    "",
                ]
            )

        # Footer
        body_lines.extend(
            [
                "---",
                "*This report was generated automatically by TeamReel's Constitutional Enforcement system*",
                f"*Workflow: [`constitutional-compliance.yml`](.github/workflows/constitutional-compliance.yml)*",
                (
                    f"*Run Details: [View Workflow]({self.workflow_run_url})*"
                    if self.workflow_run_url
                    else ""
                ),
            ]
        )

        return GitHubPRComment(
            title=title, body="\n".join(body_lines), update_existing=True
        )

    def _generate_workflow_summary(
        self, validation_results: List[ValidationResult], report: GitHubComplianceReport
    ) -> str:
        """Generate GitHub workflow step summary."""
        summary_lines = [
            "# 🏛️ Constitutional Compliance Summary",
            "",
            f"**Repository**: {self.repo_name}",
            f"**Event**: {self.event_name}",
            f"**Commit**: `{report.commit_sha[:8] if report.commit_sha else 'unknown'}`",
            "",
        ]

        if report.pr_number:
            summary_lines.extend([f"**PR**: #{report.pr_number}", ""])

        # Results summary
        summary_lines.extend(
            [
                "## 📊 Validation Results",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Files Checked | {report.files_checked} |",
                f"| Compliance Score | {report.compliance_score}/100 |",
                f"| Violations Found | {report.violations_count} |",
                f"| Overall Status | {'✅ PASSED' if report.violations_count == 0 else '❌ FAILED'} |",
                "",
            ]
        )

        if report.violations_count > 0:
            # Violations breakdown
            principle_counts = {}
            for result in validation_results:
                for violation in result.violations:
                    principle = violation.principle.value.replace("_", " ").title()
                    principle_counts[principle] = principle_counts.get(principle, 0) + 1

            summary_lines.extend(
                [
                    "## 📋 Violations by SE Principle",
                    "",
                    "| Principle | Violations |",
                    "|-----------|------------|",
                ]
            )

            for principle, count in sorted(principle_counts.items()):
                summary_lines.append(f"| {principle} | {count} |")

            summary_lines.append("")

        # Status checks summary
        if report.status_checks:
            summary_lines.extend(["## ✅ Status Checks", ""])

            for check in report.status_checks:
                status_icon = "✅" if check.state == "success" else "❌"
                summary_lines.append(
                    f"- {status_icon} **{check.context}**: {check.description}"
                )

            summary_lines.append("")

        # Next steps
        if report.violations_count == 0:
            summary_lines.extend(
                [
                    "## 🎉 Next Steps",
                    "",
                    "✅ Constitutional compliance validation passed!",
                    "",
                    "Your code meets all TeamReel constitutional requirements. The PR is ready for:",
                    "1. Code review by team members",
                    "2. Additional testing if required",
                    "3. Merge when approved",
                    "",
                ]
            )
        else:
            summary_lines.extend(
                [
                    "## 🔧 Action Required",
                    "",
                    "❌ Constitutional violations must be resolved before merge.",
                    "",
                    "Please:",
                    "1. Review the violations listed above",
                    "2. Apply the suggested fixes to your code",
                    "3. Push updated code to trigger re-validation",
                    "4. Ensure all violations are resolved",
                    "",
                ]
            )

        return "\n".join(summary_lines)

    def export_status_checks(
        self,
        report: GitHubComplianceReport,
        output_file: str = "github_status_checks.json",
    ):
        """Export status checks in GitHub Actions format."""
        status_data = []

        for check in report.status_checks:
            status_data.append(
                {
                    "context": check.context,
                    "state": check.state,
                    "description": check.description,
                    "target_url": check.target_url,
                }
            )

        with open(output_file, "w") as f:
            json.dump(status_data, f, indent=2)

        return output_file

    def export_pr_comment(
        self, report: GitHubComplianceReport, output_file: str = "pr_comment.md"
    ):
        """Export PR comment to markdown file."""
        if report.pr_comment:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report.pr_comment.body)
            return output_file
        return None

    def export_workflow_summary(
        self, report: GitHubComplianceReport, output_file: str = "workflow_summary.md"
    ):
        """Export workflow summary to markdown file."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.workflow_summary)
        return output_file

    def set_github_outputs(self, report: GitHubComplianceReport):
        """Set GitHub Actions outputs for use in subsequent steps."""
        github_output = os.getenv("GITHUB_OUTPUT")
        if not github_output:
            return

        outputs = {
            "compliance-score": str(report.compliance_score),
            "violations-count": str(report.violations_count),
            "files-checked": str(report.files_checked),
            "overall-status": "success" if report.violations_count == 0 else "failure",
            "pr-number": str(report.pr_number) if report.pr_number else "",
            "commit-sha": report.commit_sha,
        }

        with open(github_output, "a") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")

    def create_step_summary(self, report: GitHubComplianceReport):
        """Add content to GitHub Actions step summary."""
        github_step_summary = os.getenv("GITHUB_STEP_SUMMARY")
        if not github_step_summary:
            return

        with open(github_step_summary, "a", encoding="utf-8") as f:
            f.write(report.workflow_summary)
            f.write("\n")


def main():
    """CLI entry point for GitHub reporting."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate GitHub compliance reports")
    parser.add_argument(
        "--validation-report",
        required=True,
        help="Path to validation results JSON file",
    )
    parser.add_argument(
        "--output-dir", default=".", help="Output directory for reports"
    )
    parser.add_argument(
        "--export-all", action="store_true", help="Export all report formats"
    )
    parser.add_argument(
        "--set-outputs", action="store_true", help="Set GitHub Actions outputs"
    )
    parser.add_argument(
        "--create-summary",
        action="store_true",
        help="Create GitHub Actions step summary",
    )

    args = parser.parse_args()

    # Load validation results
    try:
        with open(args.validation_report) as f:
            validation_data = json.load(f)

        # Convert to ValidationResult objects (simplified for CLI usage)
        validation_results = []
        for file_path, file_data in validation_data.items():
            # Mock ValidationResult for demonstration
            from constitutional_validator import (
                ValidationResult,
                ConstitutionalViolation,
                SEPrinciple,
            )

            violations = []
            for violation_data in file_data.get("violations", []):
                violation = ConstitutionalViolation(
                    principle=SEPrinciple(violation_data.get("principle", "unknown")),
                    level=ValidationLevel(violation_data.get("level", "ERROR")),
                    message=violation_data.get("message", ""),
                    line_number=violation_data.get("line", 0),
                    suggestion=violation_data.get("suggestion", ""),
                )
                violations.append(violation)

            result = ValidationResult(
                file_path=file_path,
                is_valid=len(violations) == 0,
                violations=violations,
                compliance_score=file_data.get("compliance_score", 100.0),
            )
            validation_results.append(result)

    except Exception as e:
        print(f"Error loading validation results: {e}")
        sys.exit(1)

    # Generate report
    reporter = GitHubReporter()
    report = reporter.generate_compliance_report(validation_results)

    # Export reports
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if args.export_all or args.set_outputs:
        status_file = reporter.export_status_checks(
            report, output_dir / "github_status_checks.json"
        )
        print(f"Status checks exported to: {status_file}")

    if args.export_all:
        comment_file = reporter.export_pr_comment(report, output_dir / "pr_comment.md")
        if comment_file:
            print(f"PR comment exported to: {comment_file}")

        summary_file = reporter.export_workflow_summary(
            report, output_dir / "workflow_summary.md"
        )
        print(f"Workflow summary exported to: {summary_file}")

    # Set GitHub Actions outputs
    if args.set_outputs:
        reporter.set_github_outputs(report)
        print("GitHub Actions outputs set")

    # Create step summary
    if args.create_summary:
        reporter.create_step_summary(report)
        print("GitHub Actions step summary created")

    # Print summary
    print(f"\nCompliance Summary:")
    print(f"Files checked: {report.files_checked}")
    print(f"Compliance score: {report.compliance_score}/100")
    print(f"Violations: {report.violations_count}")
    print(f"Status: {'PASSED' if report.violations_count == 0 else 'FAILED'}")


if __name__ == "__main__":
    main()
