# Glossary

Shared vocabulary for Itqahn. All agents and humans must use these definitions consistently.

---

## A

**Activity**
: A single durable step in a Temporal workflow. Activities are retryable, timeout-bounded, and idempotent.

**Adaptive Interview**
: The Phase 1 intake process for new projects. A branching, multiple-choice questionnaire that captures project requirements, design preferences, and asset needs. Questions adapt based on previous answers. See `docs/01-product/lifecycle-phase-gates.md`.

**Asset Drift**
: Divergence between a generated asset and its style anchor, measured by embedding similarity. Drift scores above threshold trigger repair (re-edit) or regeneration. See `docs/03-platform/asset-factory-imageops.md`.

**Asset Evidence**
: Artifacts proving asset provenance and compliance in an Evidence Pack: generation parameters, model version, style anchor reference, drift score, lint results, and cryptographic signatures. Required for any asset release.

**Asset Factory**
: The automated pipeline for generating, validating, and managing visual assets (icons, illustrations, photos). All assets must comply with Design OS constraints and pass lint checks. Also known as ImageOps.

**Asset Manifest**
: The output record of an asset generation workflow (`asset-manifest.json`). Contains provenance, validation results, platform outputs, and signatures.

**Asset Registry**
: Namespaced storage for approved assets. Assets must be registered before use in production. Registry entries include version, tags, digest, and approval metadata.

**Asset Requirements Manifest**
: The Phase 1 artifact specifying all visual assets needed for a project: logos, app icons, favicons, marketing assets, UI icon policy, illustrations, and photos. Captured during Adaptive Interview before Concept Lock. See `docs/01-product/requirements-schema.md`.

**Asset Spec**
: The input specification for asset generation (`asset-spec.json`). Defines asset type, style anchor, Design OS version, platform targets, and generation constraints.

**Assumptions Register**
: A Phase 1 artifact tracking all "Not sure" responses and deferred decisions. Each assumption includes risk level, safe default (if any), and resolution deadline. Concept Lock is blocked if assumptions exceed 30% of total questions.

**Agent**
: A role-scoped worker that produces artifacts under policy constraints. Agents are not chatbots—they produce decisions, specs, code, or evidence.

**Allowlist**
: An explicit list of permitted items (tools, MCP servers, dependencies). Anything not on the list is denied by default.

**ASVS**
: OWASP Application Security Verification Standard. A framework for testing web application security. Itqahn enforces ASVS L1 minimum, L2 for production.

**Attestation**
: A signed statement asserting facts about an artifact (e.g., "this binary was built from commit X by pipeline Y").

**Auto-merge**
: GitHub feature that automatically merges a PR when all required status checks pass and required reviews are obtained. In Operator Mode, auto-merge is the default merge mechanism—manual merge buttons are not used. See `docs/07-integrations/git-integration.md`.

---

## B

**Baseline Design OS**
: The standard Design OS provided by Itqahn that all tenants inherit. Contains core tokens, components, and accessibility rules. Tenants may extend but cannot bypass baseline requirements.

**Baseline Tier**
: The default compliance tier for non-sensitive internal tools and prototypes. Requires standard gates but no regulated controls.

**Build Type**
: A category of deliverable (Service, Web App, Mobile App, Integration, Data Product, Infrastructure Change, Documentation-only).

---

## C

**Context Engineering**
: The discipline of structuring work, managing context windows, and enforcing validation gates to ensure reliable, parallelizable, and self-correcting AI-assisted development. Itqahn's Context Engineering Program defines how work flows from INITIAL through PRP to validated Evidence Packs. See `docs/03-platform/context-engineering.md`.

**Context Rot**
: Degradation in AI output quality that occurs when context windows become polluted with irrelevant information, outdated state, or excessive history. Symptoms include hallucination, inconsistency, and failure to follow instructions. Prevented through progressive disclosure and session boundaries.

**Change Request (CR)**
: A formal request to modify a locked Concept Lock artifact. CRs classify change type (feature, region, brand, assets, security), run impact analysis, and require approvals before implementation. Changes cannot be made via casual chat after Concept Lock.

