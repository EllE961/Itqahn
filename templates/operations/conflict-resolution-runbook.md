# Conflict Resolution Runbook

Step-by-step procedures for resolving conflicts in parallel work.

---

## Quick Reference

| Conflict Type | Symptoms | Resolution |
|---------------|----------|------------|
| **Textual** | Same lines changed | Manual merge |
| **Semantic** | Different changes, same effect | Choose one |
| **Structural** | File moved/renamed | Coordinate |
| **Dependency** | Package conflicts | Merge Captain |
| **Build** | CI fails after merge | Identify cause, fix |

---

## Procedure: Textual Conflict

**Symptoms**: Git reports merge conflict, same lines changed by different terminals.

### Step 1: Identify Conflict

```bash
# In your worktree
git fetch origin
git diff origin/integration-{run_id}

# See conflicting files
git status
```

### Step 2: Determine Ownership

Check `memory/file-claims.md`:
- Who claimed this file?
- Is the claim still valid?

### Step 3: Resolve

**If you own the file**:
```bash
# Pull latest integration
git fetch origin integration-{run_id}
git rebase origin/integration-{run_id}

# Resolve conflicts in editor
# (Keep your changes, integrate theirs if needed)

# Test
npm run test

# Continue
git add .
git rebase --continue
git push --force-with-lease
```

**If other terminal owns the file**:
- Contact the owner (via memory files)
- Wait for them to merge first
- Then rebase and adapt your changes

### Step 4: Verify

```bash
/verify
```

---

## Procedure: Semantic Conflict

**Symptoms**: Two terminals made different changes that achieve similar goals.

### Step 1: Identify

- Both implementations work
- Different approaches to same problem
- No textual conflict, but logical overlap

### Step 2: Evaluate

| Question | Terminal 1 | Terminal 2 |
|----------|------------|------------|
| Complexity? | | |
| Test coverage? | | |
| Performance? | | |
| Maintenance? | | |

### Step 3: Decide

- Merge Captain makes final call
- Document decision in `memory/decision-log.md`
- Chosen implementation stays, other is discarded

### Step 4: Execute

```bash
# Terminal with rejected implementation
git stash  # Save work in case needed later
git checkout integration-{run_id}
git pull
git branch -D task/{your-task}  # Delete old branch
# Reassign to new work or done
```

---

## Procedure: Structural Conflict

**Symptoms**: File moved or renamed by one terminal, modified by another.

### Step 1: Pause All Terminals

- All terminals stop making changes
- Commit any pending work

### Step 2: Coordinate

Determine target structure:
- Where should file live?
- What should it be named?
- Who uses this file?

### Step 3: Execute Restructure

**Merge Captain**:
```bash
# Make structural change
git mv old/path new/path

# Update all imports/references
# Run tests to verify

git commit -m "refactor: move X to Y [run-{id}]"
git push
```

### Step 4: All Terminals Sync

```bash
# Each terminal
git fetch origin integration-{run_id}
git rebase origin/integration-{run_id}

# Update any local references
# Run tests
```

---

## Procedure: Dependency Conflict

**Symptoms**: package.json or lock file conflicts.

### Step 1: Identify

```bash
npm ls  # See current dependencies
git diff origin/integration-{run_id} package.json
```

### Step 2: Merge Captain Takes Over

**Only Merge Captain touches dependency files.**

```bash
# Merge Captain
git fetch origin
git checkout integration-{run_id}
git pull

# Identify all needed dependencies from all terminals
# Update package.json with all needs
npm install

# Test full suite
npm test

git add package.json package-lock.json
git commit -m "chore: update dependencies [run-{id}]"
git push
```

### Step 3: All Terminals Sync

```bash
# Each terminal
git fetch origin
git rebase origin/integration-{run_id}
npm install
npm test
```

---

## Procedure: Build Failure After Merge

**Symptoms**: CI fails on integration branch after merge.

### Step 1: Identify Cause

```bash
# Check CI logs
# Identify which commit broke it
git bisect start
git bisect bad HEAD
git bisect good {last-known-good-commit}
# Follow bisect to find breaking commit
```

### Step 2: Determine Responsibility

- Which terminal introduced the break?
- Check `memory/file-claims.md` for ownership

### Step 3: Fix

**Option A: Quick Fix** (< 10 minutes)
```bash
# Responsible terminal fixes
# Push fix to integration
```

**Option B: Revert** (fix takes too long)
```bash
# Merge Captain reverts breaking commit
git revert {breaking-commit}
git push

# Responsible terminal fixes in their branch
# Re-merge when fixed
```

### Step 4: Post-Mortem

Add to `memory/decision-log.md`:
- What broke
- Why it wasn't caught
- How to prevent next time

---

## Procedure: Terminal Goes Off-Plan (Drift)

**Symptoms**: Terminal's changes don't match its plan.

### Step 1: Detect Drift

```bash
# Compare plan to reality
# Drift score > 30% = significant
```

### Step 2: Assess

| Question | Answer |
|----------|--------|
| Is drift justified? | |
| Should plan be updated? | |
| Should work be discarded? | |
| Can we split the work? | |

### Step 3: Resolution Options

**A: Update Plan**
- Drift was justified
- Update plan to reflect reality
- Continue with updated plan

**B: Revert Drift**
- Drift was not justified
- Stash or discard drifted work
- Continue with original plan

**C: Split Work**
- Drifted work is valuable but out of scope
- Create new task for drifted work
- Continue original task per plan

### Step 4: Document

Add to `memory/decision-log.md`:
- What drifted
- Resolution chosen
- Rationale

---

## Escalation

If conflict cannot be resolved:

1. **Document** the conflict fully
2. **Pause** all affected terminals
3. **Escalate** to dashboard (human review)
4. **Wait** for decision
5. **Apply** resolution

---

**Runbook Version**: 1.0.0
