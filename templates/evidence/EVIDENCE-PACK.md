# Evidence Pack Specification

The Evidence Pack is the deployable unit in Itqahn. No deployment can proceed without a complete, signed Evidence Pack.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      EVIDENCE PACK                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     MANIFEST                             │    │
│  │  pack_id, git_commit, build_id, compliance_tier         │    │
│  │  created_at, signature_hash                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    SBOM     │  │ PROVENANCE  │  │   SCANS     │             │
│  │  (CycloneDX)│  │  (in-toto)  │  │ (SAST/SCA)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   TESTS     │  │  APPROVALS  │  │  SIGNATURE  │             │
│  │  (Reports)  │  │  (Records)  │  │  (Cosign)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Manifest

The manifest is the index of all evidence items.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `pack_id` | string | Unique identifier for this pack |
| `git_commit` | string | Full git commit SHA |
| `build_id` | string | CI/CD build identifier |
| `created_at` | datetime | ISO 8601 timestamp |
| `compliance_tier` | enum | baseline, sensitive, regulated |
| `artifacts` | object | References to all evidence artifacts |
| `signature_hash` | string | SHA256 of signed manifest |

### Manifest Example

```json
{
  "pack_id": "ep-user-service-v1.2.3-abc123",
  "service": "user-service",
  "version": "1.2.3",
  "git_commit": "abc123def456789...",
  "build_id": "build-12345",
  "created_at": "2026-01-06T12:00:00Z",
  "compliance_tier": "sensitive",
  "workflow_id": "wf-xyz789",
  "artifacts": {
    "sbom": {
      "present": true,
      "path": "sbom.json",
      "format": "CycloneDX",
      "version": "1.5"
    },
    "provenance": {
      "present": true,
      "path": "provenance.json",
      "format": "in-toto",
      "signed": true
    },
    "scans": [
      {
        "type": "sast",
        "tool": "semgrep",
        "path": "scans/sast-results.json"
      },
      {
        "type": "sca",
        "tool": "trivy",
        "path": "scans/sca-results.json"
      },
      {
        "type": "secrets",
        "tool": "gitleaks",
        "path": "scans/secret-scan.json"
      }
    ],
    "tests": [
      {
        "type": "unit",
        "path": "tests/unit-results.xml"
      },
      {
        "type": "integration",
        "path": "tests/integration-results.xml"
      }
    ],
    "approvals": [
      {
        "type": "code_review",
        "path": "approvals/code-review.json"
      },
      {
        "type": "security_review",
        "path": "approvals/security-review.json"
      }
    ]
  },
  "signature_hash": "sha256:abc123..."
}
```

---

## Artifacts

### SBOM (Required)

Software Bill of Materials in CycloneDX format.

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:...",
  "version": 1,
  "metadata": {...},
  "components": [...]
}
```

### Provenance (Required)

Build provenance in in-toto format.

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [...],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {...},
    "runDetails": {...}
  }
}
```

### Scans (Required)

Security scan results:

| Scan Type | Tool | Format |
|-----------|------|--------|
| SAST | Semgrep | SARIF |
| SCA | Trivy | JSON |
| Secrets | Gitleaks | JSON |
| Container | Trivy | JSON |
| DAST | ZAP | JSON (conditional) |

### Tests (Required)

Test execution results:

| Test Type | Format |
|-----------|--------|
| Unit | JUnit XML |
| Integration | JUnit XML |
| E2E | JUnit XML |
| Coverage | JSON |

### Approvals (Conditional)

Approval records for sensitive/regulated tiers:

```json
{
  "type": "security_review",
  "approver": "security-gate",
  "approved_at": "2026-01-06T12:00:00Z",
  "workflow_id": "wf-xyz789",
  "decision": "approved",
  "conditions": []
}
```

---

## Signing

Evidence packs must be signed and verified before deployment.

### Signing Process

```
1. Generate manifest JSON
       │
       ▼
2. Compute SHA256 of manifest
       │
       ▼
3. Sign with Cosign (keyless via OIDC)
       │
       ▼
4. Store signature alongside pack
```

### Verification

```bash
# Verify evidence pack signature
cosign verify-blob \
  --signature evidence-pack.sig \
  --certificate evidence-pack.crt \
  evidence-pack-manifest.json
```

---

## Storage

Evidence must be immutable and retained per retention policy.

### Storage Location

```
s3://evidence/{service}/{version}/{build_id}/
├── manifest.json
├── manifest.sig
├── sbom.json
├── provenance.json
├── scans/
│   ├── sast-results.json
│   ├── sca-results.json
│   └── secret-scan.json
├── tests/
│   ├── unit-results.xml
│   └── integration-results.xml
└── approvals/
    └── code-review.json
```

### Retention

| Tier | Retention | Immutable |
|------|-----------|-----------|
| Baseline | 1 year | Yes |
| Sensitive | 2 years | Yes |
| Regulated | 7 years | Yes |

---

## Validation

Before deployment, the Evidence Pack is validated:

```yaml
validation_checks:
  - manifest_schema_valid
  - sbom_present
  - provenance_present
  - provenance_signed
  - scans_present
  - scan_thresholds_met
  - tests_present
  - tests_passed
  - approvals_present (conditional)
  - signature_valid
```

---

## Related Documents

- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/05-compliance/slsa-provenance.md` — Provenance details
- `policies/compliance/evidence-requirements.yaml` — Tier requirements

---

**Version**: 2.0.0 | **Date**: 2026-01-06