**Catch-up Pack**
: A compressed summary artifact enabling context restoration after reset or session handoff. Contains key decisions, current state, and file references. Used by Claude Code workers to resume work without loading full conversation history. See `docs/06-operations/claude-code-operating-model.md`.

**Circuit Breaker**
: A mechanism that halts execution when thresholds are exceeded (budget, errors, retries). Prevents runaway costs and cascading failures.

**Context Budget**
: The maximum percentage (70%) of Claude Code's context window that may be used before triggering Context Reset. Exceeding the budget forces production of a Context Reset Pack and session restart. See `docs/06-operations/claude-code-operating-model.md`.

**Context Reset Pack**
: Artifact produced when a Claude Code worker exceeds its context budget. Contains state snapshot, pending work description, resume instructions, and artifact references. Enables continuation in a fresh session. See `docs/06-operations/claude-code-operating-model.md`.

**Coordinator**
: The orchestration layer that spawns Claude Code workers, manages Git worktrees, aggregates results, resolves conflicts, and triggers merges. A single Coordinator manages all workers for a given Run. See `docs/06-operations/claude-code-operating-model.md`.

**Cutover Plan**
: A documented procedure for transitioning from legacy to rebuilt system. Includes pre-cutover checklist, step-by-step migration steps, rollback triggers, and post-cutover monitoring requirements. Required for all Legacy Rebuild completions. See `docs/03-platform/legacy-rebuild.md`.

**Component Contract**
: The specification of an approved UI component including its name, variants, props, accessibility requirements, and platform support. Defined in `components.json` as part of Design OS.

**Compliance Tier**
: Classification determining which controls apply (Baseline, Sensitive, Regulated). See `docs/05-compliance/compliance-tiers.md`.

**Concept Lock**
: The output artifact of Phase 1 (Adaptive Interview). An immutable, versioned record of all project decisions: Project Card, Region Profile, Journeys & Scope, Design OS Draft, Wireframe Choices, Asset Requirements, and Assumptions. All subsequent work must reference the Concept Lock version.

**Confidence Meter**
: A Phase 1 dashboard component showing the percentage of questions answered definitively vs. "Not sure". High confidence (>70%) indicates clear requirements; low confidence (<70%) may block Concept Lock.

**Control Plane**
: The management layer that orchestrates workflows, enforces policies, and manages identity. Contrast with Data Plane.

---

## D

**Data Plane**
: The execution layer where tenant workloads run. Isolated from control plane and other tenants.

**Design Drift**
: Divergence between Design OS specifications and actual UI implementation. Measured by the Drift Checker comparing tokens used, components instantiated, and patterns followed against Design OS definitions.

**Design Evidence**
: Artifacts proving Design OS compliance in an Evidence Pack: token version, component version, visual regression report, and accessibility scan results. Required for any UI release.

**Design Jail**
: Policy that prohibits free-form UI styling by agents. All UI must use approved components and design tokens from a versioned Design OS. Enforcement depends on Design OS artifacts existing and being valid.

**Design OS Draft**
: The preliminary Design OS configuration captured during Phase 1 (Adaptive Interview). Contains palette, typography, density, corner style, and theme choices. Becomes the basis for the project's Design OS version after Concept Lock.

**Design OS**
: The versioned, enforceable foundation for all UI in Itqahn. Comprises `tokens.json`, `components.json`, `patterns/`, `a11y-rules.md`, and `visual-baselines/`. Acts as the single source of truth for all visual design decisions.

**Design OS Release**
: A tagged, immutable version of Design OS following SemVer. Breaking changes (token renames, component removals) require major version bump. Consuming applications pin to specific Design OS versions.

**Design Tokens**
: Named values (colors, spacing, typography) defined in `tokens.json` using W3C Design Tokens format. Agents may only use these tokens, not raw CSS values. Part of Design OS.

**Draft Mode**
: The editable state of a Concept Lock during Phase 1 interview. Users can freely modify answers, and all changes are logged as revisions. No build work can begin until the Concept Lock transitions to Locked Mode.

