# Evidence Pack

The Evidence Pack is the deployable unit in Itqahn. No deployment is allowed without a valid, signed Evidence Pack.

---

## What is an Evidence Pack?

An Evidence Pack is a **signed bundle** containing:
- Proof of how an artifact was built (provenance)
- What it contains (SBOM)
- Security verification (scans)
- Quality verification (tests)
- Approval records (attestations)

**Without an Evidence Pack, deployment is blocked at admission.**

---

## Evidence Pack Contents

### Required Artifacts (All Tiers)

| Artifact | Format | Purpose |
|----------|--------|---------|
| `manifest.json` | JSON | Index of all contents |
| `provenance.intoto.jsonl` | in-toto | Build provenance (SLSA) |
| `sbom.cyclonedx.json` | CycloneDX | Software bill of materials |
| `sast-results.sarif` | SARIF | Static analysis results |
| `sca-results.json` | JSON | Dependency scan results |
| `container-scan.json` | JSON | Container image scan |
| `test-results.xml` | JUnit XML | Test execution results |
| `coverage.json` | JSON | Code coverage data |
| `policy-verdict.json` | JSON | OPA policy decision |
| `signatures/` | Directory | Artifact signatures |

### Concept Lock Artifacts (All Builds)

**Required for any artifact built on Itqahn. Proves requirements traceability.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `concept-lock/concept-lock.json` | JSON | Reference to locked requirements |
| `concept-lock/version.json` | JSON | Concept Lock version being implemented |
| `concept-lock/journeys-implemented.json` | JSON | Which journeys this build covers |
| `concept-lock/drift-check.json` | JSON | Drift from locked requirements |
| `concept-lock/change-requests.json` | JSON | Any CRs applied since initial lock |

### Concept Lock Evidence Schema

```json
{
  "concept_lock_evidence": {
    "concept_lock_id": "concept-lock-abc123",
    "concept_lock_version": "1.0.0",
    "project": {
      "name": "Task Manager App",
      "slug": "task-manager-app",
      "tenant_id": "tenant-acme"
    },
    "locked_at": "2026-01-08T12:00:00Z",
    "locked_by": "user@example.com",

    "journeys_implemented": {
      "total_in_scope": 5,
      "implemented_in_build": 2,
      "journey_ids": ["journey-001", "journey-002"],
      "journey_names": [
        "User can sign up and log in",
        "User can browse items"
      ]
    },

    "requirements_traceability": {
      "features_traced": 8,
      "features_untraced": 0,
      "all_traced": true
    },

    "drift_check": {
      "scope_drift": {
        "status": "passed",
        "features_out_of_scope": 0,
        "details": []
      },
      "design_drift": {
        "status": "passed",
        "design_os_version_match": true,
        "locked_version": "v0.1.0",
        "build_version": "v0.1.0"
      },
      "asset_drift": {
        "status": "passed",
        "assets_in_manifest": true,
        "unmanifested_assets": []
      }
    },

    "change_requests": {
      "applied_count": 0,
      "applied_crs": [],
      "pending_count": 0
    },

    "assumptions": {
      "total": 3,
      "resolved": 2,
      "unresolved": 1,
      "unresolved_blocking": false
    },

    "signatures": {
      "concept_lock_digest": "sha256:abc123...",
      "verification": "sigstore://xyz..."
    }
  }
}
```

### Design OS Artifacts (UI Releases)

**Required for any artifact containing UI code.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `design-os-version.json` | JSON | Pinned Design OS version |
| `tokens-digest.json` | JSON | Hash of tokens.json used |
| `components-digest.json` | JSON | Hash of components.json used |
| `visual-regression.html` | HTML | Visual regression report |
| `visual-regression-summary.json` | JSON | Screenshots changed/passed |
| `a11y-report.json` | JSON | Accessibility scan results (axe) |
| `design-drift-score.json` | JSON | Design drift measurement |

### Asset Evidence (Asset Production)

**Required for any artifact containing generated assets (icons, illustrations, photos).**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `assets/asset-manifest.json` | JSON | List of all generated assets with provenance |
| `assets/asset-evidence.json` | JSON | Asset generation evidence (per asset) |
| `assets/lint-report.json` | JSON | Asset lint results (palette, format, dimensions) |
| `assets/drift-scores.json` | JSON | Style anchor drift scores per asset |
| `assets/license-verification.json` | JSON | Model/training data license compliance |
| `assets/registry-records.json` | JSON | Asset Registry registration records |

### Asset Evidence Schema

