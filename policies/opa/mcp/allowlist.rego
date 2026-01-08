package itqahn.mcp

default allow := false
default reasons := ["MCP call not allowed by policy"]

# Example allowlist: map roles to MCP capabilities.
# In production, load this map from data (ConfigMap, bundle, or git).
allowed[role] := caps {
  role := "frontend-builder"
  caps := {"figma.read", "repo.read", "repo.write_branch", "issue.create", "obs.read"}
}
allowed[role] := caps {
  role := "policy-author"
  caps := {"repo.read", "repo.write_branch", "policy.write", "policy.test"}
}
allowed[role] := caps {
  role := "incident-commander"
  caps := {"obs.read", "workflow.pause", "workflow.resume", "issue.create"}
}

allow {
  input.action == "mcp.call"
  role := input.actor.role
  cap := input.resource.capability
  allowed_caps := allowed[role]
  allowed_caps[cap]
  reasons := []
}

# Provide structured denial reasons
reasons[reason] {
  input.action == "mcp.call"
  role := input.actor.role
  cap := input.resource.capability
  not allowed[role][cap]
  reason := sprintf("Role '%s' is not allowed capability '%s'", [role, cap])
}
