# Claude Code Operating Model

Itqahn executes all agent work through **Claude Code** sessions running in **Operator Mode**. This document defines the canonical operating model for parallel execution, context management, and session discipline.

---

## Goals & Non-Goals

### Goals

| Goal | Description |
|------|-------------|
| **Dashboard-driven execution** | User clicks "Start Run" in portal; no terminal interaction required |
| **Parallel throughput** | Default 5 concurrent Claude Code workers via Git worktrees |
| **Predictable quality** | Plan→Build→Verify discipline enforced on every run |
| **Context efficiency** | Progressive disclosure keeps context usage below 70% |
| **Full traceability** | Every action produces artifacts; every decision is logged |
| **Automatic Git workflow** | Issues, branches, PRs, merges handled by Itqahn—user never touches Git |

### Non-Goals

| Non-Goal | Why |
|----------|-----|
| User manually creates issues/branches/PRs | Automation-first; manual Git creates audit gaps |
| User interacts with terminal | Dashboard is the only interface |
| Single-threaded execution | Parallelism via worktrees is default |
| Unbounded context usage | Hard limit at 70% prevents degradation |
| Free-form agent communication | All communication via structured artifacts |

---

## Glossary (Operating Model Terms)

| Term | Definition |
|------|------------|
| **Plan Mode** | Initial phase where Claude Code produces a structured Plan artifact before any code is written. Minimum 2 refinement cycles unless plan is trivially complete. |
| **Verification Pass** | Mandatory end-of-session step running lint, tests, security checks, and repo rule validation. Produces Verification Report artifact. |
| **Worktree** | An independent Git working directory sharing the same repository. Enables parallel work on different branches without conflicts. |
| **Worktree Worker** | A Claude Code session running in an isolated worktree with its own branch. Workers do not share working directories. |
| **Session Budget** | Maximum tokens and cost allowed for a single Claude Code session. Enforced by circuit breakers. |
| **Context Budget** | Maximum percentage (70%) of Claude Code's context window that may be used before triggering Context Reset. |
| **Skill** | An internal, standardized procedure executed by Claude Code without external tool calls. Token-efficient and deterministic. |
| **MCP** | Model Context Protocol server providing external tool/data access. Context-expensive; use only when necessary. |
| **Coordinator** | The orchestration layer that spawns workers, aggregates results, resolves conflicts, and manages merges. |
| **Catch-up Pack** | A compressed summary artifact enabling context restoration after reset or session handoff. |
| **Context Reset Pack** | Artifact produced when context budget is exceeded. Contains state snapshot, pending work, and resume instructions. |

---

## Dashboard-First Journey

### User Experience

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPERATOR MODE DASHBOARD JOURNEY                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. USER CLICKS "START RUN"                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  • Selects project and scope (from Concept Lock)                        ││
│  │  • Confirms budget and timeout limits                                   ││
│  │  • Clicks "Start" — that's it                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  2. ITQAHN SPAWNS COORDINATOR                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Behind the scenes:                                                      ││
│  │  • Creates Run record with unique Run ID                                 ││
│  │  • Creates Epic Issue in GitHub                                          ││
│  │  • Analyzes scope for parallelization                                    ││
│  │  • Determines task dependencies                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  3. COORDINATOR SPAWNS WORKERS (up to 5)                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  For each parallelizable task:                                          ││
│  │  • Creates Work Item Issue                                               ││
│  │  • Creates Git worktree + branch                                         ││
│  │  • Spawns Claude Code session with `--dangerously-skip-permissions`     ││
│  │  • Injects CLAUDE.md rules                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  4. USER WATCHES DASHBOARD                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Dashboard shows:                                                        ││
│  │  • Active workers and their status                                       ││
│  │  • Current phase (Plan → Build → Verify)                                ││
│  │  • File locks held                                                       ││
│  │  • Merge queue position                                                  ││
│  │  • Cost accumulation                                                     ││
│  │  • [Kill Switch] for emergency stop                                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  5. WORKERS COMPLETE → PRs MERGE → RUN FINISHES                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  • All PRs auto-merge via merge queue                                    ││
│  │  • Evidence Pack generated                                               ││
│  │  • Run Summary written to repo                                           ││
│  │  • User sees "Run Complete" with links to artifacts                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What the User Does NOT Do

| Action | Who Does It | Why Not User |
|--------|-------------|--------------|
| Open terminal | Nobody | Dashboard-only interface |
| Create Git branch | Coordinator | Naming conventions enforced |
| Create GitHub issue | Coordinator | Linking and labels automated |
| Create PR | Worker | Template auto-populated |
| Click merge | Auto-merge | Checks gate everything |
| Review code | Verification Pass | Automated quality gates |
| Run tests manually | CI | Triggered by PR |

