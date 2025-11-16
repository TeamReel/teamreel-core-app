"""
Unit tests for PlanValidator class.

Tests implementation plan validation against constitutional requirements.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys
import yaml

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plan_validator import PlanValidator, PlanValidationCategory, ValidationLevel
from compliance_reporter import Violation


class TestPlanValidator:
    """Test cases for PlanValidator class."""

    def test_initialization(self):
        """Test PlanValidator initialization."""
        validator = PlanValidator()

        assert validator is not None
        assert hasattr(validator, "constitutional_validator")

    def test_validate_plan_complete_architecture(self):
        """Test validating a plan with complete architectural design."""
        plan_content = """
# Implementation Plan: User Authentication System

## Technical Architecture

### System Components
- **Authentication Service**: Handles user login/logout
- **User Management Service**: Manages user profiles  
- **Security Service**: Handles password hashing and validation

### Data Models
- **User**: id, email, password_hash, created_at
- **Session**: id, user_id, token, expires_at

### API Endpoints
- POST /auth/login - User authentication
- POST /auth/logout - Session termination
- GET /auth/profile - User profile retrieval

## SE Principles Architecture Compliance

### Single Responsibility Principle
- Authentication service only handles auth logic
- User service only manages user data
- Security service only handles encryption/hashing

### Encapsulation
- Password hashing implementation hidden behind security service interface
- Database access abstracted through repository pattern

### Loose Coupling  
- Services communicate through defined interfaces
- No direct database dependencies in business logic

## Quality Gates Integration

### Testing Strategy
- Unit tests: 80% coverage minimum
- Integration tests: API endpoint validation
- Security tests: Authentication flow validation

### Code Quality
- Complexity analysis: Cyclomatic complexity < 10
- Security scanning: No hardcoded credentials
- Naming conventions: snake_case for Python, camelCase for frontend

## Implementation Tasks

### Phase 1: Core Authentication
- [ ] T001: Create User model and database schema
- [ ] T002: Implement password hashing service
- [ ] T003: Create authentication API endpoints

### Phase 2: Session Management  
- [ ] T004: Implement session token generation
- [ ] T005: Create session validation middleware
- [ ] T006: Add logout functionality
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_content)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            assert hasattr(report, "issues")
            assert hasattr(report, "is_valid")

        finally:
            os.unlink(plan_path)

    def test_validate_plan_missing_architecture(self):
        """Test validating a plan missing technical architecture."""
        incomplete_plan = """
# Implementation Plan: Incomplete Feature

## Some Section
Just some basic content without proper architecture sections.

## Implementation Tasks
- [ ] T001: Do something
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(incomplete_plan)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            assert not report.is_valid
            assert len(report.issues) > 0

            # Should flag missing architecture sections
            issue_messages = [issue.message for issue in report.issues]
            assert any("architecture" in msg.lower() for msg in issue_messages)

        finally:
            os.unlink(plan_path)

    def test_validate_plan_missing_se_principles(self):
        """Test validating a plan missing SE principles compliance."""
        plan_without_se = """
# Implementation Plan: No SE Principles

## Technical Architecture

### System Components
- Component 1: Does something
- Component 2: Does something else

## Implementation Tasks
- [ ] T001: Implement feature
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_without_se)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            assert not report.is_valid

            # Should flag missing SE principles section
            issue_messages = [issue.message for issue in report.issues]
            assert any("SE Principles" in msg for msg in issue_messages)

        finally:
            os.unlink(plan_path)

    def test_validate_plan_missing_quality_gates(self):
        """Test validating a plan missing quality gates integration."""
        plan_without_gates = """
# Implementation Plan: No Quality Gates

## Technical Architecture

### System Components
- Component 1: Handles feature A

## SE Principles Architecture Compliance

### Single Responsibility Principle
- Components have single responsibilities

## Implementation Tasks
- [ ] T001: Do something
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_without_gates)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            # Should warn about missing quality gates

        finally:
            os.unlink(plan_path)

    def test_validate_plan_incomplete_tasks(self):
        """Test validating a plan with incomplete task breakdown."""
        plan_bad_tasks = """
# Implementation Plan: Bad Tasks

## Technical Architecture
Basic architecture

## SE Principles Architecture Compliance  
Basic compliance

