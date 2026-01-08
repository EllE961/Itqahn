# MCP Allowlists

Allowlists define which MCP operations each agent role can perform. This is the primary access control mechanism for MCP.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALLOWLIST HIERARCHY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   GLOBAL ALLOWLIST                       │    │
│  │           (Organization-wide permissions)                │    │
│  └───────────────────────┬─────────────────────────────────┘    │
│                          │                                       │
│         ┌────────────────┼────────────────┐                     │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  ROLE-BASED  │ │ TENANT-BASED │ │ WORKFLOW     │            │
│  │  ALLOWLIST   │ │ OVERRIDES    │ │ OVERRIDES    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Allowlist Schema

### Full Schema

```yaml
# templates/mcp/MCP-ALLOWLIST.yaml
apiVersion: itqahn.io/v1
kind: MCPAllowlist
metadata:
  name: default-allowlist
  version: 2.0.0

spec:
  # Global defaults
  defaults:
    rate_limit:
      requests_per_minute: 100
    timeout_seconds: 30

  # Role-based permissions
  roles:
    <role-name>:
      mcps:
        <mcp-name>:
          operations:
            - <operation>
          constraints:
            <constraint-key>: <value>
          rate_limit:
            requests_per_minute: <number>

  # Tenant overrides
  tenants:
    <tenant-id>:
      roles:
        <role-name>:
          # Same structure as roles

  # Workflow overrides
  workflows:
    <workflow-type>:
      roles:
        <role-name>:
          # Same structure as roles
```

---

## Role-Based Allowlists

### Frontend Builder

```yaml
roles:
  frontend-builder:
    description: "Builds UI components and pages"
    mcps:
      figma:
        operations:
          - file.read
          - component.export
          - token.export
        constraints:
          projects: ["*"]  # All projects

      github:
        operations:
          - repo.read
          - branch.create
          - branch.push
          - pr.create
          - pr.update
        constraints:
          repos: ["apps/*", "packages/ui/*"]
          branch_prefix: "feat/"

      jira:
        operations:
          - issue.read
          - issue.comment
          - issue.transition
        constraints:
          project_keys: ["*"]

      observability:
        operations:
          - metrics.read
          - logs.read
        constraints:
          services: ["frontend-*"]
```

### Backend Builder

```yaml
roles:
  backend-builder:
    description: "Builds backend services and APIs"
    mcps:
      github:
        operations:
          - repo.read
          - branch.create
          - branch.push
          - pr.create
          - pr.update
        constraints:
          repos: ["services/*", "packages/*"]
          branch_prefix: "feat/"

      kubernetes:
        operations:
          - namespace.read
          - deployment.read
          - pod.read
          - service.read
        constraints:
          namespaces: ["dev-*", "staging-*"]

      vault:
        operations:
          - secret.read
          - credential.issue
        constraints:
          paths: ["kv/services/*"]
          ttl_max: "1h"

      observability:
        operations:
          - metrics.read
          - logs.read
          - traces.read
        constraints:
          services: ["*"]

      jira:
        operations:
          - issue.read
          - issue.comment
          - issue.transition
```

### Security Scanner

```yaml
roles:
  security-scanner:
    description: "Scans code and infrastructure for vulnerabilities"
    mcps:
      github:
        operations:
          - repo.read
          - security_advisory.read
          - code_scanning.read
        constraints:
          repos: ["*"]

      kubernetes:
        operations:
          - namespace.read
          - pod.read
          - configmap.read
          - secret.list  # List only, not read values
        constraints:
          namespaces: ["*"]

      observability:
        operations:
          - security_events.read
          - audit_logs.read
```

### Policy Author

```yaml
roles:
  policy-author:
    description: "Creates and tests policies"
    mcps:
      github:
        operations:
          - repo.read
          - branch.create
          - branch.push
          - pr.create
        constraints:
          repos: ["policies/*"]
          branch_prefix: "policy/"

      kubernetes:
        operations:
          - policy.read
          - policy.test
        constraints:
          policy_types: ["opa", "kyverno"]
```

### SRE Operator

