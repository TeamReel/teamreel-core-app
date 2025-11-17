#!/usr/bin/env python3
"""
Naming Convention Validator - Code Naming Standards Quality Gate

This module validates naming conventions across multiple programming languages
and enforces project's constitutional naming standards as part of the quality
gates system.

Part of project's SDD Constitutional Foundation & Enforcement system.
"""

import ast
import json
import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class NamingConvention(Enum):
    """Supported naming conventions."""

    SNAKE_CASE = "snake_case"  # user_profile, get_data
    KEBAB_CASE = "kebab-case"  # user-profile, get-data
    CAMEL_CASE = "camelCase"  # userProfile, getData
    PASCAL_CASE = "PascalCase"  # UserProfile, GetData
    UPPER_SNAKE_CASE = "UPPER_SNAKE_CASE"  # MAX_SIZE, DEFAULT_TIMEOUT


@dataclass
class NamingIssue:
    """Represents a naming convention violation."""

    filename: str
    line_number: int
    element_type: str  # function, variable, class, constant, etc.
    element_name: str
    expected_convention: NamingConvention
    actual_convention: Optional[NamingConvention]
    suggestion: str


@dataclass
class FileNamingReport:
    """Naming analysis for a single file."""

    filename: str
    total_violations: int
    function_violations: int
    variable_violations: int
    class_violations: int
    constant_violations: int
    violations: List[NamingIssue] = field(default_factory=list)


@dataclass
class NamingReport:
    """Complete naming convention analysis report."""

    total_files: int
    total_violations: int
    function_violations: int
    variable_violations: int
    class_violations: int
    constant_violations: int
    files: List[FileNamingReport] = field(default_factory=list)
    violations: List[NamingIssue] = field(default_factory=list)
    is_passing: bool = True
    remediation_suggestions: List[str] = field(default_factory=list)


