#!/usr/bin/env python3
"""
Spec-Kitty Constitutional Help System

Contextual help and guidance system for constitutional compliance within spec-kitty.
Provides real-time assistance, principle explanations, and remediation guidance.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import argparse
import textwrap


@dataclass
class ConstitutionalPrinciple:
    """Constitutional principle definition and guidance."""
    
    name: str
    short_name: str
    description: str
    why_important: str
    common_violations: List[str]
    how_to_fix: List[str]
    examples: Dict[str, str]  # good/bad examples
    tools: List[str]  # tools that help enforce this principle


@dataclass
class HelpTopic:
    """Help topic with detailed guidance."""
    
    topic: str
    summary: str
    detailed_help: str
    related_principles: List[str]
    code_examples: List[str]
    see_also: List[str]


class ConstitutionalHelpSystem:
    """Main help system for constitutional compliance guidance."""
    
    def __init__(self):
        """Initialize the help system with constitutional principles."""
        self.principles = self._load_constitutional_principles()
        self.help_topics = self._load_help_topics()
        self.quick_fixes = self._load_quick_fixes()
    
    def _load_constitutional_principles(self) -> Dict[str, ConstitutionalPrinciple]:
        """Load all constitutional principles with detailed guidance."""
        principles = {}
        
        # 1. Single Responsibility Principle (SRP)
        principles['srp'] = ConstitutionalPrinciple(
            name="Single Responsibility Principle",
            short_name="SRP",
            description="Each class, function, or module should have only one reason to change.",
            why_important="Reduces complexity, improves maintainability, makes testing easier, and enables focused debugging.",
            common_violations=[
                "Functions that do multiple unrelated tasks",
                "Classes that handle both business logic and data persistence",
                "Modules that mix user interface and business logic",
                "Functions with multiple return types or purposes"
            ],
            how_to_fix=[
                "Extract each responsibility into its own function/class",
                "Use composition to combine simple components",
                "Create separate layers (UI, business logic, data)",
                "Apply the 'one reason to change' test"
            ],
            examples={
                "good": """
def calculate_tax(subtotal, tax_rate):
    \"\"\"Calculate tax amount only.\"\"\"
    return subtotal * tax_rate

def format_currency(amount):
    \"\"\"Format amount as currency only.\"\"\"
    return f"${amount:.2f}"
                """,
                "bad": """
def process_order_and_format(items, tax_rate, customer_email):
    \"\"\"This function does too many things!\"\"\"
    # Calculate total (responsibility 1)
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    # Format for display (responsibility 2)
    formatted_total = f"${total:.2f}"
    
    # Send email (responsibility 3)
    send_email(customer_email, f"Total: {formatted_total}")
    
    return total
                """
            },
            tools=["ruff", "complexity analysis", "code review"]
        )
        
        # 2. Encapsulation
        principles['encapsulation'] = ConstitutionalPrinciple(
            name="Encapsulation",
            short_name="Encapsulation",
            description="Hide internal implementation details and provide controlled access through public interfaces.",
            why_important="Prevents direct manipulation of internal state, enables safe refactoring, and provides clear contracts.",
            common_violations=[
                "Public attributes that should be private",
                "Direct access to internal data structures",
                "Missing validation in setters",
                "Exposing implementation details in public APIs"
            ],
            how_to_fix=[
                "Use private attributes (underscore prefix in Python)",
                "Provide getter/setter methods with validation",
                "Create clear public interfaces",
                "Hide implementation details behind abstractions"
            ],
            examples={
                "good": """
class BankAccount:
    def __init__(self, initial_balance=0):
        self._balance = initial_balance  # Private
    
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            return True
        return False
    
    def get_balance(self):
        return self._balance
                """,
                "bad": """
class BankAccount:
    def __init__(self, initial_balance=0):
        self.balance = initial_balance  # Public - dangerous!

