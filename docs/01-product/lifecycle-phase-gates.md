# Lifecycle Phase Gates

Itqahn uses phase gates to prevent the "prototype trap" and ensure consistent quality. Work cannot proceed to the next phase without meeting exit criteria.

---

## Overview

```
┌───────────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│      Gate 1       │───▶│   Gate 2    │───▶│   Gate 3    │───▶│   Gate 4    │
│   Concept Lock    │    │  Experience │    │     RC      │    │ Post-Launch │
│ (Adaptive         │    │    Lock     │    │             │    │  (7 days)   │
│  Interview)       │    │             │    │             │    │             │
└───────────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Gate 1: Concept Lock (Adaptive Interview)

**Goal**: Capture complete project requirements through an adaptive, guided interview before any implementation begins.

Phase 1 is the **entry gate** to Itqahn. Users MUST complete the Adaptive Interview to produce a Concept Lock Artifact before any build work can begin.

### Phase 1: Start a Project (Adaptive Interview)

The Adaptive Interview is a **dashboard-driven, branching questionnaire** that captures all information needed to begin building. It is NOT a fixed sequence of steps—questions adapt based on previous answers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ADAPTIVE INTERVIEW FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │  Project    │─────▶│   Region    │─────▶│  Journeys   │                 │
│  │   Card      │      │   Profile   │      │  & Scope    │                 │
│  └─────────────┘      └─────────────┘      └──────┬──────┘                 │
│                                                    │                        │
│         ┌──────────────────────────────────────────┤                        │
│         │                                          │                        │
│         ▼                                          ▼                        │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │  Design OS  │─────▶│  Wireframe  │─────▶│   Asset     │                 │
│  │   Draft     │      │  Selection  │      │  Manifest   │                 │
│  └─────────────┘      └─────────────┘      └──────┬──────┘                 │
│                                                    │                        │
│                                                    ▼                        │
│                                            ┌─────────────┐                  │
│                                            │ Assumptions │                  │
│                                            │  Register   │                  │
│                                            └──────┬──────┘                  │
│                                                    │                        │
│                                                    ▼                        │
│                                            ┌─────────────┐                  │
│                                            │  CONCEPT    │                  │
│                                            │   LOCK      │                  │
│                                            └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Adaptive Interview Principles

| Principle | Requirement |
|-----------|-------------|
| **Multiple-choice first** | Every question MUST have 3-12 pre-defined options |
| **Always offer escape hatches** | Every question MUST include "Not sure" and "Other (write)" options |
| **Constraint-based choices** | Brand/colors generated from accessible, compliant palettes |
| **Visual selection** | Wireframe and design choices shown as visual previews |
| **Branching logic** | Follow-up questions adapt based on previous answers |
| **Fast path available** | Minimal set completes in 2-4 minutes |
| **Save and resume** | Users can pause and continue later |

### Interview Modules (Adaptive Order)

Modules are presented in logical order but may branch or skip based on user responses:

| Module | Purpose | Triggers Additional Modules |
|--------|---------|----------------------------|
| **Project Card** | Name, type, one-liner, primary persona | Build type-specific modules |
| **Region Profile** | Operational constraints, locale, compliance | Region-specific requirements |
| **Journeys & Scope** | Core user journeys, MVP boundaries | Feature-specific modules |
| **Design OS Draft** | Palette, typography, density, spacing | Accessibility checks |
| **Wireframe Selection** | Layout templates per screen type | Asset needs |
| **Asset Manifest** | Brand assets, icons, illustrations needed | Platform-specific formats |
| **Assumptions Register** | Explicit unknowns, decisions deferred | Risk assessment |

### Branching Logic

| Previous Answer | Triggers |
|-----------------|----------|
| Build type = Mobile App | App icon requirements, platform selection (iOS/Android) |
| Build type = Web App | Favicon, OG images, responsive breakpoints |
| Region = EU | GDPR data residency, cookie consent requirements |
| Region = Middle East | RTL support, locale-specific assets |
| Journeys include payments | Payment provider selection, PCI compliance tier |
| Journeys include auth | Auth provider selection, MFA requirements |
| Personas include enterprise | Multi-tenancy requirements, SSO |
| "Not sure" selected | Logs assumption, suggests safe default |

### Time Targets

| Path | Target Duration | Content |
|------|-----------------|---------|
| **Fast path** | 2-4 minutes | Minimal required fields only |
| **Standard path** | 8-15 minutes | All modules with defaults |
| **Extended path** | 20-30 minutes | All modules with custom selections |

### Maximum Branching Depth

To prevent interview fatigue:
- Maximum branching depth: **3 levels**
- Maximum questions per module: **8**
- Maximum total questions (fast path): **15**
- Maximum total questions (extended): **45**

---

### Concept Lock Artifact

The output of Phase 1 is the **Concept Lock Artifact**—a versioned, immutable record of all project decisions.

```json
{
  "$schema": "https://itqahn.io/schemas/concept-lock/v1",
  "version": "1.0.0",
  "artifact_id": "concept-lock-abc123",
  "status": "locked",
  "locked_at": "2026-01-08T12:00:00Z",
  "locked_by": "user@example.com",

  "project_card": { },
  "region_profile": { },
  "journeys_scope": { },
  "design_os_draft": { },
  "wireframe_choices": { },
  "asset_requirements": { },
  "assumptions_register": { },

  "metadata": {
    "interview_duration_seconds": 480,
    "modules_completed": 7,
    "questions_answered": 28,
    "not_sure_count": 3,
    "custom_answers_count": 2
  },
  "signatures": {
    "user_approval": "...",
    "system_validation": "..."
  }
}
```

### Draft Mode vs. Locked Mode

| Mode | Description | Allowed Actions |
|------|-------------|-----------------|
| **Draft** | Interview in progress or not yet approved | Edit any field, add/remove modules, revise answers |
| **Locked** | User approved, artifact immutable | View only; changes require Change Request |

**Draft Mode Rules:**
- All changes logged as revisions with timestamps
- Users can freely explore and revise
- Preview panel updates in real-time
- No build work can begin
- Auto-save every 30 seconds

**Locked Mode Rules:**
- Artifact is immutable (content-addressed hash)
- Committed to Git as reference
- All subsequent work MUST reference the locked version
- Changes ONLY via formal Change Request workflow
- Drift checks compare implementation against locked artifact

### Drift Checks After Lock

Once a Concept Lock is established:

| Check Type | Frequency | Action on Drift |
|------------|-----------|-----------------|
| **Scope drift** | Every PR | Flag additions not in locked journeys |
| **Design drift** | Every UI PR | Flag tokens/components not in Design OS Draft |
| **Asset drift** | Every asset | Flag assets not in Asset Requirements Manifest |
| **Assumption validation** | Gate 2 | Require explicit resolution of "Not sure" items |

```rego
# policies/opa/concept/drift_check.rego
package itqahn.concept

