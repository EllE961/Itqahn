# Runbooks

Runbooks are executable knowledge. They define what actions are safe to take and how to perform them.

---

## Runbook Standards

Every runbook must include:

| Section | Purpose |
|---------|---------|
| **Purpose and Scope** | What this runbook covers |
| **Detection Signals** | How to know this runbook applies |
| **Prerequisites** | Access and tools needed |
| **Safe Mitigation Steps** | Actions to resolve the issue |
| **Rollback Steps** | How to undo actions |
| **Escalation Criteria** | When to escalate |
| **Verification Steps** | How to confirm resolution |

---

## Runbook Template

```markdown
# Runbook: [Service] - [Issue Type]

## Purpose and Scope
What this runbook addresses and when to use it.

## Detection Signals
- Alert: `alert-name`
- Dashboard: [link]
- Symptoms: [description]

## Prerequisites
- [ ] Access to Kubernetes cluster
- [ ] Vault read access for service secrets
- [ ] PagerDuty responder role

## Severity Assessment
| Condition | Severity |
|-----------|----------|
| Complete outage | P0 |
| >50% error rate | P1 |
| <50% error rate | P2 |

## Safe Mitigation Steps

### Step 1: Verify the Issue
```bash
kubectl get pods -n user-service
kubectl logs -n user-service deployment/user-service --tail=100
```

Expected output: [description]
If unexpected: escalate to [team]

### Step 2: Apply Mitigation
```bash
kubectl rollout restart deployment/user-service -n user-service
```

Expected: Pods restart within 2 minutes.
If not: proceed to Step 3.

### Step 3: Rollback (if needed)
```bash
kubectl rollout undo deployment/user-service -n user-service
```

## Escalation Criteria
Escalate immediately if:
- Mitigation doesn't resolve within 15 minutes
- Issue affects multiple services
- Data integrity concerns
- Security implications

Escalation path:
1. Team lead: @team-lead
2. Engineering director: @eng-director
3. On-call executive: @exec-oncall

## Verification Steps
- [ ] Error rate returned to <0.1%
- [ ] p99 latency <500ms
- [ ] No error logs in last 5 minutes
- [ ] Health check passing

## Post-Resolution
- Update incident timeline
- Notify CL for status page update
- Schedule postmortem if criteria met
```

---

## Auto-Remediation Boundary

### Automation IS Allowed For

| Action Type | Conditions |
|-------------|------------|
| **Reversible** | Can be undone without data loss |
| **Verified** | Clear success/failure criteria |
| **Bounded** | Limited blast radius |
| **Documented** | Runbook exists |

Examples:
- Restart pods
- Scale replicas up/down
- Clear caches
- Rotate credentials (if automated)
- Enable/disable circuit breakers

### Automation IS NOT Allowed For

| Action Type | Reason |
|-------------|--------|
| **Destructive data** | Cannot be undone |
| **Security-sensitive** | Requires human judgment |
| **Ambiguous** | Unclear what to do |
| **Cross-tenant** | Risk of wider impact |

Examples:
- Delete databases
- Modify production data
- Change security policies
- Deploy new code
- Grant/revoke access

---

## Runbook Categories

### Service Runbooks

Located: `runbooks/services/{service-name}/`

| Runbook | Trigger |
|---------|---------|
| `high-error-rate.md` | Error rate alert |
| `high-latency.md` | Latency alert |
| `pod-crash-loop.md` | CrashLoopBackOff |
| `memory-pressure.md` | OOM events |
| `database-connection.md` | DB connection errors |

### Infrastructure Runbooks

Located: `runbooks/infra/`

| Runbook | Trigger |
|---------|---------|
| `node-not-ready.md` | Node health alert |
| `cluster-autoscaler.md` | Scaling issues |
| `network-policy.md` | Connectivity issues |
| `certificate-expiry.md` | Cert expiring alert |

### Security Runbooks

Located: `runbooks/security/`

| Runbook | Trigger |
|---------|---------|
| `credential-leak.md` | Secret exposed |
| `suspicious-access.md` | Anomaly detected |
| `vulnerability-critical.md` | Critical CVE |
| `incident-containment.md` | Security incident |

### Design OS Runbooks

Located: `runbooks/design-os/`

| Runbook | Trigger |
|---------|---------|
| `visual-regression-failure.md` | Visual regression suddenly fails |
| `token-change-breakage.md` | Token change breaks production UI |
| `accessibility-regression.md` | WCAG violations in production |
| `design-drift-critical.md` | Drift score exceeds threshold |

### Asset Factory Runbooks

Located: `runbooks/assets/`

| Runbook | Trigger |
|---------|---------|
| `asset-drift-failure.md` | Asset drift exceeds threshold |
| `asset-lint-failure.md` | Asset fails palette/format validation |
| `asset-generation-stuck.md` | Generation workflow hung |
| `asset-budget-exceeded.md` | Cost budget exceeded |
| `asset-provider-outage.md` | Generation provider unavailable |
| `style-anchor-corruption.md` | Style anchor embedding invalid |

### Phase 1 / Intake Runbooks

Located: `runbooks/intake/`

| Runbook | Trigger |
|---------|---------|
| `interview-abandonment.md` | User abandons interview mid-flow |
| `conflicting-constraints.md` | User selections conflict with each other |
| `missing-asset-info.md` | Asset requirements incomplete at lock |
| `high-assumption-count.md` | >30% "Not sure" responses |
| `concept-lock-failure.md` | Concept Lock validation fails |
| `change-request-blocked.md` | CR blocked by policy or conflict |

---

## Phase 1 Intake Incident Runbook

### Runbook: Phase 1 UX/Intake Failure

```markdown
# Runbook: Phase 1 - Intake/Interview Failure

## Purpose and Scope
This runbook addresses scenarios where users encounter failures during the Phase 1
Adaptive Interview, including abandonment, conflicting constraints, missing asset
information, and Concept Lock validation failures.

## Detection Signals
- Alert: `phase1-interview-abandonment`
- Alert: `phase1-constraint-conflict`
- Alert: `phase1-lock-failure`
- Dashboard: Phase 1 analytics shows high drop-off
- User support tickets about interview issues

## Prerequisites
- [ ] Access to Phase 1 interview dashboard
- [ ] Access to interview session logs
- [ ] Access to Concept Lock validation logs
- [ ] User support communication channel

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Multiple users blocked from locking | P1 |
| Single user blocked, workaround available | P2 |
| UX friction, not blocking | P3 |

## Scenario 1: User Abandons Interview

### Detection
- Interview session inactive > 30 minutes
- User navigates away without saving
- Session auto-expired

### Diagnosis
Check interview state:
- Dashboard → Phase 1 → Incomplete Sessions
- Filter by session ID or user email

Identify abandonment point:
- Which module was in progress?
- How many questions completed?
- Any errors logged?

### Recovery Steps

**Step 1: Check if session is recoverable**
```
1. Go to Dashboard → Phase 1 → Session Recovery
2. Search for user email or session ID
3. Check "Draft Status" field
```

If draft exists:
- User can resume from email link
- Session state preserved for 30 days
- Send reminder email with resume link

If no draft (session lost):
- User must restart interview
- Consider fast-path mode suggestion
- Log incident for UX improvement

**Step 2: Contact user (if needed)**
```
Email template: interview-recovery-assistance

"Your project interview is saved as draft.
Resume here: [link]
Your progress: [X/Y modules completed]
Time to complete: ~[N] minutes"
```

**Step 3: Escalate if systematic**
If abandonment rate > 15% at specific question:
- Review question clarity
- Check for UX issues
- Consider adding defaults or explanations

---

## Scenario 2: Conflicting Constraints

### Detection
- Validation error: "Conflicting selections"
- User receives constraint conflict notification
- Multiple "Not sure" selections creating invalid state

### Diagnosis
Common conflicts:

| Conflict | Example | Resolution |
|----------|---------|------------|
| Region + Compliance | EU selected but no GDPR acknowledged | Auto-enable GDPR |
| Platform + Assets | iOS selected but no app icon requirements | Prompt for icons |
| Journey + Auth | Payment journey but no auth selected | Require auth selection |
| Typography + RTL | Custom font + Arabic language | Warn about RTL support |

### Recovery Steps

**Step 1: Identify conflict**
```
1. Dashboard → Phase 1 → Validation Errors
2. Find session with conflict error
3. Review conflict type and affected fields
```

**Step 2: Resolve conflict**

For auto-resolvable conflicts:
- System auto-applies safe resolution
- User notified with explanation
- Log assumption if needed

For user-required conflicts:
- Present clear options to user
- Explain why selections conflict
- Offer to revert one selection

**Step 3: Prevent future conflicts**
- Add validation to question branching
- Improve "Why we ask this" explanations
- Consider smart defaults based on common patterns

---

## Scenario 3: Missing Asset Information

### Detection
- Concept Lock validation warning: "Asset requirements incomplete"
- User attempts lock with empty asset manifest
- Asset fields marked "Not sure" > 50%

### Diagnosis
Check which assets are missing:
- Logo requirements (variants, formats)
- App icon requirements (if mobile)
- Favicon requirements (if web)
- UI icon policy

### Recovery Steps

**Step 1: Present minimal asset requirements**
```
Minimum viable asset set:
- Logo: primary + inverted variants, SVG format
- App Icon: if mobile_app in platforms (required)
- Favicon: if web in platforms (required)
- UI Icons: suggest library (Lucide) as default
```

**Step 2: Allow lock with explicit acknowledgment**
If user insists on proceeding:
- Show clear warning about missing assets
- Require explicit confirmation checkbox
- Log high-risk assumption
- Set resolution deadline to Gate 2

**Step 3: Provide asset guidance**
```
"You haven't specified brand assets. You can:
☐ Upload logo now (recommended)
☐ Use Itqahn to generate brand assets (adds ~$50)
☐ Defer to later (requires confirmation)"
```

---

## Scenario 4: High Assumption Count (>30%)

### Detection
- Interview progress shows >30% "Not sure" responses
- Confidence meter drops below threshold
- Concept Lock blocked due to assumption limit

### Diagnosis
Review assumptions:
- Which modules have most "Not sure"?
- Are they high-risk or low-risk assumptions?
- Are safe defaults being applied?

### Recovery Steps

**Step 1: Prioritize assumption resolution**
```
1. Dashboard → Phase 1 → Assumptions Register
2. Sort by risk_level DESC
3. Focus on high-risk items first
```

High-risk (must resolve before lock):
- Auth requirements
- Compliance tier
- Data classification
- Payment requirements

Medium-risk (can defer to Gate 2):
- Specific asset styles
- Optional features
- Nice-to-have journeys

Low-risk (safe defaults exist):
- Typography scale
- Corner style
- Density preference

**Step 2: Guide user through resolution**
```
"You have 12 unanswered questions (32%). To proceed:

Must resolve (3):
☐ Will your app handle payments? [Yes/No]
☐ What data sensitivity level? [Select]
☐ What authentication method? [Select]

Can defer with defaults (9):
☑ Use recommended typography (Inter)
☑ Use recommended density (comfortable)
☑ Use recommended icon library (Lucide)
..."
```

**Step 3: Allow partial lock with plan**
If user needs to proceed:
- Lock with assumptions documented
- Set explicit resolution deadlines
- Block Gate 2 if high-risk items unresolved

---

## Scenario 5: Concept Lock Validation Failure

### Detection
- Lock button returns error
- Validation API returns 4xx error
- Schema validation fails

### Diagnosis
Check validation logs:
```
1. Dashboard → Phase 1 → Lock Attempts
2. Find failed attempt by session ID
3. Review validation_errors array
```

Common failures:
- Schema validation: missing required fields
- Budget validation: exceeds tenant limits
- Policy validation: domain filter rejects scope
- Signature validation: user approval missing

### Recovery Steps

**Step 1: Address specific validation error**

Schema errors:
- Identify missing/invalid fields
- Return user to relevant module
- Pre-fill valid data, highlight errors

Budget errors:
- Show budget breakdown
- Suggest scope reduction
- Request budget increase from tenant admin

Policy errors:
- Explain which policy denied
- Offer compliant alternatives
- Escalate if policy seems incorrect

**Step 2: Retry lock**
After corrections:
- Re-run validation
- Show success/failure clearly
- Provide specific next steps

## Escalation Criteria

Escalate immediately if:
- >5 users blocked in same way (systematic issue)
- Validation logic appears broken
- Budget system returning incorrect limits
- Policy engine misconfigured

Escalation path:
1. Product Support: @product-support
2. Phase 1 Engineering: @phase1-team
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] User can resume/complete interview
- [ ] Conflicting constraints resolved
- [ ] Asset requirements captured (or acknowledged)
- [ ] Assumption count below threshold
- [ ] Concept Lock successfully created
- [ ] All validation checks passing

## Post-Resolution

- Update incident timeline
- If systematic UX issue, file improvement ticket
- If policy misconfiguration, update policies
- Schedule postmortem if P1/P2
```

---

## Design OS Incident Runbook

### Runbook: Visual Regression Failure

```markdown
# Runbook: Design OS - Visual Regression Failure

## Purpose and Scope
This runbook addresses scenarios where visual regression tests suddenly fail,
blocking UI deployments or indicating unintended UI changes.

## Detection Signals
- Alert: `visual-regression-failure`
- CI status: Visual regression check failed
- Drift score: > 0.25

## Prerequisites
- [ ] Access to CI pipeline logs
- [ ] Access to visual regression report (Chromatic/Playwright)
- [ ] Design OS repository access
- [ ] Figma file access (if sync issue)

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Production UI broken | P0 |
| All PRs blocked | P1 |
| Single PR blocked | P2 |

## Safe Mitigation Steps

### Step 1: Identify the Failure Type

Check the visual regression report:

```bash
# Download report
curl -O $CI_ARTIFACTS_URL/visual-regression.html

# Check diff count
jq '.screenshots_changed' visual-regression-summary.json
```

Failure types:
- **Intentional change**: Design OS updated, baselines need refresh
- **Unintentional regression**: Code change broke UI
- **Flaky test**: Animation/timing issue

### Step 2: For Intentional Changes

If Design OS was updated and baselines need refresh:

```bash
# Update baselines
npx playwright test --update-snapshots

# Or via Chromatic
npx chromatic --accept-changes
```

Then:
1. Review new baselines in PR
2. Get Design OS Maintainer approval
3. Merge baseline updates

### Step 3: For Unintentional Regressions

If UI changed unexpectedly:

```bash
# Find the offending commit
git log --oneline -10 -- src/

# Check for CSS/styling changes
git diff HEAD~1 -- "*.css" "*.tsx" "*.ts" | grep -E "style|color|padding"
```

Then:
1. Revert the offending change
2. Open bug ticket for proper fix
3. Re-run visual regression

### Step 4: For Token Change Breakage

If a Design OS token change broke UI:

```bash
# Check token diff
git diff HEAD~1 -- design-os/tokens.json

# Find usages
grep -r "old-token-name" src/
```

Options:
1. **Rollback Design OS**: Revert to previous version
2. **Fix consumers**: Update code to use new token
3. **Add compatibility**: Keep old token as alias

### Step 5: Emergency Rollback

If production is affected:

```bash
# Rollback to last known good Design OS version
git checkout design-os/v1.1.0 -- design-os/

# Or rollback the deployment
kubectl rollout undo deployment/frontend -n production
```

## Escalation Criteria

Escalate immediately if:
- Production UI is broken (P0)
- Multiple tenants affected
- Cannot identify root cause within 30 minutes
- Design OS corruption suspected

Escalation path:
1. Design OS Maintainer: @design-os-team
2. Frontend Architect: @frontend-architects
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Visual regression tests passing
- [ ] No screenshot diffs in report
- [ ] Drift score < 0.1
- [ ] Accessibility tests passing
- [ ] Production UI matches Design OS baselines

## Post-Resolution

- Update incident timeline
- If caused by Design OS change, update CHANGELOG
- If caused by process gap, update this runbook
- Schedule postmortem if P0/P1
```

---

## Asset Factory Incident Runbook

### Runbook: Asset Drift Failure

```markdown
# Runbook: Asset Factory - Asset Drift Failure

## Purpose and Scope
This runbook addresses scenarios where generated assets exceed drift thresholds,
indicating style mismatch from the approved style anchor.

## Detection Signals
- Alert: `asset-drift-exceeded`
- CI status: Asset validation check failed
- Drift score: > 0.25 (hard threshold) or > 0.15 (soft threshold)

## Prerequisites
- [ ] Access to Asset Factory dashboard
- [ ] Access to Assets MCP operations
- [ ] Design OS repository access
- [ ] Style anchor repository access

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Production assets affected | P0 |
| All asset generations blocked | P1 |
| Single asset blocked | P2 |

## Safe Mitigation Steps

### Step 1: Identify the Drift Cause

Check the drift report:

```bash
# View drift details from Asset Factory dashboard
# Or query via API:
curl -X GET https://assets.itqahn.io/api/v1/assets/{asset-id}/drift
```

Drift causes:
- **Style anchor mismatch**: Asset doesn't match selected anchor
- **Palette violation**: Colors outside Design OS tokens
- **Generation variance**: Model produced unexpected style
- **Stale style anchor**: Anchor embedding outdated

### Step 2: For Style Anchor Mismatch

If asset doesn't match style anchor:

```bash
# Regenerate with correct anchor
curl -X POST https://assets.itqahn.io/api/v1/assets/regenerate \
  -d '{"asset_id": "ast-abc123", "style_anchor": "icons/modern-flat"}'
```

Or via Portal:
1. Navigate to Assets Dashboard → Asset Detail
2. Click "Regenerate with Different Anchor"
3. Select correct style anchor
4. Submit regeneration request

### Step 3: For Palette Violations

If colors are outside Design OS palette:

```bash
# Run repair to adjust colors
curl -X POST https://assets.itqahn.io/api/v1/assets/repair \
  -d '{"asset_id": "ast-abc123", "repair_type": "palette"}'