# This allows: account.balance = -1000  # Oops!
                """
            },
            tools=["linting tools", "access control analysis", "code review"]
        )
        
        # 3. Loose Coupling
        principles['loose_coupling'] = ConstitutionalPrinciple(
            name="Loose Coupling",
            short_name="Loose Coupling",
            description="Components should depend on abstractions, not concrete implementations.",
            why_important="Enables independent testing, easier refactoring, better modularity, and flexible system architecture.",
            common_violations=[
                "Hard-coded dependencies on specific implementations",
                "Tight coupling between layers",
                "Direct database access from business logic",
                "UI components calling business logic directly"
            ],
            how_to_fix=[
                "Use dependency injection",
                "Define interfaces/abstractions",
                "Apply layered architecture",
                "Use event-driven communication"
            ],
            examples={
                "good": """
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class OrderProcessor:
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service
    
    def process_order(self, order):
        # ... process order ...
        self._notification_service.send("Order confirmed", order.customer)
                """,
                "bad": """
import smtplib

class OrderProcessor:
    def process_order(self, order):
        # Tightly coupled to email implementation
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # ... email logic ...
                """
            },
            tools=["dependency analysis", "architecture review", "interface design"]
        )
        
        # 4. Reusability
        principles['reusability'] = ConstitutionalPrinciple(
            name="Reusability",
            short_name="DRY",
            description="Don't Repeat Yourself - extract common functionality into reusable components.",
            why_important="Reduces maintenance burden, ensures consistency, and improves code quality through shared components.",
            common_violations=[
                "Duplicated validation logic",
                "Copy-pasted code blocks",
                "Similar functions with slight variations",
                "Hardcoded values repeated throughout codebase"
            ],
            how_to_fix=[
                "Extract common code into functions/classes",
                "Create utility libraries",
                "Use configuration files for constants",
                "Apply template/strategy patterns"
            ],
            examples={
                "good": """
def validate_email(email):
    \"\"\"Reusable email validation.\"\"\"
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user(username, email):
    if not validate_email(email):
        raise ValueError("Invalid email")
    # Create user...

def update_user_email(user_id, new_email):
    if not validate_email(new_email):
        raise ValueError("Invalid email")
    # Update email...
                """,
                "bad": """
def create_user(username, email):
    # Duplicated validation logic
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email")

def update_user_email(user_id, new_email):
    # Same validation logic duplicated!
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    if not re.match(pattern, new_email):
        raise ValueError("Invalid email")
                """
            },
            tools=["duplicate code detection", "refactoring tools", "code review"]
        )
        
        # Add remaining principles (5-8) similarly...
        principles['portability'] = ConstitutionalPrinciple(
            name="Portability",
            short_name="Portability",
            description="Code should run consistently across different environments and platforms.",
            why_important="Ensures reliable deployment, easier testing, and better team collaboration.",
            common_violations=[
                "Hardcoded file paths", "Environment-specific assumptions",
                "Platform-dependent code", "Inconsistent dependencies"
            ],
            how_to_fix=[
                "Use environment variables", "Abstract platform differences",
                "Use relative paths", "Containerize applications"
            ],
            examples={
                "good": "CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/default.json')",
                "bad": "CONFIG_PATH = '/home/user/myapp/config.json'"
            },
            tools=["environment management", "containerization", "cross-platform testing"]
        )
        
        principles['defensibility'] = ConstitutionalPrinciple(
            name="Defensibility",
            short_name="Security",
            description="Security by design with input validation and secure defaults.",
            why_important="Protects against vulnerabilities, ensures data integrity, and maintains user trust.",
            common_violations=[
                "Missing input validation", "SQL injection vulnerabilities",
                "Insecure defaults", "Exposed sensitive data"
            ],
            how_to_fix=[
                "Validate all inputs", "Use parameterized queries",
                "Apply principle of least privilege", "Encrypt sensitive data"
            ],
            examples={
                "good": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
                "bad": "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
            },
            tools=["bandit", "security scanning", "vulnerability assessment"]
        )
        
        principles['maintainability'] = ConstitutionalPrinciple(
            name="Maintainability",
            short_name="Maintainability",
            description="Code should be self-documenting with clear naming and comprehensive tests.",
            why_important="Reduces onboarding time, enables safe refactoring, and improves long-term productivity.",
            common_violations=[
                "Unclear variable names", "Missing documentation",
                "Low test coverage", "Complex nested logic"
            ],
            how_to_fix=[
                "Use descriptive names", "Add comprehensive docstrings",
                "Write thorough tests", "Refactor complex functions"
            ],
            examples={
                "good": "def calculate_monthly_payment(principal, annual_rate, years):",
                "bad": "def calc(p, r, y):"
            },
            tools=["pytest", "coverage analysis", "documentation tools"]
        )
        
        principles['simplicity'] = ConstitutionalPrinciple(
            name="Simplicity",
            short_name="YAGNI",
            description="You Aren't Gonna Need It - prefer simple solutions over complex ones.",
            why_important="Reduces cognitive load, minimizes bugs, and speeds up development.",
            common_violations=[
                "Over-engineering solutions", "Premature optimization",
                "Unnecessary abstractions", "Complex inheritance hierarchies"
            ],
            how_to_fix=[
                "Start with simple solutions", "Refactor when complexity is needed",
                "Avoid speculative features", "Prefer composition over inheritance"
            ],
            examples={
                "good": "return max(numbers) if numbers else 0",
                "bad": "# 20 lines of complex logic to find maximum"
            },
            tools=["complexity analysis", "code review", "refactoring tools"]
        )
        
        return principles
    
    def _load_help_topics(self) -> Dict[str, HelpTopic]:
        """Load help topics with detailed guidance."""
        topics = {}
        
        topics['getting-started'] = HelpTopic(
            topic="Getting Started with Constitutional Compliance",
            summary="Quick setup guide for constitutional enforcement",
            detailed_help="""
