# Context Engineering Program

The Itqahn Context Engineering Program defines how work is structured, validated, and executed to ensure reliable, parallelizable, and self-correcting builds.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT ENGINEERING WORKFLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│   │ INITIAL  │────▶│   PRP    │────▶│ EXECUTE  │────▶│ VALIDATE │          │
│   │ (intake) │     │(generate)│     │  (build) │     │  (gates) │          │
│   └──────────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘          │
│                         │                │                │                 │
│                         ▼                ▼                ▼                 │
│                    Plan artifact    Code + tests    Evidence Pack          │
│                    with examples    artifacts       with proofs            │
│                                                                             │
│   ◄─────────────────────────────────────────────────────────────────────►  │
│   If any gate fails: iterate until pass OR escalate                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Philosophy

### Why Context Engineering Exists

Context Engineering addresses the failure modes of unstructured AI-assisted development:

| Failure Mode | Symptom | Context Engineering Solution |
|--------------|---------|------------------------------|
| **Vibe Coding** | Implementing from vague prompts | PRP-first workflow with examples |
| **Context Rot** | Degraded output quality mid-session | Progressive disclosure + session boundaries |
| **Plan Drift** | Implementation diverges from spec | Validation gates + drift detection |
| **Integration Chaos** | Parallel work conflicts | Worktree isolation + merge protocols |
| **Silent Failures** | Issues discovered too late | Mandatory validation loops |
| **Scope Creep** | Unbounded work expansion | INITIAL constraints + PRP boundaries |
| **Evidence Gaps** | Missing audit trail | End-of-session verification ritual |

### Core Tenets

1. **Structured over Freeform**: Every unit of work has a spec (PRP) before execution
2. **Validate Early, Validate Often**: Gates run continuously, not just at the end
3. **Progressive Disclosure**: Load only what matters now; offload to files
4. **Iterate Until Pass**: Failures trigger correction, not abandonment
5. **Evidence as Artifact**: Every session produces verifiable records

---

## The PRP: Canonical Unit of Work

A **Product Requirements Prompt (PRP)** is the specification that defines a single unit of work. No implementation begins without an approved PRP.

### PRP Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         PRP LIFECYCLE                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. INITIAL       2. /generate-prp    3. REVIEW       4. /execute-prp    │
│  ┌─────────┐      ┌─────────────┐     ┌─────────┐     ┌─────────────┐   │
│  │ Feature │─────▶│ Draft PRP   │────▶│ Refine  │────▶│ Execute     │   │
│  │ Request │      │ + Examples  │     │ Iterate │     │ with Gates  │   │
│  └─────────┘      └─────────────┘     └────┬────┘     └──────┬──────┘   │
│                                            │                  │          │
│                                            ▼                  ▼          │
│                                       PRP v1.0          Evidence Pack    │
│                                       (approved)        (validated)      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### PRP Required Sections

Every PRP MUST include:

