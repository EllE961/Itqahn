# Principles (Non-Negotiables)

These principles are the **constitution** of Itqahn. They are not guidelines—they are enforced by policy gates and workflow constraints. Violations block progress.

---

## Priority Levels

- **P0**: Absolute requirements. Cannot be bypassed under any circumstances.
- **P1**: Core requirements. Require executive-level exception with documented justification.
- **P2**: Standard requirements. Require team-level exception with documented justification.
- **P3**: Best practices. Should be followed unless there's a clear technical reason.

---

## P0: Operator Mode Audit Trail

In **Operator Mode**, Itqahn runs Claude Code with `--dangerously-skip-permissions` to enable fully automated execution. Despite bypassing interactive approvals, **all actions MUST be audited, reversible, and evidenced**.

**Why**: Automation speed requires trust. Trust requires proof. Every automated action must leave a trail that enables post-hoc review, rollback, and compliance verification.

**Enforcement**:
- Every Operator Mode run generates a **Run Evidence Record** (run ID, inputs, outputs, policy decisions)
- All GitHub operations (issues, PRs, merges) are logged with Run ID linkage
- All high-risk actions are recorded in immutable audit log before execution
- Compensation/rollback procedures are pre-computed where possible
- Circuit breakers halt execution on anomalous behavior
- Kill switch available in dashboard for immediate halt

**Operator Mode does NOT bypass**:
- Policy evaluation (OPA gates still run)
- Evidence Pack requirements (still generated and signed)
- Audit logging (still captured for every action)
- Budget circuit breakers (still enforced)
- Secret isolation (credentials still never exposed to agents)

---

## P0: Durable State Is Mandatory

All multi-step work must run in a **durable workflow** (Temporal).

**Why**: If an agent crashes, state is not lost. Work resumes from the last checkpoint. This is non-negotiable for reliability.

**Enforcement**:
- All agent orchestration runs via Temporal workflows
- Activities have retry policies and timeouts
- State is persisted, not held in memory

---

## P0: Least Privilege, Always

Agents get only the tools and permissions they need. **Role boundaries are enforced by policy**, not goodwill.

**Why**: Prevents privilege escalation, limits blast radius of failures, enables audit.

**Enforcement**:
- Agent permissions defined in `agents/PERMISSIONS.md`
- MCP allowlists in `policies/opa/mcp/allowlist.rego`
- Vault policies scope secret access by identity

---

## P0: Secretless by Default

Agents must never receive long-lived credentials. Access is mediated via **workload identity** + **dynamic secrets**.

**Why**: Long-lived secrets get leaked. Dynamic, identity-bound secrets limit exposure.

**Enforcement**:
- SPIFFE/SPIRE for workload identity
- Vault issues short-TTL dynamic credentials
- No secrets in environment variables, configs, or code

---

## P0: GitHub as System of Record

GitHub is the **single source of truth** for all code, requirements, and execution state. All work items, PRs, merges, and releases are created and managed through GitHub automation—never manually by users in Operator Mode.

**Why**: Manual GitHub operations create audit gaps, inconsistent metadata, and drift from the orchestration state. Automated GitHub operations ensure traceability from requirement to deployment.

**Enforcement**:
- All issues, PRs, and releases are created programmatically via `gh` CLI or GitHub API
- Every commit includes Run ID and Issue ID in message
- Every PR is linked to a parent issue and workflow
- Merge queue is mandatory for all production branches
- Auto-merge is enabled only when all required checks pass
- Tags and releases are created automatically from Evidence Pack
- CODEOWNERS and branch protection are enforced at repository level

**GitHub artifacts Itqahn manages**:
| Artifact | Created By | Linked To |
|----------|-----------|-----------|
| Epic issue | Project creation | Concept Lock |
| Work item issue | Plan phase | Journey/feature |
| Branch | Work item start | Issue ID |
| Commits | Build phase | Run ID + Issue ID |
| PR | Work item completion | Work item issue |
| Check runs | CI pipeline | PR + Evidence Pack |
| Merge | Auto-merge | PR approval |
| Release | Deploy phase | Tag + Evidence Pack |

---

## P0: Policy Before Action

