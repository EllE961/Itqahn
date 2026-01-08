# Webhooks and Events

Itqahn uses webhooks and events for integrations. This document defines the event taxonomy, security requirements, and operational patterns.

---

## Event Taxonomy

### Workflow Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `workflow.created` | New workflow started | Workflow ID, type, owner |
| `workflow.phase_changed` | Gate passed | Workflow ID, old phase, new phase |
| `workflow.completed` | Workflow finished | Workflow ID, status, evidence |
| `workflow.failed` | Workflow failed | Workflow ID, error, last activity |
| `workflow.paused` | Budget/approval needed | Workflow ID, reason |

### Build Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `build.started` | CI job started | Build ID, commit, branch |
| `build.completed` | CI job finished | Build ID, status, artifacts |
| `build.failed` | CI job failed | Build ID, error, logs link |
| `evidence.created` | Evidence Pack generated | Evidence ID, manifest URL |

### Deployment Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `deploy.started` | Deployment began | Deploy ID, service, version |
| `deploy.canary_progressed` | Canary phase changed | Deploy ID, weight, metrics |
| `deploy.completed` | Deployment finished | Deploy ID, status |
| `deploy.rolled_back` | Rollback executed | Deploy ID, reason, previous |

### Approval Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `approval.requested` | Approval needed | Request ID, type, requester |
| `approval.granted` | Approval given | Request ID, approver |
| `approval.denied` | Approval denied | Request ID, approver, reason |

### Incident Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `incident.declared` | Incident opened | Incident ID, severity, service |
| `incident.updated` | Status changed | Incident ID, old status, new status |
| `incident.resolved` | Incident closed | Incident ID, duration, impact |

### GitHub Automation Events

Events specific to the GitHub Automation Program in Operator Mode.

| Event | Trigger | Payload |
|-------|---------|---------|
| `github.issue.created` | Issue created by automation | Issue ID, type (epic/work-item), run ID |
| `github.branch.created` | Branch created for work item | Branch name, run ID, issue ID |
| `github.commit.pushed` | Commit pushed | Commit SHA, run ID, issue ID, message |
| `github.pr.created` | PR created by automation | PR number, run ID, issue ID |
| `github.pr.checks_passed` | All required checks passed | PR number, check results |
| `github.pr.checks_failed` | One or more checks failed | PR number, failed checks, auto-fix status |
| `github.pr.auto_merge_enabled` | Auto-merge activated | PR number, conditions |
| `github.pr.queued` | PR entered merge queue | PR number, queue position |
| `github.pr.merged` | PR merged via queue | PR number, merge SHA, run ID |
| `github.pr.conflict` | Merge conflict detected | PR number, conflicting files, remediation |
| `github.release.created` | Release created | Tag, release URL, evidence pack URL |

### Operator Mode Events

Events specific to Operator Mode execution.

| Event | Trigger | Payload |
|-------|---------|---------|
| `operator.run.started` | Operator Mode run started | Run ID, project, concept lock version |
| `operator.run.phase_changed` | Run phase progressed | Run ID, old phase, new phase |
| `operator.run.completed` | Run finished successfully | Run ID, PRs created, evidence pack |
| `operator.run.failed` | Run failed | Run ID, error, last phase, remediation |
| `operator.run.paused` | Run paused (budget/error) | Run ID, reason, resume conditions |
| `operator.worker.allocated` | Worker allocated to run | Run ID, worker ID, capacity |
| `operator.worker.released` | Worker released | Run ID, worker ID, duration |
| `operator.kill_switch.activated` | Kill switch triggered | Reason, stopped runs, timestamp |
| `operator.kill_switch.released` | Kill switch deactivated | Reason, resumed runs |
| `operator.auto_fix.started` | Auto-remediation started | Run ID, failure type, attempt |
| `operator.auto_fix.succeeded` | Auto-remediation succeeded | Run ID, failure type, resolution |
| `operator.auto_fix.failed` | Auto-remediation failed | Run ID, failure type, escalation |
| `operator.cost.threshold` | Cost threshold reached | Run ID, current cost, threshold, action |

### CI/Pipeline Events

Events from CI pipelines triggered by GitHub Automation.

| Event | Trigger | Payload |
|-------|---------|---------|
| `ci.check.started` | CI check started | Check name, PR number, commit SHA |
| `ci.check.completed` | CI check finished | Check name, status, duration, summary |
| `ci.lint.violation` | Lint violation detected | Files, rules, auto-fixable |
| `ci.test.failure` | Test failed | Test name, file, error, flaky status |
| `ci.test.quarantined` | Test quarantined as flaky | Test name, failure history |
| `ci.security.finding` | Security finding detected | Severity, tool, location, remediation |
| `ci.design_jail.violation` | Design Jail violation | Component, token, violation type |
| `ci.asset.drift` | Asset drift detected | Asset ID, drift score, threshold |
| `ci.evidence.generated` | Evidence Pack generated | Evidence ID, manifest URL, signature |
| `ci.merge_queue.check_started` | Queue branch check started | Queue branch, PRs included |
| `ci.merge_queue.check_completed` | Queue branch check finished | Status, merged PRs, ejected PRs |

---

## Webhook Security

### Signature Verification

All webhooks are signed using HMAC-SHA256:

```
X-Itqahn-Signature: sha256=abc123...
X-Itqahn-Timestamp: 1704542400
X-Itqahn-Event: workflow.completed
```

