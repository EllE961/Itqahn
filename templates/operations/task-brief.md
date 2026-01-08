# Task Brief Template

Use this template when creating a new task with `/task`.

---

```markdown
# Task: {TASK_NAME}

**Slug**: {task-slug-kebab-case}
**Created**: {YYYY-MM-DDTHH:MM:SSZ}
**Status**: draft | planned | in-progress | blocked | done
**Run ID**: {run-id if applicable}
**Issue**: #{issue-number if applicable}

---

## Description

{Clear, concise description of what this task accomplishes. One to three sentences.}

---

## Scope

### In Scope

- {Specific item that IS included}
- {Another specific item that IS included}
- {Be explicit about boundaries}

### Out of Scope

- {Specific item that is NOT included}
- {Another item explicitly excluded}
- {Helps prevent scope creep}

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {What this depends on} | blocking / soft | resolved / pending |
| {Another dependency} | blocking / soft | resolved / pending |

*If no dependencies, state "None"*

---

## Acceptance Criteria

- [ ] {Specific, testable criterion 1}
- [ ] {Specific, testable criterion 2}
- [ ] {Specific, testable criterion 3}
- [ ] {Each criterion should be verifiable}
- [ ] {Avoid vague criteria like "works well"}

---

## Files to Change

| File | Action | Reason |
|------|--------|--------|
| `{path/to/file.ts}` | create | {Why creating this file} |
| `{path/to/other.ts}` | modify | {What changes and why} |
| `{path/to/old.ts}` | delete | {Why removing this file} |

---

## Technical Approach

{Brief description of how this will be implemented. Key decisions, patterns to use, etc.}

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {Potential risk} | low/medium/high | low/medium/high | {How to mitigate} |

*If no significant risks, state "None identified"*

---

## Verification

How to verify this task is complete:

1. {Verification step 1}
2. {Verification step 2}
3. {Run these specific tests}

---

## Notes

{Any additional context, references, or considerations}

---

## History

| Date | Action | By |
|------|--------|-----|
| {date} | Created | {worker/user} |
| {date} | Status changed to X | {worker/user} |
```

---

## Usage Notes

1. **Slug**: Use kebab-case, keep short but descriptive
2. **Scope**: Be explicit—ambiguity causes drift
3. **Acceptance Criteria**: Must be testable (yes/no, not "mostly")
4. **Files**: Estimate even if uncertain—helps detect drift
5. **Risks**: Always consider, even if "none identified"

---

**Template Version**: 1.0.0