deny[msg] {
  input.pr.files[_].path == "src/features/*"
  feature := extract_feature(input.pr.files[_].path)
  not feature_in_scope(feature, input.concept_lock.journeys_scope)
  msg := sprintf("Feature '%s' not in locked scope. File Change Request.", [feature])
}
```

---

### Exit Criteria

| Artifact | Schema | Owner |
|----------|--------|-------|
| Concept Lock Artifact | `schemas/concept-lock.json` | User (with system validation) |
| Project Card complete | `schemas/project-card.json` | Intent Interviewer |
| Region Profile complete | `schemas/region-profile.json` | Scope Guard |
| Journeys & Scope v0 | `schemas/journeys-scope.json` | Requirements Writer |
| Design OS Draft | `schemas/design-os-draft.json` | Design OS Generator |
| Wireframe Choice Set | `schemas/wireframe-choices.json` | UI Flow Designer |
| Asset Requirements Manifest | `schemas/asset-requirements.json` | Asset Requirements Capture |
| Assumptions Register | `schemas/assumptions-register.json` | Assumptions Tracker |
| Risk tier assigned | `compliance-tiers.md` | Risk Profiler |
| Token budget approved | `finops-token-budgets.md` | CFO FinOps |

### Approval Required

- **User confirmation** (explicit "Lock and Proceed" action)
- **System validation** (all required fields present, schemas valid)
- **FinOps approval** (budget within limits)

### Blocking Conditions

- Any required module incomplete
- Schema validation fails
- Unresolved "Not sure" items exceed threshold (>30% of answers)
- Token budget exceeds tenant limits
- Domain policy filter rejects scope
- User has not explicitly confirmed lock

---

## Gate 2: Experience Lock

**Goal**: Finalize user flows, data model, and API contracts before implementation.

### Exit Criteria

| Artifact | Template | Owner |
|----------|----------|-------|
| User flows documented | Wireframes or journey maps | UX Designer |
| Data classification complete | `templates/compliance/DATA-CLASSIFICATION.md` | Data Architect |
| API contracts drafted | OpenAPI spec | API Contract Guardian |
| Threat model complete | `templates/security/THREAT-MODEL.md` | Threat Modeler |
| Design Jail assets exported | `templates/design/TOKENS.md` | Design Tokens Librarian |

### Approval Required

- Design Director (UX/UI sign-off)
- Security (threat model review)
- Architecture (API contracts)

### Blocking Conditions

- User flows not documented
- Data classification missing
- API contract validation fails
- Threat model not complete for Sensitive/Regulated tier
- Design tokens not exported (for Web/Mobile apps)

---

## Gate 3: Release Candidate

**Goal**: Produce a release that can be safely deployed to production.

### Exit Criteria

| Artifact | Validation | Owner |
|----------|------------|-------|
| All hard gates pass | CI pipeline green | Engineering |
| Evidence Pack generated | `tools/validators/evidence_pack_validator.py` | Audit Evidence Notary |
| Canary rollout passes | SLO checks in canary | SRE Commander |
| Runbooks documented | `templates/ops/RUNBOOK.md` | Runbook Author |
| Rollback plan documented | Part of release plan | Release Manager |
| On-call owner assigned | PagerDuty/OpsGenie | Delivery Manager |

### Hard Gates (Must Pass)

| Gate | Policy | Blocks On |
|------|--------|-----------|
| Security scan | `policies/opa/security/` | Critical/High findings |
| SBOM generated | `policies/opa/supply-chain/sbom_required.rego` | Missing SBOM |
| Provenance signed | `policies/opa/supply-chain/provenance_required.rego` | Missing provenance |
| Tests pass | `docs/05-compliance/evidence-pack.md` | Coverage below threshold |
| Design Jail compliant | `policies/opa/ui/design_jail.rego` | Non-compliant UI changes |

### Approval Required

- Engineering Lead (code review complete)
- Security (for Sensitive/Regulated)
- Compliance (for Regulated)
- On-call owner (accepts responsibility)

### Blocking Conditions

- Any hard gate fails
- Evidence Pack validation fails
- Canary SLO violation
- No on-call owner assigned
- Missing rollback plan

---

## Gate 4: Post-Launch (7 Days)

**Goal**: Stabilize and learn before declaring the feature complete.

### Exit Criteria

| Artifact | Validation | Owner |
|----------|------------|-------|
| SLO baselines validated | 7 days of metrics | Reliability Engineer |
| Error budget policy active | Configured in monitoring | SRE Commander |
| Feedback loop established | Analytics instrumented | Analytics Instrumenter |
| Incident review (if any) | Postmortem completed | Incident Commander |

### Approval Required

- SRE (SLO validation)
- Product (feature acceptance)

### Blocking Conditions

- SLO not meeting targets
- Critical incidents unresolved
- Feedback loop not operational

---

## Human Approval Rules

Human review is **always required** for:

| Category | Reason | Approver |
|----------|--------|----------|
| Auth/authz logic | Security-critical | Security team |
| Destructive schema changes | Data loss risk | DBA + Engineering Lead |
| Payment flows | Financial risk | Security + Compliance |
| Policy exceptions | Governance override | CISO or delegate |
| Regulated data paths | Compliance requirement | Compliance team |

These are enforced by:
- CI policies (`policies/opa/security/high_risk_approvals.rego`)
- CODEOWNERS file
- PR templates with required checkboxes

---

## Gate Bypass Policy

Gates can only be bypassed with:

1. **Executive approval** (CEO, CTO, or CISO)
2. **Written justification** (recorded in decision log)
3. **Compensating controls** (documented)
4. **Time-bound exception** (automatic expiry)

All bypasses are:
- Logged to audit trail
- Reviewed in weekly governance meeting
- Subject to post-incident review if issues arise

---

## Change Request Workflow

After Concept Lock, changes to locked artifacts MUST go through the formal Change Request (CR) process. This prevents "casual" scope creep via chat or informal requests.

### Change Request Types

| Type | Description | Impact Assessment Required |
|------|-------------|---------------------------|
| **Feature** | New functionality not in original scope | Yes - scope, budget, timeline |
| **Region** | Add/change operational regions | Yes - compliance, data residency |
| **Tools** | Add/change external integrations | Yes - security, budget |
| **Brand** | Modify Design OS Draft (palette, typography) | Yes - design, assets |
| **Assets** | Add/modify asset requirements | Yes - design, cost |
| **Security** | Change auth, data classification, or compliance tier | Yes - security, compliance |

### Change Request Schema

```json
{
  "$schema": "https://itqahn.io/schemas/change-request/v1",
  "cr_id": "cr-xyz123",
  "concept_lock_id": "concept-lock-abc123",
  "type": "feature|region|tools|brand|assets|security",
  "status": "draft|submitted|under_review|approved|rejected|implemented",
  "requested_by": "user@example.com",
  "requested_at": "2026-01-08T14:00:00Z",

  "change": {
    "summary": "Add payment processing capability",
    "rationale": "Business requirement for monetization",
    "affected_modules": ["journeys_scope", "region_profile"],
    "details": { }
  },

  "impact_analysis": {
    "scope_impact": "Adds 3 new journeys, expands MVP",
    "budget_impact": {
      "token_budget_increase": 50000,
      "cost_estimate_usd": 1200
    },
    "timeline_impact": "Adds ~5 days to delivery",
    "compliance_impact": "Requires PCI compliance tier upgrade",
    "security_impact": "Adds payment provider integration",
    "design_impact": "Requires payment flow wireframes"
  },

  "gates_affected": {
    "rerun_required": ["gate_1_validation", "risk_assessment"],
    "new_approvals_required": ["security", "compliance"]
  },

  "approvals": [
    {
      "role": "product_owner",
      "status": "approved",
      "approver": "po@example.com",
      "timestamp": "2026-01-08T15:00:00Z"
    }
  ]
}
```

### Change Request Workflow

```
1. User requests change via Portal
       │
       ▼
