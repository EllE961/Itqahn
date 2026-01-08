# Agent Permissions

This document defines the permission model for Itqahn agents. Permissions are enforced through multiple layers.

---

## Enforcement Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERMISSION ENFORCEMENT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: Orchestrator                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Tool routing, role assignment, workflow context        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 2: MCP Allowlists   ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Per-role tool access, operation constraints            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 3: OPA Policies     ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Fine-grained authorization, context-aware rules        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 4: Vault Policies   ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Secret access paths, credential scopes                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 5: Git Protection   ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Branch protection, CODEOWNERS, merge requirements      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 6: K8s Admission    ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Deployment validation, evidence requirements           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Permission Tiers

### Tier Definitions

| Tier | Description | Examples |
|------|-------------|----------|
| **Read-only** | View resources without modification | View repo, docs, tickets, dashboards |
| **Write (branch)** | Create PRs in constrained paths | Open PRs, create issues |
| **Approve** | Issue approval attestations | Sign off on gates, authorize releases |
| **Deploy** | Deploy via GitOps only | Trigger ArgoCD sync (never direct kubectl) |

### Tier Requirements

| Tier | Authentication | Authorization | Audit |
|------|----------------|---------------|-------|
| Read-only | SPIFFE | MCP allowlist | Logged |
| Write | SPIFFE | MCP + OPA | Logged + signed |
| Approve | SPIFFE + human verify | OPA + approval policy | Signed + attested |
| Deploy | SPIFFE | OPA + evidence check | Full provenance |

---

## Role-Based Permissions

### Executive Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| CEO Orchestrator | ✅ All | ❌ | ✅ Workflow | ❌ |
| Studio Coach | ✅ All | ❌ | ✅ Phase gates | ❌ |
| Chief Risk Officer | ✅ All | ❌ | ✅ Risk decisions | ❌ |

**Executive roles can approve but never directly write or deploy.**

### Engineering Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Backend Builder | ✅ Code, docs | ✅ services/, packages/ | ❌ | ❌ |
| Frontend Builder | ✅ Code, docs, design | ✅ apps/, packages/ui/ | ❌ | ❌ |
| API Designer | ✅ Code, specs | ✅ specs/, contracts/ | ❌ | ❌ |
| Database Architect | ✅ Code, schema | ✅ migrations/, schema/ | ❌ | ❌ |

**Engineering roles can write code PRs but not approve or deploy.**

### Design Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Design System Guardian | ✅ Design, code | ✅ design-os/, tokens | ❌ | ❌ |
| Design OS Maintainer | ✅ Design, code | ✅ design-os/ | ✅ Design OS PRs | ❌ |
| UI Composer | ✅ Design, code | ✅ apps/, components/ | ❌ | ❌ |
| Accessibility Auditor | ✅ All | ✅ a11y fixes | ❌ | ❌ |
| Design Jail Warden | ✅ All UI code | ❌ | ✅ Block violations | ❌ |

**Design roles only write to design system and UI paths.**

### Asset Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Asset Generator | ✅ Design, assets | ✅ assets/ | ❌ | ❌ |
| Asset Reviewer | ✅ All assets | ❌ | ✅ Asset PRs | ❌ |
| Style Anchor Manager | ✅ Design | ✅ style-anchors/ | ✅ Style anchors | ❌ |

**Asset roles generate and validate assets but cannot deploy to production without review.**

### Security Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Threat Modeler | ✅ Code, infra | ✅ threat-models/ | ❌ | ❌ |
| AppSec Scanner | ✅ All | ✅ security-findings/ | ❌ | ❌ |
| Red Team Operator | ✅ All | ✅ penetration-reports/ | ❌ | ❌ |
| Security Gate | ✅ All | ❌ | ✅ Security sign-off | ❌ |

**Security roles can block merges/releases but not silently override governance.**

### Compliance Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Evidence Curator | ✅ All | ✅ evidence/ | ❌ | ❌ |
| Compliance Mapper | ✅ All | ✅ compliance/ | ❌ | ❌ |
| Audit Liaison | ✅ All | ✅ audit-reports/ | ✅ Evidence packs | ❌ |

