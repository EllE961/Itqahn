# Claude Code Operator Playbook: Context Engineering for Itqahn

This playbook defines the production-grade operating model for running Itqahn with Claude Code Max. It ensures reliability under long projects, fast parallel execution, and consistent behavior across sessions.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT ENGINEERING PILLARS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   MEMORY     │  │  PROGRESSIVE │  │    HOOKS     │  │  PARALLEL    │    │
│  │   STRATEGY   │  │  DISCLOSURE  │  │   (RITUALS)  │  │   SAFETY     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  Durable state      Load only what     Enforce good      No merge          │
│  across sessions    matters now        habits auto       chaos             │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    PLAN      │  │   TOOLING    │  │   VERIFY     │  │   RECOVERY   │    │
│  │   DISCIPLINE │  │  DISCIPLINE  │  │   RITUALS    │  │  PROCEDURES  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  Never accept       Skills over MCPs   End-of-session    When Claude       │
│  first plan         (less bloat)       verification      gets worse        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## A. Always-On Rules (CLAUDE.md Strategy)

### What Belongs in CLAUDE.md

The root `CLAUDE.md` file is **always injected** into every Claude Code session. Keep it **small and always-relevant**.

**MUST include:**

| Content | Why |
|---------|-----|
| Core discipline (Plan→Build→Verify) | Enforced every session |
| Context budget thresholds | Prevents degradation |
| Git workflow rules | Never changes |
| Forbidden actions | Safety-critical |
| Memory file locations | Always needed |

**MUST NOT include:**

| Content | Why | Where Instead |
|---------|-----|---------------|
| Project-specific requirements | Changes per project | `memory/project-index.md` |
| Current task details | Changes frequently | `memory/current-status.md` |
| Historical decisions | Grows unbounded | `memory/decision-log.md` |
| API documentation | Context bloat | External docs, retrieve as needed |
| Full code standards | Too large | `standards/` folder, load when relevant |

### Hierarchical Memory Policy

```
Repository Root
├── CLAUDE.md                    # Always injected (< 200 lines)
│
├── memory/                      # Durable project memory
│   ├── project-index.md         # What exists, where to find it
│   ├── current-status.md        # Active work, blockers, next steps
│   ├── decision-log.md          # Why we chose X over Y
│   └── standards.md             # Project-specific conventions
│
├── src/
│   └── CLAUDE.md                # Code-specific rules (if needed)
│
├── tests/
│   └── CLAUDE.md                # Test-specific rules (if needed)
│
└── docs/
    └── CLAUDE.md                # Doc-specific rules (if needed)
```

**Hierarchical rules:**

| Scope | CLAUDE.md Location | When to Create |
|-------|-------------------|----------------|
| **Global** | Repository root | Always (mandatory) |
| **Domain** | `src/`, `tests/`, `docs/` | When domain has unique rules |
| **Module** | Specific subdirectory | Rarely; only for complex modules |

**Rule**: Subfolder `CLAUDE.md` files SHOULD be < 50 lines. They supplement, not replace, the root file.

### Mandatory Memory Files

| File | Purpose | Update Cadence |
|------|---------|----------------|
| `memory/project-index.md` | What exists, key files, architecture | On structural changes |
| `memory/current-status.md` | Active tasks, blockers, next steps | Every session end |
| `memory/decision-log.md` | Decisions with rationale | When decisions made |
| `memory/standards.md` | Project conventions, patterns | When standards change |

**Memory File Format:**

```markdown
# Current Status

**Last updated**: 2026-01-08T14:30:00Z
**Updated by**: Worker-1 (run-01J5ABCD)

## Active Work
- Task: User Authentication
- Phase: Build (step 3 of 5)
- Branch: feat/run-01J5ABCD-user-auth

## Blockers
None

## Next Steps
1. Complete password reset flow
2. Add unit tests
3. Run verification

## Recent Decisions
- Chose JWT over sessions (see decision-log.md#auth-001)
```

### Keep Rules Minimal Policy

**Hard limit**: Root `CLAUDE.md` MUST be < 200 lines.

**Audit trigger**: If `CLAUDE.md` exceeds 150 lines, review and extract:
- Move project-specific content to `memory/`
- Move standards to `standards/`
- Move domain rules to subfolder `CLAUDE.md`

```yaml
# .claude/settings.yaml
memory:
  root_claude_md:
    max_lines: 200
    warn_at: 150
  subfolder_claude_md:
    max_lines: 50
    warn_at: 40
```

---

## B. Progressive Disclosure

### Core Rule

> **Only pass what matters now; retrieve the rest.**

Do NOT load entire files, full histories, or all documentation. Load the minimum needed for the current task.

### Context Budget Guardrails

| Threshold | Level | Action |
|-----------|-------|--------|
| **< 40%** | Green | Normal operation |
| **40-60%** | Yellow | Warning; consider summarization |
| **60-70%** | Orange | Start offloading to memory files |
| **70%** | Red | HARD STOP; context reset required |

### Actions When Budget Exceeded

**At Yellow (40-60%):**
```yaml
actions:
  - log_warning: "Context at {percentage}%"
  - suggest: "Consider summarizing intermediate results"
  - suggest: "Write findings to memory/current-status.md"
```

