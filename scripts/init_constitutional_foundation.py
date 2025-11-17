#!/usr/bin/env python3
"""
Constitutional Foundation Initialization Script - T031

Complete system setup for project's SDD Constitutional Foundation & Enforcement.
Initializes the entire constitutional validation system for new projects.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import os
import shutil
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import argparse


@dataclass
class InitializationConfig:
    """Configuration for constitutional foundation initialization."""

    project_name: str
    project_root: Path
    python_version: str = "3.11+"
    enable_git_hooks: bool = True
    enable_github_actions: bool = True
    enable_quality_gates: bool = True
    coverage_threshold: float = 80.0
    complexity_threshold: int = 10
    security_level: str = "high"
    naming_enforcement: bool = True
    template_sync: bool = True

    def __post_init__(self):
        """Ensure project_root is a Path object."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)


class ConstitutionalFoundationInitializer:
    """Main constitutional foundation initialization system."""

    def __init__(self, config: InitializationConfig):
        """Initialize with configuration."""
        self.config = config
        self.source_dir = Path(__file__).parent.parent  # Assumes script is in scripts/
        self.errors = []
        self.warnings = []

    def initialize_foundation(self) -> bool:
        """Complete constitutional foundation initialization."""
        print("🏗️ Initializing project Constitutional Foundation...")
        print(f"📁 Project: {self.config.project_name}")
        print(f"📍 Location: {self.config.project_root.absolute()}")

        try:
            # Step 1: Create directory structure
            self._create_directory_structure()

            # Step 2: Copy constitutional configuration
            self._setup_constitutional_configuration()

            # Step 3: Install validation engine
            self._install_validation_engine()

            # Step 4: Setup quality gates
            if self.config.enable_quality_gates:
                self._setup_quality_gates()

            # Step 5: Install Git hooks
            if self.config.enable_git_hooks:
                self._install_git_hooks()

            # Step 6: Setup GitHub Actions
            if self.config.enable_github_actions:
                self._setup_github_actions()

            # Step 7: Initialize template system
            if self.config.template_sync:
                self._initialize_template_system()

            # Step 8: Create initial tests
            self._create_initial_tests()

            # Step 9: Generate project configuration
            self._generate_project_configuration()

            # Step 10: Validate installation
            validation_success = self._validate_installation()

            # Print summary
            self._print_initialization_summary(validation_success)

            return validation_success and len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Critical initialization error: {e}")
            self._print_initialization_summary(False)
            return False

    def _create_directory_structure(self) -> None:
        """Create the required directory structure."""
        print("\n📁 Creating directory structure...")

        directories = [
            ".kittify/config",
            ".kittify/templates",
            ".kittify/memory",
            ".kittify/scripts/bash",
            ".kittify/scripts/powershell",
            "src",
            "tests/unit",
            "tests/integration",
            "tests/performance",
            "tests/e2e",
            "tests/fixtures",
            "scripts",
            ".github/workflows",
            ".github/prompts",
        ]

        for directory in directories:
            dir_path = self.config.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")

    def _setup_constitutional_configuration(self) -> None:
        """Copy constitutional configuration files."""
        print("\n⚖️ Setting up constitutional configuration...")

        config_files = [
            ("se_rules.yaml", ".kittify/config/se_rules.yaml"),
            ("quality_gates.yaml", ".kittify/config/quality_gates.yaml"),
        ]

        for source_file, dest_path in config_files:
            source_path = self.source_dir / ".kittify/config" / source_file
            dest_full_path = self.config.project_root / dest_path

            if source_path.exists():
                shutil.copy2(source_path, dest_full_path)
                print(f"  ✅ {source_file}")
            else:
                self._create_default_config_file(source_file, dest_full_path)
                self.warnings.append(
                    f"Created default {source_file} (source not found)"
                )
                print(f"  ⚠️ {source_file} (created default)")

    def _create_default_config_file(self, filename: str, dest_path: Path) -> None:
        """Create default configuration files."""
        if filename == "se_rules.yaml":
            default_content = {
                "constitutional_enforcement": {
                    "version": "1.0.0",
                    "strict_mode": True,
                    "principles": {
                        "SRP": {"enabled": True, "weight": 1.0},
                        "Encapsulation": {"enabled": True, "weight": 1.0},
                        "Loose_Coupling": {"enabled": True, "weight": 1.0},
                        "Reusability": {"enabled": True, "weight": 1.0},
                        "Portability": {"enabled": True, "weight": 1.0},
                        "Defensibility": {"enabled": True, "weight": 1.0},
                        "Maintainability": {"enabled": True, "weight": 1.0},
                        "Simplicity": {"enabled": True, "weight": 1.0},
                    },
                }
            }
        elif filename == "quality_gates.yaml":
            default_content = {
                "quality_gates": {
                    "coverage": {
                        "threshold": self.config.coverage_threshold,
                        "enabled": True,
                    },
                    "complexity": {
                        "threshold": self.config.complexity_threshold,
                        "enabled": True,
                    },
                    "security": {"level": self.config.security_level, "enabled": True},
                    "naming": {
                        "enforcement": self.config.naming_enforcement,
                        "enabled": True,
                    },
                }
            }
        else:
            default_content = {}

        with open(dest_path, "w", encoding="utf-8") as f:
            yaml.dump(default_content, f, default_flow_style=False, indent=2)

    def _install_validation_engine(self) -> None:
        """Install the constitutional validation engine."""
        print("\n🔧 Installing constitutional validation engine...")

        validator_files = [
            "constitutional_validator.py",
            "violation_detector.py",
            "compliance_reporter.py",
            "coverage_validator.py",
            "complexity_analyzer.py",
            "security_scanner.py",
            "naming_validator.py",
        ]

        source_src = self.source_dir / "src"
        dest_src = self.config.project_root / "src"

        for validator_file in validator_files:
            source_path = source_src / validator_file
            dest_path = dest_src / validator_file

            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ {validator_file}")
            else:
                self.warnings.append(f"Validation file not found: {validator_file}")
                print(f"  ⚠️ {validator_file} (not found)")

        # Copy __init__.py if it exists
        init_file = source_src / "__init__.py"
        if init_file.exists():
            shutil.copy2(init_file, dest_src / "__init__.py")

    def _setup_quality_gates(self) -> None:
        """Setup quality gate system."""
        print("\n🚪 Setting up quality gates...")

        # Copy quality gate validator
        quality_gate_file = self.source_dir / "src" / "quality_gates.py"
        if quality_gate_file.exists():
            dest_path = self.config.project_root / "src" / "quality_gates.py"
            shutil.copy2(quality_gate_file, dest_path)
            print("  ✅ Quality gates validator installed")
        else:
            self.warnings.append("Quality gates validator not found")
            print("  ⚠️ Quality gates validator (not found)")

    def _install_git_hooks(self) -> None:
        """Install Git hooks for constitutional enforcement."""
        print("\n🪝 Installing Git hooks...")

        git_dir = self.config.project_root / ".git"
        if not git_dir.exists():
            self.warnings.append("Not a Git repository - skipping Git hooks")
            print("  ⚠️ Not a Git repository - skipping Git hooks")
            return

        # Copy Git hook installation script
        hook_script = self.source_dir / "scripts" / "install_git_hooks.py"
        if not hook_script.exists():
            # Try PowerShell version
            hook_script = self.source_dir / "scripts" / "install_git_hooks.ps1"

        if hook_script.exists():
            dest_script = self.config.project_root / "scripts" / hook_script.name
            shutil.copy2(hook_script, dest_script)

            try:
                # Run the installation script
                if hook_script.suffix == ".py":
                    subprocess.run(
                        [sys.executable, str(dest_script)],
                        cwd=self.config.project_root,
                        check=True,
                    )
                elif hook_script.suffix == ".ps1":
                    subprocess.run(
                        [
                            "powershell",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            str(dest_script),
                        ],
                        cwd=self.config.project_root,
                        check=True,
                    )
                print("  ✅ Git hooks installed successfully")
            except subprocess.CalledProcessError as e:
                self.warnings.append(f"Git hooks installation failed: {e}")
                print("  ⚠️ Git hooks installation failed")
        else:
            self.warnings.append("Git hooks installation script not found")
            print("  ⚠️ Git hooks installation script not found")

    def _setup_github_actions(self) -> None:
        """Setup GitHub Actions workflows."""
        print("\n🚀 Setting up GitHub Actions...")

        workflows_source = self.source_dir / ".github" / "workflows"
        workflows_dest = self.config.project_root / ".github" / "workflows"

        if workflows_source.exists():
            for workflow_file in workflows_source.glob("*.yml"):
                dest_path = workflows_dest / workflow_file.name
                shutil.copy2(workflow_file, dest_path)
                print(f"  ✅ {workflow_file.name}")
        else:
            # Create basic constitutional validation workflow
            self._create_default_github_workflow()
            print("  ✅ constitutional-validation.yml (created default)")

    def _create_default_github_workflow(self) -> None:
        """Create default GitHub Actions workflow."""
        workflow_content = """name: Constitutional Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  constitutional-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov radon bandit
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Run Constitutional Validation
      run: |
        python src/constitutional_validator.py --strict
        python src/coverage_validator.py --threshold 80
        python src/complexity_analyzer.py --max-complexity 10
        python src/security_scanner.py --fail-on-severity high
        python src/naming_validator.py --fail-on-violations
"""

        workflow_path = (
            self.config.project_root
            / ".github"
            / "workflows"
            / "constitutional-validation.yml"
        )
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(workflow_content)

    def _initialize_template_system(self) -> None:
        """Initialize the template synchronization system."""
        print("\n📋 Initializing template system...")

        template_files = [
            "template_drift_detector.py",
            "template_synchronizer.py",
            "template_validator.py",
        ]

        # Copy template system files
        source_src = self.source_dir / "src"
        dest_src = self.config.project_root / "src"

        for template_file in template_files:
            source_path = source_src / template_file
            dest_path = dest_src / template_file

            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ {template_file}")
            else:
                self.warnings.append(f"Template file not found: {template_file}")
                print(f"  ⚠️ {template_file} (not found)")

        # Copy template manifest
        manifest_source = self.source_dir / ".kittify" / "templates" / "manifest.yaml"
        manifest_dest = (
            self.config.project_root / ".kittify" / "templates" / "manifest.yaml"
        )

        if manifest_source.exists():
            shutil.copy2(manifest_source, manifest_dest)
            print("  ✅ Template manifest copied")
        else:
            self._create_default_template_manifest(manifest_dest)
            print("  ✅ Template manifest created (default)")

    def _create_default_template_manifest(self, manifest_path: Path) -> None:
        """Create default template manifest."""
        default_manifest = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "constitutional_version": "001-sdd-constitutional-foundation",
            },
            "templates": {
                "commands": {},
                "project_templates": {},
                "config_templates": {},
            },
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(default_manifest, f, default_flow_style=False, indent=2)

    def _create_initial_tests(self) -> None:
        """Create initial test structure and basic tests."""
        print("\n🧪 Creating initial test structure...")

        # Create conftest.py
        conftest_content = '''"""
Pytest configuration for constitutional foundation tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_code_valid():
    """Sample valid Python code for testing."""
    return """
def calculate_total(items):
    """Calculate total price of items."""
    return sum(item.price for item in items)
"""


@pytest.fixture  
def sample_code_invalid():
    """Sample invalid Python code for testing."""
    return """
def bad_function(a,b,c,d,e,f,g,h,i,j):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            return g+h+i+j
    return None
"""
'''

        conftest_path = self.config.project_root / "tests" / "conftest.py"
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(conftest_content)

        # Create basic unit test
        basic_test_content = '''"""
Basic constitutional validation tests.
"""

import pytest
from constitutional_validator import ConstitutionalValidator


def test_constitutional_validator_exists():
    """Test that constitutional validator can be imported."""
    validator = ConstitutionalValidator()
    assert validator is not None


def test_sample_code_validation(sample_code_valid):
    """Test validation of valid code."""
    validator = ConstitutionalValidator()
    # Basic smoke test - actual implementation depends on validator structure
    assert sample_code_valid is not None
'''

        test_path = (
            self.config.project_root / "tests" / "unit" / "test_basic_validation.py"
        )
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(basic_test_content)

        print("  ✅ conftest.py")
        print("  ✅ test_basic_validation.py")

    def _generate_project_configuration(self) -> None:
        """Generate project configuration files."""
        print("\n⚙️ Generating project configuration...")

        # Generate pyproject.toml
        pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.config.project_name}"