---

## Parallel Execution Model

### Default Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Max parallel workers** | 5 | Balance throughput vs. conflict risk |
| **Workers per project** | 3 | Prevent file contention |
| **Worker timeout** | 4 hours | Prevent resource leaks |
| **Model** | Claude Opus 4.5 | Best quality for all tasks |

### Worker Isolation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORKER ISOLATION ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         COORDINATOR                                    │  │
│  │  • Spawns workers        • Manages locks      • Aggregates results    │  │
│  │  • Resolves conflicts    • Triggers merges    • Writes final summary  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│       ┌──────────────────────────────┼──────────────────────────────┐       │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │  WORKER #1   │             │  WORKER #2   │             │  WORKER #3   │ │
│  ├──────────────┤             ├──────────────┤             ├──────────────┤ │
│  │ Worktree:    │             │ Worktree:    │             │ Worktree:    │ │
│  │ /wt/run-A-1  │             │ /wt/run-A-2  │             │ /wt/run-A-3  │ │
│  │              │             │              │             │              │ │
│  │ Branch:      │             │ Branch:      │             │ Branch:      │ │
│  │ feat/run-A   │             │ feat/run-A   │             │ feat/run-A   │ │
│  │ -user-auth   │             │ -dashboard   │             │ -settings    │ │
│  │              │             │              │             │              │ │
│  │ Claude Code  │             │ Claude Code  │             │ Claude Code  │ │
│  │ Session      │             │ Session      │             │ Session      │ │
│  │              │             │              │             │              │ │
│  │ Context:     │             │ Context:     │             │ Context:     │ │
│  │ ISOLATED     │             │ ISOLATED     │             │ ISOLATED     │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       │         NO SHARED CONTEXT OR WORKING DIRECTORY              │       │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │    PR #1     │             │    PR #2     │             │    PR #3     │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       └──────────────────────────────┼──────────────────────────────┘       │
│                                      ▼                                       │
│                        ┌──────────────────────────┐                         │
│                        │      MERGE QUEUE         │                         │
│                        │   (Coordinator manages)  │                         │
│                        └──────────────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Worktree Naming Convention

| Entity | Pattern | Example |
|--------|---------|---------|
| **Worktree directory** | `/worktrees/run-{run_id}-{task_slug}` | `/worktrees/run-01J5ABCD-user-auth` |
| **Branch** | `feat/run-{run_id}-{task_slug}` | `feat/run-01J5ABCD-user-auth` |
| **PR title** | `[{run_id}] {task_name}` | `[run-01J5ABCD] User Authentication` |
| **Work Item Issue** | `[{run_id}] {journey_name}` | `[run-01J5ABCD] User can authenticate` |

### Worker Lifecycle

```
1. COORDINATOR CREATES WORKER
   │
   ├── git worktree add /worktrees/run-{id}-{task} -b feat/run-{id}-{task}
   ├── Create Work Item Issue in GitHub
   └── Spawn Claude Code: claude --dangerously-skip-permissions
       │
       ▼
2. WORKER ENTERS PLAN MODE
   │
   ├── Load CLAUDE.md rules
   ├── Read task context (Concept Lock, PRD section)
   ├── Generate Plan artifact
   ├── Refine plan (minimum 2 cycles)
   └── Save Plan to repo: plans/run-{id}/{task}.md
       │
       ▼
3. WORKER EXECUTES BUILD
   │
   ├── Implement per plan
   ├── Commit with message: type(scope): desc [run-{id} #{issue}]
   ├── Request file locks if needed
   └── Stay within session budget
       │
       ▼
4. WORKER RUNS VERIFICATION
   │
   ├── Run lint, tests, security scans
   ├── Check repo rules compliance
   ├── Generate Verification Report
   └── Save report: evidence/run-{id}/{task}-verification.json
       │
       ▼
5. WORKER CREATES PR
   │
   ├── gh pr create --title "[{run_id}] {task}" --body "..."
   ├── Enable auto-merge
   └── Notify Coordinator
       │
       ▼
6. COORDINATOR MANAGES MERGE
   │
   ├── Monitor merge queue
   ├── Resolve conflicts if needed
   └── Clean up worktree after merge
```

---

## Git Workflow Automation

### Principle: No User Git Actions

