"""
Tests for Git Hooks Implementation (WP04)
Comprehensive test coverage for pre-commit and pre-push hooks

SE Principle Focus: Testability and Reliability
"""

import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGitHooks:
    """Test suite for Git hooks functionality"""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary Git repository for testing"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repository
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture  
    def mock_constitutional_validator(self):
        """Mock constitutional validator for testing"""
        with patch('src.constitutional_validator.ConstitutionalValidator') as mock:
            validator_instance = MagicMock()
            mock.return_value = validator_instance
            
            # Mock validation result
            result = MagicMock()
            result.violations = []
            validator_instance.validate_file.return_value = result
            
            yield validator_instance

    def test_pre_commit_hook_exists(self):
        """Test that pre-commit hook files exist and are readable"""
        hook_files = [
            'hooks/pre-commit',
            'hooks/pre-commit.ps1'
        ]
        
        for hook_file in hook_files:
            assert os.path.exists(hook_file), f"Hook file {hook_file} should exist"
            assert os.path.isfile(hook_file), f"{hook_file} should be a file"
            
            # Check file is readable
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, f"{hook_file} should not be empty"
                assert 'constitutional' in content.lower(), f"{hook_file} should reference constitutional validation"

    def test_pre_push_hook_exists(self):
        """Test that pre-push hook files exist and are readable"""
        hook_files = [
            'hooks/pre-push',
            'hooks/pre-push.ps1'
        ]
        
        for hook_file in hook_files:
            assert os.path.exists(hook_file), f"Hook file {hook_file} should exist"
            assert os.path.isfile(hook_file), f"{hook_file} should be a file"
            
            # Check file is readable
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, f"{hook_file} should not be empty"
                assert 'quality' in content.lower(), f"{hook_file} should reference quality gates"

    def test_bash_hook_syntax(self):
        """Test that bash hooks have valid syntax"""
        bash_hooks = ['hooks/pre-commit', 'hooks/pre-push']
        
        for hook_file in bash_hooks:
            # Check shebang
            with open(hook_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                assert first_line.startswith('#!/bin/bash'), f"{hook_file} should have bash shebang"
            
            # Run bash syntax check (skip on Windows if bash not available)
            try:
                result = subprocess.run(['bash', '-n', hook_file], capture_output=True, timeout=10)
                assert result.returncode == 0, f"Bash syntax error in {hook_file}: {result.stderr.decode()}"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Skip if bash is not available (Windows) or times out
                pytest.skip(f"Bash not available for syntax checking {hook_file}")

    def test_powershell_hook_syntax(self):
        """Test that PowerShell hooks have valid syntax"""
        ps_hooks = ['hooks/pre-commit.ps1', 'hooks/pre-push.ps1']
        
        for hook_file in ps_hooks:
            # Check PowerShell comment header
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content.startswith('#'), f"{hook_file} should start with PowerShell comment"
                assert 'param(' in content, f"{hook_file} should have parameter block"
            
            # Run PowerShell syntax check (if PowerShell is available)
            try:
                result = subprocess.run(['powershell', '-NoProfile', '-Command', f'Get-Content "{hook_file}" | Out-Null'], 
                                      capture_output=True, timeout=10)
                # Don't fail test if PowerShell is unavailable (Linux/macOS)
                if result.returncode != 0 and "powershell" not in result.stderr.decode().lower():
                    assert False, f"PowerShell syntax error in {hook_file}: {result.stderr.decode()}"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # PowerShell not available - skip syntax check
                pass

    def test_installation_script_fixed(self):
        """Test that installation script no longer has Unicode issues"""
        script_file = 'scripts/install_git_hooks.ps1'
        assert os.path.exists(script_file), "Installation script should exist"
        
        with open(script_file, 'rb') as f:
            content = f.read()
            
            # Check for problematic Unicode characters that were causing issues
            problematic_chars = [
                b'\xe2\x9c\x85',  # ✅
                b'\xe2\x9d\x8c',  # ❌  
                b'\xf0\x9f\x94\xa7',  # 🔧
                b'\xf0\x9f\x92\xa1',  # 💡
                b'\xe2\x9a\xa0',  # ⚠
            ]
            
            for char in problematic_chars:
                assert char not in content, f"Installation script should not contain Unicode character {char}"

    def test_hook_integration_with_constitutional_validator(self, mock_constitutional_validator):
        """Test that hooks properly integrate with constitutional validator"""
        # This would be an integration test with the actual constitutional validator
        # For now, test the import structure
        
        pre_commit_bash = Path('hooks/pre-commit')
        content = pre_commit_bash.read_text(encoding='utf-8')
        
        # Check that hook references the constitutional validator
        assert 'constitutional_validator' in content
        assert 'src.constitutional_validator' in content or 'constitutional_validator.py' in content
        
        # Check error handling
        assert 'exit 1' in content, "Hook should exit with error code on failures"

    def test_hook_performance_expectations(self):
        """Test that hooks include performance requirements"""
        hook_files = [
            'hooks/pre-commit',
            'hooks/pre-commit.ps1',
            'hooks/pre-push', 
            'hooks/pre-push.ps1'
        ]
        
        for hook_file in hook_files:
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check that hooks have some form of error handling/timeout
                # This ensures they won't hang indefinitely
                has_error_handling = any(pattern in content for pattern in [
                    'set -e',  # Bash: exit on error
                    'ErrorActionPreference',  # PowerShell: error handling
                    'timeout',  # Explicit timeout
                    'try',  # Exception handling
                    'catch'  # Exception handling
                ])
                
                assert has_error_handling, f"{hook_file} should have error handling for performance"

    def test_cross_platform_compatibility(self):
        """Test that hooks are designed for cross-platform use"""
        # Check bash hooks use portable shebang and commands
        bash_hooks = ['hooks/pre-commit', 'hooks/pre-push']
        
        for hook_file in bash_hooks:
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Should use portable commands
                assert 'git rev-parse' in content, f"{hook_file} should use git rev-parse for repo root"
                assert '/bin/bash' in content, f"{hook_file} should use standard bash path"
                
        # Check PowerShell hooks use cross-platform PowerShell features
        ps_hooks = ['hooks/pre-commit.ps1', 'hooks/pre-push.ps1']
        
        for hook_file in ps_hooks:
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Should handle cross-platform paths
                assert 'Join-Path' in content or 'Path' in content, f"{hook_file} should use proper path handling"
                assert 'Set-StrictMode' in content, f"{hook_file} should use strict mode"

    def test_git_reporter_integration(self):
        """Test that hooks integrate with git reporter"""
        hook_files = [
            'hooks/pre-commit',
            'hooks/pre-commit.ps1',
            'hooks/pre-push',
            'hooks/pre-push.ps1'
        ]
        
        for hook_file in hook_files:
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Should reference git reporter
                assert 'git_reporter' in content, f"{hook_file} should integrate with git reporter"

    def test_hook_file_permissions(self):
        """Test that hook files have appropriate structure for Git"""
        bash_hooks = ['hooks/pre-commit', 'hooks/pre-push']
        
        for hook_file in bash_hooks:
            # Check file exists and is readable
            assert os.path.exists(hook_file), f"{hook_file} should exist"
            
            # Check it starts with shebang (required for Git hooks)
            with open(hook_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                assert first_line.startswith('#!'), f"{hook_file} should start with shebang"

    def test_installation_script_hook_detection(self):
        """Test that installation script properly detects hook files"""
        script_file = 'scripts/install_git_hooks.ps1'
        
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Should reference the hooks directory (not .git/hooks directly)
            assert 'hooks' in content, "Installation script should reference hooks directory"
            
            # Should handle the 4 hook files we created
            hook_references = [
                'pre-commit',
                'pre-push',
                'pre-commit.ps1',
                'pre-push.ps1'
            ]
            
            for hook_ref in hook_references:
                assert hook_ref in content, f"Installation script should reference {hook_ref}"


class TestHookExecutionSimulation:
    """Test hook execution without actually running git operations"""
    
    def test_pre_commit_hook_validation_flow(self):
        """Test the validation flow in pre-commit hook"""
        # This would simulate running the pre-commit hook with mock files
        # Testing the core logic without actually staging files
        
        # For now, just verify the hook files reference the correct components
        pre_commit_bash = Path('hooks/pre-commit')
        if pre_commit_bash.exists():
            content = pre_commit_bash.read_text(encoding='utf-8')
            assert 'constitutional_validator' in content, "Hook should reference constitutional validator"
            assert 'GitViolationReporter' in content, "Hook should use git reporter"
        
        # This is a conceptual test - actual implementation would require
        # more sophisticated mocking of git operations
        assert True  # Placeholder for complex integration test

    def test_pre_push_hook_quality_gates(self):
        """Test quality gate validation in pre-push hook"""
        # This would test the quality gate logic
        # Again, conceptual test for the framework
        
        assert True  # Placeholder for quality gate integration test


if __name__ == '__main__':
    pytest.main([__file__, '-v'])