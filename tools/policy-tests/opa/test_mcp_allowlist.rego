# OPA tests for MCP allowlist policies
package mcp_test

import data.mcp

# Test fixtures
mock_allowlist := {
    "backend-builder": ["github.repo.read", "github.branch.create", "jira.issue.read"],
    "frontend-builder": ["github.repo.read", "figma.file.read", "jira.issue.read"],
    "security-scanner": ["github.repo.read", "kubernetes.pod.read"],
    "sre-operator": ["kubernetes.deployment.scale", "kubernetes.pod.restart"]
}

# Test: Backend builder can read GitHub repos
test_backend_builder_github_read {
    mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "github",
        "operation": "repo.read"
    } with data.allowlists as mock_allowlist
}

# Test: Backend builder can create branches
test_backend_builder_github_branch_create {
    mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "github",
        "operation": "branch.create"
    } with data.allowlists as mock_allowlist
}

# Test: Backend builder cannot access Figma
test_backend_builder_figma_denied {
    not mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "figma",
        "operation": "file.read"
    } with data.allowlists as mock_allowlist
}

# Test: Frontend builder can read Figma
test_frontend_builder_figma_read {
    mcp.allow with input as {
        "agent_type": "frontend-builder",
        "mcp": "figma",
        "operation": "file.read"
    } with data.allowlists as mock_allowlist
}

# Test: Frontend builder cannot scale Kubernetes
test_frontend_builder_k8s_scale_denied {
    not mcp.allow with input as {
        "agent_type": "frontend-builder",
        "mcp": "kubernetes",
        "operation": "deployment.scale"
    } with data.allowlists as mock_allowlist
}

# Test: SRE can scale deployments
test_sre_k8s_scale {
    mcp.allow with input as {
        "agent_type": "sre-operator",
        "mcp": "kubernetes",
        "operation": "deployment.scale"
    } with data.allowlists as mock_allowlist
}

# Test: Unknown agent is denied
test_unknown_agent_denied {
    not mcp.allow with input as {
        "agent_type": "unknown-agent",
        "mcp": "github",
        "operation": "repo.read"
    } with data.allowlists as mock_allowlist
}

# Test: Unknown operation is denied
test_unknown_operation_denied {
    not mcp.allow with input as {
        "agent_type": "backend-builder",
        "mcp": "github",
        "operation": "repo.delete"
    } with data.allowlists as mock_allowlist
}