```yaml
prp:
  id: prp-{ulid}
  version: "1.0.0"
  status: draft | approved | in-progress | completed | abandoned

  # --- CONTEXT ---
  context:
    concept_lock_ref: "concept-lock/project-slug/v1.0.0"
    parent_issue: "#123"
    run_id: "run-{ulid}"

  # --- REQUIREMENTS ---
  requirements:
    description: "Clear, unambiguous description of what to build"
    acceptance_criteria:
      - criterion: "User can submit form with valid data"
        verification: "E2E test passes"
      - criterion: "Form validates email format"
        verification: "Unit test passes"

  # --- EXAMPLES ---
  examples:
    inputs:
      - description: "Valid form submission"
        data: { name: "John", email: "john@example.com" }
        expected_output: "Success message displayed"
      - description: "Invalid email"
        data: { name: "John", email: "invalid" }
        expected_output: "Email validation error shown"
    golden_cases:
      - file: "tests/fixtures/form-valid.json"
      - file: "tests/fixtures/form-invalid.json"

  # --- IMPLEMENTATION PLAN ---
  implementation:
    files_to_change:
      - path: "src/components/Form.tsx"
        action: create
        reason: "New form component"
      - path: "src/api/submit.ts"
        action: modify
        reason: "Add form handler"
    steps:
      - step: 1
        description: "Create form component with validation"
        validation: "npm run lint && npm run typecheck"
      - step: 2
        description: "Add API endpoint"
        validation: "npm test -- --grep 'form API'"

  # --- VALIDATION GATES ---
  validation_gates:
    required:
      - gate: lint
        command: "npm run lint"
        blocking: true
      - gate: typecheck
        command: "npm run typecheck"
        blocking: true
      - gate: unit_tests
        command: "npm test"
        blocking: true
      - gate: security_scan
        command: "npm run security:scan"
        blocking: true
    optional:
      - gate: e2e_tests
        command: "npm run test:e2e"
        blocking: false

  # --- EDGE CASES ---
  edge_cases:
    - case: "Network timeout during submit"
      handling: "Show retry button, preserve form state"
    - case: "Session expires mid-submission"
      handling: "Redirect to login, preserve draft"

  # --- ROLLBACK ---
  rollback:
    trigger: "Any validation gate fails after 3 attempts"
    procedure: |
      1. Revert uncommitted changes
      2. Document failure in decision log
      3. Escalate to dashboard
    preserves: ["memory/decision-log.md", "evidence/"]

  # --- DEFINITION OF DONE ---
  definition_of_done:
    - "All validation gates pass"
    - "PR created and linked to issue"
    - "Evidence Pack generated"
    - "Session end verification complete"
```

### PRP vs Other Artifacts

| Artifact | Purpose | When Created | Owned By |
|----------|---------|--------------|----------|
| **INITIAL** | Feature request intake | User submits request | User/Dashboard |
| **PRP** | Implementation specification | Before any code | Agent (approved by user) |
| **Plan artifact** | Detailed step-by-step approach | During PRP generation | Agent |
| **Evidence Pack** | Proof of correct execution | After validation passes | System |

---

## Intake-to-Build Workflow

### Phase 1: INITIAL (Feature Request)

The INITIAL document captures the feature request in structured form:

```markdown
# INITIAL: {Feature Name}

## FEATURE
What user-visible capability is being added?

## EXAMPLES
Concrete examples of expected behavior:
- Given X, when Y, then Z
- Input: {...}, Output: {...}

## DOCUMENTATION
What docs need updating after implementation?

## CONSTRAINTS
- Performance: Response time < 200ms
- Security: No PII in logs
- Compatibility: Must work in Safari 15+

## ACCEPTANCE
How do we know this is done?
- [ ] Criterion 1
- [ ] Criterion 2

## GOTCHAS
Known edge cases or risks:
- Watch for: X
- Known issue: Y
```

### Phase 2: PRP Generation (`/generate-prp`)

Dashboard triggers PRP generation from INITIAL:

```
Dashboard → "Generate PRP" button → Agent receives INITIAL
                                          ↓
                                   Agent produces PRP draft
                                          ↓
                                   User reviews in dashboard
                                          ↓
                              ┌─── Approved ───┐
                              │                │
                              ▼                ▼
                    Ready for execute    Needs revision
                                              ↓
                                        Agent refines
                                              ↓
                                        (loop until approved)
```

**Minimum PRP Refinement Cycles**: 2 iterations unless trivially complete.

### Phase 3: PRP Execution (`/execute-prp`)

