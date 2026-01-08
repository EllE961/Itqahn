# Agent System Contract

This contract defines the mandatory rules that all Itqahn agents must follow. It prevents "vibe-coded autonomy" and ensures predictable, auditable behavior.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT CONTRACT PILLARS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   ARTIFACT   │  │    ROLE      │  │    STOP      │          │
│  │    FIRST     │  │  BOUNDARIES  │  │  CONDITIONS  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  Every action      Least privilege    Mandatory                 │
│  produces          enforcement        escalation                │
│  evidence                                                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ DETERMINISM  │  │  PROVENANCE  │  │   SECURITY   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  Prefer schemas    Full audit trail   Never weaken             │
│  and templates     for compliance     defenses                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Contract Rules

### 1. Artifact-First Outputs

**No chat-only work.** Every agent invocation must produce at least one:

| Artifact Type | Examples |
|---------------|----------|
| **Decision** | ADR, policy verdict, risk tier, approval/denial with reasoning |
| **Spec** | PRD, NFRs, API contract, test plan, threat model |
| **Change** | Code in PR, migration file, runbook update, docs update |
| **Evidence** | Scan outputs, SBOM, provenance, release authorization |

```yaml
# Every agent output must include
output:
  artifacts:
    - type: decision | spec | change | evidence
      path: <location>
      hash: <sha256>

  # If no artifact produced
  status: failed
  reason: "No artifact produced"
```

**If no artifact is produced, the work is considered FAILED.**

---

### 2. Role Boundaries (Least Privilege)

Agents must not exceed their role:

| Role Category | CAN | CANNOT |
|---------------|-----|--------|
| **Design** | Write to design system paths | Touch production infra |
| **Builders** | Write code PRs | Bypass policy gates |
| **Security** | Block merges/releases | Silently override governance |
| **FinOps** | Pause workflows | Change product scope |
| **SRE** | Execute approved runbooks | Deploy without evidence |
| **Compliance** | Sign evidence manifests | Modify security policies |

```python
def check_role_boundary(agent: Agent, action: Action) -> bool:
    # Get agent's allowed actions
    allowed = get_allowed_actions(agent.role)

    # Check if action is within boundaries
    if action not in allowed:
        raise RoleBoundaryViolation(
            agent=agent.id,
            action=action,
            allowed=allowed
        )

    return True
```

---

### 3. Stop Conditions (Mandatory)

Agents must stop and escalate when:

| Condition | Action |
|-----------|--------|
| Policy denies action | Stop, report denial |
| Cannot verify required fact | Stop, request verification |
| Retries exceed cap | Stop, escalate |
| Budget reaches threshold | Pause, request extension |
| Human approval required | Stop, create approval request |
| Uncertainty too high | Stop, escalate to human |

```yaml
stop_conditions:
  policy_denial:
    action: stop
    escalate_to: workflow_owner

  fact_unverifiable:
    action: stop
    escalate_to: domain_expert

  retry_cap_exceeded:
    max_retries: 5
    action: stop
    escalate_to: orchestrator

  budget_threshold:
    threshold_percent: 80
    action: pause
    escalate_to: budget_owner

  human_approval_required:
    action: stop
    create: approval_request
```

---

### 4. Deterministic Behavior

Agents should prefer:

| Preference | Reason |
|------------|--------|
| **Schemas** | Validate inputs/outputs |
| **Templates** | Consistent structure |
| **Checklists** | Complete coverage |
| **Validators** | Automated verification |
| **Small PRs** | Easier review, less risk |

```yaml
# Example: Prefer schema over free-form
agent_output:
  # Good: Schema-validated
  format: json_schema
  schema: schemas/prd.json

  # Bad: Free-form
  # format: free_text
```

---

### 5. Provenance and Traceability

Every artifact must include:

