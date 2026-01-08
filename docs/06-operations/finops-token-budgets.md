# FinOps and Token Budgets

Cost is a reliability metric in Itqahn. Autonomous systems can burn budgets rapidly, so cost controls are mandatory.

---

## Why This Is Required

Autonomous systems can exhaust budgets through:

| Failure Mode | Impact |
|--------------|--------|
| Infinite loops | Unbounded token consumption |
| Large context windows | Expensive per-request |
| Redundant research | Repeated similar queries |
| Runaway environment creation | Cloud cost explosion |
| Retry storms | Multiplied API costs |

**Therefore, cost controls are reliability controls.**

---

## Budget Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUDGET HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    ORG LEVEL                             │    │
│  │              Global spend limits                         │    │
│  │               Monthly cap: $X                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                 │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ TENANT A     │  │ TENANT B     │  │ TENANT C     │          │
│  │ Monthly: $Y  │  │ Monthly: $Y  │  │ Monthly: $Y  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    WORKFLOW LEVEL                         │  │
│  │    Each workflow has per-phase budget allocation          │  │
│  │    Concept: $A | Experience: $B | RC: $C | Post: $D      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Budget Levels

| Level | Scope | Default | Override |
|-------|-------|---------|----------|
| **Org** | Global | Varies | Executive approval |
| **Tenant** | Per-customer | $5,000/month | Account manager |
| **Workflow** | Per-request | $100 | Product owner |
| **Phase** | Per-gate | Workflow/4 | Automatic |
| **Activity** | Per-step | Phase/10 | None |

---

## Circuit Breakers

### Mandatory Circuit Breakers

| Breaker | Threshold | Action |
|---------|-----------|--------|
| Max turns per stage | 50 | Pause, require approval |
| Max retries per activity | 5 | Fail activity, escalate |
| Max tokens per activity | 100,000 | Fail activity |
| Max tokens per workflow | 1,000,000 | Pause workflow |
| Max environment-hours | 24h | Terminate environments |
| Spend velocity | >$10/min | Alert, pause if sustained |

### Circuit Breaker Configuration

```yaml
circuit_breakers:
  workflow:
    max_tokens: 1000000
    max_cost_usd: 100
    max_duration_hours: 72
    max_turns: 200

  phase:
    concept:
      max_tokens: 100000
      max_turns: 30
    experience:
      max_tokens: 200000
      max_turns: 50
    rc:
      max_tokens: 500000
      max_turns: 100
    post_launch:
      max_tokens: 200000
      max_turns: 20

  activity:
    max_tokens: 50000
    max_retries: 5
    timeout_seconds: 300
```

---

## Cost Tracking

### Per-Activity Tracking

```json
{
  "activity_id": "act-abc123",
  "workflow_id": "wf-xyz789",
  "agent_id": "backend-builder",
  "model": "claude-3-opus",
  "tokens": {
    "input": 5000,
    "output": 2000,
    "total": 7000
  },
  "cost_usd": 0.21,
  "duration_ms": 15000,
  "timestamp": "2026-01-06T12:00:00Z"
}
```

### Per-Workflow Summary

```json
{
  "workflow_id": "wf-xyz789",
  "tenant_id": "tenant-abc",
  "status": "completed",
  "budget": {
    "allocated_usd": 100,
    "consumed_usd": 45.67,
    "remaining_usd": 54.33,
    "utilization": 0.4567
  },
  "tokens": {
    "total": 456789,
    "by_phase": {
      "concept": 50000,
      "experience": 150000,
      "rc": 200000,
      "post_launch": 56789
    },
    "by_model": {
      "claude-3-opus": 300000,
      "claude-3-sonnet": 156789
    }
  },
  "cloud_cost_usd": 12.34,
  "total_cost_usd": 58.01
}
```

---

## Required Dashboards

### Token Spend Dashboard

