# SLSA Provenance

Itqahn targets SLSA Level 3 for software supply chain security. All build artifacts include cryptographic provenance.

---

## SLSA Overview

SLSA (Supply-chain Levels for Software Artifacts) is a framework for software supply chain security:

| Level | Requirements | Itqahn Status |
|-------|--------------|---------------|
| **L1** | Provenance exists | Required |
| **L2** | Hosted build, signed provenance | Required |
| **L3** | Isolated builds, non-falsifiable provenance | Target |
| **L4** | Two-party review, hermetic builds | Stretch goal |

---

## SLSA L3 Requirements

### Build Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Isolated build** | Ephemeral runners, no shared state |
| **Parameterless** | Build inputs from source only |
| **Hermetic** | No network access during build |
| **Reproducible** | Same inputs → same outputs |

### Provenance Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Non-falsifiable** | Signed by build service, not user |
| **Unforgeable** | Cryptographic signature |
| **Complete** | All materials and builder info |
| **Authentic** | Verifiable via transparency log |

---

## Provenance Format

Itqahn uses in-toto attestation format:

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v1",
  "subject": [
    {
      "name": "registry.io/user-service",
      "digest": {
        "sha256": "abc123..."
      }
    }
  ],
  "predicate": {
    "buildDefinition": {
      "buildType": "https://itqahn.io/build/v1",
      "externalParameters": {
        "repository": "https://github.com/org/user-service",
        "ref": "refs/heads/main",
        "commit": "def456..."
      },
      "internalParameters": {
        "workflow_id": "wf-xyz789",
        "agent_id": "backend-builder"
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/org/user-service@def456",
          "digest": {
            "sha256": "..."
          }
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://itqahn.io/builders/github-actions/v1"
      },
      "metadata": {
        "invocationId": "github.com/org/user-service/actions/runs/123",
        "startedOn": "2026-01-06T12:00:00Z",
        "finishedOn": "2026-01-06T12:05:00Z"
      }
    }
  }
}
```

---

## Build Isolation

### Ephemeral Runners

```yaml
# GitHub Actions with ephemeral runners
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/itqahn/builder:latest
      options: --read-only --network none
```

### Network Isolation

```yaml
# No network access during build
steps:
  - name: Fetch dependencies (cached)
    run: |
      # Dependencies pre-fetched in builder image
      npm ci --offline

  - name: Build
    env:
      NO_PROXY: "*"
    run: |
      npm run build
```

### No Shared State

```yaml
# Each build starts fresh
container:
  options: |
    --rm
    --read-only
    --tmpfs /tmp:rw,noexec,nosuid
```

---

## Provenance Generation

### Automated Generation

```yaml
# SLSA GitHub Generator
- uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1
  with:
    image: ${{ env.IMAGE }}
    digest: ${{ env.DIGEST }}
```

### Itqahn-Specific Materials

In addition to standard provenance, record:

```json
{
  "materials": [
    {
      "uri": "git+https://github.com/org/repo@commit",
      "digest": {"sha256": "..."}
    },
    {
      "uri": "prompt://wf-xyz789/step-3",
      "digest": {"sha256": "..."}, // hash of prompt
      "annotations": {
        "model": "claude-3-opus",
        "agent": "backend-builder",
        "workflow_id": "wf-xyz789"
      }
    }
  ]
}
```

---

## Signing

### Sigstore Integration

```bash
# Sign with Sigstore/cosign
cosign sign \
  --key cosign.key \
  registry.io/user-service@sha256:abc123

# Or keyless signing
cosign sign \
  --fulcio-url https://fulcio.sigstore.dev \
  --rekor-url https://rekor.sigstore.dev \
  registry.io/user-service@sha256:abc123
```

### Transparency Log

All signatures recorded in Rekor:

```bash
# Verify entry exists
rekor-cli search \
  --sha sha256:abc123

# Get full entry
rekor-cli get \
  --uuid 24296fb24b8ad77a...
```

---

## Verification

### At Build Time

```yaml
- name: Verify dependencies
  run: |
    # Verify all dependencies have provenance
    slsa-verifier verify-artifact \
      --provenance-path provenance.intoto.jsonl \
      --source-uri github.com/org/repo
```

### At Deploy Time

```yaml
# Kubernetes admission controller
apiVersion: policy.sigstore.dev/v1alpha1
kind: ClusterImagePolicy
metadata:
  name: require-slsa
spec:
  images:
    - glob: "registry.io/**"
  authorities:
    - keyless:
        url: https://fulcio.sigstore.dev
        identities:
          - issuer: https://token.actions.githubusercontent.com
            subject: https://github.com/org/*
```

### Verification Code

```python
from sigstore.verify import Verifier

def verify_provenance(artifact_digest: str, provenance_path: str) -> bool:
    verifier = Verifier.production()

    # Load provenance
    with open(provenance_path) as f:
        provenance = json.load(f)

    # Verify signature
    result = verifier.verify(
        artifact_digest=artifact_digest,
        provenance=provenance,
        expected_builder="https://itqahn.io/builders/github-actions/v1"
    )

    return result.verified
```

---

## Policy Enforcement

### OPA Policy

```rego
# policies/opa/supply-chain/provenance_required.rego
package supplychain

default allow = false

allow {
  # Provenance must exist
  input.evidence_pack.artifacts.provenance

  # SLSA level must be 3+
  input.evidence_pack.artifacts.provenance.slsa_level >= 3

  # Builder must be trusted
  trusted_builders[input.provenance.predicate.runDetails.builder.id]
}

trusted_builders := {
  "https://itqahn.io/builders/github-actions/v1",
  "https://itqahn.io/builders/internal/v1",
}
```

---

## Prompt Lineage

For AI-generated code, record prompt lineage:

| Field | Value | Purpose |
|-------|-------|---------|
| `prompt_hash` | SHA256 of prompt | Audit trail without exposing content |
| `model` | Model ID + version | Reproducibility |
| `agent_id` | Agent role | Attribution |
| `workflow_id` | Workflow ID | Traceability |

```json
{
  "uri": "prompt://wf-xyz789/backend-builder/step-3",
  "digest": {
    "sha256": "hash-of-prompt-text"
  },
  "annotations": {
    "model": "claude-3-opus-20240229",
    "agent_id": "backend-builder",
    "workflow_id": "wf-xyz789",
    "activity_id": "act-step-3",
    "temperature": 0.0
  }
}
```

---

## Related Documents

- `docs/05-compliance/evidence-pack.md` — Evidence Pack structure
- `docs/05-compliance/sbom-vex.md` — Dependency tracking
- `docs/03-platform/ci-cd-gitops.md` — Build pipeline

---

**Version**: 2.0.0 | **Date**: 2026-01-06
