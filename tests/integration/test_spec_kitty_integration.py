"""
Integration tests for the complete spec-kitty constitutional validation workflow.

Tests end-to-end integration: spec → plan → tasks with constitutional validation.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Import components
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spec_validator import SpecValidator
from plan_validator import PlanValidator
from task_validator import TaskValidator
from constitutional_validator import ConstitutionalValidator


class TestSpecKittyIntegration:
    """Integration tests for spec-kitty constitutional validation workflow."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create project structure
        (self.project_path / "specs").mkdir()
        (self.project_path / "plans").mkdir()
        (self.project_path / "tasks").mkdir()

    def teardown_method(self):
        """Cleanup test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_workflow_valid_documents(self):
        """Test complete workflow with valid spec, plan, and tasks."""
        # Create valid specification
        spec_content = """
# Feature Specification: User Authentication System

## Constitutional Requirements
This feature must comply with all SE principles and quality gates defined in the constitutional framework.

## Feature Description
Implement secure user authentication system with login, logout, and session management capabilities.

## Acceptance Criteria
- [ ] AC001: User can login with valid email and password
- [ ] AC002: Invalid credentials return appropriate error message
- [ ] AC003: Successful login creates authenticated session
- [ ] AC004: User can logout and session is terminated
- [ ] AC005: Session expires after configured timeout

## SE Principles Requirements

### Single Responsibility Principle
- Authentication service only handles user authentication logic
- Session service only manages user sessions
- User service only manages user data operations

### Encapsulation
- Password hashing implementation hidden behind security service interface
- Database access abstracted through repository pattern
- Internal authentication state not exposed to external components

### Loose Coupling
- Authentication service depends on interfaces, not concrete implementations
- Components communicate through well-defined service contracts
- No direct database dependencies in business logic

## Quality Gates
- Unit test coverage >= 80%
- Integration test coverage >= 70%
- Cyclomatic complexity < 10 per function
- Security scan passes with no high-severity issues
- Performance: Authentication response < 200ms
"""

        spec_path = self.project_path / "specs" / "user-authentication.md"
        spec_path.write_text(spec_content)

        # Create valid implementation plan
        plan_content = """
# Implementation Plan: User Authentication System

## Technical Architecture

### System Components
- **AuthenticationService**: Handles user login/logout operations
- **SessionService**: Manages authenticated user sessions
- **UserRepository**: Data access layer for user information
- **SecurityService**: Password hashing and validation utilities
- **TokenService**: JWT token generation and validation

### Data Models
- **User**: id (UUID), email (String), password_hash (String), created_at (DateTime), updated_at (DateTime)
- **Session**: id (UUID), user_id (UUID), token (String), expires_at (DateTime), created_at (DateTime)

### API Endpoints
- POST /auth/login - Authenticate user credentials
- POST /auth/logout - Terminate user session
- GET /auth/profile - Retrieve authenticated user profile
- POST /auth/refresh - Refresh authentication token

## SE Principles Architecture Compliance

### Single Responsibility Principle
- AuthenticationService: Only handles authentication logic and credential validation
- SessionService: Only manages session lifecycle and token operations
- UserRepository: Only handles user data persistence and retrieval
- SecurityService: Only provides cryptographic operations and password utilities

### Encapsulation
- Password hashing algorithms encapsulated within SecurityService
- Database query logic encapsulated within repository implementations
- Token generation and validation encapsulated within TokenService
- Authentication state management encapsulated within SessionService

### Loose Coupling
- Services depend on interfaces (IUserRepository, ISecurityService, ITokenService)
- Business logic separated from data access through repository pattern
- Cross-cutting concerns (logging, validation) handled through middleware
- Configuration externalized through dependency injection

## Quality Gates Integration

### Testing Strategy
- Unit tests: 80% coverage minimum with focus on business logic
- Integration tests: API endpoint validation and database interactions
- Security tests: Authentication flow validation and vulnerability scanning
- Performance tests: Response time and concurrent user handling

### Code Quality Standards
- Complexity analysis: Cyclomatic complexity < 10 per function
- Security scanning: No hardcoded credentials or secrets
- Naming conventions: snake_case for Python, clear descriptive names
- Documentation: All public methods and classes documented

### Deployment Requirements
- Environment configuration: Separate configs for dev/staging/production
- Security configuration: Secure token secrets and password policies
- Monitoring: Authentication success/failure metrics and alerting

## Implementation Tasks

### Phase 1: Core Authentication Infrastructure
- [ ] T001: Create User model and database schema
- [ ] T002: Implement SecurityService with password hashing
- [ ] T003: Create UserRepository with database operations
- [ ] T004: Implement basic AuthenticationService