```

If repair fails:
1. Review Design OS palette in tokens.json
2. Update asset spec with correct palette constraints
3. Regenerate asset

### Step 4: For Generation Variance

If model produced unexpected style:

Options:
1. **Retry with different seed**
   ```bash
   curl -X POST https://assets.itqahn.io/api/v1/assets/regenerate \
     -d '{"asset_id": "ast-abc123", "seed": "random"}'
   ```

2. **Switch to different model**
   - Update asset spec to use alternate model
   - Regenerate

3. **Update style anchor** (requires Design Guardian approval)
   - If new style is acceptable, create new style anchor
   - Submit PR to design-os/style-anchors/

### Step 5: Emergency Override

If production is blocked and drift is acceptable:

```bash
# Approve drift exception (requires Design Guardian approval)
curl -X POST https://assets.itqahn.io/api/v1/assets/{asset-id}/approve-exception \
  -d '{"reason": "...", "approver": "design-guardian"}'
```

**Note**: Exception approvals are logged and require justification.

## Escalation Criteria

Escalate immediately if:
- Multiple assets affected (batch failure)
- Style anchor appears corrupted
- Cannot identify root cause within 30 minutes
- Budget being consumed by repeated regenerations

Escalation path:
1. Design Guardian: @design-team
2. Asset Factory Maintainer: @asset-factory-team
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Asset drift score below threshold
- [ ] Lint checks passing
- [ ] Asset registered in registry
- [ ] Visual review approved
- [ ] Production UI using correct asset version

## Post-Resolution

- Update incident timeline
- If caused by style anchor issue, update anchor
- If caused by model issue, document in known issues
- Schedule postmortem if P0/P1
```

---

## Operator Mode / GitHub Automation Runbooks

Located: `runbooks/operator-mode/`

| Runbook | Trigger |
|---------|---------|
| `run-failure.md` | Operator Mode run fails |
| `merge-conflict.md` | Auto-remediation cannot resolve conflict |
| `worktree-conflict-storm.md` | Multiple worktrees conflict on same files |
| `flaky-test-detected.md` | Test passes/fails inconsistently |
| `flaky-test-escalation.md` | Flaky test budget exceeded |
| `ci-check-blocked.md` | CI check repeatedly fails |
| `merge-queue-stuck.md` | PR stuck in merge queue |
| `rate-limit-hit.md` | GitHub API rate limit exceeded |
| `budget-exceeded.md` | Run cost exceeds budget |
| `kill-switch-triggered.md` | Kill switch activated |
| `kill-switch-recovery.md` | Restoring from kill switch |

### Runbook: Operator Mode Run Failure

```markdown
# Runbook: Operator Mode - Run Failure

## Purpose and Scope
This runbook addresses scenarios where an Operator Mode run fails to complete,
including CI failures, merge conflicts, and budget overruns.

## Detection Signals
- Alert: `operator-run-failure`
- Dashboard: Operator Mode → Failed Runs
- Event: `operator.run.failed`

## Prerequisites
- [ ] Access to Operator Mode dashboard
- [ ] Access to run logs and Evidence Pack
- [ ] Access to GitHub repository
- [ ] Notification channels (Slack, email)

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Multiple runs failing systematically | P1 |
| Single run failure, workaround available | P2 |
| Auto-remediation in progress | P3 |

## Failure Type Diagnosis

Check the run detail in dashboard:

| Failure Type | Detection | Auto-Remediation |
|--------------|-----------|------------------|
| **CI Check Failed** | Check status in GitHub panel | Retry → Regenerate → Quarantine |
| **Merge Conflict** | PR shows conflict status | Rebase → Regenerate → Split |
| **Rate Limit** | GitHub API errors | Backoff → Retry |
| **Budget Exceeded** | Cost panel shows overrun | Pause → User approval |
| **Security Finding** | Security scan failed | Block (no auto-fix) |

## Safe Mitigation Steps

### Step 1: Check Auto-Remediation Status

```
Dashboard → Run Detail → Auto-Remediation Panel

If auto-fix in progress:
- Wait for completion
- Monitor attempt count
- Check escalation threshold
```

### Step 2: For CI Check Failures

If auto-remediation exhausted:

```
1. View failed check details
2. Check if issue is in generated code or test
3. Options:
   a. Manual fix via PR edit
   b. Retry run with modified constraints
   c. Quarantine test (if flaky)
```

### Step 3: For Merge Conflicts

If auto-rebase failed:

```
1. View conflict diff in dashboard
2. Select resolution:
   a. Accept incoming (our changes)
   b. Accept current (their changes)
   c. Open in GitHub for manual merge
3. Re-run checks after resolution
```

### Step 4: For Rate Limits

```
1. Check X-RateLimit-Reset header time
2. Wait until reset OR
3. Switch to alternate GitHub App installation
4. Resume run
```

### Step 5: For Budget Exceeded

```
1. Review cost breakdown
2. Options:
   a. Approve budget extension (dashboard)
   b. Reduce scope and retry
   c. Abort run
```

## Escalation Criteria

Escalate immediately if:
- Auto-remediation fails after max attempts
- Security scan blocks with critical finding
- Multiple runs failing with same error
- Kill switch may be needed

Escalation path:
1. Platform Support: @platform-support
2. Operator Mode Team: @operator-team
3. Security (if security finding): @security-team

## Verification Steps

- [ ] Run completed or properly aborted
- [ ] All PRs merged or closed cleanly
- [ ] Evidence Pack generated (even for failures)
- [ ] No orphaned branches
- [ ] GitHub issues updated with status

## Post-Resolution

- Update run notes with resolution
- If systematic issue, file platform bug
- Review for patterns in failure causes
- Schedule postmortem if P1
```

---

### Runbook: Kill Switch Recovery

```markdown
# Runbook: Operator Mode - Kill Switch Recovery

## Purpose and Scope
This runbook addresses recovery after a kill switch has been activated,
restoring Operator Mode to normal operation.

## Detection Signals
- Alert: `operator-kill-switch-activated`
- Dashboard: Kill Switch banner visible
- Event: `operator.kill_switch.activated`

## Prerequisites
- [ ] Admin access to Operator Mode dashboard
- [ ] Incident resolved or contained
- [ ] Audit log review completed
- [ ] Root cause identified (at least preliminary)

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Kill switch for security incident | P0 (until security clears) |
| Kill switch for runaway cost | P1 |
| Kill switch for other reasons | P2 |

## Kill Switch State

When kill switch is active:
- All Operator Mode workflows terminated
- All merge queues frozen
- MCP credentials revoked
- Tool permissions suspended
- (Optional) Secrets rotated

## Safe Recovery Steps

### Step 1: Confirm Incident Resolved

```
1. Review incident timeline
2. Confirm root cause addressed
3. Get security team clearance (if security incident)
4. Document resolution in audit log
```

### Step 2: Prepare for Recovery

```
1. Identify affected runs:
   Dashboard → Kill Switch → Affected Runs

2. For each run:
   - Can it be safely resumed?
   - Does it need cleanup first?
   - Should it be abandoned?
```

### Step 3: Re-enable Operator Mode

```
Dashboard → Kill Switch → Release Kill Switch

Required inputs:
- Admin authentication (re-verify identity)
- Reason for release
- Confirmation checkbox

This will:
- Restore MCP credentials
- Unfreeze merge queues
- Re-enable workflow starts
```

### Step 4: Resume or Cleanup Runs

For each affected run:

**Option A: Resume**
```
Dashboard → Run → Resume
- Run continues from last checkpoint
- May need manual intervention for conflicts
```

**Option B: Cleanup and Restart**
```
Dashboard → Run → Cleanup
- Closes orphaned PRs
- Deletes orphaned branches
- Marks issues as blocked

Then start new run if needed.
```

**Option C: Abandon**
```
Dashboard → Run → Abandon
- Closes all PRs
- Closes work item issues
- Records abandonment reason
```

### Step 5: Verify Recovery

```
1. Start a test run (low-risk project)
2. Verify:
   - GitHub operations working
   - CI checks running
   - Merge queue accepting entries
   - Auto-merge functioning
```

## Escalation Criteria

Escalate immediately if:
- Cannot release kill switch (auth issues)
- GitHub integrations not recovering
- Repeated triggering needed

Escalation path:
1. Platform Lead: @platform-lead
2. Security Lead: @security-lead (if security incident)
3. Executive On-Call: @exec-oncall

## Verification Steps

- [ ] Kill switch released
- [ ] Operator Mode functional
- [ ] Test run completed successfully
- [ ] All affected runs resolved
- [ ] Audit log entries complete

## Post-Resolution

- Complete incident postmortem
- Update kill switch documentation if needed
- Review trigger thresholds
- Train team on recovery process
```

---

### Runbook: Merge Queue Stuck

```markdown
# Runbook: Operator Mode - Merge Queue Stuck

## Purpose and Scope
This runbook addresses scenarios where PRs are stuck in the GitHub merge queue,
blocking automated merges.

## Detection Signals
- Alert: `merge-queue-stuck`
- Dashboard: PR in queue > 2 hours
- GitHub: Queue branch checks failing repeatedly

## Prerequisites
- [ ] Access to GitHub repository
- [ ] Access to CI pipeline logs
- [ ] Permission to manage merge queue

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Multiple PRs blocked | P1 |
| Single PR blocked, others flowing | P2 |
| Queue processing slow but moving | P3 |

## Safe Mitigation Steps

### Step 1: Diagnose Queue State

```bash
# Check queue status via gh CLI
gh pr list --state open --json number,mergeable,mergeQueueEntry