All Git operations are performed by Itqahn. Users MUST NOT:
- Create branches manually
- Create issues manually
- Create PRs manually
- Merge PRs manually
- Push commits manually
- Create tags manually

### Automated Git Operations

| Operation | Triggered By | Naming Convention |
|-----------|--------------|-------------------|
| **Create Epic Issue** | Run start | `[{run_id}] {project_name} - MVP` |
| **Create Work Item Issue** | Task assignment | `[{run_id}] {journey_name}` |
| **Create branch** | Worker spawn | `feat/run-{run_id}-{task_slug}` |
| **Commit** | Worker build | `type(scope): desc [run-{id} #{issue}]` |
| **Create PR** | Build complete | `[{run_id}] {task_name}` |
| **Merge PR** | Auto-merge when checks pass | Squash merge |
| **Create tag** | Release | `v{major}.{minor}.{patch}` |
| **Create release** | All tasks complete | Auto-generated changelog |

### Required Checks Before Merge

All PRs MUST pass these checks before auto-merge:

| Check | Tool | Blocking |
|-------|------|----------|
| **Lint** | ESLint, Prettier | Yes |
| **Type check** | TypeScript | Yes |
| **Unit tests** | Jest/Vitest | Yes |
| **Integration tests** | Playwright | Yes (when applicable) |
| **Security scan** | Semgrep, Gitleaks | Yes |
| **Design Jail** | Custom | Yes (UI changes) |
| **Policy check** | OPA | Yes |
| **Verification Report** | Worker | Yes |
| **Evidence Pack** | CI | Yes |

### Definition of "Done"

A task is done when:
1. All code committed with proper message format
2. PR created with auto-merge enabled
3. All required checks pass
4. PR merged via merge queue
5. Worktree cleaned up
6. Work Item Issue closed
7. Evidence Pack includes task artifacts

---

## Plan Mode Discipline

### Mandatory Plan Phase

Every Claude Code session MUST start in Plan Mode:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLAN MODE DISCIPLINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. ENTER PLAN MODE                                                         │
│     • Read task scope from Concept Lock                                      │
│     • Read relevant PRD sections                                             │
│     • Identify affected files and systems                                    │
│                                                                              │
│  2. GENERATE INITIAL PLAN                                                   │
│     • List concrete implementation steps                                     │
│     • Identify dependencies and risks                                        │
│     • Estimate file changes                                                  │
│                                                                              │
│  3. REFINEMENT CYCLE (minimum 2x)                                           │
│     Cycle 1:                                                                 │
│     • Review plan for completeness                                           │
│     • Check for missing edge cases                                           │
│     • Verify alignment with Concept Lock                                     │
│                                                                              │
│     Cycle 2:                                                                 │
│     • Simplify if possible                                                   │
│     • Remove unnecessary steps                                               │
│     • Confirm plan is implementable                                          │
│                                                                              │
│  4. SAVE PLAN ARTIFACT                                                      │
│     Location: plans/run-{run_id}/{task_slug}.md                             │
│     Format: Structured markdown per template                                 │
│                                                                              │
│  5. EXIT PLAN MODE → BEGIN BUILD                                            │
│     Only proceed when plan is complete and saved                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Plan Artifact Format

```markdown
# Plan: {task_name}

## Context
- Run ID: {run_id}
- Issue: #{issue_number}
- Concept Lock: v{version}
- Design OS: v{version}

## Scope
{Brief description of what will be built}

## Implementation Steps

### Step 1: {step_name}
- Files: {list of files}
- Action: {create/modify/delete}
- Dependencies: {any prerequisites}

### Step 2: {step_name}
...

## File Change Summary
| File | Action | Reason |
|------|--------|--------|
| src/auth/login.ts | Create | New login component |
| src/auth/index.ts | Modify | Export new component |

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ... | ... | ... |

## Verification Criteria
- [ ] All new code has tests
- [ ] No lint errors
- [ ] No type errors
- [ ] Security scan passes
- [ ] Design tokens used (no raw CSS)

## Plan Status
- [x] Initial plan complete
- [x] Refinement cycle 1 complete
- [x] Refinement cycle 2 complete
- [ ] Ready for implementation
```

### Plan Artifact Location

```
plans/
├── run-{run_id}/
│   ├── coordinator-summary.md      # Coordinator's overall plan
│   ├── user-auth.md                # Worker 1's plan
│   ├── dashboard.md                # Worker 2's plan
│   └── settings.md                 # Worker 3's plan
```

### Clarifying Questions Policy

Workers SHOULD NOT ask clarifying questions except when:
1. The question is truly blocking (cannot proceed safely without answer)
2. Multiple valid interpretations exist with significantly different implementations
3. Security or compliance implications require explicit approval

