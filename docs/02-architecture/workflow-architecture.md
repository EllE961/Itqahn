# Workflow Architecture (Temporal)

All multi-step work in Itqahn runs as durable Temporal workflows. This is non-negotiable.

---

## Why a Workflow Engine is Mandatory

Agentic systems fail in ways normal CI/CD does not:

| Failure Mode | Problem | Workflow Solution |
|--------------|---------|-------------------|
| Timeouts | LLM calls take unpredictable time | Activity timeouts with retries |
| Rate limits | API throttling causes failures | Backoff and retry policies |
| Partial work | Crash mid-task loses progress | Durable state, resume from checkpoint |
| Retry storms | Naive retries overwhelm systems | Exponential backoff, jitter |
| State loss | Stateless execution forgets context | Workflow state persisted |
| Politeness loops | Agents endlessly apologize | Max turns, budget exhaustion |

**A workflow engine provides**:
- Durable state that survives crashes
- Deterministic retries with backoff
- Timeout management
- Idempotency guarantees
- Audit trails for every step

---

## Temporal Concepts in Itqahn

### Workflows

A **Workflow** is a multi-step process that:
- Has a unique ID
- Maintains durable state
- Can pause and resume
- Survives crashes and restarts

**Examples**:
- Feature development workflow (PRD → code → deploy)
- Incident response workflow
- Compliance audit workflow

### Activities

An **Activity** is a single step that:
- Performs actual work (LLM call, API call, file write)
- Has retry policies
- Has timeouts
- Must be idempotent

**Examples**:
- Generate code with LLM
- Run security scan
- Create pull request
- Send notification

### Signals

**Signals** are external inputs to running workflows:
- Human approvals
- External events (webhook triggers)
- Budget extensions

### Queries

**Queries** inspect workflow state without affecting it:
- Current phase
- Budget consumed
- Pending approvals

---

## Standard Workflow Stages

```
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│   Intake   │──▶│ Architect  │──▶│   Build    │──▶│   Test     │
│            │   │            │   │            │   │            │
│ • PRD      │   │ • ADRs     │   │ • Code     │   │ • Unit     │
│ • Risk     │   │ • Contracts│   │ • PRs      │   │ • Integ    │
│ • Budget   │   │ • Threat   │   │ • Review   │   │ • E2E      │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
                                                         │
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌─────▼──────┐
│ Post-Launch│◀──│   Deploy   │◀──│  Evidence  │◀──│   Policy   │
│            │   │            │   │            │   │            │
│ • SLO      │   │ • Canary   │   │ • SBOM     │   │ • Security │
│ • Feedback │   │ • Promote  │   │ • Provenance   │ • Budget   │
│ • Retro    │   │ • Rollback │   │ • Sign     │   │ • Drift    │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
```

---

## Required Workflow Invariants

### 1. Idempotency Keys

Every activity must be safe to retry:

```
activity_id = hash(workflow_id + activity_name + inputs)
```

- Same inputs → same outputs
- Use idempotency keys for external API calls
- Cache results by activity ID

### 2. Retry Policies

```yaml
retry_policy:
  initial_interval: 1s
  backoff_coefficient: 2.0
  maximum_interval: 60s
  maximum_attempts: 5
  non_retryable_errors:
    - PolicyDeniedError
    - BudgetExhaustedError
```

After max retries: escalate to human gate or dead-letter queue.

### 3. Budget Tracking

Every workflow tracks:

| Budget Type | Limit | Action on Exceed |
|-------------|-------|------------------|
| Token spend | Per-workflow limit | Pause, request extension |
| Cloud spend | Per-workflow limit | Pause, request extension |
| Wall time | 24h default | Escalate, extend or cancel |
| Turns | Max iterations | Stop, require review |

### 4. Stop Conditions

Workflows must stop when:

| Condition | Action |
|-----------|--------|
| Max turns reached | Stop, create review task |
| Max retries exceeded | Escalate to human |
| Budget exhausted | Pause, request approval |
| Policy denial | Stop, remediation required |
| Security alert | Stop immediately, trigger incident |

### 5. Human Approval Activities

High-risk operations require human signals:

```
await workflow.wait_for_signal("human_approval", timeout=24h)
```

Required for:
- Production deployments
- Auth/authz changes
- Destructive schema changes
- Policy exceptions
- Budget overrides

### 6. Audit Logging

Every activity logs:

```json
{
  "workflow_id": "wf-abc123",
  "activity_id": "act-xyz789",
  "agent_id": "backend-builder",
  "model": "claude-3-opus",
  "inputs_hash": "sha256:...",
  "outputs_hash": "sha256:...",
  "policy_verdicts": ["allowed", "allowed"],
  "tokens_used": 1234,
  "duration_ms": 5678,
  "timestamp": "2026-01-06T12:00:00Z"
}
```

---

## Workflow Namespaces

| Namespace | Purpose | Retention |
|-----------|---------|-----------|
| `itqahn-dev` | Development workflows | 7 days |
| `itqahn-staging` | Staging/test workflows | 14 days |
| `itqahn-prod` | Production workflows | 30 days |
| `itqahn-tenant-{id}` | High-assurance tenant isolation | Per contract |