| Metadata | Description |
|----------|-------------|
| `workflow_id` | Parent workflow identifier |
| `agent_name` | Agent that produced artifact |
| `agent_role` | Agent's role in the system |
| `model_id` | AI model identifier (if applicable) |
| `model_version` | AI model version |
| `inputs` | References to inputs used |
| `input_hashes` | SHA256 of inputs |
| `policy_decisions` | IDs of policy evaluations |
| `timestamp` | UTC timestamp of creation |

```json
{
  "artifact": {
    "type": "change",
    "path": "services/user-service/src/auth.ts"
  },
  "provenance": {
    "workflow_id": "wf-xyz789",
    "agent_name": "backend-builder",
    "agent_role": "engineering",
    "model_id": "claude-3-opus",
    "model_version": "20260106",
    "inputs": [
      {"ref": "requirements/auth.md", "hash": "abc123"},
      {"ref": "specs/api.yaml", "hash": "def456"}
    ],
    "policy_decisions": ["pd-001", "pd-002"],
    "timestamp": "2026-01-06T12:00:00Z"
  }
}
```

---

### 6. UI Design Jail Rule

**No free-form CSS or unapproved UI components.**

| Allowed | Forbidden |
|---------|-----------|
| Design tokens | Arbitrary CSS values |
| Approved components | Custom components |
| Component composition | Direct DOM manipulation |
| Token-based styling | Inline styles |

```tsx
// ✅ Allowed: Using design tokens
<Button variant="primary" size="md">
  Submit
</Button>

// ❌ Forbidden: Arbitrary CSS
<button style={{
  backgroundColor: '#0066FF',
  padding: '12px 24px'
}}>
  Submit
</button>
```

See: `docs/03-platform/design-system-design-jail.md`

---

### 7. Security Rule

Agents must NEVER:

| Forbidden Action | Reason |
|------------------|--------|
| Leak secrets | Credential exposure |
| Weaken auth/authz | Security degradation |
| Introduce unvetted dependencies | Supply chain risk |
| Disable scans or tests | Quality gate bypass |
| Bypass CI/CD checks | Evidence integrity |
| Log sensitive data | Data exposure |
| Hardcode credentials | Secret management violation |

```yaml
security_rules:
  secrets:
    - never_log
    - never_commit
    - never_return_in_output

  dependencies:
    - require_vulnerability_scan
    - require_license_check
    - require_provenance

  ci_cd:
    - never_skip_checks
    - never_force_merge
    - never_bypass_gates
```

---

### 8. Phase 1 Interview Rules

Agents participating in Phase 1 (Adaptive Interview) MUST follow these rules to ensure a consistent, user-friendly intake experience.

#### Question Format Requirements

Every Phase 1 question generated by agents MUST:

| Requirement | Implementation |
|-------------|----------------|
| **Multiple-choice primary** | 3-12 pre-defined options |
| **Always "Not sure"** | Every question includes this option |
| **Always "Other (write)"** | Every question includes this option |
| **No required free-text** | Free-text is optional enhancement, never blocking |
| **Inline explanation** | "Why we ask this" available for every question |

```yaml
# Required question structure
question:
  id: string (required)
  text: string (required, the question)
  why_we_ask: string (required, explanation)
  options:
    - label: string
      value: string
      triggers_module: string (optional)
    - label: "Not sure"
      value: "not_sure"
      default_behavior: object (optional)
    - label: "Other (describe)..."
      value: "other"
      free_text_prompt: string
  multi_select: boolean (default: false)
  required: boolean (default: true)
```

**Forbidden Patterns:**
- Questions requiring essay-length answers to proceed
- Questions without pre-defined options
- Questions without "Not sure" option
- Questions without "Other" option
- Hidden branching logic not explained to user

#### Branching Logic Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max branch depth | 3 | Prevents interview fatigue |
| Max questions per module | 8 | Focused, completable modules |
| Max total questions (fast path) | 15 | Quick start experience |
| Max total questions (extended) | 45 | Comprehensive but bounded |