Constitutional compliance at TeamReel is about building maintainable, secure, and scalable software.

Quick Start:
1. Install tools: pip install ruff pytest pytest-cov bandit
2. Set up pre-commit hooks: pre-commit install
3. Run constitutional validator: python src/constitutional_validator.py
4. Fix any violations found
5. Commit with confidence!

The system enforces 8 core SE principles automatically through quality gates.
            """,
            related_principles=["srp", "maintainability", "simplicity"],
            code_examples=[],
            see_also=["quality-gates", "pre-commit", "dashboard"]
        )
        
        topics['quality-gates'] = HelpTopic(
            topic="Quality Gates & Enforcement",
            summary="Understanding the automated quality gates",
            detailed_help="""
Quality gates are automated checks that enforce constitutional principles:

1. Code Quality (Ruff): Checks for style, complexity, and potential bugs
2. Test Coverage: Ensures minimum 80% test coverage
3. Security Scan (Bandit): Detects security vulnerabilities
4. Complexity Analysis: Ensures functions stay under complexity limit of 10

Failed quality gates block commits and deployments until fixed.
            """,
            related_principles=["maintainability", "defensibility", "simplicity"],
            code_examples=[],
            see_also=["getting-started", "violations", "dashboard"]
        )
        
        topics['violations'] = HelpTopic(
            topic="Common Violations & How to Fix Them",
            summary="Guide to resolving constitutional violations",
            detailed_help="""
Most common violations and their fixes:

1. High Complexity: Break large functions into smaller ones
2. Low Test Coverage: Add unit tests for uncovered code
3. Security Issues: Fix input validation and SQL injection risks
4. Code Duplication: Extract common code into reusable functions
5. Poor Naming: Use descriptive, intention-revealing names

Use 'constitutional-help fix <violation-type>' for specific guidance.
            """,
            related_principles=["srp", "reusability", "maintainability", "defensibility"],
            code_examples=[],
            see_also=["quality-gates", "principles", "tools"]
        )
        
        return topics
    
    def _load_quick_fixes(self) -> Dict[str, str]:
        """Load quick fix templates for common violations."""
        return {
            "complexity": """
To fix high complexity:

1. Identify the complex function
2. Look for nested if/else statements or loops
3. Extract logic into smaller functions:

