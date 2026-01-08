# Agent Permissions Matrix (Conceptual)

Actual enforcement is implemented through:
- MCP allowlists,
- Vault policies,
- OPA policies,
- Git branch protections,
- Kubernetes admission controls.

## Permission tiers

- **Read-only**: view repo, docs, tickets, dashboards.
- **Write (branch)**: open PRs in constrained paths.
- **Approve**: can issue an approval attestation (only certain roles).
- **Deploy**: deploy via GitOps only (never direct kubectl apply).

## High-level rules

- Executive roles: read + approve (no direct deploy)
- Engineering roles: branch writes in code paths
- Design roles: branch writes in design system paths only
- Security roles: can block merges/releases; can open remediation PRs
- Compliance roles: can block releases; can sign evidence manifests
- SRE roles: can execute approved runbooks; can trigger rollbacks
- FinOps roles: can pause workflows; can tag resources for TTL

For concrete allowlists, see:
- `policies/opa/mcp/`
- `templates/mcp/MCP-ALLOWLIST.yaml`