```yaml
roles:
  sre-operator:
    description: "Operates production infrastructure"
    mcps:
      kubernetes:
        operations:
          - namespace.read
          - deployment.read
          - deployment.scale
          - pod.read
          - pod.restart
          - service.read
        constraints:
          namespaces: ["*"]
          max_replicas: 10

      vault:
        operations:
          - secret.read
          - secret.rotate
        constraints:
          paths: ["*"]

      observability:
        operations:
          - metrics.read
          - logs.read
          - traces.read
          - alert.acknowledge
          - incident.create

      github:
        operations:
          - repo.read
          - branch.create
          - pr.create
        constraints:
          repos: ["infra/*"]
          branch_prefix: "hotfix/"
```

### Asset Generator

```yaml
roles:
  asset-generator:
    description: "Generates and manages visual assets"
    mcps:
      assets:
        operations:
          - asset.generate
          - asset.edit
          - asset.bgremove
          - asset.upscale
          - asset.vectorize
          - asset.crop
          - asset.convert
          - asset.lint
          - asset.drift
          - registry.store
          - registry.get
          - registry.list
          - registry.search
        constraints:
          providers: ["replicate", "runpod"]
          max_resolution: 4096
          max_generations_per_request: 4
          require_style_anchor: true
          require_design_os_version: true
          budget_per_workflow_usd: 5.00

      github:
        operations:
          - repo.read
          - branch.create
          - branch.push
          - pr.create
        constraints:
          repos: ["assets/*", "design-os/*"]
          branch_prefix: "asset/"

      figma:
        operations:
          - file.read
          - component.export
        constraints:
          projects: ["*"]
```

### Design Guardian (Assets)

```yaml
roles:
  design-guardian:
    description: "Reviews and approves design assets"
    mcps:
      assets:
        operations:
          - asset.lint
          - asset.drift
          - registry.get
          - registry.list
          - registry.search
        constraints:
          read_only: true

      figma:
        operations:
          - file.read
          - component.export
          - token.export
          - screenshot.capture
        constraints:
          projects: ["*"]

      github:
        operations:
          - repo.read
          - pr.review
          - pr.comment
        constraints:
          repos: ["design-os/*", "assets/*"]
```

---

## Operation Definitions

### GitHub Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `repo.read` | Read repository contents | Low |
| `repo.write` | Write to default branch | High |
| `branch.create` | Create new branch | Low |
| `branch.push` | Push to branch | Medium |
| `branch.delete` | Delete branch | Medium |
| `pr.create` | Create pull request | Low |
| `pr.update` | Update pull request | Low |
| `pr.merge` | Merge pull request | High |
| `issue.read` | Read issues | Low |
| `issue.create` | Create issues | Low |
| `check.read` | Read check status | Low |

### Kubernetes Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `namespace.read` | Read namespace | Low |
| `deployment.read` | Read deployments | Low |
| `deployment.scale` | Scale replicas | Medium |
| `deployment.restart` | Restart deployment | Medium |
| `pod.read` | Read pods | Low |
| `pod.restart` | Restart pod | Medium |
| `pod.delete` | Delete pod | High |
| `secret.list` | List secret names | Low |
| `secret.read` | Read secret values | High |
| `configmap.read` | Read configmaps | Low |

### Figma Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `file.read` | Read Figma files | Low |
| `component.export` | Export components | Low |
| `token.export` | Export design tokens | Low |
| `comment.read` | Read comments | Low |
| `comment.create` | Create comments | Low |

### Vault Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `secret.read` | Read secrets | High |
| `secret.write` | Write secrets | High |
| `secret.rotate` | Rotate secrets | Medium |
| `credential.issue` | Issue dynamic credential | Medium |
| `pki.issue` | Issue certificate | Medium |

### Assets Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `asset.generate` | Generate new image | High |
| `asset.edit` | Edit existing image | High |
| `asset.bgremove` | Remove background | Medium |
| `asset.upscale` | Upscale resolution | Medium |
| `asset.vectorize` | Convert to SVG | Medium |
| `asset.crop` | Crop and resize | Low |
| `asset.convert` | Convert format | Low |
| `asset.lint` | Validate against Design OS | Low |
| `asset.drift` | Check style drift | Low |
| `registry.store` | Store in registry | Medium |
| `registry.get` | Retrieve from registry | Low |
| `registry.list` | List registry assets | Low |
| `registry.search` | Search registry | Low |
| `registry.delete` | Delete from registry | High |

