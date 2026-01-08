# Itqahn — Autonomous Software Enterprise Platform

Itqahn is a **company-as-software** platform: a governed, auditable, and cost-controlled agentic system that turns **human intent** into **production-grade software** using **durable orchestration**, **zero-trust identity**, **policy-as-code**, and **cryptographic provenance**.

This repository is the **canonical documentation pack** and reference implementation blueprint for the Itqahn platform.

---

## What Itqahn Builds

Itqahn produces enterprise-grade software artifacts:

| Output Type | Description |
|-------------|-------------|
| **Backend Services** | REST/gRPC APIs, event-driven workers, schedulers |
| **Web Applications** | Next.js/React under strict Design Jail governance |
| **Mobile Applications** | Native or cross-platform with standard release pipelines |
| **Data Products** | Pipelines, models, feature stores with evidence and governance |
| **Infrastructure** | IaC + GitOps as controlled, policy-gated output |

Scope is controlled through **Phase Gates**, **compliance tiers**, and **policy-as-code**.

---

## Core Invariants

| # | Invariant | Implementation |
|---|-----------|----------------|
| 1 | **Durable Execution** | Every workflow is resumable, auditable, retry-safe (Temporal) |
| 2 | **Non-Human Identity** | Every agent has short-lived cryptographic identity (SPIFFE/SPIRE) |
| 3 | **Policy Before Action** | No commits, deploys, or secret access without OPA/Kyverno allow |
| 4 | **Evidence Required** | Releases include SLSA provenance + SBOM + scan/test artifacts |
| 5 | **Design Jail** | UI work is components/tokens only; no free-form CSS |
| 6 | **Cost is Reliability** | Token and cloud budget circuit breakers are mandatory |
| 7 | **Drift Control** | Semantic drift (PRD ↔ code ↔ UI) is continuously measured |

---

## Repository Structure

```
itqahn-documentation-pack/
├── docs/                    # Canonical documentation
│   ├── 00-overview/         # Platform overview, glossary, principles
│   ├── 01-product/          # Product vision, build types, phase gates
│   ├── 02-architecture/     # Reference architecture, workflows, memory
│   ├── 03-platform/         # Portal, Backstage, CI/CD, Design System
│   ├── 04-security/         # Security model, identity, secrets, SDLC
│   ├── 05-compliance/       # Evidence pack, SLSA, SBOM, audit operations
│   ├── 06-operations/       # SRE, incident response, runbooks, FinOps
│   ├── 07-integrations/     # Git, webhooks, MCP integrations
│   ├── 08-agents/           # Agent contract, permissions, catalog
│   └── 99-appendix/         # Decision log, templates index, references
│
├── agents/                  # Agent library (102 roles)
│   ├── AGENT-CONTRACT.md    # Mandatory agent rules
│   ├── PERMISSIONS.md       # Permission model
│   └── roles/               # Role definitions by category
│
├── policies/                # Policy-as-code
│   ├── opa/                 # OPA/Rego policies
│   ├── kyverno/             # Kubernetes admission policies
│   ├── security/            # Security baseline policies
│   └── compliance/          # Compliance control mappings
│
├── templates/               # Golden path templates
│   ├── governance/          # ADR, PRD, RFC templates
│   ├── evidence/            # Evidence pack templates
│   ├── mcp/                 # MCP allowlist configuration
│   ├── design/              # Design system tokens/components
│   └── backstage/           # Backstage scaffolder templates
│
├── tools/                   # Automation utilities
│   ├── validators/          # Build-time validators
│   ├── drift-checker/       # Drift scoring tool
│   ├── policy-tests/        # OPA/Kyverno test suites
│   └── docsite-build/       # MkDocs documentation site
│
└── legal/                   # Legal and policy templates
    ├── terms-of-service.md
    ├── privacy-policy.md
    ├── security-disclosure-policy.md
    └── license-policy.md
```

---

## Quick Start

### 1. Explore Documentation

Start with the documentation overview:

```bash
# Browse docs locally
cd docs/00-overview/
cat index.md

# Or build the documentation site
cd tools/docsite-build/
pip install -r requirements.txt
mkdocs serve
```

### 2. Adopt Golden Paths

Use templates to bootstrap projects:

```bash
# Review available templates
ls templates/

# Use Backstage scaffolder templates
ls templates/backstage/
```

### 3. Implement Policy Enforcement

Deploy policies before scaling agent autonomy:

```bash
# Test OPA policies
opa test policies/opa/ tools/policy-tests/opa/ -v

# Apply Kyverno policies
kubectl apply -f policies/kyverno/
```

### 4. Configure Agents

Use the agent library for your runtime:

```bash
# Review agent contract
cat agents/AGENT-CONTRACT.md

# Browse role definitions
ls agents/roles/
```

---

## Documentation Guide