# Or via Dashboard → GitHub Panel → Merge Queue
```

### Step 2: Check Queue Branch CI

```
1. Find queue branch: gh-readonly-queue/main/pr-{number}-...
2. Check CI status on queue branch
3. Look for failures specific to merge preview
```

### Step 3: Common Fixes

**If CI failing on queue branch but passed on PR:**
- Conflict with other queued PR
- Remove conflicting PR from queue
- Re-queue after other merges

**If queue seems stuck with no activity:**
```bash
# Force re-queue
gh pr merge --merge-queue --admin [PR_NUMBER]
```

**If checks timing out:**
- Check CI infrastructure
- May need to increase timeout
- Temporary: bypass with admin merge

### Step 4: Emergency Bypass

If critical and queue truly stuck:

```bash
# Admin merge (bypasses queue)
gh pr merge --admin [PR_NUMBER]
```

**Note**: Admin merges are logged and require justification.

## Escalation Criteria

Escalate if:
- Queue stuck > 4 hours
- Multiple admin bypasses needed
- CI infrastructure issues suspected

Escalation path:
1. Platform Support: @platform-support
2. GitHub Admin: @github-admins
3. CI Team: @ci-team

## Verification Steps

- [ ] Queue processing normally
- [ ] PRs merging via queue
- [ ] CI passing on queue branches
- [ ] No orphaned queue branches

## Post-Resolution

- Review queue configuration
- Check for CI reliability issues
- Document any workarounds used
```

---

### Runbook: Worktree Conflict Storm

```markdown
# Runbook: Operator Mode - Worktree Conflict Storm

## Purpose and Scope
This runbook addresses scenarios where multiple parallel worktrees are conflicting
on the same files, causing repeated merge failures and blocking the parallel task
execution system.

## Detection Signals
- Alert: `worktree-conflict-storm`
- Dashboard: File Locks Panel shows multiple blocked acquisitions
- Metric: `conflict_rate > 3 conflicts per hour on same file`
- Event: `git_orchestrator.conflict.storm_detected`

## Prerequisites
- [ ] Access to Operator Mode dashboard
- [ ] Access to Git Orchestrator logs
- [ ] Access to File Locks Panel
- [ ] Permission to adjust scheduling policies

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| >5 worktrees blocked on same file | P1 |
| 2-5 worktrees blocked, work continuing | P2 |
| Single conflict, auto-resolution working | P3 |

## What Is a Conflict Storm?

A conflict storm occurs when:
1. Multiple parallel tasks modify the same file (e.g., `package-lock.json`)
2. Rebase-on-main rule causes repeated conflict detection
3. Auto-resolution fails or produces invalid results
4. Tasks queue up waiting for file locks

```
Task A modifies package-lock.json → merges → main updated
                                          ↓
Task B rebases → CONFLICT on package-lock.json
Task C rebases → CONFLICT on package-lock.json
Task D rebases → CONFLICT on package-lock.json
                ↓
           STORM DETECTED
```

## Safe Mitigation Steps

### Step 1: Identify the Hot File

```
Dashboard → Parallel Runs → File Locks Panel

Look for:
- File with multiple pending lock requests
- File appearing in multiple conflict reports
- High conflict_count in metrics
```

Common hot files:
- `package-lock.json` (npm dependencies)
- `pnpm-lock.yaml` (pnpm dependencies)
- `migrations/*.sql` (database migrations)
- `schema.prisma` (Prisma schema)
- `design-os/tokens.json` (design tokens)
- `apps/*/routes.ts` (route registries)

### Step 2: Enable Serialization for Hot File

If conflicts are on a known hot file pattern:

```
Dashboard → Parallel Runs → Scheduling → Add Serialized Path

Add pattern: "**/package-lock.json"
Mode: "exclusive"
```

This tells the scheduler to run tasks touching this file sequentially.

### Step 3: Drain Existing Conflicts

For currently conflicting worktrees:

**Option A: Sequential Resolution (Safe)**
```
1. Dashboard → Parallel Runs → Conflict Resolution
2. Click "Serialize Conflicting Tasks"
3. System will:
   - Pause all but oldest conflicting task
   - Let oldest complete and merge
   - Resume next task with fresh rebase
   - Repeat until all resolved
```

**Option B: Regenerate from Main (Faster)**
```
1. Dashboard → Parallel Runs → Conflict Resolution
2. Select all conflicting worktrees
3. Click "Regenerate All from Main"
4. System will:
   - Abandon current branches
   - Create fresh worktrees from current main
   - Re-run tasks with serialization enabled
```

### Step 4: For Non-Automatable Hot Files

If the hot file requires manual merge decisions:

```
1. Dashboard → Parallel Runs → Conflict Resolution
2. Click "Escalate to Manual Resolution"
3. User notification sent
4. Dashboard presents:
   - All conflicting diffs
   - Suggested merge order
   - One-click resolution options
```

User selects resolution strategy:
- **Accept Oldest First**: Merge in queue order
- **Accept Highest Priority**: Merge by task priority
- **Manual Merge**: Open in GitHub for manual resolution

### Step 5: Prevent Future Storms

After resolution, configure permanent mitigation:

```yaml
# Update scheduling policy
scheduling:
  serialized_paths:
    - pattern: "**/package-lock.json"
      reason: "npm lockfile conflicts"
      mode: exclusive
    - pattern: "**/migrations/**"
      reason: "migrations must be sequential"
      mode: exclusive
    - pattern: "**/schema.prisma"
      reason: "schema conflicts are complex"
      mode: exclusive

  conflict_storm_detection:
    threshold: 3  # conflicts on same file
    window_minutes: 60
    auto_serialize: true
```

### Step 6: Emergency: Pause All Parallel Execution

If storm cannot be controlled:

```
Dashboard → Parallel Runs → Emergency → Pause All

This will:
- Stop all running worktrees
- Hold merge queue
- Preserve state for recovery
- Notify operators
```

## Escalation Criteria

Escalate immediately if:
- Storm affects >10 worktrees
- Auto-resolution corrupts files
- Merge queue completely blocked
- Data integrity concerns (migrations)
- Storm persists >2 hours

Escalation path:
1. Platform Support: @platform-support
2. Git Orchestrator Team: @git-orchestrator-team
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Conflict storm resolved
- [ ] All blocked worktrees progressing
- [ ] File locks acquired normally
- [ ] Merge queue flowing
- [ ] Serialization policy in place for hot file
- [ ] No data corruption in resolved files

## Post-Resolution

- Document which file caused storm
- Review if scheduling policy needs update
- Consider splitting tasks to avoid hot file contention
- Update conflict storm detection thresholds if needed
- Schedule postmortem if P1
```

---

### Runbook: Flaky Test Detected

```markdown
# Runbook: Operator Mode - Flaky Test Detected

## Purpose and Scope
This runbook addresses scenarios where a test passes and fails inconsistently
across CI runs, blocking automatic merge and consuming remediation budget.

## Detection Signals
- Alert: `flaky-test-detected`
- Dashboard: CI Panel shows test with inconsistent results
- Metric: `test_flakiness_score > 0.1` (>10% failure rate when code unchanged)
- Event: `ci.test.flaky_detected`
- Pattern: Same test fails on retry but passes on re-run

## Prerequisites
- [ ] Access to CI dashboard and logs
- [ ] Access to test history database
- [ ] Access to quarantine configuration
- [ ] Permission to modify test execution policy

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Flaky test blocking multiple PRs | P1 |
| Single PR blocked, workaround available | P2 |
| Flaky test detected, not blocking | P3 |

## What Is a Flaky Test?

A test is considered flaky when:
1. It fails intermittently without code changes
2. It passes on retry without fixes
3. Its results depend on external factors (timing, network, order)

Flakiness score calculation:
```
flakiness_score = failures_without_code_change / total_runs
```

Thresholds:
- `> 0.05` (5%): Warning, monitor
- `> 0.10` (10%): Flaky, consider quarantine
- `> 0.25` (25%): Highly flaky, auto-quarantine

## Safe Mitigation Steps

### Step 1: Confirm Flakiness

```
Dashboard → CI Panel → Test History → [Test Name]

Check:
- Failure rate over last 20 runs
- Code changes between pass/fail runs
- Error message patterns
- Timing patterns (time of day, load)
```

Confirm flaky if:
- Same test, same code, different results
- Error message indicates timing/race condition
- Test passes on immediate retry

### Step 2: Classify Flakiness Type

| Type | Symptoms | Resolution |
|------|----------|------------|
| **Race Condition** | Timing-dependent failures | Add waits/retries in test |
| **Resource Leak** | Fails late in test suite | Fix cleanup, isolate test |
| **External Dependency** | Network/API timeouts | Mock external calls |
| **Order Dependent** | Fails only in certain order | Fix test isolation |
| **Environment** | Fails in CI, passes locally | Fix environment assumptions |

### Step 3: Immediate Unblocking

If PR is blocked and flakiness confirmed:

**Option A: Retry with Isolation**
```
Dashboard → CI Panel → Failed Test → Retry Isolated

This will:
- Re-run only the flaky test
- Run in isolation (no parallel tests)
- If passes, mark PR as unblocked
```

**Option B: Quarantine Test**
```
Dashboard → CI Panel → Failed Test → Quarantine

This will:
- Move test to quarantine list
- Test still runs but doesn't block merge
- Quarantine ticket created automatically
- Test owner notified
```

### Step 4: Auto-Remediation Protocol

The system follows this protocol for suspected flaky tests:

```
Attempt 1: Run test → FAIL
                ↓