When in doubt, workers MUST:
- Make the safest assumption
- Document the assumption in the Plan artifact
- Proceed with implementation
- Flag for post-hoc review

---

## Verification Discipline

### Mandatory Verification Pass

Every worker MUST run a Verification Pass before creating a PR:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VERIFICATION PASS CHECKLIST                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [ ] LINT CHECK                                                              │
│      Command: npm run lint                                                   │
│      Pass criteria: 0 errors                                                 │
│                                                                              │
│  [ ] TYPE CHECK                                                              │
│      Command: npm run typecheck                                              │
│      Pass criteria: 0 errors                                                 │
│                                                                              │
│  [ ] UNIT TESTS                                                              │
│      Command: npm run test:unit                                              │
│      Pass criteria: All pass, coverage >= threshold                          │
│                                                                              │
│  [ ] INTEGRATION TESTS                                                       │
│      Command: npm run test:integration                                       │
│      Pass criteria: All pass                                                 │
│                                                                              │
│  [ ] SECURITY SCAN                                                           │
│      Command: npm run security:scan                                          │
│      Pass criteria: 0 critical, 0 high                                       │
│                                                                              │
│  [ ] SECRET SCAN                                                             │
│      Command: npm run secrets:scan                                           │
│      Pass criteria: 0 detected                                               │
│                                                                              │
│  [ ] DOCS BUILD                                                              │
│      Command: npm run docs:build                                             │
│      Pass criteria: Build succeeds                                           │
│                                                                              │
│  [ ] REPO RULES CHECK                                                        │
│      - Commit messages follow convention                                     │
│      - Required files present                                                │
│      - No forbidden patterns                                                 │
│      Pass criteria: All rules satisfied                                      │
│                                                                              │
│  [ ] PLAN ALIGNMENT CHECK                                                    │
│      - Implementation matches plan                                           │
│      - No unplanned changes                                                  │
│      - All planned steps completed                                           │
│      Pass criteria: Zero drift                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Verification Report Artifact

```json
{
  "verification_report": {
    "run_id": "run-01J5ABCD",
    "task_slug": "user-auth",
    "worker_id": "worker-1",
    "timestamp": "2026-01-08T12:00:00Z",

    "checks": {
      "lint": {
        "status": "pass",
        "errors": 0,
        "warnings": 2
      },
      "typecheck": {
        "status": "pass",
        "errors": 0
      },
      "unit_tests": {
        "status": "pass",
        "total": 42,
        "passed": 42,
        "failed": 0,
        "coverage": 87.3
      },
      "integration_tests": {
        "status": "pass",
        "total": 8,
        "passed": 8,
        "failed": 0
      },
      "security_scan": {
        "status": "pass",
        "critical": 0,
        "high": 0,
        "medium": 1,
        "low": 3
      },
      "secret_scan": {
        "status": "pass",
        "detected": 0
      },
      "repo_rules": {
        "status": "pass",
        "violations": []
      },
      "plan_alignment": {
        "status": "pass",
        "drift_score": 0.05,
        "unplanned_changes": []
      }
    },

    "overall_status": "pass",
    "ready_for_pr": true
  }
}
```

### Verification Report Location

```
evidence/
├── run-{run_id}/
│   ├── user-auth-verification.json
│   ├── dashboard-verification.json
│   ├── settings-verification.json
│   └── run-summary.json           # Coordinator's aggregated summary
```

---

## Progressive Disclosure & Context Hygiene

### Context Budget Rules

| Threshold | Action |
|-----------|--------|
| **< 50%** | Normal operation |
| **50-70%** | Warning logged; consider summarization |
| **70%** | HARD STOP; produce Context Reset Pack |
| **> 70%** | FORBIDDEN; session must be reset |

### Context Hygiene Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONTEXT HYGIENE RULES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. LOAD ONLY WHAT'S NEEDED                                                 │
│     ✓ Read relevant PRD section, not entire PRD                              │
│     ✓ Read affected files, not entire codebase                               │
│     ✓ Load current task context, not all task history                        │
│                                                                              │
│  2. WRITE TO REPO, NOT CONTEXT                                              │
│     ✓ Decisions → decision-log.md                                            │
│     ✓ Plans → plans/{task}.md                                                │
│     ✓ Notes → notes/{task}.md                                                │
│     ✓ Verification → verification-report.json                                │
│                                                                              │
│  3. SUMMARIZE BEFORE LOADING                                                │
│     ✓ Use Catch-up Pack instead of full history                              │
│     ✓ Summarize file contents when possible                                  │
│     ✓ Reference files by path, don't inline large content                    │
│                                                                              │
│  4. CLEAN UP AFTER COMPLETION                                               │
│     ✓ Remove intermediate context after task completion                      │
│     ✓ Keep only final artifacts in context                                   │
│     ✓ Write summary to repo before context reset                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Context Reset Pack

