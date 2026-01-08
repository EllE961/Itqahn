# Product Vision

## Mission

**Transform business intent into production-ready software through governed autonomous agents.**

Itqahn exists to prove that autonomous software development can be:
- Safe (no unauthorized actions, no data leaks)
- Auditable (cryptographic evidence of every decision)
- Reliable (durable execution, predictable costs)
- Compliant (evidence packs satisfy regulatory requirements)

---

## The Problem We Solve

Traditional software development has friction at every stage:

| Stage | Friction |
|-------|----------|
| Requirements | Ambiguity, scope creep, lost context |
| Architecture | Inconsistent decisions, undocumented tradeoffs |
| Development | Quality variance, security gaps, style drift |
| Testing | Incomplete coverage, flaky tests, manual effort |
| Deployment | Manual gates, missing evidence, audit scrambles |
| Operations | Undocumented runbooks, reactive incident response |

AI coding assistants solve some problems but create new ones:
- No governance (agents can do anything)
- No evidence (how do you audit AI-generated code?)
- No cost control (unbounded token usage)
- No consistency (different outputs every time)

**Itqahn solves both**: it automates development AND provides the governance, evidence, and cost control that enterprises require.

---

## Target Users

### Primary: Engineering Teams at SMB/Mid-Market

- 10-200 engineers
- Need to ship faster but can't sacrifice quality
- Compliance requirements (SOC2, GDPR, sometimes PCI/HIPAA)
- Limited DevOps/security/compliance specialists

### Secondary: Enterprise Platform Teams

- Building internal developer platforms
- Need to embed AI capabilities with governance
- Existing investment in Backstage, Temporal, Vault
- Require audit trails for regulated workloads

---

## Value Proposition

| For | Itqahn Provides |
|-----|-----------------|
| **Engineering leads** | Faster delivery with consistent quality |
| **Security teams** | Built-in AppSec gates, no manual reviews of routine code |
| **Compliance officers** | Evidence Packs satisfy auditors |
| **Finance** | Predictable, bounded costs per feature |
| **Executives** | Reduced time-to-market, reduced risk |

---

## What Makes Itqahn Different

### vs. AI Coding Assistants (Copilot, Cursor, etc.)

- **Governance**: Itqahn has policy gates; assistants have none
- **Evidence**: Itqahn produces audit packs; assistants produce code only
- **Durability**: Itqahn workflows survive crashes; assistants are stateless
- **Cost control**: Itqahn has budgets and circuit breakers; assistants charge per-token without limits

### vs. Traditional CI/CD

- **Intelligence**: Itqahn understands requirements; CI/CD just runs scripts
- **Autonomy**: Itqahn can generate, test, and fix code; CI/CD just validates
- **Completeness**: Itqahn produces evidence; CI/CD produces artifacts

### vs. Low-Code Platforms

- **Flexibility**: Itqahn generates real code; low-code is constrained
- **Portability**: Itqahn outputs are standard codebases; low-code locks you in
- **Customization**: Itqahn supports any architecture; low-code has fixed patterns

---

## North Star Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Feature Cycle Time** | PRD to production | < 5 days for standard features |
| **Evidence Completeness** | % of releases with full Evidence Pack | 100% |
| **Security Gate Pass Rate** | % of first-time passes | > 95% |
| **Cost Predictability** | Variance from estimated token budget | < 20% |
| **Drift Score** | PRD ↔ implementation alignment | > 0.90 |

---

## Non-Goals

Itqahn is **not**:

- A general-purpose AI assistant (it builds software, not answers questions)
- A low-code platform (it generates real, maintainable code)
- A replacement for human judgment on critical decisions
- A way to bypass compliance (it enforces compliance)

---

## Success State

Itqahn is successful when:

1. A product manager can describe a feature in natural language
2. The system produces a PRD, architecture, code, tests, and evidence
3. Human review is required only for high-risk decisions
4. Every release has cryptographic proof of its provenance
5. Costs are predictable and bounded
6. Auditors can verify compliance without manual evidence gathering

---

**Version**: 2.0.0 | **Date**: 2026-01-06