Attempt 2: Retry test → FAIL (same error)
                ↓
         Check: Is error deterministic?
                ↓
              NO → Flaky suspected
                ↓
Attempt 3: Retry with isolation → PASS
                ↓
         Mark as flaky, add to monitor list
                ↓
         If flakiness_score > 0.10:
                ↓
         Auto-quarantine with ticket
```

### Step 5: Quarantine Management

Quarantined tests:
- Run in CI but don't block merge
- Track flakiness score over time
- Auto-create fix ticket
- Auto-assign to test owner (from CODEOWNERS)

```
Dashboard → CI Panel → Quarantine List

Shows:
- Test name
- Flakiness score
- Days in quarantine
- Assigned owner
- Fix ticket link
```

Quarantine rules:
- Max quarantine duration: 14 days
- After 14 days: Escalate to P1 fix or delete test
- Auto-release if flakiness_score < 0.02 for 7 days

### Step 6: Fix the Flaky Test

Common fixes by type:

**Race Condition:**
```typescript
// Before (flaky)
expect(element).toBeVisible();

// After (stable)
await waitFor(() => expect(element).toBeVisible(), { timeout: 5000 });
```

**External Dependency:**
```typescript
// Before (flaky)
const response = await fetch('https://api.external.com/data');

// After (stable)
const response = await fetch(mockServer.url('/data'));
```

**Order Dependent:**
```typescript
// Before (flaky)
beforeAll(() => { globalState = initialState; });

// After (stable)
beforeEach(() => { globalState = structuredClone(initialState); });
```

### Step 7: Verify Fix

After fixing:

```
Dashboard → CI Panel → Test → Remove from Quarantine → Run Verification

Verification runs test 10 times:
- If 10/10 pass: Test unquarantined, ticket closed
- If any fail: Remains quarantined, ticket updated
```

## Escalation Criteria

Escalate immediately if:
- Flaky test is in critical path (auth, payments)
- Quarantine list grows to >10 tests
- Same test flaky for >14 days with no fix
- Flakiness affecting multiple repositories

Escalation path:
1. Test Owner: @test-codeowner
2. Team Lead: @team-lead
3. Quality Engineering: @quality-team
4. Platform Lead: @platform-lead (if systematic)

## Verification Steps

- [ ] Flakiness confirmed or ruled out
- [ ] Blocked PR unblocked (retry or quarantine)
- [ ] Root cause identified
- [ ] Fix ticket created (if quarantined)
- [ ] Test owner notified
- [ ] Quarantine duration reasonable

## Post-Resolution

- Update test with fix if applicable
- Document flakiness pattern for future reference
- Review if test design needs improvement
- Consider adding flakiness check to test PR reviews
- Update flakiness detection thresholds if needed
- Schedule postmortem if P1

## Flaky Test Budget

Each run has a flaky test budget:

```yaml
flaky_test_budget:
  max_retries_per_test: 3
  max_quarantine_requests_per_run: 5
  max_total_flaky_time_minutes: 30

  exceeded_action: escalate_to_user
```

When budget exceeded, dashboard prompts user for decision:
- Increase budget (requires justification)
- Abort run
- Force continue (creates risk ticket)
```

---

## Track Assurance Runbooks

Located: `runbooks/track-assurance/`

| Runbook | Trigger |
|---------|---------|
| `drift-threshold-exceeded.md` | Drift score > 0.50 |
| `checkpoint-creation-failed.md` | Review Checkpoint fails to save |
| `stuck-at-checkpoint.md` | Workflow paused > 24 hours |
| `replan-loop.md` | >3 replans on same checkpoint |
| `resume-failure.md` | Workflow fails to resume from checkpoint |

### Runbook: Drift Threshold Exceeded

```markdown
# Runbook: Track Assurance - Drift Threshold Exceeded

## Purpose and Scope
This runbook addresses scenarios where a workflow's drift score exceeds the
pause threshold (0.50), triggering automatic pause and Review Checkpoint creation.

## Detection Signals
- Alert: `track-assurance-drift-exceeded`
- Dashboard: Track Assurance Panel shows paused workflow
- Event: `track_assurance.drift.threshold_exceeded`
- Metric: `drift_score > 0.50`

## Prerequisites
- [ ] Access to Track Assurance Panel
- [ ] Access to Review Checkpoint viewer
- [ ] Permission to approve/reject checkpoints
- [ ] Understanding of workflow context

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Drift > 0.70 (emergency) | P1 |
| Drift 0.51-0.70 (threshold) | P2 |
| Drift 0.31-0.50 (warning) | P3 |

## Safe Resolution Steps

### Step 1: Review the Drift Report

```
Dashboard → Track Assurance → [Workflow] → Drift Details

Review:
- Overall drift score
- Category breakdown (plan, code, UI, behavior)
- Specific divergences listed
- Original spec vs current state
```

### Step 2: Understand the Divergence

For each high-drift category:

| Category | What to Check |
|----------|---------------|
| **Plan drift** | Is implementation deviating from architecture? |
| **Code drift** | Does code match PRD requirements? |
| **UI drift** | Does UI follow Design OS and mockups? |
| **Behavior drift** | Do user flows work as specified? |

### Step 3: Choose Resolution Path

**Option A: Resume with Replan**
```
Dashboard → Track Assurance → [Checkpoint] → Resume → With Replan

When to use:
- Drift is due to scope creep
- Requirements have changed
- Better approach discovered during build

Actions:
- Workflow returns to Architect phase
- Plan is revised with new understanding
- Previous work preserved where applicable
- New evidence trail created
```

**Option B: Resume As-Is**
```
Dashboard → Track Assurance → [Checkpoint] → Resume → As-Is

When to use:
- Drift is acceptable (technical necessity)
- Spec was incomplete, implementation is correct
- Minor drift within tolerance

Required:
- Justification text (logged in Evidence Pack)
- Explicit acknowledgment checkbox
- May require elevated approval for high drift
```

**Option C: Rollback to Previous Checkpoint**
```
Dashboard → Track Assurance → [Checkpoint] → Resume → From Earlier

When to use:
- Wrong direction taken
- Want to try different approach
- Work since checkpoint is not salvageable

Actions:
- Select previous checkpoint from list
- System restores to that state
- Discarded work is archived (not deleted)
```

**Option D: Terminate Workflow**
```
Dashboard → Track Assurance → [Checkpoint] → Terminate

When to use:
- Project should be cancelled
- Requirements fundamentally wrong
- Cannot proceed without major changes

Actions:
- Workflow marked terminal
- All artifacts preserved for audit
- Issue closed with explanation
```

### Step 4: Verify Resolution

After selecting option:

```
1. Confirm workflow state updated
2. Check new drift calculation (if resumed)
3. Verify Evidence Pack updated with decision
4. Monitor next activity for drift regression
```

## Escalation Criteria

Escalate immediately if:
- Drift > 0.85 (severe misalignment)
- Cannot determine correct resolution path
- Security or compliance implications
- Multiple checkpoints with high drift

Escalation path:
1. Technical Lead: @tech-lead
2. Project Owner: @project-owner
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Drift report reviewed and understood
- [ ] Resolution path selected with justification
- [ ] Workflow successfully resumed (or properly terminated)
- [ ] Evidence Pack updated with decision
- [ ] No regression in subsequent activities

## Post-Resolution

- Document why drift occurred
- Update specs if they were incomplete
- Review if similar drift likely in other workflows
- Consider adding validation earlier in pipeline
```

---

### Runbook: Stuck at Checkpoint

```markdown
# Runbook: Track Assurance - Stuck at Checkpoint

## Purpose and Scope
This runbook addresses scenarios where a workflow remains paused at a
Review Checkpoint for longer than expected without operator action.

## Detection Signals
- Alert: `track-assurance-stuck-checkpoint`
- Dashboard: Checkpoint age > 24 hours
- Event: `track_assurance.checkpoint.stale`

## Prerequisites
- [ ] Access to Track Assurance Panel
- [ ] Access to workflow owner contact info
- [ ] Permission to take action on checkpoints

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Checkpoint stuck > 72 hours, blocking | P1 |
| Checkpoint stuck > 24 hours | P2 |
| Checkpoint stuck > 8 hours | P3 |

## Safe Resolution Steps

### Step 1: Identify the Checkpoint

```
Dashboard → Track Assurance → Stale Checkpoints

Shows:
- Workflow ID and name
- Checkpoint age
- Pause reason (drift, manual, budget)
- Last activity timestamp
- Assigned owner
```

### Step 2: Contact Workflow Owner

```
1. Check owner in workflow metadata
2. Send notification via configured channels:
   - Dashboard notification
   - Email (if configured)
   - Slack (if integrated)
3. Include:
   - Checkpoint summary
   - Action required
   - Link to dashboard
```

Template:
```
Your workflow [name] has been paused at a Review Checkpoint for [X hours].

Reason: [drift exceeded / manual stop / budget limit]
Action needed: Review and select: Resume, Replan, Rollback, or Terminate

Dashboard: [link]

If no action taken within 48 hours, workflow will be auto-terminated.
```

### Step 3: Auto-Escalation Timeline

| Age | Action |
|-----|--------|
| 8 hours | First notification |
| 24 hours | Second notification + manager CC |
| 48 hours | Final warning |
| 72 hours | Auto-terminate with preservation |

### Step 4: Force Resolution (if authorized)

If owner unresponsive and blocking other work:

```
Dashboard → Track Assurance → [Checkpoint] → Admin Actions → Force Terminate

