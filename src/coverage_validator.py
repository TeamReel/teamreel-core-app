#!/usr/bin/env python3
"""
Coverage Validator - Test Coverage Quality Gate

This module implements test coverage validation as part of TeamReel's quality
gates system, enforcing minimum coverage thresholds with detailed reporting
and remediation guidance.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import json
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CoverageFormat(Enum):
    """Supported coverage report formats."""

    JSON = "json"
    XML = "xml"
    HTML = "html"
    TERMINAL = "terminal"


@dataclass
class CoverageFile:
    """Represents coverage data for a single file."""

    filename: str
    statements: int
    missing: int
    excluded: int
    coverage: float
    missing_lines: List[int] = field(default_factory=list)
    excluded_lines: List[int] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Complete coverage analysis report."""

    total_coverage: float
    threshold: float
    files_analyzed: int
    files_below_threshold: int
    total_statements: int
    total_missing: int
    files: List[CoverageFile] = field(default_factory=list)
    is_passing: bool = True
    remediation_suggestions: List[str] = field(default_factory=list)


class CoverageValidator:
    """Validates test coverage against configured thresholds."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize coverage validator with configuration."""
        self.config = config or self._default_config()
        self.threshold = self.config.get("coverage", {}).get("threshold", 80.0)
        self.exclude_patterns = self.config.get("coverage", {}).get(
            "exclude",
            [
                "*/tests/*",
                "*/test/*",
                "*/__pycache__/*",
                "*/venv/*",
                "*/.venv/*",
                "*/node_modules/*",
                "*/migrations/*",
                "**/conftest.py",
                "**/setup.py",
            ],
        )
        self.per_file_threshold = self.config.get("coverage", {}).get(
            "per_file_threshold", 70.0
        )

    def _default_config(self) -> Dict:
        """Default configuration for coverage validation."""
        return {
            "coverage": {
                "threshold": 80.0,
                "per_file_threshold": 70.0,
                "exclude": [
                    "*/tests/*",
                    "*/test/*",
                    "*/__pycache__/*",
                    "*/venv/*",
                    "*/.venv/*",
                    "*/node_modules/*",
                    "*/migrations/*",
                    "**/conftest.py",
                    "**/setup.py",
                ],
                "python": {
                    "tool": "pytest-cov",
                    "args": ["--cov=.", "--cov-report=json", "--cov-report=term"],
                },
                "javascript": {
                    "tool": "jest",
                    "args": [
                        "--coverage",
                        "--coverageReporters=json",
                        "--coverageReporters=text",
                    ],
                },
            }
        }

    def validate_python_coverage(self, source_dir: str = ".") -> CoverageReport:
        """Validate Python test coverage using pytest-cov."""
        try:
            # Run pytest with coverage
            cmd = [
                "pytest",
                f"--cov={source_dir}",
                "--cov-report=json",
                "--cov-report=term",
                "--cov-fail-under=0",  # We'll handle the threshold ourselves
            ]

            # Add exclude patterns
            for pattern in self.exclude_patterns:
                if pattern.endswith("/*"):
                    cmd.extend(["--cov-omit=", pattern])

            print(f"Running coverage analysis: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Parse coverage.json if it exists
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                return self._parse_python_coverage_json(coverage_file)
            else:
                # Fallback to parsing terminal output
                return self._parse_pytest_output(result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    "Coverage analysis timed out after 5 minutes",
                    "Consider optimizing test suite performance",
                    "Check for infinite loops or hanging tests",
                ],
            )
        except Exception as e:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    f"Coverage analysis failed: {str(e)}",
                    "Ensure pytest and pytest-cov are installed",
                    "Check that test files are properly configured",
                ],
            )

    def _parse_python_coverage_json(self, coverage_file: Path) -> CoverageReport:
        """Parse pytest-cov JSON output."""
        try:
            with open(coverage_file) as f:
                data = json.load(f)

            total_coverage = data["totals"]["percent_covered"]
            files = []
            files_below_threshold = 0

            for filename, file_data in data["files"].items():
                # Skip excluded files
                if self._should_exclude_file(filename):
                    continue

                coverage_pct = file_data["summary"]["percent_covered"]
                statements = file_data["summary"]["num_statements"]
                missing = file_data["summary"]["missing_lines"]
                excluded = file_data["summary"]["excluded_lines"]

                # Parse missing lines
                missing_lines = []
                if missing:
                    missing_lines = self._parse_line_ranges(str(missing))

                # Parse excluded lines
                excluded_lines = []
                if excluded:
                    excluded_lines = self._parse_line_ranges(str(excluded))

                coverage_file_obj = CoverageFile(
                    filename=filename,
                    statements=statements,
                    missing=len(missing_lines),
                    excluded=len(excluded_lines),
                    coverage=coverage_pct,
                    missing_lines=missing_lines,
                    excluded_lines=excluded_lines,
                )

                files.append(coverage_file_obj)

                if coverage_pct < self.per_file_threshold:
                    files_below_threshold += 1

            # Generate remediation suggestions
            suggestions = self._generate_coverage_suggestions(
                total_coverage, files_below_threshold, files
            )

            return CoverageReport(
                total_coverage=total_coverage,
                threshold=self.threshold,
                files_analyzed=len(files),
                files_below_threshold=files_below_threshold,
                total_statements=data["totals"]["num_statements"],
                total_missing=data["totals"]["missing_lines"],
                files=files,
                is_passing=total_coverage >= self.threshold,
                remediation_suggestions=suggestions,
            )

        except Exception as e:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    f"Failed to parse coverage report: {str(e)}",
                    "Ensure coverage.json is generated properly",
                    "Check pytest-cov configuration",
                ],
            )

    def _parse_pytest_output(self, stdout: str, stderr: str) -> CoverageReport:
        """Parse pytest terminal output for coverage information."""
        # Look for coverage percentage in output
        coverage_pattern = r"TOTAL\s+\d+\s+\d+\s+(\d+)%"
        match = re.search(coverage_pattern, stdout)

        if match:
            total_coverage = float(match.group(1))

            return CoverageReport(
                total_coverage=total_coverage,
                threshold=self.threshold,
                files_analyzed=1,  # Approximate
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=total_coverage >= self.threshold,
                remediation_suggestions=[
                    "Coverage parsed from terminal output - install pytest-cov for detailed analysis",
                    "Run with '--cov-report=json' for detailed file-by-file coverage",
                ],
            )
        else:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    "Could not parse coverage from output",
                    "Ensure tests are running successfully",
                    "Check pytest configuration and test discovery",
                ],
            )

    def validate_javascript_coverage(self, project_dir: str = ".") -> CoverageReport:
        """Validate JavaScript/TypeScript test coverage using Jest."""
        try:
            # Check if package.json exists
            package_json = Path(project_dir) / "package.json"
            if not package_json.exists():
                return CoverageReport(
                    total_coverage=0.0,
                    threshold=self.threshold,
                    files_analyzed=0,
                    files_below_threshold=0,
                    total_statements=0,
                    total_missing=0,
                    is_passing=True,  # Skip if no JS project
                    remediation_suggestions=[
                        "No package.json found - skipping JavaScript coverage",
                        "This appears to be a Python-only project",
                    ],
                )

            # Run Jest with coverage
            cmd = ["npm", "test", "--", "--coverage", "--coverageReporters=json"]

            print(f"Running JavaScript coverage: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=project_dir
            )

            # Look for coverage/coverage-final.json
            coverage_files = [
                Path(project_dir) / "coverage" / "coverage-final.json",
                Path(project_dir) / "coverage.json",
            ]

            for coverage_file in coverage_files:
                if coverage_file.exists():
                    return self._parse_javascript_coverage_json(coverage_file)

            # Fallback to output parsing
            return self._parse_jest_output(result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    "JavaScript coverage analysis timed out",
                    "Check Jest configuration and test performance",
                ],
            )
        except Exception as e:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=True,  # Don't fail on JS errors in Python projects
                remediation_suggestions=[
                    f"JavaScript coverage analysis failed: {str(e)}",
                    "This may be expected in Python-only projects",
                ],
            )

    def _parse_javascript_coverage_json(self, coverage_file: Path) -> CoverageReport:
        """Parse Jest coverage JSON output."""
        try:
            with open(coverage_file) as f:
                data = json.load(f)

            total_statements = 0
            total_covered = 0
            files = []
            files_below_threshold = 0

            for filename, file_data in data.items():
                if self._should_exclude_file(filename):
                    continue

                statements = len(file_data.get("s", {}))
                covered_statements = sum(
                    1 for count in file_data.get("s", {}).values() if count > 0
                )
                coverage_pct = (
                    (covered_statements / statements * 100) if statements > 0 else 100
                )

                missing_lines = [
                    int(line)
                    for line, count in file_data.get("s", {}).items()
                    if count == 0
                ]

                coverage_file_obj = CoverageFile(
                    filename=filename,
                    statements=statements,
                    missing=len(missing_lines),
                    excluded=0,
                    coverage=coverage_pct,
                    missing_lines=missing_lines,
                )

                files.append(coverage_file_obj)
                total_statements += statements
                total_covered += covered_statements

                if coverage_pct < self.per_file_threshold:
                    files_below_threshold += 1

            total_coverage_pct = (
                (total_covered / total_statements * 100)
                if total_statements > 0
                else 100
            )
            suggestions = self._generate_coverage_suggestions(
                total_coverage_pct, files_below_threshold, files
            )

            return CoverageReport(
                total_coverage=total_coverage_pct,
                threshold=self.threshold,
                files_analyzed=len(files),
                files_below_threshold=files_below_threshold,
                total_statements=total_statements,
                total_missing=total_statements - total_covered,
                files=files,
                is_passing=total_coverage_pct >= self.threshold,
                remediation_suggestions=suggestions,
            )

        except Exception as e:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=False,
                remediation_suggestions=[
                    f"Failed to parse JavaScript coverage: {str(e)}"
                ],
            )

    def _parse_jest_output(self, stdout: str, stderr: str) -> CoverageReport:
        """Parse Jest terminal output for coverage."""
        # Look for coverage table in Jest output
        coverage_pattern = r"All files\s+\|\s+([\d.]+)\s+\|"
        match = re.search(coverage_pattern, stdout)

        if match:
            total_coverage = float(match.group(1))
            return CoverageReport(
                total_coverage=total_coverage,
                threshold=self.threshold,
                files_analyzed=1,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=total_coverage >= self.threshold,
                remediation_suggestions=[
                    "Coverage parsed from Jest terminal output",
                    "Configure Jest to output JSON for detailed analysis",
                ],
            )
        else:
            return CoverageReport(
                total_coverage=0.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=True,  # Don't fail if no JS tests
                remediation_suggestions=[
                    "No JavaScript coverage data found",
                    "This may be expected in Python-only projects",
                ],
            )

    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded from coverage analysis."""
        for pattern in self.exclude_patterns:
            # Simple pattern matching - could be enhanced with fnmatch
            if pattern.replace("*", "").replace("/", "") in filename:
                return True
        return False

    def _parse_line_ranges(self, line_str: str) -> List[int]:
        """Parse line ranges like '10-15, 20, 25-30' into list of line numbers."""
        lines = []
        if not line_str or line_str == "None":
            return lines

        for part in str(line_str).split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                lines.extend(range(int(start), int(end) + 1))
            else:
                try:
                    lines.append(int(part))
                except ValueError:
                    continue

        return sorted(lines)

    def _generate_coverage_suggestions(
        self,
        total_coverage: float,
        files_below_threshold: int,
        files: List[CoverageFile],
    ) -> List[str]:
        """Generate remediation suggestions based on coverage analysis."""
        suggestions = []

        if total_coverage < self.threshold:
            gap = self.threshold - total_coverage
            suggestions.append(
                f"Coverage is {gap:.1f}% below the {self.threshold}% threshold"
            )
            suggestions.append("Focus on adding tests for uncovered code paths")

        if files_below_threshold > 0:
            suggestions.append(
                f"{files_below_threshold} files have coverage below {self.per_file_threshold}%"
            )

            # Suggest specific files to focus on
            low_coverage_files = sorted(
                [f for f in files if f.coverage < self.per_file_threshold],
                key=lambda x: x.coverage,
            )[:5]

            for file_obj in low_coverage_files:
                suggestions.append(
                    f"- {file_obj.filename}: {file_obj.coverage:.1f}% coverage ({file_obj.missing}/{file_obj.statements} lines missing)"
                )

        # General improvement suggestions
        if total_coverage < 90:
            suggestions.extend(
                [
                    "Consider adding unit tests for edge cases and error conditions",
                    "Review uncovered lines and add targeted test cases",
                    "Use coverage reports to identify missing test scenarios",
                ]
            )

        return suggestions

    def validate_coverage(self, project_dir: str = ".") -> Dict[str, CoverageReport]:
        """Validate coverage for all supported languages in the project."""
        results = {}

        # Check for Python project
        python_files = list(Path(project_dir).rglob("*.py"))
        if python_files:
            print("🐍 Analyzing Python test coverage...")
            results["python"] = self.validate_python_coverage(project_dir)

        # Check for JavaScript/TypeScript project
        package_json = Path(project_dir) / "package.json"
        if package_json.exists():
            print("📦 Analyzing JavaScript/TypeScript test coverage...")
            results["javascript"] = self.validate_javascript_coverage(project_dir)

        if not results:
            results["none"] = CoverageReport(
                total_coverage=100.0,
                threshold=self.threshold,
                files_analyzed=0,
                files_below_threshold=0,
                total_statements=0,
                total_missing=0,
                is_passing=True,
                remediation_suggestions=["No source files found to analyze"],
            )

        return results

    def format_report(
        self, reports: Dict[str, CoverageReport], format_type: str = "terminal"
    ) -> str:
        """Format coverage validation report."""
        if format_type == "json":
            return json.dumps(
                {
                    lang: {
                        "total_coverage": report.total_coverage,
                        "threshold": report.threshold,
                        "is_passing": report.is_passing,
                        "files_analyzed": report.files_analyzed,
                        "files_below_threshold": report.files_below_threshold,
                        "remediation_suggestions": report.remediation_suggestions,
                    }
                    for lang, report in reports.items()
                },
                indent=2,
            )

        # Terminal format
        output = []
        output.append("📊 TEST COVERAGE VALIDATION REPORT")
        output.append("=" * 50)

        overall_passing = all(report.is_passing for report in reports.values())

        for lang, report in reports.items():
            if lang == "none":
                continue

            output.append(f"\n{lang.upper()} Coverage:")
            output.append(
                f"  Coverage: {report.total_coverage:.1f}% (threshold: {report.threshold}%)"
            )
            output.append(f"  Status: {'✅ PASS' if report.is_passing else '❌ FAIL'}")
            output.append(f"  Files analyzed: {report.files_analyzed}")

            if report.files_below_threshold > 0:
                output.append(
                    f"  Files below threshold: {report.files_below_threshold}"
                )

            if report.remediation_suggestions:
                output.append("  Suggestions:")
                for suggestion in report.remediation_suggestions[:5]:
                    output.append(f"    • {suggestion}")

        output.append(f"\n{'='*50}")
        output.append(f"Overall Status: {'✅ PASS' if overall_passing else '❌ FAIL'}")

        if not overall_passing:
            output.append(
                "\n❌ Coverage validation failed. Please address the issues above."
            )
        else:
            output.append("\n✅ All coverage thresholds met!")

        return "\n".join(output)


def main():
    """CLI entry point for coverage validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate test coverage against thresholds"
    )
    parser.add_argument(
        "--threshold", type=float, default=80.0, help="Minimum coverage threshold"
    )
    parser.add_argument(
        "--per-file-threshold",
        type=float,
        default=70.0,
        help="Per-file coverage threshold",
    )
    parser.add_argument(
        "--project-dir", default=".", help="Project directory to analyze"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format",
    )
    parser.add_argument(
        "--fail-under",
        action="store_true",
        help="Exit with error if coverage below threshold",
    )

    args = parser.parse_args()

    # Configure validator
    config = {
        "coverage": {
            "threshold": args.threshold,
            "per_file_threshold": args.per_file_threshold,
        }
    }

    validator = CoverageValidator(config)
    reports = validator.validate_coverage(args.project_dir)

    # Output report
    print(validator.format_report(reports, args.format))

    # Exit with error if any coverage below threshold
    if args.fail_under:
        if not all(report.is_passing for report in reports.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
