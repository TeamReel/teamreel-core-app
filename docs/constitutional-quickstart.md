# Constitutional Quick-Start Guide for Developers

Welcome to project's Constitutional Software Engineering system! This guide will help you set up and integrate constitutional enforcement into your development workflow in under 30 minutes.

## What is Constitutional Software Engineering?

project's constitutional system ensures that all code adheres to proven Software Engineering (SE) principles through **mandatory automated enforcement**. Think of it as having an experienced senior engineer reviewing every line of code for architectural quality, maintainability, and security.

### The 8 Constitutional Principles

1. **Single Responsibility Principle (SRP)** - Each function/class does one thing well
2. **Encapsulation** - Data and implementation details are properly protected
3. **Loose Coupling** - Components are independently deployable and testable
4. **Reusability** - Common functionality is extracted and shared
5. **Portability** - Code runs consistently across environments
6. **Defensibility** - Security by design with input validation and secure defaults
7. **Maintainability** - Self-documenting code with comprehensive test coverage
8. **Simplicity** - Prefer simple solutions over complex ones (YAGNI)

## Quick Setup (< 30 Minutes)

### Prerequisites

- Python 3.11+ installed
- Git configured
- Your favorite code editor (VS Code recommended)
- PowerShell/Bash terminal access

### Step 1: Constitutional Environment Setup (5 min)

```bash
# 1. Clone or navigate to your project project
cd your-project-project

# 2. Install ALL constitutional dependencies (includes dashboard)
pip install -r requirements.txt

# Alternative: Install minimal constitutional enforcement tools only
# pip install ruff pytest pytest-cov bandit safety flask

# 3. Verify installation
python -c "import ruff, flask; print('✅ Constitutional tools and dashboard dependencies installed')"
```

**📋 What's Included in requirements.txt:**
- **Flask**: Web dashboard for compliance monitoring
- **Ruff**: Fast Python linter and formatter
- **Pytest**: Testing framework with coverage
- **Bandit**: Security vulnerability scanner
- **Pre-commit**: Git hooks for quality gates
- **Other**: CLI tools, YAML parsing, date utilities

### Step 2: Configure Pre-Commit Hooks (5 min)

```bash
# 1. Install pre-commit
pip install pre-commit

# 2. Create .pre-commit-config.yaml in your project root
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.', '-f', 'json', '-o', 'bandit-report.json']
EOF

# 3. Install the git hook scripts
pre-commit install

# 4. Test the hooks
pre-commit run --all-files
```

### Step 3: Constitutional Validator Setup (10 min)

```bash
# 1. Create constitutional validator script
mkdir -p src
cat > src/constitutional_validator.py << 'EOF'
#!/usr/bin/env python3
"""Quick constitutional validator for development."""

import subprocess
import sys
from pathlib import Path

def run_constitutional_checks():
    """Run all constitutional compliance checks."""
    checks_passed = 0
    total_checks = 4
    
    print("🏛️ Running Constitutional Compliance Checks...")
    
    # 1. Code Quality (Ruff)
    try:
        result = subprocess.run(['ruff', 'check', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Code Quality: PASS")
            checks_passed += 1
        else:
            print("❌ Code Quality: FAIL")
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️  Ruff not installed - install with: pip install ruff")
    
    # 2. Test Coverage  
    try:
        result = subprocess.run(['pytest', '--cov=.', '--cov-fail-under=80'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Test Coverage (≥80%): PASS")
            checks_passed += 1
        else:
            print("❌ Test Coverage: FAIL")
            print("Need minimum 80% test coverage")
    except FileNotFoundError:
        print("⚠️  Pytest not installed - install with: pip install pytest pytest-cov")
    
    # 3. Security Scan
    try:
        result = subprocess.run(['bandit', '-r', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Security Scan: PASS")
            checks_passed += 1
        else:
            print("❌ Security Scan: FAIL")
            print("Security vulnerabilities detected")
    except FileNotFoundError:
        print("⚠️  Bandit not installed - install with: pip install bandit")
    
    # 4. Complexity Check (via Ruff)
    try:
        result = subprocess.run(['ruff', 'check', '--select', 'C901', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Complexity Check (≤10): PASS")
            checks_passed += 1
        else:
            print("❌ Complexity Check: FAIL")
            print("Functions exceed complexity limit of 10")
    except FileNotFoundError:
        pass
    
    # Overall Result
    compliance_score = (checks_passed / total_checks) * 100
    print(f"\n📊 Constitutional Compliance: {compliance_score:.0f}% ({checks_passed}/{total_checks})")
    
    if compliance_score >= 80:
        print("🎉 Constitutional compliance achieved!")
        return True
    else:
        print("🚫 Constitutional violations detected - please fix before committing")
        return False

if __name__ == "__main__":
    success = run_constitutional_checks()
    sys.exit(0 if success else 1)
EOF

# 2. Make it executable
chmod +x src/constitutional_validator.py

# 3. Test the validator
python src/constitutional_validator.py
```

