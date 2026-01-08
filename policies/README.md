# Policies

This folder contains **policy-as-code** for Itqahn.

Policies are used to enforce:
- tool allowlists (MCP governance)
- supply chain integrity (SBOM + provenance)
- deployment rules (Evidence Pack required)
- UI Design Jail rules
- security and secrets constraints
- finops circuit breakers
- high-risk change approvals

## Policy layers

- `opa/` — decision policies (Rego) evaluated by the orchestrator and CI
- `kyverno/` — Kubernetes admission policies for cluster-level enforcement
- `policy-catalog.md` — mapping of policies to gates and compliance tiers

## How policies are used

1. **During workflows**: before executing tool calls or risky actions
2. **In CI**: to block merges that violate governance
3. **At deployment**: admission rejects artifacts without evidence or signatures

## Change management

- Policies are versioned and reviewed like code.
- Breaking changes require:
  - a migration note,
  - an announced effective date,
  - and a rollout plan.

See: `docs/08-security-model.md`, `docs/10-supply-chain-and-provenance.md`.