**Compliance roles can block releases and sign evidence manifests.**

### SRE Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| SRE Operator | ✅ All | ✅ runbooks/, infra/ | ❌ | ✅ Rollback only |
| Incident Commander | ✅ All | ✅ incident-reports/ | ✅ Runbook execution | ✅ Emergency |
| Auto-Remediation Bot | ✅ Ops | ❌ | ❌ | ✅ Approved actions |

**SRE roles can execute approved runbooks and trigger rollbacks.**

### FinOps Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| CFO FinOps | ✅ All cost data | ❌ | ✅ Budget extension | ❌ |
| Token Budget Enforcer | ✅ Cost data | ❌ | ✅ Pause workflow | ❌ |
| Janitor TTL Reaper | ✅ Resources | ❌ | ✅ Resource cleanup | ❌ |

**FinOps roles can pause workflows but cannot change product scope.**

### Operator Mode Bot Roles

| Role | Read | Write | Approve | Deploy |
|------|------|-------|---------|--------|
| Itqahn Orchestrator Bot | ✅ All | ✅ All automated paths | ✅ Automated gates | ✅ Via GitOps |
| Kill Switch Operator | ✅ All | ❌ | ✅ Kill switch | ❌ |

**In Operator Mode, the orchestrator bot has elevated permissions but all actions are logged and evidenced.**

---

## Operator Mode Permissions

### Bot Identity

The Itqahn orchestrator bot operates as a GitHub App with specific permissions:

```yaml
# GitHub App: itqahn-bot
identity:
  github_app_id: 123456
  installation_id: "${installation_id}"
  private_key: "${vault:github/itqahn-bot/private-key}"

permissions:
  repository:
    contents: write      # Push commits, create branches
    pull_requests: write # Create PRs, enable auto-merge
    issues: write        # Create issues, add labels
    checks: write        # Create check runs, report status
    statuses: write      # Set commit statuses
    actions: read        # Read workflow status

  organization:
    members: read        # Read team membership for CODEOWNERS
```

### Operator Mode Permission Scope

| Operation | Permission | Enforcement |
|-----------|------------|-------------|
| Create issues | `issues: write` | OPA: must use itqahn templates |
| Create branches | `contents: write` | OPA: must match `feat/run-*` pattern |
| Push commits | `contents: write` | OPA: must include run ID in message |
| Create PRs | `pull_requests: write` | OPA: must link to issue and evidence |
| Enable auto-merge | `pull_requests: write` | OPA: only for auto-generated PRs |
| Create check runs | `checks: write` | OPA: must match workflow checks |
| Create releases | `contents: write` | OPA: must have evidence pack attached |
| Merge via queue | `contents: write` | GitHub: all checks must pass |

### Bypass Constraints

In Operator Mode with `--dangerously-skip-permissions`:

| Constraint | Bypassed | Still Enforced |
|------------|----------|----------------|
| Interactive confirmations | ✅ | |
| Human review of PRs | ✅ | |
| Manual merge approval | ✅ | |
| | | Audit logging |
| | | Evidence Pack generation |
| | | Policy evaluation (OPA) |
| | | Budget circuit breakers |
| | | Security scan blocking |
| | | Secret isolation |

### Bot Audit Requirements

All bot actions MUST be logged:

```json
{
  "timestamp": "2026-01-08T14:30:00Z",
  "event_type": "bot_action",
  "bot": {
    "id": "itqahn-bot[bot]",
    "app_id": 123456,
    "installation_id": 789012
  },
  "action": {
    "type": "github.pr.create",
    "resource": "itqahn-org/task-manager#156",
    "run_id": "run-01J5ABCD"
  },
  "context": {
    "operator_mode": true,
    "skip_permissions": true,
    "concept_lock": "1.0.0",
    "workflow_id": "wf-xyz789"
  },
  "evidence": {
    "audit_log_id": "log-abc123",
    "evidence_pack_ref": "evidence-run-01J5ABCD"
  }
}
```

---

## Git Orchestrator Capability

The **Git Orchestrator** is a system-level capability that controls all Git operations for parallel task execution. Only the orchestrator may perform branch lifecycle and merge operations.

