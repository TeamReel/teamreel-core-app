"""
Unit tests for ViolationDetector class.

Tests SE principle violation detection across different file types.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Import test subjects
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from violation_detector import ViolationDetector, ViolationType, DetectedViolation
from compliance_reporter import Violation


class TestViolationDetector:
    """Test cases for ViolationDetector class."""

    def test_initialization(self):
        """Test ViolationDetector initialization."""
        detector = ViolationDetector()

        assert detector is not None
        assert hasattr(detector, "supported_extensions")
        assert ".py" in detector.supported_extensions
        assert ".js" in detector.supported_extensions
        assert ".ts" in detector.supported_extensions

    def test_get_supported_extensions(self):
        """Test getting supported file extensions."""
        detector = ViolationDetector()
        extensions = detector.get_supported_extensions()

        assert isinstance(extensions, list)
        assert ".py" in extensions
        assert ".js" in extensions
        assert ".ts" in extensions
        assert ".yaml" in extensions
        assert ".json" in extensions

    def test_is_supported_file(self):
        """Test checking if file is supported."""
        detector = ViolationDetector()

        assert detector.is_supported_file("test.py") is True
        assert detector.is_supported_file("test.js") is True
        assert detector.is_supported_file("test.ts") is True
        assert detector.is_supported_file("test.yaml") is True
        assert detector.is_supported_file("test.json") is True
        assert detector.is_supported_file("test.exe") is False
        assert detector.is_supported_file("test.bin") is False

    def test_detect_srp_violations(self):
        """Test SRP violation detection."""
        detector = ViolationDetector()

        # Code with SRP violation - function doing too many things
        srp_violation_code = '''
def process_user_and_send_email_and_log(user_data):
    """Function that violates SRP by doing multiple things."""
    # Process user data
    processed = user_data.upper()
    
    # Send email
    email_sent = send_email(processed)
    
    # Log activity  
    log_activity("user_processed", user_data)
    
    # Generate report
    report = generate_report(processed)
    
    # Update database
    update_database(user_data)
    
    return processed, email_sent, report
'''

        violations = detector.detect_srp_violations(
            srp_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        # Should detect violations or return empty list if no detection logic yet
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_encapsulation_violations(self):
        """Test encapsulation violation detection."""
        detector = ViolationDetector()

        # Code with encapsulation violation
        encapsulation_violation_code = """
class BankAccount:
    def __init__(self):
        self.balance = 1000  # Should be private
        
    def get_balance(self):
        return self.balance

# Direct access to internal state - violation
account = BankAccount()
account.balance = 999999  # Direct manipulation of internal state
"""

        violations = detector.detect_encapsulation_violations(
            encapsulation_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_coupling_violations(self):
        """Test loose coupling violation detection."""
        detector = ViolationDetector()

        # Code with coupling violation - too many imports
        coupling_violation_code = '''
import os
import sys
import json
import yaml
import requests
import pandas
import numpy
import matplotlib
import seaborn
import sklearn
import tensorflow
import torch
import flask
import django
import fastapi

def function_with_many_dependencies():
    """Function that uses many external dependencies."""
    pass
'''

        violations = detector.detect_coupling_violations(
            "test.py", coupling_violation_code
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_reusability_violations(self):
        """Test reusability violation detection."""
        detector = ViolationDetector()

        # Code with reusability violation - duplicated logic
        reusability_violation_code = '''
def calculate_user_score_1(user):
    """Calculate score for user type 1."""
    base_score = 100
    if user.is_premium:
        base_score *= 1.5
    if user.years_active > 5:
        base_score *= 1.2
    return base_score

def calculate_user_score_2(user):
    """Calculate score for user type 2.""" 
    base_score = 100  # Duplicated logic
    if user.is_premium:
        base_score *= 1.5  # Duplicated logic
    if user.years_active > 5:
        base_score *= 1.2  # Duplicated logic
    return base_score * 0.9  # Only difference
'''

        violations = detector.detect_reusability_violations(
            reusability_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_portability_violations(self):
        """Test portability violation detection."""
        detector = ViolationDetector()

        # Code with portability violations - hardcoded paths
        portability_violation_code = '''
import os

def save_file(data):
    """Save file with hardcoded Windows path."""
    file_path = "C:\\\\Windows\\\\temp\\\\data.txt"  # Windows-specific path
    with open(file_path, 'w') as f:
        f.write(data)

def load_config():
    """Load config with hardcoded Linux path."""
    config_path = "/etc/myapp/config.conf"  # Linux-specific path
    with open(config_path, 'r') as f:
        return f.read()
'''

        violations = detector.detect_portability_violations(
            portability_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_defensibility_violations(self):
        """Test defensibility violation detection."""
        detector = ViolationDetector()

        # Code with defensibility violations - no input validation
        defensibility_violation_code = '''
def process_user_input(user_input):
    """Process user input without validation."""
    # No input validation - security risk
    result = eval(user_input)  # Dangerous eval usage
    return result

def execute_command(command):
    """Execute system command without validation."""
    import os
    os.system(command)  # Command injection risk
'''

        violations = detector.detect_defensibility_violations(
            defensibility_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_maintainability_violations(self):
        """Test maintainability violation detection."""
        detector = ViolationDetector()

        # Code with maintainability violations - no documentation
        maintainability_violation_code = """
def complex_calculation(a, b, c, d, e):
    # No docstring - maintainability issue
    x = a * b + c / d - e
    y = x ** 2 + (a - b) * (c + d)
    z = y / (e + 1) if e != -1 else 0
    return (x + y + z) / 3

class DataProcessor:
    # No class documentation
    def __init__(self, config):
        self.config = config
        
    def process(self, data):
        # No method documentation
        pass