```json
{
  "asset_evidence": {
    "asset_id": "ast-abc123",
    "workflow_id": "wf-xyz789",
    "design_os_version": "1.2.0",
    "generation": {
      "prompt_hash": "sha256:abc...",
      "model": "sdxl-1.0",
      "provider": "replicate",
      "seed": 42,
      "timestamp": "2026-01-06T12:00:00Z",
      "cost_usd": 0.02
    },
    "style_anchor": {
      "name": "icons/modern-flat",
      "version": "1.0.0",
      "embedding_digest": "sha256:def..."
    },
    "validation": {
      "lint": {
        "status": "passed",
        "palette_compliant": true,
        "format_compliant": true,
        "violations": 0
      },
      "drift": {
        "score": 0.08,
        "threshold": 0.25,
        "status": "passed"
      },
      "accessibility": {
        "contrast_ratio": 5.2,
        "min_required": 4.5,
        "status": "passed"
      }
    },
    "outputs": {
      "source": {
        "path": "assets/outputs/ast-abc123/source.png",
        "digest": "sha256:ghi..."
      },
      "platforms": {
        "ios": {
          "path": "assets/outputs/ast-abc123/ios/",
          "formats": ["appiconset"]
        },
        "android": {
          "path": "assets/outputs/ast-abc123/android/",
          "formats": ["mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi"]
        },
        "web": {
          "path": "assets/outputs/ast-abc123/web/",
          "formats": ["favicon.ico", "apple-touch-icon.png"]
        }
      }
    },
    "registry": {
      "registered": true,
      "namespace": "tenant-acme/app-icons",
      "name": "task-manager-icon",
      "version": "1.0.0",
      "digest": "sha256:jkl..."
    },
    "signatures": {
      "generation": "sigstore://abc...",
      "validation": "sigstore://def..."
    }
  }
}
```

### Git Evidence (Operator Mode)

**Required for all builds in Operator Mode. Proves GitHub traceability.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `git/run-evidence.json` | JSON | Complete Run ID linkage |
| `git/issues.json` | JSON | Epic and work item issues created |
| `git/commits.json` | JSON | All commits with messages and SHAs |
| `git/pr.json` | JSON | PR metadata, checks, merge status |
| `git/merge-queue.json` | JSON | Merge queue entry/exit, queue checks |
| `git/release.json` | JSON | Release tag, changelog, artifacts |

### Git Evidence Schema

```json
{
  "git_evidence": {
    "run_id": "run-01J5ABCD...",
    "repository": {
      "owner": "itqahn-org",
      "name": "task-manager",
      "url": "https://github.com/itqahn-org/task-manager"
    },
    "issues": {
      "epic": {
        "number": 40,
        "url": "https://github.com/itqahn-org/task-manager/issues/40",
        "title": "Task Manager MVP",
        "labels": ["epic", "itqahn-generated"]
      },
      "work_items": [
        {
          "number": 42,
          "url": "https://github.com/itqahn-org/task-manager/issues/42",
          "title": "User Authentication",
          "journey_id": "journey-002",
          "labels": ["work-item", "itqahn-generated"]
        }
      ]
    },
    "branch": {
      "name": "feat/run-01J5ABCD-user-auth",
      "created_at": "2026-01-08T14:00:00Z",
      "base": "main"
    },
    "commits": [
      {
        "sha": "abc123def456...",
        "message": "feat(auth): add login form [run-01J5ABCD #42]",
        "timestamp": "2026-01-08T14:15:00Z",
        "author": "itqahn-bot[bot]"
      }
    ],
    "pull_request": {
      "number": 156,
      "url": "https://github.com/itqahn-org/task-manager/pull/156",
      "title": "feat(auth): user authentication [run-01J5ABCD #42]",
      "state": "merged",
      "labels": ["auto-generated", "run-01J5ABCD"],
      "created_at": "2026-01-08T14:30:00Z",
      "merged_at": "2026-01-08T15:00:00Z",
      "merge_commit_sha": "ghi789jkl012...",
      "checks": {
        "total": 6,
        "passed": 6,
        "failed": 0,
        "results": [
          {"name": "lint", "status": "passed", "duration": 45},
          {"name": "test", "status": "passed", "duration": 180},
          {"name": "security-scan", "status": "passed", "duration": 120},
          {"name": "design-jail", "status": "passed", "duration": 30},
          {"name": "policy-check", "status": "passed", "duration": 15},
          {"name": "evidence-pack", "status": "passed", "duration": 60}
        ]
      },
      "auto_merge": {
        "enabled": true,
        "method": "squash"
      }
    },
    "merge_queue": {
      "entered_at": "2026-01-08T14:45:00Z",
      "position": 2,
      "queue_branch": "gh-readonly-queue/main/pr-156-abc123",
      "queue_check_status": "passed",
      "merged_at": "2026-01-08T15:00:00Z"
    },
    "release": {
      "tag": "v1.2.0",
      "url": "https://github.com/itqahn-org/task-manager/releases/tag/v1.2.0",
      "created_at": "2026-01-08T16:00:00Z",
      "evidence_pack_asset": "evidence-run-01J5ABCD.json"
    },
    "signatures": {
      "commits_signed": true,
      "evidence_signed": "sigstore://xyz..."
    }
  }
}
```