### Git Orchestrator Permissions Matrix

| Operation | Git Orchestrator | Other Agents | Notes |
|-----------|------------------|--------------|-------|
| **Branch Operations** |
| Create worktree | ✅ | ❌ | Creates isolated working directory |
| Create feature branch | ✅ | ❌ | Pattern: `feat/run-{run_id}/task-{task_id}` |
| Delete worktree | ✅ | ❌ | Only after merge or cleanup |
| Delete feature branch | ✅ | ❌ | Only merged or abandoned branches |
| Force push | ❌ | ❌ | **Never allowed** |
| **PR Operations** |
| Create PR | ✅ | ❌ | Auto-linked to issue and Evidence Pack |
| Update PR | ✅ | ❌ | Rebase, description updates |
| Enable auto-merge | ✅ | ❌ | Only for bot-created PRs |
| Bypass branch protection | ❌ | ❌ | **Never allowed** |
| Bypass CODEOWNERS | ❌ | ❌ | **Never allowed** |
| **Merge Operations** |
| Enqueue to merge queue | ✅ | ❌ | After all checks pass |
| Direct merge to main | ❌ | ❌ | **Never allowed** (queue only) |
| Admin merge bypass | ❌ | ❌ | **Never allowed** |
| **Rebase Operations** |
| Rebase on main | ✅ | ❌ | Required before PR and on main update |
| Resolve conflicts (auto) | ✅ | ❌ | Safe patterns only |
| Resolve conflicts (manual) | ❌ | ❌ | Escalates to dashboard |

### Git Orchestrator Constraints

```yaml
# policies/opa/operator/git_orchestrator.rego
git_orchestrator:
  identity:
    spiffe_id: "spiffe://itqahn.io/git-orchestrator"
    github_app: "itqahn-bot"

  allowed_operations:
    branches:
      create:
        patterns:
          - "feat/run-*/task-*"
          - "fix/run-*/task-*"
          - "asset/run-*/task-*"
        constraints:
          max_concurrent_per_repo: 10
          require_run_context: true
      delete:
        conditions:
          - merged_to_main: true
          - abandoned_with_evidence: true
          - age_days_if_stale: 7

    pull_requests:
      create:
        requirements:
          - linked_issue: true
          - evidence_pack_ref: true
          - run_id_in_body: true
      auto_merge:
        conditions:
          - all_checks_pass: true
          - required_reviews: true
          - no_merge_conflicts: true

    merge_queue:
      enqueue:
        requirements:
          - ci_pass: true
          - policy_gates_pass: true
          - evidence_complete: true
      priority_assignment:
        based_on:
          - task_priority
          - dependency_order
          - queue_age

  prohibited_operations:
    always_blocked:
      - force_push
      - direct_merge_to_protected
      - bypass_branch_protection
      - bypass_codeowners
      - admin_merge
      - delete_protected_branch
```

### Non-Orchestrator Agent Git Restrictions

All agents **except** the Git Orchestrator are restricted to:

| Agent Role | Git Permissions |
|------------|-----------------|
| Backend Builder | Read repo, write to assigned worktree only |
| Frontend Builder | Read repo, write to assigned worktree only |
| Security Scanner | Read-only |
| Asset Generator | Read repo, write to assets/ in assigned worktree |
| SRE Operator | Read-only (for runbook refs) |
| All Design Roles | Read repo, write to design paths in assigned worktree |

```yaml
# Non-orchestrator agent Git constraints
non_orchestrator_agents:
  git:
    read:
      - "*"  # Can read any file

    write:
      scope: "assigned_worktree_only"
      paths: "${role_allowed_paths}"

    prohibited:
      - git push (direct)       # Must go through orchestrator
      - git branch -d           # Cannot delete branches
      - git merge               # Cannot merge
      - git rebase              # Cannot rebase (orchestrator only)
      - git checkout main       # Cannot switch to protected branches
      - git remote add          # Cannot modify remotes
```

### CI and Policy Gates: Mandatory Blockers

