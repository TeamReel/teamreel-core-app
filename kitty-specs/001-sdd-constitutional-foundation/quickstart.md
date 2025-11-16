# TeamReel SDD Constitutional Foundation - Quick Start Guide

## Overview
This guide helps you get started with the TeamReel Constitutional Foundation system that enforces 8 Software Engineering principles throughout your development workflow.

## Prerequisites
- Python 3.11+
- PowerShell 5.1+ (Windows) or Bash (Linux/macOS)
- Git 2.30+
- spec-kitty CLI installed
- TeamReel repository access

## Installation

### 1. Initialize Constitutional Foundation
```bash
# From your TeamReel project root
spec-kitty init-constitution

# This creates:
# - .kittify/memory/constitution.md (SE principles)
# - .kittify/config/quality-gates.yaml (quality thresholds)
# - .kittify/templates/manifest.yaml (template registry)
```

### 2. Install Git Hooks
```bash
# Install constitutional validation hooks
spec-kitty install-hooks

# Creates:
# - .git/hooks/pre-commit (SE principle validation)
# - .git/hooks/pre-push (quality gate validation)
```

### 3. Configure GitHub Actions
```yaml
# .github/workflows/constitutional-compliance.yml
name: Constitutional Compliance

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  constitutional-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Constitutional Compliance Check
        uses: ./.github/actions/constitutional-validator
        with:
          strict_mode: true
          quality_gates: true
          
      - name: Block Merge on Violations
        if: failure()
        run: |
          echo "Constitutional violations detected. Merge blocked."
          exit 1
```

## Usage

### Creating Features (Spec-Driven)
```bash
# 1. Create new feature with constitutional validation
spec-kitty specify "User Authentication System"

# 2. Plan feature with SE principle compliance
spec-kitty plan

# 3. Generate tasks with quality gate integration
spec-kitty tasks

# 4. Implement with continuous validation
# (Git hooks automatically validate on commit/push)
```

### Manual Constitutional Validation
```bash
# Validate specific file against SE principles
spec-kitty validate --file src/auth/models.py

# Validate entire feature specification
spec-kitty validate --spec kitty-specs/002-auth-system/spec.md

# Check quality gates
spec-kitty quality-gates --check-all
```

### Template Management
```bash
# Sync templates with constitutional requirements
spec-kitty sync-templates

# Validate template compliance
spec-kitty validate-templates

# Update constitutional version
spec-kitty update-constitution --version 1.2.0
```

## Constitutional Principles Integration

### 1. Single Responsibility Principle (SRP)
- **Validation**: Each function/class has one clear purpose
- **Implementation**: Automated analysis of function complexity and cohesion
- **Fix**: Split multi-purpose functions into focused units

### 2. Encapsulation
- **Validation**: Private members properly hidden, public interfaces clean
- **Implementation**: Access modifier analysis, interface design validation
- **Fix**: Add proper access control, define clear public APIs

### 3. Loose Coupling
- **Validation**: Minimal dependencies between modules
- **Implementation**: Import analysis, dependency graph validation
- **Fix**: Introduce interfaces, reduce direct dependencies

### 4. Reusability
- **Validation**: Code duplication detection, component composition analysis
- **Implementation**: AST analysis for duplicate patterns
- **Fix**: Extract common functionality, create reusable components

### 5. Portability
- **Validation**: Environment-specific code detection
- **Implementation**: Hard-coded path analysis, platform dependency checks
- **Fix**: Use environment variables, abstract platform-specific code

### 6. Defensibility
- **Validation**: Input validation, error handling, security practices
- **Implementation**: Security linting, input sanitization checks
- **Fix**: Add input validation, implement proper error handling

### 7. Maintainability
- **Validation**: Code complexity, documentation coverage, test coverage
- **Implementation**: Cyclomatic complexity analysis, documentation parsing
- **Fix**: Simplify complex functions, add documentation and tests

### 8. Simplicity (KISS)
- **Validation**: Over-engineering detection, unnecessary complexity analysis
- **Implementation**: Code pattern analysis, abstraction level validation
- **Fix**: Simplify logic, remove unnecessary abstractions

## Quality Gates

### Coverage Requirements
- **Unit Tests**: ≥80% coverage
- **Integration Tests**: ≥60% coverage
- **E2E Tests**: ≥40% coverage

### Complexity Limits
- **Cyclomatic Complexity**: ≤10 per function
- **Cognitive Complexity**: ≤15 per function
- **Function Length**: ≤50 lines
- **Class Length**: ≤300 lines

### Security Requirements
- **Vulnerability Scan**: No HIGH/CRITICAL vulnerabilities
- **Dependency Audit**: All dependencies security-audited
- **Secrets Scan**: No secrets in code
- **GDPR Compliance**: No PII logging

## Troubleshooting

### Common Issues

#### Constitutional Violation: SRP
```bash
Error: Function 'process_user_data' violates SRP
- Current responsibilities: validation, processing, storage
- Suggested fix: Split into validate_user_data(), process_user_data(), store_user_data()
```

#### Quality Gate Failure: Coverage
```bash
Error: Test coverage below threshold
- Current: 65%
- Required: 80%
- Missing coverage in: src/auth/validators.py (lines 45-67)
```

#### Template Sync Required
```bash
Warning: Templates out of sync with constitution v1.1.0
- Affected: spec-template.md, plan-template.md
- Action: Run 'spec-kitty sync-templates' to update
```

### Recovery Actions

#### Force Override (Emergency Only)
```bash
# Override constitutional validation (requires approval)
spec-kitty validate --override --reason "Emergency hotfix for security issue"

# Override quality gates (requires senior developer approval)
spec-kitty quality-gates --override --approver john.doe@teamreel.com
```

#### Reset Constitutional State
```bash
# Reset all constitutional tracking
spec-kitty reset-constitution

# Reinitialize with clean state
spec-kitty init-constitution --force
```

## Best Practices

### Development Workflow
1. **Start with Spec**: Always begin with `spec-kitty specify`
2. **Plan Thoroughly**: Use `spec-kitty plan` to validate approach
3. **Commit Often**: Git hooks provide immediate feedback
4. **Test Continuously**: Maintain quality gate compliance
5. **Document Changes**: Update specs when implementing

### Team Collaboration
1. **Constitutional Reviews**: Include SE principle compliance in code reviews
2. **Quality Metrics**: Monitor team compliance dashboard
3. **Training**: Regular sessions on SE principles application
4. **Feedback Loop**: Improve constitutional rules based on team feedback

### Performance Optimization
- **Incremental Validation**: Only validate changed files
- **Cache Results**: Reuse validation results for unchanged code
- **Parallel Processing**: Run quality gates in parallel
- **Early Feedback**: Fail fast on critical violations

## Dashboard & Metrics

Access the constitutional compliance dashboard:
```bash
spec-kitty dashboard

# Shows:
# - Team compliance scores by SE principle
# - Quality gate pass/fail trends
# - Template synchronization status
# - Feature lifecycle progression
```

## Support & Documentation

- **Constitution Reference**: `.kittify/memory/constitution.md`
- **Quality Gate Config**: `.kittify/config/quality-gates.yaml`
- **Template Documentation**: `.kittify/templates/README.md`
- **Team Guidelines**: `docs/constitutional-development.md`

For issues and feature requests, contact the TeamReel development team or create an issue in the project repository.