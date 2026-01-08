# Compliance Policies

This directory contains compliance control mappings and regulatory requirements for Itqahn.

## Policy Files

| Policy | Purpose |
|--------|---------|
| `control-mapping.yaml` | Maps Itqahn controls to compliance frameworks |
| `data-handling.yaml` | Data classification and handling requirements |
| `audit-requirements.yaml` | Audit logging and retention requirements |
| `evidence-requirements.yaml` | Evidence collection requirements per tier |

## Compliance Frameworks

Itqahn supports mapping to these frameworks:

- SOC 2 Type II
- ISO 27001
- NIST 800-53
- GDPR
- CCPA
- PCI DSS (when applicable)
- HIPAA (when applicable)

## Enforcement

Compliance policies are enforced through:

1. **Evidence Pack validation** — Required artifacts per tier
2. **Audit logging** — Automatic event capture
3. **Access controls** — Role-based restrictions
4. **Data handling** — Classification-driven controls

## Related

- `docs/05-compliance/` — Compliance documentation
- `docs/05-compliance/compliance-tiers.md` — Tier definitions
- `policies/opa/` — Policy enforcement rules
