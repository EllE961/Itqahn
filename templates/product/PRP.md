# PRP: Product Requirements Prompt Template

Use this template for generating and executing PRPs (the canonical unit of work).

---

```yaml
# PRP: {Title}

prp:
  id: "prp-{ulid}"
  version: "1.0.0"
  status: draft | approved | in-progress | completed | abandoned

  # ─────────────────────────────────────────────────────────────────
  # CONTEXT
  # ─────────────────────────────────────────────────────────────────
  context:
    initial_ref: "initial-{ulid}"           # Source INITIAL document
    concept_lock_ref: "v1.0.0"              # Concept Lock version
    parent_issue: "#123"                     # GitHub issue number
    run_id: "run-{ulid}"                     # Operator Mode run ID
    created_at: "{ISO-8601}"
    approved_at: null                        # Set when approved
    approved_by: null

  # ─────────────────────────────────────────────────────────────────
  # REQUIREMENTS
  # ─────────────────────────────────────────────────────────────────
  requirements:
    description: |
      {Clear, unambiguous description of what to build.
      1-3 sentences. Focus on WHAT, not HOW.}

    acceptance_criteria:
      - criterion: "{Specific, testable criterion 1}"
        verification: "{How to verify: test name, command, or manual check}"

      - criterion: "{Specific, testable criterion 2}"
        verification: "{How to verify}"

      - criterion: "{Specific, testable criterion 3}"
        verification: "{How to verify}"

    out_of_scope:
      - "{Explicitly what is NOT included}"
      - "{Another thing NOT included}"

  # ─────────────────────────────────────────────────────────────────
  # EXAMPLES (Required - from INITIAL)
  # ─────────────────────────────────────────────────────────────────
  examples:
    inputs:
      - description: "{Example 1: Happy path}"
        data:
          field1: "value1"
          field2: "value2"
        expected_output: "{Expected result}"

      - description: "{Example 2: Edge case or error}"
        data:
          field1: "invalid"
        expected_output: "{Expected error or behavior}"

    golden_cases:
      - file: "tests/fixtures/{feature}-valid.json"
        description: "Valid input fixture"

      - file: "tests/fixtures/{feature}-invalid.json"
        description: "Invalid input fixture"

  # ─────────────────────────────────────────────────────────────────
  # IMPLEMENTATION PLAN
  # ─────────────────────────────────────────────────────────────────
  implementation:
    approach: |
      {Brief description of implementation approach.
      Key decisions, patterns to use.}

    files_to_change:
      - path: "src/{path}/file.ts"
        action: create | modify | delete
        reason: "{Why this file}"

      - path: "src/{path}/other.ts"
        action: modify
        reason: "{Why this file}"

      - path: "tests/{path}/file.test.ts"
        action: create
        reason: "Tests for new functionality"

    steps:
      - step: 1
        description: "{What to do in step 1}"
        validation: "{Command to validate step: npm run lint, npm test, etc.}"
        files: ["src/file1.ts"]

      - step: 2
        description: "{What to do in step 2}"
        validation: "{Command to validate}"
        files: ["src/file2.ts"]

      - step: 3
        description: "{What to do in step 3}"
        validation: "{Command to validate}"
        files: ["tests/file.test.ts"]

  # ─────────────────────────────────────────────────────────────────
  # VALIDATION GATES
  # ─────────────────────────────────────────────────────────────────
  validation_gates:
    required:
      - gate: lint
        command: "npm run lint"
        blocking: true
        timeout_seconds: 120

      - gate: typecheck
        command: "npm run typecheck"
        blocking: true
        timeout_seconds: 120

      - gate: unit_tests
        command: "npm test"
        blocking: true
        timeout_seconds: 300
        coverage_threshold: 80

      - gate: security_scan
        command: "npm run security:scan"
        blocking: true
        timeout_seconds: 180

    optional:
      - gate: e2e_tests
        command: "npm run test:e2e"
        blocking: false
        timeout_seconds: 600

      - gate: docs_check
        command: "npm run docs:check"
        blocking: false

  # ─────────────────────────────────────────────────────────────────
  # EDGE CASES
  # ─────────────────────────────────────────────────────────────────
  edge_cases:
    - case: "{Edge case 1}"
      handling: "{How to handle}"
      test: "{Test that covers this}"

    - case: "{Edge case 2}"
      handling: "{How to handle}"
      test: "{Test that covers this}"

  # ─────────────────────────────────────────────────────────────────
  # ROLLBACK
  # ─────────────────────────────────────────────────────────────────
  rollback:
    trigger: "Any required validation gate fails after 3 attempts"

    procedure: |
      1. Commit all valid completed work
      2. Revert uncommitted failing changes
      3. Document failure in memory/decision-log.md
      4. Create rollback evidence artifact
      5. Escalate to dashboard with context

    preserves:
      - "memory/decision-log.md"
      - "evidence/"
      - "completed steps' commits"

  # ─────────────────────────────────────────────────────────────────
  # DEFINITION OF DONE
  # ─────────────────────────────────────────────────────────────────
  definition_of_done:
    - "All acceptance criteria verified"
    - "All required validation gates pass"
    - "All examples produce expected outputs"
    - "No unplanned files modified"
    - "PR created and linked to issue"
    - "Evidence Pack generated"
    - "Documentation updated (if applicable)"
    - "Session end verification complete"

# ─────────────────────────────────────────────────────────────────
# EXECUTION LOG (Filled during execution)
# ─────────────────────────────────────────────────────────────────
execution:
  started_at: null
  completed_at: null
  current_step: null

  step_results:
    # Populated as steps complete
    # - step: 1
    #   status: completed
    #   validation_passed: true
    #   notes: ""

  gate_results:
    # Populated as gates run
    # - gate: lint
    #   status: passed
    #   attempts: 1
    #   output: ""

  drift_score: null
  evidence_pack_ref: null
  pr_number: null
  branch: null
```