**Drift**
: Divergence between requirements (PRD), implementation (code), and behavior (UI). Measured continuously by the Drift Auditor.

**Drift Score**
: A normalized value from 0.0 (no drift) to 1.0 (complete divergence) measuring alignment between approved specifications and current implementation. Calculated as a weighted sum of plan drift, code drift, UI drift, and behavior drift. See `docs/03-platform/track-assurance.md`.

**Deterministic Transform**
: An asset operation (crop, resize, convert, watermark) that produces identical output for identical input. Preferred over regeneration for asset updates to reduce cost and maintain consistency.

**Durable Execution**
: Workflow execution that survives crashes and restarts. State is persisted and workflows resume from their last checkpoint.

---

## E

**Examples Library**
: A collection of validated input/output pairs (golden cases) that define expected behavior for a feature or PRP. Used for testing, validation, and as concrete specifications. Examples are required in every PRP and drive test generation.

**Evaluator Harness**
: The validation system for testing Improvement Candidates before deployment. Consists of five stages: static analysis, unit evaluation, integration evaluation, canary evaluation, and gradual rollout. See `docs/06-operations/itqahn-continuous-improvement.md`.

**Evidence Pack**
: The deployable unit. A signed bundle containing:
  - Build provenance (SLSA)
  - SBOM (CycloneDX)
  - Security scans
  - Test results
  - Approval records
  - Review Checkpoint trail (for Track Assurance runs)
  - Legacy rebuild evidence (for rebuild workflows)
  - Improvement context (active improvements affecting the run)

---

## G

**Gate**
: A checkpoint that must pass before work proceeds. Hard gates block on failure; soft gates warn but allow override with justification.

**Git Evidence**
: Artifacts in an Evidence Pack proving GitHub traceability: PR URLs, commit SHAs, check run results, merge timestamps, and release tags. Required for all builds. See `docs/05-compliance/evidence-pack.md`.

**GitHub Automation Program**
: Itqahn's fully automated GitHub workflow where all issues, branches, PRs, merges, and releases are created programmatically—never manually by users. Includes merge queue, auto-merge, and automated release tagging. See `docs/07-integrations/git-integration.md`.

**GitOps**
: Deployment model where Git is the source of deployment intent. Changes flow: PR → merge → sync to cluster.

**Golden Path**
: The recommended, pre-validated way to accomplish a task. Implemented via templates and Backstage scaffolders.

---

## I

**INITIAL**
: A structured feature request document that captures user intent before PRP generation. Contains FEATURE, EXAMPLES, DOCUMENTATION, CONSTRAINTS, ACCEPTANCE, and GOTCHAS sections. The INITIAL is the input to `/generate-prp` and defines the scope boundaries for implementation. See `templates/product/INITIAL.md`.

**Integration Branch**
: A shared branch (typically `integration-{run_id}`) where validated work from multiple parallel worktrees is merged. The Merge Captain manages integration branch health and conflict resolution. Integration branch is the staging point before merge to main.

**Idempotency**
: Property where repeating an operation produces the same result. Required for all activities and API operations.

**ImageOps**
: Alternative name for Asset Factory. The automated pipeline for generating, editing, and managing visual assets under Design OS governance.

**Improvement Candidate**
: A proposed change to Itqahn generated from improvement signals (operator feedback, incident learnings, drift patterns, CI failures, analytics). Each candidate has defined success criteria, rollback triggers, and must pass the Evaluator Harness before deployment. See `docs/06-operations/itqahn-continuous-improvement.md`.

**Improvement PR**
: A Pull Request created by the Improvement Pipeline to deploy an approved Improvement Candidate. Includes evaluation report, success criteria, rollback plan, and feature flag configuration. All Improvement PRs are code-reviewed and deployed behind feature flags.

---

## J

**Journeys & Scope**
: A Phase 1 artifact defining what the user can DO (not features). Includes user journeys with steps, success criteria, and MVP boundaries. Journey priorities determine what's in vs. out of MVP scope.

---

## K