### Additional (Tier 1+)

| Artifact | Format | Purpose |
|----------|--------|---------|
| `dast-results.sarif` | SARIF | Dynamic analysis results |
| `threat-model.json` | JSON | Threat model reference |
| `security-review.json` | JSON | Human review attestation |

### Additional (Tier 2)

| Artifact | Format | Purpose |
|----------|--------|---------|
| `cab-approval.json` | JSON | Change advisory board approval |
| `compliance-attestation.json` | JSON | Compliance officer sign-off |
| `penetration-test.json` | JSON | Pentest results reference |

### Review Checkpoint Trail (Track Assurance)

**Included when Track Assurance generates checkpoints during a run.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `checkpoints/index.json` | JSON | Index of all checkpoints in run |
| `checkpoints/{checkpoint_id}.json` | JSON | Individual checkpoint snapshot |
| `checkpoints/drift-history.json` | JSON | Drift score timeline |
| `checkpoints/decisions.json` | JSON | Operator decisions with justifications |

```json
{
  "checkpoint_trail": {
    "run_id": "run-abc123",
    "total_checkpoints": 3,
    "checkpoints": [
      {
        "checkpoint_id": "ckpt-001",
        "trigger": "automatic",
        "drift_score": 0.18,
        "threshold_status": "passed",
        "created_at": "2026-01-08T14:00:00Z"
      },
      {
        "checkpoint_id": "ckpt-002",
        "trigger": "automatic",
        "drift_score": 0.42,
        "threshold_status": "soft_pause",
        "created_at": "2026-01-08T14:30:00Z",
        "decision": {
          "action": "resume_as_is",
          "decided_by": "operator@acme.com",
          "decided_at": "2026-01-08T14:45:00Z",
          "justification": "Drift acceptable; follow-up ticket created"
        }
      }
    ],
    "final_drift_score": 0.22
  }
}
```

### Legacy Rebuild Evidence

**Required for all Legacy Rebuild workflows.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `rebuild/discovery-report.json` | JSON | Initial discovery analysis |
| `rebuild/strategy-selection.json` | JSON | Strategy choice with rationale |
| `rebuild/component-migrations.json` | JSON | Per-component migration records |
| `rebuild/parity-reports/` | JSON | API, DB, UI, behavior parity tests |
| `rebuild/cutover-log.json` | JSON | Cutover execution record |

```json
{
  "legacy_rebuild_evidence": {
    "rebuild_id": "rebuild-abc123",
    "strategy": "strangler",
    "import": {
      "source": "github.com/acme/legacy-app",
      "legacy_snapshot_sha": "abc123...",
      "imported_at": "2026-01-08T10:30:00Z"
    },
    "migrations": {
      "total_components": 12,
      "completed": 12,
      "components": [
        {
          "name": "utils/date-helpers",
          "pr_number": 123,
          "parity_result": "PASS",
          "migrated_at": "2026-01-08T12:00:00Z"
        }
      ]
    },
    "parity": {
      "overall_score": 0.97,
      "api": 0.99,
      "database": 1.00,
      "ui": 0.88,
      "behavior": 1.00
    },
    "cutover": {
      "executed_at": "2026-01-15T02:00:00Z",
      "duration_minutes": 14,
      "rollback_required": false
    }
  }
}
```

### Improvement Context Evidence

**Included when active improvements affect a run.**

| Artifact | Format | Purpose |
|----------|--------|---------|
| `improvements/active.json` | JSON | Active improvements during run |
| `improvements/history.json` | JSON | Recently deployed improvements |
| `improvements/flags.json` | JSON | Feature flag states |

```json
{
  "improvement_context": {
    "run_id": "run-xyz789",
    "active_improvements": [
      {
        "improvement_id": "imp-2026-0108-001",
        "title": "Auth refresh token handling",
        "flag_status": "enabled",
        "rollout_percentage": 25,
        "enabled_for_run": true
      }
    ],
    "recent_improvements": [
      {
        "improvement_id": "imp-2026-0101-005",
        "deployed_at": "2026-01-05T00:00:00Z",
        "status": "stable",
        "affected_this_run": false
      }
    ],
    "feature_flags": {
      "improvement.auth_refresh_token": true,
      "improvement.typescript_strict": true
    }
  }
}
```