When context budget is exceeded, the worker MUST produce a Context Reset Pack:

```json
{
  "context_reset_pack": {
    "run_id": "run-01J5ABCD",
    "task_slug": "user-auth",
    "worker_id": "worker-1",
    "created_at": "2026-01-08T12:00:00Z",
    "reason": "context_budget_exceeded",

    "state_snapshot": {
      "phase": "build",
      "plan_ref": "plans/run-01J5ABCD/user-auth.md",
      "completed_steps": [1, 2, 3],
      "pending_steps": [4, 5],
      "files_modified": [
        "src/auth/login.ts",
        "src/auth/hooks/useAuth.ts"
      ]
    },

    "pending_work": {
      "description": "Implement password reset flow",
      "blocked_by": null,
      "estimated_steps": 2
    },

    "resume_instructions": {
      "1": "Read plan at plans/run-01J5ABCD/user-auth.md",
      "2": "Check completed steps 1-3",
      "3": "Resume from step 4: password reset",
      "4": "Run verification after completion"
    },

    "artifacts_produced": [
      "src/auth/login.ts",
      "src/auth/hooks/useAuth.ts",
      "tests/auth/login.test.ts"
    ]
  }
}
```

### Catch-up Mechanism

When a worker needs to restore context (new session, handoff, or reset recovery):

```
1. LOAD CATCH-UP PACK
   │
   ├── Read: catch-up/run-{id}/{task}.md
   ├── Contains: Summary of decisions, current state, key references
   └── Size: < 2000 tokens
       │
       ▼
2. LOAD CURRENT PLAN
   │
   ├── Read: plans/run-{id}/{task}.md
   └── Check: completed vs. pending steps
       │
       ▼
3. LOAD ONLY NEEDED FILES
   │
   ├── Modified files from state snapshot
   └── Files needed for next step only
       │
       ▼
4. RESUME WORK
   │
   └── Continue from pending step
```

### Catch-up Pack Format

```markdown
# Catch-up: {task_name}

## TL;DR
{One paragraph summary of what's been done and what's next}

## Key Decisions Made
1. {Decision 1 with brief rationale}
2. {Decision 2 with brief rationale}

## Current State
- Phase: {Plan/Build/Verify}
- Progress: Step {n} of {total}
- Last action: {description}

## Next Steps
1. {Immediate next action}
2. {Following action}

## Key File References
- Plan: `plans/run-{id}/{task}.md`
- Main file: `src/auth/login.ts`
- Tests: `tests/auth/login.test.ts`

## Blockers
{None or list of blockers}
```

---

## Skills vs MCPs

### Definitions

| Concept | Definition | Token Cost | When to Use |
|---------|------------|------------|-------------|
| **Skill** | Internal standardized procedure executed without external calls | Low | Default for all repeatable tasks |
| **MCP** | External tool access via Model Context Protocol | High | Only when external data/action required |

### Decision Table

| Task | Use Skill | Use MCP | Rationale |
|------|-----------|---------|-----------|
| Generate code | ✓ Skill | | Internal capability |
| Read local file | ✓ Skill | | No external access needed |
| Write local file | ✓ Skill | | No external access needed |
| Run tests | ✓ Skill | | Local command execution |
| Lint code | ✓ Skill | | Local command execution |
| Create GitHub issue | | ✓ MCP | External GitHub API |
| Create GitHub PR | | ✓ MCP | External GitHub API |
| Read Figma design | | ✓ MCP | External Figma API |
| Query Jira ticket | | ✓ MCP | External Jira API |
| Fetch secret from Vault | | ✓ MCP | External Vault API |
| Generate image | | ✓ MCP | External NanoBanana API |

### MCP Minimization Policy

```yaml
mcp_policy:
  default_action: prefer_skill

  rules:
    - name: "Use Skills for local operations"
      condition: operation_is_local
      action: use_skill

    - name: "Use MCP only for external systems"
      condition: requires_external_api
      action: use_mcp
      log: true
      summarize_response: true

    - name: "Cache MCP responses"
      condition: mcp_response_cacheable
      action: cache_for_session
      ttl_minutes: 15

    - name: "Batch MCP calls"
      condition: multiple_mcp_calls_same_system
      action: batch_into_single_call
```