Requires:
- Platform admin role
- Documented justification
- Notification to owner

Effects:
- Workflow terminated gracefully
- Artifacts preserved
- Issue updated with explanation
- Audit log entry created
```

## Escalation Criteria

Escalate if:
- Checkpoint blocking critical path
- Owner unreachable
- Multiple workflows affected

Escalation path:
1. Project Owner: @project-owner
2. Platform Support: @platform-support
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Owner contacted
- [ ] Resolution selected or escalated
- [ ] Workflow no longer stuck
- [ ] Audit trail updated

## Post-Resolution

- Review if auto-escalation timeline appropriate
- Check if notification channels working
- Consider if workflow needs different owner
```

---

## Legacy Rebuild Runbooks

Located: `runbooks/legacy-rebuild/`

| Runbook | Trigger |
|---------|---------|
| `discovery-failure.md` | Legacy discovery cannot complete |
| `legacy-snapshot-corruption.md` | Snapshot tag or content invalid |
| `parity-test-failure.md` | Parity Harness tests failing |
| `cutover-blocked.md` | Cutover cannot proceed |
| `rollback-triggered.md` | Post-cutover rollback needed |
| `migration-data-loss.md` | Data migration validation fails |

### Runbook: Parity Test Failure

```markdown
# Runbook: Legacy Rebuild - Parity Test Failure

## Purpose and Scope
This runbook addresses scenarios where the Parity Harness reports failures,
indicating the rebuilt system does not match legacy behavior.

## Detection Signals
- Alert: `legacy-rebuild-parity-failure`
- Dashboard: Legacy Rebuild Panel shows parity failures
- Event: `legacy_rebuild.parity.failed`
- Parity score: < threshold for category

## Prerequisites
- [ ] Access to Legacy Rebuild Panel
- [ ] Access to Parity Harness reports
- [ ] Access to legacy system for comparison
- [ ] Permission to approve parity exceptions

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Critical API parity failure | P0 |
| Database migration parity failure | P0 |
| Multiple category failures | P1 |
| Single non-critical failure | P2 |

## Safe Resolution Steps

### Step 1: Review Parity Report

```
Dashboard → Legacy Rebuild → [Project] → Parity Report

Report shows:
- Overall parity score
- Per-category scores (API, DB, UI, behavior)
- Failed test cases with details
- Expected vs actual comparison
```

### Step 2: Classify Failure Type

| Type | Description | Resolution Path |
|------|-------------|-----------------|
| **True regression** | Rebuilt system behaves differently | Fix the code |
| **Intentional change** | Behavior intentionally improved | Document exception |
| **Legacy bug** | Old system had bug, new is correct | Document exception |
| **Test flakiness** | Test is inconsistent | Fix or skip test |
| **Environment difference** | Test env doesn't match | Fix test setup |

### Step 3: For True Regressions

If rebuilt system needs to match legacy:

```
1. Identify the specific API/behavior
2. Check legacy implementation
3. Update rebuilt code to match
4. Re-run parity tests
5. Verify fix doesn't break other tests
```

### Step 4: For Intentional Improvements

If change is intentional and approved:

```
Dashboard → Legacy Rebuild → Parity → Add Exception

Exception requires:
- Description of difference
- Business justification
- Approver (must be project owner or higher)
- Acknowledgment of behavior change

Exception is logged in:
- Evidence Pack
- Cutover Plan document
- Parity report
```

### Step 5: For Legacy Bugs

If old system had a bug that new system fixes:

```
Dashboard → Legacy Rebuild → Parity → Flag as Legacy Bug

Requires:
- Description of the bug
- Why new behavior is correct
- Confirmation no users depend on bug

Logged as:
- Intentional improvement
- Documented in Cutover Plan
```

### Step 6: Re-run Parity After Fixes

```
Dashboard → Legacy Rebuild → Parity → Run Full Suite

Wait for completion:
- All categories must meet threshold
- Or have documented exceptions
- Review any new failures
```

## Escalation Criteria

Escalate immediately if:
- Critical API parity failure unfixable
- Data migration issues (potential data loss)
- Cannot determine if difference is acceptable
- Parity score consistently degrading

Escalation path:
1. Legacy Rebuild Owner: @rebuild-owner
2. Technical Lead: @tech-lead
3. Product Owner: @product-owner (for behavior decisions)
4. Platform Lead: @platform-lead

## Verification Steps

- [ ] All parity failures addressed (fixed or excepted)
- [ ] Parity score meets threshold per category
- [ ] Exceptions documented and approved
- [ ] Cutover Plan updated with known differences
- [ ] Re-run confirms fixes

## Post-Resolution

- Update parity test suite if gaps found
- Document any legacy quirks discovered
- Review if more golden cases needed
- Consider adding discovered behaviors to spec
```

---

### Runbook: Cutover Blocked

```markdown
# Runbook: Legacy Rebuild - Cutover Blocked

## Purpose and Scope
This runbook addresses scenarios where the cutover from legacy to rebuilt
system cannot proceed due to failed gates or blocking conditions.

## Detection Signals
- Alert: `legacy-rebuild-cutover-blocked`
- Dashboard: Cutover button disabled with reason
- Event: `legacy_rebuild.cutover.blocked`

## Prerequisites
- [ ] Access to Legacy Rebuild Panel
- [ ] Access to Cutover Plan document
- [ ] Permission to approve cutover exceptions
- [ ] Rollback procedure documented

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Cutover deadline imminent | P1 |
| Blocking but flexible timeline | P2 |
| Informational, future cutover | P3 |

## Safe Resolution Steps

### Step 1: Identify Blocking Condition

```
Dashboard → Legacy Rebuild → [Project] → Cutover → Blocking Conditions

Common blockers:
- Parity score below threshold
- Security scan findings
- Missing human approval
- Rollback not tested
- Evidence Pack incomplete
- Dependencies not ready
```

### Step 2: Address Each Blocker

**Parity below threshold:**
- Follow Parity Test Failure runbook
- Or request exception with justification

**Security findings:**
- Review security scan results
- Fix findings or document accepted risks
- Get security team sign-off

**Missing approval:**
- Identify required approvers
- Send cutover review request
- Provide Cutover Plan document

**Rollback not tested:**
```
Dashboard → Legacy Rebuild → Cutover → Test Rollback

This will:
- Deploy rebuilt system to staging
- Simulate cutover
- Trigger rollback
- Verify legacy system restored
- Report rollback timing
```

**Evidence Pack incomplete:**
- Review missing evidence items
- Generate missing artifacts
- Upload required documents

### Step 3: Request Cutover Exception (if needed)

For blockers that cannot be fully resolved:

```
Dashboard → Legacy Rebuild → Cutover → Request Exception

Requires:
- Which gate is being bypassed
- Risk assessment
- Mitigation plan
- Approver (director-level or higher)
- Time-boxed validity
```

### Step 4: Execute Cutover

Once all blockers resolved:

```
Dashboard → Legacy Rebuild → Cutover → Execute

Cutover process:
1. Final parity check
2. Create cutover checkpoint
3. Switch traffic (gradual or immediate)
4. Monitor metrics
5. Confirm success or trigger rollback
```

### Step 5: Monitor Post-Cutover

```
Dashboard → Legacy Rebuild → Post-Cutover Metrics

Watch for:
- Error rate spike
- Latency degradation
- User complaints
- Data inconsistencies

Auto-rollback triggers if:
- Error rate > 5% for 5 minutes
- Latency p99 > 2x baseline
- Data integrity alert
```

## Escalation Criteria

Escalate immediately if:
- Cutover deadline non-negotiable
- Multiple critical blockers
- Rollback testing reveals issues
- Stakeholder disagreement on exceptions

Escalation path:
1. Project Owner: @project-owner
2. Technical Lead: @tech-lead
3. Executive Sponsor: @exec-sponsor

## Verification Steps

- [ ] All blocking conditions resolved
- [ ] Required approvals obtained
- [ ] Rollback tested successfully
- [ ] Cutover executed
- [ ] Post-cutover metrics stable
- [ ] Legacy system preserved for rollback

## Post-Resolution

- Complete cutover checklist
- Archive legacy system artifacts
- Update documentation
- Schedule legacy decommission (after bake period)
- Conduct cutover retrospective
```

---

## Improvement Pipeline Runbooks

Located: `runbooks/improvement-pipeline/`

| Runbook | Trigger |
|---------|---------|
| `evaluator-failure.md` | Improvement fails Evaluator Harness |
| `canary-regression.md` | Canary deployment shows regression |
| `auto-rollback-triggered.md` | Automatic rollback activated |
| `rollout-stalled.md` | Gradual rollout stuck |
| `feature-flag-conflict.md` | Feature flags conflicting |
| `improvement-rejected.md` | Improvement Review Board rejects |

### Runbook: Canary Regression

