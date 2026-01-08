# Data Classification

All data in Itqahn must be classified at design time. Classification determines controls, retention, and handling requirements.

---

## Classification Levels

| Level | Definition | Examples |
|-------|------------|----------|
| **Public** | Intentionally public, no harm if disclosed | Marketing content, public docs, open-source code |
| **Internal** | Internal use, minor harm if disclosed | Internal docs, non-sensitive configs, aggregated metrics |
| **Confidential** | Business-sensitive, significant harm if disclosed | Customer data, PII, API keys, financial data |
| **Regulated** | Subject to regulatory requirements | Payment card data (PCI), health data (HIPAA), financial records |

---

## Classification Decision Tree

```
                    Is disclosure harmful?
                           │
              ┌────────────┴────────────┐
              │                         │
             No                        Yes
              │                         │
              ▼                         ▼
           PUBLIC              Is it subject to regulation?
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                         Yes                       No
                          │                         │
                          ▼                         ▼
                      REGULATED            Is it business-sensitive?
                                                   │
                                      ┌────────────┴────────────┐
                                      │                         │
                                     Yes                       No
                                      │                         │
                                      ▼                         ▼
                                CONFIDENTIAL              INTERNAL
```

---

## Controls by Classification

### Public

| Control | Requirement |
|---------|-------------|
| Encryption at rest | Optional |
| Encryption in transit | Required (TLS) |
| Access control | None required |
| Logging | Basic (access counts) |
| Retention | Per business need |
| Backup | Optional |

### Internal

| Control | Requirement |
|---------|-------------|
| Encryption at rest | Recommended |
| Encryption in transit | Required (TLS) |
| Access control | Authentication required |
| Logging | Standard (who accessed) |
| Retention | 1 year default |
| Backup | Required |

### Confidential

| Control | Requirement |
|---------|-------------|
| Encryption at rest | Required (AES-256) |
| Encryption in transit | Required (mTLS) |
| Access control | Role-based, least privilege |
| Logging | Full audit (who, what, when) |
| Retention | Per data type policy |
| Backup | Required, encrypted |
| Masking | Required in non-prod |
| DLP | Recommended |

### Regulated

| Control | Requirement |
|---------|-------------|
| Encryption at rest | Required (AES-256, HSM keys) |
| Encryption in transit | Required (mTLS, TLS 1.3) |
| Access control | MFA, just-in-time access |
| Logging | Full audit, tamper-evident |
| Retention | Per regulation (often 7 years) |
| Backup | Required, encrypted, tested |
| Masking | Required always outside prod |
| DLP | Required |
| Data residency | Per regulation |
| Key management | HSM, customer-managed keys option |

---

## PII Handling

### Identifying PII

| Category | Fields |
|----------|--------|
| **Direct identifiers** | Name, email, phone, SSN, passport |
| **Indirect identifiers** | IP address, device ID, location |
| **Sensitive PII** | Race, religion, health, biometrics |

### PII Controls

| Control | Implementation |
|---------|----------------|
| **Minimization** | Collect only what's needed |
| **Purpose limitation** | Use only for stated purpose |
| **Storage limitation** | Delete when no longer needed |
| **Pseudonymization** | Replace identifiers with tokens |
| **Encryption** | Field-level encryption for sensitive |
| **Access logging** | Log all PII access |

### PII in AI Systems

| Rule | Implementation |
|------|----------------|
| No PII in prompts | Scrub before sending to LLM |
| No PII in embeddings | Hash or tokenize before embedding |
| No PII in logs | Automatic redaction |
| PII retrieval | Only with explicit consent/purpose |

---

## Multi-Tenant Data Rules

### Server-Side Tenant Resolution

Never trust client-provided tenant ID for data access:

```python
# WRONG - client can spoof
tenant_id = request.headers.get("X-Tenant-ID")

# RIGHT - derive from authenticated identity
tenant_id = identity.get_tenant_from_token(request.auth_token)
```

### Row-Level Security

```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON customers
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### Cryptographic Tenant Context

```python
# Tenant context token (signed, short-lived)
tenant_token = jwt.encode({
    "tenant_id": tenant_id,
    "permissions": ["read", "write"],
    "exp": now + timedelta(minutes=15)
}, key=tenant_signing_key)
```

### Tenant-Specific Encryption Keys

For enterprise tier:

```hcl
# Vault path structure
secret/data/tenants/{tenant_id}/encryption-key
secret/data/tenants/{tenant_id}/signing-key
```

---

## Retention Policies

### Default Retention Periods

| Data Type | Retention | Justification |
|-----------|-----------|---------------|
| Audit logs | 7 years | Compliance requirement |
| Application logs | 90 days | Operational need |
| User data | Account lifetime + 30 days | Service requirement |
| Analytics | 2 years | Business analysis |
| Backups | 30 days | Disaster recovery |
| PII (no consent) | Minimum necessary | GDPR/CCPA |

### Retention Enforcement

```yaml
# Retention policy definition
retention_policies:
  - name: audit-logs
    classification: confidential
    retention_days: 2555  # 7 years
    deletion_method: secure-delete

  - name: user-content
    classification: confidential
    retention_days: account_lifetime + 30
    deletion_method: cascading-delete

  - name: analytics
    classification: internal
    retention_days: 730
    deletion_method: batch-delete
```

### Automated Enforcement

```python
# Daily retention job
async def enforce_retention():
    for policy in retention_policies:
        expired_records = await db.find(
            table=policy.table,
            where=f"created_at < now() - interval '{policy.retention_days} days'"
        )

        for record in expired_records:
            await secure_delete(record, policy.deletion_method)
            await audit_log("retention_delete", record.id)
```

---

## Data Subject Rights (DSR/DSAR)

### Supported Rights

| Right | Implementation |
|-------|----------------|
| **Access** | Export all data for subject |
| **Rectification** | Update incorrect data |
| **Erasure** | Delete all subject data |
| **Portability** | Export in machine-readable format |
| **Restriction** | Limit processing |
| **Objection** | Stop specific processing |

### DSR Workflow

```
1. Request received (verified identity)
       │
       ▼
2. Request logged in DSR system
       │
       ▼
3. Data located across all systems
       │
       ▼
4. Action performed (export/delete/update)
       │
       ▼
5. Verification of completion
       │
       ▼
6. Response to subject (within 30 days)
       │
       ▼
7. Audit record created
```

---

## Classification in PRDs

All PRDs must include data classification:

```yaml
data:
  classification: Confidential
  pii_fields:
    - user.email
    - user.name
    - user.phone
  retention_policy: templates/compliance/RETENTION-POLICY.md
  tenant_model: Multi-namespace
  data_residency:
    - US
    - EU
```

---

## Templates

- Data classification: `templates/compliance/DATA-CLASSIFICATION.md`
- Retention policy: `templates/compliance/RETENTION-POLICY.md`

---

## Related Documents

- `docs/05-compliance/compliance-tiers.md` — Tier-specific requirements
- `docs/04-security/security-model.md` — Security controls
- `docs/02-architecture/tenancy-isolation.md` — Multi-tenant architecture

---

**Version**: 2.0.0 | **Date**: 2026-01-06