### Step 4: IDE Integration (5 min)

#### VS Code Setup

```bash
# 1. Create VS Code settings
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true,
        "source.fixAll": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true
    }
}
EOF

# 2. Create launch configuration for debugging
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Constitutional Validator",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/constitutional_validator.py",
            "console": "integratedTerminal"
        }
    ]
}
EOF
```

### Step 5: Verify Setup (5 min)

```bash
# 1. Create a simple test file
cat > test_constitutional_setup.py << 'EOF'
"""Test file to verify constitutional setup."""

def simple_function():
    """A simple function that follows SRP."""
    return "Constitutional enforcement is working!"

def test_simple_function():
    """Test the simple function."""
    result = simple_function()
    assert result == "Constitutional enforcement is working!"
    
if __name__ == "__main__":
    print(simple_function())
EOF

# 2. Run constitutional checks
python src/constitutional_validator.py

# 3. Test pre-commit hooks
git add test_constitutional_setup.py
git commit -m "Test: Verify constitutional setup"

# 4. Clean up test file
rm test_constitutional_setup.py
```

## Daily Development Workflow

### Before You Start Coding

```bash
# 1. Check constitutional status
python src/constitutional_validator.py

# 2. Pull latest changes
git pull origin main

# 3. Verify pre-commit hooks are active
pre-commit run --all-files
```

### While Coding

1. **Follow the 8 Constitutional Principles** (see reference section below)
2. **Write tests first** (TDD approach)
3. **Keep functions simple** (≤ 10 lines preferred, ≤ 15 max complexity)
4. **Use descriptive names** for variables, functions, and classes
5. **Add docstrings** to all public functions and classes

### Before Committing

```bash
# 1. Run constitutional validator
python src/constitutional_validator.py

# 2. Fix any violations found
# ... make your fixes ...

# 3. Run tests
pytest

# 4. Commit (pre-commit hooks will run automatically)
git add .
git commit -m "feat: Your descriptive commit message"
```

### If Constitutional Checks Fail

1. **Read the error messages carefully** - they contain specific guidance
2. **Fix violations one at a time** - don't try to fix everything at once
3. **Use the Constitutional Reference** below for guidance
4. **Ask for help** if you're stuck - constitutional compliance is a team effort

## Constitutional Reference for Developers

### 1. Single Responsibility Principle (SRP)

**✅ Good:**
```python
def calculate_total_price(items, tax_rate):
    """Calculate total price including tax."""
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

def format_price_display(price):
    """Format price for display."""
    return f"${price:.2f}"
```

**❌ Bad:**
```python
def process_order(items, tax_rate, customer_email):
    """This function does too many things!"""
    # Calculating price
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    # Formatting for display  
    formatted_total = f"${total:.2f}"
    
    # Sending email
    send_email(customer_email, f"Your order total: {formatted_total}")
    
    # Updating database
    update_order_history(customer_email, total)
    
    return total
```