```markdown
# Runbook: Improvement Pipeline - Canary Regression

## Purpose and Scope
This runbook addresses scenarios where an improvement deployed to canary
(5% of traffic) shows metric regression, triggering automatic rollback.

## Detection Signals
- Alert: `improvement-canary-regression`
- Dashboard: Improvement Pipeline shows canary failure
- Event: `improvement.canary.regression_detected`
- Metric: regression > 5% vs baseline

## Prerequisites
- [ ] Access to Improvement Pipeline Panel
- [ ] Access to canary metrics
- [ ] Access to feature flag controls
- [ ] Permission to modify rollout

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Canary auto-rolled back, production safe | P2 |
| Canary showing issues, not yet rolled back | P1 |
| Canary issue affecting users | P0 |

## Safe Resolution Steps

### Step 1: Verify Rollback Status

```
Dashboard → Improvement Pipeline → [Improvement] → Canary Status

Check:
- Was auto-rollback triggered?
- Is feature flag disabled?
- Are canary pods replaced?
- Is traffic back to baseline?
```

If auto-rollback successful:
- Canary regression contained
- Proceed to root cause analysis

If auto-rollback failed:
- Immediately disable feature flag manually
- Force pod restart if needed
- Page on-call if impacting users

### Step 2: Analyze Regression

```
Dashboard → Improvement Pipeline → [Improvement] → Canary Report

Report shows:
- Which metrics regressed
- Regression magnitude
- Timeline of degradation
- Comparison: canary vs control
```

Common regression types:

| Metric | Possible Causes |
|--------|-----------------|
| **Error rate** | Bug in new code, edge case |
| **Latency** | Performance regression, N+1 |
| **Success rate** | Logic error, missing handler |
| **Cost** | Inefficient implementation |

### Step 3: Root Cause Analysis

```
1. Review improvement code changes
2. Check canary logs for errors
3. Compare canary vs control behavior
4. Identify specific failure cases
5. Document root cause
```

### Step 4: Fix and Re-evaluate

If improvement should proceed:

```
1. Fix the identified issue
2. Update Improvement PR
3. Re-run Evaluator Harness from Stage 1
4. Must pass all stages again
5. Canary with fresh evaluation
```

If improvement should be abandoned:

```
Dashboard → Improvement Pipeline → [Improvement] → Close

Closes with:
- Reason for abandonment
- Root cause documentation
- Lessons learned
- Logged in improvement history
```

### Step 5: Verify Production Unaffected

```
Dashboard → Platform Metrics → Production

Confirm:
- Error rates normal
- Latency normal
- No user complaints
- Canary traffic returned to baseline
```

## Escalation Criteria

Escalate immediately if:
- Auto-rollback failed
- Production users affected
- Cannot identify root cause
- Regression in critical path

Escalation path:
1. Improvement Owner: @improvement-owner
2. Platform Team: @platform-team
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Auto-rollback completed successfully
- [ ] Feature flag disabled
- [ ] Production metrics stable
- [ ] Root cause identified
- [ ] Improvement PR updated or closed
- [ ] Incident documented

## Post-Resolution

- Document root cause
- Update improvement with fix
- Review if canary threshold appropriate
- Consider adding specific test case
- Update monitoring for similar issues
```

---

### Runbook: Evaluator Harness Failure

```markdown
# Runbook: Improvement Pipeline - Evaluator Harness Failure

## Purpose and Scope
This runbook addresses scenarios where an improvement fails one of the
five Evaluator Harness stages, blocking promotion to production.

## Detection Signals
- Alert: `improvement-evaluator-failure`
- Dashboard: Improvement shows failed stage
- Event: `improvement.evaluator.stage_failed`

## Prerequisites
- [ ] Access to Improvement Pipeline Panel
- [ ] Access to CI/CD logs
- [ ] Permission to retry or modify improvement

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Multiple improvements blocked | P1 |
| Single improvement blocked | P2 |
| Non-critical improvement | P3 |

## Evaluator Stages

| Stage | Duration | What It Checks |
|-------|----------|----------------|
| **1. Static** | Immediate | Linting, types, security scan |
| **2. Unit** | < 10 min | All unit tests pass |
| **3. Integration** | < 30 min | Integration test suite |
| **4. Canary** | 24 hours | 5% traffic, metrics |
| **5. Rollout** | 7 days | Gradual 5% → 100% |

## Safe Resolution Steps

### Step 1: Identify Failed Stage

```
Dashboard → Improvement Pipeline → [Improvement] → Evaluator Results

Shows:
- Stage number
- Failure type
- Error details
- Logs link
```

### Step 2: Stage-Specific Resolution

**Stage 1 (Static) Failure:**
```
1. Review lint/type errors
2. Fix in improvement PR
3. Push updated code
4. Stage 1 re-runs automatically
```

**Stage 2 (Unit) Failure:**
```
1. Identify failing tests
2. Check if test is correct or needs update
3. Fix code or test as appropriate
4. Trigger stage re-run
```

**Stage 3 (Integration) Failure:**
```
1. Review integration test logs
2. Check for environment issues
3. Verify test isn't flaky
4. Fix and re-run stage
```

**Stage 4 (Canary) Failure:**
- See "Canary Regression" runbook

**Stage 5 (Rollout) Failure:**
```
1. Review at which percentage failed
2. Check if load-dependent issue
3. May need performance optimization
4. Rollback and fix
```

### Step 3: Retry Failed Stage

```
Dashboard → Improvement Pipeline → [Improvement] → Retry Stage

Options:
- Retry same stage (if fix pushed)
- Restart from Stage 1 (if code changed)
- Abandon improvement
```

### Step 4: Request Stage Exception (rare)

If stage failure is not due to improvement:

```
Dashboard → Improvement Pipeline → [Improvement] → Request Exception

Requires:
- Proof failure is environmental
- Approval from platform team
- Time-boxed (next attempt must pass)
```

## Escalation Criteria

Escalate if:
- CI infrastructure issues suspected
- Cannot reproduce failure locally
- Flaky test causing repeated failures
- Critical improvement blocked

Escalation path:
1. Improvement Owner: @improvement-owner
2. CI Team: @ci-team (if infrastructure)
3. Platform Lead: @platform-lead

## Verification Steps

- [ ] Failure root cause identified
- [ ] Fix applied and pushed
- [ ] Stage re-run successful
- [ ] Improvement progressing

## Post-Resolution

- Document failure cause
- Add test coverage if gap found
- Review if stage thresholds appropriate
- Update improvement guidelines if needed
```

---

## Runbook Ownership

| Owner | Responsibility |
|-------|----------------|
| **Service team** | Service-specific runbooks |
| **Platform team** | Infrastructure runbooks |
| **Security team** | Security runbooks |
| **Design team** | Design OS runbooks |
| **Asset Factory team** | Asset generation runbooks |
| **Product team** | Phase 1 / Intake runbooks |
| **Governance team** | Change Request runbooks |
| **Operator Mode team** | Operator Mode / GitHub automation runbooks |
| **Track Assurance team** | Drift review and checkpoint runbooks |
| **Legacy Rebuild team** | Legacy rebuild and parity runbooks |
| **Improvement Pipeline team** | Self-improvement and evaluator runbooks |
| **Runbook Author agent** | Format validation, updates |

---

## Runbook Maintenance

### Review Schedule

| Trigger | Action |
|---------|--------|
| After every use | Verify accuracy, update if needed |
| Monthly | Review for staleness |
| After architecture changes | Update affected runbooks |
| After incidents | Add learnings |

### Staleness Indicators

```yaml
# Runbook frontmatter
---
title: High Error Rate
service: user-service
last_reviewed: 2026-01-06
last_used: 2026-01-05
review_interval: 30d
owners:
  - @identity-team
---
```

Stale if:
- Not reviewed in > review_interval
- Referenced commands fail
- Dashboard links broken
- Team ownership changed

---

## Runbook Discovery

### Finding Runbooks

```bash
# By service
ls runbooks/services/user-service/

# By symptom (search)
grep -r "high error rate" runbooks/

# Via service catalog
# See catalog-info.yaml annotations
```

### Linking Runbooks

```yaml
# catalog-info.yaml
annotations:
  itqahn.io/runbooks: |
    - path: runbooks/services/user-service/high-error-rate.md
      alert: user-service-error-rate
    - path: runbooks/services/user-service/high-latency.md
      alert: user-service-latency
```

---

## Context Engineering Runbooks

Located: `runbooks/context-engineering/`

| Runbook | Trigger |
|---------|---------|
| `validation-gate-failure.md` | Validation gate fails after max attempts |
| `context-drift-plan-drift.md` | Agent deviates from PRP or plan |

### Runbook: Validation Gate Failure

```markdown
# Runbook: Context Engineering - Validation Gate Failure

## Purpose and Scope
This runbook addresses scenarios where validation gates fail repeatedly during
PRP execution and require intervention.

## Detection Signals
- Alert: `validation-gate-failure`
- Dashboard: PRP Execution Panel shows gate failure
- Event: `prp.validation_gate.failed_max_attempts`
- Metric: `gate_failure_count >= 3`

## Prerequisites
- [ ] Access to PRP Execution Dashboard
- [ ] Access to validation gate logs
- [ ] Permission to approve rollback or alternative
- [ ] Understanding of PRP context

## Severity Assessment

| Condition | Severity |
|-----------|----------|
| Security gate failed | P0 (escalate to security) |
| Blocking gate failed 3+ times | P1 |
| Non-blocking gate warning | P3 |

## Safe Resolution Steps

### Step 1: Review Gate Failure Details

```
Dashboard → PRP Execution → [Run ID] → Validation Details