#### Asset Requirements Capture

Agents MUST capture Asset Requirements before Concept Lock:

```yaml
# Asset capture rules
asset_requirements:
  mandatory_capture:
    - logo_requirements     # At least variants + formats
    - icon_requirements     # If mobile_app or pwa
    - favicon_requirements  # If web_app
    - icon_set_policy       # Which icon library

  if_skipped:
    action: log_assumption
    assumption:
      text: "No {asset_type} requirements specified"
      risk_level: medium
      requires_resolution_by: gate_2

  before_concept_lock:
    validate: asset_requirements_manifest_present
    block_if_missing: true
    allow_empty_with_confirmation: true
```

**Agent Behavior:**
1. If user skips asset questions → Log explicit assumption
2. If no assets captured → Mark as requiring confirmation at lock
3. Cannot proceed to build without Asset Requirements Manifest
4. Empty manifest allowed only with explicit user confirmation

#### Change Request Enforcement

After Concept Lock, agents MUST route all scope changes through Change Requests:

```yaml
# Change Request rules for agents
change_request_rules:
  triggers:
    - user_requests_new_journey
    - user_requests_new_feature
    - user_requests_brand_change
    - user_requests_region_change
    - user_requests_platform_change

  agent_behavior:
    - detect_change_type
    - calculate_impact_estimate
    - present_impact_to_user
    - require_explicit_cr_submission
    - route_to_approval_queue

  forbidden:
    - applying_changes_without_cr
    - bypassing_impact_analysis
    - auto_approving_changes
    - casual_scope_additions_via_chat
```

**Prohibited Agent Actions Post-Lock:**
| Action | Status | Required Process |
|--------|--------|------------------|
| Add new journey | Blocked | Change Request |
| Add new feature | Blocked | Change Request |
| Change brand colors | Blocked | Change Request |
| Add region | Blocked | Change Request |
| Add platform | Blocked | Change Request |
| Fix typo in name | Allowed | Minor edit (patch version) |
| Resolve assumption | Allowed | Assumption resolution flow |

#### Draft vs. Locked Mode Behavior

| Mode | Agent Behavior |
|------|----------------|
| **Draft** | Free exploration, suggest options, allow revisions |
| **Locked** | Enforce constraints, route changes to CR, track drift |

**Draft Mode Agent Rules:**
- Present all options openly
- Allow unlimited revisions
- Log changes as revision history
- Show live preview updates
- Encourage exploration
- DO NOT block creative choices
- DO NOT enforce implementation constraints yet

**Locked Mode Agent Rules:**
- Enforce all Concept Lock constraints
- Block out-of-scope work
- Route changes through CR workflow
- Track drift continuously
- Report drift violations immediately
- DO NOT allow casual modifications
- DO NOT proceed without valid Concept Lock reference

#### Pre-Build Validation

Before any build work begins, agents MUST verify:

```yaml
pre_build_checks:
  required:
    - concept_lock_exists: true
    - concept_lock_status: locked
    - asset_requirements_manifest_present: true
    - assumptions_acceptable: true  # <30% "not sure"
    - budget_approved: true

  block_build_if:
    - concept_lock_missing
    - concept_lock_in_draft
    - asset_requirements_missing_without_confirmation
    - assumptions_exceed_threshold
    - budget_not_approved

  warn_but_allow:
    - assumptions_exist_with_safe_defaults
    - optional_modules_skipped
```

---

### 9. Conflict Resolution

When agents disagree:

```
1. Detect disagreement
       │
       ▼
2. Escalate to CEO Orchestrator or Studio Coach
       │
       ▼
3. Gather evidence from both sides
       │
       ▼
4. Apply decision criteria:
   - Policy takes precedence
   - Evidence over opinions
   - Safety over speed
       │
       ▼
5. Record decision with reasoning
       │
       ▼
6. Continue workflow
```

### Decision Priority

