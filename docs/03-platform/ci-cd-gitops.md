# CI/CD and GitOps

This document defines the continuous integration, continuous delivery, and GitOps practices for Itqahn.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CI/CD PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │ Source  │─▶│  Build  │─▶│  Test   │─▶│  Scan   │─▶│Package│ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └───┬───┘ │
│                                                          │      │
│                                                          ▼      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │Post-Live│◀─│ Promote │◀─│ Canary  │◀─│ Deploy  │◀─│Evidence│ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └───────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Continuous Integration

### Pipeline Stages

| Stage | Actions | Blocks On |
|-------|---------|-----------|
| **Source** | Checkout, validate PR format | Invalid PR template |
| **Build** | Compile, bundle, hermetic build | Build failure |
| **Test** | Unit, integration, contract | Test failure, coverage drop |
| **Scan** | SAST, SCA, secrets, containers | Critical/High findings |
| **Package** | Create artifacts, SBOM, sign | Signing failure |
| **Evidence** | Generate Evidence Pack | Missing artifacts |

### Required Checks

```yaml
# GitHub Actions workflow
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint
      - run: npm run format:check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --coverage
      - name: Check coverage
        run: |
          coverage=$(jq '.total.lines.pct' coverage/coverage-summary.json)
          if (( $(echo "$coverage < 80" | bc -l) )); then
            exit 1
          fi

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SAST
        run: semgrep --config auto --error
      - name: Secret scan
        run: gitleaks detect --source . --verbose
      - name: Dependency scan
        run: npm audit --audit-level=high

  policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: OPA evaluation
        run: opa eval --bundle policies/ --input context.json
```

### Build Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Hermetic** | No network access during build |
| **Reproducible** | Same inputs → same outputs |
| **Isolated** | Ephemeral build environment |
| **Signed** | Artifacts signed with Sigstore |

---

## Evidence Pack Generation

Every build produces an Evidence Pack:

```yaml
# evidence-pack-manifest.json
{
  "version": "1.0.0",
  "build_id": "build-abc123",
  "timestamp": "2026-01-06T12:00:00Z",
  "artifacts": {
    "provenance": "provenance.intoto.jsonl",
    "sbom": "sbom.cyclonedx.json",
    "sast_report": "sast-results.sarif",
    "sca_report": "sca-results.json",
    "test_results": "test-results.xml",
    "coverage": "coverage.json"
  },
  "signatures": {
    "manifest": "sha256:...",
    "cosign_bundle": "bundle.sig"
  },
  "attestations": [
    {
      "type": "https://slsa.dev/provenance/v1",
      "subject": "sha256:..."
    }
  ]
}
```

---

## GitOps Deployment

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git (Infra)   │───▶│    ArgoCD       │───▶│   Kubernetes    │
│                 │    │                 │    │                 │
│ • Manifests     │    │ • Sync          │    │ • Namespaces    │
│ • Kustomize     │    │ • Diff          │    │ • Deployments   │
│ • Helm values   │    │ • Rollback      │    │ • Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Git as Truth

- **Desired state** lives in Git (infra repo)
- **ArgoCD** reconciles actual to desired
- **Changes** only through PR merges
- **Rollback** = Git revert

### Environment Promotion

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│   dev    │───▶│ staging  │───▶│   prod   │
│          │    │          │    │          │
│ auto-    │    │ auto +   │    │ manual   │
│ deploy   │    │ smoke    │    │ approval │
└──────────┘    └──────────┘    └──────────┘
```

| Environment | Trigger | Gates |
|-------------|---------|-------|
| **dev** | PR merge to main | All CI checks pass |
| **staging** | Dev success | Smoke tests pass |
| **prod** | Manual approval | Evidence verified, approvals |

### ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: user-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/itqahn/infra
    targetRevision: HEAD
    path: apps/user-service/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: user-service
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## Canary Deployments

### Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                      TRAFFIC SPLIT                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 5% canary                                            │
│  ┌─────────────────────────────────────┐  ┌────────┐          │
│  │            Stable (95%)             │  │Canary  │          │
│  └─────────────────────────────────────┘  │ (5%)   │          │
│                                           └────────┘          │
│  Phase 2: 25% canary (if SLO ok)                               │
│  ┌───────────────────────────┐  ┌──────────────────┐          │
│  │       Stable (75%)        │  │   Canary (25%)   │          │
│  └───────────────────────────┘  └──────────────────┘          │
│                                                                 │
│  Phase 3: 100% (promote)                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                     New Version (100%)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Canary Analysis

```yaml
# Argo Rollouts AnalysisTemplate
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result >= 0.99
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status=~"2.."}[5m])) /
            sum(rate(http_requests_total[5m]))

    - name: latency-p99
      interval: 1m
      successCondition: result <= 500
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket[5m]))
              by (le)
            ) * 1000
