#!/usr/bin/env python3
"""
Unit Testing Infrastructure - T035

Comprehensive unit testing framework for constitutional enforcement components.
Provides test fixtures, mocks, and utilities for testing all quality gates and validators.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import os
import sys
import pytest
import unittest
import yaml
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from unittest.mock import Mock, patch, MagicMock
import subprocess
import ast


@dataclass
class TestFixture:
    """Base class for test fixtures."""

    name: str
    description: str
    data: Any
    cleanup_functions: List[Callable] = field(default_factory=list)

    def cleanup(self):
        """Clean up fixture resources."""
        for cleanup_func in self.cleanup_functions:
            try:
                cleanup_func()
            except Exception as e:
                print(f"⚠️ Cleanup warning for {self.name}: {e}")


class ConstitutionalTestFramework:
    """Main testing framework for constitutional components."""

    def __init__(self, test_data_dir: Optional[Path] = None):
        """Initialize testing framework."""
        self.test_data_dir = (
            test_data_dir or Path(__file__).parent.parent / "tests" / "fixtures"
        )
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

        self.fixtures: Dict[str, TestFixture] = {}
        self.temp_dirs: List[Path] = []

        # Initialize test data
        self._create_test_fixtures()

    def _create_test_fixtures(self):
        """Create standard test fixtures."""
        self._create_code_fixtures()
        self._create_config_fixtures()
        self._create_file_fixtures()
        self._create_project_fixtures()

    def _create_code_fixtures(self):
        """Create code sample fixtures for testing."""

        # Valid Python code samples
        valid_python_simple = '''
def calculate_total(items):
    """Calculate total price of items."""
    return sum(item.price for item in items)

class ShoppingCart:
    """Simple shopping cart implementation."""
    
    def __init__(self):
        self._items = []
    
    def add_item(self, item):
        """Add item to cart."""
        if item is None:
            raise ValueError("Item cannot be None")
        self._items.append(item)
    
    def get_total(self):
        """Get total cart value."""
        return sum(item.price for item in self._items)
'''

        valid_python_complex = '''
class UserManager:
    """Manages user operations with proper encapsulation."""
    
    def __init__(self, database):
        self._database = database
        self._cache = {}
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID with caching."""
        if user_id in self._cache:
            return self._cache[user_id]
        
        user = self._database.fetch_user(user_id)
        if user:
            self._cache[user_id] = user
        
        return user
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create new user with validation."""
        self._validate_user_data(user_data)
        
        user = User(**user_data)
        self._database.save_user(user)
        self._cache[user.id] = user
        
        return user
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> None:
        """Validate user data before creation."""
        required_fields = ['name', 'email']
        
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not user_data['email'] or '@' not in user_data['email']:
            raise ValueError("Invalid email address")
'''

        # Invalid Python code samples (violating principles)
        invalid_python_srp = '''
class UserManagerEverything:
    """BAD: Violates SRP by doing too many things."""
    
    def __init__(self):
        self.users = []
        self.emails = []
        self.reports = []
        self.analytics = {}
        self.cache = {}
        self.logs = []
    
    def create_user(self, data):
        # User creation
        user = User(data)
        self.users.append(user)
        
        # Email sending
        self.send_welcome_email(user)
        self.emails.append(f"Welcome {user.name}")
        
        # Report generation
        self.generate_user_report(user)
        self.reports.append(user.id)
        
        # Analytics tracking
        self.track_user_creation(user)
        self.analytics[user.id] = {"created": datetime.now()}
        
        # Caching
        self.cache[user.id] = user
        
        # Logging
        self.log_user_creation(user)
        self.logs.append(f"User {user.id} created")
        
        # File operations
        self.save_user_to_file(user)
        
        # Database operations
        self.save_to_database(user)
        
        # Notification sending
        self.send_notifications(user)
        
        return user
    
    def send_welcome_email(self, user): pass
    def generate_user_report(self, user): pass
    def track_user_creation(self, user): pass
    def log_user_creation(self, user): pass
    def save_user_to_file(self, user): pass
    def save_to_database(self, user): pass
    def send_notifications(self, user): pass
'''

        invalid_python_complexity = '''
def process_user_data(data):
    """BAD: Extremely complex function violating simplicity."""
    if data:
        if isinstance(data, dict):
            if 'users' in data:
                if len(data['users']) > 0:
                    for user in data['users']:
                        if user:
                            if 'profile' in user:
                                if user['profile']:
                                    if 'settings' in user['profile']:
                                        if user['profile']['settings']:
                                            if 'preferences' in user['profile']['settings']:
                                                if user['profile']['settings']['preferences']:
                                                    if 'notifications' in user['profile']['settings']['preferences']:
                                                        if user['profile']['settings']['preferences']['notifications']:
                                                            if user['profile']['settings']['preferences']['notifications'].get('email'):
                                                                return process_email_notifications(user)
                                                            elif user['profile']['settings']['preferences']['notifications'].get('sms'):
                                                                return process_sms_notifications(user)
                                                            else:
                                                                return process_default_notifications(user)
    return None
'''

        # JavaScript/TypeScript samples
        valid_javascript = """
