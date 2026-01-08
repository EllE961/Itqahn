# MCP Vault Integration

The Vault MCP provides secure access to secrets and dynamic credentials with strict scoping and audit trails.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     VAULT MCP FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│  Vault MCP  │───▶│   Vault     │             │
│  │         │    │             │    │   Server    │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │  Static  │  │  Dynamic │  │      PKI        │              │
│  │ Secrets  │  │  Creds   │  │  Certificates   │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level |
|-----------|-------------|------------|
| `kv.read` | Read KV secret | Medium |
| `kv.list` | List secret paths | Low |
| `database.issue` | Issue database credential | Medium |
| `aws.issue` | Issue AWS credential | Medium |
| `pki.issue` | Issue certificate | Medium |
| `transit.encrypt` | Encrypt data | Low |
| `transit.decrypt` | Decrypt data | Medium |
| `identity.lookup` | Lookup entity | Low |

### Forbidden Operations

| Operation | Reason |
|-----------|--------|
| `kv.write` | Secrets managed externally |
| `kv.delete` | Irreversible |
| `policy.write` | Admin only |
| `auth.configure` | Admin only |
| `seal/unseal` | Admin only |

---

## Authentication

### SPIFFE JWT Auth (Recommended)

```yaml
vault:
  auth:
    method: jwt
    role: itqahn-agent
    jwt_path: /var/run/secrets/spiffe/svid.jwt
    mount_path: auth/jwt
```

### Kubernetes Auth

```yaml
vault:
  auth:
    method: kubernetes
    role: itqahn-agent
    service_account_token_path: /var/run/secrets/kubernetes.io/serviceaccount/token
    mount_path: auth/kubernetes
```

### AppRole

```yaml
vault:
  auth:
    method: approle
    role_id_source: env
    role_id_env: VAULT_ROLE_ID
    secret_id_source: vault
    secret_id_path: auth/approle/role/itqahn-agent/secret-id
```

---

## Operations

### Read KV Secret

```json
{
  "operation": "kv.read",
  "params": {
    "mount": "kv",
    "path": "services/user-service/database",
    "version": null
  }
}
```

Response:
```json
{
  "data": {
    "host": "db.itqahn.io",
    "port": 5432,
    "database": "users"
  },
  "metadata": {
    "version": 3,
    "created_time": "2026-01-06T12:00:00Z"
  }
}
```

Note: Sensitive values (passwords, keys) are never returned directly. Use dynamic credentials instead.

### Issue Database Credential

```json
{
  "operation": "database.issue",
  "params": {
    "mount": "database",
    "role": "user-service-readonly",
    "ttl": "1h"
  }
}
```

Response:
```json
{
  "username": "v-itqahn-user-svc-ro-abc123",
  "password": "***REDACTED***",
  "ttl": 3600,
  "lease_id": "database/creds/user-service-readonly/xyz789"
}
```

### Issue AWS Credential

```json
{
  "operation": "aws.issue",
  "params": {
    "mount": "aws",
    "role": "s3-evidence-writer",
    "ttl": "1h"
  }
}
```

Response:
```json
{
  "access_key": "AKIA...",
  "secret_key": "***REDACTED***",
  "security_token": "***REDACTED***",
  "ttl": 3600,
  "lease_id": "aws/creds/s3-evidence-writer/abc123"
}
```

### Issue Certificate

```json
{
  "operation": "pki.issue",
  "params": {
    "mount": "pki",
    "role": "service-cert",
    "common_name": "user-service.production.svc.cluster.local",
    "ttl": "24h",
    "alt_names": ["user-service"]
  }
}
```

Response:
```json
{
  "certificate": "-----BEGIN CERTIFICATE-----...",
  "private_key": "***REDACTED***",
  "ca_chain": ["-----BEGIN CERTIFICATE-----..."],
  "serial_number": "12:34:56:78:90:ab:cd:ef",
  "expiration": "2026-01-07T12:00:00Z"
}
```

### Encrypt Data

```json
{
  "operation": "transit.encrypt",
  "params": {
    "mount": "transit",
    "key": "evidence-pack",
    "plaintext": "base64-encoded-data"
  }
}
```

Response:
```json
{
  "ciphertext": "vault:v1:abc123..."
}
```

### Decrypt Data

```json
{
  "operation": "transit.decrypt",
  "params": {
    "mount": "transit",
    "key": "evidence-pack",
    "ciphertext": "vault:v1:abc123..."
  }
}
```

Response:
```json
{
  "plaintext": "base64-encoded-data"
}
```

---

## Dynamic Credentials

### Why Dynamic Credentials?

| Static Secrets | Dynamic Credentials |
|----------------|---------------------|
| Long-lived | Short-lived (1h default) |
| Shared | Unique per request |
| Hard to rotate | Auto-expire |
| Audit difficult | Full audit trail |

### Credential Lifecycle

```
1. Agent requests credential
       │
       ▼
2. Vault generates unique credential
       │
       ▼
3. Credential has TTL (1h)
       │
       ▼
4. Agent uses credential
       │
       ▼
5. Credential auto-expires
       │
       ▼
6. Vault revokes access
```

### Supported Dynamic Backends

| Backend | Credential Type |
|---------|-----------------|
| `database` | PostgreSQL, MySQL, MongoDB |
| `aws` | IAM user, STS |
| `gcp` | Service account key, OAuth token |
| `azure` | Service principal |
| `pki` | X.509 certificates |
| `ssh` | SSH certificates |