**At Orange (60-70%):**
```yaml
actions:
  - update_memory_files: required
  - offload_large_content: to_files
  - compress_mcp_responses: true
  - suggest: "Run /compact after memory update"
```

**At Red (70%+):**
```yaml
actions:
  - stop_current_work: immediate
  - update_memory_files: required
  - produce_context_reset_pack: required
  - options:
      - start_new_task_context: "Fresh session for next task"
      - run_compact_safely: "After confirming memory is current"
      - spawn_sub_agent: "Delegate and import summary only"
```

### Progressive Disclosure Techniques

| Technique | When to Use | How |
|-----------|-------------|-----|
| **Lazy loading** | Large files | Read specific sections, not whole file |
| **Summary import** | Sub-agent results | Import conclusion, not full trace |
| **Reference by path** | Documentation | Point to file, don't inline |
| **Incremental context** | Long tasks | Load step-by-step, not all at once |
| **Memory retrieval** | Cross-session | Read from `memory/` not conversation |

### Sub-Agent Pattern

When spawning sub-agents for parallel work:

```yaml
sub_agent_pattern:
  spawn:
    - give: task_brief (< 500 tokens)
    - give: relevant_memory_refs
    - do_not_give: full_conversation_history

  import_result:
    - take: summary (< 200 tokens)
    - take: artifact_paths
    - do_not_take: full_trace
    - do_not_take: intermediate_steps
```

---

## C. Hooks (Reliability Rituals)

Hooks enforce good habits automatically. They fire at specific lifecycle points.

### Hook Configuration Location

```
.claude/
├── hooks/
│   ├── UserPromptSubmit.md      # Before processing user input
│   ├── Stop.md                  # End of response/turn
│   ├── PreCompact.md            # Before /compact runs
│   └── PermissionRequest.md     # On permission checks
└── settings.yaml                # Hook enablement
```

### UserPromptSubmit Hook

**MUST inject** before processing any user prompt:

```yaml
# .claude/hooks/UserPromptSubmit.md
hook: UserPromptSubmit
trigger: before_processing_prompt
inject:
  memory_pointers:
    - "Read memory/current-status.md for active work"
    - "Check memory/decision-log.md for recent decisions"
    - "Reference memory/project-index.md for file locations"

  current_context:
    - "Current phase: {phase}"
    - "Definition of done: {acceptance_criteria}"
    - "Constraints: {active_constraints}"

  reminders:
    - "Use progressive disclosure: load only what's needed"
    - "Update memory files before session end"
    - "Stay within context budget"
```

**Implementation** (MUST be implemented):

```markdown
# .claude/hooks/UserPromptSubmit.md

Before processing this prompt:

1. **Read current state**:
   - `memory/current-status.md` — What's active, blockers, next steps
   - `memory/decision-log.md` — Recent decisions (last 5 entries)

2. **Current context**:
   - Phase: Check status file
   - Definition of done: Per active task
   - Constraints: Per Concept Lock

3. **Operating rules**:
   - Load only what matters for this prompt
   - Write intermediate results to files, not context
   - Update memory before ending session
```

### Stop Hook (End-of-Turn Ritual)

**MUST enforce** at the end of every response:

```yaml
# .claude/hooks/Stop.md
hook: Stop
trigger: end_of_response
enforce:
  memory_update:
    - update: memory/current-status.md
    - record: decisions_made → memory/decision-log.md
    - record: files_changed → memory/project-index.md

  doc_index_update:
    - if: docs_changed
    - then: update relevant index files

  self_audit_checklist:
    security:
      - "No secrets in output?"
      - "No credentials hardcoded?"
    correctness:
      - "Changes match plan?"
      - "Tests cover new code?"
    consistency:
      - "Naming conventions followed?"
      - "Patterns match existing code?"
```

**Implementation** (MUST be implemented):

```markdown
# .claude/hooks/Stop.md

Before completing this response:

## Memory Update
- [ ] Update `memory/current-status.md` with:
  - Current phase and step
  - Work completed this turn
  - Next steps
  - Any blockers

- [ ] If decisions were made, append to `memory/decision-log.md`:
  - Decision ID
  - What was decided
  - Why (rationale)
  - Alternatives considered

## Quick Self-Audit
- [ ] **Security**: No secrets/credentials in output
- [ ] **Correctness**: Changes align with plan
- [ ] **Consistency**: Follows project patterns
```

### PreCompact Hook

**MUST enforce** before `/compact` executes:

```yaml
# .claude/hooks/PreCompact.md
hook: PreCompact
trigger: before_compact_command
enforce:
  memory_is_current:
    - verify: memory/current-status.md updated within last turn
    - if_stale: update_first

  minimal_state_summary:
    - create: compact_summary.md
    - include: active_task, current_step, key_decisions
    - exclude: full_history, intermediate_steps

  confirmation:
    - confirm: "Memory files are current?"
    - confirm: "Safe to compact conversation?"
```

**Implementation** (MUST be implemented):

```markdown
# .claude/hooks/PreCompact.md

Before running /compact:

## Pre-Compact Checklist
- [ ] `memory/current-status.md` is current (updated this session)
- [ ] `memory/decision-log.md` has all recent decisions
- [ ] No uncommitted important context in conversation

## Compact Summary
Create minimal state summary:
- Active task: {task}
- Current step: {step} of {total}
- Key context: {minimal essential info}

## Confirmation
Only proceed with /compact if memory is fully updated.
If not, update memory first, then compact.
```