class TaskManager {
    constructor() {
        this._tasks = [];
        this._completed = [];
    }
    
    addTask(task) {
        if (!task || !task.title) {
            throw new Error('Task must have a title');
        }
        
        this._tasks.push({
            id: Date.now(),
            title: task.title,
            description: task.description || '',
            created: new Date()
        });
    }
    
    completeTask(taskId) {
        const taskIndex = this._tasks.findIndex(t => t.id === taskId);
        if (taskIndex === -1) {
            throw new Error('Task not found');
        }
        
        const task = this._tasks.splice(taskIndex, 1)[0];
        task.completed = new Date();
        this._completed.push(task);
        
        return task;
    }
    
    getTasks() {
        return [...this._tasks]; // Return copy to maintain encapsulation
    }
}
"""

        # Store fixtures
        self.fixtures["valid_python_simple"] = TestFixture(
            name="valid_python_simple",
            description="Simple valid Python code following SE principles",
            data=valid_python_simple,
        )

        self.fixtures["valid_python_complex"] = TestFixture(
            name="valid_python_complex",
            description="Complex but valid Python code following SE principles",
            data=valid_python_complex,
        )

        self.fixtures["invalid_python_srp"] = TestFixture(
            name="invalid_python_srp",
            description="Python code violating Single Responsibility Principle",
            data=invalid_python_srp,
        )

        self.fixtures["invalid_python_complexity"] = TestFixture(
            name="invalid_python_complexity",
            description="Python code with excessive complexity",
            data=invalid_python_complexity,
        )

        self.fixtures["valid_javascript"] = TestFixture(
            name="valid_javascript",
            description="Valid JavaScript code following SE principles",
            data=valid_javascript,
        )

    def _create_config_fixtures(self):
        """Create configuration fixtures for testing."""

        # SE Rules configuration
        se_rules_config = {
            "constitutional_enforcement": {
                "version": "1.0.0",
                "strict_mode": True,
                "violation_threshold": "medium",
                "principles": {
                    "SRP": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {
                            "max_methods_per_class": 10,
                            "max_lines_per_function": 50,
                            "max_responsibilities": 1,
                        },
                    },
                    "Maintainability": {
                        "enabled": True,
                        "weight": 1.0,
                        "metrics": {
                            "max_complexity": 10,
                            "min_documentation_ratio": 0.2,
                        },
                    },
                },
            }
        }

        # Quality Gates configuration
        quality_gates_config = {
            "quality_gates": {
                "version": "1.0.0",
                "enforcement_mode": "strict",
                "gates": {
                    "coverage": {
                        "enabled": True,
                        "threshold": 80.0,
                        "fail_under": True,
                    },
                    "complexity": {
                        "enabled": True,
                        "max_complexity": 10,
                        "fail_on_violation": True,
                    },
                    "security": {
                        "enabled": True,
                        "severity_threshold": "high",
                        "fail_on_critical": True,
                    },
                },
            }
        }

        # Naming conventions
        naming_conventions_config = {
            "naming_conventions": {
                "version": "1.0.0",
                "enforcement_level": "strict",
                "languages": {
                    "python": {
                        "functions": "snake_case",
                        "variables": "snake_case",
                        "classes": "PascalCase",
                        "constants": "UPPER_SNAKE_CASE",
                    },
                    "javascript": {
                        "functions": "camelCase",
                        "variables": "camelCase",
                        "classes": "PascalCase",
                        "constants": "UPPER_SNAKE_CASE",
                    },
                },
            }
        }

        # Store config fixtures
        self.fixtures["se_rules_config"] = TestFixture(
            name="se_rules_config",
            description="Standard SE rules configuration",
            data=se_rules_config,
        )

        self.fixtures["quality_gates_config"] = TestFixture(
            name="quality_gates_config",
            description="Quality gates configuration",
            data=quality_gates_config,
        )

        self.fixtures["naming_conventions_config"] = TestFixture(
            name="naming_conventions_config",
            description="Naming conventions configuration",
            data=naming_conventions_config,
        )

    def _create_file_fixtures(self):
        """Create file system fixtures for testing."""

        # Test project structure
        project_structure = {
            "src/": {
                "main.py": self.fixtures["valid_python_simple"].data,
                "user_manager.py": self.fixtures["valid_python_complex"].data,
                "bad_code.py": self.fixtures["invalid_python_srp"].data,
                "utils/": {
                    "__init__.py": "",
                    "helpers.py": 'def format_date(date): return date.strftime("%Y-%m-%d")',
                },
            },
            "tests/": {
                "test_main.py": """
