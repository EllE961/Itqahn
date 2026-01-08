# Verification Checklist Template

Use this checklist with `/verify` command.

---

```markdown
# Verification Report

**Task**: {task-name}
**Run ID**: {run-id}
**Worker**: {worker-id}
**Timestamp**: {YYYY-MM-DDTHH:MM:SSZ}

---

## 1. Code Quality

### Lint
- [ ] `npm run lint` passes
- Errors: {0}
- Warnings: {N}

### Type Check
- [ ] `npm run typecheck` passes
- Errors: {0}

### Tests

#### Unit Tests
- [ ] `npm run test:unit` passes
- Total: {N}
- Passed: {N}
- Failed: {0}
- Coverage: {X%}

#### Integration Tests
- [ ] `npm run test:integration` passes
- Total: {N}
- Passed: {N}
- Failed: {0}

---

## 2. Security

### Security Scan
- [ ] `npm run security:scan` passes
- Critical: {0}
- High: {0}
- Medium: {N}
- Low: {N}

### Secret Scan
- [ ] `npm run secrets:scan` passes
- Detected: {0}

### Manual Check
- [ ] No credentials in code
- [ ] No API keys in code
- [ ] No sensitive data in logs
- [ ] Auth/authz properly implemented (if applicable)

---

## 3. Plan Alignment

### Scope Check
- [ ] Implementation matches plan
- Drift score: {0.XX}

### Unplanned Changes
- [ ] No unplanned files modified
- Files outside plan: {none or list}

### Missing Items
- [ ] All planned items implemented
- Missing: {none or list}

---

## 4. Consistency

### Code Patterns
- [ ] Follows existing patterns
- [ ] Naming conventions followed
- [ ] File structure consistent

### Documentation
- [ ] Code comments where needed
- [ ] API documented (if applicable)
- [ ] README updated (if needed)

---

## 5. Performance

### Quick Check
- [ ] No obvious N+1 queries
- [ ] No blocking calls in async code
- [ ] No memory leaks introduced
- [ ] Bundle size reasonable (if applicable)

---

## 6. Memory Update

### Memory Files
- [ ] `memory/current-status.md` updated
- [ ] `memory/decision-log.md` has new decisions
- [ ] `memory/project-index.md` reflects changes

---

## Summary

| Category | Status | Notes |
|----------|--------|-------|
| Code Quality | Pass/Fail | {notes} |
| Security | Pass/Fail | {notes} |
| Plan Alignment | Pass/Fail | {notes} |
| Consistency | Pass/Fail | {notes} |
| Performance | Pass/Fail | {notes} |
| Memory | Pass/Fail | {notes} |

**Overall**: PASS / FAIL

**Ready for PR**: Yes / No

---

## Blocking Issues

{List any issues that must be fixed before PR, or "None"}

---

## Warnings

{List any warnings or suggestions, or "None"}
```

---

## Verification Levels

| Level | When | Checks |
|-------|------|--------|
| **Quick** | During development | Lint + type check |
| **Standard** | Before PR | All automated checks |
| **Full** | Before merge to main | Standard + manual review |

---

**Template Version**: 1.0.0
