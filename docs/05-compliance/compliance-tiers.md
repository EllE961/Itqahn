# Compliance Tiers

Itqahn supports multiple compliance levels via policy profiles. The tier selected at Gate 1 determines which controls apply.

---

## Tier Overview

| Tier | Name | Use Case | Controls |
|------|------|----------|----------|
| **Tier 0** | Baseline | Internal tools, prototypes | Standard |
| **Tier 1** | Sensitive | PII, customer data | Enhanced |
| **Tier 2** | Regulated | PCI, HIPAA, financial | Strict |

---

## Tier 0: Baseline

**For**: Internal tools, non-sensitive workloads, prototypes

### Required Controls

| Category | Control |
|----------|---------|
| **Evidence** | Evidence Pack required |
| **Security** | SAST, SCA, secret scanning |
| **Testing** | Unit tests (70% coverage) |
| **Review** | Standard PR review |
| **Deploy** | Evidence verification |
| **SLO** | Standard SLOs |

### Gate Requirements

| Gate | Requirements |
|------|--------------|
| Gate 1 | PRD, risk tier, budget |
| Gate 2 | Design, API contracts |
| Gate 3 | Tests pass, Evidence Pack |
| Gate 4 | SLO baseline |

### Policy Profile

```yaml
tier: baseline
security:
  sast: required
  sca: required
  dast: optional
  secret_scan: required
  container_scan: required

testing:
  unit_coverage: 70
  integration: required
  e2e: optional

review:
  approvers: 1
  security_review: optional
  human_auth_review: false

evidence:
  sbom: required
  provenance: required
  attestations: required
```

---

## Tier 1: Sensitive Data

**For**: PII, customer data, enterprise identity, internal systems with sensitive data

### Additional Controls

| Category | Control |
|----------|---------|
| **Data** | Data classification required |
| **Privacy** | Retention policies enforced |
| **Access** | RBAC + audit logging |
| **Testing** | Integration tests required (80% coverage) |
| **Review** | Security review for auth changes |
| **Isolation** | Namespace isolation minimum |
| **Logging** | Full audit trail |

### Gate Requirements

| Gate | Additional Requirements |
|------|------------------------|
| Gate 1 | Data classification |
| Gate 2 | Threat model, privacy impact |
| Gate 3 | Security review, DAST |
| Gate 4 | Access review |

### Policy Profile

```yaml
tier: sensitive
inherits: baseline

security:
  dast: required
  threat_model: required
  penetration_test: annual

testing:
  unit_coverage: 80
  integration: required
  e2e: required

review:
  approvers: 2
  security_review: required_for_auth
  human_auth_review: true
  privacy_review: required

data:
  classification: required
  retention_policy: required
  encryption_at_rest: required
  encryption_in_transit: required

isolation:
  mode: namespace
  rls: required
```

---

## Tier 2: Regulated

**For**: Payment data (PCI-DSS), health data (HIPAA), financial services, government

### Additional Controls

| Category | Control |
|----------|---------|
| **Change Mgmt** | CAB approval required |
| **Evidence** | Enhanced attestations |
| **Access** | MFA required, JIT access |
| **Audit** | External audit support |
| **Testing** | Penetration testing |
| **Isolation** | vCluster or dedicated |
| **MCP** | Restricted tool set |

### Gate Requirements

| Gate | Additional Requirements |
|------|------------------------|
| Gate 1 | Compliance officer review |
| Gate 2 | External threat model review |
| Gate 3 | Compliance attestation |
| Gate 4 | Audit readiness verification |

### Policy Profile

