# MCP Security Model

This document defines the security architecture for Model Context Protocol (MCP) integrations in Itqahn.

---

## Security Principles

### Zero Trust for MCP

Every MCP call is:

1. **Authenticated**: Verified agent identity via SPIFFE
2. **Authorized**: Policy-checked before execution
3. **Audited**: Logged with full context
4. **Rate-limited**: Bounded to prevent abuse
5. **Scoped**: Minimal required permissions

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SECURITY LAYERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: Identity                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  SPIFFE workload identity for agent verification        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 2: Policy           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  OPA policy evaluation for every operation              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 3: Credential       ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Dynamic secrets from Vault, scoped per operation       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 4: Transport        ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  mTLS encryption, certificate validation                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  Layer 5: Audit            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Immutable audit log for compliance and forensics       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication

### SPIFFE Identity

Every MCP client authenticates via SPIFFE SVID:

```
spiffe://itqahn.io/agent/{agent-type}/{tenant-id}/{workflow-id}
```

Example:
```
spiffe://itqahn.io/agent/backend-builder/tenant-abc/wf-xyz789
```

### Identity Verification

```go
func VerifyMCPClient(ctx context.Context, svid *x509svid.SVID) error {
    // Verify SPIFFE ID format
    if !strings.HasPrefix(svid.ID.String(), "spiffe://itqahn.io/agent/") {
        return ErrInvalidIdentity
    }

    // Extract agent type
    agentType := extractAgentType(svid.ID)

    // Verify agent is registered
    if !isRegisteredAgent(agentType) {
        return ErrUnknownAgent
    }

    return nil
}
```

---

## Authorization

### Policy-Based Access Control

Every MCP operation is evaluated by OPA:

```rego
# policies/opa/mcp/authorization.rego
package mcp

default allow = false

allow {
    # Check agent has MCP in allowlist
    agent_allowlist := data.allowlists[input.agent_type]
    input.mcp_operation in agent_allowlist

    # Check tenant is authorized
    input.tenant_id == data.tenants[input.tenant_id]

    # Check operation-specific rules
    operation_allowed
}

operation_allowed {
    input.operation == "read"
}

operation_allowed {
    input.operation == "write"
    input.agent_type in data.write_agents
    human_approved
}

human_approved {
    input.approval_id != ""
    data.approvals[input.approval_id].status == "approved"
}
```

### Permission Matrix

| Agent Type | Read | Write | Delete | Admin |
|------------|------|-------|--------|-------|
| Frontend Builder | ✅ | ✅ (scoped) | ❌ | ❌ |
| Backend Builder | ✅ | ✅ (scoped) | ❌ | ❌ |
| Security Scanner | ✅ | ❌ | ❌ | ❌ |
| Policy Author | ✅ | ✅ (policies) | ❌ | ❌ |
| SRE Bot | ✅ | ✅ (infra) | ✅ (limited) | ❌ |

---

## Credential Management

### Dynamic Credentials

MCP credentials are never static. All credentials are:

1. **Short-lived**: Maximum 1 hour TTL
2. **Scoped**: Minimal permissions for the operation
3. **Audited**: Usage tracked in Vault
4. **Revocable**: Can be revoked immediately

```yaml
# Vault secret engine configuration
vault:
  mcp_credentials:
    github:
      type: github_app
      ttl: 1h
      max_ttl: 4h
      scopes:
        - repo:read
        - issues:write

    figma:
      type: oauth
      ttl: 1h
      scopes:
        - file:read
```

### Credential Flow

```
1. Agent requests MCP operation
       │
       ▼
2. MCP Proxy requests credential from Vault
       │
       ▼
3. Vault issues short-lived credential
       │
       ▼
4. MCP Proxy uses credential for operation
       │
       ▼
5. Credential auto-expires
```

---

## Transport Security

### mTLS Requirements

All MCP traffic uses mutual TLS:

| Requirement | Value |
|-------------|-------|
| TLS Version | 1.3 only |
| Cipher Suites | TLS_AES_256_GCM_SHA384 |
| Certificate Authority | Internal PKI |
| Certificate Lifetime | 24 hours |
| OCSP Stapling | Required |

### Certificate Validation

```yaml
tls:
  verify_client: true
  client_ca: /etc/ssl/itqahn-ca.crt
  min_version: TLS1.3
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_CHACHA20_POLY1305_SHA256
```

---

## Audit Logging

