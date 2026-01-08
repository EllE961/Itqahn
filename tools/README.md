# Tools

This directory contains utilities that support Itqahn governance and development workflows.

---

## Directory Structure

```
tools/
├── validators/        # Validation utilities
├── drift-checker/     # Drift scoring tool
├── policy-tests/      # OPA and Kyverno tests
└── docsite-build/     # Documentation site builder
```

---

## Validators (`validators/`)

Build-time validation utilities for CI and local development.

| Tool | Purpose |
|------|---------|
| `design_jail_validator.py` | Rejects UI changes violating Design Jail |
| `evidence_pack_validator.py` | Validates Evidence Pack manifest and artifacts |
| `sbom_validator.py` | SBOM format validation |

```bash
# Run validators
python tools/validators/design_jail_validator.py --check src/
python tools/validators/evidence_pack_validator.py --manifest evidence/manifest.json
python tools/validators/sbom_validator.py --sbom sbom.json
```

---

## Drift Checker (`drift-checker/`)

Scores implementation against requirements to detect divergence.

```bash
# Calculate drift score
python tools/drift-checker/drift_scoring.py \
  --intent requirements/prd.json \
  --diff pr_diff.json \
  --out drift_report.json
```

See `tools/drift-checker/README.md` for details.

---

## Policy Tests (`policy-tests/`)

Tests for OPA and Kyverno policies.

```bash
# Run OPA tests
opa test policies/opa/ tools/policy-tests/opa/ -v

# Run Kyverno tests
kyverno test tools/policy-tests/kyverno/
```

See `tools/policy-tests/README.md` for details.

---

## Documentation Build (`docsite-build/`)

MkDocs-based documentation site builder.

```bash
# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy
mkdocs gh-deploy
```

See `tools/docsite-build/README.md` for details.

---

## CI Integration

All tools are designed to run in CI pipelines:

```yaml
jobs:
  validate:
    steps:
      - name: Run validators
        run: |
          python tools/validators/design_jail_validator.py
          python tools/validators/evidence_pack_validator.py

  policy-test:
    steps:
      - name: Test policies
        run: opa test policies/opa/ tools/policy-tests/opa/

  docs:
    steps:
      - name: Build docs
        run: mkdocs build --strict
```

---

## Related

- `policies/` — Policy definitions
- `templates/` — Template files
- `docs/` — Documentation source

---

**Version**: 2.0.0 | **Date**: 2026-01-06
