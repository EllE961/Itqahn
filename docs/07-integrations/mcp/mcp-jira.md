# MCP Jira Integration

The Jira MCP enables agents to interact with issue tracking for task management, approval workflows, and evidence linking.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     JIRA MCP FLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│  Jira MCP   │───▶│  Jira API   │             │
│  │         │    │             │    │             │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │  Issues  │  │ Approvals│  │    Evidence     │              │
│  │  Tasks   │  │ Workflows│  │    Linking      │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `issue.read` | Read issue details | Low |
| `issue.search` | Search issues (JQL) | Low |
| `issue.create` | Create new issue | Low |
| `issue.update` | Update issue fields | Medium |
| `issue.transition` | Change issue status | Medium |
| `issue.comment` | Add comment | Low |
| `issue.link` | Link issues | Low |
| `issue.attach` | Attach files | Low |
| `project.read` | Read project info | Low |
| `board.read` | Read board/sprint | Low |
| `user.read` | Read user info | Low |

---

## Authentication

### OAuth 2.0 (Recommended)

```yaml
jira:
  auth:
    method: oauth2
    client_id_source: vault
    client_id_path: kv/mcp/jira/client-id
    client_secret_source: vault
    client_secret_path: kv/mcp/jira/client-secret
    scopes:
      - read:jira-work
      - write:jira-work
      - read:jira-user
```

### API Token

```yaml
jira:
  auth:
    method: api_token
    email: bot@itqahn.io
    token_source: vault
    token_path: kv/mcp/jira/api-token
```

---

## Operations

### Read Issue

```json
{
  "operation": "issue.read",
  "params": {
    "issue_key": "PROJ-123",
    "fields": ["summary", "description", "status", "assignee", "labels"]
  }
}
```

Response:
```json
{
  "key": "PROJ-123",
  "fields": {
    "summary": "Implement user authentication",
    "description": "Add OAuth2 login flow...",
    "status": {
      "name": "In Progress",
      "category": "indeterminate"
    },
    "assignee": {
      "displayName": "Backend Builder",
      "emailAddress": "backend-builder@itqahn.io"
    },
    "labels": ["feature", "auth", "workflow:wf-xyz789"]
  }
}
```

### Search Issues (JQL)

```json
{
  "operation": "issue.search",
  "params": {
    "jql": "project = PROJ AND status = 'In Progress' AND labels = 'workflow:wf-xyz789'",
    "fields": ["summary", "status", "assignee"],
    "max_results": 50
  }
}
```

### Create Issue

```json
{
  "operation": "issue.create",
  "params": {
    "project_key": "PROJ",
    "issue_type": "Task",
    "summary": "Implement login endpoint",
    "description": "Create POST /api/login endpoint with OAuth2 flow",
    "labels": ["feature", "auth", "workflow:wf-xyz789", "agent:backend-builder"],
    "custom_fields": {
      "workflow_id": "wf-xyz789",
      "agent_id": "backend-builder",
      "compliance_tier": "sensitive"
    }
  }
}
```

Response:
```json
{
  "id": "10001",
  "key": "PROJ-124",
  "self": "https://jira.example.com/rest/api/3/issue/10001"
}
```

### Transition Issue

```json
{
  "operation": "issue.transition",
  "params": {
    "issue_key": "PROJ-123",
    "transition": "Done",
    "comment": "Completed implementation. Evidence: s3://evidence/...",
    "resolution": "Done"
  }
}
```

### Add Comment

```json
{
  "operation": "issue.comment",
  "params": {
    "issue_key": "PROJ-123",
    "body": "## Implementation Update\n\nPR created: https://github.com/org/repo/pull/456\n\n**Status**: Awaiting review\n**Agent**: backend-builder\n**Workflow**: wf-xyz789"
  }
}
```

### Link Issues

```json
{
  "operation": "issue.link",
  "params": {
    "inward_issue": "PROJ-123",
    "outward_issue": "PROJ-124",
    "link_type": "Blocks"
  }
}
```

---

## Workflow Integration

### Approval Workflows

Jira is used for human approvals in sensitive workflows:

```
1. Workflow reaches approval gate
       │
       ▼
2. Agent creates approval issue
       │
       ▼
3. Human reviews and approves in Jira
       │
       ▼
4. Agent polls for status change
       │
       ▼
5. Workflow continues on approval
```

### Approval Issue Template

```json
{
  "operation": "issue.create",
  "params": {
    "project_key": "APPROVALS",
    "issue_type": "Approval Request",
    "summary": "[Approval Required] Deploy user-service v1.2.3 to production",
    "description": "## Approval Request\n\n**Workflow**: wf-xyz789\n**Service**: user-service\n**Version**: 1.2.3\n**Environment**: production\n\n### Evidence Pack\n- SBOM: ✅ Generated\n- Security Scan: ✅ No critical issues\n- Tests: ✅ 245 passed\n\n### Approval Instructions\nTransition this issue to **Approved** to proceed.",
    "labels": ["approval", "production", "workflow:wf-xyz789"],
    "assignee": "security-team"
  }
}
```

