# MCP Kubernetes Integration

The Kubernetes MCP provides controlled access to cluster resources for deployment management, observability, and infrastructure operations.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  KUBERNETES MCP FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│   K8s MCP   │───▶│ Kubernetes  │             │
│  │         │    │             │    │    API      │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │   Read   │  │  Deploy  │  │    Operate      │              │
│  │  Status  │  │  (GitOps)│  │  (Rate-limited) │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `namespace.list` | List namespaces | Low |
| `namespace.read` | Read namespace details | Low |
| `deployment.list` | List deployments | Low |
| `deployment.read` | Read deployment details | Low |
| `deployment.scale` | Scale replicas | Medium |
| `deployment.restart` | Rolling restart | Medium |
| `pod.list` | List pods | Low |
| `pod.read` | Read pod details | Low |
| `pod.logs` | Read pod logs | Low |
| `pod.restart` | Delete/restart pod | Medium |
| `service.list` | List services | Low |
| `service.read` | Read service details | Low |
| `configmap.read` | Read configmap | Low |
| `secret.list` | List secret names | Low |
| `event.list` | List events | Low |
| `hpa.read` | Read HPA status | Low |

### Write Operations (GitOps-Preferred)

| Operation | Description | Requirement |
|-----------|-------------|-------------|
| `manifest.apply` | Apply manifest | Via ArgoCD only |
| `deployment.update` | Update deployment | Via ArgoCD only |
| `rollback.execute` | Rollback deployment | Approval required |

---

## Authentication

### SPIFFE Workload Identity (Recommended)

```yaml
kubernetes:
  auth:
    method: spiffe
    trust_domain: itqahn.io
    audience: kubernetes
    token_path: /var/run/secrets/spiffe/svid.jwt
```

### Service Account Token

```yaml
kubernetes:
  auth:
    method: service_account
    token_source: vault
    vault_path: kv/mcp/kubernetes/sa-token
    namespace: itqahn-system
```

### Kubeconfig

```yaml
kubernetes:
  auth:
    method: kubeconfig
    config_source: vault
    vault_path: kv/mcp/kubernetes/kubeconfig
```

---

## Operations

### List Deployments

```json
{
  "operation": "deployment.list",
  "params": {
    "namespace": "production",
    "label_selector": "app.kubernetes.io/managed-by=itqahn"
  }
}
```

Response:
```json
{
  "deployments": [
    {
      "name": "user-service",
      "namespace": "production",
      "replicas": {
        "desired": 3,
        "ready": 3,
        "available": 3
      },
      "image": "registry.itqahn.io/user-service:v1.2.3",
      "conditions": [
        {"type": "Available", "status": "True"},
        {"type": "Progressing", "status": "True"}
      ]
    }
  ]
}
```

### Read Pod Details

```json
{
  "operation": "pod.read",
  "params": {
    "namespace": "production",
    "name": "user-service-abc123-xyz"
  }
}
```

Response:
```json
{
  "name": "user-service-abc123-xyz",
  "namespace": "production",
  "status": {
    "phase": "Running",
    "conditions": [
      {"type": "Ready", "status": "True"}
    ],
    "containerStatuses": [
      {
        "name": "user-service",
        "ready": true,
        "restartCount": 0,
        "image": "registry.itqahn.io/user-service:v1.2.3"
      }
    ]
  },
  "spec": {
    "nodeName": "node-1",
    "serviceAccountName": "user-service"
  }
}
```

### Get Pod Logs

```json
{
  "operation": "pod.logs",
  "params": {
    "namespace": "production",
    "name": "user-service-abc123-xyz",
    "container": "user-service",
    "tail_lines": 100,
    "since_seconds": 3600
  }
}
```

### Scale Deployment

```json
{
  "operation": "deployment.scale",
  "params": {
    "namespace": "production",
    "name": "user-service",
    "replicas": 5
  }
}
```

Constraints:
- Max replicas limited by allowlist
- Scaling down has minimum threshold
- Audit logged

### Restart Deployment

```json
{
  "operation": "deployment.restart",
  "params": {
    "namespace": "production",
    "name": "user-service"
  }
}
```

Constraints:
- Rate limited (1 per hour per deployment)
- Triggers rolling restart
- Audit logged

### List Events

```json
{
  "operation": "event.list",
  "params": {
    "namespace": "production",
    "field_selector": "involvedObject.name=user-service",
    "limit": 50
  }
}
```

---

## GitOps Integration

### ArgoCD Deployment Model

Direct deployments are not allowed. All changes go through GitOps:

```
1. Agent updates infra repo
       │
       ▼
2. ArgoCD detects change
       │
       ▼
3. Admission controller verifies evidence
       │
       ▼
4. Deployment proceeds
```

### Read-Only by Default