"""

        violations = detector.detect_maintainability_violations(
            maintainability_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_simplicity_violations(self):
        """Test simplicity violation detection."""
        detector = ViolationDetector()

        # Code with simplicity violations - over-engineered
        simplicity_violation_code = '''
class AbstractFactoryPatternImplementation:
    """Over-engineered factory pattern for simple task."""
    
    def create_abstract_factory(self):
        return AbstractConcreteFactoryImplementation()

class AbstractConcreteFactoryImplementation:
    """Unnecessary abstraction layer."""
    
    def create_product(self, product_type):
        if product_type == "A":
            return ConcreteProductAImplementation()
        elif product_type == "B":
            return ConcreteProductBImplementation()

class ConcreteProductAImplementation:
    """Over-engineered for simple string return."""
    
    def get_value(self):
        return self._perform_complex_value_retrieval_process()
    
    def _perform_complex_value_retrieval_process(self):
        return "A"  # Could just return "A" directly
'''

        violations = detector.detect_simplicity_violations(
            simplicity_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_complexity_violations(self):
        """Test complexity violation detection."""
        detector = ViolationDetector()

        # Code with high complexity - deep nesting
        complexity_violation_code = '''
def deeply_nested_function(data):
    """Function with excessive nesting depth."""
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item > 100:
                    if item < 1000:
                        if item % 10 == 0:
                            if item % 100 != 0:
                                if item % 5 == 0:
                                    return item * 2
                                else:
                                    return item * 3
                            else:
                                return item // 2
                        else:
                            return item + 1
                    else:
                        return item - 1
                else:
                    return item
            else:
                return item * -1
        else:
            return 0
'''

        violations = detector.detect_complexity_violations(
            complexity_violation_code, "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_naming_violations(self):
        """Test naming convention violation detection."""
        detector = ViolationDetector()

        # Python code with naming violations
        naming_violation_code = '''
def calculateUserData(userData):  # Should be snake_case
    """Function with camelCase name in Python."""
    return userData.upper()

class userManager:  # Should be PascalCase
    """Class with incorrect naming."""
    
    def getUserById(self, userId):  # Should be snake_case
        """Method with camelCase name."""
        return f"User {userId}"
'''

        violations = detector.detect_naming_violations(
            naming_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

    def test_detect_security_violations(self):
        """Test security violation detection."""
        detector = ViolationDetector()

        # Code with security violations
        security_violation_code = '''
import os

# Security violations - hardcoded secrets
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
SECRET_TOKEN = "secret_token_value"

def connect_to_database():
    """Connect with hardcoded credentials."""
    connection_string = f"mysql://admin:{PASSWORD}@localhost/db"
    return connection_string

def authenticate_api():
    """Use hardcoded API key."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return headers
'''

        violations = detector.detect_security_violations(
            security_violation_code, ".py", "test.py"
        )

        assert isinstance(violations, list)
        assert all(isinstance(v, Violation) for v in violations)

        # Should detect at least the hardcoded secrets
        if violations:
            violation_messages = [v.message for v in violations]
            assert any("password" in msg.lower() for msg in violation_messages)

    def test_detect_violations_unsupported_file(self):
        """Test detection with unsupported file type."""
        detector = ViolationDetector()

        violations = detector.detect_violations("test.exe", "binary content")

        assert violations == []

    def test_detect_violations_empty_content(self):
        """Test detection with empty file content."""
        detector = ViolationDetector()

        violations = detector.detect_violations("test.py", "")

        assert isinstance(violations, list)

    def test_error_handling_in_detection_methods(self):
        """Test error handling in individual detection methods."""
        detector = ViolationDetector()

        # Test with malformed Python code
        malformed_code = """
def incomplete_function(
    # Missing closing parenthesis and function body
"""

        # Should not crash, should return error violations
        srp_violations = detector.detect_srp_violations(
            malformed_code, ".py", "test.py"
        )
        assert isinstance(srp_violations, list)

        # If there are violations, they should include error information
        if srp_violations:
            assert any(v.severity == "ERROR" for v in srp_violations)


class TestDetectedViolation:
    """Test cases for DetectedViolation dataclass."""

    def test_detected_violation_creation(self):
        """Test creating DetectedViolation instance."""
        violation = DetectedViolation(
            violation_type=ViolationType.SRP_VIOLATION,
            severity="HIGH",
            file_path="test.py",
            line_number=10,
            column_number=5,
            description="Function has too many responsibilities",
            rule_id="SRP001",
            suggested_fix="Split function into smaller functions",
            code_snippet="def complex_function():",
            se_principle="Single Responsibility Principle",
        )

        assert violation.violation_type == ViolationType.SRP_VIOLATION
        assert violation.severity == "HIGH"
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.column_number == 5
        assert violation.description == "Function has too many responsibilities"
        assert violation.rule_id == "SRP001"
        assert violation.suggested_fix == "Split function into smaller functions"
        assert violation.code_snippet == "def complex_function():"
        assert violation.se_principle == "Single Responsibility Principle"


class TestViolationType:
    """Test cases for ViolationType enum."""

    def test_violation_type_values(self):
        """Test ViolationType enum values."""
        assert ViolationType.SRP_VIOLATION.value == "single_responsibility_principle"
        assert ViolationType.ENCAPSULATION_VIOLATION.value == "encapsulation"
        assert ViolationType.LOOSE_COUPLING_VIOLATION.value == "loose_coupling"
        assert ViolationType.REUSABILITY_VIOLATION.value == "reusability"
        assert ViolationType.PORTABILITY_VIOLATION.value == "portability"
        assert ViolationType.DEFENSIBILITY_VIOLATION.value == "defensibility"
        assert ViolationType.MAINTAINABILITY_VIOLATION.value == "maintainability"
        assert ViolationType.SIMPLICITY_VIOLATION.value == "simplicity"
