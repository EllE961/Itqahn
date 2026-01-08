# MCP GitHub Integration

The GitHub MCP provides controlled access to repositories, pull requests, issues, and CI/CD status for Itqahn agents.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB MCP FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│ GitHub MCP  │───▶│ GitHub API  │             │
│  │         │    │             │    │             │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │   Code   │  │   PRs    │  │     CI/CD       │              │
│  │   Read   │  │  Issues  │  │    Checks       │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `repo.read` | Read repository files | Low |
| `repo.search` | Search code in repos | Low |
| `branch.create` | Create new branch | Low |
| `branch.push` | Push commits to branch | Medium |
| `branch.delete` | Delete branch | Medium |
| `pr.create` | Create pull request | Low |
| `pr.update` | Update PR description/title | Low |
| `pr.comment` | Add PR comment | Low |
| `pr.review` | Submit PR review | Medium |
| `pr.merge` | Merge pull request | High |
| `issue.read` | Read issues | Low |
| `issue.create` | Create issue | Low |
| `issue.comment` | Comment on issue | Low |
| `check.read` | Read check status | Low |
| `check.create` | Create check run | Medium |
| `release.read` | Read releases | Low |
| `release.create` | Create release | High |

---

## Authentication

### GitHub App (Recommended)

```yaml
github:
  auth:
    method: github_app
    app_id: 123456
    private_key_source: vault
    vault_path: kv/mcp/github/app-key
    installation_id: 789012
```

### Personal Access Token

```yaml
github:
  auth:
    method: pat
    token_source: vault
    vault_path: kv/mcp/github/pat
```

### Fine-Grained PAT

```yaml
github:
  auth:
    method: fine_grained_pat
    token_source: vault
    vault_path: kv/mcp/github/fg-pat
    permissions:
      contents: read
      pull_requests: write
      issues: write
```

---

## Operations

### Read Repository File

```json
{
  "operation": "repo.read",
  "params": {
    "owner": "itqahn-org",
    "repo": "user-service",
    "path": "src/main.ts",
    "ref": "main"
  }
}
```

Response:
```json
{
  "content": "import express from 'express'...",
  "sha": "abc123",
  "encoding": "base64",
  "size": 4096
}
```

### Search Code

```json
{
  "operation": "repo.search",
  "params": {
    "query": "authenticate user",
    "owner": "itqahn-org",
    "repos": ["user-service", "auth-service"],
    "language": "typescript"
  }
}
```

### Create Branch

```json
{
  "operation": "branch.create",
  "params": {
    "owner": "itqahn-org",
    "repo": "user-service",
    "branch": "feat/add-login",
    "from_ref": "main"
  }
}
```

### Push Commits

```json
{
  "operation": "branch.push",
  "params": {
    "owner": "itqahn-org",
    "repo": "user-service",
    "branch": "feat/add-login",
    "commits": [
      {
        "message": "Add login endpoint",
        "files": [
          {
            "path": "src/routes/auth.ts",
            "content": "...",
            "operation": "create"
          }
        ]
      }
    ]
  }
}
```

### Create Pull Request

```json
{
  "operation": "pr.create",
  "params": {
    "owner": "itqahn-org",
    "repo": "user-service",
    "title": "Add login endpoint",
    "body": "## Summary\nAdds user login functionality...",
    "head": "feat/add-login",
    "base": "main",
    "labels": ["feature", "auth"],
    "reviewers": ["@security-team"]
  }
}
```

Response:
```json
{
  "number": 123,
  "url": "https://github.com/itqahn-org/user-service/pull/123",
  "state": "open",
  "mergeable": null
}
```

### Read Check Status

```json
{
  "operation": "check.read",
  "params": {
    "owner": "itqahn-org",
    "repo": "user-service",
    "ref": "feat/add-login"
  }
}
```

Response:
```json
{
  "check_runs": [
    {
      "name": "lint",
      "status": "completed",
      "conclusion": "success"
    },
    {
      "name": "test",
      "status": "completed",
      "conclusion": "success"
    },
    {
      "name": "security-scan",
      "status": "in_progress",
      "conclusion": null
    }
  ],
  "overall": "pending"
}
```

---

## Branch Protection

### Protected Branch Rules

Agents must respect branch protection rules:

| Rule | Agent Behavior |
|------|----------------|
| Require PR | Cannot push directly to protected branch |
| Require reviews | Cannot self-merge |
| Require checks | Wait for checks to pass |
| Require signed commits | Sign commits via Sigstore |
| Restrict pushers | Only allowed agents can push |

### Bypass Handling

