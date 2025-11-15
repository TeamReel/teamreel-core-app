---
work_package_id: "WP01"
subtasks:
  - "T001"
  - "T002"
  - "T003"
  - "T004"
  - "T005"
title: "Constitutional Core Engine"
phase: "Phase 1 - Foundation Setup"
lane: "for_review"
assignee: ""
agent: "copilot"
shell_pid: "29228"
review_status: ""
reviewed_by: ""
history:
  - timestamp: "2025-11-15T10:00:00Z"
    lane: "planned"
    agent: "system"
    shell_pid: ""
    action: "Prompt generated via /spec-kitty.tasks"
---

# Work Package Prompt: WP01 – Constitutional Core Engine

## ⚠️ IMPORTANT: Review Feedback Status

**Read this first if you are implementing this task!**

- **Has review feedback?**: Check the `review_status` field above. If it says `has_feedback`, scroll to the **Review Feedback** section immediately (right below this notice).
- **You must address all feedback** before your work is complete. Feedback items are your implementation TODO list.
- **Mark as acknowledged**: When you understand the feedback and begin addressing it, update `review_status: acknowledged` in the frontmatter.
- **Report progress**: As you address each feedback item, update the Activity Log explaining what you changed.

---

## Review Feedback

> **Populated by `/spec-kitty.review`** – Reviewers add detailed feedback here when work needs changes. Implementation must address every item listed below before returning for re-review.

*[This section is empty initially. Reviewers will populate it if the work is returned from review. If you see feedback here, treat each item as a must-do before completion.]*

---

## Objectives & Success Criteria

**Primary Goal**: Create the foundational constitutional validation engine that all other TeamReel SDD systems depend on.

**Success Criteria**:
- Constitutional validation engine can analyze code files and detect SE principle violations
- SE principles rule definitions are configurable via YAML
- Compliance reports are generated with actionable remediation guidance
- Quality gate configuration system is operational with 80% coverage, complexity <10 thresholds
- Violation detection logic accurately identifies violations across all 8 SE principles

**Independent Test**: Engine can validate a sample Python file with known violations and produce accurate compliance report with specific line numbers and suggested fixes.

## SE Principles Compliance *(mandatory)*

Ensure implementation follows all TeamReel SE Principles:

### Architecture Compliance
- [ ] **SRP**: Each component has single responsibility (validator, reporter, detector separate)
- [ ] **Encapsulation**: Internal validation logic hidden behind clean public APIs
- [ ] **Loose Coupling**: Components communicate via interfaces, not direct dependencies
- [ ] **Clean Architecture**: Core validation logic ← rules engine ← platform adapters

### Code Quality Standards  
- [ ] **Reusability**: Validation components reusable across spec-kitty, Git hooks, GitHub Actions
- [ ] **Portability**: Engine works consistently on Windows PowerShell and Linux/macOS environments
- [ ] **Defensibility**: Input validation for all code analysis, secure file handling
- [ ] **Maintainability**: Clear documentation, comprehensive unit tests, readable code structure
- [ ] **Simplicity**: Minimal dependencies, straightforward architecture, no over-engineering

### TeamReel Standards
- [ ] **Naming Conventions**: Python snake_case throughout (`constitutional_validator.py`, `compliance_reporter.py`)
- [ ] **Testing**: Minimum 80% coverage with pytest, test all 8 SE principle validations
- [ ] **Performance**: Validation completes within 30 seconds for typical feature files
- [ ] **Security**: No code execution, safe file parsing, input sanitization

## Context & Constraints

**Prerequisites**: 
- Constitution v1.1.0 available at `.kittify/memory/constitution.md`
- TeamReel SE principles fully documented (SRP, Encapsulation, Loose Coupling, Reusability, Portability, Defensibility, Maintainability, Simplicity)
- Plan document with distributed plugin architecture decisions

**Technical Constraints**:
- Python 3.11+ compatibility required
- No external service dependencies (offline capability)
- Cross-platform support (Windows PowerShell + Linux/macOS Bash)
- File-based configuration only (no database)

**Dependencies**: None - this is the foundation work package that enables all others

**Key Architectural Decisions**:
- Distributed Plugin Architecture: Core engine embedded in multiple tools
- Rule-based validation using YAML configuration files
- Modular design with separate components for validation, reporting, detection

## Subtasks & Detailed Guidance

### Subtask T001 – Create Constitutional Validation Engine
**File**: `src/constitutional_validator.py`

**Purpose**: Core engine that orchestrates SE principle validation across all code types

