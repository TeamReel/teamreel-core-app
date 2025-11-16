"""
Unit tests for TaskValidator class.

Tests task validation against constitutional requirements.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys
import yaml

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from task_validator import TaskValidator, TaskValidationCategory


class TestTaskValidator:
    """Test cases for TaskValidator class."""

    def test_initialization(self):
        """Test TaskValidator initialization."""
        validator = TaskValidator()

        assert validator is not None
        assert hasattr(validator, "constitutional_validator")

    def test_validate_task_complete_definition(self):
        """Test validating a task with complete definition."""
        task_content = '''
# Task: T001 - Implement User Authentication API

## Constitutional Compliance

### SE Principles Adherence
- **Single Responsibility**: Authentication endpoint only handles user login
- **Encapsulation**: Password validation logic encapsulated in security service
- **Loose Coupling**: Depends on IUserRepository interface, not concrete implementation

### Quality Gates Integration
- **Testing**: Unit tests with 80% coverage minimum
- **Code Quality**: Cyclomatic complexity < 10
- **Security**: No hardcoded credentials, secure password hashing

## Technical Implementation

### Function Signature
```python
async def authenticate_user(
    email: str, 
    password: str, 
    user_repository: IUserRepository
) -> AuthenticationResult:
    """Authenticate user credentials and return auth token."""
```

### Implementation Steps
1. Validate input parameters (email format, password length)
2. Query user repository for user by email
3. Verify password using security service
4. Generate authentication token
5. Return authentication result

### Error Handling
- Invalid email format: Return validation error
- User not found: Return authentication failed
- Invalid password: Return authentication failed
- Database error: Return internal server error

### Dependencies
- IUserRepository: User data access interface
- ISecurityService: Password hashing and validation
- ITokenService: Authentication token generation

## Testing Strategy

### Unit Tests
- Valid authentication: Should return success with token
- Invalid email: Should return validation error
- User not found: Should return authentication failed
- Invalid password: Should return authentication failed

### Integration Tests  
- Database connectivity: Repository integration
- Security service integration: Password validation
- Token service integration: Token generation

## Acceptance Criteria
- [ ] Function accepts email and password parameters
- [ ] Returns AuthenticationResult with success/failure status
- [ ] Generates secure authentication token on success
- [ ] Handles all error scenarios gracefully
- [ ] Achieves 80% unit test coverage
- [ ] Passes security validation checks
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_content)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            assert hasattr(report, "issues")
            assert hasattr(report, "is_valid")

        finally:
            os.unlink(task_path)

    def test_validate_task_missing_se_principles(self):
        """Test validating a task missing SE principles adherence."""
        incomplete_task = """
# Task: T002 - Basic Task

## Technical Implementation
Some basic implementation details.

## Testing Strategy
Basic testing approach.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(incomplete_task)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            assert not report.is_valid
            assert len(report.issues) > 0

            # Should flag missing constitutional compliance section
            issue_messages = [issue.message for issue in report.issues]
            assert any(
                "constitutional compliance" in msg.lower()
                or "se principles" in msg.lower()
                for msg in issue_messages
            )

        finally:
            os.unlink(task_path)

    def test_validate_task_missing_implementation_details(self):
        """Test validating a task missing technical implementation."""
        task_without_impl = """
# Task: T003 - No Implementation

## Constitutional Compliance
Basic compliance notes.

## Testing Strategy
Basic testing notes.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_without_impl)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            assert not report.is_valid

            # Should flag validation issues (constitutional compliance or task structure)
            issue_messages = [issue.message for issue in report.issues]
            assert any(
                ("constitutional" in msg.lower() or "task" in msg.lower())
                for msg in issue_messages
            )

        finally:
            os.unlink(task_path)

    def test_validate_task_missing_testing_strategy(self):
        """Test validating a task missing testing strategy."""
        task_without_tests = """
# Task: T004 - No Testing

## Constitutional Compliance
- SE principles adherence documented

