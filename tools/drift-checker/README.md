# Drift Checker

Itqahn uses drift scoring to ensure implementation matches intent.

---

## Overview

The drift checker compares implementation against requirements to detect when code diverges from stated intent.

```
┌─────────────────────────────────────────────────────────────────┐
│                      DRIFT SCORING                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Inputs:                         Outputs:                        │
│  ┌──────────────┐               ┌──────────────┐                │
│  │     PRD      │               │ Drift Score  │                │
│  │ Acceptance   │──────────────▶│  (0..1)      │                │
│  │    ADRs      │               │  Hotspots    │                │
│  │  Code Diff   │               │ Suggestions  │                │
│  └──────────────┘               └──────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Usage

```bash
# Run drift scoring
python drift_scoring.py \
  --intent requirements/prd.json \
  --diff pr_diff.json \
  --out drift_report.json
```

---

## Inputs

| Input | Description | Format |
|-------|-------------|--------|
| `--intent` | Requirements reference | JSON (PRD/AC references) |
| `--diff` | Code changes | JSON (files, paths) |
| `--out` | Output report | JSON (default: drift_report.json) |

---

## Outputs

```json
{
  "score": 0.15,
  "hotspots": ["src/auth.ts", "src/api/login.ts"],
  "suggestions": [
    "Consider adding test for edge case X"
  ],
  "intent_ref": "prd-auth-123"
}
```

### Score Interpretation

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.0 - 0.2 | Low drift | Proceed |
| 0.2 - 0.4 | Moderate drift | Review |
| 0.4 - 0.7 | High drift | Investigate |
| 0.7 - 1.0 | Severe drift | Block |

---

## Integration

### CI Integration

```yaml
# GitHub Actions
- name: Check Drift
  run: |
    python tools/drift-checker/drift_scoring.py \
      --intent ${{ github.workspace }}/requirements/prd.json \
      --diff pr_diff.json \
      --out drift_report.json

- name: Fail on High Drift
  run: |
    SCORE=$(jq '.score' drift_report.json)
    if (( $(echo "$SCORE > 0.4" | bc -l) )); then
      echo "Drift too high: $SCORE"
      exit 1
    fi
```

---

## Implementation Notes

The current implementation is a stub. Replace with real drift scoring:

1. **Embedding similarity** — Compare requirement embeddings to code
2. **Structured checks** — Match acceptance criteria to tests
3. **Test mapping** — Verify test coverage for requirements

---

## Related

- `docs/06-operations/sre-model.md` — Drift as SRE metric
- `agents/10-meta-and-evaluation/drift-detector.md` — Drift agent

---

**Version**: 2.0.0 | **Date**: 2026-01-06
