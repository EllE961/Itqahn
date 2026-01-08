# Context Budget Check — Validator Specification

**Status**: MUST be implemented

This validator monitors Claude Code context usage and enforces budget limits.

---

## Purpose

Prevent context overflow that leads to degraded performance, hallucinations, or lost work.

---

## Trigger

| Trigger | Frequency |
|---------|-----------|
| **Continuous** | Every 30 seconds during active session |
| **Before MCP call** | Before any MCP operation |
| **After large read** | After reading files > 5000 tokens |

---

## Configuration

```yaml
context_budget_check:
  thresholds:
    normal: 50        # Below 50%: normal operation
    warning: 50       # 50-70%: warning state
    soft_limit: 60    # 60%: suggest summarization
    hard_limit: 70    # 70%: force context reset

  measurement:
    method: token_count
    window: current_session
    include:
      - conversation_history
      - loaded_files
      - mcp_responses
      - working_memory
```

---

## Behavior

### At Normal (< 50%)

```yaml
action: continue
logging: none
user_notification: none
```

### At Warning (50-70%)

```yaml
action: log_warning
logging:
  level: warn
  message: "Context usage at {percentage}%"
suggestions:
  - "Consider summarizing loaded content"
  - "Write intermediate results to repo files"
  - "Use /catch-up to compress state"
```

### At Soft Limit (60%)

```yaml
action: suggest_summarization
logging:
  level: warn
  message: "Context usage at {percentage}%, approaching limit"
suggestions:
  - "Run /catch-up to create summary"
  - "Offload large content to files"
automated_actions:
  - compress_mcp_responses: true
  - suggest_file_references: true
```

### At Hard Limit (70%)

```yaml
action: force_context_reset
logging:
  level: error
  message: "Context budget exceeded at {percentage}%"
automated_actions:
  - stop_current_work: immediate
  - save_pending_changes: required
  - produce_context_reset_pack: required
  - notify_coordinator: required
  - request_new_session: required
blocking: true
```

---

## Context Reset Pack Production

When hard limit is reached, automatically produce:

```json
{
  "context_reset_pack": {
    "run_id": "{run_id}",
    "task_slug": "{task_slug}",
    "worker_id": "{worker_id}",
    "created_at": "{ISO timestamp}",
    "reason": "context_budget_exceeded",
    "context_usage_at_reset": "{percentage}%",

    "state_snapshot": {
      "phase": "{current phase}",
      "plan_ref": "{plan file path}",
      "completed_steps": [],
      "pending_steps": [],
      "files_modified": []
    },

    "pending_work": {
      "description": "{what was being done}",
      "blocked_by": null,
      "estimated_remaining_steps": 0
    },

    "resume_instructions": {
      "1": "Read plan at {plan path}",
      "2": "Check completed steps",
      "3": "Resume from step {n}",
      "4": "Run verification after completion"
    },

    "artifacts_produced": []
  }
}
```

**Location**: `context-reset/run-{run_id}/{task_slug}.json`

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Claude Code session** | Monitors token usage |
| **MCP proxy** | Checks before MCP calls |
| **Coordinator** | Notified on reset |
| **Dashboard** | Displays current usage |

---

## Metrics

| Metric | Description |
|--------|-------------|
| `context_usage_percent` | Current context usage |
| `context_resets_total` | Count of forced resets |
| `context_warnings_total` | Count of warnings issued |
| `time_in_warning_state` | Duration in warning |

---

## Error Handling

| Scenario | Action |
|----------|--------|
| **Cannot measure usage** | Assume 60%, issue warning |
| **Cannot write reset pack** | Log error, still request reset |
| **Coordinator unavailable** | Log locally, retry notification |

---

## Implementation Notes

**MUST implement:**
- Continuous monitoring loop
- Automatic Context Reset Pack generation
- Coordinator notification
- Session termination on hard limit

**SHOULD implement:**
- Predictive warnings (trending toward limit)
- Smart summarization suggestions
- Usage visualization for dashboard

---

**Version**: 1.0.0 | **Date**: 2026-01-08
