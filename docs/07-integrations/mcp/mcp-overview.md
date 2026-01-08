# MCP Overview

Model Context Protocol (MCP) is the controlled interface through which Itqahn agents interact with external systems. MCP is treated as **production infrastructure**, not plugin convenience.

---

## What is MCP?

MCP provides a standardized, policy-governed interface for agents to:

- Read and write code and documentation
- Query design sources (Figma, design systems)
- Interact with issue trackers (Jira, Linear, GitHub Issues)
- Access deployment and observability systems
- Fetch context safely with audit trails

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│  MCP Proxy  │───▶│  External   │             │
│  │         │    │  (Policy)   │    │  Service    │             │
│  └─────────┘    └──────┬──────┘    └─────────────┘             │
│                        │                                        │
│         ┌──────────────┼──────────────┐                        │
│         │              │              │                        │
│         ▼              ▼              ▼                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │   OPA    │  │  Audit   │  │  Rate    │                     │
│  │  Policy  │  │   Log    │  │  Limit   │                     │
│  └──────────┘  └──────────┘  └──────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Allowlist Only

Agents can only call approved MCPs. Unknown or unauthorized MCP calls are rejected.

```yaml
# Only allowlisted MCPs are accessible
mcp:
  mode: allowlist
  default_action: deny
```

### 2. Scoped Credentials

MCPs run with least privilege using workload identity (SPIFFE).

```yaml
# Each MCP has scoped credentials
mcp:
  github:
    identity: spiffe://itqahn.io/mcp/github
    scopes:
      - repo:read
      - issues:write
```

### 3. Audit Logs

Every MCP call is logged with workflow ID, agent ID, and policy verdict.

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "mcp": "github",
  "operation": "repo.read",
  "agent_id": "backend-builder",
  "workflow_id": "wf-xyz789",
  "policy_verdict": "allow",
  "duration_ms": 150
}
```

### 4. Policy Mediation

OPA decides whether an MCP call is allowed based on agent role, operation, and context.

### 5. Rate Limits

Enforced per tenant and per workflow to prevent denial-of-wallet attacks.

### 6. Deterministic Outputs

When possible, MCPs provide stable responses and schemas for reproducibility.

---

## MCP Categories

### Core MCPs (Required)

| MCP | Purpose | Default Mode |
|-----|---------|--------------|
| **GitHub** | PRs, checks, repo queries, code search | Read + scoped write |
| **Kubernetes** | Cluster state, deployments | Read-only |
| **Vault** | Dynamic secrets, certificate issuance | Scoped |
| **Observability** | Metrics, logs, traces, SLO status | Read-only |
| **Figma** | Design tokens, components, screenshots | Read-only |
| **Jira** | Issues, tasks, approvals | Read + write |

### Optional MCPs (Controlled)

| MCP | Purpose | Restrictions |
|-----|---------|--------------|
| **Docs Search** | Internal wiki queries | Read-only, sanitized |
| **Analytics** | Event schema governance | Schema-only |
| **Cloud Provider** | AWS/GCP/Azure operations | Policy-gated |

### Asset Generation MCPs

| MCP | Purpose | Restrictions |
|-----|---------|--------------|
| **Assets** | Asset registry, lint, drift checks | Design OS governed |
| **NanoBanana** | Image generation provider | API key via Vault, Design OS constraints |

> **NanoBanana**: Primary image generation provider for Asset Factory. API credentials are stored in Vault and injected at MCP server runtime. Agents NEVER have direct access to API keys. See `docs/07-integrations/mcp/mcp-nanobanana.md` for full specification.

---

## MCP Specification Requirements

Each MCP must publish:

| Requirement | Description |
|-------------|-------------|
| **Capabilities** | List of verbs and resources |
| **Authentication** | SPIFFE/OIDC method |
| **Rate Limits** | Quotas per tenant/workflow |
| **Logging Schema** | Audit log format |
| **Failure Modes** | How failures are handled |
| **Safe Fallbacks** | Graceful degradation behavior |

---

## MCP Request Flow

```
1. Agent requests MCP operation
       │
       ▼
2. MCP Proxy receives request
       │
       ▼
3. Policy evaluation (OPA)
       │
       ├── Deny → Return error, log
       │
       └── Allow
               │
               ▼
4. Rate limit check
       │
       ├── Exceeded → Queue or reject
       │
       └── OK
               │
               ▼
5. Execute operation
       │
       ▼
6. Log audit record
       │
       ▼
7. Return result to agent
```

---

## Configuration

### Global MCP Configuration

```yaml
mcp:
  global:
    timeout_seconds: 30
    retry:
      max_attempts: 3
      backoff_multiplier: 2

  rate_limits:
    per_workflow:
      requests_per_minute: 100
    per_tenant:
      requests_per_minute: 1000

  audit:
    enabled: true
    retention_days: 90
```

### Per-MCP Configuration

```yaml
mcp:
  github:
    enabled: true
    base_url: "https://api.github.com"
    auth:
      method: spiffe
      audience: "github.com"
    rate_limit:
      requests_per_minute: 50

  figma:
    enabled: true
    auth:
      method: oauth
      token_source: vault
    read_only: true
