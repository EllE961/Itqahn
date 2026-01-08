# Security Policies

This directory contains security baseline policies for Itqahn applications.

## Policy Files

| Policy | Purpose |
|--------|---------|
| `security-headers.yaml` | HTTP security headers requirements |
| `csp-policy.yaml` | Content Security Policy configuration |
| `crypto-standards.yaml` | Cryptographic algorithm requirements |
| `auth-requirements.yaml` | Authentication requirements |
| `api-security.yaml` | API security standards |

## Enforcement

These policies are enforced at multiple layers:

1. **Build time**: CI checks validate configuration
2. **Deploy time**: Admission controllers verify compliance
3. **Runtime**: Service mesh enforces policies

## Related

- `docs/04-security/security-model.md` — Security architecture
- `docs/04-security/appsec-asvs.md` — ASVS mapping
- `policies/opa/security/` — OPA security policies
