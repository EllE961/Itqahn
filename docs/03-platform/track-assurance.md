# Track Assurance (Drift Review Mode)

> **Version:** 1.0.0
> **Status:** Normative
> **Last Updated:** 2026-01-08

## Overview

Track Assurance is Itqahn's mechanism for detecting and resolving **drift** between approved specifications and actual implementation. When drift exceeds configured thresholds, Itqahn pauses work, preserves state, and surfaces a Review Checkpoint for operator decision—all without losing progress.

This specification defines:
- What constitutes drift in Itqahn workflows
- How drift is detected and scored
- The pause/review/resume lifecycle
- Dashboard UX for the Assurance panel
- Evidence and audit requirements
- Enforcement hooks and policy gates

---

## 1. Drift Definition

### 1.1 Drift Categories

Drift is any divergence between the **approved source of truth** and the **current state**. Itqahn recognizes four drift categories:

| Category | Source of Truth | Current State | Detection Method |
|----------|-----------------|---------------|------------------|
| **Plan Drift** | Concept Lock (approved spec) | Generated implementation plan | Semantic comparison of plan steps vs spec requirements |
| **Code Drift** | Implementation plan + Concept Lock | Committed code | AST analysis, coverage mapping, feature flag audit |
| **UI Drift** | Design OS tokens + wireframes | Rendered components | Visual regression, accessibility delta |
| **Behavior Drift** | Acceptance criteria + test contracts | Runtime behavior | Contract test results, integration test outcomes |

### 1.2 Drift Score Calculation

Each drift category produces a normalized score from 0.0 (no drift) to 1.0 (complete divergence):

```
drift_score = weighted_sum([
    (plan_drift_score,     weight: 0.30),
    (code_drift_score,     weight: 0.35),
    (ui_drift_score,       weight: 0.15),
    (behavior_drift_score, weight: 0.20)
])
```

**Thresholds:**

| Drift Score | Classification | Action |
|-------------|----------------|--------|
| 0.00 - 0.10 | **Green** | Continue autonomously |
| 0.11 - 0.30 | **Yellow** | Log warning, continue with enhanced monitoring |
| 0.31 - 0.50 | **Orange** | Soft pause: complete current step, then await review |
| 0.51 - 1.00 | **Red** | Hard pause: immediate stop, mandatory review |

### 1.3 Drift Detection Timing

Drift MUST be evaluated at these checkpoints:

1. **Post-Planning:** After Architect agent produces implementation plan
2. **Post-Build:** After each significant code generation batch
3. **Post-Test:** After test execution completes
4. **Pre-Merge:** Before any PR merge to protected branch
5. **On-Demand:** When operator triggers manual review

---

## 2. Triggers

### 2.1 Automatic Drift Detection

The drift-checker runs automatically at each checkpoint defined in Section 1.3. When `drift_score > threshold`, the system:

1. Completes the current atomic operation (if safe)
2. Persists all workflow state to Temporal
3. Generates a Review Checkpoint artifact
4. Transitions workflow to `PAUSED_FOR_REVIEW` state
5. Emits `drift.threshold_exceeded` event
6. Updates dashboard Assurance panel

**Configuration (per-project):**

```yaml
# .itqahn/track-assurance.yaml
drift_thresholds:
  soft_pause: 0.30      # Orange threshold
  hard_pause: 0.50      # Red threshold

auto_detection:
  enabled: true
  checkpoints:
    - post_planning
    - post_build
    - post_test
    - pre_merge

escalation:
  notify_on_yellow: false
  notify_on_orange: true
  notify_on_red: true
  notification_channel: "slack://itqahn-alerts"
```

### 2.2 Manual "Stop & Review" Trigger

Operators MAY trigger a review at any time from the dashboard:

**Dashboard Action:** `Project > Runs > [Active Run] > Stop & Review`

When triggered manually:

1. System waits for current atomic operation to complete (max 60 seconds)
2. If operation cannot complete safely, system performs compensating action
3. Review Checkpoint is generated with `trigger: manual`
4. Workflow enters `PAUSED_FOR_REVIEW` state
5. Operator receives confirmation with checkpoint ID

**Manual trigger is non-destructive.** All state is preserved; the operator may resume or terminate.

---

## 3. Pause/Review/Resume Lifecycle

### 3.1 Review Checkpoint Primitive

A Review Checkpoint is an immutable artifact capturing workflow state at a pause boundary:

