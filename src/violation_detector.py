"""
TeamReel Constitutional Violation Detection System

Implements detailed SE principle violation detection using AST analysis, pattern matching,
and rule-based evaluation. Supports Python, JavaScript, TypeScript, YAML, JSON, and Markdown.

SE Principle Focus:
- Encapsulation: Private implementation details hidden in detection logic
- Loose Coupling: Modular detection per file type and SE principle
- Maintainability: Clear separation of concerns and extensible architecture
"""

import ast
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .compliance_reporter import Violation
except ImportError:
    # Fallback for direct execution
    from compliance_reporter import Violation


class ViolationType(Enum):
    """Classification of constitutional violations"""

    SRP_VIOLATION = "single_responsibility_principle"
    ENCAPSULATION_VIOLATION = "encapsulation"
    LOOSE_COUPLING_VIOLATION = "loose_coupling"
    REUSABILITY_VIOLATION = "reusability"
    PORTABILITY_VIOLATION = "portability"
    DEFENSIBILITY_VIOLATION = "defensibility"
    MAINTAINABILITY_VIOLATION = "maintainability"
    SIMPLICITY_VIOLATION = "simplicity"


@dataclass
class DetectedViolation:
    """Single violation instance with precise location and details"""

    violation_type: ViolationType
    severity: str  # "HIGH", "MEDIUM", "LOW"
    file_path: str
    line_number: int
    column_number: int
    description: str
    rule_id: str
    suggested_fix: str
    code_snippet: str
    se_principle: str