No commit, deploy, environment creation, or secret access is allowed unless:
1. The action is policy-approved, and
2. The resulting artifact can be audited.

**Why**: Prevents unauthorized actions. Creates audit trail.

**Enforcement**:
- OPA gates on CI/CD pipelines
- Kyverno admission control on Kubernetes
- Git branch protection with required checks

---

## P0: Evidence Is the Product

The deployable unit is not "a container". It is an **Evidence Pack**: build provenance, SBOM, scans, tests, approvals.

**Why**: You cannot audit a running container. You can audit the evidence that proves how it was built.

**Enforcement**:
- Deploy gate requires Evidence Pack manifest
- Provenance verification at deploy time
- SBOM analysis for license/vulnerability compliance

---

## P0: Context Engineering over Vibe Coding

All work MUST follow structured workflows. Implementation without specification is prohibited.

**Why**: Unstructured AI-assisted development produces inconsistent, untestable, and unmaintainable output. "Vibe coding"—implementing from vague prompts—leads to scope creep, context rot, and silent failures.

**Enforcement**:
- Every implementation begins with an approved PRP (Product Requirements Prompt)
- PRPs are generated from structured INITIAL documents
- No code is written without explicit requirements and examples
- Dashboard blocks execution without approved PRP
- Validation gates catch unspecified behavior

**Context Engineering Workflow**:
| Phase | Input | Output | Gate |
|-------|-------|--------|------|
| **Intake** | Feature request | INITIAL document | Schema validation |
| **Plan** | INITIAL | Approved PRP | User approval |
| **Execute** | PRP | Code + tests | Validation gates |
| **Verify** | Artifacts | Evidence Pack | All gates pass |

---

## P0: Validation Gates Are Non-Negotiable

Even in Operator Mode with full automation, **all validation gates MUST run and pass**. Gates are not optional checks—they are mandatory correctness proofs.

**Why**: Autonomous execution without validation is reckless. Gates provide the safety guarantees that make autonomy acceptable.

**Enforcement**:
- All PRP executions run defined validation gates
- Blocking gates halt execution on failure
- Failed gates trigger "iterate until pass" protocol
- After max attempts (3), escalation to dashboard is mandatory
- No merge without all required gates passing
- Gate results are recorded in Evidence Pack

**Gate Categories**:
| Category | Examples | Bypass Allowed |
|----------|----------|----------------|
| **Format/Schema** | JSON validation, YAML lint | Never |
| **Code Quality** | Lint, typecheck, format | Never |
| **Tests** | Unit, integration, E2E | Never |
| **Security** | SAST, secrets, dependencies | Never |
| **Drift** | Plan alignment, design consistency | Threshold-based |
| **Docs** | API docs, README | Configurable |

---

## P1: Progressive Disclosure

Context windows are finite resources. Load only what matters now; write everything else to files.

**Why**: Context rot degrades AI output quality. Polluting context with irrelevant information, verbose outputs, or stale state causes hallucination, inconsistency, and instruction-following failures.

**Enforcement**:
- CLAUDE.md (always-on rules) MUST stay under 200 lines
- Context budget capped at 70% utilization (hard stop at threshold)
- Decisions written to `memory/decision-log.md`, not kept in context
- Exploration results written to `memory/research/`, not dumped to context
- Long outputs written to `artifacts/`, not held in context
- Session boundaries enforced when tasks exceed capacity

**Context Allocation**:
| Content Type | Where It Lives | Loaded When |
|--------------|----------------|-------------|
| Always-on rules | CLAUDE.md | Every session |
| Current task spec | PRP artifact | Active execution |
| Decisions | memory/decision-log.md | On demand |
| Project map | memory/project-index.md | On demand |
| Historical context | Evidence Packs | Never (archived) |

---

## P1: Keep Always-On Rules Minimal

The root rules file (CLAUDE.md) MUST be kept small and stable. It is the constitution, not the encyclopedia.

**Why**: Always-on rules consume context budget in every session. Bloated rules reduce capacity for actual work. Rules that change frequently cause inconsistent behavior.