# Before (complex)
def process_data(data):
    if condition1:
        if condition2:
            # ... lots of nested logic

# After (simple)
def process_data(data):
    if not meets_criteria(data):
        return None
    return transform_data(data)

def meets_criteria(data):
    return condition1 and condition2

def transform_data(data):
    # ... transformation logic
            """,
            "coverage": """
To fix low test coverage:

1. Identify uncovered code: pytest --cov=. --cov-report=html
2. Add tests for each uncovered function:

# test_example.py
def test_calculate_tax():
    result = calculate_tax(100, 0.08)
    assert result == 8.0

def test_calculate_tax_zero_rate():
    result = calculate_tax(100, 0)
    assert result == 0

3. Aim for edge cases and error conditions
4. Run tests: pytest
            """,
            "security": """
To fix security issues:

1. SQL Injection - use parameterized queries:
   # Bad: f"SELECT * FROM users WHERE id = {user_id}"
   # Good: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

2. Input Validation - validate all inputs:
   def create_user(email):
       if not validate_email(email):
           raise ValueError("Invalid email")

3. Secure Defaults - use secure configurations
4. Secrets - never hardcode passwords or API keys
            """
        }
    
    def show_help(self, topic: Optional[str] = None) -> str:
        """Show help for a specific topic or general help."""
        if not topic:
            return self._show_general_help()
        
        if topic in self.principles:
            return self._show_principle_help(topic)
        
        if topic in self.help_topics:
            return self._show_topic_help(topic)
        
        if topic in self.quick_fixes:
            return self._show_quick_fix(topic)
        
        return f"❌ Unknown help topic: {topic}\\n\\nAvailable topics: {', '.join(self._get_all_topics())}"
    
    def _show_general_help(self) -> str:
        """Show general help overview."""
        return """
🏛️ TeamReel Constitutional Help System

Constitutional software engineering ensures your code follows proven SE principles 
through automated enforcement and quality gates.

📚 HELP TOPICS:
  getting-started    - Quick setup guide
  quality-gates      - Understanding enforcement
  violations         - Common issues and fixes
  dashboard          - Compliance monitoring
  principles         - All 8 constitutional principles
  tools              - Available tools and commands