### 2. Encapsulation

**✅ Good:**
```python
class UserAccount:
    def __init__(self, username):
        self._username = username
        self._balance = 0.0  # Private attribute
    
    def deposit(self, amount):
        """Public method to safely modify balance."""
        if amount > 0:
            self._balance += amount
            return True
        return False
    
    def get_balance(self):
        """Public method to safely access balance."""
        return self._balance
```

**❌ Bad:**
```python
class UserAccount:
    def __init__(self, username):
        self.username = username
        self.balance = 0.0  # Public - can be modified directly!

# This allows dangerous direct access:
account.balance = -1000  # Oops!
```

### 3. Loose Coupling

**✅ Good:**
```python
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class EmailService(NotificationService):
    def send(self, message, recipient):
        # Email implementation
        pass

class OrderProcessor:
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service
    
    def process_order(self, order):
        # Process order...
        self._notification_service.send("Order confirmed", order.customer_email)
```

**❌ Bad:**
```python
import smtplib

class OrderProcessor:
    def process_order(self, order):
        # Tightly coupled to email - hard to test or change
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.send_message(msg)
```

### 4. Reusability & DRY

**✅ Good:**
```python
def validate_email(email):
    """Reusable email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user(username, email):
    if not validate_email(email):
        raise ValueError("Invalid email")
    # Create user...

def update_user_email(user_id, new_email):
    if not validate_email(new_email):
        raise ValueError("Invalid email")
    # Update email...
```

**❌ Bad:**
```python
def create_user(username, email):
    # Duplicated validation logic
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email")
    # Create user...

def update_user_email(user_id, new_email):
    # Same validation logic duplicated!
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, new_email):
        raise ValueError("Invalid email")
    # Update email...
```

### 5. Maintainability

**✅ Good:**
```python
def calculate_shipping_cost(weight_kg: float, distance_km: float, is_express: bool = False) -> float:
    """
    Calculate shipping cost based on package weight and delivery distance.
    
    Args:
        weight_kg: Package weight in kilograms
        distance_km: Delivery distance in kilometers  
        is_express: Whether express delivery is requested
        
    Returns:
        Shipping cost in dollars
        
    Raises:
        ValueError: If weight or distance is negative
    """
    if weight_kg < 0 or distance_km < 0:
        raise ValueError("Weight and distance must be positive")
    
    BASE_RATE = 5.00
    COST_PER_KG = 2.50
    COST_PER_KM = 0.10
    EXPRESS_MULTIPLIER = 1.5
    
    base_cost = BASE_RATE + (weight_kg * COST_PER_KG) + (distance_km * COST_PER_KM)
    
    if is_express:
        base_cost *= EXPRESS_MULTIPLIER
        
    return round(base_cost, 2)
```

**❌ Bad:**
```python
def calc(w, d, e=False):
    # What does this function do? What are w, d, e?
    return 5 + w * 2.5 + d * 0.1 * (1.5 if e else 1)
```

## Common Constitutional Violations & Fixes

### High Complexity Functions

**Problem:** Function has cyclomatic complexity > 10

**Fix:** Break into smaller functions:

```python
# ❌ Too complex
def process_user_data(data):
    if data.get('type') == 'premium':
        if data.get('payment_status') == 'paid':
            if data.get('verification') == 'complete':
                # ... 20 more lines of nested logic
                
# ✅ Better - extracted functions
def is_premium_user(data):
    return data.get('type') == 'premium'

def has_valid_payment(data):
    return data.get('payment_status') == 'paid'

def is_verified(data):
    return data.get('verification') == 'complete'

def process_user_data(data):
    if is_premium_user(data) and has_valid_payment(data) and is_verified(data):
        return process_premium_user(data)
    return process_regular_user(data)
```

### Low Test Coverage

**Problem:** Test coverage below 80%