Even in Operator Mode with `--dangerously-skip-permissions`, the following gates **cannot be bypassed**:

```yaml
mandatory_gates:
  ci_checks:
    enforcement: blocking
    bypass_allowed: false
    description: "All CI checks MUST pass before merge"
    applies_to:
      - unit_tests
      - integration_tests
      - lint_checks
      - security_scans
      - visual_regression

  policy_evaluation:
    enforcement: blocking
    bypass_allowed: false
    description: "OPA policies MUST evaluate to allow"
    applies_to:
      - audit_required
      - merge_requirements
      - evidence_pack_complete

  branch_protection:
    enforcement: blocking
    bypass_allowed: false
    description: "GitHub branch protection rules are absolute"
    rules:
      - require_pull_request_reviews
      - require_status_checks
      - require_linear_history
      - require_signed_commits  # if enabled

  codeowners_review:
    enforcement: blocking
    bypass_allowed: false
    description: "CODEOWNERS approval required for protected paths"
    exception: "Only waived for paths with no CODEOWNERS entry"

  evidence_pack:
    enforcement: blocking
    bypass_allowed: false
    description: "Evidence Pack MUST be generated and linked"
    applies_to:
      - T3_compliance
      - T4_compliance
```

### Operator Mode: What IS Bypassed vs What IS NOT

| Category | `--dangerously-skip-permissions` Bypasses | Still Enforced |
|----------|-------------------------------------------|----------------|
| **Human Interaction** | Interactive confirmations | |
| | Manual PR review prompts | |
| | Human approval dialogs | |
| **Review Requirements** | | CODEOWNERS review |
| | | Required approvals count |
| **CI/CD** | | All CI checks must pass |
| | | Security scan blocking |
| | | Visual regression checks |
| **Policies** | | OPA policy evaluation |
| | | Audit logging (mandatory) |
| | | Evidence Pack generation |
| **Git Operations** | | Branch protection rules |
| | | Merge queue requirements |
| | | Force push prohibition |
| **Financial** | | Budget circuit breakers |
| | | Cost tracking |

### Git Orchestrator Audit Trail

All Git Orchestrator operations are logged:

```json
{
  "timestamp": "2026-01-08T14:30:00Z",
  "event_type": "git_orchestrator.operation",
  "orchestrator": {
    "spiffe_id": "spiffe://itqahn.io/git-orchestrator",
    "component": "parallel-task-controller"
  },
  "operation": {
    "type": "worktree.create",
    "worktree_path": "/worktrees/feat-run-01J5ABCD-task-001",
    "branch": "feat/run-01J5ABCD/task-001",
    "base_ref": "main@abc123"
  },
  "context": {
    "run_id": "run-01J5ABCD",
    "task_id": "task-001",
    "tenant_id": "tenant-xyz",
    "workflow_id": "wf-parallel-sprint"
  },
  "evidence": {
    "audit_log_id": "log-git-789",
    "operation_hash": "sha256:...",
    "pre_state_hash": "sha256:...",
    "post_state_hash": "sha256:..."
  }
}
```

---

### Kill Switch Permissions

The Kill Switch has elevated permissions to halt all operations:

```yaml
kill_switch:
  permissions:
    - temporal.workflow.terminate  # Stop all workflows
    - github.branch.protect       # Block all merges
    - vault.lease.revoke         # Revoke credentials
    - mcp.tool.revoke            # Revoke tool access

  requires:
    - authenticated_operator
    - reason_provided
    - audit_log_entry

  actions:
    - terminate_workflows
    - freeze_merge_queues
    - revoke_mcp_credentials
    - notify_alert_channels
    - optional: rotate_secrets
```

---

## UI and Design OS Permissions

### Hard Rule: No Agent May Write CSS Directly

All UI styling MUST flow through Design OS:

```
Design OS (tokens.json, components.json)
           │
           ▼
Agent composes UI using approved components
           │
           ▼
Design Jail validator verifies compliance
           │
           ▼
Compliant UI merged
```

### UI Agent Capabilities