**Kill Switch**
: An emergency control in the Itqahn dashboard that immediately halts all Operator Mode workflows, freezes merges, revokes active tool permissions, and optionally rotates secrets. Available to operators for immediate incident containment. See `docs/06-operations/runbooks.md`.

**Kyverno**
: Kubernetes-native policy engine for admission control. Used for cluster-level enforcement alongside OPA.

---

## L

**Least Privilege**
: Principle that agents and services receive only the minimum permissions required for their role.

**Legacy Rebuild**
: The process of importing and modernizing existing, messy, or half-done repositories into well-structured, compliant projects. Supports two strategies: Strangler-style Modernization (incremental) and Clean Rebuild (from specification). See `docs/03-platform/legacy-rebuild.md`.

**Legacy Snapshot**
: An immutable Git tag (`legacy-snapshot`) created at the moment of legacy project import. Preserves the complete original repository state, discovery artifacts, and initial security scan results. Required for audit trail and rollback reference.

**Locked Mode**
: The immutable state of a Concept Lock after user approval. Changes in Locked Mode require a formal Change Request (CR). All implementation work references the locked artifact version.

---

## M

**MCP (Model Context Protocol)**
: Standard protocol for connecting AI agents to external tools and services. All MCP servers must be allowlisted.

**Merge Captain**
: The designated worktree worker responsible for managing the integration branch during parallel execution. Merge Captain handles shared files (package.json, tsconfig.json, etc.), resolves conflicts, and coordinates the final merge to main. Only one Merge Captain exists per run.

**Merge Queue**
: GitHub feature that batches and sequences PR merges to prevent race conditions and ensure CI passes on the merge result, not just the PR branch. Mandatory for production branches in Itqahn. See `docs/07-integrations/git-integration.md`.

**Merge Train**
: The sequence of PRs waiting to merge through the merge queue. Each PR in the train is tested against the expected state after all preceding PRs merge. Ensures no integration failures at merge time.

---

## N

**NanoBanana**
: The primary image generation provider for Itqahn's Asset Factory. Accessed via API key stored in Vault. Supports text-to-image, image-to-image, background removal, upscaling, and style transfer. See `docs/07-integrations/mcp/mcp-nanobanana.md`.

---

## O

**Operator Mode**
: Itqahn's fully automated execution mode where Claude Code runs with `--dangerously-skip-permissions` under a Claude Code Max subscription. Dashboard-driven with no terminal interaction. All actions are still audited, evidence-tracked, and policy-governed despite bypassing interactive approvals. See `docs/03-platform/portal-webapp.md`.

**OPA (Open Policy Agent)**
: Policy engine using Rego language for decision-making. Used for pipeline gates, access control, and compliance checks.

---

## P

**Parity Harness**
: The testing framework ensuring behavioral equivalence between legacy and rebuilt systems during Legacy Rebuild. Includes API parity testing, database parity comparison, UI visual regression, and behavior scenario verification. See `docs/03-platform/legacy-rebuild.md`.

**Pattern Library**
: A collection of pre-approved interaction patterns (e.g., auth-flow, data-table, form-wizard) defined in `patterns/` within Design OS. Agents must compose UI using these patterns for complex flows.

**Plan Mode**
: The initial phase of every Claude Code session where a structured Plan artifact is produced before any code is written. Requires minimum 2 refinement cycles unless the plan is trivially complete. Plan is saved to `plans/run-{id}/{task}.md`. See `docs/06-operations/claude-code-operating-model.md`.

**Progressive Disclosure**
: Context hygiene strategy where information is loaded only when needed and written to repo artifacts (not held in context). Keeps context usage below 70% threshold. Non-urgent information is stored in Catch-up Packs rather than kept in active context. See `docs/06-operations/claude-code-operating-model.md`.

**Phase 1**
: The first phase of Itqahn's delivery lifecycle. Consists of the Adaptive Interview that captures project requirements and produces the Concept Lock artifact. Also called "Start a Project".

**Phase Gate**
: A milestone in the delivery lifecycle requiring explicit approval. Four gates: Concept Lock, Experience Lock, Release Candidate, Post-Launch.

