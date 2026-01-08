# Git Integration

Git is the **Truth Store** for Itqahn. All code, policies, documentation, and infrastructure definitions live in Git.

---

## Goals

- All changes are reviewable, reproducible, and attributable
- Every merge is backed by verified evidence
- Drift is minimized through small PRs and enforced templates
- Releases are GitOps-driven and reversible

---

## Repository Model

### Recommended Layout

```
itqahn-org/
├── apps/                   # User-facing applications
├── services/               # Backend services
├── packages/               # Shared libraries
├── infra/                  # GitOps manifests, IaC modules
├── policies/               # OPA/Kyverno policies
├── docs/                   # Documentation
├── evidence/               # Evidence pack indices (optional)
└── concept-locks/          # Phase 1 Concept Lock artifacts
```

---

## Concept Lock Repository Model

Concept Lock artifacts from Phase 1 are versioned in Git as the foundational reference for all project work.

### Concept Lock Directory Structure

```
concept-locks/
├── {project-slug}/
│   ├── concept-lock.json        # The immutable Concept Lock artifact
│   ├── history/
│   │   ├── v1.0.0/              # Initial lock
│   │   │   ├── concept-lock.json
│   │   │   └── signatures/
│   │   ├── v1.1.0/              # After Change Request
│   │   │   ├── concept-lock.json
│   │   │   ├── change-request-cr001.json
│   │   │   └── signatures/
│   │   └── v1.2.0/
│   ├── design-os-draft/
│   │   └── design-os-draft.json # Design OS Draft from Phase 1
│   ├── asset-requirements/
│   │   └── asset-manifest.json  # Asset Requirements Manifest
│   ├── wireframes/
│   │   └── wireframe-choices.json
│   └── change-requests/
│       ├── cr-001-add-payments.json
│       └── cr-002-spanish-locale.json
```

### Concept Lock Schema (Git Storage)

```json
{
  "$schema": "https://itqahn.io/schemas/concept-lock/v1",
  "artifact_id": "concept-lock-abc123",
  "version": "1.0.0",
  "status": "locked",
  "project": {
    "name": "Task Manager App",
    "slug": "task-manager-app",
    "tenant_id": "tenant-acme"
  },
  "locked_at": "2026-01-08T12:00:00Z",
  "locked_by": "user@example.com",

  "modules": {
    "project_card": { "$ref": "./project-card.json" },
    "region_profile": { "$ref": "./region-profile.json" },
    "journeys_scope": { "$ref": "./journeys-scope.json" },
    "design_os_draft": { "$ref": "./design-os-draft/design-os-draft.json" },
    "wireframe_choices": { "$ref": "./wireframes/wireframe-choices.json" },
    "asset_requirements": { "$ref": "./asset-requirements/asset-manifest.json" },
    "assumptions_register": { "$ref": "./assumptions-register.json" }
  },

  "derived_artifacts": {
    "design_os_version": "v0.1.0",
    "design_os_ref": "design-os/v0.1.0"
  },

  "metadata": {
    "interview_duration_seconds": 480,
    "modules_completed": 7,
    "questions_answered": 28,
    "not_sure_count": 3,
    "git_commit": "abc123def456",
    "git_branch": "main"
  },

  "signatures": {
    "user_approval": "./signatures/user-approval.sig",
    "system_validation": "./signatures/system-validation.sig"
  }
}
```

### Concept Lock Versioning

Concept Locks follow SemVer with strict rules:

| Change Type | Version Bump | Trigger |
|-------------|--------------|---------|
| **Initial Lock** | 1.0.0 | Phase 1 completion, user locks |
| **Minor CR** | 1.1.0 | Change Request approved (additive) |
| **Major CR** | 2.0.0 | Change Request with breaking scope changes |
| **Patch** | 1.0.1 | Typo fix, metadata correction (no scope change) |

### Tag Convention

```
concept-lock/{project-slug}/v1.0.0
concept-lock/{project-slug}/v1.1.0
concept-lock/task-manager-app/v1.0.0
```

### CODEOWNERS for Concept Locks

```
# Concept Lock artifacts
/concept-locks/                      @product-team @governance-team
/concept-locks/*/concept-lock.json   @product-team
/concept-locks/*/design-os-draft/    @design-team
/concept-locks/*/asset-requirements/ @design-team @asset-factory
/concept-locks/*/change-requests/    @product-team @governance-team
```

### Concept Lock PR Template

```markdown
## Concept Lock Change

- Project: `task-manager-app`
- Current Version: `1.0.0`
- New Version: `1.1.0`

## Change Request
- CR ID: `cr-001`
- Type: Feature / Region / Brand / Assets / Security
- Status: Approved

## Impact Summary
- Scope: +3 journeys added
- Budget: +$250 estimated
- Timeline: +3 days estimated
- Compliance: PCI tier upgrade required
- Gates re-run: Risk Assessment, Compliance

## Approvals
- [ ] Product Owner
- [ ] Security (if security CR)
- [ ] Compliance (if compliance impact)
- [ ] FinOps (if budget impact)

## Artifacts Changed
- [ ] `concept-lock.json` - Version bump
- [ ] `journeys-scope.json` - Added payment journeys
- [ ] `region-profile.json` - (unchanged)
- [ ] `design-os-draft/` - (unchanged)
- [ ] `asset-requirements/` - Added payment icons
```

### Referencing Concept Lock in PRs

Every implementation PR MUST reference its Concept Lock version:

```yaml
# PR labels
concept-lock-version: 1.0.0
project: task-manager-app
```

```markdown
## Concept Lock Reference
- Version: `1.0.0`
- Artifact: `concept-locks/task-manager-app/concept-lock.json`
- Digest: `sha256:abc123...`

## Journey Being Implemented
- Journey: `user-can-browse-items`
- Journey ID: `journey-002`
- From Concept Lock: `journeys_scope.journeys[1]`
```

### Drift Detection Against Concept Lock

Every PR is checked for drift against the locked Concept Lock:

```rego
# policies/opa/concept/pr_drift_check.rego
package itqahn.concept.pr

# Check if PR implements journey not in Concept Lock
deny[msg] {
  input.pr.labels.journey_id != ""
  journey_id := input.pr.labels.journey_id
  not journey_in_lock(journey_id, input.concept_lock.journeys_scope.journeys)
  msg := sprintf("Journey '%s' not found in Concept Lock v%s. File Change Request.",
    [journey_id, input.concept_lock.version])
}

# Check if PR uses Design OS version different from lock
deny[msg] {
  pr_design_os := input.pr.labels.design_os_version
  lock_design_os := input.concept_lock.derived_artifacts.design_os_version
  pr_design_os != lock_design_os
  msg := sprintf("PR uses Design OS %s but Concept Lock specifies %s",
    [pr_design_os, lock_design_os])
}

# Check if PR adds features not in scope
warn[msg] {
  input.pr.files[_].path == "src/features/*"
  feature := extract_feature_name(input.pr.files[_].path)
  not feature_in_journeys(feature, input.concept_lock.journeys_scope.journeys)
  msg := sprintf("Feature '%s' may not be in locked scope - verify with Concept Lock", [feature])
}
```

### Change Request Git Workflow

```
1. User requests change via Portal
       │
       ▼
2. CR draft created in Git (not merged)
       │
       └── concept-locks/{project}/change-requests/cr-xxx.json
       │
       ▼
3. CR approved by required reviewers
       │
       ▼
4. New Concept Lock version generated
       │
       └── concept-locks/{project}/history/v1.1.0/
       │
       ▼
5. PR created to update concept-lock.json
       │
       ▼
6. PR merged, tag created
       │
       └── concept-lock/{project}/v1.1.0
       │
       ▼
7. Downstream references updated automatically
```

### Repository Patterns

| Pattern | Use Case |
|---------|----------|
| **Monorepo** | Small teams, tight coupling |
| **Polyrepo** | Large teams, independent services |
| **Hybrid** | Monorepo for services + separate infra repo |

---

## Branching Strategy

### Simple, High-Assurance Model

```
main (always releasable)
├── feat/TICKET-123-feature-name   (short-lived)
├── hotfix/TICKET-456-fix-name     (short-lived)
└── release/service/1.2.3          (tags, not branches)
```

### Branch Rules

| Branch | Purpose | Lifetime |
|--------|---------|----------|
| `main` | Production-ready code | Permanent |
| `feat/*` | Feature development | < 1 week |
| `hotfix/*` | Emergency fixes | < 1 day |
| `release/*` | Release tags | Tags, not branches |

**Avoid long-running branches.** They create merge conflicts and drift.

---

## GitHub Automation Program

In **Operator Mode**, Itqahn fully automates all GitHub operations. Users NEVER manually create issues, PRs, or trigger merges—all operations are performed programmatically via the `gh` CLI or GitHub API.

### Automation Principles

| Principle | Implementation |
|-----------|----------------|
| **GitHub is system of record** | All artifacts (issues, PRs, commits, releases) created programmatically |
| **Full traceability** | Every artifact linked to Run ID and Concept Lock |
| **Idempotent operations** | Safe to retry any operation |
| **Automated recovery** | Auto-fix common failures before escalating |
| **Human-out-of-loop** | User only intervenes on rare, unresolvable failures |