import pytest
from src.main import calculate_total

def test_calculate_total():
    items = [Mock(price=10), Mock(price=20)]
    assert calculate_total(items) == 30
                """,
                "__init__.py": "",
            },
            "requirements.txt": "pytest>=7.0.0\npytest-cov>=4.0.0\n",
            "pyproject.toml": """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=src --cov-report=html"
            """,
            ".gitignore": "*.pyc\n__pycache__/\n.coverage\nhtmlcov/\n",
            "README.md": "# Test Project\n\nThis is a test project for constitutional validation.",
        }

        self.fixtures["project_structure"] = TestFixture(
            name="project_structure",
            description="Standard project directory structure",
            data=project_structure,
        )

    def _create_project_fixtures(self):
        """Create complete project fixtures."""

        # Minimal valid project
        minimal_project = {
            "project_name": "minimal-test-project",
            "project_type": "python",
            "files": {
                "main.py": '''
def hello_world():
    """Simple hello world function."""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
                ''',
                "test_main.py": """
from main import hello_world

def test_hello_world():
    assert hello_world() == "Hello, World!"
                """,
            },
            "config": {
                "se_rules": {
                    "SRP": {"enabled": True, "weight": 1.0},
                    "Simplicity": {"enabled": True, "weight": 1.0},
                },
                "quality_gates": {
                    "coverage": {"threshold": 90.0},
                    "complexity": {"max_complexity": 5},
                },
            },
        }

        # Complex project with violations
        complex_project = {
            "project_name": "complex-test-project",
            "project_type": "python",
            "files": {
                "complex_module.py": self.fixtures["invalid_python_complexity"].data,
                "srp_violator.py": self.fixtures["invalid_python_srp"].data,
                "good_code.py": self.fixtures["valid_python_complex"].data,
            },
            "expected_violations": {
                "complexity": ["complex_module.py"],
                "srp": ["srp_violator.py"],
                "naming": [],
            },
        }

        self.fixtures["minimal_project"] = TestFixture(
            name="minimal_project",
            description="Minimal valid project for testing",
            data=minimal_project,
        )

        self.fixtures["complex_project"] = TestFixture(
            name="complex_project",
            description="Complex project with known violations",
            data=complex_project,
        )

    @contextmanager
    def temporary_directory(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(temp_dir)

        try:
            yield temp_dir
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    @contextmanager
    def temporary_project(
        self, project_fixture_name: str
    ) -> Generator[Path, None, None]:
        """Create temporary project from fixture."""
        if project_fixture_name not in self.fixtures:
            raise ValueError(f"Project fixture '{project_fixture_name}' not found")

        project_fixture = self.fixtures[project_fixture_name]
        project_data = project_fixture.data

        with self.temporary_directory() as temp_dir:
            # Create project files
            if "files" in project_data:
                for file_path, content in project_data["files"].items():
                    file_full_path = temp_dir / file_path
                    file_full_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_full_path, "w", encoding="utf-8") as f:
                        f.write(content)

            # Create config files if specified
            if "config" in project_data:
                config_dir = temp_dir / ".kittify" / "config"
                config_dir.mkdir(parents=True, exist_ok=True)

                for config_name, config_data in project_data["config"].items():
                    config_path = config_dir / f"{config_name}.yaml"
                    with open(config_path, "w", encoding="utf-8") as f:
                        yaml.dump(config_data, f, default_flow_style=False, indent=2)

            yield temp_dir

    def create_test_file(self, content: str, suffix: str = ".py") -> Path:
        """Create temporary test file with content."""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        )
        temp_file.write(content)
        temp_file.close()

        temp_path = Path(temp_file.name)

        # Add cleanup function
        def cleanup():
            if temp_path.exists():
                temp_path.unlink()

        # Store for cleanup
        if hasattr(self, "_temp_files"):
            self._temp_files.append(temp_path)
        else:
            self._temp_files = [temp_path]

        return temp_path

    def create_mock_violation_detector(self, violations: List[Dict[str, Any]]) -> Mock:
        """Create mock violation detector with predefined violations."""
        mock_detector = Mock()
        mock_detector.detect_violations.return_value = violations
        mock_detector.get_violation_count.return_value = len(violations)

        return mock_detector

    def create_mock_quality_gate(
        self, should_pass: bool, details: Optional[Dict[str, Any]] = None
    ) -> Mock:
        """Create mock quality gate for testing."""
        mock_gate = Mock()
        mock_gate.validate.return_value = should_pass
        mock_gate.get_details.return_value = details or {}
        mock_gate.get_threshold.return_value = 80.0 if should_pass else 60.0

        return mock_gate

    def assert_violations_detected(
        self, violations: List[Dict[str, Any]], expected_types: List[str]
    ):
        """Assert that specific violation types were detected."""
        detected_types = [v.get("type", "") for v in violations]

        for expected_type in expected_types:
            assert (
                expected_type in detected_types
            ), f"Expected violation type '{expected_type}' not found in {detected_types}"

    def assert_quality_gate_passes(self, gate_result: Dict[str, Any], gate_name: str):
        """Assert that a quality gate passes."""
        assert gate_result.get(
            "passed", False
        ), f"Quality gate '{gate_name}' should pass but failed: {gate_result.get('details', '')}"

    def assert_quality_gate_fails(self, gate_result: Dict[str, Any], gate_name: str):
        """Assert that a quality gate fails."""
        assert not gate_result.get(
            "passed", True
        ), f"Quality gate '{gate_name}' should fail but passed: {gate_result.get('details', '')}"

    def cleanup(self):
        """Clean up all test resources."""
        # Clean up temporary files
        if hasattr(self, "_temp_files"):
            for temp_file in self._temp_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except Exception as e:
                    print(f"⚠️ Failed to clean up temp file {temp_file}: {e}")

        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"⚠️ Failed to clean up temp dir {temp_dir}: {e}")

        # Clean up fixtures
        for fixture in self.fixtures.values():
            fixture.cleanup()


class ConstitutionalTestCase(unittest.TestCase):
    """Base test case for constitutional testing."""

    def setUp(self):
        """Set up test case."""
        self.framework = ConstitutionalTestFramework()
        self.temp_dirs = []

    def tearDown(self):
        """Clean up test case."""
        self.framework.cleanup()

    def get_fixture(self, name: str) -> TestFixture:
        """Get test fixture by name."""
        if name not in self.framework.fixtures:
            raise ValueError(f"Fixture '{name}' not found")
        return self.framework.fixtures[name]

    def create_temp_project(self, fixture_name: str) -> Path:
        """Create temporary project and return path."""
        context_manager = self.framework.temporary_project(fixture_name)
        temp_dir = context_manager.__enter__()

        # Store cleanup function
        def cleanup():
            context_manager.__exit__(None, None, None)

        self.addCleanup(cleanup)
        return temp_dir

    def assert_constitutional_compliance(self, violations: List[Dict[str, Any]]):
        """Assert that code is constitutionally compliant."""
        self.assertEqual(
            len(violations),
            0,
            f"Code should be constitutionally compliant but found violations: {violations}",
        )

    def assert_constitutional_violations(
        self, violations: List[Dict[str, Any]], expected_count: int
    ):
        """Assert specific number of constitutional violations."""
        self.assertEqual(
            len(violations),
            expected_count,
            f"Expected {expected_count} violations but found {len(violations)}: {violations}",
        )


# Pytest fixtures for use with pytest
@pytest.fixture(scope="session")
def constitutional_framework():
    """Pytest fixture for constitutional testing framework."""
    framework = ConstitutionalTestFramework()
    yield framework
    framework.cleanup()


@pytest.fixture
def temp_project(constitutional_framework):
    """Pytest fixture for temporary project."""

    def _create_temp_project(fixture_name: str):
        return constitutional_framework.temporary_project(fixture_name)

    return _create_temp_project


@pytest.fixture
def sample_code(constitutional_framework):
    """Pytest fixture for sample code."""

    def _get_sample_code(fixture_name: str):
        return constitutional_framework.fixtures[fixture_name].data

    return _get_sample_code


@pytest.fixture
def mock_components():
    """Pytest fixture for mock components."""

    class MockComponents:
        def __init__(self):
            self.violation_detector = Mock()
            self.quality_gates = Mock()
            self.naming_validator = Mock()
            self.complexity_analyzer = Mock()
            self.security_scanner = Mock()
            self.coverage_validator = Mock()

        def reset_mocks(self):
            """Reset all mocks."""
            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if isinstance(attr, Mock):
                    attr.reset_mock()

    return MockComponents()


# Test utilities
def run_constitutional_validation(code: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Run constitutional validation on code sample."""
    # This would integrate with actual validators
    # For now, return mock results
    return {
        "passed": True,
        "violations": [],
        "metrics": {"complexity": 5, "coverage": 85.0, "security_issues": 0},
    }