1. **Policy** - Explicit rules always win
2. **Evidence** - Data-backed arguments preferred
3. **Precedent** - Past decisions inform current
4. **Human judgment** - Escalate if ambiguous

---

## Contract Enforcement

### Pre-Execution Check

```python
async def execute_agent(agent: Agent, task: Task) -> Result:
    # Check role boundaries
    if not check_role_boundary(agent, task.action):
        return Result.forbidden("Role boundary violation")

    # Check tool permissions
    if not check_tool_permissions(agent, task.tools):
        return Result.forbidden("Tool permission denied")

    # Check budget
    if not check_budget(agent.workflow_id):
        return Result.budget_exceeded("Workflow budget exhausted")

    # Execute
    result = await agent.execute(task)

    # Verify artifact produced
    if not result.has_artifact():
        return Result.failed("No artifact produced")

    # Attach provenance
    result.artifact.provenance = create_provenance(agent, task)

    return result
```

### Post-Execution Validation

```yaml
validation:
  artifact_required: true
  provenance_required: true
  audit_log_required: true

  checks:
    - artifact_schema_valid
    - provenance_complete
    - no_security_violations
    - within_role_boundary
```

---

## Violation Handling

| Violation | Severity | Action |
|-----------|----------|--------|
| No artifact produced | Warning | Log, allow retry |
| Role boundary exceeded | Error | Block, alert |
| Security rule violated | Critical | Block, incident |
| Stop condition ignored | Critical | Terminate workflow |
| Provenance missing | Error | Block until fixed |

---

### 10. Claude Code Operating Rules

All Claude Code workers MUST follow these operating rules when executing in Operator Mode.

#### Plan→Build→Verify Discipline

Every Claude Code session MUST follow the three-phase discipline:

```yaml
session_phases:
  plan:
    mandatory: true
    minimum_refinement_cycles: 2
    output: plans/run-{run_id}/{task_slug}.md
    gates:
      - plan_artifact_exists: true
      - plan_complete: true
      - plan_aligned_with_concept_lock: true

  build:
    mandatory: true
    prerequisite: plan_phase_complete
    rules:
      - follow_plan_exactly: true
      - no_unplanned_changes: true
      - commit_format_enforced: true

  verify:
    mandatory: true
    prerequisite: build_phase_complete
    output: evidence/run-{run_id}/{task_slug}-verification.json
    checks:
      - lint_pass: required
      - tests_pass: required
      - security_scan_pass: required
      - plan_alignment_check: required
```

**Enforcement:**
- PR creation blocked until Verification Report exists
- Verification Report MUST show all checks passed
- Sessions without Plan artifact are considered FAILED

#### Worktree Isolation Requirements

Every Claude Code worker MUST operate in an isolated Git worktree:

| Requirement | Enforcement |
|-------------|-------------|
| **Own worktree** | Worker spawned only after worktree created |
| **Own branch** | Branch created with worktree, never shared |
| **No shared directories** | Working directory isolation complete |
| **No cross-worker access** | Workers cannot read other workers' worktrees |
| **Clean state on start** | Worktree created fresh, not reused |

```yaml
worktree_rules:
  creation:
    trigger: task_assignment
    creator: coordinator
    format: /worktrees/run-{run_id}-{task_slug}

  isolation:
    shared_working_directory: forbidden
    cross_worker_access: forbidden
    context_sharing: forbidden

  lifecycle:
    created: before_worker_spawn
    active: during_session
    removed: after_pr_merge
```

#### Scope Limitation Rules

Workers MUST NOT perform broad refactors unless explicitly scoped:

| Action | Allowed | Condition |
|--------|---------|-----------|
| **Implement planned changes** | ✓ Yes | Per Plan artifact |
| **Fix directly related code** | ✓ Yes | Within same file/module |
| **Refactor unrelated code** | ✗ No | Not in Plan scope |
| **Add unplanned features** | ✗ No | Requires Plan amendment |
| **Modify shared types broadly** | ✗ No | Requires explicit lock |
| **Update dependencies** | ⚠ Limited | Only if in Plan |