```json
{
  "checkpoint_id": "ckpt-20260108-abc123",
  "run_id": "run-abc123",
  "workflow_id": "wf-xyz789",
  "tenant_id": "tenant-acme",
  "created_at": "2026-01-08T14:30:00Z",
  "trigger": "automatic|manual",
  "drift_analysis": {
    "overall_score": 0.42,
    "category_scores": {
      "plan": 0.15,
      "code": 0.55,
      "ui": 0.10,
      "behavior": 0.45
    },
    "threshold_violated": "soft_pause",
    "drift_items": [
      {
        "category": "code",
        "location": "src/auth/login.ts:45-78",
        "expected": "OAuth2 PKCE flow per spec section 3.2",
        "actual": "Basic token exchange without PKCE",
        "severity": "high",
        "remediation_hint": "Implement PKCE challenge/verifier"
      }
    ]
  },
  "workflow_state": {
    "current_stage": "build",
    "completed_steps": ["intake", "architect", "build:auth-module"],
    "pending_steps": ["build:api-routes", "test", "policy", "evidence"],
    "temporal_run_id": "temporal-run-456",
    "temporal_workflow_id": "itqahn-build-abc123"
  },
  "artifacts": {
    "concept_lock_hash": "sha256:abc...",
    "plan_hash": "sha256:def...",
    "code_snapshot_ref": "git:feature/abc123@commit-xyz",
    "test_results_ref": "s3://evidence/run-abc123/test-results.json"
  },
  "operator_options": [
    "resume_with_replan",
    "resume_as_is",
    "terminate",
    "rollback_to_checkpoint"
  ]
}
```

### 3.2 Workflow States

```
                    ┌─────────────────┐
                    │    RUNNING      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │  PAUSED  │   │  PAUSED  │   │ COMPLETED│
       │ SOFT     │   │ HARD     │   │          │
       └────┬─────┘   └────┬─────┘   └──────────┘
            │              │
            │              │
            ▼              ▼
       ┌─────────────────────┐
       │  PAUSED_FOR_REVIEW  │
       └──────────┬──────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│RESUMED │  │RESUMED   │  │TERMINATED│  │ROLLED    │
│REPLAN  │  │AS_IS     │  │          │  │BACK      │
└────────┘  └──────────┘  └──────────┘  └──────────┘
```

### 3.3 Resume Options

#### 3.3.1 Resume with Replan

**When to use:** Drift indicates the current plan is fundamentally misaligned with the spec.

**Behavior:**
1. Architect agent generates new implementation plan from current state
2. New plan is diffed against Concept Lock for validation
3. If new plan passes drift check, workflow resumes from replanned state
4. All previously completed work is preserved where possible

**Guardrail:** Replan attempts are limited to 3 per run. Exceeding this triggers escalation.

#### 3.3.2 Resume As-Is

**When to use:** Operator has reviewed drift and determined it is acceptable (e.g., intentional deviation, spec needs update).

**Behavior:**
1. Operator MUST provide justification text (min 50 characters)
2. Justification is recorded in audit trail
3. Drift score is acknowledged but not cleared
4. Workflow resumes from paused state
5. Evidence Pack includes operator override record

#### 3.3.3 Terminate

**When to use:** Run should not continue; work will be discarded or restarted fresh.

**Behavior:**
1. Workflow enters terminal `TERMINATED` state
2. All artifacts are preserved for audit
3. Any uncommitted code changes remain in feature branch (not deleted)
4. Run is marked as `terminated_by_operator` in Evidence Pack

#### 3.3.4 Rollback to Previous Checkpoint

**When to use:** Drift was introduced in recent steps; reverting to last-known-good state is preferred.

**Behavior:**
1. System identifies most recent checkpoint where `drift_score < soft_pause`
2. Workflow state is restored to that checkpoint
3. Git branch is reset to checkpoint commit (with backup branch created)
4. Workflow resumes from restored state

**Guardrail:** Rollback requires confirmation if more than 2 hours of work would be discarded.

---

## 4. Dashboard UX: Assurance Panel

### 4.1 Panel Location

The Assurance panel appears in the Portal webapp at:
- **Project Dashboard:** Summary card showing current drift status
- **Run Details:** Full drift analysis with interactive review

### 4.2 Assurance Summary Card

Displays on the Project Dashboard:

```
┌─────────────────────────────────────────────────────────┐
│  TRACK ASSURANCE                              [●] Live  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Drift Score:  ████████░░  0.18 (Yellow)               │
│                                                         │
│  Plan:     ██░░░░░░░░  0.12                            │
│  Code:     ███░░░░░░░  0.22                            │
│  UI:       █░░░░░░░░░  0.08                            │
│  Behavior: ██░░░░░░░░  0.15                            │
│                                                         │
│  Last Check: 2 min ago    Next: Post-Build             │
│                                                         │
│  [Stop & Review]                    [View History]     │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Review Checkpoint Modal

When workflow enters `PAUSED_FOR_REVIEW`, operator sees:

```
┌─────────────────────────────────────────────────────────┐
│  REVIEW CHECKPOINT                          ckpt-abc123 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⚠️  Drift threshold exceeded (Orange: 0.42)            │
│                                                         │
│  Trigger: Automatic (post-build checkpoint)            │
│  Paused At: 2026-01-08 14:30:00 UTC                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ DRIFT ITEMS (3)                                 │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ● Code: src/auth/login.ts                       │   │
│  │   Expected: OAuth2 PKCE flow                    │   │
│  │   Actual: Basic token exchange                  │   │
│  │   Severity: HIGH                                │   │
│  │                                                 │   │
│  │ ● Code: src/api/users.ts                        │   │
│  │   Expected: Rate limiting per spec 4.1          │   │
│  │   Actual: No rate limiting implemented          │   │
│  │   Severity: MEDIUM                              │   │
│  │                                                 │   │
│  │ ● Behavior: POST /api/login                     │   │
│  │   Expected: 401 on invalid credentials          │   │
│  │   Actual: 500 error thrown                      │   │
│  │   Severity: HIGH                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ RECOMMENDED ACTION                              │   │
│  │                                                 │   │
│  │ Based on drift analysis, we recommend:          │   │
│  │ **Resume with Replan** to address auth gaps.    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Resume: Replan]  [Resume: As-Is]  [Rollback]  [End]  │
│                                                         │
│  ○ As-Is requires justification                        │
└─────────────────────────────────────────────────────────┘
```

### 4.4 Drift History Timeline

The Run Details view includes a timeline showing drift score evolution:

```
Drift Score Over Time
─────────────────────────────────────────────────────────
1.0 ┤
    │
0.5 ┤                              ●──────● PAUSED
    │                           ╱
0.3 ┤- - - - - - - - - - - - -╱- - - - - - - - (threshold)
    │                      ╱
    │                   ╱
0.0 ┼──●────●────●───●─
    └──┬────┬────┬───┬────┬────┬───
      Init Plan Build Build Test  Now
                 :1    :2
```

---

## 5. Evidence and Audit Requirements

### 5.1 Checkpoint Evidence

Every Review Checkpoint MUST be recorded in the Evidence Pack:

```json
{
  "evidence_type": "review_checkpoint",
  "checkpoint_id": "ckpt-abc123",
  "recorded_at": "2026-01-08T14:30:00Z",
  "drift_snapshot": { ... },
  "workflow_state_snapshot": { ... },
  "operator_decision": null,
  "decision_timestamp": null,
  "decision_justification": null
}
```

### 5.2 Decision Evidence

When operator makes a decision, the Evidence Pack MUST be updated:

```json
{
  "evidence_type": "checkpoint_decision",
  "checkpoint_id": "ckpt-abc123",
  "decision": "resume_as_is",
  "decided_by": "operator@acme.com",
  "decided_at": "2026-01-08T14:45:00Z",
  "justification": "Drift in auth module is acceptable; PKCE will be added in follow-up ticket ACME-1234. Rate limiting deferred to v2.",
  "acknowledged_risks": [
    "code:src/auth/login.ts:no_pkce",
    "code:src/api/users.ts:no_rate_limit"
  ]
}
```

### 5.3 Audit Trail Requirements

The following events MUST be logged to the audit destination:

| Event | Required Fields |
|-------|-----------------|
| `drift.check_started` | run_id, checkpoint_type, timestamp |
| `drift.check_completed` | run_id, drift_score, category_scores, threshold_status |
| `drift.threshold_exceeded` | run_id, drift_score, threshold_violated, drift_items |
| `drift.pause_initiated` | run_id, checkpoint_id, trigger_type |
| `drift.review_decision` | run_id, checkpoint_id, decision, operator, justification |
| `drift.resume_started` | run_id, checkpoint_id, resume_mode |
| `drift.rollback_executed` | run_id, from_checkpoint, to_checkpoint |

---

## 6. Enforcement Hooks

### 6.1 OPA Policy Gate

The `drift.assurance` policy MUST be evaluated before any merge:

```rego
# policies/opa/drift/assurance.rego
package drift.assurance

import future.keywords.in

default allow_merge = false

# Allow merge if drift is within acceptable range
allow_merge {
    input.drift_score <= input.thresholds.merge_allowed
    no_unacknowledged_high_severity
}

# Allow merge if all drift items are acknowledged
allow_merge {
    input.drift_score > input.thresholds.merge_allowed
    all_drift_acknowledged
}