---

## Secret Paths

### Path Convention

```
kv/
├── services/
│   ├── user-service/
│   │   ├── database
│   │   ├── api-keys
│   │   └── config
│   └── payment-service/
│       ├── database
│       └── stripe
├── infra/
│   ├── kubernetes/
│   └── cloud/
└── mcp/
    ├── github/
    ├── figma/
    └── jira/
```

### Path Constraints

```yaml
vault:
  path_constraints:
    allowed_paths:
      - "kv/services/{{service_name}}/*"
      - "kv/mcp/*"
    denied_paths:
      - "kv/infra/*"
      - "kv/admin/*"
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  vault:
    enabled: true
    address: "https://vault.itqahn.io"

    auth:
      method: jwt
      role: itqahn-agent
      jwt_path: /var/run/secrets/spiffe/svid.jwt

    defaults:
      ttl: 1h
      max_ttl: 4h

    rate_limits:
      requests_per_minute: 50

    tls:
      ca_cert: /etc/ssl/vault-ca.crt
      skip_verify: false
```

### Allowlist Entry

```yaml
roles:
  backend-builder:
    mcps:
      vault:
        operations:
          - kv.read
          - kv.list
          - database.issue
          - pki.issue
        constraints:
          kv_paths: ["kv/services/*"]
          database_roles: ["*-readonly"]
          pki_roles: ["service-cert"]
          max_ttl: "4h"

  sre-operator:
    mcps:
      vault:
        operations:
          - kv.read
          - kv.list
          - database.issue
          - aws.issue
          - pki.issue
          - transit.encrypt
          - transit.decrypt
        constraints:
          kv_paths: ["*"]
          max_ttl: "8h"
```

---

## Policies

### Agent Policy (Vault)

```hcl
# Vault policy for Itqahn agents
path "kv/data/services/*" {
  capabilities = ["read", "list"]
}

path "database/creds/*-readonly" {
  capabilities = ["read"]
}

path "pki/issue/service-cert" {
  capabilities = ["create", "update"]
}

path "transit/encrypt/evidence-pack" {
  capabilities = ["update"]
}

path "transit/decrypt/evidence-pack" {
  capabilities = ["update"]
}
```

### Policy Enforcement

```rego
# OPA policy for Vault MCP
package vault_mcp

deny[msg] {
    input.operation == "kv.read"
    not path_allowed(input.path)
    msg := sprintf("Path %v not in allowed paths", [input.path])
}

path_allowed(path) {
    some allowed in data.allowed_paths
    glob.match(allowed, ["/"], path)
}
```

---

## Audit Trail

### Audit Log Entry

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "type": "request",
  "auth": {
    "client_token": "hmac-sha256:abc123...",
    "accessor": "hmac-sha256:def456...",
    "entity_id": "entity-xyz789",
    "metadata": {
      "agent_id": "backend-builder",
      "workflow_id": "wf-xyz789",
      "tenant_id": "tenant-abc"
    }
  },
  "request": {
    "operation": "read",
    "path": "kv/data/services/user-service/database",
    "remote_address": "10.0.0.5"
  },
  "response": {
    "data": {
      "keys": ["host", "port", "database"]
    }
  }
}
```

### Audit Requirements

| Requirement | Implementation |
|-------------|----------------|
| All requests logged | Vault audit backend |
| HMAC sensitive data | Tokens and secrets hashed |
| Retained 2 years | Audit log archival |
| Tamper-proof | Append-only storage |

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `VAULT_AUTH_FAILED` | Authentication failed | Refresh token |
| `VAULT_FORBIDDEN` | Access denied | Check policy |
| `VAULT_NOT_FOUND` | Secret not found | Check path |
| `VAULT_SEALED` | Vault sealed | Alert ops |
| `VAULT_RATE_LIMITED` | Rate limit exceeded | Back off |

### Retry Configuration

```yaml
vault:
  retry:
    max_attempts: 3
    initial_delay_ms: 500
    retry_on:
      - VAULT_RATE_LIMITED
      - VAULT_UNAVAILABLE
```

---

## Security Considerations

### Credential Handling

- Never log secret values
- Zero credentials in memory after use
- Credentials never written to disk
- All credentials have TTL

### Network Security

- TLS required for all connections
- Certificate pinning enabled
- Network policies restrict access
- Vault in separate security zone

### Rotation

```yaml
vault:
  rotation:
    static_secrets:
      interval: 90d
      alert_before: 7d
    dynamic_ttl:
      default: 1h
      max: 4h
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `vault_mcp_requests_total` | Total requests |
| `vault_mcp_latency` | Request latency |
| `vault_credentials_issued` | Credentials issued |
| `vault_credentials_active` | Active leases |
| `vault_auth_failures` | Auth failures |

### Alerts

```yaml
alerts:
  - name: vault_auth_failures
    condition: rate(vault_mcp_errors{type="auth"}[5m]) > 0
    severity: critical

  - name: vault_lease_explosion
    condition: vault_credentials_active > 1000
    severity: warning

  - name: vault_sealed
    condition: vault_sealed == 1
    severity: critical
```

---

## Related Documents

- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/04-security/secrets-vault.md` — Secrets management
- `docs/04-security/identity-spiffe.md` — SPIFFE identity

---

**Version**: 2.0.0 | **Date**: 2026-01-06