```

### Rollback Triggers

| Trigger | Action |
|---------|--------|
| SLO violation | Automatic rollback |
| Error rate spike | Automatic rollback |
| Manual | ArgoCD rollback or Git revert |
| Security alert | Immediate rollback |

---

## Admission Control

Kubernetes admission webhooks verify:

| Check | Enforcement |
|-------|-------------|
| **Signed images** | Reject unsigned containers |
| **Evidence Pack** | Verify attestations |
| **Policy compliance** | Kyverno policies |
| **Resource limits** | Required for all pods |
| **Network policies** | Required per namespace |

```yaml
# Kyverno policy for signed images
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        resources:
          kinds:
            - Pod
      verifyImages:
        - image: "registry.example.com/*"
          key: |-
            -----BEGIN PUBLIC KEY-----
            ...
            -----END PUBLIC KEY-----
```

---

## Release Tagging

### Tag Format

```
release/<service>/<semver>

Examples:
- release/user-service/1.2.3
- release/api-gateway/2.0.0-rc.1
```

### Release Process

1. **PR merged** to main
2. **CI passes** all checks
3. **Evidence Pack** generated
4. **Tag created** with attestation link
5. **ArgoCD syncs** to target environment
6. **Canary analysis** runs
7. **Promote or rollback**

---

## Audit Trail

Every deployment records:

```json
{
  "deployment_id": "deploy-xyz789",
  "service": "user-service",
  "version": "1.2.3",
  "environment": "prod",
  "timestamp": "2026-01-06T14:00:00Z",
  "triggered_by": {
    "type": "workflow",
    "id": "wf-abc123",
    "agent": "release-manager"
  },
  "evidence_pack": "s3://evidence/user-service/1.2.3/manifest.json",
  "approvals": [
    {
      "gate": "production-deploy",
      "approver": "jane@example.com",
      "timestamp": "2026-01-06T13:55:00Z"
    }
  ],
  "canary_analysis": {
    "phases": 3,
    "duration_minutes": 30,
    "result": "success"
  }
}
```

---

## Validation Gates as CI Contract

The Context Engineering Program defines **Validation Gates** that CI MUST enforce. These gates form the contract between local validation (Operator Mode) and authoritative CI validation.

### Gate Categories

| Category | CI Check | Blocking | Evidence Artifact |
|----------|----------|----------|-------------------|
| **Format/Schema** | `npm run lint:schema` | Yes | `evidence/schema-validation.json` |
| **Code Quality** | `npm run lint && npm run typecheck` | Yes | `evidence/lint-report.json` |
| **Unit Tests** | `npm test` | Yes | `evidence/test-results.xml` |
| **Integration Tests** | `npm run test:integration` | Yes | `evidence/integration-results.xml` |
| **Security Scan** | `semgrep + gitleaks + npm audit` | Yes | `evidence/security-scan.sarif` |
| **Drift Detection** | `drift-checker` | Threshold | `evidence/drift-report.json` |
| **Docs Sync** | `docs-validator` | Configurable | `evidence/docs-check.json` |

### The Unified Validate Command

Both local (Operator Mode) and CI run the same validation:

```yaml
# scripts/validate.sh
#!/bin/bash
set -e

echo "=== VALIDATION GATES ==="

# Gate 1: Format/Schema
echo "Running schema validation..."
npm run lint:schema

