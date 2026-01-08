# Run Artifacts Check — Validator Specification

**Status**: MUST be implemented

This validator ensures all required artifacts are produced before a run is considered complete.

---

## Purpose

Prevent incomplete runs by verifying all required artifacts exist and are valid before marking a run as successful.

---

## Trigger

| Trigger | When |
|---------|------|
| **Run completion** | When Coordinator marks run as complete |
| **PR creation** | Before worker creates PR |
| **Session end** | Before worker session terminates |

---

## Configuration

```yaml
run_artifacts_check:
  required_artifacts:
    per_run:
      - path: "runs/run-{run_id}/run-record.json"
        required: true
        producer: coordinator

      - path: "runs/run-{run_id}/run-summary.md"
        required: true
        producer: coordinator

    per_task:
      - path: "plans/run-{run_id}/{task_slug}.md"
        required: true
        producer: worker
        phase: plan

      - path: "catch-up/run-{run_id}/{task_slug}.md"
        required: true
        producer: worker
        phase: ongoing

      - path: "evidence/run-{run_id}/{task_slug}-verification.json"
        required: true
        producer: worker
        phase: verify

    conditional:
      - path: "context-reset/run-{run_id}/{task_slug}.json"
        required: false
        condition: context_budget_exceeded
        producer: validator
```

---

## Behavior

### At PR Creation (per-task)

```yaml
trigger: worker_creates_pr
checks:
  - artifact: "plans/run-{run_id}/{task_slug}.md"
    validation:
      - exists: true
      - not_empty: true
      - has_required_sections: true
    on_fail: block_pr

  - artifact: "evidence/run-{run_id}/{task_slug}-verification.json"
    validation:
      - exists: true
      - valid_json: true
      - overall_status: "pass"
    on_fail: block_pr

  - artifact: "catch-up/run-{run_id}/{task_slug}.md"
    validation:
      - exists: true
    on_fail: warn_only

on_all_pass: allow_pr
on_any_fail: block_pr_with_reason
```

### At Run Completion (per-run)

```yaml
trigger: coordinator_marks_complete
checks:
  - artifact: "runs/run-{run_id}/run-record.json"
    validation:
      - exists: true
      - valid_json: true
      - has_required_fields: [run_id, start_time, tasks, status]
    on_fail: block_completion

  - artifact: "runs/run-{run_id}/run-summary.md"
    validation:
      - exists: true
      - not_empty: true
      - has_required_sections: true
    on_fail: block_completion

  - all_task_artifacts:
      for_each_task: run.tasks
      check: "evidence/run-{run_id}/{task_slug}-verification.json"
      validation:
        - exists: true
        - overall_status: "pass"
    on_fail: block_completion

on_all_pass: allow_completion
on_any_fail: block_completion_with_details
```

---

## Artifact Validation Rules

### Plan Artifact

```yaml
path: "plans/run-{run_id}/{task_slug}.md"
required_sections:
  - "## Context"
  - "## Scope"
  - "## Implementation Steps"
  - "## File Change Summary"
  - "## Verification Criteria"
  - "## Plan Status"
validation:
  - not_empty: true
  - plan_status_complete: true
```

### Verification Report

```yaml
path: "evidence/run-{run_id}/{task_slug}-verification.json"
required_fields:
  - verification_report.run_id
  - verification_report.task_slug
  - verification_report.timestamp
  - verification_report.checks
  - verification_report.overall_status
validation:
  - valid_json: true
  - overall_status: "pass"
  - all_checks_present: [lint, typecheck, unit_tests, security_scan, plan_alignment]
```

### Run Summary

```yaml
path: "runs/run-{run_id}/run-summary.md"
required_sections:
  - "## Overview"
  - "## Scope"
  - "## Workers"
  - "## Metrics"
  - "## Verification Summary"
  - "## Evidence Pack"
validation:
  - not_empty: true
  - all_tasks_listed: true
```

---

## Error Responses

### Missing Artifact

```json
{
  "error": "artifact_missing",
  "artifact": "plans/run-01J5ABCD/user-auth.md",
  "expected_producer": "worker",
  "phase": "plan",
  "action_required": "Create plan artifact before proceeding",
  "blocking": true
}
```

### Invalid Artifact

```json
{
  "error": "artifact_invalid",
  "artifact": "evidence/run-01J5ABCD/user-auth-verification.json",
  "validation_errors": [
    "overall_status is 'fail', expected 'pass'",
    "lint check failed with 3 errors"
  ],
  "action_required": "Fix verification failures and re-run /verify",
  "blocking": true
}
```

### Incomplete Artifact

```json
{
  "error": "artifact_incomplete",
  "artifact": "plans/run-01J5ABCD/user-auth.md",
  "missing_sections": ["## Verification Criteria", "## Plan Status"],
  "action_required": "Complete all required sections in plan",
  "blocking": true
}
```

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Worker** | Checked before PR creation |
| **Coordinator** | Checked before run completion |
| **CI pipeline** | Validates artifacts exist |
| **Dashboard** | Shows artifact status |

---

## Metrics

| Metric | Description |
|--------|-------------|
| `artifacts_missing_total` | Count of missing artifacts |
| `artifacts_invalid_total` | Count of invalid artifacts |
| `pr_blocked_for_artifacts` | PRs blocked due to missing artifacts |
| `runs_blocked_for_artifacts` | Runs blocked due to missing artifacts |

---

## Recovery Actions

| Scenario | Recovery |
|----------|----------|
| **Plan missing** | Run `/plan` to generate |
| **Verification missing** | Run `/verify` to generate |
| **Catch-up missing** | Run `/catch-up` to generate |
| **Run summary missing** | Coordinator must regenerate |
| **Invalid JSON** | Delete and regenerate artifact |

---

## Implementation Notes

**MUST implement:**
- Pre-PR artifact validation
- Pre-completion artifact validation
- Clear error messages with recovery actions
- Blocking behavior for required artifacts

**SHOULD implement:**
- Automatic regeneration suggestions
- Artifact freshness checks (not stale)
- Cross-reference validation (plan matches code)

---

**Version**: 1.0.0 | **Date**: 2026-01-08