### MCP Call Logging

Every MCP call MUST be logged:

```json
{
  "mcp_call": {
    "timestamp": "2026-01-08T12:00:00Z",
    "run_id": "run-01J5ABCD",
    "worker_id": "worker-1",
    "mcp_server": "github",
    "operation": "create_pr",
    "input_summary": "Create PR for user-auth feature",
    "output_summary": "PR #156 created",
    "tokens_used": 1500,
    "duration_ms": 2300
  }
}
```

---

## Edge Cases & Failure Handling

### Merge Conflicts Between Workers

```
DETECTION:
└── GitHub API returns conflict status on PR

HANDLING:
├── Step 1: Attempt auto-rebase
│   └── git fetch origin main && git rebase origin/main
│
├── Step 2: If simple conflict → auto-resolve
│   └── Accept theirs for non-overlapping, regenerate overlapping
│
├── Step 3: If complex conflict → serialize
│   └── Pause later worker, let earlier worker merge first
│
└── Step 4: If unresolvable → escalate
    └── Surface in dashboard with conflict details

PREVENTION:
├── File locking for hot files
├── Dependency-aware scheduling
└── Conflict detection before PR creation
```

### Two Workers Editing Same File

```
DETECTION:
└── Lock registry shows file already locked

HANDLING:
├── If worker can wait → queue for lock release
├── If worker cannot wait → split work into non-conflicting parts
└── If split impossible → serialize tasks

PREVENTION:
├── Exclusive locks for hot files (package-lock.json, schema files)
├── Scheduler respects conflict zones
└── Task dependency analysis before parallel spawn
```

### Flaky Tests

```
DETECTION:
└── Same test fails/passes inconsistently across runs

HANDLING:
├── Retry 1: Run test again (immediate)
├── Retry 2: Run test with fresh environment
├── Retry 3: Run test in isolation
│
├── If passes after retry → log as flaky, continue
├── If consistently fails → investigate root cause
└── If > 5 failures → quarantine test (run but don't block)

BUDGET:
├── Max flaky tests: 10 per repo
└── Alert if flaky count > 5
```

### Partial Failures (One Worker Succeeds, Another Fails)

```
HANDLING:
├── Successful worker → PR created, enters merge queue
├── Failed worker → checkpoint created
│
├── Coordinator decides:
│   ├── If independent tasks → merge success, retry failure
│   ├── If dependent tasks → pause success, fix failure first
│   └── If failure blocks all → pause run, escalate
│
└── Dashboard shows:
    ├── Which workers succeeded/failed
    ├── Dependency relationships
    └── Recommended action
```

### GitHub Outage / Rate Limiting

```
DETECTION:
├── API returns 5xx errors
├── API returns 429 (rate limit)
└── API timeout after 30s

HANDLING:
├── Rate limit (429):
│   └── Backoff until X-RateLimit-Reset, then retry
│
├── Temporary error (5xx):
│   └── Exponential backoff: 1s → 2s → 4s → 8s → 16s → escalate
│
├── Persistent outage (> 5 minutes):
│   ├── Cache reads for read operations
│   ├── Queue writes for later
│   └── Alert operator, pause non-critical work
│
└── Extended outage (> 30 minutes):
    └── Pause all GitHub operations, save state, wait for recovery
```

### Repo Rules Violated

```
DETECTION:
├── Commit message format wrong
├── Required files missing
├── Forbidden patterns detected
└── Template not followed

HANDLING:
├── Auto-fix if possible:
│   ├── Reformat commit message
│   ├── Generate missing required files
│   └── Remove forbidden patterns
│
├── If auto-fix fails:
│   ├── Log violation details
│   ├── Block PR creation
│   └── Surface in Verification Report
│
└── Worker must fix before PR
```

### Plan Drift Detected

```
DETECTION:
├── Implementation doesn't match plan
├── Unplanned files modified
├── Planned steps skipped
└── Scope creep detected

HANDLING:
├── Minor drift (< 10% deviation):
│   ├── Log in Verification Report
│   ├── Update plan to match reality
│   └── Continue
│
├── Moderate drift (10-30% deviation):
│   ├── Pause and re-enter Plan Mode
│   ├── Revise plan
│   ├── Get alignment before continuing
│   └── Document drift reason
│
└── Major drift (> 30% deviation):
    ├── STOP immediately
    ├── Create Review Checkpoint
    ├── Escalate to dashboard
    └── Require operator decision
```