no_unacknowledged_high_severity {
    high_severity_items := [item |
        item := input.drift_items[_]
        item.severity == "high"
        not item.acknowledged
    ]
    count(high_severity_items) == 0
}

all_drift_acknowledged {
    unacknowledged := [item |
        item := input.drift_items[_]
        not item.acknowledged
    ]
    count(unacknowledged) == 0
}

deny[msg] {
    input.drift_score > input.thresholds.merge_allowed
    not all_drift_acknowledged
    msg := sprintf("Drift score %.2f exceeds threshold; unacknowledged drift items present", [input.drift_score])
}
```

### 6.2 CI Gate Integration

The drift-checker MUST run as a required CI check:

```yaml
# .github/workflows/drift-check.yml
name: Drift Check
on:
  pull_request:
    branches: [main, develop]

jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Drift Checker
        uses: itqahn/drift-checker-action@v1
        with:
          concept_lock_path: .itqahn/concept-lock/
          threshold_soft: 0.30
          threshold_hard: 0.50
          fail_on: hard  # or 'soft' for stricter enforcement

      - name: Upload Drift Report
        uses: actions/upload-artifact@v4
        with:
          name: drift-report
          path: .itqahn/drift-report.json
```

### 6.3 Drift-Checker Tool Integration

The `drift-checker` CLI tool is invoked by the CI gate and can be run manually:

```bash
# Automated invocation (by CI/Itqahn)
drift-checker analyze \
  --concept-lock .itqahn/concept-lock/ \
  --code-root ./src \
  --output .itqahn/drift-report.json \
  --format json

# Output schema: tools/validators/drift-score.schema.json
```

---

## 7. Edge Cases and Failure Recovery

### 7.1 Merge Conflicts During Pause

**Scenario:** While workflow is paused, another PR merges to main, creating conflicts.

**Resolution:**
1. On resume, system detects conflict state
2. Workflow transitions to `CONFLICT_RESOLUTION` sub-state
3. Itqahn attempts automatic conflict resolution for non-semantic conflicts
4. If automatic resolution fails, operator is notified with conflict details
5. Operator may: resolve manually, rebase and resume, or terminate

### 7.2 Checkpoint During Test Failures

**Scenario:** Drift threshold exceeded while tests are failing.

**Resolution:**
1. Checkpoint captures test failure state
2. Drift analysis includes `behavior_drift` from test failures
3. Resume options include:
   - `resume_with_replan`: Architect considers test failures in new plan
   - `resume_as_is`: Requires explicit acknowledgment of failing tests
4. Evidence Pack marks checkpoint as `test_state: failing`

### 7.3 Non-Idempotent Build Artifacts

**Scenario:** Build produces different artifacts on each run (timestamps, random IDs).

**Resolution:**
1. Drift-checker uses **semantic comparison**, not byte-level diff
2. Known non-deterministic patterns are excluded from drift score:
   - Build timestamps
   - Generated UUIDs in comments
   - Source map paths
3. Configuration allows custom exclusion patterns:

```yaml
# .itqahn/track-assurance.yaml
drift_exclusions:
  - pattern: "BUILD_TIME=.*"
    reason: "Build timestamp is non-deterministic"
  - pattern: "sourceMappingURL=.*"
    reason: "Source map paths vary by environment"
```

### 7.4 Large Project Drift Analysis

**Scenario:** Project has 10,000+ files; full drift analysis takes >10 minutes.

**Resolution:**
1. Incremental drift analysis enabled by default
2. Only changed files since last checkpoint are analyzed
3. Full analysis runs on configurable schedule (default: once per day)
4. Dashboard shows "incremental" vs "full" analysis indicator

```yaml
# .itqahn/track-assurance.yaml
analysis:
  mode: incremental  # or 'full'
  full_analysis_schedule: "0 0 * * *"  # Daily at midnight
  incremental_threshold: 100  # Files changed threshold for forced full