| Section | Purpose | Key Topics |
|---------|---------|------------|
| **00-overview** | Platform introduction | Glossary, principles, getting started |
| **01-product** | Product management | Vision, build types, phase gates, ADRs |
| **02-architecture** | System design | Reference architecture, workflows, memory, tenancy |
| **03-platform** | Platform components | Portal, Backstage, CI/CD, Design Jail |
| **04-security** | Security practices | Security model, SPIFFE, Vault, SSDF, red team |
| **05-compliance** | Compliance operations | Evidence pack, SLSA, SBOM/VEX, audit readiness |
| **06-operations** | Operations | SRE model, incidents, runbooks, auto-remediation |
| **07-integrations** | External integrations | Git, webhooks, MCP (Figma, GitHub, Jira, K8s, Vault) |
| **08-agents** | Agent governance | Contract, permissions, quality bar, catalog |
| **99-appendix** | Reference materials | Decision log, template index, external links |

---

## Agent Library

Itqahn includes **102 specialized agent roles** across 11 categories:

| Category | Agents | Examples |
|----------|--------|----------|
| Core Orchestration | 6 | Orchestrator, Memory Manager, Budget Controller |
| Requirements | 12 | PRD Analyst, User Story Writer, Acceptance Criteria |
| Architecture | 10 | System Architect, API Designer, Schema Designer |
| Development | 18 | Backend Developer, Frontend Developer, DevOps Engineer |
| Quality | 14 | Test Engineer, Security Auditor, Code Reviewer |
| DevOps/SRE | 12 | Release Manager, SRE, Incident Commander |
| Security | 8 | Security Architect, Threat Modeler, Penetration Tester |
| Data | 8 | Data Engineer, ML Engineer, Analytics Engineer |
| Compliance | 6 | Compliance Officer, Auditor, Evidence Curator |
| Documentation | 4 | Technical Writer, API Doc Writer |
| Specialized | 4 | Mobile Developer, Accessibility Specialist |

All agents operate under the **Agent Contract** (`agents/AGENT-CONTRACT.md`) with role-specific permissions.

---

## Policy Framework

### OPA Policies

```bash
# Core policies
policies/opa/
├── mcp_allowlist.rego      # MCP operation permissions
├── evidence_required.rego   # Evidence pack requirements
├── drift_threshold.rego     # Drift score limits
└── budget_limit.rego        # Token budget enforcement
```

### Kyverno Policies

```bash
# Kubernetes admission policies
policies/kyverno/
├── require-evidence-pack.yaml
├── require-slsa-provenance.yaml
├── deny-privileged-containers.yaml
└── require-resource-limits.yaml
```

---

## MCP Integrations

Model Context Protocol (MCP) provides controlled tool access for agents:

| Integration | Operations | Documentation |
|-------------|------------|---------------|
| **Figma** | Read designs, tokens, components | `docs/07-integrations/mcp/mcp-figma.md` |
| **GitHub** | Repository, PR, issue management | `docs/07-integrations/mcp/mcp-github.md` |
| **Jira** | Issue tracking, approvals | `docs/07-integrations/mcp/mcp-jira.md` |
| **Kubernetes** | Read cluster state (GitOps deploys) | `docs/07-integrations/mcp/mcp-kubernetes.md` |
| **Vault** | Dynamic secrets, credential management | `docs/07-integrations/mcp/mcp-vault.md` |
| **Observability** | Metrics, logs, traces, SLOs | `docs/07-integrations/mcp/mcp-observability.md` |

See `docs/07-integrations/mcp/mcp-overview.md` for architecture and security model.

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| **Validators** | Build-time validation | `python tools/validators/design_jail_validator.py` |
| **Drift Checker** | Intent vs implementation scoring | `python tools/drift-checker/drift_scoring.py` |
| **Policy Tests** | OPA/Kyverno test suites | `opa test policies/opa/ tools/policy-tests/opa/` |
| **Docsite Build** | MkDocs documentation site | `mkdocs serve` |

---

## Compliance

Itqahn supports multiple compliance tiers:

| Tier | Requirements | Use Case |
|------|--------------|----------|
| **Standard** | Basic SBOM, tests, code review | Internal tools |
| **Enhanced** | SLSA Level 2, security scans | Customer-facing |
| **Regulated** | SLSA Level 3, signed provenance, audit logs | Financial, healthcare |

See `docs/05-compliance/compliance-tiers.md` for details.

---

## Contributing

1. Follow the governance model in `docs/01-product/adr-policy.md`
2. Use templates from `templates/governance/`
3. Ensure all changes pass policy validation
4. Include evidence in PRs for compliance requirements

---

## Safety & Disclaimer

This pack contains engineering guidance and policy templates. It is **not legal advice**. Always involve qualified legal/compliance professionals for regulated deployments.

All legal documents in `legal/` are templates requiring customization and legal review before use.

---

## Related Resources

- **Documentation Site**: https://docs.itqahn.io
- **External Standards**: See `docs/99-appendix/reference-links.md`
- **Decision Log**: See `docs/99-appendix/decision-log.md`

---

**Version**: 2.0.0 | **Date**: 2026-01-06
