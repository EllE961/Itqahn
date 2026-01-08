# Plan Review Checklist Template

Use this checklist during Plan Mode to validate plans before implementation.

---

```markdown
# Plan Review Checklist

**Task**: {task-name}
**Plan Version**: {N}
**Reviewer**: {worker-id}
**Timestamp**: {YYYY-MM-DDTHH:MM:SSZ}

---

## 1. Requirements Clarity

- [ ] Requirements are specific and measurable
- [ ] No ambiguous terms ("better", "improved", "nice", "fast")
- [ ] Scope is bounded (what's NOT included is clear)
- [ ] Success criteria are binary (done/not done, not "mostly")

**Issues found**: {none or list}

---

## 2. Risk Assessment

- [ ] Risks have been considered (even if "none significant")
- [ ] High-likelihood risks have mitigations
- [ ] Fallback approach exists if primary fails
- [ ] Dependencies on external systems identified

**Risks identified**:
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| {risk} | {H/M/L} | {mitigation} |

---

## 3. Dependencies

- [ ] Blocking dependencies are listed
- [ ] External dependencies identified
- [ ] Order of operations is clear
- [ ] No circular dependencies

**Dependencies**:
- {dependency 1}: {blocking/soft} - {status}
- {dependency 2}: {blocking/soft} - {status}

---

## 4. Acceptance Criteria

- [ ] Each criterion is testable
- [ ] Success/failure is binary
- [ ] Criteria cover ALL requirements
- [ ] No vague criteria ("works well", "is fast")

**Criteria review**:
| Criterion | Testable? | Clear? |
|-----------|-----------|--------|
| {criterion} | Yes/No | Yes/No |

---

## 5. Implementation Plan

- [ ] Files to change are listed
- [ ] Actions per file are clear (create/modify/delete)
- [ ] Logical sequence of steps
- [ ] No steps require clarification
- [ ] Estimate is reasonable

**Steps review**:
| Step | Clear? | Dependencies? |
|------|--------|---------------|
| {step} | Yes/No | {deps or none} |

---

## 6. Verification Approach

- [ ] How to verify each criterion is defined
- [ ] What tests to run is specified
- [ ] Manual verification steps (if any) are clear
- [ ] Edge cases are covered

---

## 7. Resource Estimates

- [ ] File count is reasonable for scope
- [ ] Complexity matches available time
- [ ] No obvious under/over-estimation

---

## Review Summary

| Section | Status | Notes |
|---------|--------|-------|
| Requirements | Pass/Fail | {notes} |
| Risks | Pass/Fail | {notes} |
| Dependencies | Pass/Fail | {notes} |
| Acceptance Criteria | Pass/Fail | {notes} |
| Implementation | Pass/Fail | {notes} |
| Verification | Pass/Fail | {notes} |
| Resources | Pass/Fail | {notes} |

---

## Decision

- [ ] **APPROVED**: Plan is ready for implementation
- [ ] **NEEDS REVISION**: See issues below
- [ ] **REJECTED**: Major issues, start over

**Reason**: {explanation}

---

## Issues to Address

{List specific issues that must be fixed before approval, or "None"}

1. {Issue 1}: {what to fix}
2. {Issue 2}: {what to fix}

---

## Next Steps

{What happens next—revise plan, proceed to build, etc.}
```

---

## Review Iteration

Plans should go through at least 2 review cycles:

1. **Initial Review**: Check all sections, identify gaps
2. **Refinement Review**: Verify gaps are addressed, simplify if possible
3. **Approval Review**: Final check before implementation

---

**Template Version**: 1.0.0