Execution follows the PRP step-by-step with continuous validation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    PRP EXECUTION LOOP                                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   For each step in PRP.implementation.steps:                           │
│                                                                         │
│   1. EXECUTE step                                                       │
│          ↓                                                              │
│   2. RUN step.validation                                               │
│          ↓                                                              │
│   3. CHECK result                                                       │
│          │                                                              │
│          ├── PASS → Continue to next step                              │
│          │                                                              │
│          └── FAIL → Iterate                                            │
│                  │                                                      │
│                  ├── Attempt 1: Analyze error, fix, re-run             │
│                  ├── Attempt 2: Adjust approach, re-run                │
│                  ├── Attempt 3: Narrow scope, re-run                   │
│                  └── Attempt 4+: Escalate to dashboard                 │
│                                                                         │
│   After all steps:                                                      │
│   4. RUN all PRP.validation_gates                                      │
│   5. GENERATE Evidence Pack                                            │
│   6. RUN session end verification                                      │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Validation Gates

Every PRP execution MUST pass all required validation gates:

| Gate Category | Examples | Blocking |
|---------------|----------|----------|
| **Format/Schema** | JSON schema validation, YAML lint | Yes |
| **Code Quality** | ESLint, Prettier, TypeScript | Yes |
| **Tests** | Unit, integration, E2E | Yes |
| **Security** | SAST, secret scan, dependency audit | Yes |
| **Drift Detection** | PRD alignment, UI consistency | Threshold-based |
| **Documentation** | API docs current, README updated | Configurable |

**Iterate Until Pass Rule**:
- Gates run after each significant change
- Failures trigger automatic correction attempt
- Max 3 auto-correction attempts per gate
- After max attempts: escalate to dashboard with context

---

## Progressive Disclosure

### The 70% Context Budget Rule

Claude Code sessions MUST stay below 70% context utilization:

| Level | Threshold | Action |
|-------|-----------|--------|
| Green | < 40% | Normal operation |
| Yellow | 40-60% | Summarize verbose outputs |
| Orange | 60-70% | Offload to memory files |
| Red | 70%+ | **HARD STOP**: Context Reset required |

### What Goes Where

| Information Type | Location | Loaded When |
|------------------|----------|-------------|
| **Always-on rules** | `CLAUDE.md` (< 200 lines) | Every session |
| **Current task context** | PRP artifact | Active execution |
| **Decisions made** | `memory/decision-log.md` | On demand |
| **Project structure** | `memory/project-index.md` | On demand |
| **Standards/patterns** | `memory/standards.md` | On demand |
| **Historical context** | Evidence Packs | Never (archived) |

### Context Hygiene Practices

```yaml
# What to load in context
load:
  - CLAUDE.md                    # Always-on rules
  - Current PRP                  # Active work specification
  - Relevant source files        # Files being modified

# What to write to files (not keep in context)
offload:
  - Decision rationales          # → memory/decision-log.md
  - Exploration results          # → memory/research/{topic}.md
  - Long outputs                 # → artifacts/{name}
  - Test results                 # → evidence/{type}.json

# What to never load
avoid:
  - Full codebases               # Use targeted file reads
  - Complete documentation       # Use search/grep
  - Historical conversations     # Use catch-up packs
```

### Handling Long Tasks: Session Boundaries

When tasks exceed session capacity:

```
Task too large for single session
           ↓
1. CHECKPOINT current state
   - Update memory/current-status.md
   - Commit completed work
   - Generate catch-up pack
           ↓
2. SPLIT remaining work into sub-PRPs
   - Each sub-PRP is self-contained
   - Clear dependencies documented
           ↓
3. END current session
   - Session end verification
   - Evidence Pack for completed portion
           ↓
4. NEW SESSION continues
   - Load catch-up pack
   - Execute next sub-PRP
```

---

## Validation Gates Program

### Gate Categories