### Phase 2: Session Management
- [ ] T005: Create Session model and database schema
- [ ] T006: Implement TokenService for JWT operations
- [ ] T007: Create SessionService for session lifecycle
- [ ] T008: Add session validation middleware

### Phase 3: API Implementation
- [ ] T009: Implement POST /auth/login endpoint
- [ ] T010: Implement POST /auth/logout endpoint
- [ ] T011: Implement GET /auth/profile endpoint
- [ ] T012: Implement POST /auth/refresh endpoint

### Phase 4: Security and Validation
- [ ] T013: Add input validation for all endpoints
- [ ] T014: Implement rate limiting for authentication attempts
- [ ] T015: Add security headers and CORS configuration
- [ ] T016: Implement comprehensive error handling
"""

        plan_path = self.project_path / "plans" / "user-authentication-plan.md"
        plan_path.write_text(plan_content)

        # Create valid task
        task_content = '''
# Task: T001 - Create User Model and Database Schema

## Constitutional Compliance

### SE Principles Adherence
- **Single Responsibility**: User model only represents user data structure and basic operations
- **Encapsulation**: Internal user data validation and constraints encapsulated within model
- **Loose Coupling**: Model does not depend on specific database implementation or external services

### Quality Gates Alignment
- **Testing**: Unit tests for model validation, constraints, and data integrity
- **Code Quality**: Clean model definition with clear field types and relationships
- **Security**: Sensitive fields (password_hash) properly handled and never exposed

## Technical Implementation

### Database Schema Definition
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Model Implementation
```python
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class User(Base):
    """User model representing authenticated users in the system."""
    
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    def to_dict(self):
        """Convert user to dictionary, excluding sensitive fields."""
        return {
            'id': str(self.id),
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

### Implementation Steps
1. Define database migration for user table creation
2. Implement User model with SQLAlchemy ORM
3. Add model validation for email format and constraints
4. Create database indexes for optimized queries
5. Implement model utility methods (to_dict, validation)
6. Add comprehensive unit tests for model functionality

### Error Handling
- **Database Errors**: Handle unique constraint violations for email duplicates
- **Validation Errors**: Validate email format and password requirements
- **Migration Errors**: Provide rollback capability for schema changes

### Dependencies
- **SQLAlchemy**: ORM for database model definition
- **PostgreSQL**: Primary database for production environment
- **Alembic**: Database migration management
- **Email-validator**: Email format validation library

## Testing Strategy

### Unit Tests
- Model instantiation and field validation
- Email uniqueness constraint enforcement
- Password hash field handling (never expose raw passwords)
- Timestamp field automatic population
- to_dict() method excludes sensitive fields
- Model representation (__repr__) formatting

### Integration Tests
- Database table creation and schema validation
- Model persistence and retrieval operations
- Index effectiveness for query optimization
- Migration rollback functionality

### Data Integrity Tests
- Email format validation edge cases
- UUID generation and uniqueness
- Timestamp consistency across operations
- Foreign key constraints (for future relationships)

## Acceptance Criteria
- [ ] User table created with proper schema and constraints
- [ ] User model implements all required fields and methods
- [ ] Email uniqueness constraint properly enforced
- [ ] Password hash field never exposes sensitive data
- [ ] Model validation prevents invalid data insertion
- [ ] Database indexes created for performance optimization
- [ ] Unit tests achieve 80% coverage minimum
- [ ] Integration tests validate database operations
- [ ] Migration scripts support both upgrade and downgrade
- [ ] Model documentation complete and accurate
'''

        task_path = self.project_path / "tasks" / "T001-create-user-model.md"
        task_path.write_text(task_content)

        # Test complete workflow validation
        spec_validator = SpecValidator()
        plan_validator = PlanValidator()
        task_validator = TaskValidator()

        # Validate specification
        spec_report = spec_validator.validate_spec(str(spec_path))
        assert (
            spec_report.is_valid
        ), f"Spec validation failed: {[issue.message for issue in spec_report.issues]}"

        # Validate plan
        plan_report = plan_validator.validate_plan(str(plan_path))
        assert (
            plan_report.is_valid
        ), f"Plan validation failed: {[issue.message for issue in plan_report.issues]}"

        # Validate task
        task_report = task_validator.validate_task(str(task_path))
        assert (
            task_report.is_valid
        ), f"Task validation failed: {[issue.message for issue in task_report.issues]}"

    def test_workflow_with_invalid_spec(self):
        """Test workflow behavior when specification fails validation."""
        # Create invalid specification (missing required sections)
        invalid_spec_content = """
# Incomplete Specification

Just some basic content without constitutional requirements or acceptance criteria.
"""

        spec_path = self.project_path / "specs" / "invalid-spec.md"
        spec_path.write_text(invalid_spec_content)

        # Validation should fail
        spec_validator = SpecValidator()
        spec_report = spec_validator.validate_spec(str(spec_path))

        assert not spec_report.is_valid
        assert len(spec_report.issues) > 0

    def test_workflow_spec_plan_alignment(self):
        """Test that plan properly addresses spec requirements."""
        # Create spec with specific requirements
        spec_content = """
