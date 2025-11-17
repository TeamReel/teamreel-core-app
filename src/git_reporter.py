"""
project Git-Optimized Constitutional Violation Reporter

Provides Git-specific reporting format for constitutional violations,
optimized for terminal output and Git workflow integration.

SE Principle Focus:
- Simplicity: Clear, concise violation messages for developers
- Maintainability: Structured output format for both humans and tools
- Defensibility: Secure handling of file paths and Git data
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import subprocess
import json


class GitReportFormat(Enum):
    """Git report output format options"""

    TERMINAL = "terminal"  # Colorized terminal output
    PLAIN = "plain"  # Plain text for CI/CD
    JSON = "json"  # JSON for tool integration
    GITHUB_ACTIONS = "github"  # GitHub Actions format


@dataclass
class GitFileContext:
    """Git-specific file context information"""

    file_path: str
    relative_path: str
    is_staged: bool
    is_modified: bool
    git_status: str
    line_count: int
    file_size: int


class GitViolationReporter:
    """Git-optimized constitutional violation reporter"""

    def __init__(self, format_type: GitReportFormat = GitReportFormat.TERMINAL):
        self.format_type = format_type
        self.repo_root = self._get_repo_root()
        self.supports_color = self._supports_color()

        # Git-specific color codes (ANSI)
        self.colors = {
            "red": "\033[31m" if self.supports_color else "",
            "green": "\033[32m" if self.supports_color else "",
            "yellow": "\033[33m" if self.supports_color else "",
            "blue": "\033[34m" if self.supports_color else "",
            "purple": "\033[35m" if self.supports_color else "",
            "cyan": "\033[36m" if self.supports_color else "",
            "white": "\033[37m" if self.supports_color else "",
            "bold": "\033[1m" if self.supports_color else "",
            "reset": "\033[0m" if self.supports_color else "",
        }

    def _get_repo_root(self) -> str:
        """Get the Git repository root directory"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return os.getcwd()

    def _supports_color(self) -> bool:
        """Check if terminal supports color output"""
        if self.format_type in [
            GitReportFormat.PLAIN,
            GitReportFormat.JSON,
            GitReportFormat.GITHUB_ACTIONS,
        ]:
            return False

        # Check environment variables
        if os.getenv("NO_COLOR") or os.getenv("TERM") == "dumb":
            return False

        # Check if stdout is a TTY
        return sys.stdout.isatty()

    def _get_file_context(self, file_path: str) -> GitFileContext:
        """Get Git-specific context for a file"""
        try:
            # Get relative path from repo root
            abs_path = os.path.abspath(file_path)
            rel_path = os.path.relpath(abs_path, self.repo_root)

            # Get Git status
            result = subprocess.run(
                ["git", "status", "--porcelain", rel_path],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            git_status = result.stdout.strip()
            is_staged = git_status.startswith(("A", "M", "D", "R", "C"))
            is_modified = len(git_status) > 1 and git_status[1] in "AMDRC"

            # Get file info
            file_size = 0
            line_count = 0
            if os.path.exists(abs_path):
                file_size = os.path.getsize(abs_path)
                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                except (UnicodeDecodeError, IOError):
                    line_count = 0

            return GitFileContext(
                file_path=abs_path,
                relative_path=rel_path,
                is_staged=is_staged,
                is_modified=is_modified,
                git_status=git_status,
                line_count=line_count,
                file_size=file_size,
            )
        except Exception:
            # Fallback for non-Git files
            return GitFileContext(
                file_path=file_path,
                relative_path=os.path.basename(file_path),
                is_staged=False,
                is_modified=False,
                git_status="",
                line_count=0,
                file_size=0,
            )

    def format_terminal_report(
        self, violations: List[Any], context: str = "pre-commit"
    ) -> str:
        """Format violations for terminal output with Git-specific styling"""
        if not violations:
            return self._format_success_message(context)

        output = []

        # Header
        output.append(
            f"{self.colors['red']}{self.colors['bold']}❌ Constitutional Violations Detected{self.colors['reset']}"
        )
        output.append(f"{self.colors['purple']}{'=' * 50}{self.colors['reset']}")
        output.append("")

        # Group violations by file
        violations_by_file = {}
        for violation in violations:
            file_path = getattr(violation, "file_path", "unknown")
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)

        # Report each file
        for file_path, file_violations in violations_by_file.items():
            file_context = self._get_file_context(file_path)

            # File header
            output.append(
                f"{self.colors['blue']}{self.colors['bold']}📁 {file_context.relative_path}{self.colors['reset']}"
            )

            # File status indicators
            status_indicators = []
            if file_context.is_staged:
                status_indicators.append(
                    f"{self.colors['green']}staged{self.colors['reset']}"
                )
            if file_context.is_modified:
                status_indicators.append(
                    f"{self.colors['yellow']}modified{self.colors['reset']}"
                )

            if status_indicators:
                output.append(
                    f"   {self.colors['cyan']}Status: {' | '.join(status_indicators)}{self.colors['reset']}"
                )

            output.append("")

            # Violations for this file
            for i, violation in enumerate(file_violations, 1):
                severity_color = {
                    "HIGH": self.colors["red"],
                    "MEDIUM": self.colors["yellow"],
                    "LOW": self.colors["cyan"],
                }.get(getattr(violation, "severity", "MEDIUM"), self.colors["yellow"])

                # Violation header
                rule_id = getattr(violation, "rule_id", "UNKNOWN")
                severity = getattr(violation, "severity", "MEDIUM")
                line_no = getattr(violation, "line_number", 0)
                se_principle = getattr(violation, "se_principle", "Unknown")

                output.append(
                    f"   {severity_color}🚨 Violation #{i}: {rule_id} ({severity}){self.colors['reset']}"
                )
                output.append(
                    f"      {self.colors['white']}Line {line_no} - {se_principle}{self.colors['reset']}"
                )

                # Description
                description = getattr(
                    violation, "description", "No description available"
                )
                output.append(
                    f"      {self.colors['red']}Issue: {description}{self.colors['reset']}"
                )

                # Suggested fix
                suggested_fix = getattr(
                    violation, "suggested_fix", "No suggestion available"
                )
                output.append(
                    f"      {self.colors['green']}Fix: {suggested_fix}{self.colors['reset']}"
                )

                # Code snippet (if available)
                code_snippet = getattr(violation, "code_snippet", "").strip()
                if code_snippet:
                    output.append(
                        f"      {self.colors['cyan']}Code:{self.colors['reset']}"
                    )
                    for line in code_snippet.split("\n"):
                        output.append(
                            f"        {self.colors['white']}{line}{self.colors['reset']}"
                        )

                output.append("")

            output.append("")

        # Summary
        total_violations = len(violations)
        high_violations = sum(
            1 for v in violations if getattr(v, "severity", "") == "HIGH"
        )
        medium_violations = sum(
            1 for v in violations if getattr(v, "severity", "") == "MEDIUM"
        )
        low_violations = sum(
            1 for v in violations if getattr(v, "severity", "") == "LOW"
        )

        output.append(
            f"{self.colors['purple']}{self.colors['bold']}📊 Violation Summary{self.colors['reset']}"
        )
        output.append(f"   Total: {total_violations}")
        if high_violations:
            output.append(
                f"   {self.colors['red']}High: {high_violations}{self.colors['reset']}"
            )
        if medium_violations:
            output.append(
                f"   {self.colors['yellow']}Medium: {medium_violations}{self.colors['reset']}"
            )
        if low_violations:
            output.append(
                f"   {self.colors['cyan']}Low: {low_violations}{self.colors['reset']}"
            )

        output.append("")

        # Next steps
        output.append(
            f"{self.colors['yellow']}{self.colors['bold']}🔧 Next Steps{self.colors['reset']}"
        )
        output.append(f"   1. Fix the violations listed above")
        output.append(f"   2. Review project's constitutional requirements")
        output.append(f"   3. Re-stage your files and try again")
        output.append("")

        # Documentation links
        output.append(
            f"{self.colors['blue']}{self.colors['bold']}📖 Documentation{self.colors['reset']}"
        )
        output.append(f"   • SE Rules: .kittify/config/se_rules.yaml")
        output.append(f"   • Constitution: .kittify/memory/constitution.md")
        output.append(f"   • Quality Gates: .kittify/config/quality_gates.yaml")

        return "\n".join(output)

    def format_plain_report(self, violations: List[Any]) -> str:
        """Format violations for plain text output (CI/CD friendly)"""
        if not violations:
            return "✅ No constitutional violations found"

        output = []
        output.append("CONSTITUTIONAL VIOLATIONS DETECTED")
        output.append("=" * 40)
        output.append("")

        for i, violation in enumerate(violations, 1):
            file_path = getattr(violation, "file_path", "unknown")
            rel_path = (
                os.path.relpath(file_path, self.repo_root)
                if self.repo_root
                else file_path
            )

            output.append(f"Violation #{i}:")
            output.append(f"  File: {rel_path}")
            output.append(f"  Line: {getattr(violation, 'line_number', 0)}")
            output.append(f"  Rule: {getattr(violation, 'rule_id', 'UNKNOWN')}")
            output.append(f"  Severity: {getattr(violation, 'severity', 'MEDIUM')}")
            output.append(
                f"  Principle: {getattr(violation, 'se_principle', 'Unknown')}"
            )
            output.append(
                f"  Issue: {getattr(violation, 'description', 'No description')}"
            )
            output.append(
                f"  Fix: {getattr(violation, 'suggested_fix', 'No suggestion')}"
            )
            output.append("")

        output.append(f"Total violations: {len(violations)}")
        return "\n".join(output)

    def format_json_report(self, violations: List[Any]) -> str:
        """Format violations as JSON for tool integration"""
        violations_data = []

        for violation in violations:
            file_context = self._get_file_context(getattr(violation, "file_path", ""))

            violation_data = {
                "rule_id": getattr(violation, "rule_id", "UNKNOWN"),
                "severity": getattr(violation, "severity", "MEDIUM"),
                "se_principle": getattr(violation, "se_principle", "Unknown"),
                "description": getattr(violation, "description", ""),
                "suggested_fix": getattr(violation, "suggested_fix", ""),
                "file": {
                    "path": file_context.relative_path,
                    "absolute_path": file_context.file_path,
                    "line_number": getattr(violation, "line_number", 0),
                    "column_number": getattr(violation, "column_number", 0),
                    "is_staged": file_context.is_staged,
                    "is_modified": file_context.is_modified,
                    "git_status": file_context.git_status,
                },
                "code_snippet": getattr(violation, "code_snippet", ""),
                "violation_type": str(getattr(violation, "violation_type", "")),
            }
            violations_data.append(violation_data)

        report = {
            "constitutional_violations": violations_data,
            "summary": {
                "total_violations": len(violations),
                "high_severity": sum(
                    1 for v in violations if getattr(v, "severity", "") == "HIGH"
                ),
                "medium_severity": sum(
                    1 for v in violations if getattr(v, "severity", "") == "MEDIUM"
                ),
                "low_severity": sum(
                    1 for v in violations if getattr(v, "severity", "") == "LOW"
                ),
                "files_affected": len(
                    set(getattr(v, "file_path", "") for v in violations)
                ),
            },
            "git_context": {
                "repo_root": self.repo_root,
                "timestamp": self._get_timestamp(),
            },
        }

        return json.dumps(report, indent=2)

    def format_github_actions_report(self, violations: List[Any]) -> str:
        """Format violations for GitHub Actions annotations"""
        if not violations:
            return "::notice::No constitutional violations found"

        output = []

        for violation in violations:
            file_path = getattr(violation, "file_path", "")
            rel_path = (
                os.path.relpath(file_path, self.repo_root)
                if self.repo_root
                else file_path
            )
            line_no = getattr(violation, "line_number", 1)
            col_no = getattr(violation, "column_number", 1)

            # GitHub Actions annotation format
            severity = getattr(violation, "severity", "MEDIUM")
            annotation_type = {
                "HIGH": "error",
                "MEDIUM": "warning",
                "LOW": "notice",
            }.get(severity, "warning")

            rule_id = getattr(violation, "rule_id", "UNKNOWN")
            description = getattr(violation, "description", "Constitutional violation")
            suggested_fix = getattr(violation, "suggested_fix", "")

            message = f"[{rule_id}] {description}"
            if suggested_fix:
                message += f" | Fix: {suggested_fix}"

            output.append(
                f"::{annotation_type} file={rel_path},line={line_no},col={col_no}::{message}"
            )

        # Summary
        total = len(violations)
        output.append(
            f"::warning::Constitutional validation found {total} violation(s)"
        )

        return "\n".join(output)

    def _format_success_message(self, context: str) -> str:
        """Format success message for clean validation"""
        if self.format_type == GitReportFormat.TERMINAL:
            return f"{self.colors['green']}{self.colors['bold']}✅ Constitutional validation passed{self.colors['reset']}\n{self.colors['green']}All files comply with project's SE principles{self.colors['reset']}"
        elif self.format_type == GitReportFormat.GITHUB_ACTIONS:
            return "::notice::Constitutional validation passed - all files comply with SE principles"
        else:
            return "✅ Constitutional validation passed - all files comply with SE principles"

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime

        return datetime.now().isoformat()

    def generate_report(
        self, violations: List[Any], context: str = "validation"
    ) -> str:
        """Generate violation report in the specified format"""
        if self.format_type == GitReportFormat.TERMINAL:
            return self.format_terminal_report(violations, context)
        elif self.format_type == GitReportFormat.PLAIN:
            return self.format_plain_report(violations)
        elif self.format_type == GitReportFormat.JSON:
            return self.format_json_report(violations)
        elif self.format_type == GitReportFormat.GITHUB_ACTIONS:
            return self.format_github_actions_report(violations)
        else:
            return self.format_plain_report(violations)

    def write_report_file(
        self, violations: List[Any], output_path: str, context: str = "validation"
    ) -> None:
        """Write violation report to a file"""
        report_content = self.generate_report(violations, context)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)