```yaml
kubernetes:
  mode: read_only
  exceptions:
    - operation: deployment.scale
      requires: approval
    - operation: deployment.restart
      requires: rate_limit_check
    - operation: pod.restart
      requires: rate_limit_check
```

### Admission Control

```yaml
# Kyverno policy for agent deployments
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-evidence-pack
spec:
  validationFailureAction: enforce
  rules:
    - name: check-evidence
      match:
        resources:
          kinds: ["Deployment"]
      validate:
        message: "Deployment must have valid evidence pack"
        pattern:
          metadata:
            annotations:
              itqahn.io/evidence-pack: "?*"
              itqahn.io/workflow-id: "?*"
```

---

## Namespace Isolation

### Tenant Namespaces

Each tenant gets isolated namespaces:

```
tenant-abc-dev
tenant-abc-staging
tenant-abc-prod
```

### Namespace Constraints

```yaml
kubernetes:
  namespace_constraints:
    allowed_patterns:
      - "tenant-{{tenant_id}}-*"
      - "shared-services"
    denied_patterns:
      - "kube-system"
      - "kube-public"
      - "default"
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  kubernetes:
    enabled: true
    clusters:
      - name: production
        api_server: "https://k8s.itqahn.io"
        auth:
          method: spiffe

      - name: staging
        api_server: "https://k8s-staging.itqahn.io"
        auth:
          method: spiffe

    defaults:
      timeout_seconds: 30
      page_size: 100

    rate_limits:
      read_operations_per_minute: 100
      write_operations_per_hour: 10

    excluded_namespaces:
      - kube-system
      - kube-public
      - cert-manager
```

### Allowlist Entry

```yaml
roles:
  backend-builder:
    mcps:
      kubernetes:
        operations:
          - namespace.list
          - namespace.read
          - deployment.list
          - deployment.read
          - pod.list
          - pod.read
          - pod.logs
          - service.read
          - configmap.read
          - event.list
        constraints:
          namespaces: ["dev-*", "staging-*"]
          clusters: ["staging"]

  sre-operator:
    mcps:
      kubernetes:
        operations:
          - namespace.list
          - namespace.read
          - deployment.list
          - deployment.read
          - deployment.scale
          - deployment.restart
          - pod.list
          - pod.read
          - pod.logs
          - pod.restart
          - service.read
          - configmap.read
          - secret.list
          - event.list
          - hpa.read
        constraints:
          namespaces: ["*"]
          clusters: ["production", "staging"]
          max_replicas: 20
          max_restarts_per_hour: 3
```

---

## Rate Limiting

### Operation Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| Read operations | 100 | 1 minute |
| Scale operations | 5 | 1 hour |
| Restart operations | 3 | 1 hour |
| Log fetches | 50 | 1 minute |

### Rate Limit Configuration

```yaml
kubernetes:
  rate_limits:
    per_agent:
      read: 100/min
      write: 10/hour
    per_deployment:
      scale: 5/hour
      restart: 1/hour
    per_pod:
      restart: 3/hour
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `K8S_AUTH_FAILED` | Authentication failed | Refresh credentials |
| `K8S_NOT_FOUND` | Resource not found | Check name/namespace |
| `K8S_FORBIDDEN` | Access denied | Check RBAC |
| `K8S_CONFLICT` | Resource conflict | Retry |
| `K8S_TIMEOUT` | API timeout | Retry |
| `K8S_RATE_LIMITED` | Rate limit exceeded | Back off |

### Retry Configuration

```yaml
kubernetes:
  retry:
    max_attempts: 3
    initial_delay_ms: 1000
    retry_on:
      - K8S_TIMEOUT
      - K8S_CONFLICT
```

---

## Security Considerations

### RBAC Configuration

```yaml
# Minimal RBAC for agent service account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: itqahn-agent
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services", "configmaps", "events"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments/scale"]
    verbs: ["get", "patch"]
```

### Network Policies

```yaml
# Restrict agent network access
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: itqahn-agent-policy
spec:
  podSelector:
    matchLabels:
      app: itqahn-agent
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - port: 443
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `k8s_mcp_requests_total` | Total requests |
| `k8s_mcp_latency` | Request latency |
| `k8s_deployments_scaled` | Scale operations |
| `k8s_pods_restarted` | Pod restarts |
| `k8s_events_fetched` | Events retrieved |

### Alerts

```yaml
alerts:
  - name: k8s_auth_failures
    condition: rate(k8s_mcp_errors{type="auth"}[5m]) > 0
    severity: critical

  - name: k8s_high_restart_rate
    condition: sum(k8s_pods_restarted[1h]) > 10
    severity: warning
```

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/03-platform/ci-cd-gitops.md` — GitOps deployment
- `docs/06-operations/auto-remediation.md` — Auto-remediation

---

**Version**: 2.0.0 | **Date**: 2026-01-06