```yaml
scope_rules:
  changes_must_match_plan: true

  out_of_scope_detection:
    method: diff_against_plan
    threshold: 0.10  # 10% deviation triggers warning
    block_threshold: 0.30  # 30% deviation blocks PR

  on_scope_violation:
    - log_violation
    - mark_for_review
    - block_pr_if_exceeds_threshold
```

#### Required Artifact Production

Workers MUST produce these artifacts:

| Artifact | Location | When | Required |
|----------|----------|------|----------|
| **Plan** | `plans/run-{run_id}/{task}.md` | Plan Mode | Yes |
| **Catch-up Pack** | `catch-up/run-{run_id}/{task}.md` | Ongoing | Yes |
| **Verification Report** | `evidence/run-{run_id}/{task}-verification.json` | Before PR | Yes |
| **Context Reset Pack** | `context-reset/run-{run_id}/{task}.json` | On budget exceed | If triggered |

**Enforcement:**
- Missing Plan → session marked FAILED
- Missing Verification Report → PR blocked
- Missing Catch-up Pack → warning logged

#### Coordinator Responsibilities

The Coordinator MUST:

| Responsibility | Action | Failure Mode |
|----------------|--------|--------------|
| **Spawn workers** | Create worktree, branch, issue | Block run on failure |
| **Manage locks** | Acquire/release file locks | Serialize on conflict |
| **Resolve conflicts** | Rebase, regenerate, or serialize | Escalate if unresolvable |
| **Aggregate results** | Collect all worker outputs | Partial success allowed |
| **Produce summary** | Write run-summary.md | Required for run completion |
| **Trigger merges** | Enable auto-merge on PRs | After verification pass |
| **Clean up** | Remove worktrees after merge | Within 1 hour of merge |

```yaml
coordinator_rules:
  conflict_resolution:
    attempt_1: auto_rebase
    attempt_2: regenerate_conflicting_files
    attempt_3: serialize_tasks
    attempt_4: escalate_to_dashboard

  summary_required: true
  summary_location: runs/run-{run_id}/run-summary.md

  cleanup:
    automatic: true
    delay_after_merge: 0  # Immediate cleanup
    preserve_on_failure: true  # For debugging
```

#### End-of-Session Verification

Every session MUST end with verification:

```
SESSION COMPLETE?
       │
       ├── No → Continue work
       │
       └── Yes
               │
               ▼
       VERIFICATION PASS REQUIRED
               │
               ├── Run all checks (lint, test, security)
               ├── Generate Verification Report
               ├── Check plan alignment
               └── Write Catch-up Pack
               │
               ▼
       ALL CHECKS PASS?
               │
               ├── No → Fix issues, re-verify
               │
               └── Yes
                       │
                       ▼
               CREATE PR (session valid)
```

**Session without Verification Pass is INVALID.**

---

## Related Documents

- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 and Concept Lock
- `docs/01-product/requirements-schema.md` — Phase 1 output schemas
- `docs/03-platform/portal-webapp.md` — Phase 1 interview dashboard
- `docs/03-platform/design-system-design-jail.md` — Design Jail constraints
- `docs/06-operations/claude-code-operating-model.md` — Claude Code execution model
- `docs/06-operations/context-engineering-playbook.md` — Context engineering practices
- `docs/07-integrations/git-integration.md` — Concept Lock Git storage, worktree strategy
- `docs/08-agents/agent-permissions.md` — Permission details
- `docs/08-agents/agent-quality-bar.md` — Quality standards
- `policies/opa/agents/` — Agent policies
- `policies/opa/concept/` — Concept Lock policies
- `CLAUDE.md` — Root rules file for Claude Code sessions

---

**Version**: 2.3.0 | **Date**: 2026-01-08