### Audit Record Schema

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "event_type": "mcp_operation",
  "mcp": "github",
  "operation": "repo.read",
  "resource": "itqahn-org/user-service",
  "agent": {
    "type": "backend-builder",
    "id": "agent-abc123",
    "spiffe_id": "spiffe://itqahn.io/agent/backend-builder/tenant-abc/wf-xyz789"
  },
  "workflow": {
    "id": "wf-xyz789",
    "phase": "experience"
  },
  "tenant_id": "tenant-abc",
  "policy": {
    "verdict": "allow",
    "rules_evaluated": ["mcp/github/read"],
    "evaluation_time_ms": 2
  },
  "result": {
    "status": "success",
    "duration_ms": 150
  }
}
```

### Audit Requirements

| Requirement | Implementation |
|-------------|----------------|
| Immutability | Append-only log storage |
| Retention | 2 years minimum |
| Integrity | Cryptographic hash chain |
| Availability | Replicated across regions |
| Searchability | Indexed by workflow, agent, tenant |

---

## Rate Limiting

### Rate Limit Tiers

| Tier | Per-Workflow | Per-Tenant | Per-Agent |
|------|--------------|------------|-----------|
| Standard | 100/min | 1000/min | 200/min |
| Elevated | 200/min | 2000/min | 400/min |
| Unlimited | N/A | 10000/min | N/A |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704542460
X-RateLimit-Scope: workflow
```

### Denial-of-Wallet Protection

```yaml
rate_limits:
  denial_of_wallet:
    # Alert if spend rate exceeds threshold
    alert_threshold_usd_per_minute: 10
    # Hard stop if spend exceeds limit
    hard_stop_usd_per_hour: 100
    # Circuit breaker
    circuit_breaker:
      failure_threshold: 10
      recovery_timeout_seconds: 60
```

---

## Threat Model

### Threats and Mitigations

| Threat | Mitigation |
|--------|------------|
| Credential theft | Dynamic credentials, short TTL |
| Privilege escalation | OPA policy enforcement |
| Data exfiltration | Rate limits, audit logging |
| Man-in-the-middle | mTLS with certificate pinning |
| Replay attacks | Request signing, nonce validation |
| Denial of service | Rate limiting, circuit breakers |

### Asset-Specific Threats

| Threat | Description | Mitigation |
|--------|-------------|------------|
| **Prompt injection** | Malicious instructions in asset generation prompts | Prompt sanitization, blocked pattern detection |
| **License laundering** | Using models with NC/restricted licenses for commercial use | License verification, model allowlist |
| **Cross-tenant asset leakage** | Assets from one tenant accessible to another | Namespaced registries, tenant isolation |
| **Steganography** | Hidden data embedded in generated images | Hash verification, metadata stripping |
| **Denial-of-wallet** | Excessive generation costs from runaway workflows | Per-workflow budget limits, circuit breakers |
| **Style anchor poisoning** | Compromised style anchor leading to off-brand assets | Style anchor versioning, approval workflow |
| **Model output manipulation** | Provider returning manipulated images | Output validation, drift detection |

### Asset Security Controls

```yaml
asset_security:
  prompt_sanitization:
    enabled: true
    blocked_patterns:
      - "ignore previous"
      - "system:"
      - "jailbreak"
    max_prompt_length: 2000

  license_verification:
    enabled: true
    require_commercial_license: true
    blocked_models:
      - "model-with-nc-license"

  tenant_isolation:
    registry_namespace: "tenant-{tenant_id}/"
    cross_tenant_access: deny

  output_validation:
    hash_verification: true
    metadata_strip: true
    max_file_size_mb: 50

  budget_protection:
    per_generation_max_usd: 0.50
    per_workflow_max_usd: 5.00
    circuit_breaker_enabled: true
```

### Attack Surface

```
┌─────────────────────────────────────────────────────────────────┐
│                      ATTACK SURFACE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  External Threats:                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • Compromised external service credentials              │    │
│  │ • MCP endpoint exploitation                             │    │
│  │ • Network interception                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Internal Threats:                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • Malicious agent behavior                              │    │
│  │ • Policy bypass attempts                                │    │
│  │ • Credential abuse                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Mitigations:                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • Zero trust architecture                               │    │
│  │ • Defense in depth                                      │    │
│  │ • Continuous monitoring                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Incident Response

### MCP Security Incidents

| Incident Type | Response |
|---------------|----------|
| Credential leak | Immediate revocation, rotate all credentials |
| Unauthorized access | Block agent, investigate, file IR |
| Policy bypass | Emergency policy update, block operation |
| Rate limit abuse | Throttle tenant, investigate |

### Response Playbook

```yaml
mcp_security_incident:
  severity: P1
  steps:
    - action: Revoke affected credentials
      timeout: 5m
    - action: Block agent/tenant
      timeout: 5m
    - action: Capture audit logs
      timeout: 15m
    - action: Notify security team
      timeout: immediate
    - action: Root cause analysis
      timeout: 24h
```

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/07-integrations/mcp/mcp-allowlists.md` — Allowlist configuration
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/04-security/identity-spiffe.md` — SPIFFE identity
- `docs/04-security/secrets-vault.md` — Vault integration

---

**Version**: 2.1.0 | **Date**: 2026-01-08