class PythonASTAnalyzer:
    """Analyzes Python AST for constitutional violations"""

    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.split("\n")
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError:
            self.tree = None

    def detect_srp_violations(self) -> List[DetectedViolation]:
        """Detect Single Responsibility Principle violations"""
        violations = []
        if not self.tree:
            return violations

        for node in ast.walk(self.tree):
            # Check for classes with too many responsibilities
            if isinstance(node, ast.ClassDef):
                method_count = len(
                    [n for n in node.body if isinstance(n, ast.FunctionDef)]
                )
                if (
                    method_count > 15
                ):  # High method count suggests multiple responsibilities
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.SRP_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Class '{node.name}' has {method_count} methods, suggesting multiple responsibilities",
                            rule_id="SRP-001",
                            suggested_fix="Consider splitting this class into smaller, more focused classes",
                            code_snippet=self._get_code_snippet(node.lineno, 3),
                            se_principle="Single Responsibility Principle",
                        )
                    )

            # Check for functions with high cyclomatic complexity
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.SRP_VIOLATION,
                            severity="HIGH",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Function '{node.name}' has cyclomatic complexity of {complexity}",
                            rule_id="SRP-002",
                            suggested_fix="Break this function into smaller, single-purpose functions",
                            code_snippet=self._get_code_snippet(node.lineno, 5),
                            se_principle="Single Responsibility Principle",
                        )
                    )

        return violations

    def detect_encapsulation_violations(self) -> List[DetectedViolation]:
        """Detect Encapsulation violations"""
        violations = []
        if not self.tree:
            return violations

        for node in ast.walk(self.tree):
            # Check for missing private attribute conventions
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        attr_name = target.attr
                        # Public attribute in class context that should be private
                        if not attr_name.startswith("_") and self._is_in_class_context(
                            node
                        ):
                            violations.append(
                                DetectedViolation(
                                    violation_type=ViolationType.ENCAPSULATION_VIOLATION,
                                    severity="LOW",
                                    file_path=self.file_path,
                                    line_number=node.lineno,
                                    column_number=node.col_offset,
                                    description=f"Attribute '{attr_name}' should be private (prefix with _)",
                                    rule_id="ENC-001",
                                    suggested_fix=f"Rename '{attr_name}' to '_{attr_name}' to make it private",
                                    code_snippet=self._get_code_snippet(node.lineno, 2),
                                    se_principle="Encapsulation",
                                )
                            )

            # Check for direct access to private attributes from outside class
            if isinstance(node, ast.Attribute):
                if node.attr.startswith("_") and not node.attr.startswith("__"):
                    if not self._is_same_class_access(node):
                        violations.append(
                            DetectedViolation(
                                violation_type=ViolationType.ENCAPSULATION_VIOLATION,
                                severity="MEDIUM",
                                file_path=self.file_path,
                                line_number=node.lineno,
                                column_number=node.col_offset,
                                description=f"Direct access to private attribute '{node.attr}' from outside its class",
                                rule_id="ENC-002",
                                suggested_fix="Use a public method or property to access this attribute",
                                code_snippet=self._get_code_snippet(node.lineno, 2),
                                se_principle="Encapsulation",
                            )
                        )

        return violations

    def detect_loose_coupling_violations(self) -> List[DetectedViolation]:
        """Detect Loose Coupling violations"""
        violations = []
        if not self.tree:
            return violations

        imports = self._get_all_imports()

        # Check for excessive imports (high coupling)
        if len(imports) > 20:
            violations.append(
                DetectedViolation(
                    violation_type=ViolationType.LOOSE_COUPLING_VIOLATION,
                    severity="MEDIUM",
                    file_path=self.file_path,
                    line_number=1,
                    column_number=0,
                    description=f"File has {len(imports)} imports, indicating high coupling",
                    rule_id="LC-001",
                    suggested_fix="Consider refactoring to reduce dependencies",
                    code_snippet=self._get_code_snippet(1, 10),
                    se_principle="Loose Coupling",
                )
            )

        # Check for circular imports (static analysis approximation)
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = None
                if isinstance(node, ast.Import):
                    module_name = node.names[0].name if node.names else None
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module

                if module_name and self._might_be_circular_import(module_name):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.LOOSE_COUPLING_VIOLATION,
                            severity="HIGH",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Potential circular import detected with module '{module_name}'",
                            rule_id="LC-002",
                            suggested_fix="Restructure modules to eliminate circular dependencies",
                            code_snippet=self._get_code_snippet(node.lineno, 2),
                            se_principle="Loose Coupling",
                        )
                    )

        return violations

    def detect_reusability_violations(self) -> List[DetectedViolation]:
        """Detect Reusability violations"""
        violations = []
        if not self.tree:
            return violations

        # Check for hardcoded values that should be configurable
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Str):  # String literals
                if self._is_hardcoded_config(node.s):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.REUSABILITY_VIOLATION,
                            severity="LOW",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Hardcoded value '{node.s}' should be configurable",
                            rule_id="REU-001",
                            suggested_fix="Move this value to a configuration file or constant",
                            code_snippet=self._get_code_snippet(node.lineno, 2),
                            se_principle="Reusability",
                        )
                    )

            # Check for code duplication (basic pattern matching)
            if isinstance(node, ast.FunctionDef):
                similar_functions = self._find_similar_functions(node)
                if similar_functions:
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.REUSABILITY_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Function '{node.name}' appears to have duplicated logic",
                            rule_id="REU-002",
                            suggested_fix="Extract common functionality into a shared utility function",
                            code_snippet=self._get_code_snippet(node.lineno, 3),
                            se_principle="Reusability",
                        )
                    )

        return violations

    def detect_portability_violations(self) -> List[DetectedViolation]:
        """Detect Portability violations"""
        violations = []
        if not self.tree:
            return violations

        # Check for platform-specific imports or code
        platform_specific_patterns = [
            r"import win32",
            r"import winsound",
            r"import msvcrt",
            r"/usr/",
            r"/bin/",
            r"C:\\",
            r"D:\\",
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern in platform_specific_patterns:
                if re.search(pattern, line):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.PORTABILITY_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=line.find(re.search(pattern, line).group()),
                            description=f"Platform-specific code detected: {pattern}",
                            rule_id="PORT-001",
                            suggested_fix="Use platform-agnostic alternatives or conditional imports",
                            code_snippet=self._get_code_snippet(line_num, 2),
                            se_principle="Portability",
                        )
                    )

        return violations

    def detect_defensibility_violations(self) -> List[DetectedViolation]:
        """Detect Defensibility (Security) violations"""
        violations = []
        if not self.tree:
            return violations

        # Check for potential security issues
        security_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous", "DEF-001"),
            (r"exec\s*\(", "Use of exec() is dangerous", "DEF-002"),
            (
                r'password\s*=\s*[\'"][^\'\"]+[\'"]',
                "Hardcoded password detected",
                "DEF-003",
            ),
            (
                r'api_key\s*=\s*[\'"][^\'\"]+[\'"]',
                "Hardcoded API key detected",
                "DEF-004",
            ),
            (
                r"subprocess\.call\s*\(.*shell\s*=\s*True",
                "Shell injection vulnerability",
                "DEF-005",
            ),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, description, rule_id in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.DEFENSIBILITY_VIOLATION,
                            severity="HIGH",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=0,
                            description=description,
                            rule_id=rule_id,
                            suggested_fix="Use secure alternatives and avoid hardcoded secrets",
                            code_snippet=self._get_code_snippet(line_num, 2),
                            se_principle="Defensibility",
                        )
                    )

        return violations

    def detect_maintainability_violations(self) -> List[DetectedViolation]:
        """Detect Maintainability violations"""
        violations = []
        if not self.tree:
            return violations

        # Check for missing docstrings
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.MAINTAINABILITY_VIOLATION,
                            severity="LOW",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"{node.__class__.__name__.lower().replace('def', '')} '{node.name}' is missing a docstring",
                            rule_id="MAIN-001",
                            suggested_fix="Add a descriptive docstring explaining the purpose and parameters",
                            code_snippet=self._get_code_snippet(node.lineno, 3),
                            se_principle="Maintainability",
                        )
                    )

        # Check for overly long functions
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                function_length = self._get_function_length(node)
                if function_length > 50:
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.MAINTAINABILITY_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Function '{node.name}' is {function_length} lines long",
                            rule_id="MAIN-002",
                            suggested_fix="Break this function into smaller, more manageable functions",
                            code_snippet=self._get_code_snippet(node.lineno, 3),
                            se_principle="Maintainability",
                        )
                    )

        return violations

    def detect_simplicity_violations(self) -> List[DetectedViolation]:
        """Detect Simplicity violations"""
        violations = []
        if not self.tree:
            return violations

        # Check for deeply nested code
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                max_nesting = self._calculate_max_nesting_depth(node)
                if max_nesting > 4:
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.SIMPLICITY_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Function '{node.name}' has nesting depth of {max_nesting}",
                            rule_id="SIMP-001",
                            suggested_fix="Reduce nesting using early returns or helper functions",
                            code_snippet=self._get_code_snippet(node.lineno, 3),
                            se_principle="Simplicity",
                        )
                    )

            # Check for complex boolean expressions
            if isinstance(node, ast.BoolOp):
                if len(node.values) > 3:
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.SIMPLICITY_VIOLATION,
                            severity="LOW",
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            description=f"Complex boolean expression with {len(node.values)} conditions",
                            rule_id="SIMP-002",
                            suggested_fix="Break complex boolean expressions into intermediate variables",
                            code_snippet=self._get_code_snippet(node.lineno, 2),
                            se_principle="Simplicity",
                        )
                    )

        return violations

    # Helper methods
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth in an AST node"""

        def get_depth(n, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(n):
                if isinstance(
                    child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)
                ):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth

        return get_depth(node)

    def _get_function_length(self, node: ast.FunctionDef) -> int:
        """Get the length of a function in lines"""
        if hasattr(node, "end_lineno") and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        # Fallback for older Python versions
        return len([n for n in ast.walk(node) if hasattr(n, "lineno")])

    def _is_in_class_context(self, node: ast.AST) -> bool:
        """Check if a node is within a class definition"""
        # This is a simplified check - in practice, you'd walk up the AST
        return "class " in self._get_code_snippet(node.lineno, 10)

    def _is_same_class_access(self, node: ast.Attribute) -> bool:
        """Check if attribute access is from within the same class"""
        # Simplified implementation - would need proper scope analysis
        return isinstance(node.value, ast.Name) and node.value.id == "self"

    def _get_all_imports(self) -> List[str]:
        """Get all import statements in the file"""
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _might_be_circular_import(self, module_name: str) -> bool:
        """Heuristic to detect potential circular imports"""
        file_stem = Path(self.file_path).stem
        return file_stem in module_name or module_name in file_stem

    def _is_hardcoded_config(self, value: str) -> bool:
        """Check if a string value looks like hardcoded configuration"""
        config_patterns = [
            r"^https?://",  # URLs
            r"^\d+\.\d+\.\d+\.\d+",  # IP addresses
            r"^[A-Za-z0-9+/]+=*$",  # Base64-like strings
            r"^[a-f0-9]{32,}$",  # Hash-like strings
        ]
        return any(re.match(pattern, value) for pattern in config_patterns)

    def _find_similar_functions(self, node: ast.FunctionDef) -> List[str]:
        """Find functions with similar structure (simplified)"""
        # This is a placeholder - real implementation would use more sophisticated
        # similarity metrics like AST structure comparison
        return []

    def _get_code_snippet(self, line_number: int, context_lines: int = 2) -> str:
        """Get code snippet around a specific line"""
        start = max(0, line_number - context_lines - 1)
        end = min(len(self.lines), line_number + context_lines)
        return "\n".join(self.lines[start:end])


class JavaScriptTypeScriptAnalyzer:
    """Analyzes JavaScript/TypeScript for constitutional violations"""

    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.split("\n")
        try:
            self.ast = esprima.parseScript(source_code, {"loc": True, "range": True})
        except Exception:
            self.ast = None

    def detect_violations(self) -> List[DetectedViolation]:
        """Detect all constitutional violations in JavaScript/TypeScript"""
        violations = []

        # Add similar detection methods as Python analyzer
        violations.extend(self._detect_naming_violations())
        violations.extend(self._detect_complexity_violations())
        violations.extend(self._detect_security_violations())

        return violations

    def _detect_naming_violations(self) -> List[DetectedViolation]:
        """Detect naming convention violations"""
        violations = []

        # Check for camelCase violations in function and variable names
        camel_case_pattern = r"^[a-z][a-zA-Z0-9]*$"

        for line_num, line in enumerate(self.lines, 1):
            # Simple regex-based detection for function declarations
            func_matches = re.finditer(r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            for match in func_matches:
                func_name = match.group(1)
                if not re.match(camel_case_pattern, func_name):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.MAINTAINABILITY_VIOLATION,
                            severity="LOW",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=match.start(),
                            description=f"Function '{func_name}' should use camelCase naming",
                            rule_id="JS-NAME-001",
                            suggested_fix=f"Rename to {self._to_camel_case(func_name)}",
                            code_snippet=line.strip(),
                            se_principle="Maintainability",
                        )
                    )

        return violations

    def _detect_complexity_violations(self) -> List[DetectedViolation]:
        """Detect complexity violations in JavaScript/TypeScript"""
        violations = []

        # Simple detection for deeply nested code
        for line_num, line in enumerate(self.lines, 1):
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 24:  # More than 6 levels of nesting (4 spaces each)
                violations.append(
                    DetectedViolation(
                        violation_type=ViolationType.SIMPLICITY_VIOLATION,
                        severity="MEDIUM",
                        file_path=self.file_path,
                        line_number=line_num,
                        column_number=0,
                        description=f"Deep nesting detected (level {indent_level // 4})",
                        rule_id="JS-COMPLEX-001",
                        suggested_fix="Reduce nesting using early returns or helper functions",
                        code_snippet=line.strip(),
                        se_principle="Simplicity",
                    )
                )

        return violations

    def _detect_security_violations(self) -> List[DetectedViolation]:
        """Detect security violations in JavaScript/TypeScript"""
        violations = []

        security_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous", "JS-SEC-001"),
            (
                r"innerHTML\s*=",
                "Direct innerHTML assignment can lead to XSS",
                "JS-SEC-002",
            ),
            (
                r"dangerouslySetInnerHTML",
                "React dangerouslySetInnerHTML can lead to XSS",
                "JS-SEC-003",
            ),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, description, rule_id in security_patterns:
                if re.search(pattern, line):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.DEFENSIBILITY_VIOLATION,
                            severity="HIGH",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=0,
                            description=description,
                            rule_id=rule_id,
                            suggested_fix="Use safer alternatives for DOM manipulation",
                            code_snippet=line.strip(),
                            se_principle="Defensibility",
                        )
                    )

        return violations

    def _to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase"""
        components = re.split("[_-]", name.lower())
        return components[0] + "".join(word.capitalize() for word in components[1:])