**Platform-correct Output**
: Asset variants automatically generated for each target platform (iOS asset catalogs, Android adaptive icons, web favicons). Asset Factory produces all required sizes and formats from a single source asset.

**Provenance**
: Cryptographic proof of how an artifact was built, from what inputs, and by which pipeline. Required for SLSA compliance.

**PRD (Product Requirements Document)**
: The specification defining what to build. Must follow the schema in `templates/product/PRD.md`.

**PRP (Product Requirements Prompt)**
: The canonical unit of work in Itqahn's Context Engineering Program. A structured specification that defines what to build, how to validate it, and what constitutes done. Generated from an INITIAL via `/generate-prp` and executed via `/execute-prp`. Every PRP includes context, requirements, examples, implementation plan, validation gates, edge cases, rollback procedures, and definition of done. See `docs/03-platform/context-engineering.md` and `templates/product/PRP.md`.

**Project Card**
: A Phase 1 artifact containing the foundational identity of a project: name, one-liner, build type, platforms, primary persona, and owner. The first module in the Adaptive Interview.

---

## R

**Run**
: A single execution of an Itqahn workflow, from start to completion. Each run has a unique Run ID, produces artifacts, and generates evidence. Runs are the primary unit of traceability across GitHub, CI, and Evidence Packs.

**Run Evidence Record**
: The complete audit record for an Operator Mode run. Includes Run ID, workflow type, inputs (Concept Lock, PRD), outputs (code, assets, Evidence Pack), policy decisions, GitHub artifacts created, cost metrics, and timestamps. Required for all Operator Mode executions.

**Run ID**
: A globally unique identifier for each Itqahn run (format: `run-{ulid}`). Included in all commit messages, PR descriptions, and Evidence Packs to enable full traceability from requirement to deployment.

**Region Profile**
: A Phase 1 artifact defining operational constraints based on target regions: primary/additional regions, locale, compliance requirements (GDPR, CCPA), data residency, currency, and timezone.

**Review Checkpoint**
: An immutable artifact capturing workflow state when Track Assurance pauses work for drift review. Contains drift analysis, workflow state snapshot, artifact references, and operator options (resume with replan, resume as-is, rollback, terminate). Checkpoints enable pause/review/resume without losing progress. See `docs/03-platform/track-assurance.md`.

**Regulated Tier**
: Compliance tier for workloads handling payments (PCI), health data (HIPAA), or government data (FedRAMP-style). Requires enhanced controls.

**Runbook**
: Step-by-step operational procedure for handling specific scenarios. Required format in `templates/ops/RUNBOOK.md`.

---

## S

**Safe Autonomy**
: The principle that autonomous systems can operate independently while remaining observable, auditable, and reversible. Itqahn achieves Safe Autonomy through Evidence Packs, Review Checkpoints, feature flags, automatic rollbacks, and kill switches. Autonomy increases efficiency; safety ensures trust.

**SBOM (Software Bill of Materials)**
: Inventory of all dependencies in an artifact. Format: CycloneDX. Required in every Evidence Pack.

**Sensitive Tier**
: Compliance tier for workloads handling PII, customer data, or enterprise auth. Between Baseline and Regulated.

**Session Budget**
: Maximum tokens and cost allowed for a single Claude Code session. Enforced by circuit breakers. Exceeding the session budget triggers Context Reset Pack production and session restart. See `docs/06-operations/claude-code-operating-model.md`.

**Session Ritual**
: Mandatory procedures at session start and end. Start-of-session ritual loads context, verifies prerequisites, and confirms the plan. End-of-session ritual runs validation gates, performs security hygiene checks, syncs documentation, generates evidence, and produces a summary. Sessions without proper end ritual are invalid. See `docs/03-platform/context-engineering.md`.

**Skill (Itqahn Skill)**
: An internal, standardized procedure executed by Claude Code without external tool calls. Token-efficient and deterministic. Examples: code generation, local file operations, running tests. Preferred over MCPs for all local operations. See `docs/06-operations/claude-code-operating-model.md`.

