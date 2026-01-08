# Auto-Remediation

The Auto-Remediation Bot can execute certain runbook actions automatically. This document defines what is allowed and what is forbidden.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  AUTO-REMEDIATION FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │  Alert  │───▶│ Evaluate│───▶│ Execute │───▶│ Verify  │      │
│  │ Fires   │    │ Runbook │    │ Action  │    │ Success │      │
│  └─────────┘    └────┬────┘    └────┬────┘    └────┬────┘      │
│                      │              │              │            │
│                      ▼              ▼              ▼            │
│               ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│               │ Allowed? │   │  Audit   │   │ Resolved?│       │
│               │          │   │   Log    │   │          │       │
│               └────┬─────┘   └──────────┘   └────┬─────┘       │
│                    │                             │              │
│              ┌─────┴─────┐                 ┌─────┴─────┐       │
│              │           │                 │           │       │
│             Yes         No               Yes         No        │
│              │           │                 │           │       │
│              ▼           ▼                 ▼           ▼       │
│         Execute     Escalate           Resolve    Escalate     │
│                     to Human                      to Human     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Allowed Actions

The Auto-Remediation Bot MAY perform:

### Pod/Deployment Operations

| Action | Condition | Limit |
|--------|-----------|-------|
| Restart pods | CrashLoopBackOff, unhealthy | Max 3 times per hour |
| Scale replicas up | CPU/memory pressure | Max 2x current |
| Scale replicas down | Over-provisioned | Min 2 replicas |
| Rollout restart | Deployment stuck | Max 1 per deployment per hour |

### Cache/State Operations

| Action | Condition | Limit |
|--------|-----------|-------|
| Clear cache | Cache corruption detected | Once per incident |
| Flush queue | Dead letter queue growing | Requires human confirmation |
| Reset circuit breaker | After cooldown period | Automatic |

### Network Operations

| Action | Condition | Limit |
|--------|-----------|-------|
| Refresh DNS | DNS resolution failures | Once per hour |
| Restart sidecar | Envoy unhealthy | Max 3 times per hour |

### Credential Operations

| Action | Condition | Limit |
|--------|-----------|-------|
| Rotate dynamic secrets | Near expiry | Automatic |
| Refresh service token | Token rejected | Max 3 times per hour |

---

## Forbidden Actions

The Auto-Remediation Bot MUST NOT perform:

### Data Operations

| Forbidden | Reason |
|-----------|--------|
| Delete database records | Irreversible data loss |
| Modify production data | Requires human verification |
| Truncate tables | Irreversible |
| Drop indexes | Performance impact uncertain |

### Security Operations

| Forbidden | Reason |
|-----------|--------|
| Grant access | Security decision |
| Revoke access | May break legitimate users |
| Modify security policies | Governance requirement |
| Disable security controls | Creates vulnerability |

### Deployment Operations

| Forbidden | Reason |
|-----------|--------|
| Deploy new code | Requires approval |
| Rollback to unverified version | May introduce bugs |
| Modify environment variables | Configuration change |
| Change resource limits | Capacity planning decision |

### Cross-Tenant Operations

| Forbidden | Reason |
|-----------|--------|
| Actions affecting other tenants | Blast radius |
| Shared resource modifications | Impact assessment needed |
| Global configuration changes | Wide impact |

---

## Decision Matrix

```python
def can_auto_remediate(action: Action) -> tuple[bool, str]:
    # Check action type
    if action.type in FORBIDDEN_TYPES:
        return False, "Action type forbidden"

    # Check reversibility
    if not action.is_reversible():
        return False, "Action is not reversible"

    # Check verification
    if not action.has_verification_criteria():
        return False, "No verification criteria"

    # Check blast radius
    if action.blast_radius > ALLOWED_BLAST_RADIUS:
        return False, "Blast radius too large"

    # Check rate limits
    if action.exceeds_rate_limit():
        return False, "Rate limit exceeded"

    # Check runbook exists
    if not action.has_runbook():
        return False, "No runbook for action"

    return True, "Allowed"
```

---

## Rate Limits

| Action Category | Limit | Window |
|-----------------|-------|--------|
| Pod restarts | 3 per pod | 1 hour |
| Deployment restarts | 1 per deployment | 1 hour |
| Scale operations | 2 per deployment | 1 hour |
| Cache clears | 1 per service | 1 hour |
| Total actions | 10 per service | 1 hour |

---

## Audit Logging

Every auto-remediation action is logged:

```json
{
  "event_type": "auto_remediation",
  "timestamp": "2026-01-06T12:00:00Z",
  "action": {
    "type": "pod_restart",
    "target": "user-service/pod-abc123",
    "reason": "CrashLoopBackOff detected"
  },
  "trigger": {
    "alert_id": "alert-xyz789",
    "runbook": "runbooks/services/user-service/pod-crash-loop.md"
  },
  "decision": {
    "allowed": true,
    "evaluation": [
      {"check": "reversible", "result": "pass"},
      {"check": "rate_limit", "result": "pass"},
      {"check": "blast_radius", "result": "pass"}
    ]
  },
  "result": {
    "status": "success",
    "verification": "pod_healthy_after_restart",
    "duration_ms": 45000
  }
}
```

---

## Escalation Triggers

Escalate to human when:

| Condition | Escalation |
|-----------|------------|
| Action not allowed | Page on-call |
| Rate limit exceeded | Page on-call |
| Action failed | Page on-call |
| Verification failed | Page on-call |
| Multiple services affected | Page on-call + team lead |
| Security-related alert | Page security on-call |

### Escalation Message

```
Auto-remediation escalation

Alert: user-service-error-rate
Attempted action: pod_restart
Result: FAILED

Reason: Rate limit exceeded (3 restarts in last hour)

Runbook: https://docs.example.com/runbooks/user-service/high-error-rate

Action required: Manual investigation needed.
```

---

## Configuration

```yaml
# auto-remediation config
auto_remediation:
  enabled: true

  allowed_actions:
    - type: pod_restart
      max_per_hour: 3
    - type: deployment_restart
      max_per_hour: 1
    - type: scale_up
      max_multiplier: 2
    - type: cache_clear
      requires_confirmation: false

  forbidden_actions:
    - type: data_delete
    - type: security_modify
    - type: deploy_new_version

  escalation:
    on_failure: page_oncall
    on_rate_limit: page_oncall
    channels:
      - slack: "#ops-alerts"
      - pagerduty: "auto-remediation"
```

---

## Related Documents

- `docs/06-operations/runbooks.md` — Runbook standards
- `docs/06-operations/incident-response.md` — Incident handling
- `agents/09-sre-and-ops/auto-remediation-bot.md` — Bot agent

---

**Version**: 2.0.0 | **Date**: 2026-01-06
