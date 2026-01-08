# Audit-Ready Operations

Itqahn maintains continuous audit readiness. All changes, approvals, and decisions are recorded with complete traceability.

---

## Audit Trail Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUDIT TRAIL                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Change Records │  │   Approvals     │  │   Evidence      │  │
│  │                 │  │                 │  │                 │  │
│  │ • Git commits   │  │ • Human sign-off│  │ • Evidence Packs│  │
│  │ • PR merges     │  │ • Agent verdicts│  │ • Scan reports  │  │
│  │ • Deployments   │  │ • Policy gates  │  │ • Test results  │  │
│  │ • Config changes│  │ • Exceptions    │  │ • Provenance    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   ACCESS LOGS                             │   │
│  │  • Authentication events • Secret access • Data access    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Change Records

### Git as Change Log

Every change is recorded in Git with:

| Field | Source | Purpose |
|-------|--------|---------|
| Who | Commit author, PR creator | Attribution |
| What | Diff, PR description | Change content |
| When | Commit timestamp | Timeline |
| Why | PR description, ticket link | Justification |
| How | Review comments, approvals | Process verification |

### Change Record Format

```json
{
  "change_id": "chg-abc123",
  "type": "code_change",
  "timestamp": "2026-01-06T12:00:00Z",
  "git": {
    "repository": "github.com/org/user-service",
    "commit": "def456...",
    "branch": "main",
    "pr_number": 123,
    "merge_commit": "ghi789..."
  },
  "actor": {
    "type": "agent",
    "id": "backend-builder",
    "workflow_id": "wf-xyz789"
  },
  "approvals": [
    {
      "type": "code_review",
      "approver": "jane@example.com",
      "timestamp": "2026-01-06T11:55:00Z"
    },
    {
      "type": "security_review",
      "approver": "appsec-reviewer",
      "timestamp": "2026-01-06T11:58:00Z"
    }
  ],
  "references": {
    "ticket": "JIRA-123",
    "prd": "requirements/feature-x.md",
    "evidence_pack": "evidence/user-service/1.2.3/build-abc123"
  }
}
```

---

## Approval Records

### Human Approvals

```json
{
  "approval_id": "apr-def456",
  "type": "human_approval",
  "gate": "production_deploy",
  "decision": "approved",
  "approver": {
    "email": "jane@example.com",
    "role": "engineering_lead"
  },
  "timestamp": "2026-01-06T13:00:00Z",
  "context": {
    "workflow_id": "wf-xyz789",
    "change_id": "chg-abc123",
    "justification": "Reviewed and approved for production deployment"
  },
  "signature": "base64-encoded-signature"
}
```

### Policy Verdicts

```json
{
  "verdict_id": "vrd-ghi789",
  "type": "policy_verdict",
  "policy_set": "production_deploy",
  "decision": "allow",
  "timestamp": "2026-01-06T12:30:00Z",
  "policies_evaluated": [
    {
      "policy": "security/sast_clean",
      "result": "pass"
    },
    {
      "policy": "security/sca_thresholds",
      "result": "pass"
    },
    {
      "policy": "compliance/evidence_required",
      "result": "pass"
    }
  ],
  "inputs": {
    "evidence_pack": "evidence/user-service/1.2.3/build-abc123",
    "compliance_tier": "sensitive"
  }
}
```

### Exception Records

```json
{
  "exception_id": "exc-jkl012",
  "type": "policy_exception",
  "policy": "security/sast_clean",
  "reason": "False positive in third-party code",
  "approver": {
    "email": "ciso@example.com",
    "role": "CISO"
  },
  "expires": "2026-02-06T00:00:00Z",
  "scope": {
    "service": "user-service",
    "finding_id": "SAST-12345"
  },
  "compensating_controls": [
    "Manual code review completed",
    "Runtime monitoring increased"
  ],
  "timestamp": "2026-01-06T10:00:00Z"
}
```

---

## Access Logs

### Authentication Events

```json
{
  "event_type": "authentication",
  "timestamp": "2026-01-06T09:00:00Z",
  "actor": {
    "user_id": "user-abc123",
    "email": "jane@example.com",
    "ip_address": "192.0.2.1"
  },
  "action": "login",
  "result": "success",
  "method": "oidc",
  "mfa_used": true,
  "session_id": "sess-xyz789"
}
```

