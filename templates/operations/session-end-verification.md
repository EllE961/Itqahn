# Session End Verification Template

Use this template with `/end` command to complete session verification.

---

```markdown
# Session End Verification

**PRP**: {prp-id}
**Run ID**: {run-id}
**Worker**: {worker-id or terminal-id}
**Timestamp**: {YYYY-MM-DDTHH:MM:SSZ}

---

## 1. Validation Gates

All required gates MUST pass before session can end.

### Code Quality Gates

| Gate | Command | Result | Notes |
|------|---------|--------|-------|
| Lint | `npm run lint` | Pass / Fail | Errors: {0} |
| Typecheck | `npm run typecheck` | Pass / Fail | Errors: {0} |
| Format | `npm run format:check` | Pass / Fail | |

### Test Gates

| Gate | Command | Result | Coverage | Notes |
|------|---------|--------|----------|-------|
| Unit Tests | `npm test` | Pass / Fail | {X}% | Passed: {N}/{N} |
| Integration | `npm run test:integration` | Pass / Fail | | Passed: {N}/{N} |

### Security Gates

| Gate | Command | Result | Findings | Notes |
|------|---------|--------|----------|-------|
| SAST | `semgrep` | Pass / Fail | Critical: {0}, High: {0} | |
| Secrets | `gitleaks` | Pass / Fail | Found: {0} | |
| Dependencies | `npm audit` | Pass / Fail | High+: {0} | |

### Drift Gate

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Drift Score | {0.XX} | < 0.30 | Pass / Fail |

---

## 2. Security Hygiene Check

- [ ] No secrets or credentials in code
- [ ] No API keys in committed files
- [ ] No sensitive data in logs or console
- [ ] Auth/authz properly implemented (if applicable)
- [ ] Input validation in place (if applicable)
- [ ] No SQL injection vulnerabilities (if applicable)
- [ ] No XSS vulnerabilities (if applicable)

**Security Notes**: {Any security observations or concerns}

---

## 3. Documentation Sync Check

- [ ] API documentation updated (if endpoints changed)
- [ ] README reflects changes (if applicable)
- [ ] `memory/current-status.md` updated
- [ ] `memory/decision-log.md` has new decisions
- [ ] Type definitions current (if interfaces changed)
- [ ] Comments added for complex logic

**Files Updated**:
- {list of documentation files touched}

---

## 4. Plan Alignment Check

### PRP Alignment

- [ ] All acceptance criteria verified
- [ ] Implementation matches PRP approach
- [ ] No unplanned files modified
- [ ] No out-of-scope features added

### Files Changed vs Planned

| Planned File | Action | Status |
|--------------|--------|--------|
| {path/file1.ts} | create | Done / Not Done |
| {path/file2.ts} | modify | Done / Not Done |

### Unplanned Changes

| File | Why Changed | Justified |
|------|-------------|-----------|
| {path/file.ts or "None"} | {reason} | Yes / No |

---

## 5. Evidence Pack

- [ ] Evidence artifacts generated
- [ ] All changes committed
- [ ] Commit messages follow format
- [ ] PR created / updated
- [ ] PR linked to issue
- [ ] Labels applied

**Evidence Location**: `evidence/{run-id}/`

**Artifacts**:
- [ ] `lint-report.json`
- [ ] `test-results.xml`
- [ ] `coverage.json`
- [ ] `security-scan.sarif`
- [ ] `drift-report.json`

---

## 6. Session Summary

### Completed

- {Completed item 1}
- {Completed item 2}
- {Completed item 3}

### Changes Made

| Category | Count | Details |
|----------|-------|---------|
| Files created | {N} | {list} |
| Files modified | {N} | {list} |
| Files deleted | {N} | {list} |
| Tests added | {N} | |
| Lines added | {N} | |
| Lines removed | {N} | |

### Decisions Made

| Decision | Rationale | Alternative Considered |
|----------|-----------|------------------------|
| {Decision 1} | {Why} | {What else was considered} |
| {Decision 2} | {Why} | {What else was considered} |

### Issues Encountered

| Issue | Resolution | Follow-up Needed |
|-------|------------|------------------|
| {Issue 1 or "None"} | {How resolved} | Yes / No |

---

## 7. Next Steps

### Immediate

- [ ] {Next immediate action if any}
- [ ] {Another immediate action}

### Future Work

- {Work identified but out of scope for this PRP}
- {Technical debt noted}

### Blockers

- {Any blockers for downstream work, or "None"}

---

## Verification Summary

| Category | Status | Notes |
|----------|--------|-------|
| Validation Gates | Pass / Fail | {notes} |
| Security | Pass / Fail | {notes} |
| Docs | Pass / Fail | {notes} |
| Alignment | Pass / Fail | {notes} |
| Evidence | Pass / Fail | {notes} |

**Overall**: PASS / FAIL

**Ready for Merge**: Yes / No

---

## Sign-off

```yaml
verification:
  completed_by: "{worker-id}"
  completed_at: "{ISO-8601}"
  all_gates_passed: true | false
  pr_number: "#{number}"
  evidence_pack: "evidence/{run-id}/manifest.json"
```
```

---

## Verification Checklist (Quick Reference)

Use this condensed checklist for quick verification:

```markdown
## Quick Verification Checklist

- [ ] `npm run lint` passes
- [ ] `npm run typecheck` passes
- [ ] `npm test` passes (coverage >= 80%)
- [ ] `npm run security:scan` passes (no critical/high)
- [ ] No secrets in code
- [ ] Docs updated
- [ ] memory/current-status.md updated
- [ ] memory/decision-log.md updated
- [ ] All PRP acceptance criteria met
- [ ] No unplanned files changed
- [ ] Drift score < 0.30
- [ ] Evidence artifacts generated
- [ ] All changes committed
- [ ] PR created with proper labels
```

---

## Failure Handling

If any check fails:

| Failure Type | Action |
|--------------|--------|
| **Validation gate** | Fix issue, re-run gate |
| **Security finding** | Must fix before proceeding |
| **Drift > 0.30** | Review with PRP owner |
| **Missing docs** | Update before completing |
| **Evidence missing** | Generate before completing |

If cannot resolve:
1. Document what was tried
2. Escalate via dashboard
3. Do NOT mark session as complete

---

**Template Version**: 1.0.0