### Context Overflow / Hallucination Risk

```
DETECTION:
├── Context usage > 70%
├── Responses become repetitive
├── Factual inconsistencies appear
└── Worker references non-existent files

HANDLING:
├── At 70% context:
│   ├── STOP current work
│   ├── Produce Context Reset Pack
│   ├── Save all artifacts to repo
│   └── Request new session or handoff
│
├── On hallucination detection:
│   ├── STOP immediately
│   ├── Discard suspicious output
│   ├── Log incident
│   ├── Reset context
│   └── Resume from last known good state
│
└── PREVENTION:
    ├── Monitor context usage continuously
    ├── Progressive disclosure by default
    └── Write to repo, not context
```

### Operator Mode Risk Mitigation

Despite `--dangerously-skip-permissions`, these controls remain active:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              OPERATOR MODE SAFETY CONTROLS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STILL ENFORCED (cannot be bypassed):                                       │
│  ├── Audit logging (every action logged)                                     │
│  ├── Evidence Pack generation (signed, complete)                             │
│  ├── Policy evaluation (OPA gates run)                                       │
│  ├── Security scanning (blocks on critical findings)                         │
│  ├── Budget circuit breakers (hard limits enforced)                          │
│  ├── Secret isolation (credentials via Vault only)                           │
│  ├── Kill switch (immediate halt available)                                  │
│  ├── Merge queue (all checks must pass)                                      │
│  ├── CODEOWNERS (still enforced)                                             │
│  └── Plan→Build→Verify discipline (mandatory phases)                        │
│                                                                              │
│  BYPASSED (for automation speed):                                            │
│  ├── Interactive file approvals                                              │
│  ├── Manual PR review                                                        │
│  ├── Manual merge button                                                     │
│  └── Per-command confirmations                                               │
│                                                                              │
│  CATASTROPHIC ACTION PREVENTION:                                             │
│  ├── No force push to main/master                                            │
│  ├── No deletion of protected branches                                       │
│  ├── No secret exposure in logs/output                                       │
│  ├── No bypass of security scan blocks                                       │
│  └── No deployment without Evidence Pack                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Artifacts Produced Each Run

### Artifact Inventory

| Artifact | Location | Producer | When |
|----------|----------|----------|------|
| **Run Record** | `runs/run-{id}/run-record.json` | Coordinator | Run start |
| **Plan (per task)** | `plans/run-{id}/{task}.md` | Worker | Plan Mode |
| **Catch-up Pack** | `catch-up/run-{id}/{task}.md` | Worker | Ongoing |
| **Context Reset Pack** | `context-reset/run-{id}/{task}.json` | Worker | On reset |
| **Verification Report** | `evidence/run-{id}/{task}-verification.json` | Worker | Before PR |
| **Evidence Pack** | `evidence/run-{id}/evidence-pack.json` | CI | On merge |
| **Run Summary** | `runs/run-{id}/run-summary.md` | Coordinator | Run end |
| **Decision Log** | `decisions/run-{id}/decision-log.md` | All | Ongoing |

### Directory Structure

```
{repo}/
├── runs/
│   └── run-{id}/
│       ├── run-record.json          # Immutable run metadata
│       └── run-summary.md           # Final summary
├── plans/
│   └── run-{id}/
│       ├── coordinator-summary.md   # Overall coordination plan
│       ├── {task-1}.md              # Worker 1's plan
│       ├── {task-2}.md              # Worker 2's plan
│       └── {task-3}.md              # Worker 3's plan
├── catch-up/
│   └── run-{id}/
│       ├── {task-1}.md              # Worker 1's catch-up
│       ├── {task-2}.md              # Worker 2's catch-up
│       └── {task-3}.md              # Worker 3's catch-up
├── context-reset/
│   └── run-{id}/
│       └── {task}.json              # Context reset packs (if any)
├── evidence/
│   └── run-{id}/
│       ├── {task-1}-verification.json
│       ├── {task-2}-verification.json
│       ├── {task-3}-verification.json
│       └── evidence-pack.json       # Aggregated Evidence Pack
└── decisions/
    └── run-{id}/
        └── decision-log.md          # All decisions with rationale
```

### Run Summary Format