```yaml
github:
  branch_protection:
    respect_protection: true
    allow_bypass: false
    bypass_requires:
      - human_approval
      - emergency_flag
```

---

## Workflow Integration

### Commit Attribution

All commits include agent attribution:

```
feat: Add login endpoint

Implements user authentication via OAuth2.

Workflow-ID: wf-xyz789
Agent: backend-builder
Model: claude-3-opus
Evidence: s3://evidence/user-service/1.2.3/build-abc123

🤖 Generated with Itqahn
Co-Authored-By: Backend Builder <backend-builder@itqahn.io>
```

### PR Labels

Automatic labels based on workflow context:

| Label | Meaning |
|-------|---------|
| `workflow:wf-xyz789` | Associated workflow |
| `agent:backend-builder` | Creating agent |
| `tier:sensitive` | Compliance tier |
| `phase:experience` | Workflow phase |
| `auto-generated` | Agent-created PR |

---

## Configuration

### MCP Configuration

```yaml
mcp:
  github:
    enabled: true
    base_url: "https://api.github.com"
    enterprise_url: null  # For GitHub Enterprise

    auth:
      method: github_app
      app_id: 123456
      private_key_source: vault
      vault_path: kv/mcp/github/app-key

    rate_limits:
      requests_per_hour: 5000
      search_per_minute: 30

    defaults:
      default_branch: main
      commit_signing: true

    allowed_orgs:
      - itqahn-org

    webhook_secret_source: vault
    webhook_secret_path: kv/mcp/github/webhook-secret
```

### Allowlist Entry

```yaml
roles:
  backend-builder:
    mcps:
      github:
        operations:
          - repo.read
          - repo.search
          - branch.create
          - branch.push
          - pr.create
          - pr.update
          - pr.comment
          - issue.read
          - issue.comment
          - check.read
        constraints:
          orgs: ["itqahn-org"]
          repos: ["services/*", "packages/*"]
          branch_prefix: "feat/"
          protected_branches: deny
```

---

## Rate Limiting

### GitHub API Limits

| Limit Type | Value | Handling |
|------------|-------|----------|
| Core API | 5000/hour | Queue excess |
| Search API | 30/minute | Rate limit |
| GraphQL | 5000 points/hour | Track points |

### MCP Rate Limits

```yaml
github:
  rate_limits:
    per_agent:
      requests_per_minute: 50
    per_workflow:
      requests_per_minute: 100
    per_tenant:
      requests_per_hour: 1000
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `GITHUB_AUTH_FAILED` | Authentication failed | Refresh token |
| `GITHUB_NOT_FOUND` | Resource not found | Check path |
| `GITHUB_CONFLICT` | Merge conflict | Resolve conflict |
| `GITHUB_RATE_LIMITED` | Rate limit exceeded | Back off |
| `GITHUB_PROTECTED` | Branch protected | Use PR flow |
| `GITHUB_PERMISSION` | Insufficient permissions | Check scopes |

### Retry Configuration

```yaml
github:
  retry:
    max_attempts: 3
    initial_delay_ms: 1000
    max_delay_ms: 30000
    retry_on:
      - GITHUB_RATE_LIMITED
      - GITHUB_SERVER_ERROR
```

---

## Security Considerations

### Scoped Access

- GitHub App installed only on required repos
- Fine-grained PATs scoped to specific repos
- No admin access granted to agents
- Webhook secrets stored in Vault

### Audit Trail

Every GitHub operation logged:

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "mcp": "github",
  "operation": "pr.create",
  "agent_id": "backend-builder",
  "workflow_id": "wf-xyz789",
  "resource": "itqahn-org/user-service/pull/123",
  "result": "success"
}
```

### Secrets Protection

- Never commit secrets
- Pre-commit hooks scan for secrets
- Gitleaks integration
- Immediate revocation on detection

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `github_mcp_requests_total` | Total requests |
| `github_mcp_latency` | Request latency |
| `github_mcp_rate_limit_remaining` | Remaining quota |
| `github_prs_created` | PRs created by agents |
| `github_commits_pushed` | Commits pushed |

### Alerts

```yaml
alerts:
  - name: github_rate_limit_low
    condition: github_mcp_rate_limit_remaining < 100
    severity: warning

  - name: github_auth_failures
    condition: rate(github_mcp_errors{type="auth"}[5m]) > 0
    severity: critical
```

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/07-integrations/git-integration.md` — Git integration
- `docs/03-platform/ci-cd-gitops.md` — CI/CD pipeline

---

**Version**: 2.0.0 | **Date**: 2026-01-06
