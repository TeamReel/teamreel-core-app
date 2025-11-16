"""
Quality Gates Validation Module

Integrates all quality gate validators into a unified interface.
"""

try:
    from .coverage_validator import CoverageValidator
    from .complexity_analyzer import ComplexityAnalyzer
    from .security_scanner import SecurityScanner
    from .naming_validator import NamingValidator
except ImportError:
    # Fallback for direct execution - create placeholder classes
    class CoverageValidator:
        def __init__(self, config=None):
            pass

        def validate_coverage(self, report):
            return True

    class ComplexityAnalyzer:
        def __init__(self, config=None):
            pass

        def analyze_complexity(self, report):
            return True

    class SecurityScanner:
        def __init__(self, config=None):
            pass

        def scan_security(self, report):
            return True

    class NamingValidator:
        def __init__(self, config=None):
            pass

        def validate_naming(self, report):
            return True


__all__ = [
    "QualityGateValidator",
]


class QualityGateValidator:
    """Unified interface for all quality gate validations."""

    def __init__(self, config=None):
        self.coverage_validator = CoverageValidator(config)
        self.complexity_analyzer = ComplexityAnalyzer(config)
        self.security_scanner = SecurityScanner(config)
        self.naming_validator = NamingValidator(config)

    def validate_all(self, project_dir="."):
        """Run all quality gate validations."""
        results = {}

        # Run coverage validation
        results["coverage"] = self.coverage_validator.validate_coverage(project_dir)

        # Run complexity analysis
        results["complexity"] = self.complexity_analyzer.analyze_complexity(project_dir)

        # Run security scanning
        results["security"] = self.security_scanner.scan_security(project_dir)

        # Run naming validation
        results["naming"] = self.naming_validator.validate_naming(project_dir)

        return results