---

## PRP Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PRP LIFECYCLE                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  INITIAL submitted                                                    │
│       │                                                               │
│       ▼                                                               │
│  /generate-prp                                                        │
│       │                                                               │
│       ▼                                                               │
│  PRP draft created (status: draft)                                   │
│       │                                                               │
│       ├──▶ User reviews in dashboard                                 │
│       │                                                               │
│       ├── Approved ──▶ status: approved                              │
│       │                      │                                        │
│       └── Needs revision ──▶ Agent refines ──▶ (loop)               │
│                                                                       │
│  /execute-prp (status: in-progress)                                  │
│       │                                                               │
│       ▼                                                               │
│  For each step:                                                       │
│       Execute step → Run validation → Pass? Continue : Iterate       │
│       │                                                               │
│       ▼                                                               │
│  All steps complete                                                   │
│       │                                                               │
│       ▼                                                               │
│  Run all validation gates                                            │
│       │                                                               │
│       ▼                                                               │
│  All gates pass                                                       │
│       │                                                               │
│       ▼                                                               │
│  Session end verification                                            │
│       │                                                               │
│       ▼                                                               │
│  Evidence Pack generated (status: completed)                         │
│       │                                                               │
│       ▼                                                               │
│  PR created/merged                                                   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Required Sections

Every PRP MUST include:

| Section | Required | Purpose |
|---------|----------|---------|
| **context** | Yes | Links to source, locks, and tracking |
| **requirements** | Yes | What to build and how to verify |
| **examples** | Yes | Concrete input/output pairs |
| **implementation** | Yes | Files and steps |
| **validation_gates** | Yes | What must pass |
| **edge_cases** | Yes | Known special cases |
| **rollback** | Yes | What to do on failure |
| **definition_of_done** | Yes | When is this complete |

---

## Validation Rules

PRP must pass these checks before approval:

| Check | Requirement |
|-------|-------------|
| **Examples** | At least 2 examples with input/output |
| **Acceptance criteria** | At least 3 binary, testable criteria |
| **Files** | All files listed with action and reason |
| **Gates** | At least lint, typecheck, tests, security |
| **Rollback** | Procedure documented |
| **No ambiguity** | No vague terms like "fast", "better", "nice" |

---

## PRP Versioning

PRPs may be updated during execution:

| Version | When | Approval |
|---------|------|----------|
| 1.0.0 | Initial approval | User approval |
| 1.1.0 | Scope clarification (additive) | Auto-approve |
| 1.2.0 | Approach change | User review |
| 2.0.0 | Scope change (breaking) | User approval |

---

**Template Version**: 1.0.0
