# Workload Identity (SPIFFE/SPIRE)

Every workload in Itqahn has a cryptographic identity. No service trusts another based on network location alone.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPIFFE/SPIRE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SPIRE SERVER                          │    │
│  │                                                          │    │
│  │  • Certificate Authority                                 │    │
│  │  • Registration API                                      │    │
│  │  • Attestation policies                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│              ┌─────────────┼─────────────┐                      │
│              │             │             │                      │
│              ▼             ▼             ▼                      │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  SPIRE Agent  │ │  SPIRE Agent  │ │  SPIRE Agent  │         │
│  │   (Node 1)    │ │   (Node 2)    │ │   (Node 3)    │         │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘         │
│          │                 │                 │                  │
│          ▼                 ▼                 ▼                  │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │   Workload    │ │   Workload    │ │   Workload    │         │
│  │   (SVID)      │ │   (SVID)      │ │   (SVID)      │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## SPIFFE Concepts

### SPIFFE ID

A unique identifier for every workload:

```
spiffe://itqahn.io/ns/production/sa/user-service
         └─────────┘ └──────────┘ └─────────────┘
         Trust domain  Path components   Workload
```

| Component | Description |
|-----------|-------------|
| Trust domain | `itqahn.io` (organization-wide) |
| Namespace | Kubernetes namespace |
| Service account | Kubernetes service account |

### SVID (SPIFFE Verifiable Identity Document)

Short-lived credential proving identity:

| Format | Use Case | TTL |
|--------|----------|-----|
| X.509 | mTLS, TLS client auth | 1 hour |
| JWT | API authentication | 5 minutes |

### Trust Bundle

Collection of CA certificates for verifying SVIDs from trusted domains.

---

## Workload Attestation

How SPIRE verifies workload identity:

### Kubernetes Attestor

```yaml
# Registration entry
spiffe_id: spiffe://itqahn.io/ns/production/sa/user-service
parent_id: spiffe://itqahn.io/spire/agent/k8s_sat/node-1
selectors:
  - k8s:ns:production
  - k8s:sa:user-service
  - k8s:container-image:registry.io/user-service@sha256:abc123
```

### Attestation Flow

```
1. Workload starts
       │
       ▼
2. SPIRE Agent detects workload
       │
       ▼
3. Agent attests workload attributes
   • Namespace
   • Service account
   • Container image hash
       │
       ▼
4. Agent requests SVID from Server
       │
       ▼
5. Server validates against registration
       │
       ▼
6. Server issues SVID to workload
       │
       ▼
7. Workload uses SVID for authentication
```

---

## mTLS Configuration

All service-to-service communication uses mutual TLS:

```yaml
# Envoy sidecar configuration
static_resources:
  clusters:
    - name: user-service
      type: STRICT_DNS
      transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
          common_tls_context:
            tls_certificate_sds_secret_configs:
              - name: "spiffe://itqahn.io/ns/production/sa/api-gateway"
                sds_config:
                  api_config_source:
                    api_type: GRPC
                    grpc_services:
                      - envoy_grpc:
                          cluster_name: spire-agent
            validation_context_sds_secret_config:
              name: "spiffe://itqahn.io"
              sds_config:
                api_config_source:
                  api_type: GRPC
                  grpc_services:
                    - envoy_grpc:
                        cluster_name: spire-agent
```

---

## Identity-Based Access Control

### Policy Example (OPA)

```rego
package authz

default allow = false

# Allow user-service to call auth-service
allow {
  input.source.spiffe_id == "spiffe://itqahn.io/ns/production/sa/user-service"
  input.destination.spiffe_id == "spiffe://itqahn.io/ns/production/sa/auth-service"
  input.method == "POST"
  input.path == "/api/v1/validate"
}
```

### Vault Policy Binding

```hcl
# Vault policy bound to SPIFFE ID
path "secret/data/production/user-service/*" {
  capabilities = ["read"]
}

# Role binding
vault write auth/jwt/role/user-service \
  bound_claims='{"sub": "spiffe://itqahn.io/ns/production/sa/user-service"}' \
  policies="user-service-policy"
```

---

## Agent Identity

Itqahn agents have SPIFFE identities:

```
spiffe://itqahn.io/agent/backend-builder
spiffe://itqahn.io/agent/security-reviewer
spiffe://itqahn.io/agent/release-manager
```

### Agent Registration

```yaml
# Agent workload registration
- spiffe_id: spiffe://itqahn.io/agent/backend-builder
  selectors:
    - k8s:ns:itqahn-agents
    - k8s:sa:backend-builder
    - k8s:pod-label:agent:backend-builder
  ttl: 3600
```

---

## SVID Rotation

SVIDs are automatically rotated before expiry:

| Setting | Value |
|---------|-------|
| Default TTL | 1 hour |
| Rotation buffer | 50% of TTL |
| Grace period | 5 minutes |

```python
# SDK handles rotation automatically
from spiffe import SpiffeWorkloadAPI

api = SpiffeWorkloadAPI()
# SVIDs automatically refreshed
svid = api.fetch_x509_svid()
```

---

## Federation

For multi-cluster or external services:

```yaml
# Trust bundle exchange
federation:
  - trust_domain: partner.example.com
    bundle_endpoint:
      address: https://partner.example.com/spire/bundle
      spiffe_id: spiffe://partner.example.com/spire/server
```

---

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| SVID not issued | Check registration entries | Add missing selectors |
| mTLS failure | Verify trust bundles | Update federation config |
| Identity mismatch | Check pod labels/SA | Fix workload configuration |

### Debug Commands

```bash
# Check agent health
spire-agent healthcheck

# List registered entries
spire-server entry show

# View current SVID
spire-agent api fetch x509
```

---

## Related Documents

- `docs/04-security/secrets-vault.md` — Vault integration
- `docs/04-security/security-model.md` — Overall security model
- `docs/02-architecture/reference-architecture.md` — Architecture overview

---

**Version**: 2.0.0 | **Date**: 2026-01-06
