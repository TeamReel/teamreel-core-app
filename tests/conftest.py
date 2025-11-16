"""
Test fixtures and configuration for TeamReel Constitutional Validator tests.
"""

import os
import sys
from pathlib import Path

# Add src to Python path for testing
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

import pytest
from constitutional_validator import ConstitutionalValidator
from compliance_reporter import ComplianceReport, Violation
from violation_detector import ViolationDetector


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary configuration directory with test configs."""
    config_dir = tmp_path / ".kittify" / "config"
    config_dir.mkdir(parents=True)

    # Create test SE rules config
    se_rules_content = """
se_principles:
  SRP:
    description: "Single Responsibility Principle"
    rules:
      - rule_id: "SRP001"
        name: "function_complexity"
        threshold: 10
        file_types: ["py", "ts", "js"]
        violation_message: "Function exceeds complexity limit"
        suggested_fix: "Split complex function into smaller functions"
        severity: "ERROR"

  Encapsulation:
    description: "Information hiding"
    rules:
      - rule_id: "ENC001"
        name: "private_member_access"
        pattern: "\\\\._[a-zA-Z_]"
        file_types: ["py"]
        violation_message: "Direct access to private member"
        suggested_fix: "Use public methods to access internal state"
        severity: "ERROR"
"""

    (config_dir / "se_rules.yaml").write_text(se_rules_content)

    # Create test quality gates config
    quality_gates_content = """
quality_gates:
  coverage:
    enabled: true
    unit_test_threshold: 0.8
    failure_action: "block"
    
  complexity:
    enabled: true
    cyclomatic_max: 10
    failure_action: "block"
    
  security:
    enabled: true
    vulnerability_scan: true
    failure_action: "block"
    
  naming_conventions:
    enabled: true
    python_code: "snake_case"
    failure_action: "warn"
"""

    (config_dir / "quality_gates.yaml").write_text(quality_gates_content)

    return config_dir


@pytest.fixture
def sample_python_code():
    """Sample Python code with various violations for testing."""
    return {
        "valid_code": '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        self._internal_state = 0
    
    def add(self, value):
        """Add value to internal state."""
        self._internal_state += value
        return self._internal_state
''',
        "srp_violation": '''
def process_user_data_and_send_email_and_log_activity(user_data):
    """This function does too many things - SRP violation."""
    # Process data
    processed = user_data.upper()
    
    # Send email  
    email_sent = send_email(processed)
    
    # Log activity
    log_activity("user_processed", user_data)
    
    # Generate report
    report = generate_report(processed)
    
    # Update database
    update_database(user_data, processed)
    
    return processed, email_sent, report
''',
        "encapsulation_violation": """
class BankAccount:
    def __init__(self):
        self.balance = 1000  # Should be private
        
    def get_balance(self):
        return self.balance

# Direct access to internal state - violation
account = BankAccount()
account.balance = 999999  # Direct manipulation
""",
        "complexity_violation": '''
def complex_function(data):
    """Overly complex function with high cyclomatic complexity."""
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item > 100:
                    if item < 1000:
                        if item % 10 == 0:
                            if item % 100 != 0:
                                if item % 5 == 0:
                                    result.append(item * 2)
                                else:
                                    result.append(item * 3)
                            else:
                                result.append(item // 2)
                        else:
                            result.append(item + 1)
                    else:
                        result.append(item - 1)
                else:
                    result.append(item)
            else:
                result.append(item * -1)
        else:
            result.append(0)
    return result
''',
        "security_violation": '''
import os

# Security violations - hardcoded secrets
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
SECRET_TOKEN = "secret_token_value"

def connect_to_database():
    """Connect with hardcoded credentials."""
    connection_string = f"mysql://admin:{PASSWORD}@localhost/db"
    return connection_string
''',
        "naming_violation": '''
def calculateUserData(userData):
    """Function uses camelCase instead of snake_case."""
    return userData.upper()

class userManager:
    """Class uses lowercase instead of PascalCase."""
    
    def getUserById(self, userId):
        """Method uses camelCase instead of snake_case."""
        return f"User {userId}"
''',
    }


@pytest.fixture
def constitutional_validator():
    """Create ConstitutionalValidator instance for testing."""
    return ConstitutionalValidator()


@pytest.fixture
def violation_detector():
    """Create ViolationDetector instance for testing."""
    return ViolationDetector()


@pytest.fixture
def sample_violations():
    """Sample violation objects for testing reports."""
    return [
        Violation(
            principle="SRP",
            severity="ERROR",
            message="Function has too many responsibilities",
            file_path="test.py",
            line_number=10,
            suggested_fix="Split function into smaller functions",
            rule_id="SRP001",
        ),
        Violation(
            principle="Encapsulation",
            severity="WARNING",
            message="Direct access to private member",
            file_path="test.py",
            line_number=25,
            suggested_fix="Use public methods for access",
            rule_id="ENC001",
        ),
        Violation(
            principle="Defensibility",
            severity="HIGH",
            message="Hardcoded password detected",
            file_path="config.py",
            line_number=5,
            suggested_fix="Use environment variables",
            rule_id="SEC001",
        ),
    ]
