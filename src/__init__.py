"""
TeamReel Constitutional Foundation Package

This package provides the core constitutional validation engine and supporting components
for enforcing TeamReel's Software Development Design (SDD) principles across the platform.

SE Principles Focus:
- SRP: Each module has a single, well-defined responsibility
- Encapsulation: Clean public APIs hide internal implementation details
- Loose Coupling: Minimal dependencies between components
- Reusability: Components can be used across different contexts
- Portability: Works consistently across platforms and environments
- Defensibility: Robust error handling and input validation
- Maintainability: Clear code structure and comprehensive testing
- Simplicity: Straightforward architecture without over-engineering
"""

from .constitutional_validator import ConstitutionalValidator, ValidationScope
from .compliance_reporter import ComplianceReport, Violation
from .violation_detector import ViolationDetector
from .quality_gates import QualityGateValidator
from .naming_validator import NamingValidator
from .coverage_validator import CoverageValidator
from .complexity_analyzer import ComplexityAnalyzer
from .security_scanner import SecurityScanner

__version__ = "1.0.0"
__author__ = "TeamReel Engineering"

# Public API
__all__ = [
    "ConstitutionalValidator",
    "ValidationScope",
    "ComplianceReport",
    "Violation",
    "ViolationDetector",
    "QualityGateValidator",
    "NamingValidator",
    "CoverageValidator",
    "ComplexityAnalyzer",
    "SecurityScanner",
]
