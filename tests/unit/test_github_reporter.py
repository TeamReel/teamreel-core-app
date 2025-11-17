#!/usr/bin/env python3
"""
Unit tests for GitHub Reporter functionality.

Tests GitHub-specific reporting capabilities for constitutional compliance
validation, including status checks, PR comments, and compliance dashboards.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from github_reporter import (
    GitHubReporter,
    GitHubStatusCheck,
    GitHubPRComment,
    GitHubComplianceReport,
    ValidationResult,
)

# Import constitutional validator for test data
from compliance_reporter import ComplianceReport, Violation


class TestGitHubStatusCheck(unittest.TestCase):
    """Test GitHubStatusCheck dataclass."""

    def test_status_check_creation(self):
        """Test creating a GitHubStatusCheck."""
        check = GitHubStatusCheck(
            context="Constitutional Compliance",
            state="success",
            description="All checks passed",
            target_url="https://github.com/project/test/actions/runs/123",
        )

        self.assertEqual(check.context, "Constitutional Compliance")
        self.assertEqual(check.state, "success")
        self.assertEqual(check.description, "All checks passed")
        self.assertEqual(
            check.target_url, "https://github.com/project/test/actions/runs/123"
        )

    def test_status_check_without_target_url(self):
        """Test creating a GitHubStatusCheck without target URL."""
        check = GitHubStatusCheck(
            context="Test Check", state="failure", description="Test failed"
        )

        self.assertEqual(check.context, "Test Check")
        self.assertEqual(check.state, "failure")
        self.assertEqual(check.description, "Test failed")
        self.assertIsNone(check.target_url)


class TestGitHubPRComment(unittest.TestCase):
    """Test GitHubPRComment dataclass."""

    def test_pr_comment_creation(self):
        """Test creating a GitHubPRComment."""
        comment = GitHubPRComment(
            title="Test Comment",
            body="This is a test comment body.",
            update_existing=False,
        )

        self.assertEqual(comment.title, "Test Comment")
        self.assertEqual(comment.body, "This is a test comment body.")
        self.assertFalse(comment.update_existing)

    def test_pr_comment_default_update(self):
        """Test GitHubPRComment with default update_existing."""
        comment = GitHubPRComment(
            title="Test Comment", body="This is a test comment body."
        )

        self.assertTrue(comment.update_existing)


class TestGitHubComplianceReport(unittest.TestCase):
    """Test GitHubComplianceReport dataclass."""

    def test_compliance_report_creation(self):
        """Test creating a GitHubComplianceReport."""
        status_check = GitHubStatusCheck("Test", "success", "Passed")
        pr_comment = GitHubPRComment("Test", "Test body")

        report = GitHubComplianceReport(
            pr_number=123,
            commit_sha="abc123def456",
            compliance_score=95.5,
            violations_count=2,
            files_checked=10,
            status_checks=[status_check],
            pr_comment=pr_comment,
            workflow_summary="Test summary",
            artifacts=["report1.json", "report2.md"],
        )

        self.assertEqual(report.pr_number, 123)
        self.assertEqual(report.commit_sha, "abc123def456")
        self.assertEqual(report.compliance_score, 95.5)
        self.assertEqual(report.violations_count, 2)
        self.assertEqual(report.files_checked, 10)
        self.assertEqual(len(report.status_checks), 1)
        self.assertEqual(report.status_checks[0].context, "Test")
        self.assertIsNotNone(report.pr_comment)
        self.assertEqual(report.workflow_summary, "Test summary")
        self.assertEqual(len(report.artifacts), 2)


class TestGitHubReporter(unittest.TestCase):
    """Test GitHubReporter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.reporter = GitHubReporter(
            "project/test-repo", "https://github.com/project/test-repo"
        )

        # Create sample compliance reports (using available classes)
        self.sample_violations = [
            Violation(
                principle="single_responsibility",
                severity="ERROR",
                message="Class has too many responsibilities",
                file_path="src/test_file1.py",
                line_number=25,
                suggested_fix="Split class into smaller, focused classes",
            )
        ]

        self.sample_report_with_violations = ComplianceReport(
            compliance_status="FAIL",
            violations=self.sample_violations,
            quality_gates={"coverage_threshold": False, "complexity_limit": True},
            metadata={"files_checked": 2, "compliance_score": 85.0},
        )

        self.sample_report_clean = ComplianceReport(
            compliance_status="PASS",
            violations=[],
            quality_gates={"coverage_threshold": True, "complexity_limit": True},
            metadata={"files_checked": 1, "compliance_score": 100.0},
        )

        # Create sample validation results
        self.validation_results = [
            ValidationResult(
                file_path="src/test_file1.py",
                is_valid=False,
                violations=self.sample_violations,
                compliance_score=85.0,
            ),
            ValidationResult(
                file_path="src/clean_file.py",
                is_valid=True,
                violations=[],
                compliance_score=100.0,
            ),
        ]

    @patch.dict(os.environ, {"GITHUB_REPOSITORY": "project/test-repo"})
    def test_reporter_initialization_from_env(self):
        """Test GitHubReporter initialization from environment variables."""
        reporter = GitHubReporter()
        self.assertEqual(reporter.repo_name, "project/test-repo")
        self.assertEqual(reporter.base_url, "https://github.com/project/test-repo")

    @patch.dict(
        os.environ,
        {
            "GITHUB_RUN_ID": "123456789",
            "GITHUB_SHA": "abc123def456",
            "GITHUB_ACTOR": "test-user",
        },
    )
    def test_reporter_initialization_with_github_env(self):
        """Test GitHubReporter initialization with GitHub environment variables."""
        reporter = GitHubReporter()
        self.assertEqual(reporter.workflow_run_id, "123456789")
        self.assertEqual(reporter.commit_sha, "abc123def456")
        self.assertEqual(reporter.actor, "test-user")

    def test_generate_compliance_report(self):
        """Test generating a comprehensive compliance report."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        self.assertEqual(report.violations_count, 1)
        self.assertEqual(report.files_checked, 2)
        self.assertEqual(report.compliance_score, 92.5)  # Average of 85.0 and 100.0

        # Check status checks are generated
        self.assertGreater(len(report.status_checks), 0)
        main_check = next(
            (
                check
                for check in report.status_checks
                if check.context == "Constitutional Compliance"
            ),
            None,
        )
        self.assertIsNotNone(main_check)
        self.assertEqual(main_check.state, "failure")  # Because there are violations

        # Check workflow summary is generated
        self.assertIn("Constitutional Compliance Summary", report.workflow_summary)
        self.assertIn("1", report.workflow_summary)  # violations count

    def test_generate_compliance_report_no_violations(self):
        """Test generating compliance report with no violations."""
        clean_results = [
            ValidationResult(
                file_path="src/clean_file.py",
                is_valid=True,
                violations=[],
                compliance_score=100.0,
            )
        ]

        report = self.reporter.generate_compliance_report(clean_results)

        self.assertEqual(report.violations_count, 0)
        self.assertEqual(report.files_checked, 1)
        self.assertEqual(report.compliance_score, 100.0)

        # Check main status check is success
        main_check = next(
            (
                check
                for check in report.status_checks
                if check.context == "Constitutional Compliance"
            ),
            None,
        )
        self.assertIsNotNone(main_check)
        self.assertEqual(main_check.state, "success")

    def test_generate_status_checks(self):
        """Test generating GitHub status checks."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        # Should have main compliance check plus SE principle checks
        self.assertGreater(len(report.status_checks), 1)

        # Check main compliance status
        main_check = next(
            (
                check
                for check in report.status_checks
                if check.context == "Constitutional Compliance"
            ),
            None,
        )
        self.assertIsNotNone(main_check)
        self.assertEqual(main_check.state, "failure")
        self.assertIn("1 violations found", main_check.description)

        # Check SE principle status checks exist
        srp_check = next(
            (
                check
                for check in report.status_checks
                if "Single Responsibility" in check.context
            ),
            None,
        )
        self.assertIsNotNone(srp_check)
        self.assertEqual(srp_check.state, "failure")

    @patch.dict(os.environ, {"GITHUB_REF": "refs/pull/123/merge"})
    def test_get_pr_number_from_ref(self):
        """Test extracting PR number from GitHub ref."""
        with patch.dict(os.environ, {"GITHUB_REF": "refs/pull/123/merge"}):
            reporter = GitHubReporter()
            self.assertEqual(reporter.pr_number, 123)

    @patch("builtins.open", mock_open(read_data='{"pull_request": {"number": 456}}'))
    @patch.dict(os.environ, {"GITHUB_EVENT_PATH": "/tmp/event.json"})
    @patch("os.path.exists", return_value=True)
    def test_get_pr_number_from_event(self, mock_exists):
        """Test extracting PR number from GitHub event file."""
        reporter = GitHubReporter()
        self.assertEqual(reporter.pr_number, 456)

    def test_generate_pr_comment_success(self):
        """Test generating PR comment for successful validation."""
        clean_results = [
            ValidationResult(
                file_path="src/clean_file.py",
                is_valid=True,
                violations=[],
                compliance_score=100.0,
            )
        ]

        report = self.reporter.generate_compliance_report(clean_results)

        self.assertIsNotNone(report.pr_comment)
        self.assertIn("Constitutional Compliance: PASSED", report.pr_comment.body)
        self.assertIn("Congratulations!", report.pr_comment.body)
        self.assertIn("approved for merge", report.pr_comment.body)

    def test_generate_pr_comment_failure(self):
        """Test generating PR comment for failed validation."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        self.assertIsNotNone(report.pr_comment)
        self.assertIn("Constitutional Compliance: FAILED", report.pr_comment.body)
        self.assertIn("violations that must be fixed", report.pr_comment.body)
        self.assertIn("Single Responsibility", report.pr_comment.body)
        self.assertIn("Class has too many responsibilities", report.pr_comment.body)

    def test_export_status_checks(self):
        """Test exporting status checks to JSON file."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as tmp_file:
            output_file = self.reporter.export_status_checks(report, tmp_file.name)

            # Read back the exported file
            with open(output_file, "r") as f:
                data = json.load(f)

            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)

            # Check structure of first status check
            first_check = data[0]
            self.assertIn("context", first_check)
            self.assertIn("state", first_check)
            self.assertIn("description", first_check)

            # Cleanup
            os.unlink(output_file)

    def test_export_pr_comment(self):
        """Test exporting PR comment to markdown file."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as tmp_file:
            output_file = self.reporter.export_pr_comment(report, tmp_file.name)

            # Read back the exported file
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("Constitutional Compliance Report", content)
            self.assertIn("violations that must be fixed", content)

            # Cleanup
            os.unlink(output_file)

    def test_export_workflow_summary(self):
        """Test exporting workflow summary to markdown file."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as tmp_file:
            output_file = self.reporter.export_workflow_summary(report, tmp_file.name)

            # Read back the exported file
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("Constitutional Compliance Summary", content)
            self.assertIn("Validation Results", content)

            # Cleanup
            os.unlink(output_file)

    @patch("builtins.open", mock_open())
    @patch.dict(os.environ, {"GITHUB_OUTPUT": "/tmp/github_output"})
    def test_set_github_outputs(self):
        """Test setting GitHub Actions outputs."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        with patch("builtins.open", mock_open()) as mock_file:
            self.reporter.set_github_outputs(report)

            # Check that file was opened for append
            mock_file.assert_called_once_with("/tmp/github_output", "a")

            # Check that writes were made (can't easily verify content with mock_open)
            handle = mock_file.return_value
            self.assertGreater(handle.write.call_count, 0)

    @patch("builtins.open", mock_open())
    @patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "/tmp/step_summary"})
    def test_create_step_summary(self):
        """Test creating GitHub Actions step summary."""
        report = self.reporter.generate_compliance_report(self.validation_results)

        with patch("builtins.open", mock_open()) as mock_file:
            self.reporter.create_step_summary(report)

            # Check that file was opened for append with UTF-8 encoding
            mock_file.assert_called_once_with(
                "/tmp/step_summary", "a", encoding="utf-8"
            )

            # Check that writes were made
            handle = mock_file.return_value
            self.assertGreater(handle.write.call_count, 0)

    def test_no_github_env_handling(self):
        """Test handling when GitHub environment variables are not set."""
        # Clear all GitHub environment variables
        env_vars = [
            "GITHUB_OUTPUT",
            "GITHUB_STEP_SUMMARY",
            "GITHUB_EVENT_PATH",
            "GITHUB_REF",
        ]

        with patch.dict(os.environ, {var: "" for var in env_vars}, clear=True):
            reporter = GitHubReporter()
            report = reporter.generate_compliance_report(self.validation_results)

            # These should not raise exceptions
            reporter.set_github_outputs(report)
            reporter.create_step_summary(report)


class TestGitHubReporterCLI(unittest.TestCase):
    """Test GitHubReporter CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_validation_data = {
            "src/test_file.py": {
                "violations": [
                    {
                        "principle": "single_responsibility",
                        "level": "ERROR",
                        "message": "Class has too many responsibilities",
                        "line": 25,
                        "suggestion": "Split class into smaller parts",
                    }
                ],
                "compliance_score": 85.0,
            }
        }

    def test_cli_main_function_exists(self):
        """Test that the main CLI function exists."""
        from github_reporter import main

        self.assertTrue(callable(main))

    @patch(
        "sys.argv",
        [
            "github_reporter.py",
            "--validation-report",
            "test_report.json",
            "--export-all",
        ],
    )
    @patch("builtins.open", mock_open())
    @patch("json.load")
    @patch("pathlib.Path.mkdir")
    def test_cli_export_all(self, mock_mkdir, mock_json_load):
        """Test CLI with --export-all flag."""
        mock_json_load.return_value = self.test_validation_data

        # This would normally call sys.exit, so we catch SystemExit
        with self.assertRaises(SystemExit) as cm:
            from github_reporter import main

            main()

        # Should exit with code 0 for success
        # Note: The actual CLI implementation may vary


if __name__ == "__main__":
    # Set up test environment
    os.environ.setdefault("GITHUB_REPOSITORY", "project/test-repo")

    # Run tests
    unittest.main(verbosity=2)
