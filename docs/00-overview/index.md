# Itqahn Overview

## What is Itqahn?

Itqahn is an **autonomous company-as-software platform**: it combines a developer portal, durable orchestration, policy enforcement, and evidence generation to reliably transform business intent into production-ready systems.

Unlike "agent demos", Itqahn is designed to operate like an elite software enterprise:

- **Durable execution** — workflow engines, retries, state persistence
- **Zero-trust identity** — workload identity federation (SPIFFE/SPIRE)
- **Policy-as-code governance** — prevent unsafe actions by design
- **Supply-chain integrity** — SLSA provenance, signed artifacts, curated dependencies
- **Evidence-first compliance** — audit packs built automatically
- **Reliability + cost engineering** — SLOs, token budgets, circuit breakers

## Itqahn in One Sentence

**Itqahn is a governed factory that builds software, and proves it was built safely.**

---

## Scope

### What Itqahn Can Build

Itqahn can generate and operate:

| Build Type | Description |
|------------|-------------|
| **Web Products** | Websites, portals, dashboards, marketplaces (component/tokens-only UI) |
| **Backend Services** | APIs, workers, schedulers, event processors |
| **Mobile Apps** | Release-ready iOS/Android or cross-platform apps |
| **Integrations** | Payments, email/SMS, CRM, ERP, maps, analytics |
| **Data Systems** | Pipelines, warehouses, governance tooling |
| **Infrastructure** | IaC + GitOps manifests (policy-gated) |

### What Itqahn Will Not Build (Hard Boundaries)

Itqahn must refuse requests that are:

- Illegal or facilitating wrongdoing
- Harmful (malware, phishing, exploitation)
- Disallowed by corporate policy or jurisdiction
- Requesting unsafe "autonomous deployment without governance"

These refusals are enforced via:
- **Domain Policy Filter** agent (`agents/01-intake-and-clarity/domain-policy-filter.md`)
- **OPA policies** (`policies/opa/`)

---

## Success Criteria

Itqahn is successful when it can repeatedly deliver:

| Criterion | Definition |
|-----------|------------|
| **Correctness** | Features match the PRD and acceptance criteria |
| **Safety** | No unauthorized access, no cross-tenant leaks, no secret exposures |
| **Auditability** | Every release has provenance, SBOM, scans, tests, and approvals recorded |
| **Maintainability** | Changes are small, reviewed, tested, observable, and reversible |
| **Cost Predictability** | "Cost per feature" and "cost per tenant" is measurable and bounded |

---

## Operating Assumption

LLMs are powerful but fallible. Therefore **trust is never assumed**—it is earned through:

- Deterministic pipelines
- Policy gates
- Repeatable tests
- Cryptographic evidence

---

## How to Navigate This Repository

| Directory | Purpose |
|-----------|---------|
| `docs/` | Canonical documentation (you are here) |
| `agents/` | 102 agent role definitions with contracts |
| `policies/` | OPA/Kyverno policy enforcement |
| `templates/` | Golden path artifacts |
| `tools/` | Validators and automation scripts |
| `legal/` | Terms, policies, compliance templates |

### Recommended Reading Order

1. **This overview** — understand what Itqahn is
2. **[Principles](principles.md)** — non-negotiable rules
3. **[Glossary](glossary.md)** — shared vocabulary
4. **[Product Vision](../01-product/product-vision.md)** — mission and value
5. **[Lifecycle Phase Gates](../01-product/lifecycle-phase-gates.md)** — how work flows
6. **[Reference Architecture](../02-architecture/reference-architecture.md)** — system design

---

**Version**: 2.0.0 | **Date**: 2026-01-06