class ConfigurationAnalyzer:
    """Analyzes YAML/JSON configuration files for constitutional violations"""

    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.split("\n")

        # Try to parse as YAML first, then JSON
        self.config = None
        try:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                self.config = yaml.safe_load(source_code)
            elif file_path.endswith(".json"):
                self.config = json.loads(source_code)
        except Exception:
            pass

    def detect_violations(self) -> List[DetectedViolation]:
        """Detect constitutional violations in configuration files"""
        violations = []

        violations.extend(self._detect_security_violations())
        violations.extend(self._detect_portability_violations())
        violations.extend(self._detect_maintainability_violations())

        return violations

    def _detect_security_violations(self) -> List[DetectedViolation]:
        """Detect security issues in configuration"""
        violations = []

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*[:=]\s*[\'"][^\'\"]{3,}[\'"]',
            r'api_key\s*[:=]\s*[\'"][^\'\"]{10,}[\'"]',
            r'secret\s*[:=]\s*[\'"][^\'\"]{8,}[\'"]',
            r'token\s*[:=]\s*[\'"][^\'\"]{10,}[\'"]',
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.DEFENSIBILITY_VIOLATION,
                            severity="HIGH",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=0,
                            description="Hardcoded secret detected in configuration",
                            rule_id="CONFIG-SEC-001",
                            suggested_fix="Use environment variables or secure secret management",
                            code_snippet=line.strip(),
                            se_principle="Defensibility",
                        )
                    )

        return violations

    def _detect_portability_violations(self) -> List[DetectedViolation]:
        """Detect portability issues in configuration"""
        violations = []

        # Check for absolute paths
        absolute_path_patterns = [
            r'[\'"]?[C-Z]:\\',  # Windows absolute paths
            r'[\'"]?/usr/',  # Unix absolute paths
            r'[\'"]?/bin/',  # Unix absolute paths
            r'[\'"]?/opt/',  # Unix absolute paths
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern in absolute_path_patterns:
                if re.search(pattern, line):
                    violations.append(
                        DetectedViolation(
                            violation_type=ViolationType.PORTABILITY_VIOLATION,
                            severity="MEDIUM",
                            file_path=self.file_path,
                            line_number=line_num,
                            column_number=0,
                            description="Absolute path detected in configuration",
                            rule_id="CONFIG-PORT-001",
                            suggested_fix="Use relative paths or environment-specific configuration",
                            code_snippet=line.strip(),
                            se_principle="Portability",
                        )
                    )

        return violations

    def _detect_maintainability_violations(self) -> List[DetectedViolation]:
        """Detect maintainability issues in configuration"""
        violations = []

        # Check for missing documentation in YAML files
        if self.file_path.endswith((".yaml", ".yml")):
            comment_lines = sum(
                1 for line in self.lines if line.strip().startswith("#")
            )
            total_lines = len([line for line in self.lines if line.strip()])

            if total_lines > 20 and comment_lines / total_lines < 0.1:
                violations.append(
                    DetectedViolation(
                        violation_type=ViolationType.MAINTAINABILITY_VIOLATION,
                        severity="LOW",
                        file_path=self.file_path,
                        line_number=1,
                        column_number=0,
                        description="Configuration file lacks sufficient documentation",
                        rule_id="CONFIG-MAIN-001",
                        suggested_fix="Add comments explaining configuration options",
                        code_snippet="# Add explanatory comments",
                        se_principle="Maintainability",
                    )
                )

        return violations


class ViolationDetector:
    """Main violation detection coordinator"""

    def __init__(self):
        self.supported_extensions = {
            ".py": PythonASTAnalyzer,
            ".js": JavaScriptTypeScriptAnalyzer,
            ".ts": JavaScriptTypeScriptAnalyzer,
            ".tsx": JavaScriptTypeScriptAnalyzer,
            ".jsx": JavaScriptTypeScriptAnalyzer,
            ".yaml": ConfigurationAnalyzer,
            ".yml": ConfigurationAnalyzer,
            ".json": ConfigurationAnalyzer,
        }

    def detect_violations(
        self, file_path: str, source_code: str
    ) -> List[DetectedViolation]:
        """
        Detect all constitutional violations in a given file

        Args:
            file_path: Path to the file being analyzed
            source_code: Content of the file

        Returns:
            List of detected violations
        """
        file_extension = Path(file_path).suffix.lower()

        if file_extension not in self.supported_extensions:
            return []  # Unsupported file type

        analyzer_class = self.supported_extensions[file_extension]
        analyzer = analyzer_class(source_code, file_path)

        if hasattr(analyzer, "detect_violations"):
            return analyzer.detect_violations()
        else:
            # For PythonASTAnalyzer which has separate methods for each SE principle
            violations = []
            if hasattr(analyzer, "detect_srp_violations"):
                violations.extend(analyzer.detect_srp_violations())
            if hasattr(analyzer, "detect_encapsulation_violations"):
                violations.extend(analyzer.detect_encapsulation_violations())
            if hasattr(analyzer, "detect_loose_coupling_violations"):
                violations.extend(analyzer.detect_loose_coupling_violations())
            if hasattr(analyzer, "detect_reusability_violations"):
                violations.extend(analyzer.detect_reusability_violations())
            if hasattr(analyzer, "detect_portability_violations"):
                violations.extend(analyzer.detect_portability_violations())
            if hasattr(analyzer, "detect_defensibility_violations"):
                violations.extend(analyzer.detect_defensibility_violations())
            if hasattr(analyzer, "detect_maintainability_violations"):
                violations.extend(analyzer.detect_maintainability_violations())
            if hasattr(analyzer, "detect_simplicity_violations"):
                violations.extend(analyzer.detect_simplicity_violations())

            return violations

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return list(self.supported_extensions.keys())

    def is_supported_file(self, file_path: str) -> bool:
        """Check if a file type is supported for analysis"""
        return Path(file_path).suffix.lower() in self.supported_extensions

    # Individual SE principle detection methods for constitutional validator integration
    def detect_srp_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Single Responsibility Principle violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            srp_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.SRP_VIOLATION
            ]

            # Convert to Violation objects
            violations = []
            for dv in srp_violations:
                violations.append(
                    Violation(
                        principle="SRP",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="SRP",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="SRP-ERROR",
                )
            ]

    def detect_encapsulation_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Encapsulation violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            enc_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.ENCAPSULATION_VIOLATION
            ]

            violations = []
            for dv in enc_violations:
                violations.append(
                    Violation(
                        principle="Encapsulation",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Encapsulation",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="ENC-ERROR",
                )
            ]

    def detect_coupling_violations(
        self, file_path: str, content: str
    ) -> List[Violation]:
        """Detect Loose Coupling violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            coupling_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.LOOSE_COUPLING_VIOLATION
            ]

            violations = []
            for dv in coupling_violations:
                violations.append(
                    Violation(
                        principle="LooseCoupling",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="LooseCoupling",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="LC-ERROR",
                )
            ]

    def detect_reusability_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Reusability violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            reuse_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.REUSABILITY_VIOLATION
            ]

            violations = []
            for dv in reuse_violations:
                violations.append(
                    Violation(
                        principle="Reusability",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Reusability",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="REU-ERROR",
                )
            ]

    def detect_portability_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Portability violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            port_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.PORTABILITY_VIOLATION
            ]

            violations = []
            for dv in port_violations:
                violations.append(
                    Violation(
                        principle="Portability",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Portability",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="PORT-ERROR",
                )
            ]

    def detect_defensibility_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Defensibility violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            def_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.DEFENSIBILITY_VIOLATION
            ]

            violations = []
            for dv in def_violations:
                violations.append(
                    Violation(
                        principle="Defensibility",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Defensibility",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="DEF-ERROR",
                )
            ]

    def detect_maintainability_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Maintainability violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            maint_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.MAINTAINABILITY_VIOLATION
            ]

            violations = []
            for dv in maint_violations:
                violations.append(
                    Violation(
                        principle="Maintainability",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Maintainability",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="MAINT-ERROR",
                )
            ]

    def detect_simplicity_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect Simplicity violations"""
        try:
            detected_violations = self.detect_violations(file_path, content)
            simp_violations = [
                v
                for v in detected_violations
                if v.violation_type == ViolationType.SIMPLICITY_VIOLATION
            ]

            violations = []
            for dv in simp_violations:
                violations.append(
                    Violation(
                        principle="Simplicity",
                        severity=dv.severity,
                        message=dv.description,
                        file_path=file_path,
                        line_number=dv.line_number,
                        suggested_fix=dv.suggested_fix,
                        rule_id=dv.rule_id,
                    )
                )
            return violations
        except Exception as e:
            return [
                Violation(
                    principle="Simplicity",
                    severity="ERROR",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                    rule_id="SIMP-ERROR",
                )
            ]

    def detect_complexity_violations(
        self, content: str, file_path: str
    ) -> List[Violation]:
        """Detect complexity violations"""
        violations = []
        lines = content.split("\n")

        # Basic complexity detection - count nested loops and conditions
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            indent_level = len(line) - len(line.lstrip())

            # High nesting level indicates complexity
            if indent_level > 24:  # More than 6 levels of 4-space indentation
                violations.append(
                    Violation(
                        principle="Simplicity",
                        severity="WARNING",
                        message="Excessive nesting depth indicates high complexity",
                        file_path=file_path,
                        line_number=i,
                        suggested_fix="Consider refactoring to reduce nesting depth",
                        rule_id="COMPLEX-001",
                    )
                )

        return violations

    def detect_naming_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect naming convention violations"""
        violations = []
        lines = content.split("\n")

        # Basic naming pattern checks
        for i, line in enumerate(lines, 1):
            # Check for camelCase in Python files (should be snake_case)
            if file_ext == ".py" and re.search(r"def [a-z]+[A-Z]", line):
                violations.append(
                    Violation(
                        principle="Maintainability",
                        severity="WARNING",
                        message="Function name should use snake_case in Python",
                        file_path=file_path,
                        line_number=i,
                        suggested_fix="Use snake_case for function names",
                        rule_id="NAME-001",
                    )
                )

        return violations

    def detect_security_violations(
        self, content: str, file_ext: str, file_path: str
    ) -> List[Violation]:
        """Detect security-related violations"""
        violations = []
        lines = content.split("\n")

        security_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        Violation(
                            principle="Defensibility",
                            severity="HIGH",
                            message=message,
                            file_path=file_path,
                            line_number=i,
                            suggested_fix="Move sensitive values to environment variables",
                            rule_id="SEC-001",
                        )
                    )

        return violations


# Factory function for easy instantiation
def create_violation_detector() -> ViolationDetector:
    """Create a new ViolationDetector instance"""
    return ViolationDetector()


if __name__ == "__main__":
    # Example usage
    detector = create_violation_detector()

    # Sample Python code with violations
    sample_python = """
def bad_function_with_many_responsibilities():
    # This function does too many things
    password = "hardcoded_password"  # Security violation
    data = eval(user_input)  # Security violation
    
    if condition1:
        if condition2:
            if condition3:
                if condition4:
                    if condition5:  # Deep nesting violation
                        return "too nested"
    
    # Missing return statement
"""

    violations = detector.detect_violations("example.py", sample_python)
    for violation in violations:
        print(f"{violation.se_principle}: {violation.description}")
        print(f"  Line {violation.line_number}: {violation.suggested_fix}")
        print()
