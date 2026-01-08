# Validation Tools

This directory contains validators used by the Context Engineering Program to enforce validation gates during PRP execution.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VALIDATION GATE ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │ Local        │     │ CI           │     │ Evidence     │                │
│  │ Validation   │────▶│ Validation   │────▶│ Pack         │                │
│  │ (Operator)   │     │ (GitHub)     │     │ (Signed)     │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│        │                    │                    │                          │
│        ▼                    ▼                    ▼                          │
│  Advisory only        Authoritative        Audit trail                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Validators

### Core Validators (Required Gates)

| Validator | Purpose | Blocking | Artifacts |
|-----------|---------|----------|-----------|
| `lint-validator` | Code style and patterns | Yes | `lint-report.json` |
| `typecheck-validator` | TypeScript type safety | Yes | `typecheck-output.txt` |
| `test-validator` | Unit and integration tests | Yes | `test-results.xml` |
| `security-validator` | SAST, secrets, dependencies | Yes | `security-scan.sarif` |
| `drift-validator` | Plan alignment check | Threshold | `drift-report.json` |

### Specialized Validators

| Validator | Purpose | Blocking | Artifacts |
|-----------|---------|----------|-----------|
| `design_jail_validator.py` | Design OS compliance | Yes | `design-jail-report.json` |
| `evidence_pack_validator.py` | Evidence Pack completeness | Yes | `evidence-validation.json` |
| `sbom_validator.py` | SBOM accuracy and format | Yes | `sbom-validation.json` |

### Context Engineering Validators

| Validator | Purpose | Blocking | Artifacts |
|-----------|---------|----------|-----------|
| `context-budget-check.md` | Context utilization monitoring | Warning | `context-budget.json` |
| `run-artifacts-check.md` | Run artifacts completeness | Yes | `run-artifacts.json` |
| `prp-schema-validator` | PRP format validation | Yes | `prp-validation.json` |
| `initial-schema-validator` | INITIAL format validation | Yes | `initial-validation.json` |

---

## Validator Specifications

### lint-validator

**Description**: Runs ESLint and Prettier to check code style and patterns.

**Inputs**:
- Source files in `src/`
- Configuration in `.eslintrc.js` and `.prettierrc`

**Outputs**:
```json
{
  "validator": "lint",
  "status": "pass | fail",
  "errors": 0,
  "warnings": 5,
  "files_checked": 42,
  "report_file": "evidence/lint-report.json"
}
```

