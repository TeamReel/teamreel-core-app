#!/usr/bin/env python3
"""
Complexity Analyzer - Cyclomatic Complexity Quality Gate

This module analyzes code complexity and enforces limits on cyclomatic complexity
to maintain code readability and maintainability as part of TeamReel's quality
gates system.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import ast
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ComplexityLevel(Enum):
    """Complexity risk levels based on cyclomatic complexity."""
    LOW = "low"          # 1-5
    MODERATE = "moderate"  # 6-10
    HIGH = "high"        # 11-20  
    VERY_HIGH = "very_high"  # 21+


@dataclass
class ComplexityIssue:
    """Represents a complexity violation."""
    filename: str
    function_name: str
    line_number: int
    complexity: int
    threshold: int
    level: ComplexityLevel
    suggestion: str


@dataclass
class FileComplexity:
    """Complexity analysis for a single file."""
    filename: str
    average_complexity: float
    max_complexity: int
    function_count: int
    violations: List[ComplexityIssue] = field(default_factory=list)


@dataclass
class ComplexityReport:
    """Complete complexity analysis report."""
    total_files: int
    total_functions: int
    average_complexity: float
    max_complexity: int
    violations_count: int
    threshold: int
    files: List[FileComplexity] = field(default_factory=list)
    violations: List[ComplexityIssue] = field(default_factory=list)
    is_passing: bool = True
    remediation_suggestions: List[str] = field(default_factory=list)


class ComplexityAnalyzer:
    """Analyzes code complexity and enforces complexity limits."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize complexity analyzer with configuration."""
        self.config = config or self._default_config()
        self.max_complexity = self.config.get('complexity', {}).get('max_complexity', 10)
        self.exclude_patterns = self.config.get('complexity', {}).get('exclude', [
            '*/tests/*',
            '*/test/*',
            '*/__pycache__/*',
            '*/migrations/*',
            '**/conftest.py'
        ])
    
    def _default_config(self) -> Dict:
        """Default configuration for complexity analysis."""
        return {
            'complexity': {
                'max_complexity': 10,
                'exclude': [
                    '*/tests/*',
                    '*/test/*', 
                    '*/__pycache__/*',
                    '*/migrations/*',
                    '**/conftest.py'
                ],
                'python': {
                    'tool': 'radon',
                    'args': ['cc', '--show-complexity', '--json']
                },
                'javascript': {
                    'tool': 'eslint',
                    'rules': ['complexity']
                }
            }
        }
    
    def analyze_python_complexity(self, source_dir: str = ".") -> ComplexityReport:
        """Analyze Python code complexity using radon."""
        try:
            # Try radon first
            return self._analyze_with_radon(source_dir)
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to AST-based analysis
            print("Radon not available, using built-in AST analyzer")
            return self._analyze_with_ast(source_dir)
    
    def _analyze_with_radon(self, source_dir: str) -> ComplexityReport:
        """Use radon tool for complexity analysis."""
        cmd = ['radon', 'cc', source_dir, '--show-complexity', '--json']
        
        print(f"Running complexity analysis: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise subprocess.SubprocessError(f"Radon failed: {result.stderr}")
        
        return self._parse_radon_output(result.stdout)
    
    def _parse_radon_output(self, radon_json: str) -> ComplexityReport:
        """Parse radon JSON output."""
        try:
            data = json.loads(radon_json)
            
            files = []
            all_violations = []
            total_functions = 0
            total_complexity = 0.0
            max_complexity = 0
            
            for filename, file_data in data.items():
                if self._should_exclude_file(filename):
                    continue
                
                function_complexities = []
                file_violations = []
                
                for item in file_data:
                    complexity = item['complexity']
                    function_name = item['name']
                    line_number = item['lineno']
                    
                    function_complexities.append(complexity)
                    total_functions += 1
                    total_complexity += complexity
                    max_complexity = max(max_complexity, complexity)
                    
                    if complexity > self.max_complexity:
                        level = self._get_complexity_level(complexity)
                        suggestion = self._get_complexity_suggestion(complexity, function_name)
                        
                        violation = ComplexityIssue(
                            filename=filename,
                            function_name=function_name,
                            line_number=line_number,
                            complexity=complexity,
                            threshold=self.max_complexity,
                            level=level,
                            suggestion=suggestion
                        )
                        
                        file_violations.append(violation)
                        all_violations.append(violation)
                
                if function_complexities:
                    avg_complexity = sum(function_complexities) / len(function_complexities)
                    
                    file_complexity = FileComplexity(
                        filename=filename,
                        average_complexity=avg_complexity,
                        max_complexity=max(function_complexities),
                        function_count=len(function_complexities),
                        violations=file_violations
                    )
                    
                    files.append(file_complexity)
            
            avg_overall = total_complexity / total_functions if total_functions > 0 else 0
            suggestions = self._generate_complexity_suggestions(all_violations, avg_overall)
            
            return ComplexityReport(
                total_files=len(files),
                total_functions=total_functions,
                average_complexity=avg_overall,
                max_complexity=max_complexity,
                violations_count=len(all_violations),
                threshold=self.max_complexity,
                files=files,
                violations=all_violations,
                is_passing=len(all_violations) == 0,
                remediation_suggestions=suggestions
            )
            
        except json.JSONDecodeError as e:
            return ComplexityReport(
                total_files=0,
                total_functions=0,
                average_complexity=0.0,
                max_complexity=0,
                violations_count=0,
                threshold=self.max_complexity,
                is_passing=False,
                remediation_suggestions=[
                    f"Failed to parse radon output: {str(e)}",
                    "Check radon installation and configuration"
                ]
            )
    
    def _analyze_with_ast(self, source_dir: str) -> ComplexityReport:
        """Fallback AST-based complexity analysis."""
        python_files = list(Path(source_dir).rglob("*.py"))
        python_files = [f for f in python_files if not self._should_exclude_file(str(f))]
        
        files = []
        all_violations = []
        total_functions = 0
        total_complexity = 0.0
        max_complexity = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                file_analysis = self._analyze_ast_file(tree, str(py_file))
                
                if file_analysis.function_count > 0:
                    files.append(file_analysis)
                    all_violations.extend(file_analysis.violations)
                    total_functions += file_analysis.function_count
                    total_complexity += file_analysis.average_complexity * file_analysis.function_count
                    max_complexity = max(max_complexity, file_analysis.max_complexity)
                
            except Exception as e:
                print(f"Warning: Could not analyze {py_file}: {e}")
                continue
        
        avg_overall = total_complexity / total_functions if total_functions > 0 else 0
        suggestions = self._generate_complexity_suggestions(all_violations, avg_overall)
        
        return ComplexityReport(
            total_files=len(files),
            total_functions=total_functions,
            average_complexity=avg_overall,
            max_complexity=max_complexity,
            violations_count=len(all_violations),
            threshold=self.max_complexity,
            files=files,
            violations=all_violations,
            is_passing=len(all_violations) == 0,
            remediation_suggestions=suggestions
        )
    
    def _analyze_ast_file(self, tree: ast.AST, filename: str) -> FileComplexity:
        """Analyze single file using AST."""
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        function_complexities = []
        file_violations = []
        
        for func_name, complexity, line_no in visitor.function_complexities:
            function_complexities.append(complexity)
            
            if complexity > self.max_complexity:
                level = self._get_complexity_level(complexity)
                suggestion = self._get_complexity_suggestion(complexity, func_name)
                
                violation = ComplexityIssue(
                    filename=filename,
                    function_name=func_name,
                    line_number=line_no,
                    complexity=complexity,
                    threshold=self.max_complexity,
                    level=level,
                    suggestion=suggestion
                )
                
                file_violations.append(violation)
        
        avg_complexity = sum(function_complexities) / len(function_complexities) if function_complexities else 0
        
        return FileComplexity(
            filename=filename,
            average_complexity=avg_complexity,
            max_complexity=max(function_complexities) if function_complexities else 0,
            function_count=len(function_complexities),
            violations=file_violations
        )
    
    def analyze_javascript_complexity(self, project_dir: str = ".") -> ComplexityReport:
        """Analyze JavaScript/TypeScript complexity using ESLint."""
        try:
            package_json = Path(project_dir) / "package.json"
            if not package_json.exists():
                return ComplexityReport(
                    total_files=0,
                    total_functions=0,
                    average_complexity=0.0,
                    max_complexity=0,
                    violations_count=0,
                    threshold=self.max_complexity,
                    is_passing=True,  # Skip if no JS project
                    remediation_suggestions=[
                        "No package.json found - skipping JavaScript complexity analysis"
                    ]
                )
            
            # Run ESLint with complexity rule
            cmd = [
                'npx', 'eslint', 
                '--rule', f'complexity: ["error", {self.max_complexity}]',
                '--format', 'json',
                '**/*.{js,ts,jsx,tsx}'
            ]
            
            print(f"Running JavaScript complexity analysis: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=project_dir)
            
            return self._parse_eslint_output(result.stdout)
            
        except Exception as e:
            return ComplexityReport(
                total_files=0,
                total_functions=0,
                average_complexity=0.0,
                max_complexity=0,
                violations_count=0,
                threshold=self.max_complexity,
                is_passing=True,  # Don't fail on JS errors in Python projects
                remediation_suggestions=[
                    f"JavaScript complexity analysis failed: {str(e)}",
                    "This may be expected in Python-only projects"
                ]
            )
    
    def _parse_eslint_output(self, eslint_json: str) -> ComplexityReport:
        """Parse ESLint JSON output for complexity violations."""
        try:
            data = json.loads(eslint_json) if eslint_json.strip() else []
            
            violations = []
            files_analyzed = 0
            
            for file_result in data:
                filename = file_result['filePath']
                if self._should_exclude_file(filename):
                    continue
                
                files_analyzed += 1
                
                for message in file_result['messages']:
                    if message['ruleId'] == 'complexity':
                        # Parse complexity from message
                        complexity_match = re.search(r'complexity of (\d+)', message['message'])
                        complexity = int(complexity_match.group(1)) if complexity_match else self.max_complexity + 1
                        
                        violation = ComplexityIssue(
                            filename=filename,
                            function_name=message.get('source', 'unknown'),
                            line_number=message['line'],
                            complexity=complexity,
                            threshold=self.max_complexity,
                            level=self._get_complexity_level(complexity),
                            suggestion=self._get_complexity_suggestion(complexity, 'function')
                        )
                        violations.append(violation)
            
            return ComplexityReport(
                total_files=files_analyzed,
                total_functions=len(violations),  # Approximate
                average_complexity=0.0,  # ESLint doesn't provide this
                max_complexity=max([v.complexity for v in violations]) if violations else 0,
                violations_count=len(violations),
                threshold=self.max_complexity,
                violations=violations,
                is_passing=len(violations) == 0,
                remediation_suggestions=self._generate_complexity_suggestions(violations, 0)
            )
            
        except json.JSONDecodeError:
            return ComplexityReport(
                total_files=0,
                total_functions=0,
                average_complexity=0.0,
                max_complexity=0,
                violations_count=0,
                threshold=self.max_complexity,
                is_passing=True,
                remediation_suggestions=[
                    "No ESLint complexity violations found or ESLint not configured"
                ]
            )
    
    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded from complexity analysis."""
        for pattern in self.exclude_patterns:
            if pattern.replace('*', '').replace('/', '') in filename:
                return True
        return False
    
    def _get_complexity_level(self, complexity: int) -> ComplexityLevel:
        """Determine complexity risk level."""
        if complexity <= 5:
            return ComplexityLevel.LOW
        elif complexity <= 10:
            return ComplexityLevel.MODERATE
        elif complexity <= 20:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.VERY_HIGH
    
    def _get_complexity_suggestion(self, complexity: int, function_name: str) -> str:
        """Generate specific suggestion for complexity reduction."""
        if complexity <= 15:
            return f"Consider breaking {function_name} into smaller functions using Extract Method refactoring"
        elif complexity <= 25:
            return f"Function {function_name} is too complex - extract multiple helper functions and consider using strategy pattern"
        else:
            return f"Function {function_name} is extremely complex - requires significant refactoring into multiple classes/modules"
    
    def _generate_complexity_suggestions(self, violations: List[ComplexityIssue], avg_complexity: float) -> List[str]:
        """Generate remediation suggestions based on complexity violations."""
        suggestions = []
        
        if not violations:
            suggestions.append("All functions meet complexity requirements!")
            return suggestions
        
        # General suggestions
        suggestions.append(f"Found {len(violations)} complexity violations")
        
        # Group by severity
        high_complexity = [v for v in violations if v.complexity > 20]
        moderate_complexity = [v for v in violations if 15 < v.complexity <= 20]
        
        if high_complexity:
            suggestions.append(f"{len(high_complexity)} functions have very high complexity (>20)")
            suggestions.append("Priority: Refactor high-complexity functions first")
        
        if moderate_complexity:
            suggestions.append(f"{len(moderate_complexity)} functions have high complexity (15-20)")
        
        # Specific techniques
        suggestions.extend([
            "Refactoring techniques to reduce complexity:",
            "- Extract Method: Break large functions into smaller ones",
            "- Extract Class: Move related functionality to separate classes", 
            "- Replace Conditional with Polymorphism: Use inheritance instead of complex if/else",
            "- Simplify Conditional Expressions: Use early returns and guard clauses",
            "- Replace Nested Conditional with Guard Clauses"
        ])
        
        # Most complex functions
        worst_violations = sorted(violations, key=lambda x: x.complexity, reverse=True)[:3]
        suggestions.append("Most complex functions to address first:")
        for violation in worst_violations:
            suggestions.append(f"- {violation.filename}:{violation.line_number} {violation.function_name} (complexity: {violation.complexity})")
        
        return suggestions
    
    def validate_complexity(self, project_dir: str = ".") -> Dict[str, ComplexityReport]:
        """Validate complexity for all supported languages."""
        results = {}
        
        # Check for Python files
        python_files = list(Path(project_dir).rglob("*.py"))
        if python_files:
            print("🐍 Analyzing Python code complexity...")
            results['python'] = self.analyze_python_complexity(project_dir)
        
        # Check for JavaScript/TypeScript files
        js_files = list(Path(project_dir).rglob("*.js")) + list(Path(project_dir).rglob("*.ts"))
        if js_files:
            print("📦 Analyzing JavaScript/TypeScript complexity...")
            results['javascript'] = self.analyze_javascript_complexity(project_dir)
        
        if not results:
            results['none'] = ComplexityReport(
                total_files=0,
                total_functions=0,
                average_complexity=0.0,
                max_complexity=0,
                violations_count=0,
                threshold=self.max_complexity,
                is_passing=True,
                remediation_suggestions=["No source files found to analyze"]
            )
        
        return results
    
    def format_report(self, reports: Dict[str, ComplexityReport], format_type: str = "terminal") -> str:
        """Format complexity analysis report."""
        if format_type == "json":
            return json.dumps({
                lang: {
                    "total_files": report.total_files,
                    "total_functions": report.total_functions,
                    "average_complexity": report.average_complexity,
                    "max_complexity": report.max_complexity,
                    "violations_count": report.violations_count,
                    "threshold": report.threshold,
                    "is_passing": report.is_passing,
                    "violations": [
                        {
                            "filename": v.filename,
                            "function_name": v.function_name,
                            "line_number": v.line_number,
                            "complexity": v.complexity,
                            "level": v.level.value,
                            "suggestion": v.suggestion
                        }
                        for v in report.violations
                    ]
                }
                for lang, report in reports.items()
            }, indent=2)
        
        # Terminal format
        output = []
        output.append("🔄 CYCLOMATIC COMPLEXITY ANALYSIS REPORT")
        output.append("=" * 55)
        
        overall_passing = all(report.is_passing for report in reports.values())
        
        for lang, report in reports.items():
            if lang == 'none':
                continue
            
            output.append(f"\n{lang.upper()} Complexity Analysis:")
            output.append(f"  Files analyzed: {report.total_files}")
            output.append(f"  Functions analyzed: {report.total_functions}")
            
            if report.total_functions > 0:
                output.append(f"  Average complexity: {report.average_complexity:.1f}")
                output.append(f"  Maximum complexity: {report.max_complexity}")
            
            output.append(f"  Violations: {report.violations_count} (threshold: ≤{report.threshold})")
            output.append(f"  Status: {'✅ PASS' if report.is_passing else '❌ FAIL'}")
            
            if report.violations:
                output.append("  Top violations:")
                for violation in sorted(report.violations, key=lambda x: x.complexity, reverse=True)[:5]:
                    output.append(f"    • {violation.filename}:{violation.line_number} {violation.function_name} (complexity: {violation.complexity})")
        
        output.append(f"\n{'='*55}")
        output.append(f"Overall Status: {'✅ PASS' if overall_passing else '❌ FAIL'}")
        
        if not overall_passing:
            output.append("\n❌ Complexity validation failed. Please reduce function complexity.")
            # Show remediation suggestions
            for lang, report in reports.items():
                if report.violations and report.remediation_suggestions:
                    output.append(f"\n{lang.upper()} Remediation Suggestions:")
                    for suggestion in report.remediation_suggestions[:5]:
                        output.append(f"  • {suggestion}")
        else:
            output.append("\n✅ All functions meet complexity requirements!")
        
        return "\n".join(output)


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.function_complexities = []
        self.current_function = None
        self.current_complexity = 0
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        old_complexity = self.current_complexity
        
        self.current_function = node.name
        self.current_complexity = 1  # Base complexity
        
        # Visit function body
        self.generic_visit(node)
        
        # Record function complexity
        self.function_complexities.append((node.name, self.current_complexity, node.lineno))
        
        # Restore previous state
        self.current_function = old_function
        self.current_complexity = old_complexity
    
    def visit_If(self, node):
        """Visit if statement."""
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit while loop."""
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loop."""
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        """Visit except handler."""
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        """Visit with statement."""
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Visit boolean operation (and/or)."""
        if self.current_function and isinstance(node.op, (ast.And, ast.Or)):
            self.current_complexity += len(node.values) - 1
        self.generic_visit(node)


def main():
    """CLI entry point for complexity analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze code complexity and enforce limits")
    parser.add_argument("--max-complexity", type=int, default=10, help="Maximum allowed complexity")
    parser.add_argument("--project-dir", default=".", help="Project directory to analyze")
    parser.add_argument("--format", choices=["terminal", "json"], default="terminal", help="Output format")
    parser.add_argument("--fail-on-violations", action="store_true", help="Exit with error if violations found")
    
    args = parser.parse_args()
    
    # Configure analyzer
    config = {
        'complexity': {
            'max_complexity': args.max_complexity
        }
    }
    
    analyzer = ComplexityAnalyzer(config)
    reports = analyzer.validate_complexity(args.project_dir)
    
    # Output report
    print(analyzer.format_report(reports, args.format))
    
    # Exit with error if violations found
    if args.fail_on_violations:
        if not all(report.is_passing for report in reports.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()