**SLO/SLI**
: Service Level Objective (target) / Service Level Indicator (measurement). Every service must define SLOs.

**SLSA (Supply-chain Levels for Software Artifacts)**
: Framework for software supply chain security. Itqahn targets SLSA L3 (isolated builds, provenance, verification).

**SPIFFE/SPIRE**
: Identity framework for workloads. Provides short-lived cryptographic identities (SVIDs) for zero-trust communication.

**Strangler-style Modernization**
: A Legacy Rebuild strategy that incrementally replaces legacy components while maintaining a working system. Components are migrated in dependency order through a facade layer. Named after the strangler fig pattern. Preferred when a working production system exists. See `docs/03-platform/legacy-rebuild.md`.

**Style Anchor**
: An approved visual style definition with an embedding (CLIP vector) used for drift detection. Generated assets must match their style anchor within threshold. Style anchors are versioned in `design-os/style-anchors/`.

**SVID**
: SPIFFE Verifiable Identity Document. A short-lived X.509 certificate or JWT proving workload identity.

---

## T

**Temporal**
: Workflow engine for durable orchestration. All multi-step work in Itqahn runs as Temporal workflows.

**Track Assurance**
: Itqahn's drift detection and review system. Monitors divergence between approved specifications and implementation. When drift exceeds thresholds, pauses work and surfaces a Review Checkpoint for operator decision. Also known as "Drift Review Mode". See `docs/03-platform/track-assurance.md`.

**Tenant**
: An isolated organizational unit with its own data, configurations, and resource limits.

**Tenant Design OS**
: A tenant-specific extension of Baseline Design OS. May override brand colors and add components but cannot remove baseline requirements or bypass accessibility rules. Enterprise tenants may operate fully independent Design OS instances.

**Token**
: A named design value (color, spacing, typography, etc.) defined in Design OS `tokens.json`. All UI styling must reference tokens—raw CSS values are prohibited.

---

## V

**Validation Gate**
: A checkpoint in the PRP execution that must pass before work continues. Gates are categorized as format/schema, code quality, tests, security, drift detection, and documentation. Blocking gates halt execution on failure; non-blocking gates log warnings. The "iterate until pass" rule requires automatic correction attempts before escalation. See `docs/03-platform/context-engineering.md`.

**Verification Pass**
: Mandatory end-of-session step where a Claude Code worker runs lint, tests, security scans, and repo rule validation. Produces a Verification Report artifact that must exist before PR creation. See `docs/06-operations/claude-code-operating-model.md`.

**Verification Prompt**
: The end-of-session command (`/end`) that triggers the mandatory verification ritual. Executes validation gates, security hygiene checks, documentation sync, plan alignment check, summary generation, and evidence pack creation. Sessions without verification prompt are invalid and their artifacts are not merged. See `templates/operations/session-end-verification.md`.

**VEX (Vulnerability Exploitability eXchange)**
: Format for communicating whether vulnerabilities are actually exploitable in a specific context. Used to reduce false positives.

**Visual Baseline**
: Reference screenshots stored in `visual-baselines/` within Design OS. Used for visual regression testing—any UI change must be compared against baselines. Changes to baselines require Design OS Maintainer approval.

---

## W

**Wireframe Choice Set**
: A Phase 1 artifact documenting the user's layout template selections for each screen type (home, listing, detail, form, etc.). Users visually select from 3-6 variants per screen type and can mix-and-match templates.

**Workflow**
: A durable, multi-step process orchestrated by Temporal. Composed of activities, signals, and queries.

**Worktree**
: An independent Git working directory sharing the same repository. Enables parallel work on different branches without conflicts. Each Claude Code worker operates in its own worktree. See `docs/07-integrations/git-integration.md`.

**Worktree Worker**
: A Claude Code session running in an isolated worktree with its own branch. Workers do not share working directories or context. Multiple Worktree Workers execute in parallel, coordinated by the Coordinator. See `docs/06-operations/claude-code-operating-model.md`.

---

**Version**: 2.6.0 | **Date**: 2026-01-08