| Agent Role | Can Do | Cannot Do |
|------------|--------|-----------|
| **UI Composer** | Compose using `<Button>`, `<Input>`, etc. | Write `style={}` or CSS |
| **Frontend Builder** | Import from design system | Create custom components |
| **Design System Guardian** | Propose token/component changes | Bypass Design Jail |
| **Design OS Maintainer** | Update tokens.json, components.json | Deploy without review |
| **Design Jail Warden** | Block non-compliant PRs | Approve violations |
| **Accessibility Auditor** | Flag a11y issues, propose fixes | Ignore WCAG requirements |

### CSS Writing: Explicitly Prohibited

| Action | Allowed | Prohibited |
|--------|---------|------------|
| Reference token | `var(--color-brand-primary)` | |
| Use component | `<Button variant="primary">` | |
| Write inline style | | `style={{ color: 'red' }}` |
| Write CSS class | | `.my-button { padding: 8px }` |
| Use raw hex color | | `color: #3b82f6` |
| Use raw pixel value | | `margin: 16px` |
| Create custom component | | `const FancyButton = styled.button` |

### Design OS Change Authorization

Only these roles may modify Design OS artifacts:

| Role | tokens.json | components.json | patterns/ | a11y-rules.md |
|------|-------------|-----------------|-----------|---------------|
| Design OS Maintainer | ✅ Propose | ✅ Propose | ✅ Propose | ❌ |
| Design System Guardian | ✅ Propose | ✅ Propose | ✅ Propose | ❌ |
| Accessibility Specialist | ❌ | ❌ | ❌ | ✅ Propose |
| Frontend Architect | ❌ | ✅ Propose | ✅ Propose | ❌ |

All Design OS changes require:
1. PR to design-os branch
2. Design Jail Warden review
3. Schema validation pass
4. Visual regression pass
5. Accessibility audit pass

---

## Path Constraints

### Code Paths

```yaml
paths:
  engineering:
    backend-builder:
      - "services/**"
      - "packages/**"
      - "!packages/ui/**"
    frontend-builder:
      - "apps/**"
      - "packages/ui/**"

  design:
    design-system-guardian:
      - "design/**"
      - "packages/ui/tokens/**"
    ui-composer:
      - "apps/*/components/**"
      - "apps/*/pages/**"

  security:
    threat-modeler:
      - "docs/security/**"
      - "threat-models/**"
    appsec-scanner:
      - "security-findings/**"

  compliance:
    evidence-curator:
      - "evidence/**"
    compliance-mapper:
      - "compliance/**"

  sre:
    sre-operator:
      - "runbooks/**"
      - "infra/**"

  assets:
    asset-generator:
      - "assets/specs/**"
      - "assets/outputs/**"
      - "assets/manifests/**"
      - "assets/lint-reports/**"
    style-anchor-manager:
      - "design-os/style-anchors/**"
    asset-reviewer:
      - "assets/**"  # Read only
```

### Vault Paths

```yaml
vault_paths:
  backend-builder:
    - "kv/services/*"
    - "database/creds/*-readonly"

  sre-operator:
    - "kv/**"
    - "database/creds/*"
    - "pki/issue/*"

  security-scanner:
    - "kv/security/*"
```

---

## MCP Permissions

### Permission Matrix

| Role | GitHub | K8s | Vault | Figma | Jira | Observability | Assets |
|------|--------|-----|-------|-------|------|---------------|--------|
| Backend Builder | RW | R | R | - | RW | R | - |
| Frontend Builder | RW | R | R | R | RW | R | R |
| Security Scanner | R | R | R | - | RW | R | - |
| SRE Operator | RW | RW | RW | - | RW | RW | - |
| Design Guardian | R | - | - | R | RW | - | RW |
| Asset Generator | RW | - | R | R | RW | - | RW |
| Asset Reviewer | R | - | - | R | RW | - | R |

Legend: R = Read, W = Write, RW = Read/Write, - = No access

### Operation Constraints