---

## Manifest Schema

```json
{
  "$schema": "https://itqahn.io/schemas/evidence-pack/v1",
  "version": "1.0.0",
  "metadata": {
    "build_id": "build-abc123",
    "artifact_type": "container-image",
    "artifact_digest": "sha256:abc123...",
    "git_commit": "def456...",
    "git_repo": "github.com/org/repo",
    "branch": "main",
    "workflow_id": "wf-xyz789",
    "timestamp": "2026-01-06T12:00:00Z",
    "compliance_tier": "sensitive"
  },
  "artifacts": {
    "provenance": {
      "path": "provenance.intoto.jsonl",
      "digest": "sha256:...",
      "slsa_level": 3
    },
    "sbom": {
      "path": "sbom.cyclonedx.json",
      "digest": "sha256:...",
      "format": "CycloneDX",
      "version": "1.5"
    },
    "security": {
      "sast": {
        "path": "sast-results.sarif",
        "digest": "sha256:...",
        "tool": "semgrep",
        "findings": {
          "critical": 0,
          "high": 0,
          "medium": 2,
          "low": 5
        }
      },
      "sca": {
        "path": "sca-results.json",
        "digest": "sha256:...",
        "tool": "snyk",
        "findings": {
          "critical": 0,
          "high": 0,
          "medium": 3,
          "low": 12
        }
      },
      "container": {
        "path": "container-scan.json",
        "digest": "sha256:...",
        "tool": "trivy"
      }
    },
    "testing": {
      "results": {
        "path": "test-results.xml",
        "digest": "sha256:...",
        "passed": 245,
        "failed": 0,
        "skipped": 3
      },
      "coverage": {
        "path": "coverage.json",
        "digest": "sha256:...",
        "line_coverage": 85.2,
        "branch_coverage": 78.5
      }
    },
    "policy": {
      "path": "policy-verdict.json",
      "digest": "sha256:...",
      "decision": "allow",
      "policies_evaluated": 15
    },
    "approvals": [
      {
        "type": "security_review",
        "approver": "security-reviewer-agent",
        "timestamp": "2026-01-06T11:55:00Z",
        "attestation": "attestations/security-review.sig"
      }
    ],
    "concept_lock": {
      "id": "concept-lock-abc123",
      "version": "1.0.0",
      "project_slug": "task-manager-app",
      "digest": "sha256:abc123...",
      "journeys_implemented": ["journey-001", "journey-002"],
      "drift_check_status": "passed",
      "change_requests_applied": 0,
      "assumptions_unresolved": 1
    },
    "design_os": {
      "version": "1.2.0",
      "tokens": {
        "path": "design-os/tokens.json",
        "digest": "sha256:abc123..."
      },
      "components": {
        "path": "design-os/components.json",
        "digest": "sha256:def456..."
      },
      "visual_regression": {
        "path": "visual-regression-summary.json",
        "digest": "sha256:ghi789...",
        "status": "passed",
        "screenshots_changed": 0,
        "screenshots_total": 45,
        "report": "visual-regression.html"
      },
      "accessibility": {
        "path": "a11y-report.json",
        "digest": "sha256:jkl012...",
        "status": "passed",
        "violations": 0,
        "warnings": 3,
        "standard": "WCAG 2.1 AA"
      },
      "drift_score": {
        "path": "design-drift-score.json",
        "score": 0.05,
        "threshold": 0.25,
        "status": "passed"
      }
    },
    "assets": {
      "count": 3,
      "manifest": {
        "path": "assets/asset-manifest.json",
        "digest": "sha256:mno345..."
      },
      "evidence": {
        "path": "assets/asset-evidence.json",
        "digest": "sha256:pqr678..."
      },
      "lint": {
        "path": "assets/lint-report.json",
        "digest": "sha256:stu901...",
        "status": "passed",
        "violations": 0
      },
      "drift": {
        "path": "assets/drift-scores.json",
        "digest": "sha256:vwx234...",
        "max_score": 0.12,
        "threshold": 0.25,
        "status": "passed"
      },
      "license": {
        "path": "assets/license-verification.json",
        "digest": "sha256:yza567...",
        "status": "passed",
        "commercial_ok": true
      },
      "registry": {
        "path": "assets/registry-records.json",
        "digest": "sha256:bcd890...",
        "all_registered": true
      }
    }
  },
  "signatures": {
    "manifest_signature": "signatures/manifest.sig",
    "signing_key": "cosign-pub-key",
    "transparency_log": "rekor.sigstore.dev/entry/123"
  }
}
```