**Implementation Requirements**:
- Main `ConstitutionalValidator` class with public `validate()` method
- Support for Python, JavaScript/TypeScript, YAML/JSON file analysis
- Integration with SE rules engine (T002) for configurable validation
- Clear separation between file parsing, rule application, and result generation
- Error handling for malformed files, unsupported file types

**Key Methods**:
```python
class ConstitutionalValidator:
    def __init__(self, config_path: str = '.kittify/config/se_rules.yaml')
    def validate(self, file_path: str, validation_scope: List[str]) -> ComplianceReport
    def validate_batch(self, file_paths: List[str]) -> List[ComplianceReport]
    def get_supported_file_types(self) -> List[str]
```

**SE Principle Focus**: This component must exemplify SRP (single responsibility) and Encapsulation (clear interface)

### Subtask T002 – Implement SE Principles Rule Definitions
**File**: `.kittify/config/se_rules.yaml`

**Purpose**: Configurable rule definitions mapping each of the 8 SE principles to specific validation criteria

**Implementation Requirements**:
- YAML structure defining rules for each SE principle
- Configurable thresholds (complexity limits, naming patterns, etc.)
- Rule descriptions with violation examples and suggested fixes
- Support for file-type specific rules (Python vs TypeScript vs YAML)

**Rule Structure Example**:
```yaml
se_principles:
  SRP:
    description: "Single Responsibility Principle - each module has one clear purpose"
    rules:
      - rule_id: "SRP001"
        name: "function_complexity"
        threshold: 10
        file_types: ["py", "ts", "js"]
        violation_message: "Function exceeds complexity limit"
        suggested_fix: "Split complex function into smaller, focused functions"
  
  Encapsulation:
    description: "Internal details hidden behind clear interfaces"
    rules:
      - rule_id: "ENC001"
        name: "private_member_access"
        pattern: "direct access to private members"
        # ... additional rule details
```

**SE Principle Focus**: Reusability (rules reused across all validation contexts) and Maintainability (clear, updatable rule definitions)

### Subtask T003 – Build Constitutional Compliance Report Generator
**File**: `src/compliance_reporter.py`

**Purpose**: Generate structured compliance reports with actionable violation details and remediation guidance

**Implementation Requirements**:
- `ComplianceReport` data class with all required fields per data model
- Multiple output formats: JSON (for tools), human-readable text (for developers)
- Violation categorization by severity (ERROR, WARNING, INFO)
- Specific line number references and suggested fixes
- Summary statistics (total violations, compliance percentage, etc.)

**Key Classes**:
```python
@dataclass
class Violation:
    principle: str  # SRP, Encapsulation, etc.
    severity: str   # ERROR, WARNING, INFO
    message: str
    file_path: str
    line_number: Optional[int]
    suggested_fix: str
    rule_id: str

@dataclass 
class ComplianceReport:
    compliance_status: str  # PASS, FAIL, WARNING
    violations: List[Violation]
    quality_gates: Dict[str, bool]
    metadata: Dict[str, Any]
    
    def to_json(self) -> str
    def to_human_readable(self) -> str
    def get_summary_stats(self) -> Dict[str, int]
```

**SE Principle Focus**: Encapsulation (clean data structures) and Simplicity (clear, focused reporting)

### Subtask T004 – Create Quality Gate Configuration System
**File**: `.kittify/config/quality_gates.yaml`

**Purpose**: Configurable quality gate definitions with hard-blocking thresholds for coverage, complexity, security, naming

**Implementation Requirements**:
- YAML configuration defining all quality gate types and thresholds
- Coverage requirements: unit tests (80%), integration tests (60%), e2e tests (40%)
- Complexity limits: cyclomatic complexity (<10), cognitive complexity (<15)
- Security rules: no HIGH/CRITICAL vulnerabilities, no secrets in code
- Naming conventions: REST (kebab-case), Python (snake_case), Frontend (camelCase)

**Configuration Structure**:
```yaml
quality_gates:
  coverage:
    unit_test_threshold: 0.8
    integration_test_threshold: 0.6
    e2e_test_threshold: 0.4
    exclude_patterns: ["**/migrations/**", "**/tests/**"]
    
  complexity:
    cyclomatic_max: 10
    cognitive_max: 15
    function_length_max: 50
    class_length_max: 300
    
  security:
    vulnerability_scan: true
    dependency_audit: true
    secrets_scan: true
    allowed_levels: ["LOW", "MEDIUM"]
    
  naming_conventions:
    rest_api: "kebab-case"
    python_code: "snake_case"
    typescript_code: "camelCase"
    constants: "UPPER_SNAKE_CASE"
```