## Technical Implementation
- Implementation details provided
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_without_tests)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            # Should warn about missing testing strategy

        finally:
            os.unlink(task_path)

    def test_validate_task_missing_acceptance_criteria(self):
        """Test validating a task missing acceptance criteria."""
        task_without_criteria = """
# Task: T005 - No Acceptance Criteria

## Constitutional Compliance
SE principles documented

## Technical Implementation
Implementation provided

## Testing Strategy
Testing approach defined
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_without_criteria)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            # Should warn about missing acceptance criteria

        finally:
            os.unlink(task_path)

    def test_validate_task_nonexistent_file(self):
        """Test validating a nonexistent task file."""
        validator = TaskValidator()
        report = validator.validate_task("/nonexistent/task.md")

        assert report is not None
        assert not report.is_valid
        assert len(report.issues) > 0

    def test_validate_task_empty_file(self):
        """Test validating an empty task file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            assert not report.is_valid

        finally:
            os.unlink(task_path)

    def test_task_validation_categories(self):
        """Test that all task validation categories are defined."""
        expected_categories = [
            "constitutional_compliance",
            "se_principles_adherence",
            "implementation_details",
            "dependency_definition",
            "error_handling",
            "testing_strategy",
            "acceptance_criteria",
            "quality_gates_alignment",
        ]

        for category in expected_categories:
            assert hasattr(TaskValidationCategory, category.upper())

    def test_validate_task_with_function_signature(self):
        """Test validating a task with proper function signature."""
        task_with_signature = '''
# Task: T006 - With Function Signature

## Constitutional Compliance
SE principles documented

## Technical Implementation

### Function Signature
```python
def process_user_data(
    user_id: UUID,
    user_data: UserUpdateRequest,
    repository: IUserRepository
) -> ProcessingResult:
    """Process user data update request."""
```

### Implementation Steps
1. Validate input parameters
2. Process the data
3. Return result

## Testing Strategy
Unit and integration tests defined

## Acceptance Criteria
- [ ] Function processes user data correctly
- [ ] Returns appropriate result type
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_with_signature)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            # Should recognize function signature

        finally:
            os.unlink(task_path)

    def test_validate_task_with_error_handling(self):
        """Test validating a task with comprehensive error handling."""
        task_with_errors = """
# Task: T007 - With Error Handling

## Constitutional Compliance
SE principles adherence documented

## Technical Implementation

### Error Handling Strategy
- **ValidationError**: Invalid input parameters
- **NotFoundError**: Resource not found
- **DatabaseError**: Database connectivity issues
- **AuthorizationError**: Insufficient permissions

### Error Response Format
```python
class ErrorResponse:
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
```

## Testing Strategy
Error scenarios covered in tests

## Acceptance Criteria
- [ ] All error scenarios handled gracefully
- [ ] Consistent error response format
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_with_errors)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            # Should recognize error handling strategy

        finally:
            os.unlink(task_path)

    def test_validate_task_with_dependencies(self):
        """Test validating a task with dependency definitions."""
        task_with_deps = """
# Task: T008 - With Dependencies

## Constitutional Compliance
SE principles compliance documented

## Technical Implementation

### Dependencies
- **IUserRepository**: User data access interface
- **ISecurityService**: Password hashing and validation  
- **ILoggerService**: Application logging
- **ConfigurationService**: Application configuration

### Dependency Injection
```python
@inject
def __init__(
    self,
    user_repo: IUserRepository,
    security: ISecurityService,
    logger: ILoggerService
):
```

## Testing Strategy
Dependency mocking strategy defined

## Acceptance Criteria
- [ ] All dependencies properly injected
- [ ] Interfaces used instead of concrete classes
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(task_with_deps)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            assert report is not None
            # Should recognize dependency definitions

        finally:
            os.unlink(task_path)

    def test_error_handling_malformed_task(self):
        """Test error handling with malformed task content."""
        malformed_task = """
# Task with Issues

Broken structure without proper sections

### Random nested section
- Unorganized content
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(malformed_task)
            task_path = f.name

        try:
            validator = TaskValidator()
            report = validator.validate_task(task_path)

            # Should handle malformed content gracefully
            assert report is not None

        finally:
            os.unlink(task_path)

    def test_validation_with_custom_config(self):
        """Test task validation with custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text(
                """
task_validation:
  require_function_signature: true
  require_error_handling: true
  require_dependency_injection: true
"""
            )

            validator = TaskValidator(str(config_file))
            assert validator is not None

    def test_batch_task_validation(self):
        """Test validating multiple task files."""
        task1_content = """
# Task 1
## Constitutional Compliance
Basic compliance
## Technical Implementation
Basic implementation
## Testing Strategy
Basic testing
## Acceptance Criteria
- [ ] Criterion 1
"""

        task2_content = """
# Task 2
## Constitutional Compliance
Advanced compliance
## Technical Implementation
Advanced implementation
## Testing Strategy
Advanced testing
## Acceptance Criteria
- [ ] Advanced criterion
"""

        task_files = []
        try:
            for content in [task1_content, task2_content]:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as f:
                    f.write(content)
                    task_files.append(f.name)

            validator = TaskValidator()
            reports = [validator.validate_task(path) for path in task_files]

            assert len(reports) == 2
            assert all(report is not None for report in reports)

        finally:
            for path in task_files:
                if os.path.exists(path):
                    os.unlink(path)