2. System runs impact analysis
       │
       ├── Scope impact: Which journeys/features affected?
       ├── Budget impact: Additional tokens/cost?
       ├── Timeline impact: Delay estimate?
       ├── Compliance impact: Tier change needed?
       └── Design impact: New wireframes/assets?
       │
       ▼
3. Impact summary presented to user
       │
       ├── User cancels → CR closed
       │
       └── User confirms → CR submitted
       │
       ▼
4. Required approvers notified
       │
       ├── Security (if security type)
       ├── Compliance (if compliance impact)
       ├── FinOps (if budget impact)
       └── Product Owner (always)
       │
       ▼
5. Approvers review and decide
       │
       ├── Any rejection → CR rejected (with feedback)
       │
       └── All approved → CR approved
       │
       ▼
6. Gates re-run if required
       │
       ├── Validation fails → CR blocked, feedback provided
       │
       └── Validation passes → CR ready to implement
       │
       ▼
7. Concept Lock artifact updated
       │
       └── New version created (immutable chain)
```

### Change Request Enforcement

```rego
# policies/opa/concept/change_request.rego
package itqahn.concept

# Block direct modifications to locked artifacts
deny[msg] {
  input.action == "modify"
  input.artifact.type == "concept-lock"
  input.artifact.status == "locked"
  not input.change_request.status == "approved"
  msg := "Cannot modify locked Concept Lock without approved Change Request"
}

# Require re-gating for compliance-impacting changes
require_gate_rerun[gate] {
  input.change_request.type == "security"
  gate := "risk_assessment"
}

require_gate_rerun[gate] {
  input.change_request.impact_analysis.compliance_impact != ""
  gate := "compliance_tier_validation"
}
```

---

## Related Documents

- `docs/05-compliance/compliance-tiers.md` — Control requirements by tier
- `docs/05-compliance/evidence-pack.md` — Evidence Pack contents
- `docs/04-security/security-model.md` — Security gates
- `docs/01-product/requirements-schema.md` — Phase 1 output schemas
- `docs/03-platform/portal-webapp.md` — Phase 1 dashboard UX
- `templates/governance/APPROVALS.md` — Approval workflow template

---

**Version**: 2.2.0 | **Date**: 2026-01-08