**Fix:** Add comprehensive tests:

```python
# test_shipping.py
import pytest
from shipping import calculate_shipping_cost

def test_basic_shipping_cost():
    cost = calculate_shipping_cost(1.0, 10.0)
    assert cost == 12.5  # 5 + 2.5 + 1.0

def test_express_shipping():
    cost = calculate_shipping_cost(1.0, 10.0, is_express=True)
    assert cost == 18.75  # (5 + 2.5 + 1.0) * 1.5

def test_negative_weight_raises_error():
    with pytest.raises(ValueError):
        calculate_shipping_cost(-1.0, 10.0)

def test_zero_distance():
    cost = calculate_shipping_cost(1.0, 0.0)
    assert cost == 7.5  # 5 + 2.5 + 0
```

### Security Vulnerabilities

**Problem:** Bandit detects security issues

**Fix:** Address each vulnerability:

```python
# ❌ Security issue - SQL injection risk
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# ✅ Fixed - using parameterized queries  
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
```

## Advanced Constitutional Tools

### Constitutional Compliance Dashboard

```bash
# Start the web-based dashboard
python src/dashboard.py

# Open in browser: http://localhost:8080
# View real-time compliance metrics, team performance, and violation trends
```

### Automated CI/CD Integration

Add to your `.github/workflows/constitutional-compliance.yml`:

```yaml
name: Constitutional Compliance Check

on: [push, pull_request]

jobs:
  constitutional-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff pytest pytest-cov bandit safety
          
      - name: Run Constitutional Validator
        run: python src/constitutional_validator.py
        
      - name: Block merge on violations
        if: failure()
        run: |
          echo "❌ Constitutional violations detected!"
          echo "Please fix all violations before merging."
          exit 1
```

### Team Metrics and Reporting

```bash
# Generate team constitutional report
python -c "
from src.dashboard import ConstitutionalDashboard
dashboard = ConstitutionalDashboard()
metrics = dashboard._get_latest_compliance_metrics()
for metric in metrics:
    print(f'{metric.principle}: {metric.score:.1f}% ({metric.status})')
"
```

## Troubleshooting

### "Ruff not found" error

```bash
pip install ruff
# or
pip install --upgrade ruff
```

### "Pre-commit hooks not running"

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test manually
pre-commit run --all-files
```

### "Constitutional validator fails"

1. Check Python version: `python --version` (should be 3.11+)
2. Install missing dependencies: `pip install -r requirements.txt`
3. Run individual checks to isolate the issue:
   ```bash
   ruff check .
   pytest --cov=.
   bandit -r .
   ```

### "VS Code not showing violations"

1. Install Python extension
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Check Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"

## Getting Help

### Constitutional Violation Assistance

1. **Read the error message carefully** - it contains specific guidance
2. **Check this guide** for examples and patterns
3. **Ask teammates** - constitutional compliance is a team responsibility
4. **Review the project mission statement** in `.kittify/memory/mission.md`

### Resources

- **Constitutional Dashboard**: `http://localhost:8080` (when running)
- **Mission Statement**: `.kittify/memory/mission.md`
- **Team Slack**: `#constitutional-engineering` channel
- **Documentation**: `docs/` directory

### Constitutional Champions

Each team has designated Constitutional Champions who can help with:
- Complex architectural decisions
- Constitutional principle interpretation
- Code review and pair programming
- Training and onboarding

## Next Steps

1. **Complete this setup** (should take < 30 minutes)
2. **Run your first constitutional check**: `python src/constitutional_validator.py`
3. **Make your first constitutional commit** following the workflow above
4. **Explore the dashboard** at `http://localhost:8080`
5. **Join the team** in maintaining constitutional excellence!

---

**Welcome to Constitutional Software Engineering at project!** 🏛️

*This guide is your gateway to building maintainable, secure, and scalable software that follows proven engineering principles. Constitutional compliance isn't just about passing tests—it's about building software that stands the test of time.*