def create_violation(
    violation_type: str, severity: str, file_path: str, line_number: int, message: str
) -> Dict[str, Any]:
    """Create a violation dictionary for testing."""
    return {
        "type": violation_type,
        "severity": severity,
        "file_path": file_path,
        "line_number": line_number,
        "message": message,
        "rule": f"{violation_type}_rule",
        "detected_at": datetime.utcnow().isoformat() + "Z",
    }


def assert_file_exists(file_path: Path, message: str = ""):
    """Assert that file exists."""
    assert file_path.exists(), f"File should exist: {file_path}. {message}"


def assert_file_contains(file_path: Path, content: str, message: str = ""):
    """Assert that file contains specific content."""
    assert file_path.exists(), f"File should exist: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    assert content in file_content, f"File should contain '{content}'. {message}"


def assert_directory_structure(base_path: Path, expected_structure: Dict[str, Any]):
    """Assert that directory has expected structure."""
    for item_name, item_content in expected_structure.items():
        item_path = base_path / item_name

        if isinstance(item_content, dict):
            # It's a directory
            assert item_path.is_dir(), f"Should be directory: {item_path}"
            assert_directory_structure(item_path, item_content)
        else:
            # It's a file
            assert item_path.is_file(), f"Should be file: {item_path}"


if __name__ == "__main__":
    # Example usage
    framework = ConstitutionalTestFramework()

    print("🧪 Constitutional Testing Framework Initialized")
    print(f"📁 Test data directory: {framework.test_data_dir}")
    print(f"🔧 Available fixtures: {len(framework.fixtures)}")

    for fixture_name, fixture in framework.fixtures.items():
        print(f"  • {fixture_name}: {fixture.description}")

    # Demonstrate temporary project creation
    print("\n🏗️ Creating temporary project...")
    with framework.temporary_project("minimal_project") as project_dir:
        print(f"📍 Temporary project created at: {project_dir}")

        # List files in project
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                print(f"  📄 {file_path.relative_to(project_dir)}")

    print("🧹 Cleaning up...")
    framework.cleanup()
    print("✅ Unit testing infrastructure ready!")
