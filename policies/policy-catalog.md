# Policy Catalog

This catalog maps policy modules to the lifecycle gates and compliance tiers.

---

## Policy Organization

```
policies/
├── opa/                  # Open Policy Agent rules
│   ├── mcp/              # MCP governance
│   ├── deploy/           # Deployment rules
│   ├── supply-chain/     # Supply chain security
│   ├── security/         # Security rules
│   ├── ui/               # UI governance
│   └── finops/           # Cost controls
├── kyverno/              # Kubernetes admission policies
├── security/             # Security baseline policies
└── compliance/           # Compliance control mappings
```

---

## Gate Mapping

### Gate 1 (Concept Lock)
- Risk tier must be assigned
- Compliance tier must be assigned

### Gate 2 (Experience Lock)
- Threat model required for Sensitive/Regulated
- API contracts required for any external API

### Gate 3 (Release Candidate)
- Evidence Pack required
- SBOM required
- Provenance required
- Security scans thresholds
- Design Jail checks for UI changes
- High-risk approvals present

---

## OPA Policy Modules

### MCP Governance
| Policy | Purpose |
|--------|---------|
| `opa/mcp/allowlist.rego` | Enforce agent-to-MCP permissions |
| `opa/mcp/rate_limits.rego` | Rate limiting rules (optional) |

### Supply Chain
| Policy | Purpose |
|--------|---------|
| `opa/supply-chain/sbom_required.rego` | Require SBOM for deployments |
| `opa/supply-chain/provenance_required.rego` | Require signed provenance |
| `opa/supply-chain/dependency_allowlist.rego` | Allowed dependencies (optional) |

### Deployment Governance
| Policy | Purpose |
|--------|---------|
| `opa/deploy/evidence_required.rego` | Require Evidence Pack |
| `opa/deploy/signature_required.rego` | Require artifact signatures (optional) |

### Security
| Policy | Purpose |
|--------|---------|
| `opa/security/no_secrets.rego` | Block secret exposure |
| `opa/security/high_risk_approvals.rego` | Require approvals for sensitive ops |
| `opa/security/prompt_injection_guard.rego` | Prompt injection defense (optional) |

### UI Governance
| Policy | Purpose |
|--------|---------|
| `opa/ui/design_jail.rego` | Enforce Design Jail rules |

### FinOps
| Policy | Purpose |
|--------|---------|
| `opa/finops/budget_caps.rego` | Token/cost budget enforcement |

---

## Kyverno Policies

| Policy | Purpose |
|--------|---------|
| `kyverno/require-resource-limits.yaml` | Require CPU/memory limits |
| `kyverno/disallow-privileged.yaml` | Block privileged containers |
| `kyverno/require-ttl-label.yaml` | Require TTL for ephemeral resources |

---

## Security Baseline Policies

| Policy | Purpose |
|--------|---------|
| `security/security-headers.yaml` | Required HTTP security headers |
| `security/csp-policy.yaml` | Content Security Policy |
| `security/crypto-standards.yaml` | Cryptographic requirements |
| `security/auth-requirements.yaml` | Authentication standards |
| `security/api-security.yaml` | API security requirements |

---

## Compliance Policies

| Policy | Purpose |
|--------|---------|
| `compliance/control-mapping.yaml` | Control-to-framework mapping |
| `compliance/audit-requirements.yaml` | Audit logging requirements |
| `compliance/evidence-requirements.yaml` | Evidence requirements by tier |

---

## Compliance Tiers

| Tier | Description | Policies |
|------|-------------|----------|
| **Baseline** | Standard controls | All OPA modules, baseline security |
| **Sensitive** | Enhanced controls | Baseline + stricter approvals, threat model |
| **Regulated** | Full audit trail | Sensitive + immutable logs, signed provenance |

See: `docs/05-compliance/compliance-tiers.md`

---

## Related Documents

- `docs/04-security/security-model.md` — Security architecture
- `docs/05-compliance/` — Compliance documentation
- `docs/07-integrations/mcp/mcp-allowlists.md` — MCP allowlists

---

**Version**: 2.0.0 | **Date**: 2026-01-06