# Factory functions for easy instantiation
def create_terminal_reporter() -> GitViolationReporter:
    """Create a Git reporter for terminal output"""
    return GitViolationReporter(GitReportFormat.TERMINAL)


def create_ci_reporter() -> GitViolationReporter:
    """Create a Git reporter for CI/CD output"""
    return GitViolationReporter(GitReportFormat.PLAIN)


def create_json_reporter() -> GitViolationReporter:
    """Create a Git reporter for JSON output"""
    return GitViolationReporter(GitReportFormat.JSON)


def create_github_actions_reporter() -> GitViolationReporter:
    """Create a Git reporter for GitHub Actions"""
    return GitViolationReporter(GitReportFormat.GITHUB_ACTIONS)


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="project Git Constitutional Violation Reporter"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "plain", "json", "github"],
        default="terminal",
        help="Output format",
    )
    parser.add_argument("--context", default="validation", help="Validation context")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Create sample violations for testing
    from types import SimpleNamespace

    sample_violations = [
        SimpleNamespace(
            rule_id="SRP-001",
            severity="HIGH",
            se_principle="Single Responsibility Principle",
            description="Function has cyclomatic complexity of 15 (max: 10)",
            suggested_fix="Break this function into smaller, single-purpose functions",
            file_path="src/example.py",
            line_number=42,
            column_number=8,
            code_snippet="def complex_function():\n    if condition1:\n        if condition2:\n            # nested logic...",
            violation_type="SRP_VIOLATION",
        )
    ]

    # Create reporter
    format_map = {
        "terminal": GitReportFormat.TERMINAL,
        "plain": GitReportFormat.PLAIN,
        "json": GitReportFormat.JSON,
        "github": GitReportFormat.GITHUB_ACTIONS,
    }

    reporter = GitViolationReporter(format_map[args.format])

    # Generate report
    if args.output:
        reporter.write_report_file(sample_violations, args.output, args.context)
        print(f"Report written to: {args.output}")
    else:
        print(reporter.generate_report(sample_violations, args.context))