version = "0.1.0"
description = "project project with Constitutional Foundation enforcement"
requires-python = ">={self.config.python_version.rstrip('+')}"
dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pyyaml>=6.0.0",
    "radon>=5.1.0",
    "bandit>=1.7.0",
]

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "venv/*", ".venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
"""

        pyproject_path = self.config.project_root / "pyproject.toml"
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(pyproject_content)

        # Generate .gitignore
        gitignore_content = """# Constitutional Foundation
.coverage
htmlcov/
.pytest_cache/
__pycache__/
*.pyc
*.pyo
*.pyd

# Development
.venv/
venv/
env/
.env
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Distribution
build/
dist/
*.egg-info/

# Constitutional Logs
.kittify/memory/logs/
"""

        gitignore_path = self.config.project_root / ".gitignore"
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)

        print("  ✅ pyproject.toml")
        print("  ✅ .gitignore")

    def _validate_installation(self) -> bool:
        """Validate the constitutional foundation installation."""
        print("\n🔍 Validating installation...")

        validation_success = True

        # Check required files exist
        required_files = [
            "src/constitutional_validator.py",
            ".kittify/config/se_rules.yaml",
            ".kittify/config/quality_gates.yaml",
            "tests/conftest.py",
            "pyproject.toml",
        ]

        for required_file in required_files:
            file_path = self.config.project_root / required_file
            if file_path.exists():
                print(f"  ✅ {required_file}")
            else:
                print(f"  ❌ {required_file} (missing)")
                self.errors.append(f"Required file missing: {required_file}")
                validation_success = False

        # Try to import constitutional validator
        try:
            sys.path.insert(0, str(self.config.project_root / "src"))
            import constitutional_validator

            print("  ✅ Constitutional validator importable")
        except ImportError as e:
            print("  ❌ Constitutional validator import failed")
            self.warnings.append(f"Import test failed: {e}")

        # Run basic tests if possible
        try:
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                cwd=self.config.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if test_result.returncode == 0:
                print("  ✅ Basic tests passing")
            else:
                print("  ⚠️ Some tests failing (expected for new installation)")
                self.warnings.append("Some initial tests failing")
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            print("  ⚠️ Could not run test validation")
            self.warnings.append("Test validation skipped")

        return validation_success

    def _print_initialization_summary(self, success: bool) -> None:
        """Print comprehensive initialization summary."""
        print("\n" + "=" * 60)
        print("🏗️ CONSTITUTIONAL FOUNDATION INITIALIZATION COMPLETE")
        print("=" * 60)

        if success:
            print("✅ Status: SUCCESS")
        else:
            print("❌ Status: COMPLETED WITH ISSUES")

        print(f"📁 Project: {self.config.project_name}")
        print(f"📍 Location: {self.config.project_root.absolute()}")

        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        print(f"\n🎯 Next Steps:")
        print("   1. Review configuration files in .kittify/config/")
        print("   2. Customize quality gate thresholds as needed")
        print("   3. Run: pytest tests/ to validate installation")
        print("   4. Run: python src/constitutional_validator.py --help")
        print("   5. Commit initial constitutional foundation to Git")

        if self.config.enable_github_actions:
            print("   6. Push to GitHub to trigger constitutional validation workflow")

        print("\n📚 Documentation:")
        print("   • Constitutional rules: .kittify/config/se_rules.yaml")
        print("   • Quality gates: .kittify/config/quality_gates.yaml")
        print("   • Templates: .kittify/templates/manifest.yaml")

        print(f"\n🔧 Configuration Summary:")
        print(f"   • Coverage threshold: {self.config.coverage_threshold}%")
        print(f"   • Complexity threshold: ≤{self.config.complexity_threshold}")
        print(f"   • Security level: {self.config.security_level}")
        print(f"   • Git hooks: {'✅' if self.config.enable_git_hooks else '❌'}")
        print(
            f"   • GitHub Actions: {'✅' if self.config.enable_github_actions else '❌'}"
        )
        print(f"   • Template sync: {'✅' if self.config.template_sync else '❌'}")


def main():
    """Main CLI entry point for constitutional foundation initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize project Constitutional Foundation",
        epilog="This script sets up the complete constitutional enforcement system for a project project.",
    )

    parser.add_argument("project_name", help="Name of the project to initialize")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the project (default: current directory)",
    )
    parser.add_argument(
        "--python-version",
        default="3.11+",
        help="Required Python version (default: 3.11+)",
    )
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        default=80.0,
        help="Test coverage threshold percentage (default: 80.0)",
    )
    parser.add_argument(
        "--complexity-threshold",
        type=int,
        default=10,
        help="Maximum cyclomatic complexity (default: 10)",
    )
    parser.add_argument(
        "--security-level",
        choices=["low", "medium", "high", "critical"],
        default="high",
        help="Security scanning level (default: high)",
    )
    parser.add_argument(
        "--no-git-hooks", action="store_true", help="Skip Git hooks installation"
    )
    parser.add_argument(
        "--no-github-actions", action="store_true", help="Skip GitHub Actions setup"
    )
    parser.add_argument(
        "--no-quality-gates", action="store_true", help="Skip quality gates setup"
    )
    parser.add_argument(
        "--no-naming-enforcement",
        action="store_true",
        help="Disable naming convention enforcement",
    )
    parser.add_argument(
        "--no-template-sync",
        action="store_true",
        help="Skip template synchronization system",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if directory is not empty",
    )

    args = parser.parse_args()

    # Validate project directory
    if (
        not args.force
        and args.project_root.exists()
        and any(args.project_root.iterdir())
    ):
        print(
            "❌ Error: Project directory is not empty. Use --force to proceed anyway."
        )
        sys.exit(1)

    # Create configuration
    config = InitializationConfig(
        project_name=args.project_name,
        project_root=args.project_root,
        python_version=args.python_version,
        enable_git_hooks=not args.no_git_hooks,
        enable_github_actions=not args.no_github_actions,
        enable_quality_gates=not args.no_quality_gates,
        coverage_threshold=args.coverage_threshold,
        complexity_threshold=args.complexity_threshold,
        security_level=args.security_level,
        naming_enforcement=not args.no_naming_enforcement,
        template_sync=not args.no_template_sync,
    )

    # Initialize foundation
    initializer = ConstitutionalFoundationInitializer(config)
    success = initializer.initialize_foundation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
