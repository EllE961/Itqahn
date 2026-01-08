# Decision Log

This document tracks significant architectural and design decisions made for Itqahn. Each entry follows the ADR (Architecture Decision Record) format.

---

## Decision Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | Use Temporal for workflow orchestration | Accepted | 2025-09-15 |
| ADR-002 | Adopt SPIFFE/SPIRE for workload identity | Accepted | 2025-09-20 |
| ADR-003 | Implement Design Jail for UI governance | Accepted | 2025-10-01 |
| ADR-004 | Use OPA + Kyverno for policy enforcement | Accepted | 2025-10-10 |
| ADR-005 | Evidence Pack as deployment gate | Accepted | 2025-10-15 |
| ADR-006 | Agent Contract as mandatory rules | Accepted | 2025-10-20 |
| ADR-007 | MCP as controlled tool interface | Accepted | 2025-11-01 |
| ADR-008 | GitOps-only deployment model | Accepted | 2025-11-10 |
| ADR-009 | Multi-tenant isolation model | Accepted | 2025-11-15 |
| ADR-010 | Compliance tier classification | Accepted | 2025-12-01 |

---

## ADR-001: Use Temporal for Workflow Orchestration

**Status**: Accepted
**Date**: 2025-09-15
**Deciders**: Architecture Team, CEO Orchestrator

### Context

Itqahn needs durable, observable workflow orchestration that survives failures and provides exactly-once semantics.

### Decision

Use Temporal as the workflow orchestration engine.

### Consequences

**Positive:**
- Durable execution survives infrastructure failures
- Built-in retry and timeout handling
- Observable workflow state
- Strong consistency guarantees

**Negative:**
- Operational complexity of running Temporal cluster
- Learning curve for Temporal's programming model
- Additional infrastructure dependency

**Risks:**
- Temporal availability becomes critical path

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Custom state machine | Too much maintenance, no durability |
| Step Functions | AWS lock-in, limited observability |
| Airflow | Designed for batch, not interactive workflows |
| Conductor | Less mature, smaller community |

---

## ADR-002: Adopt SPIFFE/SPIRE for Workload Identity

**Status**: Accepted
**Date**: 2025-09-20
**Deciders**: Security Team, Platform Team

### Context

Agents and services need cryptographic identities that don't rely on static secrets.

### Decision

Use SPIFFE for identity format and SPIRE as the identity provider.

### Consequences

**Positive:**
- Zero static secrets for service authentication
- Short-lived certificates auto-rotated
- Works across cloud providers
- Standard format (SPIFFE ID)

**Negative:**
- Requires SPIRE server infrastructure
- Initial PKI setup complexity
- All services must integrate SPIFFE libraries

---

## ADR-003: Implement Design Jail for UI Governance

**Status**: Accepted
**Date**: 2025-10-01
**Deciders**: Design Team, Frontend Engineering

### Context

Autonomous agents producing UI must not introduce arbitrary CSS or unapproved components.

### Decision

Implement "Design Jail" - a hard constraint where UI agents can only use design tokens and approved components.

### Consequences

**Positive:**
- Consistent visual design across all outputs
- Enforces design system adoption
- Prevents UI drift
- Easier accessibility compliance

**Negative:**
- Limits creative flexibility
- Requires comprehensive design token library
- Build-time validation adds CI time

---

## ADR-004: Use OPA + Kyverno for Policy Enforcement

**Status**: Accepted
**Date**: 2025-10-10
**Deciders**: Security Team, Platform Team

### Context

Policy enforcement needs to happen at multiple layers: API calls, Kubernetes admission, and agent actions.

### Decision

Use OPA for general policy evaluation and Kyverno for Kubernetes-specific policies.

### Consequences

**Positive:**
- Rego is powerful and widely understood
- Kyverno integrates natively with K8s
- Policies as code, version controlled
- Centralized policy management

**Negative:**
- Two policy languages to maintain
- OPA/Rego learning curve
- Policy testing requires investment

---

## ADR-005: Evidence Pack as Deployment Gate

