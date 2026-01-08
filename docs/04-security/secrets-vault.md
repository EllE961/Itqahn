# Secrets Management (Vault)

Itqahn uses HashiCorp Vault for secretless runtime. Agents never handle long-lived credentials.

---

## The Golden Rule

**Agents must never handle raw long-lived secrets.**

All credential access is:
- Identity-bound (SPIFFE)
- Short-lived (minutes)
- Audited (every access logged)
- Policy-gated (least privilege)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VAULT ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     VAULT CLUSTER                        │    │
│  │                                                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │   Secret    │  │   Database  │  │    PKI      │     │    │
│  │  │   Engine    │  │   Engine    │  │   Engine    │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  │                                                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │    AWS      │  │    GCP      │  │   Azure     │     │    │
│  │  │   Engine    │  │   Engine    │  │   Engine    │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  │                                                          │    │
│  └──────────────────────────┬───────────────────────────────┘    │
│                             │                                    │
│                    ┌────────┴────────┐                          │
│                    │    JWT Auth     │                          │
│                    │  (SPIFFE SVIDs) │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              │              │              │                    │
│              ▼              ▼              ▼                    │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│        │ Workload │  │ Workload │  │  Agent   │                │
│        │    A     │  │    B     │  │          │                │
│        └──────────┘  └──────────┘  └──────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dynamic Secrets

### Database Credentials

```hcl
# Database secret engine configuration
path "database/creds/user-service-readonly" {
  capabilities = ["read"]
}

# Role definition
resource "vault_database_secret_backend_role" "user-service" {
  name    = "user-service-readonly"
  backend = vault_mount.postgres.path
  db_name = "users-db"

  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"
  ]

  default_ttl = "300"   # 5 minutes
  max_ttl     = "600"   # 10 minutes
}
```

### Cloud Credentials

```hcl
# AWS secret engine
path "aws/creds/s3-uploader" {
  capabilities = ["read"]
}

# AWS role
resource "vault_aws_secret_backend_role" "s3-uploader" {
  name            = "s3-uploader"
  backend         = vault_mount.aws.path
  credential_type = "assumed_role"
  role_arns       = ["arn:aws:iam::123456789:role/s3-uploader"]
  default_sts_ttl = 900   # 15 minutes
  max_sts_ttl     = 1800  # 30 minutes
}
```

### API Keys

```hcl
# KV secret engine for third-party API keys
path "secret/data/integrations/stripe" {
  capabilities = ["read"]
}
```

---

## Authentication Flow

### SPIFFE JWT Auth

```
1. Workload receives SVID from SPIRE
       │
       ▼
2. Workload exchanges JWT-SVID for Vault token
       │
       ▼
3. Vault validates JWT against SPIRE trust bundle
       │
       ▼
4. Vault issues token with bound policies
       │
       ▼
5. Workload requests dynamic secret
       │
       ▼
6. Vault issues short-lived credential
       │
       ▼
7. Credential auto-expires after TTL
```

### Configuration

```hcl
# JWT auth method configuration
resource "vault_jwt_auth_backend" "spiffe" {
  path               = "jwt"
  jwks_url           = "https://spire-server:8443/keys"
  default_role       = "default"
  bound_issuer       = "spiffe://itqahn.io"
}

# Role binding SPIFFE ID to Vault policies
resource "vault_jwt_auth_backend_role" "user-service" {
  backend        = vault_jwt_auth_backend.spiffe.path
  role_name      = "user-service"
  token_policies = ["user-service-secrets"]

  bound_claims = {
    sub = "spiffe://itqahn.io/ns/production/sa/user-service"
  }

  user_claim = "sub"
  role_type  = "jwt"
}
```

---

## Access Policies

### Policy Structure

```hcl
# Per-service policy
path "database/creds/user-service-*" {
  capabilities = ["read"]
}

path "secret/data/production/user-service/*" {
  capabilities = ["read"]
}

# Deny access to other services
path "secret/data/production/auth-service/*" {
  capabilities = ["deny"]
}
```

### Tenant Isolation

```hcl
# Tenant-scoped secrets
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/*" {
  capabilities = ["read"]
}

# Deny access to other tenants
path "secret/data/tenants/*" {
  capabilities = ["deny"]
}
```

---

## Audit Logging

All Vault operations are logged:

```json
{
  "time": "2026-01-06T12:00:00Z",
  "type": "response",
  "auth": {
    "client_token": "hmac-sha256:...",
    "accessor": "hmac-sha256:...",
    "display_name": "jwt-spiffe://itqahn.io/ns/production/sa/user-service",
    "policies": ["user-service-secrets"],
    "metadata": {
      "role": "user-service"
    }
  },
  "request": {
    "id": "req-abc123",
    "operation": "read",
    "path": "database/creds/user-service-readonly",
    "remote_address": "10.0.0.5"
  },
  "response": {
    "data": {
      "username": "v-user-service-abc123"
    }
  }
}
```

---

## Prohibited Patterns

| Pattern | Problem | Alternative |
|---------|---------|-------------|
| Environment variables with secrets | Visible in logs, process listing | Vault sidecar/agent |
| Secrets in prompts | LLM training data risk | Reference by path, fetch at runtime |
| `.env` files | Committed to repos | Vault integration |
| Long-lived API keys | Compromise window | Dynamic credentials |
| Shared credentials | No audit attribution | Per-workload identity |

---

## Required Controls

| Control | Implementation |
|---------|----------------|
| Secret scanning | CI gates, pre-commit hooks |
| Least privilege | Scoped Vault policies |
| Short TTLs | Max 1 hour for most secrets |
| Automatic revocation | Incident response automation |
| Tenant separation | Policy-enforced path isolation |
| Rotation | Automated, no human intervention |

---

## SDK Usage

### Python

```python
import hvac
from spiffe import SpiffeWorkloadAPI

# Get SPIFFE identity
spiffe_api = SpiffeWorkloadAPI()
jwt_svid = spiffe_api.fetch_jwt_svid(audience=["vault"])

# Authenticate to Vault
client = hvac.Client(url="https://vault:8200")
client.auth.jwt.jwt_login(
    role="user-service",
    jwt=jwt_svid.token
)

# Get dynamic database credentials
creds = client.secrets.database.generate_credentials(
    name="user-service-readonly"
)

# Use credentials (they auto-expire)
db_user = creds["data"]["username"]
db_pass = creds["data"]["password"]
```

### Sidecar Pattern

```yaml
# Vault Agent sidecar
containers:
  - name: vault-agent
    image: hashicorp/vault:latest
    args:
      - agent
      - -config=/etc/vault/agent.hcl

  - name: app
    image: user-service:latest
    volumeMounts:
      - name: vault-secrets
        mountPath: /secrets
        readOnly: true

volumes:
  - name: vault-secrets
    emptyDir:
      medium: Memory
```

---

## Emergency Procedures

### Credential Revocation

```bash
# Revoke all tokens for a service
vault token revoke -mode path auth/jwt/login/user-service

# Revoke specific lease
vault lease revoke database/creds/user-service-readonly/abc123

# Revoke all leases for a service
vault lease revoke -prefix database/creds/user-service-readonly/
```

### Incident Response

On security incident:
1. Revoke all active leases
2. Rotate root credentials
3. Audit access logs
4. Re-issue credentials after remediation

---

## Related Documents

- `docs/04-security/identity-spiffe.md` — Workload identity
- `docs/04-security/security-model.md` — Security architecture
- `templates/security/SECRETS.md` — Secret management template

---

**Version**: 2.0.0 | **Date**: 2026-01-06