### Secret Access

```json
{
  "event_type": "secret_access",
  "timestamp": "2026-01-06T12:05:00Z",
  "actor": {
    "type": "workload",
    "spiffe_id": "spiffe://itqahn.io/ns/production/sa/user-service"
  },
  "action": "read",
  "resource": "database/creds/user-service-readonly",
  "result": "success",
  "lease_id": "database/creds/user-service-readonly/abc123",
  "lease_ttl": 300,
  "workflow_id": "wf-xyz789"
}
```

### Data Access

```json
{
  "event_type": "data_access",
  "timestamp": "2026-01-06T12:10:00Z",
  "actor": {
    "user_id": "user-abc123",
    "service": "user-service"
  },
  "action": "read",
  "resource": {
    "type": "customer_data",
    "table": "users",
    "record_count": 50
  },
  "purpose": "support_request",
  "ticket": "SUPPORT-456",
  "tenant_id": "tenant-def456"
}
```

---

## Retention Policies

| Log Type | Baseline | Sensitive | Regulated |
|----------|----------|-----------|-----------|
| Change records | 1 year | 3 years | 7 years |
| Approval records | 1 year | 3 years | 7 years |
| Access logs | 90 days | 1 year | 7 years |
| Evidence Packs | 1 year | 3 years | 7 years |
| Security events | 1 year | 3 years | 7 years |

### Tamper-Evidence

For regulated tier:
- Logs written to append-only storage
- Cryptographic chaining (hash of previous entry)
- Periodic integrity verification
- External audit storage copy

---

## Audit Queries

### Common Audit Questions

| Question | Query |
|----------|-------|
| Who deployed X? | `change_records WHERE type=deploy AND service=X` |
| What changed in release Y? | `change_records WHERE evidence_pack LIKE %/Y/%` |
| Who approved production deploy? | `approvals WHERE gate=production_deploy AND change_id=X` |
| Was security review done? | `approvals WHERE type=security_review AND change_id=X` |
| Who accessed secret Z? | `access_logs WHERE resource=Z` |

### Audit API

```python
# Query audit records
results = audit_api.query(
    record_type="change_records",
    filters={
        "service": "user-service",
        "date_range": ("2026-01-01", "2026-01-06")
    },
    include=["approvals", "evidence_pack"]
)
```

---

## Audit Reports

### Periodic Reports

| Report | Frequency | Audience |
|--------|-----------|----------|
| Change summary | Weekly | Engineering |
| Access review | Monthly | Security |
| Exception summary | Monthly | Compliance |
| Full audit trail | Quarterly | External auditors |

### Report Format

```markdown
# Change Audit Report - January 2026

## Summary
- Total changes: 234
- Production deployments: 45
- Security reviews: 45 (100%)
- Exceptions granted: 2

## Changes by Service
| Service | Changes | Deploys | Incidents |
|---------|---------|---------|-----------|
| user-service | 45 | 8 | 0 |
| auth-service | 23 | 4 | 0 |
...

## Exceptions
| ID | Policy | Approver | Expires |
|----|--------|----------|---------|
| exc-jkl012 | sast_clean | CISO | 2026-02-06 |
...

## Access Anomalies
None detected
```

---

## Compliance Frameworks

### SOC 2 Mapping

| SOC 2 Control | Itqahn Implementation |
|---------------|----------------------|
| CC6.1 - Logical access | Access logs, RBAC |
| CC6.2 - Authentication | Auth events, MFA |
| CC6.3 - Authorization | Policy verdicts |
| CC7.1 - System monitoring | Audit trail |
| CC8.1 - Change management | Change records |

### GDPR Mapping

| GDPR Article | Itqahn Implementation |
|--------------|----------------------|
| Art. 30 - Records of processing | Data access logs |
| Art. 32 - Security of processing | Security controls, audit |
| Art. 33 - Breach notification | Incident records |

---

## Related Documents

- `docs/05-compliance/compliance-tiers.md` — Tier requirements
- `docs/05-compliance/evidence-pack.md` — Evidence documentation
- `docs/06-operations/incident-response.md` — Incident records

---

**Version**: 2.0.0 | **Date**: 2026-01-06