**SE Principle Focus**: Portability (consistent across environments) and Defensibility (secure defaults)

### Subtask T005 – Implement Constitutional Violation Detection Logic
**File**: `src/violation_detector.py`

**Purpose**: Core logic that analyzes code files and detects violations of specific SE principles

**Implementation Requirements**:
- File parsing for Python, JavaScript/TypeScript, YAML/JSON
- AST analysis for code structure violations (complexity, naming, etc.)
- Pattern matching for architectural violations (coupling, encapsulation)
- Integration with external tools (radon for complexity, bandit for security)
- Accurate line number detection and context extraction

**Key Detection Areas**:
1. **SRP Violations**: Functions/classes with multiple responsibilities
2. **Encapsulation Violations**: Direct access to private members, missing interfaces
3. **Coupling Violations**: Excessive imports, circular dependencies
4. **Reusability Violations**: Code duplication, hard-coded values
5. **Portability Violations**: Environment-specific code, absolute paths
6. **Defensibility Violations**: Missing input validation, insecure patterns
7. **Maintainability Violations**: Missing tests, inadequate documentation
8. **Simplicity Violations**: Over-engineering, unnecessary complexity

**Key Methods**:
```python
class ViolationDetector:
    def detect_srp_violations(self, file_content: str, file_type: str) -> List[Violation]
    def detect_encapsulation_violations(self, file_content: str) -> List[Violation]
    def detect_coupling_violations(self, file_path: str) -> List[Violation]
    def detect_complexity_violations(self, file_content: str) -> List[Violation]
    # ... methods for all 8 SE principles
```

**SE Principle Focus**: Maintainability (clear detection logic, well-tested) and Accuracy (precise violation identification)

## Testing Strategy

**Unit Tests** (pytest):
- Test each SE principle detection individually
- Test edge cases (empty files, malformed code, etc.)
- Test configuration loading and validation
- Test report generation formats

**Integration Tests**:
- Test full validation workflow with sample files
- Test configuration changes and rule updates
- Test performance with large file sets

**Test Files Structure**:
```
tests/
├── unit/
│   ├── test_constitutional_validator.py
│   ├── test_compliance_reporter.py
│   ├── test_violation_detector.py
│   └── test_quality_gates.py
├── integration/
│   └── test_full_validation_workflow.py
└── fixtures/
    ├── sample_code/
    └── expected_reports/
```

## Definition of Done

- [ ] All 5 subtasks completed and tested
- [ ] Constitutional validation engine can validate Python, JavaScript, YAML files
- [ ] SE rules configuration is complete for all 8 principles
- [ ] Compliance reports generated with accurate line numbers and fixes
- [ ] Quality gate configuration operational with all required thresholds
- [ ] Violation detection works for all SE principles with <5% false positives
- [ ] Unit test coverage ≥80% for all components
- [ ] Integration tests pass for full validation workflow
- [ ] Performance requirement met: <30 seconds for typical feature validation
- [ ] Documentation complete for all public APIs and configuration options

## Risks & Mitigation

**Risk**: AST parsing fails for complex code structures
**Mitigation**: Implement fallback to pattern-based detection, comprehensive test coverage

**Risk**: SE principle detection has high false positive rate
**Mitigation**: Extensive testing with real TeamReel codebase, tunable sensitivity thresholds

**Risk**: Performance requirements not met for large file sets
**Mitigation**: Implement parallel processing, file filtering, incremental validation

## Reviewer Guidance

When reviewing this work package:

1. **Functional Testing**: Use sample files with known violations to verify detection accuracy
2. **Configuration Validation**: Ensure SE rules and quality gates are properly configurable
3. **Integration Readiness**: Verify clean APIs that other work packages can integrate with
4. **Performance Testing**: Validate <30 second requirement with representative file sets
5. **Error Handling**: Test with malformed files, missing configurations, edge cases

**Key Review Questions**:
- Can the engine accurately detect all 8 SE principle violations?
- Are the generated reports actionable for developers?
- Is the configuration system flexible enough for team customization?
- Does the architecture support the distributed plugin approach?

## Activity Log

- 2025-11-15T20:59:17Z – copilot – shell_pid=29228 – lane=doing – Started implementation
- 2025-11-15T21:15:00Z – copilot – shell_pid=29228 – lane=doing – Completed all 5 subtasks: constitutional_validator.py, se_rules.yaml, compliance_reporter.py, quality_gates.yaml, violation_detector.py
- 2025-11-15T21:09:35Z – copilot – shell_pid=29228 – lane=for_review – Constitutional Core Engine complete - all 5 subtasks implemented
