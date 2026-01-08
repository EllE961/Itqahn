# Reference Architecture

Itqahn is split into a **Control Plane** (platform) and a **Data Plane** (tenant workloads).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CONTROL PLANE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Developer  │  │  Orchestrator│  │   Policy     │  │   Identity   │ │
│  │    Portal    │  │   (Temporal) │  │    Layer     │  │   + Secrets  │ │
│  │  (Backstage) │  │              │  │  (OPA/Kyv)   │  │ (SPIFFE/Vault│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │                 │          │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐ │
│  │  Truth Store │  │ Supply Chain │  │ Observability│  │   Evidence   │ │
│  │    (Git)     │  │  (CI/SLSA)   │  │   (OTel)     │  │    Store     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │   Trust Boundary   │
                          └─────────┬─────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                            DATA PLANE                                    │
│  ┌───────────────────────────┐    ┌───────────────────────────────────┐ │
│  │     SMB / Shared Mode     │    │      Enterprise / Isolated Mode   │ │
│  │  • Namespaces + NetPol    │    │  • vCluster / Dedicated Nodes     │ │
│  │  • Row-Level Security     │    │  • Tenant-Specific Keys           │ │
│  │  • Shared Control Plane   │    │  • Stricter Quotas                │ │
│  └───────────────────────────┘    └───────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Control Plane Components

### Developer Portal (Backstage)

**Purpose**: The "front door" for developers and agents.

| Feature | Function |
|---------|----------|
| Service Catalog | Inventory of all services, owners, dependencies |
| Golden Paths | Scaffolders for approved project types |
| TechDocs | Documentation site (this documentation) |
| Templates | Self-service creation of services, APIs, apps |

**Key integrations**:
- Git (source of truth)
- Temporal (workflow status)
- Kubernetes (runtime status)

---

### Orchestrator (Temporal)

**Purpose**: Durable workflow execution for all agent work.

| Feature | Function |
|---------|----------|
| Workflows | Multi-step processes that survive crashes |
| Activities | Individual steps with retry policies |
| Signals | External triggers and human approvals |
| Queries | Real-time workflow state inspection |

**Configuration**:
- Namespace per environment (`itqahn-dev`, `itqahn-staging`, `itqahn-prod`)
- Optional namespace per high-assurance tenant
- Retention: 30 days for completed workflows

See `docs/02-architecture/workflow-architecture.md` for details.

---

### Truth Store (Git)

**Purpose**: Single source of truth for all artifacts.

| What | Where |
|------|-------|
| Requirements (PRDs) | `requirements/` |
| Source code | `src/` or service repos |
| Infrastructure | `infra/` (Terraform, manifests) |
| Policies | `policies/` |
| Documentation | `docs/` |
| ADRs | `docs/99-appendix/adrs/` |

**Rules**:
- All changes via PR
- Branch protection enforced
- Signed commits for production branches
- No direct pushes to main

---

### Policy Layer (OPA + Kyverno)

**Purpose**: Enforce rules as code.

| Engine | Scope |
|--------|-------|
| **OPA** | Pipeline gates, access decisions, budget checks |
| **Kyverno** | Kubernetes admission control |

**Key policies**:
- No deploy without Evidence Pack
- No secrets in code
- No privileged containers
- Budget caps enforced
- MCP allowlists enforced

See `policies/` directory for all policy definitions.

---

### Supply Chain (CI/SLSA)

**Purpose**: Secure, hermetic builds with provenance.

| Component | Function |
|-----------|----------|
| Hermetic builds | Isolated build environments |
| SBOM generation | CycloneDX format |
| Provenance | SLSA L3 attestations |
| Signing | Sigstore/cosign |
| Scanning | SAST, dependency, container |

**Pipeline stages**:
1. Source validation
2. Build (hermetic)
3. Test
4. Scan
5. Generate SBOM + provenance
6. Sign artifacts
7. Package Evidence Pack

---

### Identity + Secrets (SPIFFE/SPIRE + Vault)

**Purpose**: Zero-trust identity and secretless runtime.

| Component | Function |
|-----------|----------|
| **SPIFFE/SPIRE** | Workload identity (SVIDs) |
| **Vault** | Dynamic secrets, short TTL |
| **mTLS** | All service-to-service communication |

**Rules**:
- No long-lived credentials
- Secrets never in environment variables
- Identity-bound access only
- Automatic credential rotation

See `docs/04-security/identity-spiffe.md` and `docs/04-security/secrets-vault.md`.

---

### Observability (OpenTelemetry)

**Purpose**: Unified telemetry collection.

| Signal | Tools |
|--------|-------|
| Logs | Structured JSON, centralized aggregation |
| Metrics | Prometheus format, SLO dashboards |
| Traces | Distributed tracing, request correlation |

**Requirements**:
- All services emit traces, metrics, logs
- SLOs defined before production
- Dashboards linked to runbooks

---

### Evidence Store

**Purpose**: Immutable storage for Evidence Packs.

| Feature | Function |
|---------|----------|
| Immutability | Write-once, no modifications |
| Retention | Per compliance tier requirements |
| Verification | Signature validation at deploy time |
| Access control | Read-only for most, write only from CI |

---

## Data Plane Isolation Modes

### SMB / Shared Mode

For cost-effective multi-tenancy:

| Control | Implementation |
|---------|----------------|
| Namespace isolation | Each tenant gets dedicated namespace |
| Network policies | Deny all, allow explicit |
| Row-level security | Database-level tenant filtering |
| Resource quotas | CPU, memory, storage limits |
| RBAC | Tenant-scoped roles |

**Best for**: Internal tools, non-regulated workloads, cost-sensitive customers.

---

### Enterprise / Isolated Mode

For high-assurance requirements:

| Control | Implementation |
|---------|----------------|
| vCluster | Virtual cluster per tenant |
| Dedicated nodes | Node affinity, taints/tolerations |
| Tenant-specific keys | Separate encryption keys in Vault |
| Stricter quotas | Higher limits, guaranteed resources |
| Enhanced logging | All actions audited |

**Best for**: Regulated industries, enterprise customers, high-value data.

See `docs/02-architecture/tenancy-isolation.md` for details.

---

## Trust Boundaries (Non-Negotiable)

| Boundary | Enforcement |
|----------|-------------|
| Agents never run with cluster-admin | RBAC, admission policies |
| Tenants never share secret scopes | Vault policies, namespace isolation |
| Build environments are isolated | Ephemeral builders, no shared state |
| Deployments require signed evidence | Admission webhook verification |

---

## Standard Request Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 1. User │───▶│ 2.Intake│───▶│ 3.Plan  │───▶│ 4.Build │
│  Intent │    │  Agents │    │ Workflow│    │  Code   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                  │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───▼─────┐
│ 8. Post │◀───│ 7.Deploy│◀───│ 6.Sign  │◀───│ 5. CI   │
│  Launch │    │ (GitOps)│    │Evidence │    │  Gates  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

1. **User submits intent** — Via portal wizard or API
2. **Intake agents produce PRD** — Requirements, constraints, risk tier
3. **Orchestrator executes plan** — With budgets and stop conditions
4. **Builders generate code** — In feature branches
5. **CI runs gates** — Policies evaluate, tests run
6. **Evidence Pack produced** — Signed with provenance
7. **GitOps deploys** — Canary rollout with analysis
8. **Post-launch verification** — SLOs confirmed, gate closes

---

## Related Documents

- `docs/02-architecture/workflow-architecture.md` — Temporal model
- `docs/02-architecture/tenancy-isolation.md` — Multi-tenancy details
- `docs/04-security/security-model.md` — Security architecture
- `docs/05-compliance/evidence-pack.md` — Evidence Pack definition

---

**Version**: 2.0.0 | **Date**: 2026-01-06
