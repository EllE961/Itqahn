# Parallel Safety Checklist

Use this checklist when running multiple Claude Code terminals in parallel.

---

## Before Starting Parallel Work

```markdown
## Pre-Parallel Checklist

**Run ID**: {run-id}
**Terminals**: {N of 5}
**Date**: {YYYY-MM-DD}

### Setup
- [ ] Each terminal has its own git worktree
- [ ] Each terminal has its own branch
- [ ] Integration branch created: `integration-{run_id}`
- [ ] Merge Captain designated: Terminal {N}

### File Ownership
- [ ] `memory/file-claims.md` created/updated
- [ ] Each terminal knows which files it owns
- [ ] Shared files (package.json, etc.) assigned to Merge Captain
- [ ] No overlapping claims

### Sync Points
- [ ] Defined when terminals must pause to integrate
- [ ] Communication channel established (memory files)
- [ ] Conflict resolution procedure agreed

### Branches

| Terminal | Worktree | Branch | Claimed Files |
|----------|----------|--------|---------------|
| 1 | /wt/{name} | task/{name} | {files} |
| 2 | /wt/{name} | task/{name} | {files} |
| 3 | /wt/{name} | task/{name} | {files} |
```

---

## During Parallel Work

```markdown
## Ongoing Parallel Checklist

### Per Terminal
- [ ] Working only in assigned worktree
- [ ] Working only on assigned branch
- [ ] Not editing files claimed by others
- [ ] Committing frequently (< 1 hour gaps)
- [ ] Syncing with integration branch regularly

### Coordination
- [ ] `memory/file-claims.md` stays current
- [ ] Integration branch updated as PRs merge
- [ ] No terminal has gone silent > 30 minutes
- [ ] Drift scans run periodically

### Warning Signs
- [ ] Same file showing in multiple terminal diffs
- [ ] Integration branch CI failing
- [ ] Sync conflicts appearing
```

---

## Before Merging to Integration

```markdown
## Pre-Merge Checklist (Per Terminal)

**Terminal**: {N}
**Branch**: {branch-name}
**Target**: integration-{run_id}

### Verification
- [ ] `/verify` passes all checks
- [ ] No uncommitted changes
- [ ] Branch rebased on latest integration
- [ ] File claims still valid

### PR Quality
- [ ] PR title follows convention
- [ ] PR description complete
- [ ] Labels applied
- [ ] CI checks configured

### Conflict Check
- [ ] No conflicts with integration branch
- [ ] No conflicts with other pending PRs
- [ ] If conflicts: resolve before merging
```

---

## Before Merging to Main

```markdown
## Pre-Main Merge Checklist

**Run ID**: {run-id}
**Integration Branch**: integration-{run_id}
**Merge Captain**: Terminal {N}

### All Tasks Complete
- [ ] All terminals have merged to integration
- [ ] All terminals have run `/verify`
- [ ] All acceptance criteria met

### Integration Quality
- [ ] Integration branch CI passes
- [ ] Full verification suite passes
- [ ] No pending conflicts
- [ ] Documentation updated

### Merge Captain Actions
- [ ] Final review of integration branch
- [ ] Run full verification
- [ ] Create PR to main
- [ ] Trigger auto-merge

### Post-Merge
- [ ] Clean up worktrees
- [ ] Archive file claims
- [ ] Update memory with completion status
```

---

## File Claims Format

```markdown
# File Claims

**Run ID**: {run-id}
**Updated**: {timestamp}

## Active Claims

| File/Directory | Claimed By | Since | Until |
|----------------|------------|-------|-------|
| src/auth/* | Terminal 1 | {time} | task-complete |
| src/dashboard/* | Terminal 2 | {time} | task-complete |
| package.json | Merge Captain | always | always |
| package-lock.json | Merge Captain | always | always |
| tsconfig.json | Merge Captain | always | always |

## Claim Protocol

1. Before editing a file, check this table
2. If unclaimed, add your claim
3. If claimed by another, coordinate first
4. Release claim when your task is complete

## Shared Files (Always Merge Captain)

- package.json / package-lock.json
- tsconfig.json / tsconfig.*.json
- .eslintrc.* / .prettierrc.*
- Schema/migration files
- Global type definitions
```

---

**Template Version**: 1.0.0