**Enforcement**:
- CLAUDE.md capped at 200 lines maximum
- Changes to CLAUDE.md require review and justification
- Detailed procedures belong in memory files, not CLAUDE.md
- CLAUDE.md contains pointers to documentation, not full documentation
- Version tracking and change log for CLAUDE.md modifications

**CLAUDE.md Structure**:
```markdown
# Project Rules (< 200 lines)
- Identity and role
- Critical constraints (security, compliance)
- Memory file pointers
- Context budget thresholds
- Hook references
- Links to detailed docs
```

---

## P1: Design OS as Source of Truth

All UI is governed by a **versioned Design OS**. Design OS defines the complete vocabulary of tokens, components, patterns, and accessibility rules that agents may use.

**Why**: Without a versioned source of truth, agents invent styles, components diverge, and accessibility regresses. Design OS makes the allowed vocabulary explicit and enforceable.

**Enforcement**:
- Design OS versioned in Git with SemVer tags
- `tokens.json` and `components.json` are the only valid styling sources
- UI releases must pin a Design OS version in Evidence Pack
- OPA policies verify Design OS version exists and is not deprecated

---

## P1: Design Jail for UI

Agents do not invent UI styling. UI is composed using **approved components** and **design tokens** from Design OS only. **Design Jail enforcement depends on Design OS artifacts existing and being valid.**

**Why**: Prevents visual inconsistency, accessibility failures, and design debt.

**Enforcement**:
- Design Jail Warden agent reviews all UI changes
- `policies/opa/ui/design_jail.rego` blocks non-compliant changes
- Token lint rejects raw CSS values (hex colors, pixel values)
- Component allowlist rejects unknown components
- Visual regression tests against Design OS baselines
- Accessibility gates (axe) enforce WCAG AA

---

## P1: Assets Governed by Design OS

All generated visual assets (icons, illustrations, photos) must comply with **Design OS constraints**. Assets are validated against style anchors, palette rules, and accessibility requirements.

**Why**: Without governance, generated assets drift from brand standards, introduce licensing risks, and bypass accessibility requirements. Design OS extends to assets, not just UI components.

**Enforcement**:
- Asset generation requires Design OS version in spec
- Style anchor matching via embedding similarity
- Palette extraction validates against Design OS tokens
- Assets blocked from production until registered in Asset Registry
- Evidence Pack includes asset provenance and validation results

---

## P1: Repair Before Regeneration

When assets need updates, prefer **deterministic transforms** (crop, resize, recolor) over regeneration. Regeneration is expensive and non-deterministic.

**Why**: Generation is costly (compute, API fees, review time). Many asset updates are simple transforms that should not require regeneration. Cost efficiency is a reliability concern.

**Enforcement**:
- Asset Factory attempts repair first when drift detected
- Regeneration requires justification if repair was skipped
- Cost circuit breakers limit regeneration loops
- Metrics track repair vs. regeneration ratio

---

## P1: Cost Is a Reliability Metric

Token usage and cloud spend are governed by budgets, circuit breakers, and anomaly detection.

**Why**: Unbounded costs are a reliability failure. "Denial of wallet" is a real attack vector.

**Enforcement**:
- Per-workflow, per-phase, per-tenant token budgets
- Circuit breakers halt runaway spending
- FinOps agents monitor and alert on anomalies
- Asset generation budgets enforced per-workflow

---

## P1: Drift Must Be Measured

The system continuously measures divergence between **requirements** (PRD) and **implementation** (code/UI).

**Why**: Drift is how features become incorrect over time. Measuring it enables correction.

**Enforcement**:
- Drift Auditor agent runs on every PR
- Semantic similarity scoring (PRD ↔ code ↔ UI)
- Drift exceeding threshold triggers review

---

## P1: Safe Autonomy

Autonomous operation MUST remain **observable, auditable, and reversible**. Speed does not justify opacity.

**Why**: Itqahn operates with high autonomy (Operator Mode, self-improvement). This autonomy is only acceptable if every action can be observed in real-time, audited after the fact, and reversed if necessary. Safe Autonomy is the principle that enables trust in automated systems.

**Enforcement**:
- All improvements deploy behind feature flags with automatic rollback
- Review Checkpoints capture state at every pause boundary
- Kill switch available for immediate halt of all automated operations
- Evidence Pack includes all decision points and outcomes
- No silent changes—every modification creates auditable records