---

## Failure Handling

### Activity Failure

```
Activity fails
    │
    ▼
Retry with backoff (up to max_attempts)
    │
    ├── Success → Continue workflow
    │
    └── Max retries exceeded
            │
            ▼
        Escalate to human gate
            │
            ├── Human approves retry → Retry
            ├── Human provides fix → Apply and continue
            └── Human cancels → Workflow cancelled
```

### Policy Failure

```
Policy denies action
    │
    ▼
Workflow pauses
    │
    ▼
Create remediation task
    │
    ├── Agent fixes issue → Resume workflow
    │
    └── Requires exception
            │
            ▼
        Human approval required
```

### Budget Exhaustion

```
Budget limit reached
    │
    ▼
Workflow pauses
    │
    ▼
Notification to owner
    │
    ├── Owner extends budget → Resume
    │
    └── Owner denies extension → Cancel workflow
```

### Security Alert

```
Security issue detected
    │
    ▼
Workflow stops immediately
    │
    ▼
Incident playbook triggers
    │
    ▼
Human investigation required
```

---

## Pause/Resume at Safe Boundaries

Workflows MUST support pausing at defined safe boundaries without losing progress.

### Safe Boundaries

| Boundary Type | Definition | Example |
|---------------|------------|---------|
| **Activity boundary** | Between activity completions | After code generation, before test |
| **Stage boundary** | Between workflow stages | After Build, before Test |
| **Checkpoint boundary** | Explicit checkpoint markers | After drift check passes |

### Pause Triggers

| Trigger | Behavior |
|---------|----------|
| **Drift threshold exceeded** | Pause after current activity completes |
| **Budget warning** | Soft pause at next checkpoint |
| **Budget exhausted** | Hard pause immediately (compensate if needed) |
| **Manual Stop & Review** | Pause at next safe boundary (max 60s wait) |
| **Kill switch** | Force stop, create emergency checkpoint |

### Resume Protocol

```
Workflow paused
    │
    ▼
Create Review Checkpoint artifact
    │
    ▼
Wait for operator decision (signal)
    │
    ├── Resume with replan → Re-execute Architect stage from checkpoint
    ├── Resume as-is → Continue from checkpoint (requires justification)
    ├── Rollback → Restore to previous checkpoint, resume from there
    └── Terminate → Mark workflow terminal, preserve artifacts
```

### Checkpoint Storage

Checkpoints are persisted to durable storage with the following retention:

| Checkpoint Type | Retention | Storage |
|-----------------|-----------|---------|
| **Automatic (drift)** | 30 days | S3 + Evidence Pack |
| **Manual (Stop & Review)** | 90 days | S3 + Evidence Pack |
| **Emergency (Kill switch)** | 1 year | S3 + Evidence Pack + Audit |

---

## Checkpointing Model

### Checkpoint Contents

Every checkpoint captures complete workflow state:

```json
{
  "checkpoint_id": "ckpt-abc123",
  "workflow_id": "wf-xyz789",
  "run_id": "run-def456",
  "created_at": "2026-01-08T14:30:00Z",
  "trigger": "automatic|manual|emergency",

  "workflow_state": {
    "current_stage": "build",
    "completed_activities": ["intake", "architect", "build:module-1"],
    "pending_activities": ["build:module-2", "test", "policy"],
    "temporal_state": {
      "run_id": "temporal-run-123",
      "history_event_id": 456
    }
  },

  "artifact_refs": {
    "concept_lock": "s3://artifacts/concept-lock-v1.0.0.json",
    "plan": "s3://artifacts/plan-abc123.json",
    "code_snapshot": "git:feature/abc123@commit-xyz",
    "test_results": "s3://artifacts/test-results-partial.json"
  },

  "metrics": {
    "tokens_consumed": 45000,
    "cost_consumed": 12.50,
    "duration_seconds": 3600
  },

  "drift_snapshot": {
    "score": 0.42,
    "category_scores": {"plan": 0.15, "code": 0.55, "ui": 0.10, "behavior": 0.45}
  }
}
```

### Checkpoint Restoration

When resuming from a checkpoint:

1. Load checkpoint from storage
2. Validate checkpoint integrity (hash verification)
3. Restore Temporal workflow state
4. Reload artifact references
5. Re-validate policy gates (may have changed)
6. Resume from `pending_activities[0]`

---

## Parallel Work Coordination

### Worktree-Based Parallelism

Parallel tasks execute in isolated Git worktrees to prevent conflicts:

```
Main Repository
    │
    ├── .git (shared)
    │
    ├── worktree-run-001/  (User Auth task)
    │   └── feat/run-001-user-auth
    │
    ├── worktree-run-002/  (Dashboard task)
    │   └── feat/run-002-dashboard
    │
    └── worktree-run-003/  (Settings task)
        └── feat/run-003-settings
```

### File Locking

Parallel tasks MUST acquire locks before modifying shared files:

| Lock Type | Duration | Queuing |
|-----------|----------|---------|
| **Exclusive** | Task duration | FIFO queue |
| **Shared** | Read-only access | Multiple readers |

**Files requiring exclusive locks:**
- `package.json` / `package-lock.json`
- Schema migration files
- Shared type definitions
- Configuration files

### Merge Queue Integration

All parallel PRs flow through GitHub merge queue:

```
Task A completes → PR #1 → Merge Queue Position 1 → CI → Merge
Task B completes → PR #2 → Merge Queue Position 2 → CI (includes PR #1) → Merge
Task C completes → PR #3 → Merge Queue Position 3 → CI (includes PR #1, #2) → Merge
```

### Conflict Resolution

```
Parallel tasks complete
    │
    ▼
PRs enter merge queue
    │
    ├── No conflicts → Merge in order
    │
    └── Conflicts detected
            │
            ▼
        Auto-rebase attempted
            │
            ├── Success → Continue merge queue
            │
            └── Failure → Serialize conflicting tasks
                    │
                    ▼
                Complete first task, rebase others
```

---

## Circuit Breakers

### Circuit Breaker Types

| Breaker | Threshold | Reset Condition |
|---------|-----------|-----------------|
| **Budget** | Per-workflow limit | Manual extension |
| **Error rate** | >5% in 5 minutes | Manual reset |
| **Retry** | Max attempts exceeded | Manual intervention |
| **Time** | 24h default | Extension or cancel |
| **Drift** | Score > 0.50 | Review checkpoint decision |

### Circuit Breaker States

```
CLOSED (normal)
    │
    ├── Threshold exceeded → OPEN
    │
    ▼
OPEN (blocked)
    │
    ├── Manual reset → CLOSED
    ├── Cooldown period (5 min) → HALF_OPEN
    │
    ▼
HALF_OPEN (testing)
    │
    ├── Success → CLOSED
    └── Failure → OPEN
```

### Budget Circuit Breaker Example

```yaml
circuit_breaker:
  type: budget
  thresholds:
    warning: 0.80   # 80% of budget → warning notification
    soft_pause: 0.95  # 95% → pause at next checkpoint
    hard_pause: 1.00  # 100% → immediate pause
  actions:
    on_warning:
      - notify: owner
      - log: budget_warning
    on_soft_pause:
      - checkpoint: current_state
      - notify: owner
      - wait_for_signal: budget_extension
    on_hard_pause:
      - compensate: current_activity
      - checkpoint: emergency
      - notify: owner
      - wait_for_signal: budget_extension
```

---

## Stuck Workflow Recovery

### Stuck Detection

A workflow is considered stuck when:

| Condition | Timeout | Detection |
|-----------|---------|-----------|
| **Activity not responding** | 15 minutes | Heartbeat timeout |
| **Signal not received** | 24 hours | Signal timeout |
| **Infinite loop** | 100 iterations | Turn counter |
| **Pause not acknowledging** | 60 seconds | Pause signal timeout |

### Recovery Protocol

```
Stuck workflow detected
    │
    ▼
Attempt graceful stop (30s timeout)
    │
    ├── Success → Create checkpoint, notify owner
    │
    └── Failure → Force terminate
            │
            ▼
        Create emergency checkpoint from last known state
            │
            ▼
        Mark workflow as STUCK_RECOVERY
            │
            ▼
        Notify owner with recovery options:
        ├── Resume from emergency checkpoint
        ├── Retry from last successful checkpoint
        └── Terminate and start fresh
```

### Emergency Checkpoint

When normal checkpointing fails, emergency checkpoint captures:

- Last known Temporal history event
- Git ref at last commit
- Partial artifacts (may be incomplete)
- Error state and stack traces
- Resource utilization at time of failure

---

## Workflow Patterns

### Saga Pattern (Compensating Actions)

For operations that need rollback:

```
1. Reserve resources
2. Create PR
3. Run tests
4. Merge PR
5. Deploy to canary

If step 5 fails:
    5c. Rollback canary
    4c. Revert merge
    3c. (tests don't need compensation)
    2c. Close PR
    1c. Release resources
```

### Parent-Child Workflows

For complex operations:

```
Parent: Feature Development
    │
    ├── Child: Backend Implementation
    ├── Child: Frontend Implementation
    ├── Child: Integration Tests
    └── Child: Evidence Pack Generation
```

### Continue-As-New

For long-running workflows that exceed history limits:

```
if workflow.history_length > 10000:
    workflow.continue_as_new(current_state)
```

---

## Related Documents

- `docs/03-platform/track-assurance.md` — Drift detection and review checkpoints
- `docs/03-platform/legacy-rebuild.md` — Legacy rebuild workflow patterns
- `docs/06-operations/finops-token-budgets.md` — Budget configuration
- `docs/06-operations/incident-response.md` — Incident workflows
- `docs/06-operations/itqahn-continuous-improvement.md` — Self-improvement workflow
- `docs/07-integrations/git-integration.md` — Parallel work and worktree coordination
- `docs/08-agents/agent-system-contract.md` — Agent workflow rules

---

**Version**: 2.4.0 | **Date**: 2026-01-08