### Verification Code

```python
import hmac
import hashlib
import time

def verify_webhook(
    payload: bytes,
    signature: str,
    timestamp: str,
    secret: str
) -> bool:
    # Check timestamp freshness (5 minute window)
    if abs(time.time() - int(timestamp)) > 300:
        return False

    # Compute expected signature
    message = f"{timestamp}.{payload.decode()}"
    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| HTTPS only | TLS 1.2+ required |
| Signature verification | HMAC-SHA256 |
| Timestamp validation | 5-minute window |
| IP allowlisting | Optional |
| Secret rotation | Every 90 days |

---

## Retry Policy

### Retry Configuration

```yaml
webhooks:
  retry:
    max_attempts: 5
    initial_interval: 1s
    max_interval: 60s
    backoff_multiplier: 2
    retryable_status_codes:
      - 408  # Request Timeout
      - 429  # Too Many Requests
      - 500  # Internal Server Error
      - 502  # Bad Gateway
      - 503  # Service Unavailable
      - 504  # Gateway Timeout
```

### Retry Schedule

| Attempt | Delay | Cumulative |
|---------|-------|------------|
| 1 | Immediate | 0s |
| 2 | 1s | 1s |
| 3 | 2s | 3s |
| 4 | 4s | 7s |
| 5 | 8s | 15s |

After max attempts, event goes to dead letter queue.

---

## Idempotency

### Idempotency Keys

Every webhook includes:

```
X-Itqahn-Delivery-ID: dlv-abc123
```

Receivers should:
1. Store processed delivery IDs
2. Check before processing
3. Return 200 if already processed

### Implementation

```python
async def handle_webhook(request: Request) -> Response:
    delivery_id = request.headers.get("X-Itqahn-Delivery-ID")

    # Check if already processed
    if await is_processed(delivery_id):
        return Response(status_code=200, body="Already processed")

    # Verify signature
    if not verify_webhook(...):
        return Response(status_code=401, body="Invalid signature")

    # Process event
    try:
        await process_event(request.json())
        await mark_processed(delivery_id)
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500, body=str(e))
```

---

## Webhook Configuration

### Registration

```yaml
# Webhook subscription
webhooks:
  - url: "https://example.com/webhooks/itqahn"
    secret: "${WEBHOOK_SECRET}"
    events:
      - "workflow.*"
      - "deploy.*"
      - "incident.*"
    active: true
    content_type: "application/json"
```

### Event Filtering

```yaml
# Subscribe to specific events only
webhooks:
  - url: "https://slack.example.com/webhook"
    events:
      - "incident.declared"
      - "incident.resolved"
    filter:
      severity:
        - P0
        - P1

  - url: "https://jira.example.com/webhook"
    events:
      - "workflow.completed"
    filter:
      compliance_tier:
        - sensitive
        - regulated
```

---

## Event Payload Format

### Standard Envelope

```json
{
  "id": "evt-abc123",
  "type": "workflow.completed",
  "timestamp": "2026-01-06T12:00:00Z",
  "source": "itqahn.io/workflows",
  "subject": "wf-xyz789",
  "data": {
    "workflow_id": "wf-xyz789",
    "status": "completed",
    "evidence_pack": "s3://evidence/..."
  },
  "metadata": {
    "tenant_id": "tenant-abc",
    "correlation_id": "corr-def456"
  }
}
```

### CloudEvents Compatibility

Events follow CloudEvents spec:

```json
{
  "specversion": "1.0",
  "type": "io.itqahn.workflow.completed",
  "source": "https://itqahn.io/workflows",
  "id": "evt-abc123",
  "time": "2026-01-06T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {...}
}
```

---

## Internal Event Bus

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Producer   │───▶│   Kafka     │───▶│  Consumer   │
│  (Service)  │    │   Topic     │    │  (Service)  │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Webhook    │
                   │  Dispatcher │
                   └─────────────┘
```

### Topic Naming

```
itqahn.{domain}.{event_type}

Examples:
- itqahn.workflows.created
- itqahn.builds.completed
- itqahn.incidents.declared
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `webhook_deliveries_total` | Total delivery attempts |
| `webhook_deliveries_success` | Successful deliveries |
| `webhook_deliveries_failed` | Failed deliveries |
| `webhook_delivery_latency` | Delivery latency |
| `webhook_retry_count` | Retry attempts |

### Alerting

```yaml
alerts:
  - name: webhook_delivery_failure_rate
    condition: rate(webhook_deliveries_failed[5m]) > 0.1
    severity: warning

  - name: webhook_dlq_growing
    condition: webhook_dlq_size > 100
    severity: critical
```

---

## Related Documents

- `docs/00-overview/principles.md` — Operator Mode audit principles
- `docs/03-platform/portal-webapp.md` — Operator Mode dashboard
- `docs/06-operations/incident-response.md` — Incident events and Kill Switch
- `docs/06-operations/runbooks.md` — Operator Mode failure runbooks
- `docs/07-integrations/git-integration.md` — GitHub Automation Program
- `docs/07-integrations/mcp/mcp-github.md` — GitHub MCP and webhooks
- `docs/07-integrations/mcp/mcp-jira.md` — Jira integration

---

**Version**: 2.3.0 | **Date**: 2026-01-08