🔍 CONSTITUTIONAL PRINCIPLES:
  srp               - Single Responsibility Principle
  encapsulation     - Information hiding and data protection
  loose-coupling    - Dependency management
  reusability       - DRY (Don't Repeat Yourself)
  portability       - Platform independence
  defensibility     - Security by design
  maintainability   - Self-documenting code
  simplicity        - YAGNI (You Aren't Gonna Need It)

⚡ QUICK FIXES:
  complexity        - Fix high complexity functions
  coverage          - Improve test coverage
  security          - Resolve security vulnerabilities

💡 USAGE:
  constitutional-help <topic>           - Get detailed help
  constitutional-help principles        - List all principles
  constitutional-help srp               - Learn about SRP
  constitutional-help violations        - Common violations guide

🚀 QUICK START:
  1. Run: python src/constitutional_validator.py
  2. Fix any violations found
  3. Commit with confidence!

For more help: constitutional-help getting-started
        """
    
    def _show_principle_help(self, principle_key: str) -> str:
        """Show detailed help for a constitutional principle."""
        principle = self.principles[principle_key]
        
        help_text = f"""
🏛️ {principle.name} ({principle.short_name})

📖 DESCRIPTION:
{textwrap.fill(principle.description, width=70)}

🎯 WHY IT'S IMPORTANT:
{textwrap.fill(principle.why_important, width=70)}

❌ COMMON VIOLATIONS:
"""
        for violation in principle.common_violations:
            help_text += f"  • {violation}\\n"
        
        help_text += f"""
✅ HOW TO FIX:
"""
        for fix in principle.how_to_fix:
            help_text += f"  • {fix}\\n"
        
        if principle.examples.get('good') or principle.examples.get('bad'):
            help_text += f"""
💡 EXAMPLES:

✅ Good Example:
{principle.examples.get('good', 'No example available')}

❌ Bad Example:
{principle.examples.get('bad', 'No example available')}
"""
        
        help_text += f"""
🔧 ENFORCEMENT TOOLS:
{', '.join(principle.tools)}

💡 TIP: Run 'constitutional-help violations' for common fixes
        """
        
        return help_text
    
    def _show_topic_help(self, topic_key: str) -> str:
        """Show help for a specific topic."""
        topic = self.help_topics[topic_key]
        
        help_text = f"""
📚 {topic.topic}

{topic.summary}

{topic.detailed_help}
"""
        
        if topic.related_principles:
            help_text += f"""
🏛️ RELATED PRINCIPLES:
{', '.join(topic.related_principles)}
"""
        
        if topic.see_also:
            help_text += f"""
🔗 SEE ALSO:
{', '.join(topic.see_also)}
"""
        
        return help_text
    
    def _show_quick_fix(self, fix_key: str) -> str:
        """Show quick fix guide."""
        return f"""
⚡ QUICK FIX: {fix_key.upper()}

{self.quick_fixes[fix_key]}

💡 Need more help? Try: constitutional-help violations
        """
    
    def _get_all_topics(self) -> List[str]:
        """Get list of all available help topics."""
        topics = list(self.help_topics.keys())
        topics.extend(self.principles.keys())
        topics.extend(self.quick_fixes.keys())
        return sorted(topics)
    
    def list_principles(self) -> str:
        """List all constitutional principles with brief descriptions."""
        output = "🏛️ Constitutional Principles:\\n\\n"
        
        for key, principle in self.principles.items():
            output += f"  {principle.short_name:15} - {principle.description}\\n"
        
        output += "\\n💡 Use 'constitutional-help <principle>' for detailed guidance"
        return output
    
    def search_help(self, query: str) -> str:
        """Search help content for a query."""
        results = []
        query_lower = query.lower()
        
        # Search principles
        for key, principle in self.principles.items():
            if (query_lower in principle.name.lower() or 
                query_lower in principle.description.lower() or
                any(query_lower in violation.lower() for violation in principle.common_violations)):
                results.append(f"principle:{key} - {principle.name}")
        
        # Search topics
        for key, topic in self.help_topics.items():
            if (query_lower in topic.topic.lower() or 
                query_lower in topic.summary.lower() or
                query_lower in topic.detailed_help.lower()):
                results.append(f"topic:{key} - {topic.topic}")
        
        # Search quick fixes
        for key, fix_content in self.quick_fixes.items():
            if query_lower in fix_content.lower():
                results.append(f"fix:{key} - Quick fix for {key}")
        
        if not results:
            return f"❌ No help found for '{query}'\\n\\nTry: constitutional-help principles"
        
        output = f"🔍 Search results for '{query}':\\n\\n"
        for result in results[:10]:  # Limit to top 10 results
            output += f"  • {result}\\n"
        
        if len(results) > 10:
            output += f"  ... and {len(results) - 10} more results\\n"
        
        return output


def main():
    """Main CLI interface for the constitutional help system."""
    parser = argparse.ArgumentParser(
        description="TeamReel Constitutional Help System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  constitutional-help                    - Show general help
  constitutional-help srp                - Learn about Single Responsibility Principle
  constitutional-help violations         - Common violations and fixes
  constitutional-help getting-started    - Quick setup guide
  constitutional-help search "test"      - Search help content
        """
    )
    
    parser.add_argument(
        'topic',
        nargs='?',
        help='Help topic to display (principle, topic, or quick fix)'
    )
    
    parser.add_argument(
        '--list-principles',
        action='store_true',
        help='List all constitutional principles'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search help content for a query'
    )
    
    args = parser.parse_args()
    
    help_system = ConstitutionalHelpSystem()
    
    if args.list_principles:
        print(help_system.list_principles())
    elif args.search:
        print(help_system.search_help(args.search))
    else:
        print(help_system.show_help(args.topic))


if __name__ == "__main__":
    main()