| Metric | Visualization |
|--------|---------------|
| Token spend per workflow | Time series |
| Token spend per agent | Bar chart |
| Cost per feature shipped | Trend line |
| Cost per tenant | Table with alerts |
| Top cost anomalies | Alert list |

### Cost Anomaly Detection

```yaml
anomaly_detection:
  metrics:
    - name: token_spend_rate
      threshold_stddev: 3
      window: 1h
      action: alert

    - name: cloud_cost_rate
      threshold_stddev: 3
      window: 1h
      action: alert

    - name: environment_count
      threshold_absolute: 10
      action: alert_and_cleanup
```

---

## Budget Enforcement

### Orchestrator Enforcement

```python
async def execute_activity(activity: Activity) -> Result:
    # Check budget before execution
    remaining = await get_remaining_budget(activity.workflow_id)

    if remaining <= 0:
        return Result.budget_exhausted(
            "Workflow budget exhausted. Request extension."
        )

    # Estimate cost
    estimated = estimate_activity_cost(activity)

    if estimated > remaining:
        return Result.budget_exceeded(
            f"Estimated cost ${estimated} exceeds remaining ${remaining}"
        )

    # Execute with tracking
    result = await execute_with_tracking(activity)

    # Update budget
    await deduct_from_budget(activity.workflow_id, result.actual_cost)

    return result
```

### Policy Enforcement

```rego
# policies/opa/finops/budget_caps.rego
package finops

deny[msg] {
  input.workflow.cost_usd > input.workflow.budget_usd
  msg := sprintf("Workflow %v exceeded budget: $%v > $%v",
    [input.workflow.id, input.workflow.cost_usd, input.workflow.budget_usd])
}

deny[msg] {
  input.tenant.monthly_cost_usd > input.tenant.monthly_budget_usd
  msg := sprintf("Tenant %v exceeded monthly budget",
    [input.tenant.id])
}
```

---

## Budget Extension Process

```
1. Workflow pauses at budget limit
       │
       ▼
2. Notification sent to workflow owner
       │
       ▼
3. Owner reviews spend breakdown
       │
       ├── Approve extension
       │       │
       │       ▼
       │   Budget increased
       │   Workflow resumes
       │
       └── Deny extension
               │
               ▼
           Workflow cancelled
           Resources cleaned up
```

### Extension Request

```json
{
  "request_type": "budget_extension",
  "workflow_id": "wf-xyz789",
  "current_budget_usd": 100,
  "consumed_usd": 100,
  "requested_extension_usd": 50,
  "justification": "Feature requires additional research phase",
  "approver": "product-owner@example.com"
}
```

---

## Cost Optimization

### Model Selection

| Task Complexity | Recommended Model | Cost Factor |
|-----------------|-------------------|-------------|
| Simple generation | Claude 3 Haiku | 1x |
| Standard tasks | Claude 3 Sonnet | 3x |
| Complex reasoning | Claude 3 Opus | 15x |

### Caching Strategy

- Cache embeddings (reuse for similar queries)
- Cache frequent API responses
- Use RAG to avoid re-generating known content

### Resource Cleanup

```yaml
# TTL enforcement
cleanup:
  ephemeral_environments:
    ttl_hours: 4
    warning_at: 3h

  preview_deployments:
    ttl_days: 7
    warning_at: 5d

  test_resources:
    ttl_hours: 2
    cleanup_on_workflow_complete: true
```

---

## Agents

| Agent | Responsibility |
|-------|----------------|
| **CFO FinOps** | Overall budget governance |
| **Token Budget Enforcer** | Real-time budget enforcement |
| **Cloud Cost Optimizer** | Cloud spend optimization |
| **Denial of Wallet Detector** | Anomaly detection |
| **Janitor TTL Reaper** | Resource cleanup |

---

## Related Documents

- `docs/02-architecture/workflow-architecture.md` — Budget in workflows
- `agents/11-finops-and-cost-control/` — FinOps agents
- `policies/opa/finops/` — Budget policies

---

**Version**: 2.0.0 | **Date**: 2026-01-06