### PermissionRequest Hook (Operator Mode)

For Operator Mode with `--dangerously-skip-permissions`:

```yaml
# .claude/hooks/PermissionRequest.md
hook: PermissionRequest
trigger: on_permission_check
mode: operator_mode  # --dangerously-skip-permissions active

behavior:
  bypass_interactive: true  # No approval prompts

  still_enforced:
    - evidence_pack_generation
    - verification_checklist
    - memory_updates
    - audit_logging
    - forbidden_action_blocks

  internal_safety_rails:
    - check: "Action allowed by Itqahn policies?"
    - check: "Evidence will be generated?"
    - check: "Rollback possible?"
    - on_violation: block_and_log
```

**Implementation** (MUST be implemented):

```markdown
# .claude/hooks/PermissionRequest.md

## Operator Mode Configuration

When running with `--dangerously-skip-permissions`:

### Bypassed (for speed)
- Interactive file approval prompts
- Command confirmation dialogs
- Manual review gates

### Still Enforced (Itqahn safety rails)
- Evidence Pack generation (mandatory)
- Verification checklist completion
- Memory file updates
- Audit log entries
- Forbidden action blocks (force push, secret exposure, etc.)

### Internal Check
Before any significant action:
1. Is this action within the current plan scope?
2. Will evidence be generated?
3. Is rollback possible if needed?
4. Does this violate any Itqahn policy?

If any check fails → Block action and log reason.
```

---

## D. Plan Mode Discipline

### Every Task Starts in Plan Mode

```yaml
plan_mode_policy:
  trigger: new_task_start
  mandatory: true
  exit_condition: plan_approved

  iteration_requirement:
    minimum_cycles: 2
    do_not_accept_first_plan: true
```

### Plan Must Include

| Element | Required | Validation |
|---------|----------|------------|
| **Clear requirements** | Yes | No ambiguity, measurable |
| **Identified risks** | Yes | At least considered |
| **Dependencies listed** | Yes | Blocking items identified |
| **Acceptance criteria** | Yes | Testable conditions |
| **File change estimate** | Yes | Which files, what actions |
| **Verification approach** | Yes | How to confirm success |

### Plan Review Checklist

```markdown
# Plan Review Checklist

## Requirements Clarity
- [ ] Requirements are specific and measurable
- [ ] No ambiguous terms ("better", "improved", "nice")
- [ ] Scope is bounded (what's NOT included is clear)

## Risk Assessment
- [ ] Risks identified (even if "none significant")
- [ ] Mitigation for high-likelihood risks
- [ ] Fallback if approach fails

## Dependencies
- [ ] Blocking dependencies listed
- [ ] External dependencies identified
- [ ] Order of operations clear

## Acceptance Criteria
- [ ] Each criterion is testable
- [ ] Success/failure is binary (no "mostly done")
- [ ] Criteria cover all requirements

## Implementation Plan
- [ ] Files to change are listed
- [ ] Actions per file are clear (create/modify/delete)
- [ ] Logical sequence of steps

## Verification Approach
- [ ] How to verify each criterion
- [ ] What tests to run
- [ ] What to check manually
```

### Plan Mode Workflow

```
NEW TASK RECEIVED
       │
       ▼
ENTER PLAN MODE
       │
       ├── 1. Read task requirements
       ├── 2. Read relevant memory files
       ├── 3. Generate initial plan
       │
       ▼
REFINEMENT CYCLE 1
       │
       ├── Review against checklist
       ├── Identify gaps
       ├── Improve plan
       │
       ▼
REFINEMENT CYCLE 2+
       │
       ├── Simplify if possible
       ├── Verify completeness
       ├── Confirm implementable
       │
       ▼
PLAN APPROVED?
       │
       ├── No → Continue refining
       │
       └── Yes
               │
               ├── Save plan artifact
               ├── Update memory/current-status.md
               └── EXIT PLAN MODE → Begin Build
```

---

## E. Slash Commands

### Mandatory Slash Commands

All slash commands live in `.claude/commands/` as markdown files.

| Command | Purpose | Output Location |
|---------|---------|-----------------|
| `/plan` | Create/refine plan with iteration | `plans/run-{id}/{task}.md` |
| `/task` | Create isolated task brief | `tasks/{task-slug}.md` |
| `/commit` | Clean diff → commit message → commit | Git commit |
| `/pr` | Create PR with labels and links | GitHub PR |
| `/verify` | Security + tests + style checks | `evidence/{task}-verification.json` |
| `/catchup` | Read memory → current state summary | Console output |
| `/doc-update` | Update docs + index + cross-links | Modified docs |
| `/end` | Final ritual: memory + next steps | Updated memory files |

### /plan Command

```markdown
# /plan — Create or Refine Implementation Plan

## Behavior
1. If no plan exists:
   - Read task requirements
   - Read relevant memory files
   - Generate initial plan
   - Run Plan Review Checklist
   - Iterate until checklist passes

2. If plan exists:
   - Load existing plan
   - Apply requested changes
   - Re-run checklist
   - Save updated plan

## Output
- Plan artifact: `plans/run-{run_id}/{task_slug}.md`
- Memory update: `memory/current-status.md`

## Exit Condition
Plan passes all checklist items AND operator approves.
```