---

## P1: Checkpoint-Based Resumption

When work pauses, **state MUST be preserved** at safe boundaries for later resumption.

**Why**: Autonomous workflows may be paused for drift review, budget limits, or operator intervention. Losing progress wastes resources and erodes trust. Checkpointing enables pause/review/resume without loss.

**Enforcement**:
- Track Assurance creates Review Checkpoints at drift thresholds
- Temporal workflows persist state to durable storage
- Checkpoints are immutable artifacts in Evidence Pack
- Resume options preserve completed work while allowing course correction
- Stuck workflow detection triggers emergency checkpoint creation

---

## P1: Parity Before Cutover

Legacy rebuilds MUST demonstrate **behavioral equivalence** before cutover.

**Why**: Rebuilding a system is useless if it behaves differently than the original. Parity verification ensures the rebuilt system matches legacy behavior before traffic is switched.

**Enforcement**:
- Parity Harness required for all Legacy Rebuild workflows
- API parity, database parity, UI parity, and behavior parity tests
- Cutover blocked until parity score exceeds threshold
- Automatic rollback triggers if post-cutover metrics regress
- Parity evidence required in Evidence Pack

---

## P1: Self-Improvement Requires Evaluation

Itqahn MAY improve itself, but **only through the Evaluator Harness** with success criteria and rollback capability.

**Why**: Unvalidated self-modification is dangerous. Improvements must prove they help before deployment. Regression detection and automatic rollback ensure bad changes don't persist.

**Enforcement**:
- All Improvement Candidates pass 5-stage Evaluator Harness
- Success criteria defined with baseline and target metrics
- Automatic rollback on threshold breach
- Feature flags control gradual rollout (5% → 25% → 50% → 100%)
- Improvement Review Board oversight for high-impact changes
- No silent changes—all improvements via auditable PRs

---

## P2: Human Review Where It Matters

Human approval is required for:

| Category | Reason |
|----------|--------|
| Authentication/authorization paths | Security-critical |
| Destructive schema changes | Data loss risk |
| Payment flows | Financial risk |
| High-risk policy exceptions | Governance override |
| Regulated data handling | Compliance requirement |

**Enforcement**:
- PR templates require security/compliance checkboxes
- High-risk changes require CODEOWNERS approval
- Audit log captures all human approvals

---

## P2: Production Parity

Tests run in **ephemeral environments** that match production topology and policies as closely as possible.

**Why**: Tests that pass in a different environment provide false confidence.

**Enforcement**:
- CI creates production-like namespaces
- Same network policies, resource limits, identity
- Ephemeral environments destroyed after tests

---

## P3: Everything Must Be Observable

If you cannot observe it, you cannot operate it. Every service ships with logs, metrics, traces, and SLOs.

**Why**: Enables incident response, capacity planning, and continuous improvement.

**Enforcement**:
- Service templates include observability by default
- SLO definitions required before production deploy
- Alert runbooks linked to dashboards

---

## Principles in Code

These principles appear as:
- **Policy files** in `policies/opa/` and `policies/kyverno/`
- **Workflow steps** in `templates/`
- **Agent contracts** in `agents/AGENT-CONTRACT.md`
- **Gate definitions** in `docs/01-product/lifecycle-phase-gates.md`
- **Design OS artifacts** in `templates/design/` and `docs/03-platform/design-os.md`
- **Asset Factory specification** in `docs/03-platform/asset-factory-imageops.md`
- **Asset MCP integration** in `docs/07-integrations/mcp/mcp-assets.md`
- **Track Assurance specification** in `docs/03-platform/track-assurance.md`
- **Legacy Rebuild specification** in `docs/03-platform/legacy-rebuild.md`
- **Continuous Improvement specification** in `docs/06-operations/itqahn-continuous-improvement.md`
- **Context Engineering Program** in `docs/03-platform/context-engineering.md`
- **PRP templates** in `templates/product/PRP.md` and `templates/product/INITIAL.md`
- **Session verification** in `templates/operations/session-end-verification.md`

---

**Version**: 2.5.0 | **Date**: 2026-01-08