```markdown
# Run Summary: {run_id}

## Overview
- **Run ID**: run-01J5ABCD
- **Started**: 2026-01-08T10:00:00Z
- **Completed**: 2026-01-08T12:30:00Z
- **Duration**: 2h 30m
- **Status**: Success

## Scope
- **Project**: Task Manager App
- **Concept Lock**: v1.0.0
- **Journeys Completed**: 3 of 3

## Workers
| Worker | Task | Status | PR | Duration |
|--------|------|--------|-----|----------|
| worker-1 | User Auth | ✓ Merged | #156 | 45m |
| worker-2 | Dashboard | ✓ Merged | #157 | 52m |
| worker-3 | Settings | ✓ Merged | #158 | 38m |

## Metrics
- **Total tokens**: 125,000
- **Total cost**: $12.50
- **Files changed**: 24
- **Lines added**: 1,245
- **Lines removed**: 89
- **Tests added**: 18

## Verification Summary
- **Lint**: Pass (0 errors)
- **Tests**: Pass (42/42)
- **Security**: Pass (0 critical)
- **Coverage**: 87.3%

## Evidence Pack
- Location: `evidence/run-01J5ABCD/evidence-pack.json`
- Digest: `sha256:abc123...`

## Artifacts
- Plans: `plans/run-01J5ABCD/`
- Verification: `evidence/run-01J5ABCD/`
- Decisions: `decisions/run-01J5ABCD/decision-log.md`
```

---

## Enforcement Hooks

### Check Locations

| Check | Location | Enforcement Point |
|-------|----------|-------------------|
| **Plan required** | `.claude/commands/plan.md` | Session start |
| **Verification required** | `.claude/commands/verify.md` | Before PR |
| **Context budget** | `tools/validators/context-budget-check.md` | Continuous |
| **Run artifacts** | `tools/validators/run-artifacts-check.md` | Run end |
| **Commit format** | `.github/workflows/commit-lint.yml` | Push |
| **PR template** | `.github/PULL_REQUEST_TEMPLATE.md` | PR creation |
| **Required checks** | Branch protection rules | Merge |

### Merge Blocking Checks

These checks MUST pass before any PR can merge:

```yaml
# .github/branch-protection.yml
main:
  required_status_checks:
    strict: true
    contexts:
      - lint
      - typecheck
      - test:unit
      - test:integration
      - security:scan
      - security:secrets
      - design-jail        # If UI changes
      - policy-check       # OPA evaluation
      - verification-report # Worker verification
      - evidence-pack      # Evidence generation
```

### Enforcement Behavior Specifications

#### context-budget-check

```yaml
# tools/validators/context-budget-check.md
name: Context Budget Check
trigger: continuous (every 30 seconds)
behavior:
  - measure: current_context_usage_percentage
  - thresholds:
      warning: 50
      soft_limit: 60
      hard_limit: 70
  - actions:
      at_warning: log_warning
      at_soft_limit: suggest_summarization
      at_hard_limit: force_context_reset
  - on_hard_limit:
      - stop_current_work
      - save_all_pending_changes
      - produce_context_reset_pack
      - notify_coordinator
      - request_new_session
```

#### run-artifacts-check

```yaml
# tools/validators/run-artifacts-check.md
name: Run Artifacts Check
trigger: run_completion
behavior:
  - verify_required_artifacts:
      - run-record.json: required
      - plans/{task}.md: required_per_task
      - verification-report.json: required_per_task
      - run-summary.md: required
  - verify_artifact_integrity:
      - all_files_exist: true
      - all_json_valid: true
      - all_hashes_match: true
  - on_missing:
      - block_run_completion
      - list_missing_artifacts
      - request_regeneration
  - on_invalid:
      - block_run_completion
      - list_invalid_artifacts
      - request_fix
```

---

## Related Documents

- `docs/00-overview/glossary.md` — Term definitions
- `docs/00-overview/principles.md` — Core principles including Safe Autonomy
- `docs/02-architecture/workflow-architecture.md` — Temporal workflow details
- `docs/03-platform/portal-webapp.md` — Dashboard UI specification
- `docs/03-platform/track-assurance.md` — Drift detection and checkpoints
- `docs/05-compliance/evidence-pack.md` — Evidence Pack specification
- `docs/06-operations/finops-token-budgets.md` — Budget configuration
- `docs/06-operations/context-engineering-playbook.md` — Context engineering practices
- `docs/07-integrations/git-integration.md` — Git workflow automation
- `docs/07-integrations/mcp/mcp-overview.md` — MCP architecture
- `docs/08-agents/agent-system-contract.md` — Agent operating rules
- `CLAUDE.md` — Root rules file for Claude Code sessions
- `.claude/hooks/` — Hook configuration files
- `.claude/commands/` — Slash command definitions
- `templates/operations/` — Operational templates

---

**Version**: 1.0.0 | **Date**: 2026-01-08