```yaml
validation_gates:
  # Category 1: Format & Schema
  format:
    - name: json_schema
      check: "Validate all JSON against schemas"
      tool: ajv-cli
      blocking: true

    - name: yaml_lint
      check: "YAML syntax and structure"
      tool: yamllint
      blocking: true

    - name: markdown_lint
      check: "Documentation format"
      tool: markdownlint
      blocking: false

  # Category 2: Code Quality
  quality:
    - name: lint
      check: "Code style and patterns"
      tool: eslint
      blocking: true

    - name: typecheck
      check: "Type safety"
      tool: tsc --noEmit
      blocking: true

    - name: format
      check: "Code formatting"
      tool: prettier --check
      blocking: true

  # Category 3: Tests
  tests:
    - name: unit
      check: "Unit test suite"
      tool: vitest run
      blocking: true
      coverage_threshold: 80%

    - name: integration
      check: "Integration tests"
      tool: vitest run --config vitest.integration.config.ts
      blocking: true

    - name: e2e
      check: "End-to-end tests"
      tool: playwright test
      blocking: configurable

  # Category 4: Security
  security:
    - name: sast
      check: "Static analysis"
      tool: semgrep
      blocking: true

    - name: secrets
      check: "Secret detection"
      tool: gitleaks
      blocking: true

    - name: dependencies
      check: "Dependency vulnerabilities"
      tool: npm audit
      blocking: severity >= high

  # Category 5: Drift Detection
  drift:
    - name: plan_alignment
      check: "Implementation matches PRP"
      tool: drift-checker
      blocking: drift_score > 0.50

    - name: design_os
      check: "UI follows Design OS"
      tool: design-os-lint
      blocking: true

  # Category 6: Documentation
  docs:
    - name: api_docs
      check: "API documentation current"
      tool: typedoc --validation
      blocking: false

    - name: readme
      check: "README reflects changes"
      tool: readme-validator
      blocking: false
```

### Gate Execution Protocol

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GATE EXECUTION PROTOCOL                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   For each gate in validation_gates:                                    │
│                                                                          │
│   RUN gate.tool                                                         │
│       │                                                                  │
│       ├── PASS ──────────────────────────────────────────▶ Next gate   │
│       │                                                                  │
│       └── FAIL                                                          │
│              │                                                           │
│              ▼                                                           │
│       Is gate.blocking?                                                  │
│              │                                                           │
│       ├── NO ────▶ Log warning, continue                               │
│       │                                                                  │
│       └── YES                                                           │
│              │                                                           │
│              ▼                                                           │
│       ITERATE (max 3 attempts)                                          │
│              │                                                           │
│       ├── Attempt 1: Analyze, fix specific error                        │
│       ├── Attempt 2: Broaden fix, check related issues                 │
│       ├── Attempt 3: Simplify approach, minimal fix                    │
│              │                                                           │
│       └── All attempts fail?                                            │
│              │                                                           │
│              ▼                                                           │
│       ESCALATE to dashboard                                             │
│       - Document what was tried                                         │
│       - Propose alternative approaches                                  │
│       - Request human decision                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Repeated Gate Failures: Escalation Protocol

When validation gates fail repeatedly:

| Failure Count | Action |
|---------------|--------|
| 1 | Analyze error, apply targeted fix |
| 2 | Review approach, consider alternatives |
| 3 | Narrow scope, attempt minimal viable fix |
| 4+ | **ESCALATE**: Pause work, notify dashboard |

**Escalation includes**:
- Summary of all attempts
- Error messages and logs
- Proposed alternatives
- Rollback option

**Dashboard options**:
- Approve alternative approach
- Provide additional context
- Rollback to last good state
- Terminate PRP

---

## Session Rituals

### Start-of-Task Ritual

Every task begins with:

```yaml
start_ritual:
  steps:
    - name: load_context
      actions:
        - Read CLAUDE.md
        - Read memory/current-status.md
        - Load assigned PRP

    - name: verify_prerequisites
      checks:
        - PRP status is "approved"
        - Worktree is clean
        - Branch is up-to-date
        - Required tools available

    - name: clarify_if_needed
      trigger: "Any ambiguity in PRP"
      action: "Ask clarifying questions via dashboard"

    - name: confirm_plan
      output: |
        ## Task Start Confirmation
        - PRP: {prp-id}
        - Branch: {branch-name}
        - First step: {step-1-description}
        - Ready to begin
```

