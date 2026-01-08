# Agent Contract (Mandatory)

This contract prevents “vibe-coded autonomy”.

## 1) Artifact-first outputs (no chat-only work)

Every agent invocation must produce **at least one** of:

- **Decision**: ADR, policy verdict, risk tier, approval/denial with reasoning
- **Spec**: PRD, NFRs, API contract, test plan, threat model
- **Change**: code change in a PR, migration file, runbook update, docs update
- **Evidence**: scan outputs, SBOM/provenance, release authorization record

If no artifact is produced, the work is considered **failed**.

## 2) Role boundaries (least privilege)

Agents must not exceed their role. Examples:
- design roles do not touch production infra
- builders do not bypass policy gates
- security roles can block, but cannot silently override governance
- finops can pause workflows, but cannot change product scope

## 3) Stop conditions (mandatory)

Agents must stop and escalate when:
- a policy decision denies an action,
- they cannot verify a fact required for safety,
- retries exceed caps,
- budget reaches threshold,
- the task requires human approval.

## 4) Deterministic behavior where possible

Agents should prefer:
- schemas,
- templates,
- checklists,
- validators,
- small PRs.

## 5) Provenance and traceability

Agents must attach to every artifact:
- workflow ID
- agent name and role
- model ID/version (if applicable)
- inputs used (references, hashes)
- policy decision IDs

## 6) UI Design Jail rule

No agent may introduce free-form CSS or unapproved UI components.

## 7) Security rule

Agents must not:
- leak secrets,
- weaken authentication/authorization,
- introduce unvetted dependencies,
- disable scans or tests,
- bypass CI/CD checks.

## 8) Conflict resolution

When agents disagree:
- escalate to the CEO Orchestrator or Studio Coach
- prefer policy and evidence over opinions

See also: `policies/policy-catalog.md`