**Pass Criteria**:
- Zero errors
- Warnings allowed (logged but don't block)

**CI Command**:
```bash
npm run lint -- --format json --output-file evidence/lint-report.json
```

---

### typecheck-validator

**Description**: Runs TypeScript compiler in check mode.

**Inputs**:
- TypeScript files in `src/`
- Configuration in `tsconfig.json`

**Outputs**:
```json
{
  "validator": "typecheck",
  "status": "pass | fail",
  "errors": 0,
  "files_checked": 42,
  "output_file": "evidence/typecheck-output.txt"
}
```

**Pass Criteria**:
- Zero type errors
- Zero implicit any (if strict mode)

**CI Command**:
```bash
npx tsc --noEmit 2>&1 | tee evidence/typecheck-output.txt
```

---

### test-validator

**Description**: Runs test suites and checks coverage thresholds.

**Inputs**:
- Test files in `tests/` or `*.test.ts`
- Configuration in `vitest.config.ts` or `jest.config.js`

**Outputs**:
```json
{
  "validator": "tests",
  "status": "pass | fail",
  "total": 150,
  "passed": 150,
  "failed": 0,
  "skipped": 2,
  "coverage": {
    "lines": 85.5,
    "branches": 78.2,
    "functions": 90.1,
    "statements": 84.3
  },
  "threshold_met": true,
  "report_file": "evidence/test-results.xml"
}
```

**Pass Criteria**:
- All tests pass (except explicitly skipped)
- Coverage >= 80% lines
- No test timeout

**CI Command**:
```bash
npm test -- --coverage --reporter=junit --outputFile=evidence/test-results.xml
```

---

### security-validator

**Description**: Runs security scans (SAST, secrets, dependency audit).

**Inputs**:
- Source code
- Dependencies in `package.json`

**Outputs**:
```json
{
  "validator": "security",
  "status": "pass | fail",
  "sast": {
    "critical": 0,
    "high": 0,
    "medium": 3,
    "low": 5
  },
  "secrets": {
    "found": 0
  },
  "dependencies": {
    "critical": 0,
    "high": 0,
    "moderate": 2
  },
  "report_file": "evidence/security-scan.sarif"
}
```

**Pass Criteria**:
- Zero critical findings
- Zero high findings
- Zero secrets detected

**CI Command**:
```bash
semgrep --config auto --sarif --output evidence/sast.sarif
gitleaks detect --source . --report-format sarif --report-path evidence/secrets.sarif
npm audit --json > evidence/npm-audit.json
```

---

### drift-validator

**Description**: Checks if implementation aligns with approved PRP.

**Inputs**:
- Current PRP artifact
- Git diff of changed files
- Implementation artifacts

**Outputs**:
```json
{
  "validator": "drift",
  "status": "pass | warning | fail",
  "drift_score": 0.15,
  "threshold": 0.30,
  "categories": {
    "scope": 0.05,
    "approach": 0.08,
    "files": 0.02,
    "behavior": 0.00
  },
  "divergences": [
    {
      "category": "files",
      "description": "Modified src/utils.ts (not in PRP)",
      "severity": "low"
    }
  ],
  "report_file": "evidence/drift-report.json"
}
```

**Pass Criteria**:
- Drift score < 0.30: Pass
- Drift score 0.30-0.50: Warning, continue
- Drift score > 0.50: Fail, pause for review

**CI Command**:
```bash
drift-checker --prp prp.yaml --threshold 0.30 --output evidence/drift-report.json
```

---

### design_jail_validator.py

**Description**: Validates UI code against Design OS constraints.

**Inputs**:
- UI components in `src/components/`
- Design OS in `design-os/`

**Outputs**:
```json
{
  "validator": "design-jail",
  "status": "pass | fail",
  "violations": [],
  "tokens_used": ["color-primary", "spacing-md"],
  "components_validated": 15,
  "report_file": "evidence/design-jail-report.json"
}
```

**Pass Criteria**:
- Zero Design Jail violations
- All tokens from approved token set
- All components from approved component library

**CI Command**:
```bash
python tools/validators/design_jail_validator.py --config design-os/config.json
```

---

### evidence_pack_validator.py

**Description**: Validates Evidence Pack completeness and integrity.

**Inputs**:
- Evidence Pack manifest
- Referenced artifacts

**Outputs**:
```json
{
  "validator": "evidence-pack",
  "status": "pass | fail",
  "manifest_valid": true,
  "artifacts_present": true,
  "signatures_valid": true,
  "missing_artifacts": [],
  "report_file": "evidence/evidence-validation.json"
}
```

**Pass Criteria**:
- Manifest follows schema
- All referenced artifacts exist
- Signatures verify

**CI Command**:
```bash
python tools/validators/evidence_pack_validator.py --manifest evidence/manifest.json
```

---

### prp-schema-validator

**Description**: Validates PRP document structure and content.

**Inputs**:
- PRP YAML file

**Outputs**:
```json
{
  "validator": "prp-schema",
  "status": "pass | fail",
  "errors": [],
  "warnings": [],
  "sections_present": {
    "context": true,
    "requirements": true,
    "examples": true,
    "implementation": true,
    "validation_gates": true,
    "edge_cases": true,
    "rollback": true,
    "definition_of_done": true
  }
}
```

**Pass Criteria**:
- All required sections present
- At least 2 examples
- At least 3 acceptance criteria
- All files listed have action and reason
- No vague terms ("fast", "better", "nice")

**CI Command**:
```bash
prp-validator --file prp.yaml --schema templates/product/PRP.schema.json
```

---

## Using Validators

### Local (Operator Mode)

```bash
# Run all validators
npm run validate

# Run specific validator
npm run validate:lint
npm run validate:tests
npm run validate:security
npm run validate:drift

# Run with verbose output
npm run validate -- --verbose
```

### CI (GitHub Actions)

```yaml
# .github/workflows/validate.yml
name: Validation Gates
on: [pull_request, merge_group]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run validate
      - uses: actions/upload-artifact@v4
        with:
          name: evidence
          path: evidence/
```

### Programmatic

```typescript
import { runValidators } from '@itqahn/validators';

const results = await runValidators({
  gates: ['lint', 'typecheck', 'tests', 'security', 'drift'],
  outputDir: 'evidence/',
  failFast: false,
});

if (!results.allPassed) {
  console.error('Validation failed:', results.failures);
  process.exit(1);
}
```

---

## Adding New Validators

1. Create validator file in `tools/validators/`
2. Implement standard interface:

```python
# tools/validators/my_validator.py
def validate(config: dict) -> dict:
    """
    Run validation and return results.

    Returns:
        {
            "validator": "my-validator",
            "status": "pass | fail",
            "details": {...},
            "report_file": "evidence/my-report.json"
        }
    """
    pass
```

3. Add to `validation_gates` in PRP template
4. Add to CI workflow
5. Document in this README

---

## Error Handling

| Error Type | Action |
|------------|--------|
| Validator crashes | Log error, mark as fail, continue |
| Timeout | Mark as fail with timeout reason |
| Missing config | Use defaults, log warning |
| Invalid output | Mark as fail, log parse error |

---

## Related Documents

- `docs/03-platform/context-engineering.md` — Context Engineering Program
- `docs/03-platform/ci-cd-gitops.md` — CI/CD and validation gates
- `docs/05-compliance/evidence-pack.md` — Evidence Pack specification
- `templates/product/PRP.md` — PRP template with gate definitions
- `docs/06-operations/runbooks.md` — Validation Gate Failure Runbook

---

**Version**: 1.0.0 | **Date**: 2026-01-08
