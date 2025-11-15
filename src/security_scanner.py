#!/usr/bin/env python3
"""
Security Scanner - Security Vulnerability Quality Gate

This module performs comprehensive security scanning across multiple languages
and identifies potential security vulnerabilities, enforcing security standards
as part of TeamReel's quality gates system.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import json
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SecuritySeverity(Enum):
    """Security vulnerability severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_CRYPTO = "weak_crypto"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"
    CONFIGURATION_ISSUE = "configuration_issue"
    OTHER = "other"


@dataclass
class SecurityIssue:
    """Represents a security vulnerability."""
    filename: str
    line_number: int
    vulnerability_type: VulnerabilityType
    severity: SecuritySeverity
    title: str
    description: str
    cwe_id: Optional[str] = None
    confidence: str = "high"
    remediation: str = ""


@dataclass
class FileSecurityReport:
    """Security analysis for a single file."""
    filename: str
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[SecurityIssue] = field(default_factory=list)


@dataclass
class SecurityReport:
    """Complete security analysis report."""
    total_files: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    files: List[FileSecurityReport] = field(default_factory=list)
    issues: List[SecurityIssue] = field(default_factory=list)
    is_passing: bool = True
    remediation_suggestions: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)


class SecurityScanner:
    """Comprehensive security vulnerability scanner."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize security scanner with configuration."""
        self.config = config or self._default_config()
        self.fail_on_severity = self.config.get('security', {}).get('fail_on_severity', 'medium')
        self.exclude_patterns = self.config.get('security', {}).get('exclude', [
            '*/tests/*',
            '*/test/*',
            '*/__pycache__/*',
            '*/node_modules/*',
            '*/venv/*',
            '*/env/*'
        ])
    
    def _default_config(self) -> Dict:
        """Default configuration for security scanning."""
        return {
            'security': {
                'fail_on_severity': 'medium',  # Fail on medium+ severity
                'exclude': [
                    '*/tests/*',
                    '*/test/*',
                    '*/__pycache__/*',
                    '*/node_modules/*',
                    '*/venv/*',
                    '*/env/*'
                ],
                'python': {
                    'tools': ['bandit', 'safety'],
                    'bandit_args': ['-f', 'json', '-r'],
                    'safety_args': ['check', '--json']
                },
                'javascript': {
                    'tools': ['eslint-security', 'npm-audit'],
                    'eslint_rules': [
                        'security/detect-buffer-noassert',
                        'security/detect-child-process',
                        'security/detect-disable-mustache-escape',
                        'security/detect-eval-with-expression',
                        'security/detect-new-buffer',
                        'security/detect-no-csrf-before-method-override',
                        'security/detect-non-literal-fs-filename',
                        'security/detect-non-literal-regexp',
                        'security/detect-non-literal-require',
                        'security/detect-object-injection',
                        'security/detect-possible-timing-attacks',
                        'security/detect-pseudoRandomBytes',
                        'security/detect-unsafe-regex'
                    ]
                }
            }
        }
    
    def scan_python_security(self, project_dir: str = ".") -> SecurityReport:
        """Scan Python code for security vulnerabilities."""
        python_files = list(Path(project_dir).rglob("*.py"))
        if not python_files:
            return SecurityReport(
                total_files=0,
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                is_passing=True,
                remediation_suggestions=["No Python files found to scan"],
                tools_used=[]
            )
        
        all_issues = []
        tools_used = []
        
        # Run Bandit for static analysis
        bandit_issues = self._run_bandit(project_dir)
        all_issues.extend(bandit_issues)
        if bandit_issues:
            tools_used.append("bandit")
        
        # Run Safety for dependency vulnerabilities
        safety_issues = self._run_safety(project_dir)
        all_issues.extend(safety_issues)
        if safety_issues:
            tools_used.append("safety")
        
        # Additional pattern-based security checks
        pattern_issues = self._scan_security_patterns_python(project_dir)
        all_issues.extend(pattern_issues)
        if pattern_issues:
            tools_used.append("pattern-matching")
        
        return self._create_security_report(all_issues, tools_used)
    
    def _run_bandit(self, project_dir: str) -> List[SecurityIssue]:
        """Run Bandit security scanner."""
        try:
            cmd = ['bandit', '-f', 'json', '-r', project_dir]
            print(f"Running Bandit: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                return self._parse_bandit_output(result.stdout)
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Bandit not available or failed: {e}")
        
        return []
    
    def _parse_bandit_output(self, bandit_json: str) -> List[SecurityIssue]:
        """Parse Bandit JSON output."""
        try:
            data = json.loads(bandit_json)
            issues = []
            
            for result in data.get('results', []):
                if self._should_exclude_file(result['filename']):
                    continue
                
                severity = self._map_bandit_severity(result['issue_severity'])
                vuln_type = self._map_bandit_vulnerability_type(result['test_id'])
                
                issue = SecurityIssue(
                    filename=result['filename'],
                    line_number=result['line_number'],
                    vulnerability_type=vuln_type,
                    severity=severity,
                    title=result['issue_text'],
                    description=result['issue_text'],
                    cwe_id=result.get('issue_cwe', {}).get('id'),
                    confidence=result['issue_confidence'].lower(),
                    remediation=self._get_bandit_remediation(result['test_id'])
                )
                
                issues.append(issue)
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Bandit output: {e}")
            return []
    
    def _run_safety(self, project_dir: str) -> List[SecurityIssue]:
        """Run Safety dependency scanner."""
        try:
            cmd = ['safety', 'check', '--json']
            print(f"Running Safety: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=project_dir)
            
            if result.stdout:
                return self._parse_safety_output(result.stdout)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Safety not available or failed: {e}")
        
        return []
    
    def _parse_safety_output(self, safety_json: str) -> List[SecurityIssue]:
        """Parse Safety JSON output."""
        try:
            data = json.loads(safety_json)
            issues = []
            
            for vuln in data:
                issue = SecurityIssue(
                    filename="requirements.txt",  # Safety scans dependencies
                    line_number=0,
                    vulnerability_type=VulnerabilityType.DEPENDENCY_VULNERABILITY,
                    severity=SecuritySeverity.HIGH,  # Assume high for dependency vulns
                    title=f"Vulnerable dependency: {vuln['package_name']}",
                    description=vuln['advisory'],
                    cwe_id=None,
                    confidence="high",
                    remediation=f"Update {vuln['package_name']} to version {vuln['analyzed_version']} or later"
                )
                
                issues.append(issue)
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Safety output: {e}")
            return []
    
    def _scan_security_patterns_python(self, project_dir: str) -> List[SecurityIssue]:
        """Scan for security anti-patterns using regex."""
        patterns = {
            'hardcoded_password': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\(["\'][^"\']*%[^"\']*["\']',
                r'cursor\.execute.*%.*\)',
                r'query\s*=\s*["\'][^"\']*%[^"\']*["\']'
            ],
            'command_injection': [
                r'os\.system\(',
                r'subprocess\.(call|run|Popen).*shell=True',
                r'eval\(',
                r'exec\('
            ],
            'weak_crypto': [
                r'md5\(',
                r'sha1\(',
                r'random\.random\(',
                r'DES\.',
                r'RC4\.'
            ]
        }
        
        issues = []
        python_files = list(Path(project_dir).rglob("*.py"))
        
        for py_file in python_files:
            if self._should_exclude_file(str(py_file)):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
            
                for line_no, line in enumerate(lines, 1):
                    for pattern_type, pattern_list in patterns.items():
                        for pattern in pattern_list:
                            if re.search(pattern, line, re.IGNORECASE):
                                issue = SecurityIssue(
                                    filename=str(py_file),
                                    line_number=line_no,
                                    vulnerability_type=self._map_pattern_to_vuln_type(pattern_type),
                                    severity=self._get_pattern_severity(pattern_type),
                                    title=f"Potential {pattern_type.replace('_', ' ')} detected",
                                    description=f"Pattern '{pattern}' matches line: {line.strip()[:100]}",
                                    confidence="medium",
                                    remediation=self._get_pattern_remediation(pattern_type)
                                )
                                issues.append(issue)
            
            except Exception as e:
                print(f"Warning: Could not scan {py_file}: {e}")
                continue
        
        return issues
    
    def scan_javascript_security(self, project_dir: str = ".") -> SecurityReport:
        """Scan JavaScript/TypeScript code for security vulnerabilities."""
        js_files = list(Path(project_dir).rglob("*.js")) + list(Path(project_dir).rglob("*.ts"))
        package_json = Path(project_dir) / "package.json"
        
        if not js_files and not package_json.exists():
            return SecurityReport(
                total_files=0,
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                is_passing=True,
                remediation_suggestions=["No JavaScript/TypeScript project found"],
                tools_used=[]
            )
        
        all_issues = []
        tools_used = []
        
        # Run npm audit for dependency vulnerabilities
        if package_json.exists():
            npm_issues = self._run_npm_audit(project_dir)
            all_issues.extend(npm_issues)
            if npm_issues:
                tools_used.append("npm-audit")
        
        # Run ESLint with security rules
        if js_files:
            eslint_issues = self._run_eslint_security(project_dir)
            all_issues.extend(eslint_issues)
            if eslint_issues:
                tools_used.append("eslint-security")
            
            # Pattern-based security checks
            pattern_issues = self._scan_security_patterns_js(project_dir)
            all_issues.extend(pattern_issues)
            if pattern_issues:
                tools_used.append("pattern-matching")
        
        return self._create_security_report(all_issues, tools_used)
    
    def _run_npm_audit(self, project_dir: str) -> List[SecurityIssue]:
        """Run npm audit for dependency vulnerabilities."""
        try:
            cmd = ['npm', 'audit', '--json']
            print(f"Running npm audit: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=project_dir)
            
            if result.stdout:
                return self._parse_npm_audit_output(result.stdout)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"npm audit not available or failed: {e}")
        
        return []
    
    def _parse_npm_audit_output(self, npm_json: str) -> List[SecurityIssue]:
        """Parse npm audit JSON output."""
        try:
            data = json.loads(npm_json)
            issues = []
            
            for vuln_id, vuln in data.get('vulnerabilities', {}).items():
                severity = self._map_npm_severity(vuln.get('severity', 'info'))
                
                issue = SecurityIssue(
                    filename="package.json",
                    line_number=0,
                    vulnerability_type=VulnerabilityType.DEPENDENCY_VULNERABILITY,
                    severity=severity,
                    title=f"Vulnerable dependency: {vuln.get('name', vuln_id)}",
                    description=vuln.get('title', 'Dependency vulnerability'),
                    cwe_id=None,
                    confidence="high",
                    remediation=f"Update to fixed version or run 'npm audit fix'"
                )
                
                issues.append(issue)
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse npm audit output: {e}")
            return []
    
    def _run_eslint_security(self, project_dir: str) -> List[SecurityIssue]:
        """Run ESLint with security plugin."""
        try:
            cmd = [
                'npx', 'eslint',
                '--ext', '.js,.ts,.jsx,.tsx',
                '--format', 'json',
                '.'
            ]
            
            print(f"Running ESLint security: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=project_dir)
            
            if result.stdout:
                return self._parse_eslint_security_output(result.stdout)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"ESLint security not available or failed: {e}")
        
        return []
    
    def _parse_eslint_security_output(self, eslint_json: str) -> List[SecurityIssue]:
        """Parse ESLint JSON output for security issues."""
        try:
            data = json.loads(eslint_json) if eslint_json.strip() else []
            issues = []
            
            for file_result in data:
                filename = file_result['filePath']
                if self._should_exclude_file(filename):
                    continue
                
                for message in file_result['messages']:
                    rule_id = message.get('ruleId', '')
                    
                    if rule_id.startswith('security/'):
                        severity = self._map_eslint_severity(message['severity'])
                        vuln_type = self._map_eslint_security_rule(rule_id)
                        
                        issue = SecurityIssue(
                            filename=filename,
                            line_number=message['line'],
                            vulnerability_type=vuln_type,
                            severity=severity,
                            title=message['message'],
                            description=message['message'],
                            confidence="high",
                            remediation=self._get_eslint_security_remediation(rule_id)
                        )
                        
                        issues.append(issue)
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse ESLint output: {e}")
            return []
    
    def _scan_security_patterns_js(self, project_dir: str) -> List[SecurityIssue]:
        """Scan JavaScript/TypeScript for security anti-patterns."""
        patterns = {
            'hardcoded_secret': [
                r'apiKey\s*[:=]\s*["\'][^"\']+["\']',
                r'password\s*[:=]\s*["\'][^"\']+["\']',
                r'secret\s*[:=]\s*["\'][^"\']+["\']',
                r'token\s*[:=]\s*["\'][^"\']+["\']'
            ],
            'xss': [
                r'innerHTML\s*=',
                r'document\.write\(',
                r'eval\(',
                r'dangerouslySetInnerHTML'
            ],
            'command_injection': [
                r'exec\(',
                r'spawn\(',
                r'child_process'
            ],
            'insecure_random': [
                r'Math\.random\(',
                r'crypto\.pseudoRandomBytes'
            ]
        }
        
        issues = []
        js_files = list(Path(project_dir).rglob("*.js")) + list(Path(project_dir).rglob("*.ts"))
        
        for js_file in js_files:
            if self._should_exclude_file(str(js_file)):
                continue
            
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_no, line in enumerate(lines, 1):
                    for pattern_type, pattern_list in patterns.items():
                        for pattern in pattern_list:
                            if re.search(pattern, line, re.IGNORECASE):
                                issue = SecurityIssue(
                                    filename=str(js_file),
                                    line_number=line_no,
                                    vulnerability_type=self._map_pattern_to_vuln_type(pattern_type),
                                    severity=self._get_pattern_severity(pattern_type),
                                    title=f"Potential {pattern_type.replace('_', ' ')} detected",
                                    description=f"Pattern '{pattern}' matches line: {line.strip()[:100]}",
                                    confidence="medium",
                                    remediation=self._get_pattern_remediation_js(pattern_type)
                                )
                                issues.append(issue)
            
            except Exception as e:
                print(f"Warning: Could not scan {js_file}: {e}")
                continue
        
        return issues
    
    def validate_security(self, project_dir: str = ".") -> Dict[str, SecurityReport]:
        """Validate security for all supported languages."""
        results = {}
        
        # Check for Python files
        python_files = list(Path(project_dir).rglob("*.py"))
        if python_files:
            print("🐍 Scanning Python code for security vulnerabilities...")
            results['python'] = self.scan_python_security(project_dir)
        
        # Check for JavaScript/TypeScript files
        js_files = list(Path(project_dir).rglob("*.js")) + list(Path(project_dir).rglob("*.ts"))
        package_json = Path(project_dir) / "package.json"
        if js_files or package_json.exists():
            print("📦 Scanning JavaScript/TypeScript for security vulnerabilities...")
            results['javascript'] = self.scan_javascript_security(project_dir)
        
        if not results:
            results['none'] = SecurityReport(
                total_files=0,
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                is_passing=True,
                remediation_suggestions=["No source files found to scan"],
                tools_used=[]
            )
        
        return results
    
    def _create_security_report(self, issues: List[SecurityIssue], tools_used: List[str]) -> SecurityReport:
        """Create security report from issues list."""
        # Count by severity
        critical_issues = len([i for i in issues if i.severity == SecuritySeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == SecuritySeverity.HIGH])
        medium_issues = len([i for i in issues if i.severity == SecuritySeverity.MEDIUM])
        low_issues = len([i for i in issues if i.severity == SecuritySeverity.LOW])
        
        # Group by file
        files_dict = {}
        for issue in issues:
            if issue.filename not in files_dict:
                files_dict[issue.filename] = []
            files_dict[issue.filename].append(issue)
        
        files = []
        for filename, file_issues in files_dict.items():
            file_report = FileSecurityReport(
                filename=filename,
                total_issues=len(file_issues),
                critical_issues=len([i for i in file_issues if i.severity == SecuritySeverity.CRITICAL]),
                high_issues=len([i for i in file_issues if i.severity == SecuritySeverity.HIGH]),
                medium_issues=len([i for i in file_issues if i.severity == SecuritySeverity.MEDIUM]),
                low_issues=len([i for i in file_issues if i.severity == SecuritySeverity.LOW]),
                issues=file_issues
            )
            files.append(file_report)
        
        # Check if passing based on fail_on_severity
        fail_threshold = SecuritySeverity(self.fail_on_severity)
        failing_issues = []
        
        if fail_threshold == SecuritySeverity.LOW:
            failing_issues = issues
        elif fail_threshold == SecuritySeverity.MEDIUM:
            failing_issues = [i for i in issues if i.severity in [SecuritySeverity.MEDIUM, SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]]
        elif fail_threshold == SecuritySeverity.HIGH:
            failing_issues = [i for i in issues if i.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]]
        elif fail_threshold == SecuritySeverity.CRITICAL:
            failing_issues = [i for i in issues if i.severity == SecuritySeverity.CRITICAL]
        
        is_passing = len(failing_issues) == 0
        remediation_suggestions = self._generate_security_suggestions(issues)
        
        return SecurityReport(
            total_files=len(files),
            total_issues=len(issues),
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            files=files,
            issues=issues,
            is_passing=is_passing,
            remediation_suggestions=remediation_suggestions,
            tools_used=tools_used
        )
    
    def _generate_security_suggestions(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate remediation suggestions based on security issues."""
        if not issues:
            return ["No security vulnerabilities found!"]
        
        suggestions = []
        suggestions.append(f"Found {len(issues)} security issues that need attention")
        
        # Group by vulnerability type
        vuln_counts = {}
        for issue in issues:
            vuln_type = issue.vulnerability_type.value
            vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
        
        # Priority suggestions
        critical_high = [i for i in issues if i.severity in [SecuritySeverity.CRITICAL, SecuritySeverity.HIGH]]
        if critical_high:
            suggestions.append(f"URGENT: {len(critical_high)} critical/high severity issues require immediate attention")
        
        # Top vulnerability types
        if vuln_counts:
            top_vulns = sorted(vuln_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions.append("Most common vulnerability types:")
            for vuln_type, count in top_vulns:
                suggestions.append(f"- {vuln_type.replace('_', ' ').title()}: {count} issues")
        
        # General security recommendations
        suggestions.extend([
            "",
            "General security recommendations:",
            "- Keep dependencies up to date (run 'npm audit fix' or 'pip install --upgrade')",
            "- Use secrets management (environment variables, key vaults)",
            "- Implement input validation and sanitization",
            "- Use parameterized queries for database operations",
            "- Enable security linters in your CI/CD pipeline",
            "- Conduct regular security reviews and penetration testing"
        ])
        
        return suggestions
    
    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded from security scanning."""
        for pattern in self.exclude_patterns:
            if pattern.replace('*', '').replace('/', '') in filename:
                return True
        return False
    
    # Utility mapping methods
    def _map_bandit_severity(self, severity: str) -> SecuritySeverity:
        """Map Bandit severity to our enum."""
        mapping = {
            'LOW': SecuritySeverity.LOW,
            'MEDIUM': SecuritySeverity.MEDIUM,
            'HIGH': SecuritySeverity.HIGH
        }
        return mapping.get(severity.upper(), SecuritySeverity.MEDIUM)
    
    def _map_npm_severity(self, severity: str) -> SecuritySeverity:
        """Map npm audit severity to our enum."""
        mapping = {
            'info': SecuritySeverity.INFO,
            'low': SecuritySeverity.LOW,
            'moderate': SecuritySeverity.MEDIUM,
            'high': SecuritySeverity.HIGH,
            'critical': SecuritySeverity.CRITICAL
        }
        return mapping.get(severity.lower(), SecuritySeverity.MEDIUM)
    
    def _map_eslint_severity(self, severity: int) -> SecuritySeverity:
        """Map ESLint severity to our enum."""
        if severity == 2:
            return SecuritySeverity.HIGH
        else:
            return SecuritySeverity.MEDIUM
    
    def _map_bandit_vulnerability_type(self, test_id: str) -> VulnerabilityType:
        """Map Bandit test ID to vulnerability type."""
        mapping = {
            'B101': VulnerabilityType.WEAK_CRYPTO,  # assert_used
            'B102': VulnerabilityType.COMMAND_INJECTION,  # exec_used
            'B103': VulnerabilityType.CONFIGURATION_ISSUE,  # set_bad_file_permissions
            'B104': VulnerabilityType.HARDCODED_SECRET,  # hardcoded_bind_all_interfaces
            'B105': VulnerabilityType.HARDCODED_SECRET,  # hardcoded_password_string
            'B106': VulnerabilityType.HARDCODED_SECRET,  # hardcoded_password_funcarg
            'B107': VulnerabilityType.HARDCODED_SECRET,  # hardcoded_password_default
            'B108': VulnerabilityType.CONFIGURATION_ISSUE,  # hardcoded_tmp_directory
            'B201': VulnerabilityType.COMMAND_INJECTION,  # flask_debug_true
            'B301': VulnerabilityType.INSECURE_DESERIALIZATION,  # pickle
            'B302': VulnerabilityType.WEAK_CRYPTO,  # marshal
            'B303': VulnerabilityType.WEAK_CRYPTO,  # md5
            'B304': VulnerabilityType.WEAK_CRYPTO,  # des
            'B305': VulnerabilityType.WEAK_CRYPTO,  # cipher
            'B306': VulnerabilityType.WEAK_CRYPTO,  # mkstemp_q
            'B307': VulnerabilityType.COMMAND_INJECTION,  # eval
            'B308': VulnerabilityType.COMMAND_INJECTION,  # mark_safe
            'B309': VulnerabilityType.WEAK_CRYPTO,  # httpsconnection
            'B310': VulnerabilityType.PATH_TRAVERSAL,  # urllib_urlopen
            'B311': VulnerabilityType.WEAK_CRYPTO,  # random
            'B312': VulnerabilityType.CONFIGURATION_ISSUE,  # telnetlib
            'B313': VulnerabilityType.SQL_INJECTION,  # xml_bad_cElementTree
            'B314': VulnerabilityType.SQL_INJECTION,  # xml_bad_ElementTree
            'B315': VulnerabilityType.SQL_INJECTION,  # xml_bad_expatreader
            'B316': VulnerabilityType.SQL_INJECTION,  # xml_bad_expatbuilder
            'B317': VulnerabilityType.SQL_INJECTION,  # xml_bad_sax
            'B318': VulnerabilityType.SQL_INJECTION,  # xml_bad_minidom
            'B319': VulnerabilityType.SQL_INJECTION,  # xml_bad_pulldom
            'B320': VulnerabilityType.SQL_INJECTION,  # xml_bad_etree
            'B321': VulnerabilityType.CONFIGURATION_ISSUE,  # ftplib
            'B322': VulnerabilityType.COMMAND_INJECTION,  # input
            'B323': VulnerabilityType.PATH_TRAVERSAL,  # unverified_context
            'B324': VulnerabilityType.WEAK_CRYPTO,  # hashlib_new_insecure_functions
            'B325': VulnerabilityType.CONFIGURATION_ISSUE,  # tempnam
            'B501': VulnerabilityType.CONFIGURATION_ISSUE,  # request_with_no_cert_validation
            'B502': VulnerabilityType.CONFIGURATION_ISSUE,  # ssl_with_bad_version
            'B503': VulnerabilityType.CONFIGURATION_ISSUE,  # ssl_with_bad_defaults
            'B504': VulnerabilityType.CONFIGURATION_ISSUE,  # ssl_with_no_version
            'B505': VulnerabilityType.WEAK_CRYPTO,  # weak_cryptographic_key
            'B506': VulnerabilityType.CONFIGURATION_ISSUE,  # yaml_load
            'B507': VulnerabilityType.CONFIGURATION_ISSUE,  # ssh_no_host_key_verification
            'B601': VulnerabilityType.COMMAND_INJECTION,  # paramiko_calls
            'B602': VulnerabilityType.COMMAND_INJECTION,  # subprocess_popen_with_shell_equals_true
            'B603': VulnerabilityType.COMMAND_INJECTION,  # subprocess_without_shell_equals_true
            'B604': VulnerabilityType.COMMAND_INJECTION,  # any_other_function_with_shell_equals_true
            'B605': VulnerabilityType.COMMAND_INJECTION,  # start_process_with_a_shell
            'B606': VulnerabilityType.COMMAND_INJECTION,  # start_process_with_no_shell
            'B607': VulnerabilityType.COMMAND_INJECTION,  # start_process_with_partial_path
            'B608': VulnerabilityType.SQL_INJECTION,  # hardcoded_sql_expressions
            'B609': VulnerabilityType.PATH_TRAVERSAL,  # linux_commands_wildcard_injection
            'B610': VulnerabilityType.SQL_INJECTION,  # django_extra_used
            'B611': VulnerabilityType.SQL_INJECTION,  # django_rawsql_used
            'B701': VulnerabilityType.CONFIGURATION_ISSUE,  # jinja2_autoescape_false
            'B702': VulnerabilityType.CONFIGURATION_ISSUE,  # use_of_mako_templates
            'B703': VulnerabilityType.CONFIGURATION_ISSUE   # django_mark_safe
        }
        return mapping.get(test_id, VulnerabilityType.OTHER)
    
    def _map_eslint_security_rule(self, rule_id: str) -> VulnerabilityType:
        """Map ESLint security rule to vulnerability type."""
        mapping = {
            'security/detect-buffer-noassert': VulnerabilityType.OTHER,
            'security/detect-child-process': VulnerabilityType.COMMAND_INJECTION,
            'security/detect-disable-mustache-escape': VulnerabilityType.XSS,
            'security/detect-eval-with-expression': VulnerabilityType.COMMAND_INJECTION,
            'security/detect-new-buffer': VulnerabilityType.OTHER,
            'security/detect-no-csrf-before-method-override': VulnerabilityType.OTHER,
            'security/detect-non-literal-fs-filename': VulnerabilityType.PATH_TRAVERSAL,
            'security/detect-non-literal-regexp': VulnerabilityType.OTHER,
            'security/detect-non-literal-require': VulnerabilityType.COMMAND_INJECTION,
            'security/detect-object-injection': VulnerabilityType.COMMAND_INJECTION,
            'security/detect-possible-timing-attacks': VulnerabilityType.OTHER,
            'security/detect-pseudoRandomBytes': VulnerabilityType.WEAK_CRYPTO,
            'security/detect-unsafe-regex': VulnerabilityType.OTHER
        }
        return mapping.get(rule_id, VulnerabilityType.OTHER)
    
    def _map_pattern_to_vuln_type(self, pattern_type: str) -> VulnerabilityType:
        """Map pattern type to vulnerability type."""
        mapping = {
            'hardcoded_password': VulnerabilityType.HARDCODED_SECRET,
            'hardcoded_secret': VulnerabilityType.HARDCODED_SECRET,
            'sql_injection': VulnerabilityType.SQL_INJECTION,
            'command_injection': VulnerabilityType.COMMAND_INJECTION,
            'weak_crypto': VulnerabilityType.WEAK_CRYPTO,
            'xss': VulnerabilityType.XSS,
            'insecure_random': VulnerabilityType.WEAK_CRYPTO
        }
        return mapping.get(pattern_type, VulnerabilityType.OTHER)
    
    def _get_pattern_severity(self, pattern_type: str) -> SecuritySeverity:
        """Get severity for pattern-based detections."""
        severity_mapping = {
            'hardcoded_password': SecuritySeverity.HIGH,
            'hardcoded_secret': SecuritySeverity.HIGH,
            'sql_injection': SecuritySeverity.HIGH,
            'command_injection': SecuritySeverity.HIGH,
            'weak_crypto': SecuritySeverity.MEDIUM,
            'xss': SecuritySeverity.HIGH,
            'insecure_random': SecuritySeverity.MEDIUM
        }
        return severity_mapping.get(pattern_type, SecuritySeverity.MEDIUM)
    
    def _get_bandit_remediation(self, test_id: str) -> str:
        """Get remediation advice for Bandit test ID."""
        remediations = {
            'B105': "Use environment variables or secure vaults for passwords",
            'B106': "Don't pass passwords as function arguments",
            'B107': "Avoid hardcoded password defaults",
            'B301': "Avoid pickle for untrusted data - use JSON instead",
            'B302': "Avoid marshal for untrusted data",
            'B303': "Use SHA-256 or stronger hash algorithms instead of MD5",
            'B304': "Use AES instead of DES encryption",
            'B311': "Use secrets.SystemRandom() for cryptographic purposes",
            'B602': "Avoid shell=True in subprocess calls",
            'B608': "Use parameterized queries to prevent SQL injection"
        }
        return remediations.get(test_id, "Review and fix this security issue")
    
    def _get_eslint_security_remediation(self, rule_id: str) -> str:
        """Get remediation advice for ESLint security rule."""
        remediations = {
            'security/detect-child-process': "Validate and sanitize inputs to child process calls",
            'security/detect-eval-with-expression': "Avoid eval() - use safer alternatives like JSON.parse()",
            'security/detect-non-literal-fs-filename': "Validate file paths and use path.join()",
            'security/detect-non-literal-require': "Use static require statements when possible",
            'security/detect-object-injection': "Validate object keys and use Map() for dynamic keys",
            'security/detect-pseudoRandomBytes': "Use crypto.randomBytes() for security purposes"
        }
        return remediations.get(rule_id, "Review and fix this security issue")
    
    def _get_pattern_remediation(self, pattern_type: str) -> str:
        """Get remediation advice for pattern-based detections."""
        remediations = {
            'hardcoded_password': "Move sensitive data to environment variables or secure vaults",
            'hardcoded_secret': "Use environment variables or configuration files for secrets",
            'sql_injection': "Use parameterized queries or ORM methods",
            'command_injection': "Validate inputs and avoid shell execution",
            'weak_crypto': "Use strong cryptographic algorithms (AES, SHA-256+)",
            'xss': "Properly escape user input and use safe templating",
            'insecure_random': "Use cryptographically secure random generators"
        }
        return remediations.get(pattern_type, "Review and fix this security issue")
    
    def _get_pattern_remediation_js(self, pattern_type: str) -> str:
        """Get JavaScript-specific remediation advice."""
        remediations = {
            'hardcoded_secret': "Use environment variables (process.env) for secrets",
            'xss': "Use textContent instead of innerHTML, or sanitize with DOMPurify",
            'command_injection': "Validate inputs and avoid exec/spawn with user data",
            'insecure_random': "Use crypto.randomBytes() or window.crypto.getRandomValues()"
        }
        return remediations.get(pattern_type, "Review and fix this security issue")
    
    def format_report(self, reports: Dict[str, SecurityReport], format_type: str = "terminal") -> str:
        """Format security analysis report."""
        if format_type == "json":
            return json.dumps({
                lang: {
                    "total_files": report.total_files,
                    "total_issues": report.total_issues,
                    "critical_issues": report.critical_issues,
                    "high_issues": report.high_issues,
                    "medium_issues": report.medium_issues,
                    "low_issues": report.low_issues,
                    "is_passing": report.is_passing,
                    "tools_used": report.tools_used,
                    "issues": [
                        {
                            "filename": issue.filename,
                            "line_number": issue.line_number,
                            "vulnerability_type": issue.vulnerability_type.value,
                            "severity": issue.severity.value,
                            "title": issue.title,
                            "description": issue.description,
                            "cwe_id": issue.cwe_id,
                            "confidence": issue.confidence,
                            "remediation": issue.remediation
                        }
                        for issue in report.issues
                    ]
                }
                for lang, report in reports.items()
            }, indent=2)
        
        # Terminal format
        output = []
        output.append("🛡️  SECURITY VULNERABILITY SCAN REPORT")
        output.append("=" * 55)
        
        overall_passing = all(report.is_passing for report in reports.values())
        total_critical = sum(report.critical_issues for report in reports.values())
        total_high = sum(report.high_issues for report in reports.values())
        total_medium = sum(report.medium_issues for report in reports.values())
        total_low = sum(report.low_issues for report in reports.values())
        
        for lang, report in reports.items():
            if lang == 'none':
                continue
            
            output.append(f"\n{lang.upper()} Security Scan:")
            output.append(f"  Files scanned: {report.total_files}")
            output.append(f"  Tools used: {', '.join(report.tools_used) if report.tools_used else 'pattern-matching'}")
            output.append(f"  Total issues: {report.total_issues}")
            
            if report.total_issues > 0:
                output.append(f"    Critical: {report.critical_issues}")
                output.append(f"    High: {report.high_issues}")
                output.append(f"    Medium: {report.medium_issues}")
                output.append(f"    Low: {report.low_issues}")
            
            output.append(f"  Status: {'✅ PASS' if report.is_passing else '❌ FAIL'}")
            
            if report.issues:
                # Show worst issues first
                worst_issues = sorted(report.issues, 
                                    key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x.severity.value), 
                                    reverse=True)[:5]
                output.append("  Top security issues:")
                for issue in worst_issues:
                    severity_icon = {
                        'critical': '🔴',
                        'high': '🟠', 
                        'medium': '🟡',
                        'low': '🔵',
                        'info': '⚪'
                    }.get(issue.severity.value, '❓')
                    
                    output.append(f"    {severity_icon} {issue.filename}:{issue.line_number} - {issue.title}")
        
        output.append(f"\n{'='*55}")
        
        if total_critical + total_high + total_medium + total_low > 0:
            output.append(f"Summary: 🔴 {total_critical} critical, 🟠 {total_high} high, 🟡 {total_medium} medium, 🔵 {total_low} low")
        
        output.append(f"Overall Status: {'✅ PASS' if overall_passing else '❌ FAIL'}")
        
        if not overall_passing:
            output.append("\n❌ Security scan failed. Please address the security vulnerabilities.")
            # Show remediation suggestions
            for lang, report in reports.items():
                if report.issues and report.remediation_suggestions:
                    output.append(f"\n{lang.upper()} Remediation Suggestions:")
                    for suggestion in report.remediation_suggestions[:7]:
                        output.append(f"  • {suggestion}")
        else:
            output.append("\n✅ No security vulnerabilities found!")
        
        return "\n".join(output)


def main():
    """CLI entry point for security scanning."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan code for security vulnerabilities")
    parser.add_argument("--fail-on-severity", choices=["info", "low", "medium", "high", "critical"], 
                       default="medium", help="Minimum severity level to fail on")
    parser.add_argument("--project-dir", default=".", help="Project directory to scan")
    parser.add_argument("--format", choices=["terminal", "json"], default="terminal", help="Output format")
    parser.add_argument("--fail-on-violations", action="store_true", help="Exit with error if violations found")
    
    args = parser.parse_args()
    
    # Configure scanner
    config = {
        'security': {
            'fail_on_severity': args.fail_on_severity
        }
    }
    
    scanner = SecurityScanner(config)
    reports = scanner.validate_security(args.project_dir)
    
    # Output report
    print(scanner.format_report(reports, args.format))
    
    # Exit with error if violations found
    if args.fail_on_violations:
        if not all(report.is_passing for report in reports.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()