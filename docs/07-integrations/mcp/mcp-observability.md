# MCP Observability Integration

The Observability MCP provides access to metrics, logs, traces, and SLO status for monitoring and incident response.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY MCP FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│   Obs MCP   │───▶│ Observability│             │
│  │         │    │             │    │   Stack      │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │ Metrics  │  │   Logs   │  │     Traces      │              │
│  │(Prometheus)│ │(Loki)   │  │    (Tempo)      │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Backend |
|-----------|-------------|---------|
| `metrics.query` | Query metrics | Prometheus |
| `metrics.range` | Range query | Prometheus |
| `metrics.series` | List series | Prometheus |
| `logs.query` | Query logs | Loki |
| `logs.stream` | Stream logs | Loki |
| `traces.get` | Get trace by ID | Tempo |
| `traces.search` | Search traces | Tempo |
| `slo.status` | SLO burn rate | SLO engine |
| `alert.list` | List active alerts | Alertmanager |
| `alert.silence` | Silence alert | Alertmanager |
| `incident.list` | List incidents | Incident system |
| `dashboard.get` | Get dashboard | Grafana |

---

## Authentication

### SPIFFE Identity

```yaml
observability:
  auth:
    method: spiffe
    trust_domain: itqahn.io
```

### Service Account

```yaml
observability:
  auth:
    method: service_account
    prometheus_token_source: vault
    prometheus_token_path: kv/mcp/observability/prometheus
    loki_token_source: vault
    loki_token_path: kv/mcp/observability/loki
```

---

## Operations

### Query Metrics (Instant)

```json
{
  "operation": "metrics.query",
  "params": {
    "query": "sum(rate(http_requests_total{service=\"user-service\"}[5m]))",
    "time": "2026-01-06T12:00:00Z"
  }
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {},
        "value": [1704542400, "125.5"]
      }
    ]
  }
}
```

### Query Metrics (Range)

```json
{
  "operation": "metrics.range",
  "params": {
    "query": "rate(http_requests_total{service=\"user-service\"}[5m])",
    "start": "2026-01-06T11:00:00Z",
    "end": "2026-01-06T12:00:00Z",
    "step": "1m"
  }
}
```

### Query Logs

```json
{
  "operation": "logs.query",
  "params": {
    "query": "{service=\"user-service\"} |= \"error\"",
    "start": "2026-01-06T11:00:00Z",
    "end": "2026-01-06T12:00:00Z",
    "limit": 100
  }
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "result": [
      {
        "stream": {
          "service": "user-service",
          "level": "error"
        },
        "values": [
          ["1704542400000000000", "Error processing request: connection refused"]
        ]
      }
    ]
  }
}
```

### Get Trace

```json
{
  "operation": "traces.get",
  "params": {
    "trace_id": "abc123def456"
  }
}
```

Response:
```json
{
  "trace_id": "abc123def456",
  "spans": [
    {
      "span_id": "span-1",
      "operation_name": "HTTP GET /api/users",
      "service": "user-service",
      "duration_ms": 150,
      "status": "OK"
    },
    {
      "span_id": "span-2",
      "parent_span_id": "span-1",
      "operation_name": "PostgreSQL SELECT",
      "service": "user-service",
      "duration_ms": 45,
      "status": "OK"
    }
  ]
}
```

### Search Traces

```json
{
  "operation": "traces.search",
  "params": {
    "service": "user-service",
    "operation": "HTTP POST /api/login",
    "min_duration_ms": 500,
    "start": "2026-01-06T11:00:00Z",
    "end": "2026-01-06T12:00:00Z",
    "limit": 20
  }
}
```

### Get SLO Status

```json
{
  "operation": "slo.status",
  "params": {
    "service": "user-service",
    "slo_name": "availability"
  }
}
```

Response:
```json
{
  "service": "user-service",
  "slo_name": "availability",
  "target": 0.999,
  "current": 0.9995,
  "error_budget": {
    "total_minutes": 43.2,
    "consumed_minutes": 21.6,
    "remaining_percent": 50.0
  },
  "burn_rate": {
    "1h": 0.5,
    "6h": 0.8,
    "24h": 0.6
  },
  "status": "healthy"
}
```

### List Active Alerts

```json
{
  "operation": "alert.list",
  "params": {
    "filter": {
      "service": "user-service",
      "severity": ["critical", "warning"]
    },
    "state": "firing"
  }
}
```

Response:
```json
{
  "alerts": [
    {
      "name": "HighErrorRate",
      "service": "user-service",
      "severity": "warning",
      "state": "firing",
      "started_at": "2026-01-06T11:45:00Z",
      "labels": {
        "service": "user-service",
        "environment": "production"
      },
      "annotations": {
        "summary": "Error rate > 1% for 5 minutes",
        "runbook": "https://runbooks.itqahn.io/user-service/high-error-rate"
      }
    }
  ]
}
```

### Silence Alert

```json
{
  "operation": "alert.silence",
  "params": {
    "matchers": [
      {"name": "alertname", "value": "HighErrorRate"},
      {"name": "service", "value": "user-service"}
    ],
    "duration": "1h",
    "comment": "Known issue, fix deploying",
    "created_by": "sre-operator"
  }
}
```

---

## Pre-Built Queries

### Common Queries

| Query Name | PromQL |
|------------|--------|
| Error Rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` |
| P99 Latency | `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| Request Rate | `sum(rate(http_requests_total[5m]))` |
| CPU Usage | `avg(rate(container_cpu_usage_seconds_total[5m])) by (pod)` |
| Memory Usage | `avg(container_memory_working_set_bytes) by (pod)` |

