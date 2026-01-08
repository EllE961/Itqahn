# MCP Specification

## MCP name
Name.

## Capabilities
List capability strings (e.g., `repo.read`, `figma.read`, `obs.read`).

## AuthN/AuthZ
- workload identity method (SPIFFE/OIDC)
- authorization model

## Logging
- required log fields (workflow_id, agent_role, policy_verdict)

## Rate limits
- per tenant
- per workflow

## Failure modes
How the MCP fails safely.