### Evidence Linking

Every completed task links to evidence:

```json
{
  "operation": "issue.comment",
  "params": {
    "issue_key": "PROJ-123",
    "body": "## Evidence Pack\n\n- **Location**: s3://evidence/user-service/1.2.3/build-abc123\n- **SBOM**: [View](s3://evidence/.../sbom.json)\n- **Provenance**: [View](s3://evidence/.../provenance.json)\n- **Scans**: [View](s3://evidence/.../scans/)\n\n[Full Evidence Pack](https://portal.itqahn.io/evidence/wf-xyz789)"
  }
}
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  jira:
    enabled: true
    base_url: "https://itqahn.atlassian.net"

    auth:
      method: oauth2
      client_id_source: vault
      client_secret_source: vault

    defaults:
      default_project: "ITQAHN"
      workflow_label_prefix: "workflow:"
      agent_label_prefix: "agent:"

    rate_limits:
      requests_per_minute: 100

    custom_fields:
      workflow_id: "customfield_10001"
      agent_id: "customfield_10002"
      compliance_tier: "customfield_10003"
      evidence_url: "customfield_10004"
```

### Allowlist Entry

```yaml
roles:
  backend-builder:
    mcps:
      jira:
        operations:
          - issue.read
          - issue.search
          - issue.create
          - issue.update
          - issue.transition
          - issue.comment
          - issue.link
        constraints:
          project_keys: ["PROJ", "BACKEND"]
          allowed_transitions: ["In Progress", "In Review", "Done"]

  security-scanner:
    mcps:
      jira:
        operations:
          - issue.read
          - issue.create
          - issue.comment
        constraints:
          project_keys: ["SEC", "VULN"]
```

---

## Custom Fields

### Required Custom Fields

| Field | Purpose | Type |
|-------|---------|------|
| `workflow_id` | Link to Itqahn workflow | Text |
| `agent_id` | Creating agent | Text |
| `compliance_tier` | Compliance classification | Select |
| `evidence_url` | Evidence pack location | URL |
| `approval_deadline` | Approval SLA | Date |

### Field Mapping

```yaml
jira:
  field_mapping:
    workflow_id: customfield_10001
    agent_id: customfield_10002
    compliance_tier: customfield_10003
    evidence_url: customfield_10004
    approval_deadline: customfield_10005
```

---

## Webhooks

### Supported Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `issue_created` | New issue | Track new tasks |
| `issue_updated` | Field change | Sync status |
| `issue_transitioned` | Status change | Approval detection |
| `comment_created` | New comment | Human feedback |

### Webhook Configuration

```yaml
jira:
  webhooks:
    enabled: true
    endpoint: "https://itqahn.io/webhooks/jira"
    secret_source: vault
    secret_path: kv/mcp/jira/webhook-secret
    events:
      - issue_created
      - issue_updated
      - issue_transitioned
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `JIRA_AUTH_FAILED` | Authentication failed | Refresh token |
| `JIRA_NOT_FOUND` | Issue not found | Check key |
| `JIRA_PERMISSION` | Insufficient permissions | Check project access |
| `JIRA_TRANSITION_INVALID` | Invalid transition | Check workflow |
| `JIRA_RATE_LIMITED` | Rate limit exceeded | Back off |

### Retry Configuration

```yaml
jira:
  retry:
    max_attempts: 3
    initial_delay_ms: 1000
    retry_on:
      - JIRA_RATE_LIMITED
      - JIRA_SERVER_ERROR
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `jira_mcp_requests_total` | Total requests |
| `jira_mcp_latency` | Request latency |
| `jira_issues_created` | Issues created |
| `jira_transitions_total` | Status transitions |
| `jira_approval_latency` | Time to approval |

### Alerts

```yaml
alerts:
  - name: jira_auth_failures
    condition: rate(jira_mcp_errors{type="auth"}[5m]) > 0
    severity: critical

  - name: jira_approval_stale
    condition: jira_pending_approvals > 10
    severity: warning
```

---

## Security Considerations

### Access Control

- Service account with minimal permissions
- Project-scoped access only
- No admin access granted
- API token rotated every 90 days

### Data Handling

- No sensitive data in issue descriptions
- Evidence URLs use signed links
- Comments sanitized for PII
- Attachments scanned for secrets

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/05-compliance/evidence-pack.md` — Evidence linking
- `docs/06-operations/incident-response.md` — Incident tracking

---

**Version**: 2.0.0 | **Date**: 2026-01-06
