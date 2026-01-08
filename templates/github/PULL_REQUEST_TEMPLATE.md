## Summary
<!-- Brief description of changes. For automated PRs, this is auto-populated. -->
-

## Linked Issues
<!-- Required: Link to parent issue(s). Format: Closes #123 or Fixes #456 -->
- Closes #

## Run Context
<!-- For Operator Mode PRs, populated automatically -->
| Field | Value |
|-------|-------|
| **Run ID** | `run-` |
| **Workflow ID** | `wf-` |
| **Issue ID** | `#` |
| **Branch** | `itqahn/run-xxx/` |

## What Changed?
<!-- Describe the changes made -->
-

## Why?
<!-- Explain the motivation and context -->
-

## How to Test
<!-- Testing checklist - check applicable items -->
- [ ] Unit tests
- [ ] Integration tests
- [ ] Contract tests (if API change)
- [ ] E2E journeys (if user-facing)
- [ ] Visual regression (if UI change)

## Risk Flags
<!-- Check all that apply - triggers additional reviews -->
- [ ] Touches auth/authz
- [ ] Destructive migration
- [ ] Payments/billing
- [ ] Regulated data (PII/PHI)
- [ ] UI change (Design Jail applies)
- [ ] Infrastructure change
- [ ] Security-sensitive

## Compliance Tier
<!-- Select the applicable compliance tier -->
- [ ] T1 (public docs)
- [ ] T2 (internal tools)
- [ ] T3 (customer data)
- [ ] T4 (regulated/financial)

## Evidence Pack
<!-- Required for T3/T4 changes. For Operator Mode PRs, auto-linked. -->
| Evidence | Status |
|----------|--------|
| Evidence Pack | <!-- Link or "Pending" --> |
| Policy Verdict | <!-- pass/fail/pending --> |
| Security Scan | <!-- pass/fail/pending --> |
| Lint Report | <!-- pass/fail/pending --> |

## Merge Requirements
<!-- Auto-checked by merge queue -->
- [ ] All CI checks passing
- [ ] Required reviews obtained
- [ ] No merge conflicts
- [ ] Branch up to date with base
- [ ] Evidence Pack complete (if required)

---

## For Reviewers

### Review Checklist
- [ ] Code follows project conventions
- [ ] Tests cover the changes
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated (if needed)
- [ ] Design OS compliance (for UI changes)

### Auto-Merge Status
<!-- For Operator Mode PRs with auto-merge enabled -->
- [ ] Auto-merge enabled
- [ ] Will merge when all checks pass

---

<!--
OPERATOR MODE METADATA (do not edit)
This section is populated automatically by Itqahn Operator Mode.
-->
<!--
run_id:
workflow_id:
issue_id:
created_by: itqahn-bot
auto_merge: true
merge_queue: enabled
-->