**Status**: Accepted
**Date**: 2025-10-15
**Deciders**: Compliance Team, SRE Team

### Context

Deployments must have verifiable evidence of security scans, tests, and provenance.

### Decision

Create Evidence Pack - a collection of SBOM, provenance, scan results, and test reports - required for all deployments.

### Consequences

**Positive:**
- Audit-ready by default
- Clear deployment requirements
- Traceable supply chain
- Automated compliance evidence

**Negative:**
- Larger artifact storage
- Slower CI pipeline
- Requires tooling integration

---

## ADR-006: Agent Contract as Mandatory Rules

**Status**: Accepted
**Date**: 2025-10-20
**Deciders**: Executive Team, Engineering Leadership

### Context

Autonomous agents need hard constraints to prevent unbounded behavior.

### Decision

Define Agent Contract with mandatory rules: artifact-first outputs, role boundaries, stop conditions, determinism preference, provenance requirements.

### Consequences

**Positive:**
- Predictable agent behavior
- Auditability of all actions
- Clear escalation paths
- Prevents "vibe-coded autonomy"

**Negative:**
- Limits agent creativity
- More complex agent implementation
- Contract enforcement overhead

---

## ADR-007: MCP as Controlled Tool Interface

**Status**: Accepted
**Date**: 2025-11-01
**Deciders**: Security Team, Platform Team

### Context

Agents need controlled access to external systems (GitHub, Jira, Kubernetes, etc.).

### Decision

Implement MCP (Model Context Protocol) layer with allowlists, rate limits, and audit logging.

### Consequences

**Positive:**
- Centralized access control
- Full audit trail of tool usage
- Rate limiting prevents abuse
- Policy-mediated access

**Negative:**
- Additional proxy layer
- Potential latency impact
- MCP implementation for each integration

---

## ADR-008: GitOps-Only Deployment Model

**Status**: Accepted
**Date**: 2025-11-10
**Deciders**: SRE Team, Security Team

### Context

Direct deployments bypass review and audit processes.

### Decision

All deployments must go through GitOps (ArgoCD). No direct kubectl apply allowed.

### Consequences

**Positive:**
- All changes are version controlled
- Review process for all changes
- Easy rollback via git revert
- Clear audit trail

**Negative:**
- Slower emergency response
- Git repo becomes critical path
- Requires GitOps infrastructure

---

## ADR-009: Multi-Tenant Isolation Model

**Status**: Accepted
**Date**: 2025-11-15
**Deciders**: Architecture Team, Security Team

### Context

Itqahn serves multiple tenants with varying isolation requirements.

### Decision

Implement tiered isolation: shared control plane with isolated data plane. Namespace-based isolation in Kubernetes.

### Consequences

**Positive:**
- Cost-effective for most tenants
- Strong isolation where needed
- Flexible isolation levels

**Negative:**
- Complexity of multi-tenant systems
- Noisy neighbor risks in shared tier
- Requires careful RBAC design

---

## ADR-010: Compliance Tier Classification

**Status**: Accepted
**Date**: 2025-12-01
**Deciders**: Compliance Team, Product Team

### Context

Different projects have different compliance requirements.

### Decision

Implement three tiers: Baseline (standard), Sensitive (additional controls), Regulated (full audit trail).

### Consequences

**Positive:**
- Right-sized compliance for each project
- Clear requirements per tier
- Efficient resource allocation

**Negative:**
- Complexity of tier management
- Potential for misclassification
- Different workflows per tier

---

## Template: New Decision Record

```markdown
## ADR-XXX: [Title]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Deciders**: [List of teams/individuals]

### Context

[What is the issue that we're seeing that is motivating this decision?]

### Decision

[What is the change that we're proposing?]

### Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Drawback 1]
- [Drawback 2]

**Risks:**
- [Risk 1]

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| [Alt 1] | [Reason] |
```

---

## Related Documents

- `docs/01-product/adr-policy.md` — ADR creation policy
- `templates/governance/ADR.md` — ADR template
- `docs/02-architecture/` — Architecture documentation

---

**Version**: 2.0.0 | **Date**: 2026-01-06