# Gate 2: Code Quality
echo "Running lint..."
npm run lint
echo "Running typecheck..."
npm run typecheck

# Gate 3: Unit Tests
echo "Running unit tests..."
npm test -- --coverage

# Gate 4: Integration Tests
echo "Running integration tests..."
npm run test:integration

# Gate 5: Security Scan
echo "Running security scan..."
semgrep --config auto --error --json > evidence/sast.json
gitleaks detect --source . --verbose
npm audit --audit-level=high

# Gate 6: Drift Detection
echo "Running drift check..."
drift-checker --threshold 0.30

# Gate 7: Docs Sync (optional)
echo "Checking docs sync..."
docs-validator --warn

echo "=== ALL GATES PASSED ==="
```

### Local vs CI Validation

| Aspect | Local (Operator Mode) | CI (Authoritative) |
|--------|----------------------|-------------------|
| **Runner** | Claude Code session | GitHub Actions |
| **Scope** | Current worktree | Full repository |
| **Speed** | Incremental | Full |
| **Authority** | Advisory | Blocking |
| **Evidence** | Local artifacts | Signed artifacts |

### CI Workflow for Validation Gates

```yaml
# .github/workflows/validate.yml
name: Validation Gates
on:
  pull_request:
    branches: [main]
  merge_group:
    types: [checks_requested]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        run: npm ci

      - name: Gate 1 - Schema Validation
        run: npm run lint:schema

      - name: Gate 2 - Code Quality
        run: |
          npm run lint
          npm run typecheck

      - name: Gate 3 - Unit Tests
        run: npm test -- --coverage
        env:
          CI: true

      - name: Gate 4 - Integration Tests
        run: npm run test:integration

      - name: Gate 5 - Security Scan
        run: |
          npx semgrep --config auto --error
          npx gitleaks detect --source .
          npm audit --audit-level=high

      - name: Gate 6 - Drift Detection
        run: npx drift-checker --threshold 0.30

      - name: Gate 7 - Generate Evidence
        run: |
          mkdir -p evidence
          npm run evidence:generate

      - name: Upload Evidence
        uses: actions/upload-artifact@v4
        with:
          name: evidence-pack
          path: evidence/
```

### Gate-to-Evidence Mapping

Every gate produces evidence that feeds into the Evidence Pack:

```yaml
evidence_mapping:
  lint:
    gate: "Code Quality"
    output: "evidence/lint-report.json"
    required_for: ["pr_merge", "release"]

  typecheck:
    gate: "Code Quality"
    output: "evidence/typecheck-output.txt"
    required_for: ["pr_merge", "release"]

  unit_tests:
    gate: "Unit Tests"
    output: "evidence/test-results.xml"
    coverage: "evidence/coverage.json"
    required_for: ["pr_merge", "release"]

  security_scan:
    gate: "Security Scan"
    output: "evidence/security-scan.sarif"
    required_for: ["pr_merge", "release", "deploy"]

  drift_check:
    gate: "Drift Detection"
    output: "evidence/drift-report.json"
    required_for: ["pr_merge"]
    threshold: 0.30
```

### Gate Failure Recovery

When gates fail, CI provides structured feedback:

```yaml
# Gate failure response format
gate_failure:
  gate_name: "unit_tests"
  status: "failed"
  details:
    failing_tests: 3
    test_names:
      - "auth.login.should-validate-email"
      - "auth.login.should-rate-limit"
      - "auth.logout.should-clear-session"
    logs_url: "https://github.com/actions/runs/123/logs"
  recommended_action: "Review failing tests and fix or update expectations"
  escalation: "After 3 failures, escalate to dashboard"
```

---

## Related Documents

- `docs/00-overview/principles.md` — Validation gates are non-negotiable principle
- `docs/03-platform/context-engineering.md` — Context Engineering Program and gate definitions
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/05-compliance/slsa-provenance.md` — Build provenance
- `docs/06-operations/runbooks.md` — Validation Gate Failure Runbook
- `docs/07-integrations/git-integration.md` — Git workflows and PRP-based branches

---

**Version**: 2.1.0 | **Date**: 2026-01-08