```yaml
# MCP operation constraints per role
roles:
  backend-builder:
    github:
      operations: [read, branch.create, branch.push, pr.create]
      constraints:
        branch_prefix: "feat/"
        protected_branches: deny
    kubernetes:
      operations: [read]
      constraints:
        namespaces: ["dev-*", "staging-*"]

  sre-operator:
    kubernetes:
      operations: [read, scale, restart]
      constraints:
        namespaces: ["*"]
        max_replicas: 20

  asset-generator:
    assets:
      operations:
        - asset.generate
        - asset.edit
        - asset.bgremove
        - asset.upscale
        - asset.vectorize
        - asset.lint
        - asset.drift
        - registry.store
        - registry.get
        - registry.list
      constraints:
        providers: ["replicate", "runpod"]
        max_resolution: 4096
        require_style_anchor: true
        require_design_os_version: true
        budget_per_workflow_usd: 5.00
    github:
      operations: [read, branch.create, branch.push, pr.create]
      constraints:
        repos: ["assets/*", "design-os/*"]
        branch_prefix: "asset/"

  asset-reviewer:
    assets:
      operations:
        - asset.lint
        - asset.drift
        - registry.get
        - registry.list
        - registry.search
      constraints:
        read_only: true
```

---

## Approval Workflows

### Approval Types

| Approval | Required For | Approvers |
|----------|--------------|-----------|
| Code merge | PR to main | CODEOWNERS + CI pass |
| Security sign-off | Security-critical changes | Security Gate |
| Release authorization | Production deploy | Compliance + Security |
| Budget extension | Exceed workflow budget | CFO FinOps |
| Emergency deploy | Hotfix to production | Incident Commander |

### Approval Chain

```
1. Agent requests action requiring approval
       │
       ▼
2. System identifies approval type
       │
       ▼
3. Approval request created
       │
       ├── Jira ticket for human approval
       │
       └── Notification to approvers
       │
       ▼
4. Approver reviews and decides
       │
       ├── Approve → Action proceeds
       │
       └── Deny → Action blocked, feedback returned
```

---

## Policy Enforcement

### OPA Policy Example

```rego
# policies/opa/agents/permissions.rego
package agent_permissions

default allow = false

# Engineering roles can write to their paths
allow {
    input.role in ["backend-builder", "frontend-builder"]
    input.action == "write"
    path_allowed(input.role, input.path)
}

# Security roles can block
allow {
    input.role in ["security-gate", "appsec-scanner"]
    input.action == "block"
}

# Only approve roles can approve
allow {
    input.action == "approve"
    input.role in data.approve_roles
    approval_conditions_met
}

path_allowed(role, path) {
    allowed_paths := data.role_paths[role]
    some pattern in allowed_paths
    glob.match(pattern, ["/"], path)
}
```

### Kyverno Policy Example

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: agent-deployment-constraints
spec:
  validationFailureAction: enforce
  rules:
    - name: require-agent-identity
      match:
        resources:
          kinds: ["Deployment"]
      validate:
        message: "Deployment must have agent identity annotation"
        pattern:
          metadata:
            annotations:
              itqahn.io/agent-id: "?*"
              itqahn.io/workflow-id: "?*"
```

---

## Audit Logging

### Permission Check Log

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "event_type": "permission_check",
  "agent": {
    "id": "backend-builder-abc123",
    "role": "backend-builder"
  },
  "action": {
    "type": "write",
    "resource": "github:itqahn-org/user-service",
    "path": "src/auth.ts"
  },
  "decision": {
    "allowed": true,
    "policy": "agent_permissions/write_code",
    "constraints_checked": ["path", "branch_prefix"]
  },
  "context": {
    "workflow_id": "wf-xyz789",
    "tenant_id": "tenant-abc"
  }
}
```

---

## Related Documents

- `docs/00-overview/principles.md` — Operator Mode audit principles
- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/03-platform/portal-webapp.md` — Operator Mode dashboard and Kill Switch
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/07-integrations/git-integration.md` — GitHub Automation Program
- `docs/07-integrations/mcp/mcp-allowlists.md` — MCP allowlists
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/08-agents/agent-system-contract.md` — Contract rules
- `policies/opa/agents/` — Agent policies
- `policies/opa/operator/` — Operator Mode policies

---

**Version**: 2.4.0 | **Date**: 2026-01-08