### End-of-Task Ritual (Verification Prompt)

Every session MUST end with verification. **No exceptions**.

```yaml
end_ritual:
  command: /end

  steps:
    - name: validation_pass
      required: true
      actions:
        - Run: npm run lint
        - Run: npm run typecheck
        - Run: npm test
        - Run: npm run security:scan
      on_failure: "Iterate until pass or escalate"

    - name: security_hygiene
      required: true
      checks:
        - No secrets in code
        - No credentials in logs
        - No sensitive data exposed
        - Auth/authz properly implemented (if applicable)

    - name: docs_sync
      required: true
      checks:
        - API documentation current
        - README reflects changes
        - Memory files updated
        - Decision log has new decisions

    - name: plan_alignment
      required: true
      checks:
        - Implementation matches PRP
        - All acceptance criteria met
        - No unplanned changes
        - Drift score < threshold

    - name: summary
      required: true
      output: |
        ## Session Summary

        ### Completed
        - {list of completed items}

        ### Changes Made
        - Files: {list of files changed}
        - Tests: {tests added/modified}
        - Docs: {docs updated}

        ### Decisions Made
        - {key decisions with rationale}

        ### Next Steps
        - {what needs to happen next}
        - {any blockers or risks}

    - name: evidence_pack
      required: true
      actions:
        - Generate evidence pack
        - Commit all changes
        - Create/update PR
        - Update memory files
```

### Verification Checklist Template

```markdown
# Session End Verification

**Task**: {task-name}
**PRP**: {prp-id}
**Run ID**: {run-id}
**Timestamp**: {ISO-8601}

## 1. Validation Gates

- [ ] `npm run lint` passes (errors: 0)
- [ ] `npm run typecheck` passes (errors: 0)
- [ ] `npm test` passes (coverage: X%)
- [ ] `npm run security:scan` passes (critical: 0, high: 0)

## 2. Security Hygiene

- [ ] No secrets in code
- [ ] No credentials in logs
- [ ] No sensitive data exposed
- [ ] Auth/authz correct (if applicable)

## 3. Documentation Sync

- [ ] API docs current
- [ ] README reflects changes
- [ ] `memory/current-status.md` updated
- [ ] `memory/decision-log.md` has new decisions

## 4. Plan Alignment

- [ ] Implementation matches PRP
- [ ] All acceptance criteria met
- [ ] No unplanned files changed
- [ ] Drift score: {X.XX} (< 0.30 = good)

## 5. Evidence Pack

- [ ] Evidence artifacts generated
- [ ] All changes committed
- [ ] PR created/updated
- [ ] Issue linked

## Summary

| Category | Status | Notes |
|----------|--------|-------|
| Validation | Pass/Fail | |
| Security | Pass/Fail | |
| Docs | Pass/Fail | |
| Alignment | Pass/Fail | |
| Evidence | Pass/Fail | |

**Overall**: PASS / FAIL
**Ready for merge**: Yes / No
```

---

## Sub-Agents and Parallelism

### When to Use Sub-Agents

| Scenario | Use Sub-Agent? | Rationale |
|----------|----------------|-----------|
| **Long research/exploration** | Yes | Keeps main context clean |
| **Independent subtask** | Yes | Parallel execution |
| **File-heavy read operations** | Yes | Avoids context bloat |
| **Quick lookup** | No | Overhead not worth it |
| **State-dependent work** | No | Needs main context |

### Sub-Agent Protocol

```yaml
sub_agent:
  spawn_conditions:
    - Task is independent from main work
    - Will return discrete result
    - Does not need ongoing state from main

  handoff:
    provide:
      - Clear task description
      - Relevant file references
      - Expected output format
    do_not_provide:
      - Full conversation history
      - Unrelated context
      - Main session state

  merge_back:
    - Sub-agent returns structured result
    - Main agent incorporates result
    - Result is summarized, not dumped
    - Original sub-agent context discarded
```