### Service Health Query

```json
{
  "operation": "metrics.query",
  "params": {
    "preset": "service_health",
    "service": "user-service"
  }
}
```

Returns combined health metrics:
```json
{
  "service": "user-service",
  "health": {
    "error_rate": 0.001,
    "p99_latency_ms": 150,
    "request_rate": 1250,
    "slo_status": "healthy",
    "active_alerts": 0
  }
}
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  observability:
    enabled: true

    prometheus:
      url: "https://prometheus.itqahn.io"
      auth:
        method: bearer
        token_source: vault
        token_path: kv/mcp/observability/prometheus

    loki:
      url: "https://loki.itqahn.io"
      auth:
        method: bearer
        token_source: vault
        token_path: kv/mcp/observability/loki

    tempo:
      url: "https://tempo.itqahn.io"
      auth:
        method: bearer
        token_source: vault
        token_path: kv/mcp/observability/tempo

    alertmanager:
      url: "https://alertmanager.itqahn.io"
      auth:
        method: bearer
        token_source: vault
        token_path: kv/mcp/observability/alertmanager

    grafana:
      url: "https://grafana.itqahn.io"
      auth:
        method: api_key
        token_source: vault
        token_path: kv/mcp/observability/grafana

    rate_limits:
      queries_per_minute: 100
      log_bytes_per_request: 10MB

    defaults:
      max_range: 7d
      max_results: 10000
      timeout_seconds: 30
```

### Allowlist Entry

```yaml
roles:
  backend-builder:
    mcps:
      observability:
        operations:
          - metrics.query
          - metrics.range
          - logs.query
          - traces.search
          - slo.status
          - alert.list
        constraints:
          services: ["*"]
          max_range: "24h"

  sre-operator:
    mcps:
      observability:
        operations:
          - metrics.query
          - metrics.range
          - logs.query
          - logs.stream
          - traces.get
          - traces.search
          - slo.status
          - alert.list
          - alert.silence
          - incident.list
          - dashboard.get
        constraints:
          services: ["*"]
          max_range: "30d"
          can_silence: true
```

---

## Query Safety

### Query Limits

| Limit | Default | Maximum |
|-------|---------|---------|
| Time range | 24h | 30d |
| Data points | 10,000 | 100,000 |
| Log lines | 1,000 | 10,000 |
| Query timeout | 30s | 120s |
| Log bytes | 10MB | 100MB |

### Dangerous Query Detection

```yaml
observability:
  query_safety:
    block_patterns:
      - ".*without\\s*\\(.*\\).*"  # Aggregation without labels
      - ".*\\{\\}.*"               # Empty label selector
    warn_patterns:
      - ".*\\[30d\\].*"            # Long range
      - ".*count\\(.*\\).*"        # High cardinality
```

### Query Validation

```json
{
  "operation": "metrics.query",
  "params": {
    "query": "sum(rate(http_requests_total{}[5m]))"
  }
}
```

Response (rejected):
```json
{
  "error": "QUERY_REJECTED",
  "message": "Empty label selector not allowed",
  "suggestion": "Add service label: sum(rate(http_requests_total{service=\"...\"}[5m]))"
}
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `OBS_AUTH_FAILED` | Authentication failed | Refresh token |
| `OBS_QUERY_TIMEOUT` | Query timeout | Reduce range/complexity |
| `OBS_QUERY_REJECTED` | Query not allowed | Fix query |
| `OBS_RATE_LIMITED` | Rate limit exceeded | Back off |
| `OBS_DATA_TOO_LARGE` | Response too large | Add filters |

### Retry Configuration

```yaml
observability:
  retry:
    max_attempts: 3
    initial_delay_ms: 500
    retry_on:
      - OBS_QUERY_TIMEOUT
      - OBS_RATE_LIMITED
```

---

## Incident Integration

### Auto-Detection

```json
{
  "operation": "incident.detect",
  "params": {
    "service": "user-service",
    "signals": ["error_rate", "latency", "saturation"]
  }
}
```

Response:
```json
{
  "detected": true,
  "severity": "P2",
  "signals": [
    {
      "name": "error_rate",
      "current": 0.05,
      "threshold": 0.01,
      "status": "breached"
    }
  ],
  "suggested_runbook": "https://runbooks.itqahn.io/user-service/high-error-rate"
}
```

### Incident Context

```json
{
  "operation": "incident.context",
  "params": {
    "service": "user-service",
    "time": "2026-01-06T11:45:00Z",
    "window": "30m"
  }
}
```

Returns:
- Recent deployments
- Config changes
- Related alerts
- Upstream/downstream status
- Similar past incidents

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `obs_mcp_requests_total` | Total requests |
| `obs_mcp_latency` | Query latency |
| `obs_mcp_bytes_returned` | Data returned |
| `obs_mcp_queries_rejected` | Rejected queries |
| `obs_mcp_cache_hits` | Cache hit ratio |

### Alerts

```yaml
alerts:
  - name: obs_high_query_latency
    condition: histogram_quantile(0.99, obs_mcp_latency) > 10
    severity: warning

  - name: obs_auth_failures
    condition: rate(obs_mcp_errors{type="auth"}[5m]) > 0
    severity: critical
```

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/06-operations/sre-model.md` — SRE model
- `docs/06-operations/incident-response.md` — Incident response

---

**Version**: 2.0.0 | **Date**: 2026-01-06