---

## Constraints

### Common Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `repos` | Repository patterns | `["services/*", "apps/*"]` |
| `namespaces` | K8s namespace patterns | `["prod-*", "staging-*"]` |
| `paths` | Vault path patterns | `["kv/services/*"]` |
| `branch_prefix` | Required branch prefix | `"feat/"` |
| `projects` | Figma project filter | `["design-system"]` |
| `ttl_max` | Maximum credential TTL | `"1h"` |
| `max_replicas` | Maximum scale target | `10` |
| `providers` | Asset generation providers | `["replicate", "runpod"]` |
| `max_resolution` | Maximum asset resolution | `4096` |
| `budget_per_workflow_usd` | Asset budget per workflow | `5.00` |
| `require_style_anchor` | Require style anchor reference | `true` |
| `require_design_os_version` | Require Design OS version | `true` |

### Constraint Examples

```yaml
constraints:
  # Glob patterns
  repos: ["services/*", "!services/legacy-*"]

  # Explicit list
  namespaces: ["dev", "staging", "prod"]

  # Time-based
  ttl_max: "4h"

  # Numeric limits
  max_replicas: 20
  max_pods_to_restart: 5

  # Environment-based
  environments: ["dev", "staging"]
```

---

## Tenant Overrides

Override role permissions for specific tenants:

```yaml
tenants:
  tenant-enterprise:
    description: "Enterprise customer with elevated limits"
    roles:
      backend-builder:
        mcps:
          github:
            rate_limit:
              requests_per_minute: 200
          kubernetes:
            operations:
              - namespace.read
              - deployment.read
              - deployment.scale
              - pod.read
              - pod.restart
            constraints:
              namespaces: ["tenant-enterprise-*"]
              max_replicas: 50

  tenant-restricted:
    description: "Restricted tenant with limited access"
    roles:
      backend-builder:
        mcps:
          kubernetes:
            operations:
              - namespace.read
              - deployment.read
              - pod.read
            # No write operations
```

---

## Workflow Overrides

Override role permissions for specific workflow types:

```yaml
workflows:
  regulated-build:
    description: "Regulated tier workflow with additional controls"
    roles:
      backend-builder:
        mcps:
          github:
            operations:
              - repo.read
              - branch.create
              - branch.push
              - pr.create
              # No direct merge - requires human approval
            constraints:
              repos: ["services/*"]
              require_signed_commits: true

  hotfix:
    description: "Emergency hotfix workflow"
    roles:
      sre-operator:
        mcps:
          kubernetes:
            operations:
              - deployment.read
              - deployment.scale
              - deployment.restart
              - pod.restart
            constraints:
              namespaces: ["prod-*"]
              max_pods_to_restart: 10
```

---

## Validation

### Schema Validation

```bash
# Validate allowlist file
itqahn validate allowlist templates/mcp/MCP-ALLOWLIST.yaml
```

### Policy Testing

```rego
# Test allowlist permissions
test_frontend_builder_can_read_figma {
    allow with input as {
        "agent_type": "frontend-builder",
        "mcp": "figma",
        "operation": "file.read"
    }
}

test_frontend_builder_cannot_write_kubernetes {
    not allow with input as {
        "agent_type": "frontend-builder",
        "mcp": "kubernetes",
        "operation": "deployment.scale"
    }
}
```

---

## Best Practices

### Allowlist Design

| Practice | Description |
|----------|-------------|
| **Least privilege** | Grant minimum required permissions |
| **Explicit deny** | Default deny, explicit allow |
| **Scope constraints** | Always add resource constraints |
| **Separate duties** | Don't combine conflicting roles |
| **Regular audit** | Review allowlists quarterly |

### Common Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Wildcard repos | Explicit repo patterns |
| No rate limits | Always set rate limits |
| Missing constraints | Add resource constraints |
| Overly broad roles | Split into focused roles |

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/07-integrations/mcp/mcp-security-model.md` — Security model
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `policies/opa/mcp/` — MCP policies
- `templates/mcp/MCP-ALLOWLIST.yaml` — Allowlist template

---

**Version**: 2.1.0 | **Date**: 2026-01-08