### Automated GitHub Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GITHUB AUTOMATION FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. PROJECT CREATED (Portal)                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Creates:                                                                ││
│  │  ├── Epic Issue (#40) "Task Manager MVP" [itqahn-epic]                  ││
│  │  ├── Labels: project, concept-lock, run-{id}                            ││
│  │  ├── Milestone: "Task Manager v1.0"                                      ││
│  │  └── Links to: Concept Lock artifact                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  2. RUN STARTED (Operator Mode)                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  For each work item:                                                     ││
│  │  ├── Work Item Issue (#42) "User Authentication" [itqahn-work-item]     ││
│  │  ├── Labels: work-item, journey-{id}, run-{id}                          ││
│  │  ├── Links to: Epic Issue, Journey in Concept Lock                       ││
│  │  └── Assigns: orchestrator bot                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  3. BUILD PHASE                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Creates:                                                                ││
│  │  ├── Branch: feat/run-{id}-{work-item-slug}                             ││
│  │  ├── Commits: feat({scope}): {message} [run-{id} #{issue}]             ││
│  │  └── (Multiple commits as code is generated)                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  4. PR CREATED                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Creates:                                                                ││
│  │  ├── PR (#156) with template populated automatically                     ││
│  │  ├── Links to: Work Item Issue, Evidence Pack                            ││
│  │  ├── Labels: auto-generated, run-{id}, concept-lock-{version}           ││
│  │  ├── Auto-merge: enabled (when checks pass)                              ││
│  │  └── Reviewers: none required (Operator Mode)                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  5. CI CHECKS RUN                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Required checks:                                                        ││
│  │  ├── lint (ESLint, Prettier)                                            ││
│  │  ├── test (unit, integration)                                            ││
│  │  ├── security-scan (Semgrep, Gitleaks)                                  ││
│  │  ├── design-jail (if UI changes)                                         ││
│  │  ├── asset-validation (if assets changed)                                ││
│  │  ├── policy-check (OPA)                                                  ││
│  │  └── evidence-pack (generate and sign)                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  6. MERGE QUEUE                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  When all checks pass:                                                   ││
│  │  ├── PR enters merge queue                                               ││
│  │  ├── Queue branch created: gh-readonly-queue/main/pr-156-...            ││
│  │  ├── CI runs again on queue branch (merge preview)                       ││
│  │  └── If pass → auto-merge to main                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│       │                                                                      │
│       ▼                                                                      │
│  7. RELEASE (when milestone complete)                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Creates:                                                                ││
│  │  ├── Tag: v1.0.0                                                         ││
│  │  ├── Release with auto-generated changelog                               ││
│  │  ├── Evidence Pack attached as release asset                             ││
│  │  └── Epic Issue closed                                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Issue Templates (Itqahn Auto-Generated)

#### Epic Issue

```yaml
# Created automatically when project starts
name: itqahn-epic
title: "{project_name} - MVP"
labels: ["epic", "itqahn-generated"]
body:
  project_slug: "task-manager-app"
  concept_lock_version: "1.0.0"
  concept_lock_ref: "concept-locks/task-manager-app/concept-lock.json"
  run_id: "run-01J5ABCD..."
  journeys_count: 8
  estimated_work_items: 12

  description: |
    ## Concept Lock Reference
    - Version: 1.0.0
    - Artifact: `concept-locks/task-manager-app/concept-lock.json`
    - Locked: 2026-01-08T12:00:00Z

    ## Journeys in Scope
    - [ ] #42 User Authentication
    - [ ] #43 Dashboard Home
    - [ ] #44 Task CRUD
    ...
```

#### Work Item Issue

```yaml
# Created automatically when run starts
name: itqahn-work-item
title: "{journey_name}"
labels: ["work-item", "itqahn-generated", "journey-{id}"]
body:
  run_id: "run-01J5ABCD..."
  parent_epic: "#40"
  journey_id: "journey-002"
  concept_lock_version: "1.0.0"

  description: |
    ## Journey Reference
    - Journey: `user-can-authenticate`
    - From Concept Lock: `journeys_scope.journeys[1]`

    ## Success Criteria
    - User can log in with email/password
    - User can reset password
    - Session persists across browser refresh

    ## Implementation
    - Branch: `feat/run-01J5ABCD-user-auth`
    - PR: (will be linked when created)
```

### Branch Naming Convention

| Pattern | Example | Use |
|---------|---------|-----|
| `feat/run-{run_id}-{slug}` | `feat/run-01J5ABCD-user-auth` | Feature work from Operator Mode |
| `fix/run-{run_id}-{slug}` | `fix/run-01J5EFGH-login-bug` | Bug fix from Operator Mode |
| `hotfix/{issue}-{slug}` | `hotfix/123-security-patch` | Manual hotfix (rare) |
| `cr/run-{run_id}-{cr_id}` | `cr/run-01J5IJKL-cr001` | Change Request implementation |
| `rebuild/main` | `rebuild/main` | Primary Legacy Rebuild development |
| `rebuild/strangler/{component}` | `rebuild/strangler/auth-service` | Per-component Strangler migration |
| `rebuild/clean/{module}` | `rebuild/clean/api-v2` | Clean Rebuild module |
| `rebuild/parity-tests` | `rebuild/parity-tests` | Parity verification suite |
| `assurance/{checkpoint_id}` | `assurance/ckpt-abc123` | Track Assurance checkpoint branch |
| `improve-itqahn/{candidate_id}` | `improve-itqahn/imp-2026-0108-001` | Self-improvement implementation |

### System-Owned Branches

The following branches are **system-owned** and MUST NOT be modified manually:

| Branch Pattern | Owner | Purpose | Protection |
|----------------|-------|---------|------------|
| `rebuild/*` | Legacy Rebuild workflow | Component migrations | Auto-created, force-push allowed by system |
| `assurance/*` | Track Assurance workflow | Checkpoint snapshots | Auto-created, read-only after creation |
| `improve-itqahn/*` | Improvement Pipeline | Self-improvement PRs | Auto-created, standard PR protection |

**System-owned branch rules:**
- MUST NOT be created manually
- MUST NOT be modified outside their owning workflow
- MAY be force-pushed by the owning system (with audit)
- MUST be cleaned up by the owning system after completion

### Commit Message Format

All commits MUST include Run ID and Issue ID:

```
{type}({scope}): {description} [run-{id} #{issue}]

- type: feat, fix, docs, style, refactor, test, chore
- scope: module or area affected
- description: concise change summary
- run-id: Operator Mode run identifier
- issue: GitHub issue number
```

**Examples:**
```
feat(auth): add login form component [run-01J5ABCD #42]
fix(auth): correct password validation [run-01J5ABCD #42]
test(auth): add unit tests for login [run-01J5ABCD #42]
```

**Enforcement:**
```yaml
# .github/workflows/commit-lint.yml
- name: Lint Commit Messages
  uses: wagoid/commitlint-github-action@v5
  with:
    configFile: commitlint.config.js
```

```javascript
// commitlint.config.js
module.exports = {
  rules: {
    'run-id-required': [2, 'always'],
    'issue-required': [2, 'always'],
  },
  plugins: ['@itqahn/commitlint-plugin'],
};
```

### Merge Queue Configuration

Merge queue is **mandatory** for the `main` branch:

```yaml
# Repository settings
merge_queue:
  enabled: true
  merge_method: squash

  # Build on queue branch, not just PR branch
  build_on_merge_commit: true

  # Batch settings
  max_entries_to_build: 5
  min_entries_to_merge: 1

  # Timing
  wait_timer_minutes: 0  # Merge immediately when ready

  # Status checks must pass on queue branch
  status_check_policy:
    - lint
    - test
    - security-scan
    - design-jail
    - policy-check
    - evidence-pack
```

**Merge Queue Event Handling:**

CI MUST respond to merge queue events:

```yaml
# .github/workflows/ci.yml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  merge_group:  # CRITICAL: Run on merge queue branches
    types: [checks_requested]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: npm test
```

### Auto-Merge Configuration

```yaml
# Enabled automatically when PR is created by Itqahn
auto_merge:
  enabled: true
  merge_method: squash

  # Conditions for auto-merge
  conditions:
    - all_checks_passed
    - no_changes_requested
    - head_ref_matches: "feat/run-*"  # Only auto-merge Itqahn branches
```

**Auto-Merge Flow:**
```
1. PR created with auto-merge enabled
       │
       ▼
2. CI checks run
       │
       ├── Any check fails → Auto-remediation attempts
       │
       └── All checks pass
               │
               ▼
3. PR enters merge queue
       │
       ▼
4. Queue branch CI runs
       │
       ├── Fails → PR ejected from queue, retry
       │
       └── Passes → Auto-merge to main
```

### Bot Identity and Permissions

The Itqahn orchestrator bot requires specific permissions:

```yaml
# GitHub App permissions
permissions:
  contents: write        # Push commits, create branches
  pull_requests: write   # Create PRs, enable auto-merge
  issues: write          # Create issues, add labels
  checks: write          # Create check runs
  statuses: write        # Set commit statuses
  actions: read          # Read workflow status

# Branch protection exception
branch_protection:
  main:
    bypass_actors:
      - itqahn-bot[bot]  # Allow bot to merge via queue
```

### Edge Case Handling

#### Merge Conflicts

```
Detection:
└── GitHub API returns conflict status when PR cannot be merged cleanly

Auto-Remediation:
├── Attempt 1: Auto-rebase onto main
│   └── git fetch origin main && git rebase origin/main
├── Attempt 2: Regenerate changed files
│   └── Re-run Claude Code on conflicting files only
├── Attempt 3: Split PR into smaller, non-conflicting PRs
│   └── Create separate PRs for each logical change
└── Escalate: Surface in dashboard for manual resolution
```

**OPA Policy:**
```rego
# policies/opa/github/merge_conflict.rego
package itqahn.github.conflict

action := "auto_rebase" {
  input.conflict_type == "simple"
  input.files_conflicting < 3
}

action := "regenerate" {
  input.conflict_type == "simple"
  input.files_conflicting >= 3
  input.files_conflicting < 10
}

action := "split_pr" {
  input.files_conflicting >= 10
}

action := "escalate" {
  input.conflict_type == "complex"
}
```

#### Flaky Tests

```yaml
# Flaky test policy
flaky_tests:
  detection:
    # Test is flaky if it fails/passes inconsistently
    threshold: 3  # Same test fails 3+ times in different runs
    window: "7d"

  handling:
    retry:
      max_attempts: 3
      backoff: exponential

    quarantine:
      enabled: true
      after_failures: 5
      quarantine_label: "flaky"
      # Quarantined tests run but don't block merge

    budget:
      max_flaky_tests: 10  # Hard limit on quarantined tests
      alert_at: 5

  evidence:
    # Flaky test handling is recorded in Evidence Pack
    record_retries: true
    record_quarantine: true
```

#### Blocked Checks

```
Check Type │ Auto-Remediation │ Escalation
───────────┼──────────────────┼────────────────────
lint       │ Auto-fix, commit │ Review lint config
test       │ Retry 3x         │ Investigate failure
security   │ Never auto-fix   │ Security team review
timeout    │ Retry with 2x    │ Investigate CI infra
rate-limit │ Backoff, retry   │ Request quota increase
```

#### Rate Limits

```yaml
rate_limit_handling:
  github_api:
    detection: "X-RateLimit-Remaining < 100"
    strategy:
      - action: backoff
        wait_until: "X-RateLimit-Reset"
      - action: batch
        combine_operations: true
      - action: queue
        delay_non_critical: true

    notification:
      dashboard: true
      slack: "#itqahn-alerts"

    escalation:
      after_minutes: 30
      contact: "platform-team"
```

#### Stuck PRs

```
Detection:
├── PR open > 24 hours with all checks passing
├── PR in merge queue > 2 hours
├── PR with repeated check failures (> 5)
└── PR with unresolved conflict > 4 hours

Auto-Remediation:
├── Stuck in queue: Force re-queue
├── Repeated failures: Regenerate PR
├── Unresolved conflict: Split or escalate
└── All else: Close PR, create new run

Evidence:
└── Stuck PR handling recorded in Run Evidence Record
```

#### Large Assets (Git LFS)

```yaml
# Git LFS policy
git_lfs:
  enabled: true

  track_patterns:
    - "*.png"
    - "*.jpg"
    - "*.ico"
    - "*.svg"  # Only if > 100KB
    - "*.woff2"

  size_limits:
    per_file: "10MB"
    per_commit: "50MB"

  alternatives:
    # If file too large for LFS, use artifact storage
    fallback: "artifact_storage"
    artifact_storage_url: "s3://itqahn-artifacts/"

  evidence:
    # LFS files referenced by digest in Evidence Pack
    include_digests: true
```

#### Secret Leakage Prevention

```yaml
secret_scanning:
  pre_commit:
    enabled: true
    tool: gitleaks

  push_protection:
    enabled: true
    block_pushes: true

  on_detection:
    actions:
      - block_push
      - alert_security_team
      - rotate_if_possible
      - create_incident

  rotation_workflow:
    # Triggered when secret detected
    steps:
      - identify_secret_type
      - check_if_rotatable
      - rotate_via_vault
      - update_consumers
      - invalidate_old_secret
      - log_incident
```

### Release Automation

```
1. Milestone completion detected
   └── All work item issues closed
       │
       ▼
2. Generate changelog
   └── From commit messages since last release
       │
       ▼
3. Bump version
   └── Based on commit types (feat → minor, fix → patch)
       │
       ▼
4. Create tag
   └── v{major}.{minor}.{patch}
       │
       ▼
5. Create release
   └── With changelog, Evidence Pack attached
       │
       ▼
6. Close epic issue
   └── Link to release
```

**Release Workflow:**
```yaml
# .github/workflows/release.yml
name: Release
on:
  workflow_dispatch:
    inputs:
      run_id:
        description: 'Operator Mode Run ID'
        required: true

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Changelog
        run: npx standard-version --dry-run

      - name: Verify Evidence Pack
        run: |
          npx itqahn-cli evidence verify \
            --run-id ${{ inputs.run_id }}

      - name: Create Release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          release_name: Release ${{ steps.version.outputs.tag }}
          body_path: CHANGELOG.md

      - name: Attach Evidence Pack
        run: |
          gh release upload ${{ steps.version.outputs.tag }} \
            evidence-${{ inputs.run_id }}.json
```

### GitHub Actions Required for Operator Mode

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push, PR, merge_group | Run all checks |
| `commit-lint.yml` | push | Validate commit format |
| `evidence.yml` | PR merge | Generate Evidence Pack |
| `release.yml` | workflow_dispatch | Create releases |
| `auto-remediate.yml` | check_run failure | Attempt auto-fixes |

### Enforcement Hooks

#### Commit Message Validation
```rego
# policies/opa/github/commit_format.rego
package itqahn.github.commit

deny[msg] {
  not regex.match(`^\w+\(.+\): .+ \[run-\w+ #\d+\]$`, input.commit.message)
  msg := "Commit message must include [run-{id} #{issue}]"
}
```

#### PR Evidence Required
```rego
# policies/opa/github/pr_evidence.rego
package itqahn.github.pr

deny[msg] {
  input.pr.labels[_] == "auto-generated"
  not has_evidence_pack_link(input.pr.body)
  msg := "Auto-generated PRs must link to Evidence Pack"
}

deny[msg] {
  input.pr.base.ref == "main"
  not input.pr.labels[_] == "run-*"
  msg := "PRs to main must have run-{id} label"
}
```

#### Release Evidence Required
```rego
# policies/opa/github/release_evidence.rego
package itqahn.github.release

deny[msg] {
  not has_evidence_asset(input.release.assets)
  msg := "Releases must have Evidence Pack attached"
}

has_evidence_asset(assets) {
  assets[_].name == "evidence-*.json"
}
```

---

## Parallel Work: Worktree-per-Task Model

Itqahn runs **multiple Claude Code sessions in parallel** to maximize throughput. Each parallel task operates in an isolated Git worktree, eliminating conflicts between concurrent executions.

### Why Worktrees?

| Challenge | Solution |
|-----------|----------|
| Concurrent sessions conflict on working directory | Each session has its own worktree |
| Branch switching interrupts work | Worktrees allow simultaneous branches |
| Shared lockfiles cause corruption | Worktrees isolate file system state |
| Single checkout limits parallelism | Worktrees enable N parallel tasks |

### Worktree Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    GIT ORCHESTRATOR (System-Level)                     │  │
│  │                                                                         │  │
│  │  • Creates worktrees  • Manages locks  • Schedules tasks  • Merges     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│       ┌──────────────────────────────┼──────────────────────────────┐       │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │  WORKTREE 1  │             │  WORKTREE 2  │             │  WORKTREE 3  │ │
│  │              │             │              │             │              │ │
│  │ Claude Code  │             │ Claude Code  │             │ Claude Code  │ │
│  │ Session #1   │             │ Session #2   │             │ Session #3   │ │
│  │              │             │              │             │              │ │
│  │ Branch:      │             │ Branch:      │             │ Branch:      │ │
│  │ feat/run-A   │             │ feat/run-B   │             │ feat/run-C   │ │
│  │              │             │              │             │              │ │
│  │ Task:        │             │ Task:        │             │ Task:        │ │
│  │ User Auth    │             │ Dashboard    │             │ Settings     │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │    PR #1     │             │    PR #2     │             │    PR #3     │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       └──────────────────────────────┼──────────────────────────────┘       │
│                                      │                                       │
│                                      ▼                                       │
│                        ┌──────────────────────────┐                         │
│                        │      MERGE QUEUE         │                         │
│                        │   (Deterministic Order)  │                         │
│                        └──────────────────────────┘                         │
│                                      │                                       │
│                                      ▼                                       │
│                               ┌────────────┐                                │
│                               │    main    │                                │
│                               └────────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Worktree Lifecycle

```
1. RUN STARTED
   │
   ▼
2. Git Orchestrator creates worktree
   git worktree add /worktrees/run-{id} -b feat/run-{id}-{task}
   │
   ▼
3. Claude Code session spawned in worktree directory
   cd /worktrees/run-{id} && claude-code --dangerously-skip-permissions
   │
   ▼
4. Work performed (commits, file changes)
   All changes isolated to this worktree
   │
   ▼
5. PR created from worktree branch
   │
   ▼
6. After merge: Worktree cleaned up
   git worktree remove /worktrees/run-{id}
```

### Worktree Directory Structure

```
/itqahn/
├── repo/                          # Main repository (bare or regular)
│   └── .git/
├── worktrees/                     # All active worktrees
│   ├── run-01J5ABCD-user-auth/   # Worktree for task 1
│   │   ├── .git                  # Worktree git file
│   │   ├── src/
│   │   └── ...
│   ├── run-01J5EFGH-dashboard/   # Worktree for task 2
│   │   ├── .git
│   │   ├── src/
│   │   └── ...
│   └── run-01J5IJKL-settings/    # Worktree for task 3
│       ├── .git
│       ├── src/
│       └── ...
└── locks/                         # File lock registry
    └── file-locks.json
```

### Concurrency Limits and Scheduling

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| **Max parallel worktrees per tenant** | 5 | Resource and cost control |
| **Max parallel worktrees per project** | 3 | Conflict likelihood |
| **Max parallel worktrees per repository** | 10 | GitHub API limits |
| **Worktree timeout** | 4 hours | Prevent resource leaks |

#### Scheduling Rules

Tasks MUST be scheduled with conflict awareness:

```yaml
scheduling:
  policy: conflict_aware

  # Tasks that MUST run serially (never parallelize)
  serialized_paths:
    - "**/package-lock.json"
    - "**/yarn.lock"
    - "**/pnpm-lock.yaml"
    - "**/migrations/**"
    - "**/schema.prisma"
    - "**/schema.graphql"
    - "**/design-os/tokens.json"
    - "**/route-registry.ts"
    - "**/.env*"

  # Tasks that SHOULD run serially if touching same area
  conflict_zones:
    - pattern: "src/auth/**"
      max_concurrent: 1
    - pattern: "src/api/routes/**"
      max_concurrent: 1
    - pattern: "src/shared/types/**"
      max_concurrent: 2

  # Priority scoring
  priority:
    critical_path: 100     # Tasks blocking other tasks
    user_facing: 80        # User-visible features
    infrastructure: 60     # Infra changes
    documentation: 40      # Docs only
    refactoring: 20        # Non-urgent cleanup
```

#### Scheduling Algorithm

```python
def schedule_tasks(pending_tasks: list[Task], active_worktrees: list[Worktree]) -> list[Task]:
    """
    Schedule tasks respecting concurrency limits and conflict zones.
    Returns tasks that can start immediately.
    """
    schedulable = []

    for task in pending_tasks:
        # Check global limits
        if len(active_worktrees) >= MAX_PARALLEL_WORKTREES:
            break

        # Check project limits
        project_worktrees = [w for w in active_worktrees if w.project == task.project]
        if len(project_worktrees) >= MAX_PROJECT_WORKTREES:
            continue

        # Check file conflicts
        if has_file_conflict(task, active_worktrees):
            continue

        # Check serialized paths
        if touches_serialized_path(task) and any_task_touches_serialized_path(active_worktrees):
            continue

        # Check conflict zones
        if violates_conflict_zone(task, active_worktrees):
            continue

        # Check dependencies
        if has_unmet_dependencies(task, active_worktrees):
            continue

        schedulable.append(task)

    # Sort by priority
    return sorted(schedulable, key=lambda t: t.priority, reverse=True)
```

### File Locks and Ownership

Hot files require explicit locks to prevent corruption:

#### Lock Types

| Lock Type | Scope | Duration | Release |
|-----------|-------|----------|---------|
| **Exclusive** | Single task owns file | Until PR merged | Automatic on merge |
| **Shared** | Multiple tasks read | Until all readers done | Automatic on task completion |
| **Advisory** | Warning only | N/A | N/A |

#### Hot Files (Require Exclusive Lock)

```yaml
hot_files:
  exclusive_lock_required:
    # Package managers
    - pattern: "**/package-lock.json"
      reason: "Concurrent npm installs corrupt lockfile"
    - pattern: "**/yarn.lock"
      reason: "Concurrent yarn installs corrupt lockfile"
    - pattern: "**/pnpm-lock.yaml"
      reason: "Concurrent pnpm installs corrupt lockfile"

    # Database
    - pattern: "**/migrations/**"
      reason: "Migrations must be sequential"
    - pattern: "**/schema.prisma"
      reason: "Schema changes affect migrations"
    - pattern: "**/schema.graphql"
      reason: "Schema changes must be atomic"

    # Design system
    - pattern: "**/design-os/tokens.json"
      reason: "Token changes affect all UI"
    - pattern: "**/design-os/components.json"
      reason: "Component changes affect all UI"

    # Routing
    - pattern: "**/route-registry.ts"
      reason: "Route conflicts cause runtime errors"
    - pattern: "**/routes/index.ts"
      reason: "Route conflicts cause runtime errors"

    # Configuration
    - pattern: "**/.env*"
      reason: "Environment conflicts cause deployment issues"
    - pattern: "**/config/*.json"
      reason: "Config conflicts cause runtime issues"
```

#### Lock Registry

```json
{
  "locks": [
    {
      "file": "package-lock.json",
      "lock_type": "exclusive",
      "held_by": "run-01J5ABCD",
      "worktree": "/worktrees/run-01J5ABCD-user-auth",
      "acquired_at": "2026-01-08T12:00:00Z",
      "expires_at": "2026-01-08T16:00:00Z"
    },
    {
      "file": "src/auth/**",
      "lock_type": "exclusive",
      "held_by": "run-01J5ABCD",
      "worktree": "/worktrees/run-01J5ABCD-user-auth",
      "acquired_at": "2026-01-08T12:00:00Z",
      "expires_at": "2026-01-08T16:00:00Z"
    }
  ]
}
```

#### Lock Acquisition Protocol

```python
def acquire_lock(task: Task, file_pattern: str, lock_type: LockType) -> LockResult:
    """
    Acquire a file lock for a task.
    """
    existing_lock = get_lock(file_pattern)

    if existing_lock is None:
        # No existing lock, acquire it
        return create_lock(task, file_pattern, lock_type)

    if existing_lock.lock_type == LockType.EXCLUSIVE:
        if lock_type == LockType.EXCLUSIVE:
            # Cannot acquire exclusive if another exclusive exists
            return LockResult(
                acquired=False,
                reason=f"Exclusive lock held by {existing_lock.held_by}",
                wait_for=existing_lock.held_by
            )
        else:
            # Cannot acquire shared if exclusive exists
            return LockResult(
                acquired=False,
                reason=f"Exclusive lock held by {existing_lock.held_by}",
                wait_for=existing_lock.held_by
            )

    if existing_lock.lock_type == LockType.SHARED:
        if lock_type == LockType.SHARED:
            # Add to shared lock holders
            return add_shared_holder(existing_lock, task)
        else:
            # Cannot acquire exclusive if shared exists
            return LockResult(
                acquired=False,
                reason=f"Shared lock held by {existing_lock.holders}",
                wait_for=existing_lock.holders
            )

    return create_lock(task, file_pattern, lock_type)
```

### Rebase-on-Latest-Main Rule

All worktrees MUST stay current with main to minimize merge conflicts:

```yaml
rebase_policy:
  # When to rebase
  triggers:
    - before_pr_creation: true
    - on_main_update: true
    - on_conflict_detected: true
    - periodic_minutes: 30

  # How to rebase
  strategy:
    method: rebase
    preserve_merges: false
    autostash: true

  # Conflict handling
  on_conflict:
    - attempt_auto_resolve: true
    - if_auto_fails: regenerate_conflicting_files
    - if_regenerate_fails: split_pr
    - if_split_fails: escalate_to_dashboard
```

#### Automatic Rebase Workflow

```
1. Main branch updated (another PR merged)
       │
       ▼
2. Git Orchestrator detects update
       │
       ▼
3. For each active worktree:
   ├── Stash local changes
   ├── Fetch origin main
   ├── Rebase onto origin/main
   │   ├── Success → Continue work
   │   └── Conflict → Auto-resolve or escalate
   └── Pop stash
       │
       ▼
4. If conflict:
   ├── Attempt auto-resolution (accept theirs + regenerate ours)
   ├── If fails → Mark files for regeneration
   └── Resume Claude Code with conflict context
```

### Merge Queue and Merge Train

#### Deterministic Merge Order

PRs merge in a deterministic order based on:

1. **Priority** (highest first)
2. **Age** (oldest first, as tiebreaker)
3. **Dependencies** (dependencies merge first)

```yaml
merge_queue:
  ordering:
    primary: priority
    secondary: created_at
    tertiary: dependencies

  priority_rules:
    hotfix: 100
    security: 90
    blocking_dependency: 80
    critical_path: 70
    feature: 50
    refactor: 30
    documentation: 10

  dependency_handling:
    # If PR A depends on PR B, B must merge first
    enforce_order: true
    # If dependency fails, dependent PRs are ejected
    eject_on_dependency_failure: true
```

#### Merge Train Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MERGE TRAIN STATUS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Queue Position │ PR     │ Status      │ Checks   │ Priority │ Wait Time   │
│  ───────────────┼────────┼─────────────┼──────────┼──────────┼───────────  │
│       1         │ #156   │ Merging     │ ✓✓✓✓✓   │ 70       │ 0m          │
│       2         │ #158   │ CI Running  │ ✓✓✓○○   │ 50       │ 3m          │
│       3         │ #157   │ Queued      │ ✓✓✓✓✓   │ 50       │ 5m          │
│       4         │ #159   │ Waiting     │ ✓✓✓✓✓   │ 30       │ 8m          │
│                                                                              │
│  Legend: ✓ = Passed, ○ = Running, ✗ = Failed                               │
│                                                                              │
│  Estimated time to merge #159: ~15 minutes                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Merge Queue Conflict Detection

```python
def detect_queue_conflicts(queued_prs: list[PR]) -> list[Conflict]:
    """
    Detect potential conflicts between queued PRs before they merge.
    """
    conflicts = []

    for i, pr_a in enumerate(queued_prs):
        for pr_b in queued_prs[i+1:]:
            # Check file overlap
            overlapping_files = set(pr_a.changed_files) & set(pr_b.changed_files)

            if overlapping_files:
                # Check if changes conflict
                for file in overlapping_files:
                    if changes_conflict(pr_a.diff(file), pr_b.diff(file)):
                        conflicts.append(Conflict(
                            pr_a=pr_a,
                            pr_b=pr_b,
                            file=file,
                            resolution=determine_resolution(pr_a, pr_b, file)
                        ))

    return conflicts

def determine_resolution(pr_a: PR, pr_b: PR, file: str) -> Resolution:
    """
    Determine how to resolve the conflict.
    """
    # Higher priority PR wins
    if pr_a.priority > pr_b.priority:
        return Resolution.EJECT_PR_B
    elif pr_b.priority > pr_a.priority:
        return Resolution.EJECT_PR_A
    else:
        # Same priority: older PR wins
        if pr_a.created_at < pr_b.created_at:
            return Resolution.EJECT_PR_B
        else:
            return Resolution.EJECT_PR_A
```

### Task Dependencies

Some tasks depend on others completing first:

```yaml
dependencies:
  # Explicit dependencies (from work item graph)
  explicit:
    - task: "api-endpoints"
      depends_on: ["database-schema"]
    - task: "frontend-components"
      depends_on: ["api-endpoints", "design-tokens"]

  # Implicit dependencies (detected from file analysis)
  implicit:
    detect_import_dependencies: true
    detect_type_dependencies: true

  handling:
    # Wait for dependencies before starting
    wait_for_dependencies: true

    # If dependency fails, how to handle dependent tasks
    on_dependency_failure:
      action: pause_and_notify
      retry_after_fix: true
```

#### Dependency Graph Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TASK DEPENDENCY GRAPH                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌─────────────────┐                                       │
│                    │  database-schema │ ← COMPLETED ✓                        │
│                    └────────┬────────┘                                       │
│                             │                                                │
│              ┌──────────────┴──────────────┐                                │
│              ▼                              ▼                                │
│  ┌─────────────────┐            ┌─────────────────┐                         │
│  │  api-endpoints  │ ← RUNNING  │  design-tokens  │ ← COMPLETED ✓           │
│  └────────┬────────┘            └────────┬────────┘                         │
│           │                               │                                  │
│           └──────────────┬───────────────┘                                  │
│                          ▼                                                   │
│              ┌─────────────────────┐                                        │
│              │ frontend-components │ ← WAITING (blocked by api-endpoints)   │
│              └─────────────────────┘                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Failure Handling

#### Failure Categories

| Failure | Detection | Auto-Remediation | Escalation |
|---------|-----------|------------------|------------|
| **CI fails** | Check status API | Retry → Regenerate → Quarantine | Dashboard |
| **Merge conflict** | Git merge failure | Rebase → Regenerate → Split | Dashboard |
| **Flaky test** | Inconsistent pass/fail | Retry → Quarantine | After budget exhausted |
| **Partial completion** | Task timeout | Checkpoint → Resume | Dashboard |
| **Worktree corruption** | Git errors | Delete → Recreate | Dashboard |
| **Rate limit** | API 429 response | Backoff → Retry | After max retries |
| **Lock timeout** | Lock expires without release | Force release → Retry | Dashboard |

#### Auto-Remediation Protocol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AUTO-REMEDIATION PROTOCOL                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FAILURE DETECTED                                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ATTEMPT 1: Quick Fix                                                  │   │
│  │ • Retry operation (up to 3x with exponential backoff)                 │   │
│  │ • Apply auto-fix if available (e.g., lint fix)                        │   │
│  │ • Rebase if conflict detected                                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ├── Success → Continue                                                 │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ATTEMPT 2: Regenerate                                                 │   │
│  │ • Identify failing files                                              │   │
│  │ • Re-run Claude Code on those files only                              │   │
│  │ • Preserve working files                                              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ├── Success → Continue                                                 │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ATTEMPT 3: Isolate                                                    │   │
│  │ • Split PR into smaller, independent PRs                              │   │
│  │ • Quarantine failing component                                        │   │
│  │ • Proceed with working components                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ├── Success → Continue with partial                                    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ESCALATE TO DASHBOARD                                                 │   │
│  │ • Surface failure with full context                                   │   │
│  │ • Present safe resolution options to user                             │   │
│  │ • Wait for user decision                                              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Failure Budget

Each run has a failure budget to prevent infinite retry loops:

```yaml
failure_budget:
  per_run:
    max_retries: 10
    max_regenerations: 5
    max_split_attempts: 3
    max_quarantines: 5

  per_task:
    max_retries: 3
    max_regenerations: 2
    max_ci_failures: 5

  per_file:
    max_regenerations: 3

  # When budget exhausted
  on_budget_exhausted:
    action: escalate_to_dashboard
    options:
      - retry_with_fresh_budget
      - abort_task
      - abort_run
      - continue_with_failures
```

### Operator Mode Compensating Controls

When running with `--dangerously-skip-permissions`, additional controls compensate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              OPERATOR MODE COMPENSATING CONTROLS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BYPASSED (for automation)       │  STILL ENFORCED (non-negotiable)         │
│  ────────────────────────────────┼───────────────────────────────────────── │
│  Interactive confirmations       │  Audit logging (every action logged)    │
│  Human review of PRs             │  Evidence Pack generation (signed)      │
│  Manual merge approval           │  Policy evaluation (OPA gates)          │
│  File-by-file approval           │  Security scanning (block on critical)  │
│                                  │  Budget circuit breakers                │
│                                  │  Secret isolation (Vault-only)          │
│                                  │  Kill switch availability               │
│                                  │  Merge queue (all checks must pass)     │
│                                  │  CODEOWNERS (still applies)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pre-Execution Validation

Before any task starts:

```python
def pre_execution_validation(task: Task, run: Run) -> ValidationResult:
    """
    Validate task before starting execution.
    """
    checks = []

    # Check 1: Budget available
    budget = get_remaining_budget(run)
    if budget.usd < task.estimated_cost:
        return ValidationResult(
            valid=False,
            reason="Insufficient budget",
            required_action="Approve budget extension or reduce scope"
        )

    # Check 2: No conflicting locks
    locks = get_conflicting_locks(task)
    if locks:
        return ValidationResult(
            valid=False,
            reason=f"Conflicting locks: {locks}",
            required_action="Wait for locks to release or reschedule"
        )

    # Check 3: Dependencies met
    unmet = get_unmet_dependencies(task)
    if unmet:
        return ValidationResult(
            valid=False,
            reason=f"Unmet dependencies: {unmet}",
            required_action="Wait for dependencies or reorder tasks"
        )

    # Check 4: Concurrency limits
    if exceeds_concurrency_limit(task):
        return ValidationResult(
            valid=False,
            reason="Concurrency limit reached",
            required_action="Wait for other tasks to complete"
        )

    # Check 5: Required secrets available
    secrets = get_required_secrets(task)
    if not all_secrets_available(secrets):
        return ValidationResult(
            valid=False,
            reason="Required secrets not available in Vault",
            required_action="Configure secrets before running"
        )

    return ValidationResult(valid=True)
```

#### Post-Execution Validation

After every task:

```python
def post_execution_validation(task: Task, result: TaskResult) -> ValidationResult:
    """
    Validate task output before proceeding.
    """
    # Check 1: All files pass lint
    lint_result = run_lint(result.changed_files)
    if lint_result.errors:
        return ValidationResult(
            valid=False,
            reason="Lint errors",
            auto_fix=lint_result.fixable,
            required_action="Fix lint errors"
        )

    # Check 2: All tests pass
    test_result = run_tests(result.affected_tests)
    if test_result.failures:
        return ValidationResult(
            valid=False,
            reason="Test failures",
            required_action="Fix failing tests"
        )

    # Check 3: Security scan clean
    security_result = run_security_scan(result.changed_files)
    if security_result.critical or security_result.high:
        return ValidationResult(
            valid=False,
            reason="Security findings",
            blocking=True,
            required_action="Security team review required"
        )

    # Check 4: No secrets in code
    secret_result = run_secret_scan(result.changed_files)
    if secret_result.detected:
        return ValidationResult(
            valid=False,
            reason="Secrets detected in code",
            blocking=True,
            required_action="Remove secrets and rotate"
        )

    # Check 5: Evidence Pack generated
    evidence = generate_evidence_pack(task, result)
    if not evidence.valid:
        return ValidationResult(
            valid=False,
            reason="Evidence Pack invalid",
            required_action="Regenerate Evidence Pack"
        )

    return ValidationResult(valid=True)
```

### PR Metadata (Auto-Populated)

Every PR created by Operator Mode includes:

```markdown
## Itqahn Operator Mode PR

### Run Context
| Field | Value |
|-------|-------|
| **Run ID** | `run-01J5ABCD...` |
| **Workflow ID** | `wf-xyz789` |
| **Worktree** | `/worktrees/run-01J5ABCD-user-auth` |
| **Issue** | #42 |
| **Concept Lock** | v1.0.0 |
| **Design OS** | v1.2.0 |

### Risk Assessment
| Risk | Level |
|------|-------|
| **Tier** | T2 (Internal) |
| **Touches Auth** | ❌ No |
| **Database Migration** | ❌ No |
| **Payment Code** | ❌ No |
| **Security Sensitive** | ❌ No |

### Validation Results
| Check | Status |
|-------|--------|
| **Lint** | ✅ Passed |
| **Tests** | ✅ 42/42 passed |
| **Coverage** | ✅ 87.3% |
| **Security Scan** | ✅ 0 critical, 0 high |
| **Design Jail** | ✅ Passed |
| **Policy Check** | ✅ All gates passed |

### Evidence Pack
- Location: `s3://evidence/run-01J5ABCD/evidence.json`
- Digest: `sha256:abc123...`
- Signature: `sigstore://...`

### Artifacts
- [ ] Code changes: 8 files, +245 / -12 lines
- [ ] Tests: 5 new, 2 modified
- [ ] Docs: 1 updated

### Auto-Merge
- [x] Auto-merge enabled
- [x] Will merge when all checks pass
```

### Dashboard Integration

The Operator Mode dashboard shows all parallel runs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PARALLEL RUNS DASHBOARD                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Active Worktrees: 3 / 5                           Cost Today: $127.50      │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Run ID        │ Task           │ Status    │ PR     │ Queue │ Time   │  │
│  │  ──────────────┼────────────────┼───────────┼────────┼───────┼─────── │  │
│  │  run-01J5ABCD  │ User Auth      │ ✓ Merged  │ #156   │ -     │ 45m    │  │
│  │  run-01J5EFGH  │ Dashboard      │ ● Testing │ #157   │ 2     │ 32m    │  │
│  │  run-01J5IJKL  │ Settings       │ ● Building│ -      │ -     │ 15m    │  │
│  │  run-01J5MNOP  │ Notifications  │ ○ Queued  │ -      │ -     │ -      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Legend: ✓ Complete  ● In Progress  ○ Waiting  ✗ Failed                     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  FILE LOCKS                                                             │ │
│  │                                                                         │ │
│  │  🔒 package-lock.json     held by: run-01J5EFGH   expires: 15m         │ │
│  │  🔒 src/api/routes/**     held by: run-01J5IJKL   expires: 30m         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MERGE QUEUE                                                            │ │
│  │                                                                         │ │
│  │  Position 1: #157 (Dashboard)     CI Running ●●●○○                      │ │
│  │  Position 2: #158 (API Endpoints) Waiting                               │ │
│  │  Position 3: #159 (Settings)      Waiting                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [ + Start New Task ]  [ View All Runs ]  [ Manage Locks ]  [ Kill Switch ]│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PR Requirements

### Mandatory PR Contents

| Requirement | Enforcement |
|-------------|-------------|
| Linked issue/ticket | PR template |
| Updated docs (if behavior changes) | CODEOWNERS review |
| Tests (or explicit justification) | CI gate |
| Evidence preview | CI summary comment |

### PR Size Rule

**Prefer multiple small PRs over one large PR.**

| PR Size | Lines Changed | Guidance |
|---------|---------------|----------|
| Small | < 200 | Ideal |
| Medium | 200-500 | Acceptable |
| Large | > 500 | Split if possible |

### PR Template

```markdown
## Summary
<!-- Brief description of changes -->

## Related
- Issue: #123
- PRD: requirements/feature-x.md

## Changes
- [ ] Change 1
- [ ] Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Security Checklist
- [ ] No secrets in code
- [ ] Input validation added
- [ ] Auth/authz unchanged OR reviewed by security

## Evidence
<!-- CI will add evidence summary -->
```

---

## Required Checks

| Check | Tool | Gate Type |
|-------|------|-----------|
| Lint + formatting | ESLint, Prettier | Hard |
| Unit tests | Jest, pytest | Hard |
| Integration tests | Playwright, pytest | Hard (when applicable) |
| SAST | Semgrep | Hard |
| Secret scan | Gitleaks | Hard |
| SCA + license | Snyk, Licensee | Hard |
| Design Jail validator | Custom | Hard (UI changes) |
| Policy evaluation | OPA | Hard |
| Provenance + SBOM | Sigstore, Syft | Hard |
| Drift score | Custom | Soft |

**PR cannot merge if any hard gate fails.**

---

## Merge Strategy

| Repository Type | Strategy | Reason |
|-----------------|----------|--------|
| Application repos | Squash merge | Clean history |
| Infra/policy repos | Merge commit | Audit trail |

### Commit Signing

| Actor | Signing |
|-------|---------|
| Human maintainers | Signed commits (recommended) |
| Agents/bots | Sign artifacts, not commits |

---

## Design OS Repository Model

Design OS is versioned in Git with the same rigor as application code. UI changes must link to specific Design OS versions.

### Repository Options

| Model | When to Use | Example |
|-------|-------------|---------|
| **Monorepo** | Small teams, single product | `design-os/` directory in main repo |
| **Dedicated repo** | Multiple products sharing Design OS | `org/design-os` repository |
| **Per-tenant** | Enterprise multi-tenancy | `org/tenant-abc-design-os` |

### Design OS Versioning

Design OS follows SemVer with strict rules:

| Change Type | Version Bump | Examples |
|-------------|--------------|----------|
| **Breaking** | MAJOR | Token renamed, component removed |
| **Additive** | MINOR | New token, new component |
| **Fix** | PATCH | Value tweak, bug fix |

### Tag Convention

```
design-os/v1.2.3
design-os/v1.2.3-beta.1
design-os/v1.2.3-rc.1
```

### CODEOWNERS for Design OS

```
# Design OS artifacts
/design-os/                @design-team @frontend-architects
/design-os/tokens.json     @design-team
/design-os/components.json @design-team @accessibility-team
/design-os/a11y-rules.md   @accessibility-team
/design-os/patterns/       @design-team @ux-team
```

### UI Change Linkage

Every UI PR must reference its Design OS version:

```yaml
# PR labels
design-os-version: 1.2.3
```

```markdown
## Design OS
- Version: `1.2.3`
- Tokens digest: `sha256:abc123...`
- Components digest: `sha256:def456...`
```

### Design OS CHANGELOG

```markdown
# Design OS Changelog

## [1.2.0] - 2026-01-06

### Added
- New `color.semantic.info` token
- `Tooltip` component with hover/focus triggers

### Changed
- `Button` loading state now uses skeleton animation

### Deprecated
- `color.primary` → use `color.brand.primary` (removed in 2.0.0)

## [1.1.0] - 2025-12-15
...
```

### Release Process

```
1. Design changes approved in Figma
       │
       ▼
2. Figma MCP extracts to PR
       │
       ▼
3. Schema validation passes
       │
       ▼
4. Visual regression baselines updated
       │
       ▼
5. Accessibility audit passes
       │
       ▼
6. CHANGELOG updated
       │
       ▼
7. Version tagged (e.g., design-os/v1.2.0)
       │
       ▼
8. Consuming apps upgrade Design OS dependency
```

---

## Asset Repository Model

Assets generated by Asset Factory are versioned in Git with the same rigor as code.

### Asset Directory Structure

```
assets/
├── specs/                    # Asset generation specifications
│   └── {asset-id}/
│       └── asset-spec.json
├── outputs/                  # Generated asset outputs
│   └── {asset-id}/
│       ├── source.png        # Original generation
│       ├── ios/              # iOS variants
│       ├── android/          # Android variants
│       └── web/              # Web variants
├── manifests/               # Asset manifests with provenance
│   └── {asset-id}/
│       └── asset-manifest.json
├── style-anchors/           # Style anchor definitions (in Design OS)
│   ├── icons/
│   ├── illustrations/
│   └── photos/
└── lint-reports/            # Asset lint results
    └── {asset-id}/
        └── lint-report.json
```

### Asset Naming Convention

| Asset Type | Naming Pattern | Example |
|------------|----------------|---------|
| App icon | `{app-name}-icon` | `task-manager-icon` |
| Feature icon | `{feature}-icon` | `notifications-icon` |
| Illustration | `{scene}-illustration` | `onboarding-welcome-illustration` |
| Photo | `{subject}-photo` | `team-collaboration-photo` |
| Badge | `{type}-badge` | `premium-badge` |

### Asset Versioning

Assets follow SemVer:

| Change Type | Version Bump | Examples |
|-------------|--------------|----------|
| **Breaking** | MAJOR | Completely different design |
| **Visual update** | MINOR | Color change, style refresh |
| **Fix** | PATCH | Bug fix, format correction |

### Tag Convention

```
assets/{asset-name}/v1.2.3
assets/{asset-name}/v1.2.3-draft.1
```

### CODEOWNERS for Assets

```
# Asset artifacts
/assets/                    @design-team @asset-factory
/assets/specs/              @design-team
/assets/style-anchors/      @design-team @design-guardian
/design-os/style-anchors/   @design-team @design-guardian
```

### Asset PR Template

```markdown
## Asset Request
- Asset ID: `ast-abc123`
- Type: App Icon / Illustration / Photo / Badge
- Style Anchor: `icons/modern-flat`

## Design OS
- Version: `1.2.0`
- Tokens digest: `sha256:abc123...`

## Validation
- [ ] Lint passed (palette, format, dimensions)
- [ ] Drift score: 0.08 (threshold: 0.25)
- [ ] License verified
- [ ] Registered in Asset Registry

## Platform Outputs
- [ ] iOS asset catalog generated
- [ ] Android adaptive icon generated
- [ ] Web variants generated

## Evidence
- Manifest: `assets/manifests/ast-abc123/asset-manifest.json`
- Lint report: `assets/lint-reports/ast-abc123/lint-report.json`
```

---

## Attestation Linkage

Every merge must be associated with:

| Data | Location |
|------|----------|
| Workflow ID | PR description or labels |
| Agent role(s) | Commit metadata |
| Model versions | Evidence Pack |
| Policy verdict IDs | CI summary |
| Evidence Pack location | Release metadata |

### Linkage in PR

```yaml
# Labels
workflow-id: wf-xyz789
agent: backend-builder
tier: sensitive

# Evidence comment (added by CI)
## Evidence Summary
- SBOM: ✅ Generated
- Provenance: ✅ Signed
- Security scan: ✅ 0 critical, 0 high
- Tests: ✅ 245 passed
- Coverage: ✅ 85.2%
- Policy: ✅ All gates passed
- Evidence Pack: s3://evidence/user-service/1.2.3/build-abc123
```

---

## GitOps Deployment

### Model

```
1. PR merged to main
       │
       ▼
2. CI generates Evidence Pack
       │
       ▼
3. Update infra repo with new image tag
       │
       ▼
4. ArgoCD detects change
       │
       ▼
5. Admission control verifies Evidence Pack
       │
       ▼
6. Canary deployment begins
       │
       ▼
7. SLO analysis
       │
       ├── Pass → Promote to 100%
       │
       └── Fail → Automatic rollback
```

### Rollback

Rollback options:
1. **Git revert**: Revert the merge commit
2. **ArgoCD rollback**: Roll back to previous sync
3. **Manual**: Apply previous manifest

---

## GitHub/GitLab Configuration

### Branch Protection (main)

```yaml
branch_protection:
  main:
    required_status_checks:
      strict: true
      contexts:
        - lint
        - test
        - security-scan
        - policy-check
    required_pull_request_reviews:
      required_approving_review_count: 1
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
    restrictions:
      users: []
      teams: []
    enforce_admins: true
    allow_force_pushes: false
    allow_deletions: false
```

### CODEOWNERS

```
# Default owner
* @platform-team

# Security-critical paths
/auth/** @security-team
/policies/** @security-team @compliance-team

# Infrastructure
/infra/** @platform-team @sre-team

# Service-specific
/services/user-service/** @identity-team
/services/payment-service/** @payments-team @security-team
```

---

## Templates

- PR template: `templates/github/PULL_REQUEST_TEMPLATE.md`
- CODEOWNERS: `templates/github/CODEOWNERS`
- Issue templates: `templates/github/ISSUE_TEMPLATE/`

---

## Claude Code Automation Backbone

Itqahn uses Claude Code as the execution engine for all agent work. Git serves as the backbone connecting parallel Claude Code sessions to a coherent, traceable workflow.

### Core Principle: Git as Coordination Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                CLAUDE CODE ↔ GIT COORDINATION MODEL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         COORDINATOR                                    │  │
│  │                                                                         │  │
│  │  • Spawns Claude Code workers in isolated worktrees                    │  │
│  │  • Creates all Git artifacts (branches, issues, PRs)                   │  │
│  │  • Manages file locks to prevent conflicts                             │  │
│  │  • Aggregates results and triggers merges                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│       ┌──────────────────────────────┼──────────────────────────────┐       │
│       ▼                              ▼                              ▼       │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐ │
│  │  WORKTREE 1  │             │  WORKTREE 2  │             │  WORKTREE 3  │ │
│  │              │             │              │             │              │ │
│  │ Claude Code  │             │ Claude Code  │             │ Claude Code  │ │
│  │ Session      │             │ Session      │             │ Session      │ │
│  │              │             │              │             │              │ │
│  │ Branch:      │             │ Branch:      │             │ Branch:      │ │
│  │ feat/run-A-1 │             │ feat/run-A-2 │             │ feat/run-A-3 │ │
│  └──────────────┘             └──────────────┘             └──────────────┘ │
│       │                              │                              │       │
│       ▼                              ▼                              ▼       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                            GIT REPOSITORY                                ││
│  │                                                                          ││
│  │  .git/ (shared)                                                          ││
│  │  ├── worktrees/ (tracking)                                               ││
│  │  └── refs/ (branches from all workers)                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│                        ┌──────────────────────────┐                         │
│                        │      MERGE QUEUE         │                         │
│                        │   (Sequential merge)     │                         │
│                        └──────────────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Worktree Branch Strategy

Each Claude Code worker operates in an isolated Git worktree with its own branch:

| Entity | Naming Convention | Example |
|--------|-------------------|---------|
| **Worktree directory** | `/worktrees/run-{run_id}-{task_slug}` | `/worktrees/run-01J5ABCD-user-auth` |
| **Worker branch** | `feat/run-{run_id}-{task_slug}` | `feat/run-01J5ABCD-user-auth` |
| **Coordinator branch** | `run/{run_id}/coordinator` | `run/01J5ABCD/coordinator` |

**Worktree lifecycle:**

```bash
# 1. Coordinator creates worktree for worker
git worktree add /worktrees/run-01J5ABCD-user-auth -b feat/run-01J5ABCD-user-auth

# 2. Worker operates entirely within its worktree
cd /worktrees/run-01J5ABCD-user-auth
claude --dangerously-skip-permissions

# 3. Worker commits with conventional format
git commit -m "feat(auth): add login form [run-01J5ABCD #42]"

# 4. Worker pushes and creates PR
git push -u origin feat/run-01J5ABCD-user-auth
gh pr create --title "[run-01J5ABCD] User Auth" --body "..."

# 5. After merge, coordinator cleans up
git worktree remove /worktrees/run-01J5ABCD-user-auth
```

### PR Strategy: One PR per Work Item

Each worker creates exactly one PR per work item:

```yaml
pr_strategy:
  one_pr_per_work_item: true

  pr_creation:
    trigger: worker_build_complete
    template: .github/PULL_REQUEST_TEMPLATE/operator-mode.md
    auto_merge: enabled
    reviewers: none  # Operator Mode bypasses manual review
    labels:
      - "auto-generated"
      - "run-{run_id}"
      - "concept-lock-{version}"

  pr_lifecycle:
    created_by: worker
    checks_run_by: ci
    merged_by: merge_queue
    cleanup_by: coordinator
```

### Commit Conventions (Machine-Readable)

All commits MUST follow this format for automated parsing:

```
{type}({scope}): {description} [run-{run_id} #{issue}]

Types:
  feat     New feature
  fix      Bug fix
  docs     Documentation
  style    Formatting
  refactor Code restructure
  test     Tests
  chore    Maintenance

Examples:
  feat(auth): implement login form [run-01J5ABCD #42]
  fix(auth): correct validation logic [run-01J5ABCD #42]
  test(auth): add unit tests for login [run-01J5ABCD #42]
```

**Parsing regex:**
```regex
^(?<type>\w+)\((?<scope>[^)]+)\): (?<description>.+) \[run-(?<run_id>\w+) #(?<issue>\d+)\]$
```

### Auto-Issue Creation Rules

Itqahn creates all GitHub issues programmatically:

| Issue Type | Created When | Created By | Linked To |
|------------|--------------|------------|-----------|
| **Epic Issue** | Run starts | Coordinator | Concept Lock |
| **Work Item Issue** | Task assigned | Coordinator | Epic, Journey |
| **Bug Issue** | Test failure | CI | PR, Work Item |
| **Incident Issue** | Security alert | Security scan | Run, Evidence |

**Issue creation is forbidden for users in Operator Mode.**

### Merge Policy

```yaml
merge_policy:
  method: squash

  required_before_merge:
    - all_checks_pass: true
    - verification_report_exists: true
    - evidence_pack_generated: true
    - no_conflicts: true

  auto_merge:
    enabled: true
    conditions:
      - branch_pattern: "feat/run-*"
      - label: "auto-generated"
      - all_checks_pass: true

  merge_queue:
    enabled: true
    build_on_merge_commit: true
    max_entries: 5
```

### Dashboard ↔ Git Entity Mapping

| Dashboard Entity | Git Entity | Relationship |
|------------------|------------|--------------|
| **Run** | Epic Issue + branches | Run spawns Epic + N work branches |
| **Task** | Work Item Issue + branch | Task = Issue + PR workflow |
| **Worker** | Worktree | 1:1 worker-to-worktree mapping |
| **PR** | Pull Request | Worker creates, merge queue processes |
| **Merge** | Squash commit to main | Auto-merge on check pass |
| **Release** | Tag + GitHub Release | Created on milestone completion |

### Conflict Recovery Protocol

When merge conflicts occur between parallel workers:

```
CONFLICT DETECTED
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 1: IDENTIFY CONFLICT TYPE                              │
│                                                              │
│  Simple (< 3 files, non-overlapping logic):                  │
│  └── Proceed to auto-rebase                                  │
│                                                              │
│  Complex (overlapping logic, semantic conflict):             │
│  └── Proceed to serialization                                │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: AUTO-REBASE ATTEMPT                                 │
│                                                              │
│  git fetch origin main                                       │
│  git rebase origin/main                                      │
│                                                              │
│  Success → Continue to merge queue                           │
│  Failure → Proceed to regeneration                           │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: REGENERATE CONFLICTING FILES                        │
│                                                              │
│  • Identify conflicting files                                │
│  • Re-run Claude Code on those files only                    │
│  • Preserve non-conflicting work                             │
│                                                              │
│  Success → Continue to merge queue                           │
│  Failure → Proceed to serialization                          │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: SERIALIZE CONFLICTING TASKS                         │
│                                                              │
│  • Pause later-priority worker                               │
│  • Let earlier-priority worker merge first                   │
│  • Resume paused worker with rebased branch                  │
│                                                              │
│  Success → Merge in order                                    │
│  Failure → Escalate to dashboard                             │
└──────────────────────────────────────────────────────────────┘
```

### Safe Revert Procedure

When a merged PR causes issues:

```bash
# 1. Identify the merge commit
MERGE_COMMIT=$(git log --oneline main | grep "run-{run_id}" | head -1 | cut -d' ' -f1)

# 2. Create revert commit
git revert -m 1 $MERGE_COMMIT

# 3. Push revert
git push origin main

# 4. Create incident issue
gh issue create \
  --title "[REVERT] Reverting run-{run_id} due to {reason}" \
  --body "Reverted commit: $MERGE_COMMIT\nReason: {reason}\nRun ID: {run_id}"

# 5. Update Evidence Pack with revert record
```

### Git Worktrees as Parallelism Primitive

Worktrees are the **canonical mechanism** for parallel Claude Code execution:

```yaml
worktree_policy:
  max_per_run: 5
  max_per_repo: 10
  timeout_hours: 4

  creation:
    trigger: task_assignment
    creator: coordinator
    isolation: complete  # No shared working directory

  lifecycle:
    created: on_task_start
    active: during_task_execution
    removed: after_pr_merge

  cleanup:
    automatic: true
    trigger: pr_merged OR timeout_exceeded OR run_cancelled
    preserve_on_failure: true  # For debugging
```

**Worktree isolation guarantees:**
- Each worker has exclusive access to its worktree
- No file system contention between workers
- Separate branch per worktree
- Independent `node_modules` / dependencies if needed
- Clean state on creation

---

## PRP-Based Git Workflow

The Context Engineering Program ties Git operations directly to PRP (Product Requirements Prompt) lifecycle.

### PRP-to-Branch Mapping

Every PRP execution maps to a dedicated branch:

| PRP State | Git State |
|-----------|-----------|
| PRP created | No branch yet |
| PRP approved | Branch created: `prp/run-{run_id}-{prp_slug}` |
| PRP executing | Commits on branch |
| PRP validated | PR created, gates passing |
| PRP completed | PR merged, branch deleted |
| PRP abandoned | Branch deleted, no PR |

### Branch Naming for PRPs

```yaml
# PRP-based branch naming
prp_branches:
  # Standard PRP work
  pattern: "prp/run-{run_id}-{prp_slug}"
  example: "prp/run-01J5ABCD-user-auth-form"

  # Sub-PRPs (task splits)
  sub_pattern: "prp/run-{run_id}-{prp_slug}-{sub_id}"
  example: "prp/run-01J5ABCD-user-auth-form-validation"

  # Integration branch for parallel PRPs
  integration_pattern: "integration-{run_id}"
  example: "integration-01J5ABCD"
```

### PRP-to-Issue Linking

Every PRP creates a linked GitHub issue:

```yaml
# PRP Issue (auto-created)
issue:
  title: "[PRP] {prp_title}"
  labels: ["prp", "itqahn-generated", "run-{run_id}"]
  body: |
    ## PRP Reference
    - ID: {prp_id}
    - INITIAL: #{initial_issue}
    - Concept Lock: v{version}

    ## Acceptance Criteria
    {acceptance_criteria_list}

    ## Validation Gates
    {gates_list}

    ## Files to Change
    {files_list}

  # Linked automatically
  linked_pr: #{pr_number}
  parent_epic: #{epic_issue}
```

### Commit Message with PRP Reference

```
{type}({scope}): {description} [prp-{id} #{issue}]

Examples:
feat(auth): add login form validation [prp-01J5XYZ #156]
fix(auth): correct email regex [prp-01J5XYZ #156]
test(auth): add login form tests [prp-01J5XYZ #156]
```

---

## No Human Manual Git Work Policy

In Operator Mode, **users NEVER manually create or manage Git artifacts**. All Git operations are system-owned.

### Policy Enforcement

| Git Operation | Manual Allowed | System-Only |
|---------------|----------------|-------------|
| Create issue | No | Yes (from INITIAL/PRP) |
| Create branch | No | Yes (from PRP approval) |
| Push commits | No | Yes (from PRP execution) |
| Create PR | No | Yes (from validation pass) |
| Add labels | No | Yes (automated) |
| Enable auto-merge | No | Yes (automated) |
| Merge PR | No | Yes (via merge queue) |
| Create release | No | Yes (from milestone completion) |
| Create tag | No | Yes (from release) |

### Dashboard as the Only Interface

Users interact with Git **only through the dashboard**:

| User Action (Dashboard) | System Response (Git) |
|-------------------------|-----------------------|
| "New Feature" button | Creates INITIAL issue |
| "Approve PRP" button | Creates branch from PRP |
| "Execute PRP" button | Commits code to branch |
| "Validate" button | Runs gates, reports status |
| "View PR" link | Opens GitHub PR (read-only) |
| "Approve Merge" button | Enters merge queue |
| "Rollback" button | Reverts to checkpoint |
| "Release" button | Creates tag + release |

### Why No Manual Git

| Manual Action | Risk | Mitigation |
|---------------|------|------------|
| Manual issue | No PRP linkage, untracked scope | Block via CODEOWNERS |
| Manual branch | Outside run, no evidence | Branch protection rules |
| Manual commit | No run ID, no audit trail | Commit lint enforcement |
| Manual PR | No auto-merge, no gates | Require labels |
| Manual merge | Bypass merge queue | Require merge queue |

### Exceptions (Rare)

Manual Git work is allowed ONLY for:

| Exception | When | Approval Required |
|-----------|------|-------------------|
| Emergency hotfix | Production down | On-call lead |
| Security patch | Critical CVE | Security team |
| CI infrastructure | Pipeline broken | Platform team |

Emergency exceptions MUST:
- Create issue first (even if manual)
- Follow commit format with `[hotfix #{issue}]`
- Create PR (even if fast-merged)
- Generate Evidence Pack after the fact
- Document in incident report

---

## Related Documents

- `docs/00-overview/principles.md` — GitHub as System of Record principle
- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 and Concept Lock definition
- `docs/01-product/requirements-schema.md` — Phase 1 output schemas
- `docs/03-platform/ci-cd-gitops.md` — CI/CD details
- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/portal-webapp.md` — Operator Mode dashboard, Parallel Runs UI
- `docs/03-platform/track-assurance.md` — Assurance branch conventions, drift-triggered checkpoints
- `docs/03-platform/legacy-rebuild.md` — Rebuild branch conventions, legacy snapshot tags
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/05-compliance/evidence-pack.md` — Git Evidence requirements
- `docs/06-operations/runbooks.md` — Worktree, Merge Queue, and Flaky Test runbooks
- `docs/06-operations/claude-code-operating-model.md` — Claude Code execution model
- `docs/06-operations/context-engineering-playbook.md` — Context engineering practices
- `docs/03-platform/context-engineering.md` — Context Engineering Program and PRP workflow
- `docs/06-operations/itqahn-continuous-improvement.md` — Improvement PR workflow
- `docs/07-integrations/webhooks-events.md` — GitHub event taxonomy
- `docs/07-integrations/mcp/mcp-github.md` — GitHub MCP
- `docs/07-integrations/mcp/mcp-figma.md` — Figma extraction pipeline
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/08-agents/agent-permissions.md` — Git Orchestrator and bot permissions
- `CLAUDE.md` — Root rules file for Claude Code sessions

---

**Version**: 2.7.0 | **Date**: 2026-01-08