## Implementation Tasks
- Do something (not properly formatted)
- Another task without ID
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_bad_tasks)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            # Should identify task formatting issues

        finally:
            os.unlink(plan_path)

    def test_validate_plan_nonexistent_file(self):
        """Test validating a nonexistent plan file."""
        validator = PlanValidator()
        report = validator.validate_plan("/nonexistent/plan.md")

        assert report is not None
        assert not report.is_valid
        assert len(report.issues) > 0

    def test_validate_plan_empty_file(self):
        """Test validating an empty plan file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            assert not report.is_valid

        finally:
            os.unlink(plan_path)

    def test_plan_validation_categories(self):
        """Test that all plan validation categories are defined."""
        expected_categories = [
            "architecture_design",
            "se_principles_compliance",
            "component_definition",
            "interface_contracts",
            "quality_gates_integration",
            "task_breakdown",
            "dependency_management",
            "testing_strategy",
        ]

        for category in expected_categories:
            assert hasattr(PlanValidationCategory, category.upper())

    def test_validate_plan_with_data_models(self):
        """Test validating a plan with proper data model definitions."""
        plan_with_models = """
# Implementation Plan: With Data Models

## Technical Architecture

### Data Models
- **User**: id (UUID), email (String), password_hash (String), created_at (DateTime)
- **Profile**: id (UUID), user_id (UUID), first_name (String), last_name (String)

### API Endpoints
- GET /users/{id} - Retrieve user by ID
- POST /users - Create new user

## SE Principles Architecture Compliance

### Encapsulation
- User password handling encapsulated in security service
- Database access through repository pattern

## Quality Gates Integration
Testing and validation requirements defined

## Implementation Tasks
- [ ] T001: Create User model
- [ ] T002: Implement user repository
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_with_models)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            # Should recognize data model definitions

        finally:
            os.unlink(plan_path)

    def test_validate_plan_with_interface_contracts(self):
        """Test validating a plan with interface contract definitions."""
        plan_with_contracts = """
# Implementation Plan: With Interface Contracts

## Technical Architecture

### Interface Contracts

#### IUserRepository
```python
class IUserRepository:
    def create_user(self, user_data: UserCreate) -> User
    def get_user_by_id(self, user_id: UUID) -> Optional[User]
    def update_user(self, user_id: UUID, updates: UserUpdate) -> User
```

#### IAuthenticationService  
```python
class IAuthenticationService:
    def authenticate(self, email: str, password: str) -> Optional[AuthToken]
    def validate_token(self, token: str) -> Optional[User]
```

## SE Principles Architecture Compliance

### Loose Coupling
- Components depend on interfaces, not concrete implementations

## Implementation Tasks
- [ ] T001: Define interface contracts
- [ ] T002: Implement concrete classes
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(plan_with_contracts)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            assert report is not None
            # Should recognize interface contracts

        finally:
            os.unlink(plan_path)

    def test_error_handling_malformed_markdown(self):
        """Test error handling with malformed markdown."""
        malformed_plan = """
# Plan with Issues

## Unclosed section
Missing proper structure

### Nested without context
- Broken list
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(malformed_plan)
            plan_path = f.name

        try:
            validator = PlanValidator()
            report = validator.validate_plan(plan_path)

            # Should handle malformed content gracefully
            assert report is not None

        finally:
            os.unlink(plan_path)

    def test_validation_with_custom_config(self):
        """Test plan validation with custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text(
                """
plan_validation:
  require_interface_contracts: true
  require_data_models: true
  min_task_count: 3
"""
            )

            validator = PlanValidator(str(config_file))
            assert validator is not None

    def test_batch_plan_validation(self):
        """Test validating multiple plan files."""
        plan1_content = """
# Plan 1
## Technical Architecture
Basic architecture
## SE Principles Architecture Compliance
Basic compliance
## Implementation Tasks
- [ ] T001: Task 1
"""

        plan2_content = """
# Plan 2  
## Technical Architecture
Advanced architecture
## SE Principles Architecture Compliance
Advanced compliance
## Implementation Tasks
- [ ] T001: Advanced task
"""

        plan_files = []
        try:
            for content in [plan1_content, plan2_content]:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as f:
                    f.write(content)
                    plan_files.append(f.name)

            validator = PlanValidator()
            reports = [validator.validate_plan(path) for path in plan_files]

            assert len(reports) == 2
            assert all(report is not None for report in reports)

        finally:
            for path in plan_files:
                if os.path.exists(path):
                    os.unlink(path)