Review:
- Which gate failed (lint, typecheck, tests, security, etc.)
- Error messages and logs
- Attempts made (should be 3)
- What fixes were tried
```

### Step 2: Analyze Root Cause

| Gate Type | Common Causes | Quick Fix |
|-----------|---------------|-----------|
| **Lint** | New pattern not in config | Update eslint config |
| **Typecheck** | Missing type definitions | Add types, fix inferences |
| **Unit Tests** | Logic error, missing mock | Fix code or update test |
| **Integration** | External dependency issue | Mock or skip temporarily |
| **Security** | Critical vulnerability | Cannot skip, must fix |
| **Drift** | Implementation diverged | Review PRP alignment |

### Step 3: Choose Resolution Path

**Option A: Fix and Retry**
```
Dashboard → PRP Execution → [Run ID] → Retry Gate

Steps:
1. Review suggested fix from agent
2. Approve fix or provide guidance
3. Agent applies fix
4. Gate runs again
```

**Option B: Narrow Scope**
```
Dashboard → PRP Execution → [Run ID] → Narrow Scope

Steps:
1. Review which parts of PRP are failing
2. Split PRP into smaller, passing portions
3. Create new PRP for remaining work
4. Complete passing portions first
```

**Option C: Rollback**
```
Dashboard → PRP Execution → [Run ID] → Rollback

Steps:
1. Revert all uncommitted changes
2. Preserve completed work (if any)
3. Document why rollback was needed
4. Create new PRP with adjusted approach
```

**Option D: Override (Non-Blocking Only)**
```
Dashboard → PRP Execution → [Run ID] → Override Gate

WARNING: Only for non-blocking gates (docs, optional checks)

Steps:
1. Document reason for override
2. Create follow-up task for gate fix
3. Continue with execution
```

### Step 4: For Security Gate Failures

NEVER override security gates. Instead:

```
1. Dashboard → PRP Execution → Security Details
2. Review vulnerability details
3. Options:
   a. Fix vulnerability and retry
   b. If false positive: request security review
   c. If unfixable: escalate to security team
```

### Step 5: Document Resolution

After resolution:
```
1. Update memory/decision-log.md with:
   - What failed
   - Why it failed
   - What was done to resolve
   - Any follow-up needed

2. If systematic issue:
   - Create issue for process improvement
   - Update PRP template if needed
```

## Escalation Criteria

Escalate immediately if:
- Security gate fails with critical/high finding
- Same gate fails across multiple PRPs
- Gate failure exposes process gap
- Resolution requires architectural change

Escalation path:
1. PRP Owner: @prp-owner
2. Team Lead: @team-lead
3. Security Team: @security-team (for security gates)
4. Platform Support: @platform-support (for tooling issues)

## Verification Steps

- [ ] Gate failure understood
- [ ] Resolution path chosen and executed
- [ ] Gate now passes OR rollback complete
- [ ] Decision documented
- [ ] Follow-up tasks created if needed

## Post-Resolution

- Document failure pattern for future reference
- Consider if gate configuration needs adjustment
- Review if PRP templates need update
- Update runbook if new failure pattern discovered
```

---

### Runbook: Context Drift / Plan Drift

```markdown
# Runbook: Context Engineering - Context Drift / Plan Drift

## Purpose and Scope
This runbook addresses scenarios where agent implementation diverges from the
approved PRP or plan, triggering drift detection and requiring realignment.

## Detection Signals
- Alert: `prp-drift-detected`
- Dashboard: Drift Score indicator changes color
- Event: `prp.drift.threshold_exceeded`
- Metric: `drift_score > 0.30`

## Prerequisites
- [ ] Access to PRP Execution Dashboard
- [ ] Access to drift analysis details
- [ ] Permission to approve plan changes
- [ ] Understanding of original PRP intent

## Severity Assessment

| Drift Score | Severity | Action |
|-------------|----------|--------|
| 0.00-0.30 | Normal | Continue, log only |
| 0.31-0.50 | Warning (P3) | Review, may continue |
| 0.51-0.70 | Pause (P2) | Stop, require approval |
| 0.71-1.00 | Emergency (P1) | Immediate stop, full review |

## What Is Drift?

Drift occurs when implementation deviates from the approved PRP:

| Drift Category | Example | Detection |
|----------------|---------|-----------|
| **Scope Drift** | Implementing features not in PRP | File change analysis |
| **Approach Drift** | Using different patterns than specified | Code pattern analysis |
| **Dependency Drift** | Adding unplanned dependencies | package.json analysis |
| **File Drift** | Modifying unplanned files | Git diff analysis |
| **Behavior Drift** | Different behavior than specified | Test result analysis |

## Safe Resolution Steps

### Step 1: Review Drift Analysis

```
Dashboard → PRP Execution → [Run ID] → Drift Details

Review:
- Overall drift score
- Category breakdown
- Specific divergences listed
- Original PRP vs current implementation
```

### Step 2: Assess Drift Justification

Ask these questions:

| Question | If Yes | If No |
|----------|--------|-------|
| Is drift necessary for PRP success? | May be valid | Likely error |
| Was it discovered during implementation? | Document decision | Revert |
| Does it improve the outcome? | Consider accepting | Revert |
| Does it stay within scope? | May accept | Must revert |
| Is it reversible? | Less risky | More risky |

### Step 3: Choose Resolution Path

**Option A: Accept Drift (Update PRP)**
```
Dashboard → PRP Execution → [Run ID] → Accept Drift

If drift is justified:
1. Review specific divergences
2. Update PRP to reflect new reality
3. Document why drift was accepted
4. Continue with updated PRP
```

**Option B: Revert Drift**
```
Dashboard → PRP Execution → [Run ID] → Revert Drift

If drift is not justified:
1. Identify drifted changes
2. Revert or stash drifted work
3. Re-anchor agent to original PRP
4. Continue from last aligned state
```

**Option C: Split Work**
```
Dashboard → PRP Execution → [Run ID] → Split Drift

If drift is valuable but out of scope:
1. Preserve drifted work in separate branch
2. Create new PRP for drifted work
3. Revert current PRP to original scope
4. Complete original PRP
5. Execute new PRP for valuable drift
```

**Option D: Pause for Replanning**
```
Dashboard → PRP Execution → [Run ID] → Pause for Replan

If drift indicates PRP was flawed:
1. Pause execution
2. Review what was learned
3. Create new, better PRP
4. Abandon or archive original PRP
5. Execute new PRP
```

### Step 4: Re-Anchor After Resolution

After resolving drift:

```
1. Confirm current state matches (updated) PRP
2. Run drift check again
3. Verify drift score < 0.30
4. Resume execution

If drift persists:
- Review agent understanding
- Provide clearer guidance
- Consider more detailed PRP
```

### Step 5: Prevent Future Drift

After resolution:

```yaml
# Add to memory/decision-log.md
drift_resolution:
  prp_id: "{prp-id}"
  drift_score: 0.45
  category: "scope"
  cause: "Discovered need for additional validation"
  resolution: "accept"
  prp_updated: true
  prevention: "Add validation requirements to PRP template"
```

Consider:
- Was PRP detailed enough?
- Were constraints clear?
- Should PRP template be updated?
- Does agent need different guidance?

## Escalation Criteria

Escalate immediately if:
- Drift score > 0.70 (emergency)
- Drift involves security-sensitive code
- Drift affects multiple PRPs from same agent
- Cannot determine if drift is valid
- Drift resolution conflicts with business needs

Escalation path:
1. PRP Owner: @prp-owner
2. Team Lead: @team-lead
3. Product Owner: @product-owner (for scope questions)
4. Architecture: @architecture (for pattern questions)

## Verification Steps

- [ ] Drift score understood
- [ ] Drift categories reviewed
- [ ] Resolution path chosen
- [ ] Current state aligned with (updated) PRP
- [ ] Drift score < 0.30 after resolution
- [ ] Decision documented

## Post-Resolution

- Update memory/decision-log.md
- Review if PRP process needs improvement
- Consider if agent guidance needs update
- Update drift detection thresholds if too sensitive
- Schedule review if systematic issue
```

---

## Related Documents

- `docs/00-overview/principles.md` — Operator Mode audit principles
- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 and Concept Lock
- `docs/03-platform/portal-webapp.md` — Operator Mode dashboard and Kill Switch
- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/03-platform/track-assurance.md` — Track Assurance specification
- `docs/03-platform/legacy-rebuild.md` — Legacy Rebuild specification
- `docs/06-operations/auto-remediation.md` — Automation details
- `docs/06-operations/incident-response.md` — Incident handling
- `docs/06-operations/itqahn-continuous-improvement.md` — Self-improvement pipeline
- `docs/07-integrations/git-integration.md` — GitHub Automation Program
- `docs/07-integrations/webhooks-events.md` — GitHub and Operator Mode events
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/08-agents/agent-permissions.md` — Bot permissions
- `docs/08-agents/agent-quality-bar.md` — Agent quality gates
- `docs/03-platform/context-engineering.md` — Context Engineering Program
- `templates/product/INITIAL.md` — Feature request template
- `templates/product/PRP.md` — PRP template
- `templates/ops/RUNBOOK.md` — Runbook template

---

**Version**: 2.6.0 | **Date**: 2026-01-08