### Parallel Execution Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Coordinator                                                            │
│       │                                                                  │
│       ├──▶ Worktree 1 (Branch: task/auth)                               │
│       │        └── PRP: Authentication feature                          │
│       │                                                                  │
│       ├──▶ Worktree 2 (Branch: task/dashboard)                          │
│       │        └── PRP: Dashboard UI                                     │
│       │                                                                  │
│       ├──▶ Worktree 3 (Branch: task/api)                                │
│       │        └── PRP: API endpoints                                   │
│       │                                                                  │
│       ├──▶ Worktree 4 (Branch: task/tests)                              │
│       │        └── PRP: Test coverage                                   │
│       │                                                                  │
│       └──▶ Worktree 5 (Merge Captain, Branch: integration-{run_id})    │
│                └── Merges validated work                                 │
│                                                                          │
│   Rules:                                                                 │
│   - One PRP per worktree                                                │
│   - No file ownership overlap                                           │
│   - Merge Captain handles shared files                                  │
│   - All gates must pass before integration                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

See `docs/07-integrations/git-integration.md` for detailed parallelism protocols.

---

## Format and Token Efficiency

### Format Selection Rules

| Use Case | Format | Rationale |
|----------|--------|-----------|
| **Configuration** | YAML | Human-readable, comments allowed |
| **Data interchange** | JSON | Strict, machine-parseable |
| **Documentation** | Markdown | Readable, renderable |
| **Schemas** | JSON Schema | Validation support |
| **Evidence artifacts** | JSON | Structured, queryable |
| **Memory files** | Markdown | Quick human review |

### Token Efficiency Practices

```yaml
efficiency_rules:
  # Prefer structured over verbose
  - rule: "Use tables over prose for lists > 3 items"
    example: "| Col1 | Col2 | instead of bullet points"

  # Avoid redundancy
  - rule: "Reference files instead of duplicating"
    example: "See `memory/standards.md` instead of repeating"

  # Summarize, don't dump
  - rule: "Summarize long outputs"
    example: "Tests passed: 47/47 (details in test-results.json)"

  # Targeted reads
  - rule: "Read specific file sections, not entire files"
    example: "Read lines 50-100 instead of whole file"

  # Progressive loading
  - rule: "Load context on demand"
    example: "Load function only when modifying it"
```

---

## Dashboard Mapping

### Dashboard Actions and PRP Workflow

| Dashboard Action | System Behavior | Agent Receives |
|------------------|-----------------|----------------|
| **"New Feature"** | Creates INITIAL template | Notification |
| **"Generate PRP"** | Triggers `/generate-prp` | INITIAL document |
| **"Approve PRP"** | Sets PRP status to approved | Updated PRP |
| **"Execute PRP"** | Triggers `/execute-prp` | Approved PRP |
| **"Validate"** | Runs all validation gates | Gate commands |
| **"Merge"** | Triggers merge via Merge Captain | Merge approval |
| **"Rollback"** | Reverts to checkpoint | Rollback instruction |

### User Dashboard Views

```yaml
dashboard_views:

  # Main progress view
  prp_status:
    shows:
      - PRP ID and title
      - Current status (draft/approved/in-progress/completed)
      - Current step (if in-progress)
      - Validation gate results
      - Drift score
      - Time elapsed

  # Validation detail view
  validation_view:
    shows:
      - Gate-by-gate status
      - Error messages (if failed)
      - Retry count
      - Suggested fixes (if available)

  # Failure/escalation view
  escalation_view:
    shows:
      - What failed and why
      - What was tried
      - Proposed alternatives
      - User options:
        - Approve alternative
        - Provide guidance
        - Rollback
        - Terminate

  # Parallel execution view
  parallel_view:
    shows:
      - All active worktrees
      - Per-worktree status
      - File ownership map
      - Merge queue status
      - Conflict indicators
```

