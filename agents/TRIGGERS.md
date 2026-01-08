# Agent Triggers (Canonical)

Triggers define when Itqahn invokes an agent automatically.

## Workflow triggers

- New intake → intent-interviewer, scope-guard, requirements-writer
- Concept lock → cto-architecture, ciso-security, compliance-tier-decider
- UI changes → design-jail-warden, accessibility-specialist, visual-regression-keeper
- API changes → api-contract-guardian, contract-test-writer
- Dependency changes → dependency-sentinel, license-compliance-checker
- Any merge to main → audit-evidence-notary
- Budget anomaly → token-budget-enforcer, denial-of-wallet-detector
- Policy denial → policy-author + remediation owner
- CI failure → test-failure-investigator
- Incident declared → incident-commander, incident-forensics, runbook-author
- Drift threshold exceeded → drift-auditor

## Repo event triggers (examples)

- PR opened:
  - run: test-strategist (if no tests), appsec-reviewer (if auth/integration changed)
- PR labeled `ui`:
  - run: design-jail-warden, accessibility-specialist
- PR labeled `migration`:
  - run: migration-specialist, change-manager
- Release tag created:
  - run: release-manager, release-safety-guardian, audit-evidence-notary

## Human-triggered roles

Certain roles are invoked explicitly when needed:
- red-team-attacker
- chaos-engineer
- oscal-mapper

The orchestrator records all triggers as workflow events.
