# OPA Policies (Rego)

These policies are evaluated by:
- the orchestrator (before tool calls and risky actions),
- CI (before merges),
- deployment admission (before rollout).

## Inputs

Policies expect a JSON input with fields like:
- `action`: attempted operation (e.g., `deploy`, `mcp.call`, `merge`)
- `actor`: agent identity (role, spiffe_id)
- `resource`: target resource (repo path, cluster namespace, secret path)
- `context`: risk tier, compliance tier, workflow ID
- `evidence`: references to Evidence Pack artifacts when relevant

## Outputs

Policies return:
- `allow: true|false`
- `reasons: [string]`
- `requirements: [string]` (what must be provided to allow)

See templates:
- `templates/governance/POLICY-INPUT.json`
