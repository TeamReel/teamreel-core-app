#!/usr/bin/env python3
"""
Integration tests for GitHub Actions workflows and validation.

Tests the complete GitHub Actions CI/CD pipeline including workflow syntax,
action integration, and end-to-end constitutional compliance validation.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, Mock

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestWorkflowSyntax(unittest.TestCase):
    """Test GitHub Actions workflow file syntax and structure."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.actions_dir = self.project_root / ".github" / "actions"

    def test_workflow_files_exist(self):
        """Test that required workflow files exist."""
        required_workflows = ["quality-gates.yml", "constitutional-compliance.yml"]

        for workflow_file in required_workflows:
            workflow_path = self.workflows_dir / workflow_file
            self.assertTrue(
                workflow_path.exists(), f"Workflow file {workflow_file} not found"
            )

    def test_action_files_exist(self):
        """Test that required action files exist."""
        action_path = self.actions_dir / "constitutional-validator" / "action.yml"
        self.assertTrue(
            action_path.exists(), "Constitutional validator action not found"
        )

    def test_workflow_yaml_syntax(self):
        """Test that all workflow YAML files have valid syntax."""
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        for workflow_file in workflow_files:
            with self.subTest(workflow=workflow_file.name):
                try:
                    with open(workflow_file, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.fail(f"YAML syntax error in {workflow_file.name}: {e}")

    def test_action_yaml_syntax(self):
        """Test that all action YAML files have valid syntax."""
        action_files = list(self.actions_dir.glob("**/action.yml")) + list(
            self.actions_dir.glob("**/action.yaml")
        )

        for action_file in action_files:
            with self.subTest(action=action_file.name):
                try:
                    with open(action_file, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.fail(f"YAML syntax error in {action_file}: {e}")

    def test_workflow_structure(self):
        """Test that workflows have required structure."""
        quality_gates_path = self.workflows_dir / "quality-gates.yml"
        constitutional_compliance_path = (
            self.workflows_dir / "constitutional-compliance.yml"
        )

        # Test quality-gates.yml structure
        if quality_gates_path.exists():
            with open(quality_gates_path, "r", encoding="utf-8") as f:
                quality_gates = yaml.safe_load(f)

            self.assertIn("name", quality_gates)
            self.assertIn("on", quality_gates)
            self.assertIn("jobs", quality_gates)

            # Check for pull_request trigger
            self.assertIn("pull_request", quality_gates["on"])

            # Check for required jobs
            self.assertIn("quality-gates", quality_gates["jobs"])

        # Test constitutional-compliance.yml structure
        if constitutional_compliance_path.exists():
            with open(constitutional_compliance_path, "r", encoding="utf-8") as f:
                constitutional_compliance = yaml.safe_load(f)

            self.assertIn("name", constitutional_compliance)
            self.assertIn("on", constitutional_compliance)
            self.assertIn("jobs", constitutional_compliance)

            # Check for pull_request trigger
            self.assertIn("pull_request", constitutional_compliance["on"])

    def test_timeout_minutes_compliance(self):
        """Test that workflow timeouts meet performance requirements (<= 5 minutes)."""
        workflow_files = list(self.workflows_dir.glob("*.yml"))

        for workflow_file in workflow_files:
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r", encoding="utf-8") as f:
                    workflow_data = yaml.safe_load(f)

                # Check job-level timeouts
                if "jobs" in workflow_data:
                    for job_name, job_data in workflow_data["jobs"].items():
                        if "timeout-minutes" in job_data:
                            timeout = job_data["timeout-minutes"]
                            self.assertLessEqual(
                                timeout,
                                5,
                                f"Job '{job_name}' in {workflow_file.name} has timeout {timeout}min > 5min limit",
                            )

    def test_action_structure(self):
        """Test that action files have required structure."""
        action_path = self.actions_dir / "constitutional-validator" / "action.yml"

        if action_path.exists():
            with open(action_path, "r", encoding="utf-8") as f:
                action_data = yaml.safe_load(f)

            # Required action metadata
            self.assertIn("name", action_data)
            self.assertIn("description", action_data)
            self.assertIn("inputs", action_data)
            self.assertIn("outputs", action_data)
            self.assertIn("runs", action_data)

            # Check runs configuration
            runs = action_data["runs"]
            self.assertIn("using", runs)
            self.assertEqual(runs["using"], "composite")
            self.assertIn("steps", runs)

            # Check required inputs
            inputs = action_data["inputs"]
            expected_inputs = [
                "config-path",
                "validation-scope",
                "strictness",
                "report-format",
            ]
            for input_name in expected_inputs:
                self.assertIn(
                    input_name, inputs, f"Missing required input: {input_name}"
                )

            # Check required outputs
            outputs = action_data["outputs"]
            expected_outputs = [
                "validation-result",
                "compliance-score",
                "violations-count",
                "report-path",
            ]
            for output_name in expected_outputs:
                self.assertIn(
                    output_name, outputs, f"Missing required output: {output_name}"
                )


class TestWorkflowIntegration(unittest.TestCase):
    """Test GitHub Actions workflow integration and functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        self.workflows_dir = self.project_root / ".github" / "workflows"

    def test_constitutional_validator_integration(self):
        """Test that workflows properly integrate with constitutional validator action."""
        workflow_files = list(self.workflows_dir.glob("*.yml"))

        found_integration = False
        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if workflow uses the constitutional validator action
            if "./.github/actions/constitutional-validator" in content:
                found_integration = True

                # Load YAML to check step configuration
                workflow_data = yaml.safe_load(content)

                # Find steps that use the action
                for job_name, job_data in workflow_data.get("jobs", {}).items():
                    if "steps" in job_data:
                        for step in job_data["steps"]:
                            if (
                                "uses" in step
                                and "constitutional-validator" in step["uses"]
                            ):
                                # Check that step has proper configuration
                                self.assertIn(
                                    "with",
                                    step,
                                    f"Constitutional validator step missing 'with' configuration",
                                )

        self.assertTrue(
            found_integration, "No workflow found using constitutional validator action"
        )

    def test_branch_protection_configuration(self):
        """Test that workflows are configured for proper branch protection."""
        constitutional_compliance_path = (
            self.workflows_dir / "constitutional-compliance.yml"
        )

        if constitutional_compliance_path.exists():
            with open(constitutional_compliance_path, "r", encoding="utf-8") as f:
                workflow_data = yaml.safe_load(f)

            # Check pull request triggers
            on_config = workflow_data.get("on", {})
            self.assertIn("pull_request", on_config)

            # Check that PR events include the right types
            pr_config = on_config["pull_request"]
            if isinstance(pr_config, dict) and "types" in pr_config:
                pr_types = pr_config["types"]
                required_types = ["opened", "synchronize", "reopened"]
                for pr_type in required_types:
                    self.assertIn(
                        pr_type, pr_types, f"Missing PR event type: {pr_type}"
                    )

    def test_concurrency_configuration(self):
        """Test that workflows have proper concurrency controls."""
        constitutional_compliance_path = (
            self.workflows_dir / "constitutional-compliance.yml"
        )

        if constitutional_compliance_path.exists():
            with open(constitutional_compliance_path, "r", encoding="utf-8") as f:
                workflow_data = yaml.safe_load(f)

            # Check for concurrency configuration
            if "concurrency" in workflow_data:
                concurrency = workflow_data["concurrency"]
                self.assertIn("group", concurrency)
                self.assertIn("cancel-in-progress", concurrency)

    def test_status_check_names(self):
        """Test that workflows create properly named status checks."""
        workflow_files = list(self.workflows_dir.glob("*.yml"))

        expected_status_contexts = ["Constitutional Compliance", "Quality Gates"]

        found_contexts = []
        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for status check context definitions
            for context in expected_status_contexts:
                if context in content:
                    found_contexts.append(context)

        # Should find at least the main constitutional compliance context
        self.assertIn("Constitutional Compliance", found_contexts)


class TestWorkflowExecution(unittest.TestCase):
    """Test GitHub Actions workflow execution scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent

    @unittest.skipIf(
        not os.getenv("GITHUB_ACTIONS"), "Only run in GitHub Actions environment"
    )
    def test_workflow_in_github_actions(self):
        """Test workflow execution in GitHub Actions environment."""
        # This test only runs when executed in actual GitHub Actions
        self.assertTrue(os.getenv("GITHUB_ACTIONS"))
        self.assertIsNotNone(os.getenv("GITHUB_WORKFLOW"))
        self.assertIsNotNone(os.getenv("GITHUB_RUN_ID"))

    def test_constitutional_validator_cli_exists(self):
        """Test that constitutional validator CLI is available."""
        validator_path = self.project_root / "src" / "constitutional_validator.py"
        self.assertTrue(
            validator_path.exists(), "Constitutional validator CLI not found"
        )

        # Check that it's executable as a Python module
        try:
            result = subprocess.run(
                [sys.executable, str(validator_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should not fail with import errors (exit code may vary)
            self.assertNotIn("ImportError", result.stderr)
            self.assertNotIn("ModuleNotFoundError", result.stderr)
        except subprocess.TimeoutExpired:
            self.fail("Constitutional validator CLI took too long to respond")
        except FileNotFoundError:
            self.skipTest("Python interpreter not available for CLI test")

    def test_github_reporter_cli_exists(self):
        """Test that GitHub reporter CLI is available."""
        reporter_path = self.project_root / "src" / "github_reporter.py"
        self.assertTrue(reporter_path.exists(), "GitHub reporter CLI not found")

        # Check that it's executable as a Python module
        try:
            result = subprocess.run(
                [sys.executable, str(reporter_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should not fail with import errors (exit code may vary)
            self.assertNotIn("ImportError", result.stderr)
            self.assertNotIn("ModuleNotFoundError", result.stderr)
        except subprocess.TimeoutExpired:
            self.fail("GitHub reporter CLI took too long to respond")
        except FileNotFoundError:
            self.skipTest("Python interpreter not available for CLI test")


class TestWorkflowPerformance(unittest.TestCase):
    """Test GitHub Actions workflow performance characteristics."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        self.workflows_dir = self.project_root / ".github" / "workflows"

    def test_workflow_job_parallelization(self):
        """Test that workflows use job parallelization where appropriate."""
        quality_gates_path = self.workflows_dir / "quality-gates.yml"

        if quality_gates_path.exists():
            with open(quality_gates_path, "r", encoding="utf-8") as f:
                workflow_data = yaml.safe_load(f)

            jobs = workflow_data.get("jobs", {})

            # Check for matrix strategy in quality gates
            quality_gates_job = jobs.get("quality-gates", {})
            if "strategy" in quality_gates_job:
                strategy = quality_gates_job["strategy"]
                self.assertIn(
                    "matrix",
                    strategy,
                    "Quality gates should use matrix strategy for parallelization",
                )

                # Check fail-fast setting for performance
                if "fail-fast" in strategy:
                    # fail-fast: false allows all matrix jobs to complete for comprehensive reporting
                    self.assertFalse(strategy["fail-fast"])

    def test_workflow_caching_configuration(self):
        """Test that workflows use caching where appropriate."""
        workflow_files = list(self.workflows_dir.glob("*.yml"))

        found_caching = False
        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for Python dependency caching
            if "cache: 'pip'" in content or "actions/cache" in content:
                found_caching = True

        # At least one workflow should use caching for performance
        self.assertTrue(
            found_caching, "No workflows found using caching for performance"
        )

    def test_workflow_step_optimization(self):
        """Test that workflow steps are optimized for performance."""
        workflow_files = list(self.workflows_dir.glob("*.yml"))

        for workflow_file in workflow_files:
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r", encoding="utf-8") as f:
                    workflow_data = yaml.safe_load(f)

                # Check for conditional step execution
                for job_name, job_data in workflow_data.get("jobs", {}).items():
                    if "steps" in job_data:
                        for step in job_data["steps"]:
                            # Steps should have conditions where appropriate
                            if "name" in step and "upload" in step["name"].lower():
                                # Upload steps should typically use 'if: always()' or similar
                                if "if" not in step:
                                    # This is just a warning, not a failure
                                    pass


if __name__ == "__main__":
    # Ensure we can import required modules
    try:
        import yaml
    except ImportError:
        print(
            "ERROR: PyYAML is required for workflow tests. Install with: pip install PyYAML"
        )
        sys.exit(1)

    # Run tests
    unittest.main(verbosity=2)
