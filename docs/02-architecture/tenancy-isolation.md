# Tenancy Isolation

Itqahn supports multiple isolation modes to balance cost, security, and compliance requirements.

---

## Isolation Modes

| Mode | Use Case | Isolation Level | Cost |
|------|----------|-----------------|------|
| **Shared (SMB)** | Internal tools, cost-sensitive | Namespace + policies | Low |
| **Isolated (Enterprise)** | Regulated, enterprise | vCluster + dedicated | High |

---

## Shared Mode (SMB)

```
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ ns: tenant-a│  │ ns: tenant-b│  │ ns: tenant-c│         │
│  │             │  │             │  │             │         │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │         │
│  │ │ workload│ │  │ │ workload│ │  │ │ workload│ │         │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │         │
│  │ NetworkPol │  │ NetworkPol │  │ NetworkPol │         │
│  │ Quotas     │  │ Quotas     │  │ Quotas     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SHARED CONTROL PLANE                     │   │
│  │  Temporal | Vault | OPA | Observability              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Controls

| Control | Implementation |
|---------|----------------|
| **Namespace isolation** | Each tenant gets dedicated namespace |
| **Network policies** | Default deny; allow only explicit |
| **Resource quotas** | CPU, memory, storage limits per tenant |
| **RBAC** | Tenant-scoped roles, no cluster access |
| **Row-level security** | Database-level tenant filtering |
| **Secrets** | Vault paths scoped by tenant ID |

### Network Policy Example

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress: []
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

### Resource Quota Example

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "5"
    services: "10"
```

### Row-Level Security (Database)

```sql
-- PostgreSQL RLS policy
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
```

Application must set tenant context:

```sql
SET app.tenant_id = 'tenant-a-uuid';
SELECT * FROM orders;  -- Only sees tenant-a's orders
```

---

## Isolated Mode (Enterprise)

```
┌─────────────────────────────────────────────────────────────┐
│                    PHYSICAL CLUSTER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────┐  ┌───────────────────────┐   │
│  │   vCluster: tenant-a      │  │   vCluster: tenant-b  │   │
│  │   ┌─────────────────────┐ │  │   ┌─────────────────┐ │   │
│  │   │ Virtual Control     │ │  │   │ Virtual Control │ │   │
│  │   │ Plane (API Server)  │ │  │   │ Plane           │ │   │
│  │   └─────────────────────┘ │  │   └─────────────────┘ │   │
│  │   ┌─────────────────────┐ │  │   ┌─────────────────┐ │   │
│  │   │ Workloads           │ │  │   │ Workloads       │ │   │
│  │   │ (dedicated nodes)   │ │  │   │ (dedicated)     │ │   │
│  │   └─────────────────────┘ │  │   └─────────────────┘ │   │
│  └───────────────────────────┘  └───────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         PHYSICAL CONTROL PLANE (Platform)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Controls

| Control | Implementation |
|---------|----------------|
| **vCluster** | Virtual Kubernetes cluster per tenant |
| **Dedicated nodes** | Node affinity, taints/tolerations |
| **Tenant-specific keys** | Separate encryption keys in Vault |
| **Enhanced RBAC** | Full cluster-admin within vCluster |
| **Dedicated observability** | Separate metrics/logs namespaces |
| **Custom policies** | Tenant-specific OPA bundles |

### vCluster Benefits

| Feature | Benefit |
|---------|---------|
| Full Kubernetes API | Tenant can use any K8s features |
| CRD isolation | Tenant CRDs don't affect others |
| Admission control | Tenant-specific webhooks |
| RBAC isolation | Full admin without platform access |
| Resource isolation | Guaranteed resources via node pools |

### Node Affinity Example

```yaml
apiVersion: v1
kind: Pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: tenant
                operator: In
                values:
                  - enterprise-tenant-a
  tolerations:
    - key: "tenant"
      operator: "Equal"
      value: "enterprise-tenant-a"
      effect: "NoSchedule"
```

### Tenant-Specific Encryption

```hcl
# Vault policy for tenant-specific keys
path "transit/encrypt/tenant-a-key" {
  capabilities = ["update"]
  allowed_parameters = {
    "plaintext" = []
  }
}

path "transit/decrypt/tenant-a-key" {
  capabilities = ["update"]
  allowed_parameters = {
    "ciphertext" = []
  }
}
```

---

## Context Isolation

Regardless of mode, all requests must include tenant context:

### HTTP Headers

```
X-Tenant-ID: tenant-a-uuid
X-Correlation-ID: req-12345
```

### Temporal Workflows

```python
workflow_options = WorkflowOptions(
    id=f"tenant-{tenant_id}-{workflow_type}-{uuid}",
    task_queue=f"tenant-{tenant_id}-queue",
    search_attributes={
        "TenantId": tenant_id,
        "ComplianceTier": "regulated"
    }
)
```

### Database Connections

```python
# Connection pool per tenant (isolated mode)
# Or RLS context per request (shared mode)

async with get_tenant_connection(tenant_id) as conn:
    # All queries automatically scoped
    results = await conn.fetch("SELECT * FROM orders")
```

---

## AI/LLM Context Isolation

Critical: Prevent cross-tenant data leakage in AI contexts.

| Control | Implementation |
|---------|----------------|
| **Prompt isolation** | Tenant data never in shared prompts |
| **Memory isolation** | Separate vector namespaces per tenant |
| **Model isolation** | Optional: dedicated model deployments |
| **Output filtering** | Post-generation PII/tenant scan |

### Vector Store Isolation

```python
# Each tenant gets separate namespace
episodic_memory = VectorStore(
    collection=f"tenant-{tenant_id}-episodic",
    metadata_filter={"tenant_id": tenant_id}
)
```

### Prompt Assembly

```python
def assemble_prompt(tenant_id: str, task: str) -> str:
    # Load only tenant's context
    context = memory.retrieve(
        tenant_id=tenant_id,  # Strict filter
        query=task
    )

    # Verify no cross-tenant leakage
    assert all(doc.tenant_id == tenant_id for doc in context)

    return prompt_template.format(
        context=context,
        task=task
    )
```

---

## Compliance Tier Mapping

| Isolation Mode | Baseline | Sensitive | Regulated |
|----------------|----------|-----------|-----------|
| **Shared** | Yes | Yes (with RLS) | No |
| **Isolated** | Optional | Yes | Yes (required) |

Regulated workloads **must** use isolated mode.

---

## Migration Path

### Shared → Isolated

1. Provision vCluster for tenant
2. Create dedicated node pool
3. Migrate workloads (blue-green)
4. Migrate data with validation
5. Update DNS/routing
6. Verify isolation controls
7. Decommission shared resources

### Isolated → Shared (Downgrade)

Requires:
- Compliance review approval
- Data classification review
- Customer consent (if applicable)

---

## Related Documents

- `docs/02-architecture/reference-architecture.md` — Overall architecture
- `docs/04-security/security-model.md` — Trust boundaries
- `docs/05-compliance/compliance-tiers.md` — Tier requirements

---

**Version**: 2.0.0 | **Date**: 2026-01-06