# Feature Specification: Data Processing

## Constitutional Requirements
Must comply with SE principles.

## Acceptance Criteria
- [ ] AC001: Process data efficiently
- [ ] AC002: Handle errors gracefully
- [ ] AC003: Validate input data

## SE Principles Requirements
- Single Responsibility: Each component has one job
- Encapsulation: Hide implementation details
- Loose Coupling: Components interact through interfaces

## Quality Gates
- 80% test coverage
- Complexity < 10
"""

        # Create plan that addresses spec requirements
        plan_content = """
# Implementation Plan: Data Processing

## Technical Architecture

### System Components
- **DataProcessor**: Handles data processing logic (AC001)
- **ErrorHandler**: Manages error scenarios (AC002)
- **InputValidator**: Validates input data (AC003)

## SE Principles Architecture Compliance

### Single Responsibility Principle
- DataProcessor only processes data
- ErrorHandler only handles errors
- InputValidator only validates inputs

### Encapsulation
- Processing algorithms hidden behind service interface
- Error handling logic encapsulated

### Loose Coupling
- Components interact through defined interfaces

## Quality Gates Integration
- Unit tests: 80% coverage minimum
- Complexity analysis: < 10 per function

## Implementation Tasks
- [ ] T001: Implement DataProcessor
- [ ] T002: Create ErrorHandler
- [ ] T003: Build InputValidator
"""

        spec_path = self.project_path / "specs" / "data-processing.md"
        plan_path = self.project_path / "plans" / "data-processing-plan.md"

        spec_path.write_text(spec_content)
        plan_path.write_text(plan_content)

        # Both should validate successfully
        spec_validator = SpecValidator()
        plan_validator = PlanValidator()

        spec_report = spec_validator.validate_spec(str(spec_path))
        plan_report = plan_validator.validate_plan(str(plan_path))

        assert spec_report.is_valid
        assert plan_report.is_valid

    def test_constitutional_validator_integration(self):
        """Test integration with core constitutional validator."""
        constitutional_validator = ConstitutionalValidator()

        # Should have access to all validation components
        assert constitutional_validator is not None

        # Test with a simple valid content
        valid_content = """
# Test Content

## SE Principles Requirements
- Single Responsibility: Defined
- Encapsulation: Defined  
- Loose Coupling: Defined

## Quality Gates
- Testing: 80% coverage
- Complexity: < 10
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(valid_content)
            temp_path = f.name

        try:
            # Should validate successfully
            report = constitutional_validator.validate_content(temp_path)
            assert report is not None

        finally:
            os.unlink(temp_path)

    def test_batch_validation_workflow(self):
        """Test validating multiple files in batch."""
        # Create multiple spec files
        spec_contents = [
            """
# Spec 1
## Constitutional Requirements
Requirements defined
## Acceptance Criteria
- [ ] AC001: Criterion 1
## SE Principles Requirements
- Single Responsibility: Defined
## Quality Gates
- Testing: 80% coverage
""",
            """
# Spec 2
## Constitutional Requirements
Requirements defined
## Acceptance Criteria
- [ ] AC001: Criterion 1
## SE Principles Requirements
- Single Responsibility: Defined
## Quality Gates
- Testing: 80% coverage
""",
        ]

        spec_paths = []
        for i, content in enumerate(spec_contents):
            spec_path = self.project_path / "specs" / f"spec-{i+1}.md"
            spec_path.write_text(content)
            spec_paths.append(str(spec_path))

        # Validate all specs
        spec_validator = SpecValidator()
        reports = [spec_validator.validate_spec(path) for path in spec_paths]

        assert len(reports) == 2
        assert all(report.is_valid for report in reports)

    def test_error_propagation_workflow(self):
        """Test that validation errors are properly propagated."""
        # Create spec with constitutional violations
        invalid_spec = """
# Invalid Specification

Missing all required constitutional sections.
"""

        spec_path = self.project_path / "specs" / "invalid.md"
        spec_path.write_text(invalid_spec)

        spec_validator = SpecValidator()
        report = spec_validator.validate_spec(str(spec_path))

        # Should have validation errors
        assert not report.is_valid
        assert len(report.issues) > 0

        # Issues should describe missing constitutional elements
        issue_messages = [issue.message for issue in report.issues]
        constitutional_issues = [
            msg
            for msg in issue_messages
            if "constitutional" in msg.lower()
            or "se principles" in msg.lower()
            or "quality gates" in msg.lower()
        ]
        assert len(constitutional_issues) > 0