```yaml
tier: regulated
inherits: sensitive

security:
  penetration_test: quarterly
  vulnerability_scan: daily
  red_team: required

testing:
  unit_coverage: 90
  security_tests: required
  chaos_testing: required

review:
  approvers: 3
  security_review: always
  compliance_review: always
  cab_approval: required
  human_auth_review: always

evidence:
  enhanced_attestations: required
  audit_trail: 7_years
  change_tickets: required

access:
  mfa: required
  jit: required
  access_review: quarterly

isolation:
  mode: vcluster_or_dedicated
  encryption_keys: tenant_specific

mcp:
  restricted_set: true
  human_approval_for_external: true
```

---

## Tier Selection

### Selection Criteria

| Factor | Tier 0 | Tier 1 | Tier 2 |
|--------|--------|--------|--------|
| PII | No | Yes | Yes |
| Payment data | No | No | Yes |
| Health data | No | No | Yes |
| Public-facing | Any | Any | Requires T1+ |
| External users | Any | Recommended | - |
| Financial data | No | Limited | Yes |

### Decision Flow

```
Does it handle payment/health/gov data?
         │
    ┌────┴────┐
   Yes       No
    │         │
  Tier 2     Does it handle PII?
              │
         ┌────┴────┐
        Yes       No
         │         │
       Tier 1    Is it public-facing?
                   │
              ┌────┴────┐
             Yes       No
              │         │
           Tier 1    Tier 0
```

### Escalation

Tiers can only be escalated up, never down:
- Tier 0 → Tier 1: Risk Profiler or human approval
- Tier 1 → Tier 2: CISO approval required
- Tier 2 → Tier 1: Not allowed
- Tier 1 → Tier 0: Not allowed

---

## Control Mapping

### Framework Mappings

| Framework | Tier 0 | Tier 1 | Tier 2 |
|-----------|--------|--------|--------|
| SOC 2 | Partial | Full | Full+ |
| GDPR | Basic | Full | Full |
| PCI-DSS | N/A | N/A | Full |
| HIPAA | N/A | N/A | Full |
| ISO 27001 | Partial | Partial | Full |

### Control Matrix

| Control | Tier 0 | Tier 1 | Tier 2 |
|---------|--------|--------|--------|
| Access control | RBAC | RBAC+Audit | RBAC+MFA+JIT |
| Encryption at rest | Optional | Required | HSM |
| Audit logging | Basic | Full | Tamper-evident |
| Vulnerability scan | Weekly | Daily | Continuous |
| Penetration test | None | Annual | Quarterly |
| Incident response | Standard | Enhanced | Dedicated |

---

## Implementation

### OPA Policy Sets

```rego
# policies/opa/compliance/tier_enforcement.rego
package compliance

tier_controls := {
  "baseline": {
    "sast": true,
    "sca": true,
    "coverage_min": 70,
  },
  "sensitive": {
    "sast": true,
    "sca": true,
    "dast": true,
    "coverage_min": 80,
    "security_review": true,
  },
  "regulated": {
    "sast": true,
    "sca": true,
    "dast": true,
    "coverage_min": 90,
    "security_review": true,
    "compliance_review": true,
    "cab_approval": true,
  },
}

deny[msg] {
  tier := input.compliance_tier
  controls := tier_controls[tier]
  controls.security_review
  not input.security_review_approved
  msg := sprintf("Tier %v requires security review", [tier])
}
```

### CI Pipeline Integration

```yaml
# CI workflow selects checks based on tier
jobs:
  compliance-checks:
    steps:
      - name: Load tier config
        run: |
          TIER=$(jq -r '.compliance_tier' manifest.json)
          echo "TIER=$TIER" >> $GITHUB_ENV

      - name: Run tier-specific checks
        run: |
          ./scripts/run-compliance-checks.sh $TIER
```

---

## Templates

- Tier selection: `templates/compliance/COMPLIANCE-TIER.md`
- Evidence Pack: `templates/evidence/EVIDENCE-PACK.md`

---

## Related Documents

- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/05-compliance/audit-ready-operations.md` — Audit support
- `policies/policy-catalog.md` — Policy mappings

---

**Version**: 2.0.0 | **Date**: 2026-01-06