### Dashboard-Agent Communication

```yaml
communication:
  # Dashboard → Agent
  dashboard_to_agent:
    - type: command
      examples: ["/generate-prp", "/execute-prp", "/validate"]

    - type: approval
      examples: ["PRP approved", "Merge approved"]

    - type: feedback
      examples: ["Revise section X", "Add example for Y"]

    - type: decision
      examples: ["Use approach A", "Rollback to checkpoint"]

  # Agent → Dashboard
  agent_to_dashboard:
    - type: status_update
      examples: ["Step 2/5 complete", "Running tests"]

    - type: escalation
      examples: ["Gate failed after 3 attempts", "Needs clarification"]

    - type: result
      examples: ["PRP draft ready", "Validation passed"]

    - type: artifact
      examples: ["Evidence Pack generated", "PR created"]
```

---

## MCP Usage Discipline

### Skill-First Policy

**Skills** (internal procedures) are preferred over **MCPs** (external tool calls):

| Category | Use Skill | Use MCP |
|----------|-----------|---------|
| Code generation | ✓ | |
| Local file operations | ✓ | |
| Running local tests | ✓ | |
| Git operations (local) | ✓ | |
| GitHub API calls | | ✓ |
| External API access | | ✓ |
| Figma extraction | | ✓ |
| Jira sync | | ✓ |

### MCP Call Protocol

```yaml
mcp_protocol:
  before_calling:
    - Verify MCP is on allowlist
    - Confirm operation is necessary
    - Check if skill can accomplish same

  during_call:
    - Use minimal parameters
    - Request only needed fields
    - Avoid broad queries

  after_call:
    - Extract relevant data
    - Discard unused response
    - Summarize for context
```

### Avoiding MCP Bloat

```yaml
anti_patterns:
  - name: "Broad GitHub query"
    bad: "Fetch all repository issues"
    good: "Fetch issue #123 details only"

  - name: "Repeated tool calls"
    bad: "Check file status after every edit"
    good: "Batch status check at end"

  - name: "Full object retrieval"
    bad: "Get complete Figma file"
    good: "Get specific component by ID"
```

---

## Error Handling and Recovery

### Validation Gate Failure Recovery

See `docs/06-operations/runbooks.md` → "Validation Gate Failure Runbook".

### Context Drift Recovery

See `docs/06-operations/runbooks.md` → "Context Drift / Plan Drift Runbook".

### Escalation Matrix

| Issue Type | First Responder | Escalation Path |
|------------|-----------------|-----------------|
| Validation gate failure | Agent (auto-fix) | Dashboard → User |
| Plan drift detected | Agent (realign) | Dashboard → User |
| Context budget exceeded | Agent (reset) | Dashboard → User |
| Parallel conflict | Merge Captain | Dashboard → User |
| Security finding | Block (no auto) | Security team |

---

## Integration with Existing Systems

### Relationship to Other Itqahn Components

| Component | Context Engineering Integration |
|-----------|--------------------------------|
| **Concept Lock** | PRP references Concept Lock version |
| **Evidence Pack** | PRP execution produces Evidence Pack |
| **Track Assurance** | Drift detection runs during PRP execution |
| **Design OS** | Design gates validate during execution |
| **Git Automation** | PRP lifecycle tied to Git workflow |

### Cross-References

- `docs/00-overview/glossary.md` — Term definitions
- `docs/00-overview/principles.md` — Core principles
- `docs/03-platform/track-assurance.md` — Drift detection
- `docs/06-operations/runbooks.md` — Failure runbooks
- `docs/07-integrations/git-integration.md` — Git workflow
- `docs/08-agents/agent-quality-bar.md` — Agent standards
- `templates/product/INITIAL.md` — Feature request template
- `templates/product/PRP.md` — PRP template
- `templates/operations/session-end-verification.md` — End verification checklist

---

**Version**: 1.0.0 | **Date**: 2026-01-08
