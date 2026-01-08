# SRE Model

Itqahn follows Site Reliability Engineering practices for operating production systems.

---

## Observability Baseline

Every service must emit:

| Signal | Format | Requirements |
|--------|--------|--------------|
| **Logs** | Structured JSON | Correlation IDs, severity levels |
| **Metrics** | Prometheus | RED/USE metrics |
| **Traces** | OpenTelemetry | Distributed tracing |

### Logging Standard

```json
{
  "timestamp": "2026-01-06T12:00:00.000Z",
  "level": "INFO",
  "service": "user-service",
  "version": "1.2.3",
  "trace_id": "abc123",
  "span_id": "def456",
  "correlation_id": "req-xyz789",
  "message": "User authenticated",
  "context": {
    "user_id": "usr-123",
    "method": "oidc"
  }
}
```

### Metrics Standard (RED)

| Metric | Type | Labels |
|--------|------|--------|
| `requests_total` | Counter | service, endpoint, status |
| `request_duration_seconds` | Histogram | service, endpoint |
| `errors_total` | Counter | service, endpoint, error_type |

### Tracing Standard

```yaml
# OpenTelemetry configuration
exporters:
  otlp:
    endpoint: "otel-collector:4317"

processors:
  batch:
    timeout: 1s

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

---

## SLO Framework

### Default SLOs

| SLO | Target | Measurement Window |
|-----|--------|-------------------|
| Availability | 99.9% | 30 days |
| p99 Latency | < 500ms | 30 days |
| Error Rate | < 0.1% | 30 days |

### SLO Definition

```yaml
# templates/ops/SLO.md format
slos:
  - name: availability
    description: "Service responds successfully to requests"
    sli:
      type: request_success_rate
      metric: |
        sum(rate(requests_total{status!~"5.."}[5m])) /
        sum(rate(requests_total[5m]))
    target: 0.999
    window: 30d
    alerting:
      burn_rate_short: 14.4  # 2% of budget in 1h
      burn_rate_long: 6.0    # 5% of budget in 6h

  - name: latency
    description: "99th percentile request latency"
    sli:
      type: latency_percentile
      percentile: 99
      metric: |
        histogram_quantile(0.99,
          sum(rate(request_duration_seconds_bucket[5m]))
          by (le)
        )
    target: 0.5  # 500ms
    window: 30d
```

### Error Budgets

```
Error Budget = 1 - SLO Target

For 99.9% availability:
- Error budget = 0.1%
- Monthly budget = 43.2 minutes of downtime
- Daily budget = 1.44 minutes
```

**When error budget is exhausted:**
1. Feature freeze activated
2. Reliability-only work prioritized
3. Root cause analysis required
4. Executive review before resuming features

---

## On-Call Model

### Ownership Requirements

| Requirement | Implementation |
|-------------|----------------|
| Service owner | Defined in `catalog-info.yaml` |
| Escalation policy | PagerDuty/OpsGenie configured |
| Runbooks | Current and linked |
| Contact info | Updated in service catalog |

### Escalation Tiers

| Tier | Response Time | Escalation Path |
|------|---------------|-----------------|
| T1 | 5 min (P0/P1) | Primary on-call |
| T2 | 15 min | Secondary on-call |
| T3 | 30 min | Team lead |
| T4 | 1 hour | Engineering director |

### On-Call Handoff

```markdown
# On-Call Handoff Template

## Current Incidents
- None active

## Ongoing Issues
- Issue X: monitoring, expected resolution by Y

## Recent Changes
- Deploy user-service 1.2.3 on 2026-01-06

## Upcoming Risks
- Maintenance window scheduled for 2026-01-08

## Notes for Next Shift
- Watch metric X after recent deploy
```

---

## Alert Philosophy

### Alert Criteria

Only alert when:
- Human action is required
- The issue affects users or will soon
- There is a runbook to follow

Never alert for:
- Informational events (use dashboards)
- Self-healing conditions
- Low-priority non-actionable issues

### Alert Routing

```yaml
# PagerDuty routing
routes:
  - match:
      severity: critical
    receiver: pagerduty-critical

  - match:
      severity: warning
    receiver: slack-ops

  - match_re:
      service: user-service
    receiver: identity-team
```

---

## Deployment Safety

### Canary Releases

```yaml
# Argo Rollouts strategy
strategy:
  canary:
    steps:
      - setWeight: 5
      - pause: {duration: 5m}
      - analysis:
          templates:
            - templateName: success-rate
      - setWeight: 25
      - pause: {duration: 10m}
      - analysis:
          templates:
            - templateName: success-rate
      - setWeight: 50
      - pause: {duration: 15m}
      - setWeight: 100
```

### Automatic Rollback

Triggers:
- SLO regression during canary
- Error rate increase > 50%
- p99 latency increase > 100%
- Failed health checks

### Post-Launch Verification

Gate 4 requirements:
- SLO baseline validated (7 days)
- Error budget policy active
- Feedback loop operational
- No critical incidents

---

## Dashboards

### Required Dashboards

| Dashboard | Contents |
|-----------|----------|
| Service overview | SLOs, traffic, errors, latency |
| Infrastructure | CPU, memory, network, disk |
| Dependencies | Downstream service health |
| Business metrics | Feature usage, conversions |

### Dashboard Linking

```yaml
# Service catalog annotation
annotations:
  grafana/dashboard: "https://grafana.example.com/d/user-service"
  grafana/on-call: "https://grafana.example.com/d/on-call"
```

---

## Related Documents

- `docs/06-operations/incident-response.md` — Incident handling
- `docs/06-operations/runbooks.md` — Operational procedures
- `templates/ops/SLO.md` — SLO template

---

**Version**: 2.0.0 | **Date**: 2026-01-06