```

---

## Error Handling

### MCP Error Codes

| Code | Meaning | Agent Action |
|------|---------|--------------|
| `MCP_UNAUTHORIZED` | Policy denied access | Check allowlist |
| `MCP_RATE_LIMITED` | Rate limit exceeded | Back off and retry |
| `MCP_TIMEOUT` | Operation timed out | Retry with backoff |
| `MCP_UNAVAILABLE` | Service unreachable | Use fallback |
| `MCP_INVALID_REQUEST` | Malformed request | Fix request |

### Fallback Behavior

```yaml
mcp:
  fallback:
    github:
      on_unavailable: cache_read
      cache_ttl_minutes: 15

    figma:
      on_unavailable: use_cached_tokens
      cache_ttl_minutes: 60
```

---

## Monitoring

### MCP Metrics

| Metric | Description |
|--------|-------------|
| `mcp_requests_total` | Total MCP requests by type |
| `mcp_requests_latency` | Request latency histogram |
| `mcp_requests_errors` | Error count by type |
| `mcp_rate_limit_hits` | Rate limit violations |
| `mcp_policy_denials` | Policy denial count |

### Alerting

```yaml
alerts:
  - name: mcp_high_error_rate
    condition: rate(mcp_requests_errors[5m]) / rate(mcp_requests_total[5m]) > 0.05
    severity: warning

  - name: mcp_policy_denials_spike
    condition: rate(mcp_policy_denials[5m]) > 10
    severity: warning
```

---

## MCP Minimization Policy

Claude Code workers MUST prefer Skills over MCPs to reduce context bloat and improve efficiency.

### Skills vs MCPs

| Concept | Definition | Context Impact | When to Use |
|---------|------------|----------------|-------------|
| **Skill** | Internal procedure without external calls | Low | Default for all local operations |
| **MCP** | External tool via Model Context Protocol | High | Only when external system access required |

### Decision Table

| Task | Approach | Rationale |
|------|----------|-----------|
| Generate code | **Skill** | Internal Claude capability |
| Read local file | **Skill** | Direct file system access |
| Write local file | **Skill** | Direct file system access |
| Run tests | **Skill** | Local command execution |
| Run linter | **Skill** | Local command execution |
| Search codebase | **Skill** | Local grep/find operations |
| Create GitHub issue | **MCP** | External GitHub API |
| Create GitHub PR | **MCP** | External GitHub API |
| Read Figma design | **MCP** | External Figma API |
| Query Jira ticket | **MCP** | External Jira API |
| Fetch from Vault | **MCP** | External secrets API |
| Generate image | **MCP** | External NanoBanana API |

### Minimization Rules

```yaml
mcp_minimization:
  default_action: prefer_skill

  rules:
    - name: "Exhaust Skills first"
      description: "Only use MCP when Skill cannot accomplish task"
      enforcement: warning_on_unnecessary_mcp

    - name: "Batch MCP calls"
      description: "Combine multiple MCP calls to same system"
      enforcement: suggest_batching

    - name: "Cache MCP responses"
      description: "Cache responses for session duration when appropriate"
      ttl_minutes: 15
      cacheable: [read_operations]

    - name: "Summarize MCP outputs"
      description: "Compress large MCP responses before adding to context"
      max_output_tokens: 500
```

### MCP Call Logging

All MCP calls MUST be logged for audit and context analysis:

```json
{
  "mcp_call_log": {
    "timestamp": "2026-01-08T12:00:00Z",
    "run_id": "run-01J5ABCD",
    "worker_id": "worker-1",
    "mcp_server": "github",
    "operation": "create_pr",
    "input_summary": "Create PR for user-auth",
    "output_summary": "PR #156 created",
    "tokens_consumed": 1500,
    "cached": false,
    "could_have_used_skill": false
  }
}
```

### Operator Mode MCP Boundaries

Even in Operator Mode (with `--dangerously-skip-permissions`), MCPs are still bounded:

| Control | Status | Reason |
|---------|--------|--------|
| **Allowlist enforcement** | Active | Only approved MCPs accessible |
| **Rate limiting** | Active | Prevents runaway costs |
| **Audit logging** | Active | Every MCP call logged |
| **Policy evaluation** | Active | OPA decides per-call |
| **Credential isolation** | Active | Secrets via Vault only |

**No MCP can:**
- Access credentials directly (always via Vault)
- Bypass policy evaluation
- Operate without audit logging
- Exceed rate limits
- Access non-allowlisted external systems

### Context Budget Impact

MCP calls consume context budget. Workers MUST monitor:

```yaml
context_monitoring:
  mcp_call_weight: high  # MCP responses are context-heavy

  budget_tracking:
    - before_mcp_call: check_remaining_budget
    - after_mcp_call: update_consumed_budget
    - on_budget_warning: consider_summarization
    - on_budget_exceeded: produce_context_reset_pack

  response_compression:
    max_inline_tokens: 500
    large_response_action: write_to_file_and_reference
```

---

## Related Documents

- `docs/06-operations/claude-code-operating-model.md` — Skills vs MCPs in Claude Code
- `docs/06-operations/context-engineering-playbook.md` — Context engineering and MCP policy
- `docs/07-integrations/mcp/mcp-security-model.md` — Security details
- `docs/07-integrations/mcp/mcp-allowlists.md` — Allowlist configuration
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/07-integrations/mcp/mcp-nanobanana.md` — NanoBanana MCP specification
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory with NanoBanana
- `policies/opa/mcp/` — MCP policies
- `CLAUDE.md` — Root rules file with Skill-first policy

---

**Version**: 2.4.0 | **Date**: 2026-01-08