---

## Evidence Pack Lifecycle

```
┌──────────────┐
│    Build     │
│   Complete   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Generate   │
│   Artifacts  │
│              │
│ • SBOM       │
│ • Provenance │
│ • Scans      │
│ • Tests      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Evaluate   │
│    Policy    │
│              │
│ • OPA gates  │
│ • Thresholds │
│ • Approvals  │
└──────┬───────┘
       │
       ├── Fail ──▶ Block deployment
       │
       ▼ Pass
┌──────────────┐
│   Assemble   │
│     Pack     │
│              │
│ • Manifest   │
│ • Checksums  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     Sign     │
│     Pack     │
│              │
│ • Sigstore   │
│ • Rekor log  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Store     │
│              │
│ • Immutable  │
│ • Versioned  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Verify     │
│  at Deploy   │
│              │
│ • Signature  │
│ • Policy     │
└──────┬───────┘
       │
       ├── Fail ──▶ Admission rejected
       │
       ▼ Pass
┌──────────────┐
│   Deploy     │
│   Allowed    │
└──────────────┘
```

---

## Validation

### Schema Validation

```python
# tools/validators/evidence_pack_validator.py
def validate_manifest(manifest: dict) -> ValidationResult:
    # Required fields
    required = ["version", "metadata", "artifacts", "signatures"]
    for field in required:
        if field not in manifest:
            return ValidationResult(valid=False, error=f"Missing {field}")

    # Artifact checksums
    for name, artifact in manifest["artifacts"].items():
        if "digest" in artifact:
            actual = compute_digest(artifact["path"])
            if actual != artifact["digest"]:
                return ValidationResult(
                    valid=False,
                    error=f"Digest mismatch for {name}"
                )

    return ValidationResult(valid=True)
```

### Signature Verification

```bash
# Verify manifest signature
cosign verify-blob \
  --key cosign.pub \
  --signature signatures/manifest.sig \
  manifest.json

# Verify via Rekor transparency log
rekor-cli verify \
  --artifact manifest.json \
  --signature signatures/manifest.sig
```

---

## Storage Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Immutable** | Write-once storage, no modifications |
| **Versioned** | Unique path per build |
| **Linked** | Reference from deployment record |
| **Accessible** | Available for audits |
| **Retained** | Per compliance tier policy |

### Storage Path

```
evidence/
├── {service}/
│   └── {version}/
│       └── {build-id}/
│           ├── manifest.json
│           ├── provenance.intoto.jsonl
│           ├── sbom.cyclonedx.json
│           ├── ...
│           └── signatures/
```

### Retention

| Tier | Retention |
|------|-----------|
| Baseline | 1 year |
| Sensitive | 3 years |
| Regulated | 7 years |

---

## Admission Control

Kubernetes admission webhook verifies Evidence Pack:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: evidence-pack-validator
webhooks:
  - name: evidence.itqahn.io
    rules:
      - operations: ["CREATE", "UPDATE"]
        resources: ["deployments", "statefulsets"]
    clientConfig:
      service:
        name: evidence-validator
        namespace: itqahn-system
        path: /validate
```

### Validation Steps

1. Extract image digest from deployment
2. Look up Evidence Pack by digest
3. Verify manifest signature
4. Verify policy verdict is "allow"
5. Verify no critical/high findings (per tier)
6. Allow or reject deployment

---

## Templates

- Evidence Pack structure: `templates/evidence/EVIDENCE-PACK.md`
- Manifest schema: `templates/evidence/evidence-pack-manifest.schema.json`

---

## Related Documents

- `docs/00-overview/principles.md` — Evidence is the Product principle
- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 and Concept Lock
- `docs/01-product/requirements-schema.md` — Phase 1 output schemas
- `docs/03-platform/ci-cd-gitops.md` — CI/CD integration
- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/03-platform/track-assurance.md` — Track Assurance and checkpoint evidence
- `docs/03-platform/legacy-rebuild.md` — Legacy Rebuild and rebuild evidence
- `docs/05-compliance/slsa-provenance.md` — Build provenance
- `docs/05-compliance/sbom-vex.md` — Software bill of materials
- `docs/06-operations/itqahn-continuous-improvement.md` — Self-improvement and improvement evidence
- `docs/07-integrations/git-integration.md` — GitHub Automation Program and Git Evidence
- `docs/07-integrations/webhooks-events.md` — GitHub and CI events
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/08-agents/agent-permissions.md` — Bot permissions for GitHub

---

**Version**: 2.4.0 | **Date**: 2026-01-08