class NamingValidator:
    """Validates naming conventions across multiple languages."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize naming validator with configuration."""
        self.config = config or self._default_config()
        self.exclude_patterns = self.config.get("naming", {}).get(
            "exclude",
            [
                "*/tests/*",
                "*/test/*",
                "*/__pycache__/*",
                "*/node_modules/*",
                "*/migrations/*",
                "**/conftest.py",
            ],
        )

        # project naming conventions (from constitutional requirements)
        self.python_conventions = self.config.get("naming", {}).get(
            "python",
            {
                "functions": NamingConvention.SNAKE_CASE,
                "variables": NamingConvention.SNAKE_CASE,
                "classes": NamingConvention.PASCAL_CASE,
                "constants": NamingConvention.UPPER_SNAKE_CASE,
                "modules": NamingConvention.SNAKE_CASE,
            },
        )

        self.javascript_conventions = self.config.get("naming", {}).get(
            "javascript",
            {
                "functions": NamingConvention.CAMEL_CASE,
                "variables": NamingConvention.CAMEL_CASE,
                "classes": NamingConvention.PASCAL_CASE,
                "constants": NamingConvention.UPPER_SNAKE_CASE,
                "components": NamingConvention.PASCAL_CASE,
            },
        )

        self.api_conventions = self.config.get("naming", {}).get(
            "api",
            {
                "endpoints": NamingConvention.KEBAB_CASE,
                "parameters": NamingConvention.SNAKE_CASE,
            },
        )

    def _default_config(self) -> Dict:
        """Default configuration for naming validation."""
        return {
            "naming": {
                "exclude": [
                    "*/tests/*",
                    "*/test/*",
                    "*/__pycache__/*",
                    "*/node_modules/*",
                    "*/migrations/*",
                    "**/conftest.py",
                ],
                "python": {
                    "functions": "snake_case",
                    "variables": "snake_case",
                    "classes": "PascalCase",
                    "constants": "UPPER_SNAKE_CASE",
                    "modules": "snake_case",
                },
                "javascript": {
                    "functions": "camelCase",
                    "variables": "camelCase",
                    "classes": "PascalCase",
                    "constants": "UPPER_SNAKE_CASE",
                    "components": "PascalCase",
                },
                "api": {"endpoints": "kebab-case", "parameters": "snake_case"},
            }
        }

    def validate_python_naming(self, project_dir: str = ".") -> NamingReport:
        """Validate Python naming conventions."""
        python_files = list(Path(project_dir).rglob("*.py"))
        python_files = [
            f for f in python_files if not self._should_exclude_file(str(f))
        ]

        if not python_files:
            return NamingReport(
                total_files=0,
                total_violations=0,
                function_violations=0,
                variable_violations=0,
                class_violations=0,
                constant_violations=0,
                is_passing=True,
                remediation_suggestions=["No Python files found to validate"],
            )

        all_violations = []
        files = []

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(py_file))
                file_violations = self._validate_python_ast(tree, str(py_file))

                if file_violations:
                    all_violations.extend(file_violations)

                    file_report = FileNamingReport(
                        filename=str(py_file),
                        total_violations=len(file_violations),
                        function_violations=len(
                            [v for v in file_violations if v.element_type == "function"]
                        ),
                        variable_violations=len(
                            [v for v in file_violations if v.element_type == "variable"]
                        ),
                        class_violations=len(
                            [v for v in file_violations if v.element_type == "class"]
                        ),
                        constant_violations=len(
                            [v for v in file_violations if v.element_type == "constant"]
                        ),
                        violations=file_violations,
                    )

                    files.append(file_report)

            except Exception as e:
                print(f"Warning: Could not validate {py_file}: {e}")
                continue

        # Count violations by type
        function_violations = len(
            [v for v in all_violations if v.element_type == "function"]
        )
        variable_violations = len(
            [v for v in all_violations if v.element_type == "variable"]
        )
        class_violations = len([v for v in all_violations if v.element_type == "class"])
        constant_violations = len(
            [v for v in all_violations if v.element_type == "constant"]
        )

        suggestions = self._generate_python_suggestions(all_violations)

        return NamingReport(
            total_files=len(python_files),
            total_violations=len(all_violations),
            function_violations=function_violations,
            variable_violations=variable_violations,
            class_violations=class_violations,
            constant_violations=constant_violations,
            files=files,
            violations=all_violations,
            is_passing=len(all_violations) == 0,
            remediation_suggestions=suggestions,
        )

    def _validate_python_ast(self, tree: ast.AST, filename: str) -> List[NamingIssue]:
        """Validate Python AST for naming conventions."""
        visitor = PythonNamingVisitor(filename, self.python_conventions)
        visitor.visit(tree)
        return visitor.violations

    def validate_javascript_naming(self, project_dir: str = ".") -> NamingReport:
        """Validate JavaScript/TypeScript naming conventions."""
        js_files = (
            list(Path(project_dir).rglob("*.js"))
            + list(Path(project_dir).rglob("*.ts"))
            + list(Path(project_dir).rglob("*.jsx"))
            + list(Path(project_dir).rglob("*.tsx"))
        )

        js_files = [f for f in js_files if not self._should_exclude_file(str(f))]

        if not js_files:
            return NamingReport(
                total_files=0,
                total_violations=0,
                function_violations=0,
                variable_violations=0,
                class_violations=0,
                constant_violations=0,
                is_passing=True,
                remediation_suggestions=[
                    "No JavaScript/TypeScript files found to validate"
                ],
            )

        all_violations = []
        files = []

        for js_file in js_files:
            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                file_violations = self._validate_javascript_content(
                    content, str(js_file)
                )

                if file_violations:
                    all_violations.extend(file_violations)

                    file_report = FileNamingReport(
                        filename=str(js_file),
                        total_violations=len(file_violations),
                        function_violations=len(
                            [v for v in file_violations if v.element_type == "function"]
                        ),
                        variable_violations=len(
                            [v for v in file_violations if v.element_type == "variable"]
                        ),
                        class_violations=len(
                            [v for v in file_violations if v.element_type == "class"]
                        ),
                        constant_violations=len(
                            [v for v in file_violations if v.element_type == "constant"]
                        ),
                        violations=file_violations,
                    )

                    files.append(file_report)

            except Exception as e:
                print(f"Warning: Could not validate {js_file}: {e}")
                continue

        # Count violations by type
        function_violations = len(
            [v for v in all_violations if v.element_type == "function"]
        )
        variable_violations = len(
            [v for v in all_violations if v.element_type == "variable"]
        )
        class_violations = len([v for v in all_violations if v.element_type == "class"])
        constant_violations = len(
            [v for v in all_violations if v.element_type == "constant"]
        )

        suggestions = self._generate_javascript_suggestions(all_violations)

        return NamingReport(
            total_files=len(js_files),
            total_violations=len(all_violations),
            function_violations=function_violations,
            variable_violations=variable_violations,
            class_violations=class_violations,
            constant_violations=constant_violations,
            files=files,
            violations=all_violations,
            is_passing=len(all_violations) == 0,
            remediation_suggestions=suggestions,
        )

    def _validate_javascript_content(
        self, content: str, filename: str
    ) -> List[NamingIssue]:
        """Validate JavaScript content using regex patterns."""
        violations = []
        lines = content.split("\n")

        # Patterns for different JavaScript constructs
        patterns = {
            "function": [
                r"function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",  # function declarations
                r"const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?\(",  # arrow functions
                r"([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?function",  # method definitions
                r"([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*=>",  # arrow functions
            ],
            "variable": [
                r"(?:let|const|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",  # variable declarations
            ],
            "class": [
                r"class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",  # class declarations
            ],
            "constant": [
                r"const\s+([A-Z_][A-Z0-9_]*)\s*=",  # constants (all caps)
            ],
        }

        # React component pattern
        component_pattern = r"(?:function|const)\s+([A-Z][a-zA-Z0-9]*)\s*[=\(]"

        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("/*"):
                continue

            # Check React components
            component_match = re.search(component_pattern, line)
            if component_match:
                component_name = component_match.group(1)
                expected_convention = self.javascript_conventions.get(
                    "components", NamingConvention.PASCAL_CASE
                )
                actual_convention = self._detect_naming_convention(component_name)

                if actual_convention != expected_convention:
                    suggestion = self._get_naming_suggestion(
                        component_name, expected_convention
                    )
                    violation = NamingIssue(
                        filename=filename,
                        line_number=line_no,
                        element_type="component",
                        element_name=component_name,
                        expected_convention=expected_convention,
                        actual_convention=actual_convention,
                        suggestion=suggestion,
                    )
                    violations.append(violation)
                continue

            # Check other constructs
            for element_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        name = match.group(1)

                        # Skip certain names
                        if self._should_skip_js_name(name, element_type):
                            continue

                        expected_convention = self.javascript_conventions.get(
                            element_type + "s", NamingConvention.CAMEL_CASE
                        )
                        actual_convention = self._detect_naming_convention(name)

                        if actual_convention != expected_convention:
                            suggestion = self._get_naming_suggestion(
                                name, expected_convention
                            )
                            violation = NamingIssue(
                                filename=filename,
                                line_number=line_no,
                                element_type=element_type,
                                element_name=name,
                                expected_convention=expected_convention,
                                actual_convention=actual_convention,
                                suggestion=suggestion,
                            )
                            violations.append(violation)

        return violations

    def validate_api_endpoints(self, project_dir: str = ".") -> NamingReport:
        """Validate API endpoint naming conventions."""
        violations = []

        # Look for Django URLs
        django_files = list(Path(project_dir).rglob("*urls.py"))
        for url_file in django_files:
            if self._should_exclude_file(str(url_file)):
                continue

            try:
                with open(url_file, "r", encoding="utf-8") as f:
                    content = f.read()

                violations.extend(self._validate_django_urls(content, str(url_file)))
            except Exception as e:
                print(f"Warning: Could not validate {url_file}: {e}")

        # Look for Express.js routes
        js_files = list(Path(project_dir).rglob("*.js")) + list(
            Path(project_dir).rglob("*.ts")
        )
        for js_file in js_files:
            if self._should_exclude_file(str(js_file)):
                continue

            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                violations.extend(self._validate_express_routes(content, str(js_file)))
            except Exception as e:
                print(f"Warning: Could not validate routes in {js_file}: {e}")

        suggestions = self._generate_api_suggestions(violations)

        return NamingReport(
            total_files=len(django_files) + len(js_files),
            total_violations=len(violations),
            function_violations=0,
            variable_violations=0,
            class_violations=0,
            constant_violations=0,
            violations=violations,
            is_passing=len(violations) == 0,
            remediation_suggestions=suggestions,
        )

    def _validate_django_urls(self, content: str, filename: str) -> List[NamingIssue]:
        """Validate Django URL patterns."""
        violations = []
        lines = content.split("\n")

        # Pattern for Django URL patterns
        url_pattern = r'path\s*\(\s*[\'"]([^\'"]*)[\'"]\s*,'

        for line_no, line in enumerate(lines, 1):
            matches = re.finditer(url_pattern, line)
            for match in matches:
                url_path = match.group(1)

                # Skip empty paths, parameters, and regex
                if (
                    not url_path
                    or "<" in url_path
                    or "^" in url_path
                    or "$" in url_path
                ):
                    continue

                # Extract path segments
                segments = [seg for seg in url_path.split("/") if seg]

                for segment in segments:
                    if not segment or segment.startswith("<"):  # Skip parameters
                        continue

                    expected_convention = self.api_conventions.get(
                        "endpoints", NamingConvention.KEBAB_CASE
                    )
                    actual_convention = self._detect_naming_convention(segment)

                    if actual_convention != expected_convention:
                        suggestion = self._get_naming_suggestion(
                            segment, expected_convention
                        )
                        violation = NamingIssue(
                            filename=filename,
                            line_number=line_no,
                            element_type="endpoint",
                            element_name=segment,
                            expected_convention=expected_convention,
                            actual_convention=actual_convention,
                            suggestion=suggestion,
                        )
                        violations.append(violation)

        return violations

    def _validate_express_routes(
        self, content: str, filename: str
    ) -> List[NamingIssue]:
        """Validate Express.js route patterns."""
        violations = []
        lines = content.split("\n")

        # Pattern for Express routes
        route_pattern = r'(?:app|router)\.\w+\s*\(\s*[\'"]([^\'"]*)[\'"]\s*,'

        for line_no, line in enumerate(lines, 1):
            matches = re.finditer(route_pattern, line)
            for match in matches:
                route_path = match.group(1)

                # Skip empty paths, parameters, and wildcards
                if not route_path or ":" in route_path or "*" in route_path:
                    continue

                # Extract path segments
                segments = [seg for seg in route_path.split("/") if seg]

                for segment in segments:
                    if not segment or segment.startswith(":"):  # Skip parameters
                        continue

                    expected_convention = self.api_conventions.get(
                        "endpoints", NamingConvention.KEBAB_CASE
                    )
                    actual_convention = self._detect_naming_convention(segment)

                    if actual_convention != expected_convention:
                        suggestion = self._get_naming_suggestion(
                            segment, expected_convention
                        )
                        violation = NamingIssue(
                            filename=filename,
                            line_number=line_no,
                            element_type="endpoint",
                            element_name=segment,
                            expected_convention=expected_convention,
                            actual_convention=actual_convention,
                            suggestion=suggestion,
                        )
                        violations.append(violation)

        return violations

    def validate_naming_conventions(
        self, project_dir: str = "."
    ) -> Dict[str, NamingReport]:
        """Validate naming conventions for all supported languages."""
        results = {}

        # Check for Python files
        python_files = list(Path(project_dir).rglob("*.py"))
        if python_files:
            print("🐍 Validating Python naming conventions...")
            results["python"] = self.validate_python_naming(project_dir)

        # Check for JavaScript/TypeScript files
        js_files = (
            list(Path(project_dir).rglob("*.js"))
            + list(Path(project_dir).rglob("*.ts"))
            + list(Path(project_dir).rglob("*.jsx"))
            + list(Path(project_dir).rglob("*.tsx"))
        )
        if js_files:
            print("📦 Validating JavaScript/TypeScript naming conventions...")
            results["javascript"] = self.validate_javascript_naming(project_dir)

        # Check for API endpoints
        url_files = (
            list(Path(project_dir).rglob("*urls.py"))
            + list(Path(project_dir).rglob("*routes.js"))
            + list(Path(project_dir).rglob("*routes.ts"))
        )
        if url_files:
            print("🌐 Validating API endpoint naming conventions...")
            results["api"] = self.validate_api_endpoints(project_dir)

        if not results:
            results["none"] = NamingReport(
                total_files=0,
                total_violations=0,
                function_violations=0,
                variable_violations=0,
                class_violations=0,
                constant_violations=0,
                is_passing=True,
                remediation_suggestions=["No source files found to validate"],
            )

        return results

    def _detect_naming_convention(self, name: str) -> Optional[NamingConvention]:
        """Detect the naming convention used in a name."""
        if not name:
            return None

        # UPPER_SNAKE_CASE (constants)
        if re.match(r"^[A-Z][A-Z0-9_]*$", name):
            return NamingConvention.UPPER_SNAKE_CASE

        # snake_case
        if re.match(r"^[a-z][a-z0-9_]*$", name):
            return NamingConvention.SNAKE_CASE

        # kebab-case
        if re.match(r"^[a-z][a-z0-9-]*$", name):
            return NamingConvention.KEBAB_CASE

        # PascalCase
        if re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
            return NamingConvention.PASCAL_CASE

        # camelCase
        if re.match(r"^[a-z][a-zA-Z0-9]*$", name):
            return NamingConvention.CAMEL_CASE

        return None

    def _get_naming_suggestion(
        self, name: str, target_convention: NamingConvention
    ) -> str:
        """Generate a suggestion for correct naming."""
        if target_convention == NamingConvention.SNAKE_CASE:
            suggestion = self._to_snake_case(name)
        elif target_convention == NamingConvention.KEBAB_CASE:
            suggestion = self._to_kebab_case(name)
        elif target_convention == NamingConvention.CAMEL_CASE:
            suggestion = self._to_camel_case(name)
        elif target_convention == NamingConvention.PASCAL_CASE:
            suggestion = self._to_pascal_case(name)
        elif target_convention == NamingConvention.UPPER_SNAKE_CASE:
            suggestion = self._to_upper_snake_case(name)
        else:
            suggestion = name

        return f"Consider renaming '{name}' to '{suggestion}'"

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Handle camelCase and PascalCase
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        # Handle kebab-case
        name = name.replace("-", "_")
        return name.lower()

    def _to_kebab_case(self, name: str) -> str:
        """Convert name to kebab-case."""
        # Handle camelCase and PascalCase
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
        # Handle snake_case
        name = name.replace("_", "-")
        return name.lower()

    def _to_camel_case(self, name: str) -> str:
        """Convert name to camelCase."""
        # Handle snake_case and kebab-case
        parts = re.split(r"[_-]", name.lower())
        if len(parts) == 1:
            return parts[0].lower()
        return parts[0].lower() + "".join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        # Handle snake_case and kebab-case
        parts = re.split(r"[_-]", name.lower())
        return "".join(word.capitalize() for word in parts)

    def _to_upper_snake_case(self, name: str) -> str:
        """Convert name to UPPER_SNAKE_CASE."""
        return self._to_snake_case(name).upper()

    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded from naming validation."""
        for pattern in self.exclude_patterns:
            if pattern.replace("*", "").replace("/", "") in filename:
                return True
        return False

    def _should_skip_python_name(self, name: str, element_type: str) -> bool:
        """Check if Python name should be skipped."""
        # Skip dunder methods and common Python names
        skip_names = {
            "__init__",
            "__str__",
            "__repr__",
            "__len__",
            "__call__",
            "__enter__",
            "__exit__",
            "__iter__",
            "__next__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__contains__",
            "__eq__",
            "__ne__",
            "__lt__",
            "__le__",
            "__gt__",
            "__ge__",
            "__hash__",
            "__bool__",
            "setUp",
            "tearDown",
            "setUpClass",
            "tearDownClass",  # unittest
        }

        if name in skip_names:
            return True

        # Skip single letter variables
        if element_type == "variable" and len(name) == 1:
            return True

        # Skip private names (starting with _)
        if name.startswith("_"):
            return True

        return False

    def _should_skip_js_name(self, name: str, element_type: str) -> bool:
        """Check if JavaScript name should be skipped."""
        # Skip common JS/React names
        skip_names = {
            "React",
            "Component",
            "useState",
            "useEffect",
            "useContext",
            "useReducer",
            "useCallback",
            "useMemo",
            "useRef",
            "useImperativeHandle",
            "useLayoutEffect",
            "useDebugValue",
            "props",
            "state",
            "render",
            "componentDidMount",
            "componentDidUpdate",
            "componentWillUnmount",
        }

        if name in skip_names:
            return True

        # Skip single letter variables
        if element_type == "variable" and len(name) == 1:
            return True

        return False

    def _generate_python_suggestions(self, violations: List[NamingIssue]) -> List[str]:
        """Generate remediation suggestions for Python naming issues."""
        if not violations:
            return ["All Python names follow proper conventions!"]

        suggestions = []
        suggestions.append(
            f"Found {len(violations)} Python naming convention violations"
        )

        # Count by type
        type_counts = {}
        for violation in violations:
            type_counts[violation.element_type] = (
                type_counts.get(violation.element_type, 0) + 1
            )

        if type_counts:
            suggestions.append("Violations by type:")
            for element_type, count in type_counts.items():
                suggestions.append(f"- {element_type}s: {count} violations")

        suggestions.extend(
            [
                "",
                "Python naming conventions (project Constitutional Requirements):",
                "- Functions: snake_case (get_user_data, calculate_total)",
                "- Variables: snake_case (user_name, total_count)",
                "- Classes: PascalCase (UserProfile, DataProcessor)",
                "- Constants: UPPER_SNAKE_CASE (MAX_SIZE, DEFAULT_TIMEOUT)",
                "- Modules: snake_case (user_utils, data_processing)",
            ]
        )

        # Show worst violations
        if len(violations) > 5:
            suggestions.append(f"\nTop violations to fix first:")
            for violation in violations[:5]:
                suggestions.append(
                    f"- {violation.filename}:{violation.line_number} {violation.element_name}"
                )

        return suggestions

    def _generate_javascript_suggestions(
        self, violations: List[NamingIssue]
    ) -> List[str]:
        """Generate remediation suggestions for JavaScript naming issues."""
        if not violations:
            return ["All JavaScript names follow proper conventions!"]

        suggestions = []
        suggestions.append(
            f"Found {len(violations)} JavaScript naming convention violations"
        )

        # Count by type
        type_counts = {}
        for violation in violations:
            type_counts[violation.element_type] = (
                type_counts.get(violation.element_type, 0) + 1
            )

        if type_counts:
            suggestions.append("Violations by type:")
            for element_type, count in type_counts.items():
                suggestions.append(f"- {element_type}s: {count} violations")

        suggestions.extend(
            [
                "",
                "JavaScript naming conventions (project Constitutional Requirements):",
                "- Functions: camelCase (getUserData, calculateTotal)",
                "- Variables: camelCase (userName, totalCount)",
                "- Classes: PascalCase (UserProfile, DataProcessor)",
                "- Constants: UPPER_SNAKE_CASE (MAX_SIZE, DEFAULT_TIMEOUT)",
                "- React Components: PascalCase (UserProfile, VideoWorkflow)",
            ]
        )

        # Show worst violations
        if len(violations) > 5:
            suggestions.append(f"\nTop violations to fix first:")
            for violation in violations[:5]:
                suggestions.append(
                    f"- {violation.filename}:{violation.line_number} {violation.element_name}"
                )

        return suggestions

    def _generate_api_suggestions(self, violations: List[NamingIssue]) -> List[str]:
        """Generate remediation suggestions for API naming issues."""
        if not violations:
            return ["All API endpoints follow proper conventions!"]

        suggestions = []
        suggestions.append(f"Found {len(violations)} API endpoint naming violations")

        suggestions.extend(
            [
                "",
                "API naming conventions (project Constitutional Requirements):",
                "- Endpoints: kebab-case with trailing slashes (/user-profiles/, /video-workflows/)",
                "- Parameters: snake_case (user_id, workflow_type)",
                "",
                "Examples:",
                "- Good: /api/user-profiles/{id}/video-workflows/",
                "- Bad: /api/userProfiles/{id}/videoWorkflows/",
                "- Good: /api/ai-tasks/{task_id}/results/",
                "- Bad: /api/aiTasks/{taskId}/results/",
            ]
        )

        return suggestions

    def format_report(
        self, reports: Dict[str, NamingReport], format_type: str = "terminal"
    ) -> str:
        """Format naming convention analysis report."""
        if format_type == "json":
            return json.dumps(
                {
                    lang: {
                        "total_files": report.total_files,
                        "total_violations": report.total_violations,
                        "function_violations": report.function_violations,
                        "variable_violations": report.variable_violations,
                        "class_violations": report.class_violations,
                        "constant_violations": report.constant_violations,
                        "is_passing": report.is_passing,
                        "violations": [
                            {
                                "filename": v.filename,
                                "line_number": v.line_number,
                                "element_type": v.element_type,
                                "element_name": v.element_name,
                                "expected_convention": v.expected_convention.value,
                                "actual_convention": (
                                    v.actual_convention.value
                                    if v.actual_convention
                                    else None
                                ),
                                "suggestion": v.suggestion,
                            }
                            for v in report.violations
                        ],
                    }
                    for lang, report in reports.items()
                },
                indent=2,
            )

        # Terminal format
        output = []
        output.append("📝 NAMING CONVENTION VALIDATION REPORT")
        output.append("=" * 55)

        overall_passing = all(report.is_passing for report in reports.values())
        total_violations = sum(report.total_violations for report in reports.values())

        for lang, report in reports.items():
            if lang == "none":
                continue

            output.append(f"\n{lang.upper()} Naming Conventions:")
            output.append(f"  Files analyzed: {report.total_files}")
            output.append(f"  Total violations: {report.total_violations}")

            if report.total_violations > 0:
                output.append(f"    Functions: {report.function_violations}")
                output.append(f"    Variables: {report.variable_violations}")
                output.append(f"    Classes: {report.class_violations}")
                output.append(f"    Constants: {report.constant_violations}")

            output.append(f"  Status: {'✅ PASS' if report.is_passing else '❌ FAIL'}")

            if report.violations:
                # Show worst violations
                output.append("  Top violations:")
                for violation in report.violations[:5]:
                    output.append(
                        f"    • {violation.filename}:{violation.line_number} - {violation.element_name} ({violation.element_type})"
                    )

        output.append(f"\n{'='*55}")
        output.append(f"Total violations: {total_violations}")
        output.append(f"Overall Status: {'✅ PASS' if overall_passing else '❌ FAIL'}")

        if not overall_passing:
            output.append(
                "\n❌ Naming convention validation failed. Please fix naming violations."
            )
            # Show remediation suggestions
            for lang, report in reports.items():
                if report.violations and report.remediation_suggestions:
                    output.append(f"\n{lang.upper()} Naming Guidelines:")
                    for suggestion in report.remediation_suggestions[:7]:
                        output.append(f"  • {suggestion}")
        else:
            output.append("\n✅ All names follow proper naming conventions!")

        return "\n".join(output)


class PythonNamingVisitor(ast.NodeVisitor):
    """AST visitor to validate Python naming conventions."""

    def __init__(self, filename: str, conventions: Dict[str, NamingConvention]):
        self.filename = filename
        self.conventions = conventions
        self.violations = []
        self.current_class = None

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        if not self._should_skip_python_name(node.name, "function"):
            expected_convention = self.conventions.get(
                "functions", NamingConvention.SNAKE_CASE
            )
            actual_convention = self._detect_naming_convention(node.name)

            if actual_convention != expected_convention:
                suggestion = self._get_naming_suggestion(node.name, expected_convention)
                violation = NamingIssue(
                    filename=self.filename,
                    line_number=node.lineno,
                    element_type="function",
                    element_name=node.name,
                    expected_convention=expected_convention,
                    actual_convention=actual_convention,
                    suggestion=suggestion,
                )
                self.violations.append(violation)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definition."""
        old_class = self.current_class
        self.current_class = node.name

        expected_convention = self.conventions.get(
            "classes", NamingConvention.PASCAL_CASE
        )
        actual_convention = self._detect_naming_convention(node.name)

        if actual_convention != expected_convention:
            suggestion = self._get_naming_suggestion(node.name, expected_convention)
            violation = NamingIssue(
                filename=self.filename,
                line_number=node.lineno,
                element_type="class",
                element_name=node.name,
                expected_convention=expected_convention,
                actual_convention=actual_convention,
                suggestion=suggestion,
            )
            self.violations.append(violation)

        self.generic_visit(node)
        self.current_class = old_class

    def visit_Assign(self, node):
        """Visit assignment (for variables and constants)."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id

                if self._should_skip_python_name(name, "variable"):
                    continue

                # Detect if it's a constant (all uppercase)
                if name.isupper():
                    element_type = "constant"
                    expected_convention = self.conventions.get(
                        "constants", NamingConvention.UPPER_SNAKE_CASE
                    )
                else:
                    element_type = "variable"
                    expected_convention = self.conventions.get(
                        "variables", NamingConvention.SNAKE_CASE
                    )

                actual_convention = self._detect_naming_convention(name)

                if actual_convention != expected_convention:
                    suggestion = self._get_naming_suggestion(name, expected_convention)
                    violation = NamingIssue(
                        filename=self.filename,
                        line_number=node.lineno,
                        element_type=element_type,
                        element_name=name,
                        expected_convention=expected_convention,
                        actual_convention=actual_convention,
                        suggestion=suggestion,
                    )
                    self.violations.append(violation)

        self.generic_visit(node)

    def _detect_naming_convention(self, name: str) -> Optional[NamingConvention]:
        """Detect the naming convention used in a name."""
        if not name:
            return None

        # UPPER_SNAKE_CASE (constants)
        if re.match(r"^[A-Z][A-Z0-9_]*$", name):
            return NamingConvention.UPPER_SNAKE_CASE

        # snake_case
        if re.match(r"^[a-z][a-z0-9_]*$", name):
            return NamingConvention.SNAKE_CASE

        # PascalCase
        if re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
            return NamingConvention.PASCAL_CASE

        # camelCase
        if re.match(r"^[a-z][a-zA-Z0-9]*$", name):
            return NamingConvention.CAMEL_CASE

        return None

    def _get_naming_suggestion(
        self, name: str, target_convention: NamingConvention
    ) -> str:
        """Generate a suggestion for correct naming."""
        if target_convention == NamingConvention.SNAKE_CASE:
            suggestion = self._to_snake_case(name)
        elif target_convention == NamingConvention.CAMEL_CASE:
            suggestion = self._to_camel_case(name)
        elif target_convention == NamingConvention.PASCAL_CASE:
            suggestion = self._to_pascal_case(name)
        elif target_convention == NamingConvention.UPPER_SNAKE_CASE:
            suggestion = self._to_upper_snake_case(name)
        else:
            suggestion = name

        return f"Consider renaming '{name}' to '{suggestion}'"

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Handle camelCase and PascalCase
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

    def _to_camel_case(self, name: str) -> str:
        """Convert name to camelCase."""
        parts = name.split("_")
        if len(parts) == 1:
            return parts[0].lower()
        return parts[0].lower() + "".join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        parts = name.split("_")
        return "".join(word.capitalize() for word in parts)

    def _to_upper_snake_case(self, name: str) -> str:
        """Convert name to UPPER_SNAKE_CASE."""
        return self._to_snake_case(name).upper()

    def _should_skip_python_name(self, name: str, element_type: str) -> bool:
        """Check if Python name should be skipped."""
        # Skip dunder methods and common Python names
        skip_names = {
            "__init__",
            "__str__",
            "__repr__",
            "__len__",
            "__call__",
            "__enter__",
            "__exit__",
            "__iter__",
            "__next__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__contains__",
            "__eq__",
            "__ne__",
            "__lt__",
            "__le__",
            "__gt__",
            "__ge__",
            "__hash__",
            "__bool__",
            "setUp",
            "tearDown",
            "setUpClass",
            "tearDownClass",  # unittest
        }

        if name in skip_names:
            return True

        # Skip single letter variables
        if element_type == "variable" and len(name) == 1:
            return True

        # Skip private names (starting with _)
        if name.startswith("_"):
            return True

        return False


def main():
    """CLI entry point for naming convention validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate naming conventions across multiple languages"
    )
    parser.add_argument(
        "--project-dir", default=".", help="Project directory to validate"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with error if violations found",
    )

    args = parser.parse_args()

    validator = NamingValidator()
    reports = validator.validate_naming_conventions(args.project_dir)

    # Output report
    print(validator.format_report(reports, args.format))

    # Exit with error if violations found
    if args.fail_on_violations:
        if not all(report.is_passing for report in reports.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