```

### 7.5 Infinite Re-Plan Loop

**Scenario:** Replan repeatedly produces plans that drift immediately.

**Resolution:**
1. Replan attempts are tracked per run
2. After 3 replan attempts, system escalates:
   - Workflow enters `ESCALATED` state
   - Operator notification with loop analysis
   - Options: manual plan adjustment, spec revision request, terminate
3. Consecutive replans within 1 hour trigger immediate escalation

### 7.6 Operator Override Abuse

**Scenario:** Operator repeatedly uses "Resume As-Is" to bypass drift checks.

**Resolution:**
1. Override frequency is tracked per project
2. Thresholds trigger warnings:
   - >3 overrides per week: Dashboard warning
   - >5 overrides per week: Escalation to project owner
   - >10 overrides per week: Auto-pause on new drift (requires justification before each resume)
3. All overrides are included in project compliance reports

### 7.7 Stuck Workflow Recovery

**Scenario:** Workflow fails to pause cleanly; state is inconsistent.

**Resolution:**
1. Temporal workflow has `STUCK_DETECTION_TIMEOUT` (default: 15 minutes)
2. If workflow doesn't respond to pause signal within timeout:
   - Force-terminate Temporal workflow
   - Create emergency checkpoint from last known state
   - Mark run as `STUCK_RECOVERY`
   - Notify operator
3. Recovery options:
   - Attempt resume from emergency checkpoint
   - Terminate and start fresh run

### 7.8 Network Partition During Review

**Scenario:** Operator submits decision but network fails before confirmation.

**Resolution:**
1. Decision submission is idempotent (keyed by checkpoint_id + decision)
2. Client retries with exponential backoff
3. If decision recorded server-side, duplicate submissions are acknowledged
4. If decision not recorded, client shows retry UI
5. Checkpoint remains in `PAUSED_FOR_REVIEW` until confirmed

---

## 8. Permissions and Access Control

### 8.1 Required Permissions

| Action | Required Role |
|--------|---------------|
| View drift status | `project:read` |
| Trigger manual review | `project:write` |
| Resume with replan | `project:write` |
| Resume as-is | `project:admin` |
| Rollback | `project:admin` |
| Terminate | `project:admin` |
| Modify thresholds | `project:admin` |

### 8.2 Operator Mode Permissions

When Operator Mode is enabled with `--dangerously-skip-permissions`:

- All review decisions are auto-approved
- Justification is still REQUIRED for "Resume As-Is"
- All decisions are logged with `operator_mode: true`
- Evidence Pack includes operator mode flag

---

## 9. Metrics and Observability

### 9.1 Key Metrics

| Metric | Description | Labels |
|--------|-------------|--------|
| `itqahn_drift_score` | Current drift score | project, run_id, category |
| `itqahn_drift_checks_total` | Total drift checks performed | project, checkpoint_type, result |
| `itqahn_drift_pauses_total` | Total drift-triggered pauses | project, trigger_type, threshold |
| `itqahn_drift_review_duration_seconds` | Time spent in review | project, decision |
| `itqahn_drift_replan_attempts_total` | Replan attempts | project, run_id |
| `itqahn_drift_overrides_total` | Resume-as-is decisions | project, operator |

### 9.2 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `DriftThresholdExceeded` | drift_score > hard_pause | warning |
| `DriftReviewStuck` | review_duration > 4 hours | warning |
| `DriftReplanLoopDetected` | replan_attempts > 2 in 1 hour | critical |
| `DriftOverrideAbuse` | overrides > 5 in 7 days | warning |

---

## 10. Related Documentation

- [Workflow Architecture](../02-architecture/workflow-architecture.md) - Temporal workflow patterns
- [Evidence Pack](../05-compliance/evidence-pack.md) - Checkpoint evidence requirements
- [Git Integration](../07-integrations/git-integration.md) - Branch management during pause
- [Agent Quality Bar](../08-agents/agent-quality-bar.md) - Drift escalation rules
- [Runbooks](../06-operations/runbooks.md) - Drift-related incident response

---

## Appendix A: Drift Score Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DriftScore",
  "type": "object",
  "required": ["overall_score", "category_scores", "timestamp"],
  "properties": {
    "overall_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "category_scores": {
      "type": "object",
      "properties": {
        "plan": { "type": "number", "minimum": 0, "maximum": 1 },
        "code": { "type": "number", "minimum": 0, "maximum": 1 },
        "ui": { "type": "number", "minimum": 0, "maximum": 1 },
        "behavior": { "type": "number", "minimum": 0, "maximum": 1 }
      },
      "required": ["plan", "code", "ui", "behavior"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "drift_items": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/DriftItem"
      }
    }
  },
  "definitions": {
    "DriftItem": {
      "type": "object",
      "required": ["category", "location", "expected", "actual", "severity"],
      "properties": {
        "category": { "enum": ["plan", "code", "ui", "behavior"] },
        "location": { "type": "string" },
        "expected": { "type": "string" },
        "actual": { "type": "string" },
        "severity": { "enum": ["low", "medium", "high", "critical"] },
        "remediation_hint": { "type": "string" },
        "acknowledged": { "type": "boolean", "default": false },
        "acknowledged_by": { "type": "string" },
        "acknowledged_at": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```
