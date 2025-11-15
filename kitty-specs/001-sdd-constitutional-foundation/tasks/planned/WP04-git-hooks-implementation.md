---
work_package_id: "WP04"
subtasks:
  - "T011"
  - "T012"
  - "T013"
  - "T014"
title: "Git Hooks Implementation"
phase: "Phase 1 - Foundation Setup"
lane: "planned"
assignee: ""
agent: ""
shell_pid: ""
review_status: ""
reviewed_by: ""
history:
  - timestamp: "2025-11-15T10:00:00Z"
    lane: "planned"
    agent: "system"
    shell_pid: ""
    action: "Prompt generated via /spec-kitty.tasks"
---

# Work Package Prompt: WP04 – Git Hooks Implementation

## Objectives & Success Criteria

**Primary Goal**: User Story 1 - Automated constitutional enforcement at commit/push level with immediate developer feedback.

**Success Criteria**:
- Pre-commit hooks block commits with SE principle violations
- Pre-push hooks enforce quality gates (coverage, complexity, security)
- Git hook installation is automated and cross-platform
- Violation reports provide specific line numbers and remediation guidance

**Independent Test**: Commit code with complexity >10 and verify Git hooks block with specific violation details.

## SE Principles Compliance *(mandatory)*

### Architecture Compliance
- [ ] **SRP**: Each hook has single responsibility (pre-commit: validation, pre-push: quality gates)
- [ ] **Portability**: Works on Windows PowerShell and Linux/macOS Bash environments
- [ ] **Defensibility**: Secure script execution, input validation for Git data

## Context & Constraints

**Prerequisites**: WP01 (Constitutional Core Engine) must be complete
**Dependencies**: Constitutional validation engine, SE rules configuration
**Platform Support**: Windows PowerShell 5.1+, Linux/macOS Bash
**Performance**: Real-time feedback (<5 seconds for typical commits)

## Subtasks & Detailed Guidance

### Subtask T011 – Create Pre-commit Hook for SE Principle Validation
**File**: `.git/hooks/pre-commit`

**Purpose**: Validate staged files against constitutional SE principles before commit

**Implementation Requirements**:
- Cross-platform script (PowerShell + Bash versions)
- Integration with constitutional validation engine from WP01
- Fast validation of only staged files (not entire repository)
- Clear violation reporting with specific line numbers
- Exit code 1 on violations to block commit

### Subtask T012 – Implement Pre-push Hook for Quality Gate Enforcement
**File**: `.git/hooks/pre-push`

**Purpose**: Enforce quality gates (coverage, complexity, security) before push

**Implementation Requirements**:
- Run full quality gate validation on push
- Integration with quality gate configuration from WP01
- Comprehensive reporting for all quality gate failures
- Block push on any quality gate failure

### Subtask T013 – Build Git Hook Installation Automation Script
**File**: `scripts/install_git_hooks.sh` (and `.ps1` version)

**Purpose**: Automated installation of constitutional Git hooks

**Implementation Requirements**:
- Cross-platform installation scripts
- Backup existing hooks if present
- Verify installation success
- Team-wide deployment capability

### Subtask T014 – Add Constitutional Violation Reporting to Git Workflows
**File**: `src/git_reporter.py`

**Purpose**: Generate Git-optimized violation reports

**Implementation Requirements**:
- Git-specific reporting format
- Integration with constitutional validation engine
- Clear, actionable violation messages
- Support for both pre-commit and pre-push contexts

## Definition of Done

- [ ] Pre-commit hooks block SE principle violations
- [ ] Pre-push hooks enforce all quality gates
- [ ] Cross-platform compatibility verified
- [ ] Automated installation works on Windows/Linux/macOS
- [ ] Performance: <5 seconds for pre-commit, <30 seconds for pre-push
- [ ] Clear violation reporting with remediation guidance
- [ ] Integration tests pass for full Git workflow