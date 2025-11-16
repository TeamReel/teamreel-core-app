"""
Integration Tests for Git Hooks Installation (WP04)
Tests the complete installation and execution workflow

SE Principle Focus: Integration and End-to-End Reliability
"""

import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path


class TestGitHooksInstallation:
    """Integration tests for Git hooks installation process"""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary Git repository with hooks structure"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)

        # Initialize git repository
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
        )

        # Create basic directory structure
        (repo_path / "src").mkdir()
        (repo_path / "hooks").mkdir()
        (repo_path / "scripts").mkdir()

        # Copy hook files to temp repo
        src_hooks = Path("hooks")
        dst_hooks = repo_path / "hooks"

        if src_hooks.exists():
            for hook_file in src_hooks.glob("*"):
                if hook_file.is_file():
                    shutil.copy2(hook_file, dst_hooks / hook_file.name)

        # Copy installation script
        src_script = Path("scripts/install_git_hooks.ps1")
        if src_script.exists():
            shutil.copy2(src_script, repo_path / "scripts" / "install_git_hooks.ps1")

        # Create minimal constitutional validator for testing
        minimal_validator = '''
"""Minimal constitutional validator for testing"""
class ConstitutionalValidator:
    def validate_file(self, file_path):
        class Result:
            violations = []
        return Result()
'''
        (repo_path / "src" / "constitutional_validator.py").write_text(
            minimal_validator
        )

        # Create minimal git reporter
        minimal_reporter = '''
"""Minimal git reporter for testing"""
from enum import Enum

class GitReportFormat(Enum):
    TERMINAL = "terminal"

class GitViolationReporter:
    def __init__(self, format_type=GitReportFormat.TERMINAL):
        self.format_type = format_type
    
    def report_file_violations(self, file_path, violations):
        if violations:
            print(f"Violations in {file_path}: {len(violations)}")
'''
        (repo_path / "src" / "git_reporter.py").write_text(minimal_reporter)

        # Create minimal quality gates
        minimal_quality = '''
"""Minimal quality gates for testing"""
class QualityGateValidator:
    def validate_repository(self, repo_path):
        class Result:
            passed = True
            gate_results = {}
        return Result()
'''
        (repo_path / "src" / "quality_gates.py").write_text(minimal_quality)

        yield repo_path

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_hook_files_installation(self, temp_git_repo):
        """Test that hook files can be installed to .git/hooks"""
        hooks_dir = temp_git_repo / ".git" / "hooks"

        # Expected hook files
        expected_hooks = ["pre-commit", "pre-commit.ps1", "pre-push", "pre-push.ps1"]

        # Manually install hooks (simulating installation script)
        for hook_name in expected_hooks:
            src_hook = temp_git_repo / "hooks" / hook_name
            if src_hook.exists():
                dst_hook = hooks_dir / hook_name
                shutil.copy2(src_hook, dst_hook)

                # Verify installation
                assert dst_hook.exists(), f"Hook {hook_name} should be installed"
                assert dst_hook.is_file(), f"Hook {hook_name} should be a file"

                # Check content is copied
                src_content = src_hook.read_text(encoding="utf-8")
                dst_content = dst_hook.read_text(encoding="utf-8")
                assert (
                    src_content == dst_content
                ), f"Hook {hook_name} content should match"

    def test_bash_pre_commit_hook_execution(self, temp_git_repo):
        """Test bash pre-commit hook execution"""
        # Install the hook
        src_hook = temp_git_repo / "hooks" / "pre-commit"
        if not src_hook.exists():
            pytest.skip("pre-commit hook not found")

        dst_hook = temp_git_repo / ".git" / "hooks" / "pre-commit"
        shutil.copy2(src_hook, dst_hook)

        # Make executable (Unix-like systems)
        if hasattr(os, "chmod"):
            os.chmod(dst_hook, 0o755)

        # Create a test file to commit
        test_file = temp_git_repo / "test.py"
        test_file.write_text('# Simple test file\nprint("Hello")\n')

        # Stage the file
        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        # Try to run the hook directly (not through git commit)
        # This tests the hook logic without triggering actual git operations
        try:
            result = subprocess.run(
                ["bash", str(dst_hook)],
                cwd=temp_git_repo,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Hook should execute without crashing
            # May return 0 (success) or 1 (violations found) - both are valid outcomes
            assert result.returncode in [
                0,
                1,
            ], f"Hook returned unexpected code: {result.returncode}"

            # Should not crash with unhandled exceptions
            assert "Traceback" not in result.stderr, f"Hook crashed: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("Hook execution timed out - performance issue")
        except subprocess.CalledProcessError as e:
            # This is expected if bash is not available (Windows)
            if "bash" in str(e):
                pytest.skip("Bash not available for testing")
            else:
                raise

    def test_powershell_pre_commit_hook_execution(self, temp_git_repo):
        """Test PowerShell pre-commit hook execution"""
        # Install the hook
        src_hook = temp_git_repo / "hooks" / "pre-commit.ps1"
        if not src_hook.exists():
            pytest.skip("pre-commit.ps1 hook not found")

        dst_hook = temp_git_repo / ".git" / "hooks" / "pre-commit.ps1"
        shutil.copy2(src_hook, dst_hook)

        # Create a test file to commit
        test_file = temp_git_repo / "test.py"
        test_file.write_text('# Simple test file\nprint("Hello")\n')

        # Stage the file
        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        # Try to run the PowerShell hook
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-File", str(dst_hook)],
                cwd=temp_git_repo,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Hook should execute without crashing
            assert result.returncode in [
                0,
                1,
            ], f"PowerShell hook returned unexpected code: {result.returncode}"

            # Should not crash with syntax errors
            assert (
                "ParseException" not in result.stderr
            ), f"PowerShell hook has syntax errors: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("PowerShell hook execution timed out - performance issue")
        except FileNotFoundError:
            pytest.skip("PowerShell not available for testing")
        except subprocess.CalledProcessError as e:
            if "powershell" in str(e):
                pytest.skip("PowerShell not available for testing")
            else:
                raise

    def test_installation_script_basic_execution(self, temp_git_repo):
        """Test that installation script can run without crashing"""
        script_path = temp_git_repo / "scripts" / "install_git_hooks.ps1"
        if not script_path.exists():
            pytest.skip("Installation script not found")

        try:
            # Test help function (should not install anything)
            result = subprocess.run(
                ["powershell", "-NoProfile", "-File", str(script_path), "-Help"],
                cwd=temp_git_repo,
                capture_output=True,
                text=True,
                timeout=15,
            )

            # Should show help without errors
            assert (
                result.returncode == 0
            ), f"Installation script help failed: {result.stderr}"
            assert (
                "Usage:" in result.stdout or "help" in result.stdout.lower()
            ), "Help should show usage information"

        except subprocess.TimeoutExpired:
            pytest.fail("Installation script timed out")
        except FileNotFoundError:
            pytest.skip("PowerShell not available for testing")

    def test_hook_performance_requirements(self, temp_git_repo):
        """Test that hooks meet performance requirements (< 5 seconds)"""
        # This is a simplified performance test
        hooks_to_test = []

        # Check which hooks exist
        for hook_name in ["pre-commit", "pre-commit.ps1"]:
            src_hook = temp_git_repo / "hooks" / hook_name
            if src_hook.exists():
                hooks_to_test.append((hook_name, src_hook))

        if not hooks_to_test:
            pytest.skip("No hooks available for performance testing")

        for hook_name, src_hook in hooks_to_test:
            # Install hook
            dst_hook = temp_git_repo / ".git" / "hooks" / hook_name
            shutil.copy2(src_hook, dst_hook)

            if hook_name.endswith(".ps1"):
                continue  # Skip PowerShell performance test for now

            # Make executable
            if hasattr(os, "chmod"):
                os.chmod(dst_hook, 0o755)

            # Create minimal test file
            test_file = temp_git_repo / "simple.py"
            test_file.write_text('print("test")\n')
            subprocess.run(["git", "add", "simple.py"], cwd=temp_git_repo, check=True)

            # Time the hook execution
            import time

            start_time = time.time()

            try:
                result = subprocess.run(
                    ["bash", str(dst_hook)],
                    cwd=temp_git_repo,
                    capture_output=True,
                    timeout=10,
                )  # Max 10 seconds

                end_time = time.time()
                execution_time = end_time - start_time

                # Should complete within 5 seconds for simple file
                assert (
                    execution_time < 5.0
                ), f"Hook {hook_name} took {execution_time:.2f}s, should be < 5s"

            except subprocess.TimeoutExpired:
                pytest.fail(f"Hook {hook_name} exceeded 10 second timeout")
            except subprocess.CalledProcessError:
                # Hook may fail due to missing dependencies, but shouldn't timeout
                end_time = time.time()
                execution_time = end_time - start_time
                assert (
                    execution_time < 5.0
                ), f"Hook {hook_name} took {execution_time:.2f}s even when failing"

    def test_hook_error_handling(self, temp_git_repo):
        """Test that hooks handle errors gracefully"""
        # Test with missing constitutional validator
        hooks_dir = temp_git_repo / ".git" / "hooks"

        # Remove the constitutional validator to test error handling
        (temp_git_repo / "src" / "constitutional_validator.py").unlink(missing_ok=True)

        for hook_name in ["pre-commit", "pre-commit.ps1"]:
            src_hook = temp_git_repo / "hooks" / hook_name
            if not src_hook.exists():
                continue

            dst_hook = hooks_dir / hook_name
            shutil.copy2(src_hook, dst_hook)

            # Create test file
            test_file = temp_git_repo / "error_test.py"
            test_file.write_text('print("error test")\n')
            subprocess.run(
                ["git", "add", "error_test.py"], cwd=temp_git_repo, check=True
            )

            if hook_name.endswith(".ps1"):
                cmd = ["powershell", "-NoProfile", "-File", str(dst_hook)]
            else:
                cmd = ["bash", str(dst_hook)]
                if hasattr(os, "chmod"):
                    os.chmod(dst_hook, 0o755)

            try:
                result = subprocess.run(
                    cmd, cwd=temp_git_repo, capture_output=True, text=True, timeout=10
                )

                # Should handle missing validator gracefully (not crash)
                # May return error code, but should not have unhandled exceptions
                assert (
                    "Traceback" not in result.stderr
                ), f"Hook {hook_name} crashed with unhandled exception"

                # Should provide meaningful error message
                error_output = result.stderr + result.stdout
                meaningful_error = any(
                    keyword in error_output.lower()
                    for keyword in [
                        "validator",
                        "not found",
                        "missing",
                        "error",
                        "constitutional",
                    ]
                )
                assert (
                    meaningful_error
                ), f"Hook {hook_name} should provide meaningful error message"

            except subprocess.TimeoutExpired:
                pytest.fail(f"Hook {hook_name} timed out during error handling")
            except FileNotFoundError:
                # Skip if interpreter not available
                continue


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