### /task Command

```markdown
# /task — Create Isolated Task Brief

## Behavior
1. Gather task information:
   - Name and description
   - Scope (what's in, what's out)
   - Dependencies
   - Acceptance criteria

2. Create task brief from template

3. Update memory with new task

## Output
- Task brief: `tasks/{task-slug}.md`
- Memory update: `memory/current-status.md`

## Template
See: templates/operations/task-brief.md
```

### /commit Command

```markdown
# /commit — Clean Commit Workflow

## Behavior
1. Show diff summary (files changed, lines added/removed)
2. Generate commit message from diff:
   - Type: feat/fix/docs/style/refactor/test/chore
   - Scope: affected module
   - Description: what changed
   - Footer: run ID and issue number

3. Confirm message (or allow edit)
4. Execute commit

## Output
- Git commit with conventional format
- Console: commit hash and summary

## Format
```
type(scope): description [run-{id} #{issue}]

- Detail 1
- Detail 2
```
```

### /pr Command

```markdown
# /pr — Create Pull Request

## Prerequisites
- All changes committed
- Verification report exists
- Plan artifact exists

## Behavior
1. Generate PR title: `[{run_id}] {task_name}`
2. Generate PR body from template
3. Add labels: auto-generated, run-{id}
4. Create PR via gh CLI
5. Enable auto-merge (squash)

## Output
- GitHub PR created
- Auto-merge enabled
- Console: PR URL

## Template
See: templates/github/pr-template.md
```

### /verify Command

```markdown
# /verify — Run Verification Checks

## Checks (in order)
1. **Lint**: `npm run lint`
2. **Type check**: `npm run typecheck`
3. **Unit tests**: `npm run test:unit`
4. **Integration tests**: `npm run test:integration`
5. **Security scan**: `npm run security:scan`
6. **Secret scan**: `npm run secrets:scan`
7. **Plan alignment**: Compare implementation to plan

## Output
- Verification report: `evidence/run-{id}/{task}-verification.json`
- Console: Pass/fail summary

## On Failure
- Report which checks failed
- Suggest fixes
- Block PR creation until fixed

## Template
See: templates/operations/verification-checklist.md
```

### /catchup Command

```markdown
# /catchup — Restore Context from Memory

## Behavior
1. Read memory files:
   - `memory/current-status.md`
   - `memory/decision-log.md` (last 10 entries)
   - `memory/project-index.md`

2. Read recent changes:
   - `git log --oneline -10`
   - Recent file modifications

3. Produce current-state summary:
   - Active task and phase
   - Recent decisions
   - Next steps
   - Any blockers

## Output
- Console: Concise current-state summary (< 500 tokens)

## Use When
- Starting new session
- After context reset
- After /compact
- Resuming interrupted work
```

### /doc-update Command

```markdown
# /doc-update — Update Documentation

## Behavior
1. Identify changed files (from git diff or explicit list)
2. For each changed file:
   - Update relevant docs if behavior changed
   - Update API docs if interfaces changed
   - Update README if setup changed

3. Update indexes:
   - `docs/00-overview/` if structure changed
   - Cross-links if references changed

4. Validate:
   - No broken links
   - All referenced files exist

## Output
- Updated documentation files
- Console: List of docs updated
```

### /end Command

```markdown
# /end — End-of-Session Ritual

## Behavior
1. **Memory update**:
   - Update `memory/current-status.md`
   - Append decisions to `memory/decision-log.md`
   - Update `memory/project-index.md` if structure changed

2. **Next steps**:
   - Document what to do next
   - Note any blockers
   - List pending items

3. **Risk scan**:
   - Security: No exposed secrets?
   - Correctness: Implementation matches plan?
   - Consistency: Follows project patterns?

4. **Commit memory changes**:
   - `git add memory/`
   - `git commit -m "chore: update memory files [run-{id}]"`

## Output
- Updated memory files
- Git commit for memory
- Console: Session summary

## MUST Run Before
- Ending a session
- Switching tasks
- Running /compact
```

---

## F. Parallelism (Multi-Terminal + Worktrees)

### Perfect Parallel Workflow

Up to **5 Claude Code terminals** running concurrently, each in its own isolated environment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         MERGE CAPTAIN                                    ││
│  │         (Only one terminal merges to main; others sync through)         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│       ┌──────────────────────────────┼──────────────────────────────────┐   │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │ TERMINAL 1   │             │ TERMINAL 2   │             │ TERMINAL 3   │ │
│  │              │             │              │             │              │ │
│  │ Worktree:    │             │ Worktree:    │             │ Worktree:    │ │
│  │ /wt/auth     │             │ /wt/dash     │             │ /wt/api      │ │
│  │              │             │              │             │              │ │
│  │ Branch:      │             │ Branch:      │             │ Branch:      │ │
│  │ task/auth    │             │ task/dash    │             │ task/api     │ │
│  │              │             │              │             │              │ │
│  │ Owns:        │             │ Owns:        │             │ Owns:        │ │
│  │ src/auth/*   │             │ src/dash/*   │             │ src/api/*    │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       └──────────────────────────────┴──────────────────────────────┘       │
│                                      │                                       │
│                                      ▼                                       │
│                    ┌────────────────────────────────┐                       │
│                    │      STAGING BRANCH            │                       │
│                    │   (integration-{run_id})       │                       │
│                    └────────────────────────────────┘                       │
│                                      │                                       │
│                                      ▼                                       │
│                    ┌────────────────────────────────┐                       │
│                    │           MAIN                 │                       │
│                    │    (via Merge Captain only)    │                       │
│                    └────────────────────────────────┘                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Worktree Requirements

| Requirement | Rule |
|-------------|------|
| **Isolation** | Each terminal MUST work in its own git worktree |
| **Own branch** | Each worktree MUST have its own branch |
| **No sharing** | Terminals MUST NOT edit files in other worktrees |
| **Clean state** | Worktrees created fresh, not reused |

### Branch Naming Convention

```
task/{task-slug}           # Task-scoped branches (short, descriptive)

Examples:
  task/auth-login          # Authentication login feature
  task/dash-charts         # Dashboard charts
  task/api-users           # API user endpoints

Integration branch:
  integration-{run_id}     # Staging branch for current run
```

### Merge Captain Rule

**Only ONE terminal acts as Merge Captain:**

| Role | Responsibility |
|------|----------------|
| **Merge Captain** | Merges to main, manages integration branch |
| **Other terminals** | Push to own branch, sync through integration |

```yaml
merge_captain_protocol:
  designation: first_terminal_or_coordinator

  captain_actions:
    - merge: integration → main (when ready)
    - resolve: complex conflicts
    - gate: final verification before main

  other_terminal_actions:
    - push: to own task branch
    - merge: own branch → integration (small PRs)
    - sync: pull from integration frequently
    - never: push directly to main
```

### File Ownership Protocol

**Claim files to prevent conflicts:**

```markdown
# memory/file-claims.md

## Active Claims

| File/Directory | Claimed By | Since | Until |
|----------------|------------|-------|-------|
| src/auth/* | Terminal 1 | 2026-01-08T10:00 | Task complete |
| src/dashboard/* | Terminal 2 | 2026-01-08T10:00 | Task complete |
| src/api/users.ts | Terminal 3 | 2026-01-08T10:00 | Task complete |
| package.json | Merge Captain | Always | Always |

## Claim Rules
1. Check claims before editing a file
2. If claimed by another, coordinate or wait
3. Release claim when task complete
4. Shared files (package.json, etc.) → Merge Captain only
```

### Lock-Step Points

Terminals MUST pause and integrate at defined sync points:

| Sync Point | When | Action |
|------------|------|--------|
| **End of phase** | Plan→Build transition | All terminals sync to integration |
| **Shared file change** | package.json, schema | Pause all, apply change, sync all |
| **Conflict detected** | CI fails on integration | All pause, resolve, then continue |
| **Verification** | Before merge to main | All tasks verified |

### Merging Strategy

```yaml
merge_strategy:
  pr_size: small  # Integrate frequently, not giant PRs
  frequency: after_each_logical_unit  # Don't accumulate changes

  flow:
    1_terminal_completes_unit:
      - run: /verify
      - run: /commit
      - run: /pr (to integration branch)

    2_merge_to_integration:
      - trigger: PR checks pass
      - method: squash_merge
      - then: sync_other_terminals

    3_merge_to_main:
      - trigger: all_tasks_complete OR milestone_reached
      - actor: merge_captain_only
      - prerequisite: full_verification_pass
```

### Conflict Prevention Rules

| Rule | Enforcement |
|------|-------------|
| **File ownership** | Check `memory/file-claims.md` before editing |
| **Hot file protection** | Shared files edited only by Merge Captain |
| **Early detection** | Run `git fetch && git diff origin/integration` frequently |
| **Small changes** | Commit and push often to surface conflicts early |

### Edge Case Handling

#### Two Terminals Changed Same File

```
CONFLICT DETECTED
       │
       ▼
1. IDENTIFY CONFLICT TYPE
   ├── Non-overlapping changes → Auto-merge possible
   └── Overlapping changes → Manual resolution needed
       │
       ▼
2. RESOLUTION PROTOCOL
   ├── Earlier commit wins (by timestamp)
   ├── Later terminal rebases on earlier
   ├── If semantic conflict → Merge Captain decides
   └── Both terminals pause until resolved
       │
       ▼
3. POST-RESOLUTION
   ├── Update file-claims.md to prevent recurrence
   ├── Sync all terminals from integration
   └── Continue work
```

#### Broken Build After Merge

```
CI FAILS ON INTEGRATION
       │
       ▼
1. ALL TERMINALS PAUSE
       │
       ▼
2. IDENTIFY CAUSE
   ├── Which commit broke it?
   └── Which terminal?
       │
       ▼
3. FIX PROTOCOL
   ├── Responsible terminal fixes
   ├── If unclear → Merge Captain investigates
   └── Revert if fix not quick
       │
       ▼
4. RESUME
   ├── CI passes
   ├── All terminals sync
   └── Continue work
```

#### Partial Features Across Branches

```
FEATURE SPANS MULTIPLE TERMINALS
       │
       ▼
1. COORDINATE UPFRONT
   ├── Define interface contracts first
   ├── Each terminal owns its part
   └── Integration tests in separate task
       │
       ▼
2. MERGE ORDER
   ├── Core/shared code first
   ├── Dependent code after
   └── Integration tests last
       │
       ▼
3. VERIFICATION
   ├── Each part passes its tests
   └── Integration tests pass after all merged
```

#### Terminal Goes Off-Plan (Drift)

```
DRIFT DETECTED
       │
       ├── Drift score > 30%
       └── Unplanned files modified
       │
       ▼
1. PAUSE TERMINAL
       │
       ▼
2. ASSESS
   ├── Is drift justified?
   ├── Should plan be updated?
   └── Should work be discarded?
       │
       ▼
3. RESOLUTION
   ├── Update plan → Continue with updated plan
   ├── Revert drift → Continue with original plan
   └── New task → Split off drifted work
```

### Parallel Safety Checklist

```markdown
# Parallel Safety Checklist

## Before Starting Parallel Work
- [ ] File claims documented in `memory/file-claims.md`
- [ ] Merge Captain designated
- [ ] Integration branch created
- [ ] Sync points defined

## During Parallel Work
- [ ] Each terminal in own worktree
- [ ] Each terminal on own branch
- [ ] No editing files claimed by others
- [ ] Frequent commits (< 1 hour gaps)
- [ ] Frequent sync with integration

## Before Merging to Integration
- [ ] /verify passes
- [ ] No uncommitted changes
- [ ] Branch rebased on integration
- [ ] File claims still valid

## Before Merging to Main
- [ ] All tasks complete or at milestone
- [ ] All terminals synced
- [ ] Integration branch CI passes
- [ ] Merge Captain approves
```

### Conflict Resolution Runbook

```markdown
# Conflict Resolution Runbook

## Step 1: Identify Conflict
```bash
git fetch origin
git diff origin/integration
```

## Step 2: Determine Conflict Type

| Type | Symptoms | Resolution |
|------|----------|------------|
| **Textual** | Same lines changed | Manual merge |
| **Semantic** | Different changes, same effect | Choose one |
| **Structural** | File moved/renamed | Coordinate |
| **Dependency** | Package conflicts | Merge Captain |

## Step 3: Resolution Protocol

### Textual Conflict
1. Fetch latest integration
2. Rebase your branch
3. Resolve conflicts in editor
4. Run tests
5. Push rebased branch

### Semantic Conflict
1. Both terminals pause
2. Compare implementations
3. Choose better approach
4. Other terminal adopts
5. Both sync and continue

### Structural Conflict
1. All terminals pause
2. Agree on final structure
3. Merge Captain applies
4. All terminals sync

### Dependency Conflict
1. Merge Captain takes over package.json
2. All terminals pause
3. Captain resolves and pushes
4. All terminals sync
```

---

## G. End-of-Session Verification

### Verification Ritual (Mandatory)

Every session MUST end with verification. No exceptions.

```
SESSION ENDING
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VERIFICATION RITUAL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CODE QUALITY                                                             │
│     [ ] Lint passes (0 errors)                                               │
│     [ ] Type check passes (0 errors)                                         │
│     [ ] Tests pass (unit + integration)                                      │
│     [ ] Coverage not decreased                                               │
│                                                                              │
│  2. SECURITY HYGIENE                                                         │
│     [ ] Security scan passes (0 critical/high)                               │
│     [ ] Secret scan passes (0 detected)                                      │
│     [ ] No credentials in code/logs/output                                   │
│     [ ] No sensitive data exposed                                            │
│                                                                              │
│  3. CONSISTENCY                                                              │
│     [ ] Implementation matches plan                                          │
│     [ ] Naming conventions followed                                          │
│     [ ] Patterns match existing code                                         │
│     [ ] No unplanned changes                                                 │
│                                                                              │
│  4. PERFORMANCE                                                              │
│     [ ] No obvious performance regressions                                   │
│     [ ] No N+1 queries introduced                                            │
│     [ ] No blocking calls in async code                                      │
│                                                                              │
│  5. DOCUMENTATION                                                            │
│     [ ] Changed behavior documented                                          │
│     [ ] API changes in API docs                                              │
│     [ ] Memory files updated                                                 │
│                                                                              │
│  6. MEMORY UPDATE                                                            │
│     [ ] current-status.md is current                                         │
│     [ ] decision-log.md has new decisions                                    │
│     [ ] project-index.md reflects structure                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
ALL PASS? ─── No ──→ Fix issues, re-verify
       │
      Yes
       │
       ▼
SESSION COMPLETE (valid)
```

### Quick Self-Audit Questions

Ask yourself before ending:

1. **Security**: "Could this expose secrets or credentials?"
2. **Correctness**: "Does this do what the plan says?"
3. **Consistency**: "Does this match how we do things elsewhere?"
4. **Completeness**: "Is anything half-done that shouldn't be?"
5. **Memory**: "Will I (or next session) know what happened?"

### Verification Report Schema

```json
{
  "verification": {
    "timestamp": "2026-01-08T14:30:00Z",
    "session_id": "session-xyz",
    "run_id": "run-01J5ABCD",
    "task": "user-auth",

    "code_quality": {
      "lint": {"status": "pass", "errors": 0},
      "typecheck": {"status": "pass", "errors": 0},
      "tests": {"status": "pass", "passed": 42, "failed": 0},
      "coverage": {"current": 87.3, "delta": +2.1}
    },

    "security": {
      "scan": {"status": "pass", "critical": 0, "high": 0},
      "secrets": {"status": "pass", "detected": 0},
      "manual_check": "confirmed_no_credentials"
    },

    "consistency": {
      "plan_alignment": {"status": "pass", "drift": 0.05},
      "conventions": "followed",
      "patterns": "matched"
    },

    "memory_updated": {
      "current_status": true,
      "decision_log": true,
      "project_index": false  // No structural changes
    },

    "overall": "pass"
  }
}
```

---

## H. Tooling Discipline: Skills vs MCPs

### Core Policy

> **Prefer local operations (Skills) over MCP calls.**

MCPs add tool definitions to context, increasing token usage and reducing reliability.

### When to Use What

| Approach | Token Cost | Use When |
|----------|------------|----------|
| **Skill** (local) | Low | Can accomplish with code/files/CLI |
| **MCP** (external) | High | Must access external system |

### Decision Matrix

| Task | Use | Why |
|------|-----|-----|
| Read file | Skill | Direct file access |
| Write file | Skill | Direct file access |
| Search code | Skill | grep/ripgrep locally |
| Run tests | Skill | Local CLI |
| Run linter | Skill | Local CLI |
| Generate code | Skill | Internal capability |
| Parse JSON/YAML | Skill | Internal capability |
| Create GitHub issue | MCP | External API required |
| Create GitHub PR | MCP | External API required |
| Read Figma design | MCP | External API required |
| Query database | MCP | External system |
| Send notification | MCP | External service |

### MCP Downsides

| Issue | Impact |
|-------|--------|
| **Context bloat** | Tool definitions consume tokens |
| **Reliability decrease** | More tools = more failure modes |
| **Latency increase** | External calls are slower |
| **Rate limits** | External APIs have quotas |

### MCP Usage Rubric

**Before using MCP, ask:**

1. Can I accomplish this with local files/code? → Use Skill
2. Can I use CLI tools instead? → Use Skill
3. Do I absolutely need external data? → Use MCP
4. Can I cache the MCP result? → Cache it
5. Can I summarize the MCP response? → Summarize it

**When using MCP:**

```yaml
mcp_usage_protocol:
  before_call:
    - verify: skill_cannot_accomplish
    - check: context_budget_allows

  during_call:
    - request: only_needed_fields
    - avoid: full_object_dumps

  after_call:
    - summarize: compress_to_essentials
    - cache: if_reusable
    - store: large_responses_to_files
```

### MCP Response Handling

```yaml
mcp_response_handling:
  small_response: # < 500 tokens
    action: use_directly

  medium_response: # 500-2000 tokens
    action: summarize_before_using

  large_response: # > 2000 tokens
    action: write_to_file_and_reference

  reusable_response:
    action: cache_for_session
    ttl: 15_minutes
```

---

## I. Context Rot and Recovery

### Symptoms of Context Rot

| Symptom | Description | Severity |
|---------|-------------|----------|
| **Hallucination** | References non-existent files/functions | High |
| **Tool avoidance** | Refuses to use available tools | Medium |
| **Inconsistency** | Contradicts earlier statements | Medium |
| **Repetition** | Repeats same content multiple times | Medium |
| **Confusion** | Asks questions already answered | Low |
| **Slowdown** | Responses become slower/shorter | Low |

### Recovery Actions

#### Level 1: Reduce Context

```yaml
action: reduce_context
when: early_symptoms
steps:
  - remove: large_file_contents_from_conversation
  - remove: old_intermediate_steps
  - keep: final_results_and_decisions
  - use: file_references_not_inline_content
```

#### Level 2: Remove Distractors

```yaml
action: remove_distractors
when: medium_symptoms
steps:
  - identify: content_not_relevant_to_current_task
  - remove: that_content
  - focus: only_current_task_context
  - update: memory_files_with_removed_context
```

#### Level 3: Rely on Memory

```yaml
action: rely_on_memory
when: significant_symptoms
steps:
  - update: all_memory_files_to_current
  - state: "I will now rely on memory files"
  - read: memory/current-status.md
  - read: memory/decision-log.md (recent)
  - continue: with_fresh_context_from_memory
```

#### Level 4: Safe Compact

```yaml
action: safe_compact
when: serious_symptoms
prerequisite: memory_files_are_current
steps:
  - verify: memory/current-status.md is updated
  - verify: memory/decision-log.md is updated
  - run: /compact
  - then: /catchup to restore essential context
```

#### Level 5: Hard Reset

```yaml
action: hard_reset
when: severe_symptoms_or_unrecoverable
steps:
  - update: all_memory_files
  - document: current_state_thoroughly
  - commit: memory_changes
  - end: current_session
  - start: fresh_session
  - run: /catchup in new session
```

### Hard Reset Procedure

When a task needs fresh start without losing decisions:

```markdown
# Hard Reset Procedure

## 1. Preserve State (Before Reset)
- [ ] Update `memory/current-status.md` with:
  - What was being attempted
  - Where it went wrong
  - What's still valid
- [ ] Update `memory/decision-log.md` with all decisions
- [ ] Commit memory changes: `git add memory/ && git commit -m "chore: pre-reset memory update"`

## 2. Document Recovery Context
Create `memory/reset-context-{timestamp}.md`:
```markdown
# Reset Context

## Task
{task name and description}

## State at Reset
- Phase: {phase}
- Step: {step}
- Issue: {what went wrong}

## Valid Work to Preserve
- {list of valid completed work}

## Decisions to Carry Forward
- {key decisions from decision-log}

## Approach for Fresh Start
- {recommended approach}
```

## 3. Execute Reset
- [ ] End current session
- [ ] Start new session
- [ ] Run `/catchup`
- [ ] Read reset context file
- [ ] Continue from last good state

## 4. Cleanup (After Successful Recovery)
- [ ] Archive reset context file
- [ ] Update memory with recovery outcome
```

### Prevention Strategies

| Strategy | How |
|----------|-----|
| **Progressive disclosure** | Load only what's needed |
| **Regular memory updates** | Keep memory current |
| **Small task scopes** | Don't let tasks grow too large |
| **Frequent commits** | Checkpoint progress often |
| **Context monitoring** | Watch for budget warnings |

---

## J. Dashboard Alignment

### Operator Controls

The Itqahn dashboard MUST expose these controls for the context engineering workflow:

#### Start Run

```yaml
control: start_run
behavior:
  - enter: plan_mode
  - iterate: plan_until_approved
  - then: execute_plan
  - parallel: up_to_5_terminals

display:
  - plan_status: draft/reviewing/approved
  - iteration_count: N
  - checklist_status: items_passed/total
```

#### Active Terminals View

```yaml
control: active_terminals
display:
  - terminal_count: N of 5
  - per_terminal:
      - id: terminal_1
      - worktree: /wt/auth
      - branch: task/auth-login
      - status: building/verifying/waiting
      - current_task: "Implementing login form"
      - file_claims: [src/auth/*]
      - last_activity: 2 min ago

  - merge_captain: terminal_1
  - integration_branch: integration-run-01J5ABCD
```

#### Pause & Review

```yaml
control: pause_and_review
behavior:
  - pause: all_active_terminals
  - trigger: plan_review_checklist
  - trigger: drift_scan_all_terminals

display:
  - review_panel:
      - plan_checklist_status
      - drift_scores_per_terminal
      - file_ownership_conflicts
      - recommended_actions

actions:
  - resume_all: continue_after_review
  - resume_selected: continue_specific_terminals
  - stop_drifted: halt_terminals_with_high_drift
```

#### Verify & Merge

```yaml
control: verify_and_merge
behavior:
  - run: /verify on all terminals
  - aggregate: verification_results
  - if_all_pass: enable_merge_button
  - merge: via_merge_captain

display:
  - verification_summary:
      - lint: pass/fail
      - tests: N passed, M failed
      - security: issues_count
      - plan_alignment: drift_score

  - merge_readiness: ready/blocked
  - blocking_issues: [list if any]

actions:
  - merge_to_integration: if_verified
  - merge_to_main: if_all_complete_and_verified
```

#### Compact Safely

```yaml
control: compact_safely
behavior:
  - verify: memory_files_are_current
  - if_stale: prompt_to_update_first
  - run: PreCompact_hook
  - then: /compact

display:
  - memory_freshness:
      - current_status: updated_X_min_ago
      - decision_log: updated_X_min_ago
      - project_index: updated_X_min_ago

  - compact_readiness: ready/need_memory_update

actions:
  - update_then_compact: if_memory_stale
  - compact_now: if_memory_current
```

#### Context Budget Monitor

```yaml
control: context_budget
display:
  - per_terminal:
      - id: terminal_1
      - usage: 45%
      - status: green/yellow/orange/red
      - trend: increasing/stable/decreasing

  - alerts:
      - terminal_2: "Approaching limit (65%)"
      - terminal_4: "OVER LIMIT - reset required"

actions:
  - suggest_compact: for_yellow_terminals
  - force_reset: for_red_terminals
  - view_usage_breakdown: per_terminal
```

### Dashboard Behaviors Summary

| Control | Primary Action | Guard Rails |
|---------|---------------|-------------|
| **Start Run** | Plan Mode → Execute | Plan must be approved |
| **Active Terminals** | Monitor status | Show file ownership |
| **Pause & Review** | Force plan review | Drift scan required |
| **Verify & Merge** | Run checks → merge | All checks must pass |
| **Compact Safely** | Memory → compact | Memory must be current |
| **Context Budget** | Monitor usage | Alert on thresholds |

---

## Related Documents

- `docs/06-operations/claude-code-operating-model.md` — Base operating model
- `docs/07-integrations/git-integration.md` — Git workflow and worktrees
- `docs/08-agents/agent-system-contract.md` — Agent contract rules
- `docs/07-integrations/mcp/mcp-overview.md` — MCP usage policy
- `docs/03-platform/track-assurance.md` — Drift detection
- `docs/00-overview/principles.md` — Core principles
- `CLAUDE.md` — Root rules file
- `.claude/hooks/` — Hook configurations
- `.claude/commands/` — Slash commands
- `templates/operations/` — Operation templates

---

**Version**: 1.0.0 | **Date**: 2026-01-08
