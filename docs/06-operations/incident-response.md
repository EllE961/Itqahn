# Incident Response

Itqahn uses a Google SRE-inspired incident model with defined roles, severity levels, and communication protocols.

---

## Severity Levels

| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| **P0** | Outage or confirmed data exposure | 5 min | Complete service unavailable, security breach |
| **P1** | Significant degradation, SLO breach | 15 min | Major feature broken, >50% errors |
| **P2** | Partial functionality loss | 1 hour | Feature degraded, workaround exists |
| **P3** | Minor issue | 4 hours | Cosmetic bug, low-impact error |

---

## Core Roles

### Incident Commander (IC)

**Responsibilities:**
- Overall incident ownership
- Coordinate response team
- Make critical decisions
- Authorize emergency changes
- Declare incident resolved

**Authority:**
- Can override normal processes
- Can escalate to any level
- Final decision maker

### Operations Lead (OL)

**Responsibilities:**
- Technical investigation
- Execute remediation steps
- Coordinate engineering response
- Update IC on progress
- Document technical actions

### Communications Lead (CL)

**Responsibilities:**
- External communications (status page)
- Internal communications (stakeholders)
- Timeline documentation
- Coordinate with support
- Draft customer communications

---

## Incident Lifecycle

```
┌──────────────┐
│   Detect     │
│              │
│ • Alert      │
│ • Report     │
│ • Monitor    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Triage     │
│              │
│ • Severity   │
│ • Impact     │
│ • Assign IC  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Mobilize    │
│              │
│ • Page team  │
│ • Create ch  │
│ • Start doc  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Investigate │
│              │
│ • Diagnose   │
│ • Identify   │
│ • Document   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Remediate   │
│              │
│ • Fix/mitigate│
│ • Verify     │
│ • Monitor    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Resolve    │
│              │
│ • Confirm    │
│ • Communicate│
│ • Document   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Postmortem  │
│              │
│ • Analysis   │
│ • Actions    │
│ • Share      │
└──────────────┘
```

---

## Mandatory Capabilities

### Kill Switch

Pause all workflows immediately:

```bash
# Pause Temporal namespace
tctl namespace update --state disabled itqahn-prod

# Or per-workflow type
tctl workflow terminate --query "WorkflowType='FeatureWorkflow'"
```

### Credential Revocation

Revoke all active credentials:

```bash
# Revoke Vault leases
vault lease revoke -prefix auth/

# Revoke specific service
vault lease revoke -prefix database/creds/user-service/
```

### Deployment Rollback

```bash
# ArgoCD rollback
argocd app rollback user-service --revision 5

# Or Git revert
git revert HEAD
git push origin main
```

### Incident Channel

- Create dedicated Slack channel: `#inc-YYYYMMDD-short-desc`
- Add bot for timeline tracking
- Pin relevant dashboards
- Add all responders

### Timeline Document

```markdown
# Incident: user-service outage
**Severity**: P0
**IC**: @jane
**Status**: Investigating

## Timeline (UTC)
- 14:00 - Alert fired: user-service error rate >50%
- 14:02 - IC assigned, channel created
- 14:05 - Root cause identified: database connection exhaustion
- 14:10 - Mitigation: increased connection pool
- 14:15 - Verified: error rate returning to normal
- 14:30 - Incident resolved

## Impact
- Duration: 30 minutes
- Users affected: ~5,000
- Error budget consumed: 15%

## Root Cause
Connection pool configured too low for traffic spike.

## Action Items
- [ ] Increase default connection pool size
- [ ] Add alert for connection pool exhaustion
- [ ] Review capacity planning
```

---

## Communication Cadence

### Internal Updates

| Severity | Frequency | Channel |
|----------|-----------|---------|
| P0 | Every 15 min | Incident channel + email to execs |
| P1 | Every 30 min | Incident channel |
| P2 | Every hour | Incident channel |
| P3 | At resolution | Incident channel |

### External Updates

| Severity | First Update | Subsequent | Where |
|----------|--------------|------------|-------|
| P0 | Within 15 min | Every 30 min | Status page, email |
| P1 | Within 30 min | Every hour | Status page |
| P2 | Within 1 hour | At resolution | Status page |
| P3 | At resolution | - | - |

---

## Postmortems

### When Required

A postmortem is required when:
- >20% of error budget consumed
- Any data exposure (security incident)
- Repeat incident within 90 days
- P0 or P1 severity

### Postmortem Template

```markdown
# Postmortem: [Title]

## Summary
Brief description of the incident.

## Impact
- Duration:
- Users affected:
- Revenue impact:
- Error budget consumed:

## Timeline
Detailed timeline of events.

## Root Cause
Technical explanation of what went wrong.

## Contributing Factors
What made this worse or harder to detect.

## What Went Well
- Fast detection
- Effective communication
- Successful rollback

## What Could Be Improved
- Monitoring gaps
- Documentation gaps
- Process issues

## Action Items
| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| Add connection pool alert | @bob | 2026-01-13 | Open |

## Lessons Learned
Key takeaways for the team.
```

### Blameless Culture

- Focus on systems, not individuals
- Ask "what" failed, not "who" failed
- Assume good intent
- Share learnings widely

---

## Agent Roles in Incidents

| Agent | Role |
|-------|------|
| **Incident Commander** (human) | Overall coordination |
| **SRE Commander** | Technical investigation support |
| **Auto-Remediation Bot** | Execute safe remediations |
| **Runbook Author** | Update runbooks based on learnings |

---

## Operator Mode Incident Types

### Severity Levels for Operator Mode

| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| **P0** | Kill switch triggered, security breach | 5 min | Credential leak, runaway execution |
| **P1** | Multiple runs failing, merge queue stuck | 15 min | CI blocked, GitHub API down |
| **P2** | Single run failure, auto-remediation exhausted | 1 hour | Test failures, conflicts |
| **P3** | Performance degradation | 4 hours | Slow execution, high cost |

### Operator Mode Incident Categories

| Category | Trigger | Response |
|----------|---------|----------|
| **Security** | Credential exposure, prompt injection | Kill switch → Security review |
| **GitHub Automation** | API failure, rate limit, stuck queue | Auto-retry → Manual intervention |
| **CI/Pipeline** | Check failures, timeout | Auto-fix → Quarantine → Escalate |
| **Cost/Budget** | Budget exceeded, runaway spend | Pause → Operator approval |
| **Kill Switch** | Emergency stop activated | Full halt → Root cause → Recovery |

### Kill Switch Incident Protocol

When kill switch is activated:

```
┌──────────────────────────────────────────────────────────────────┐
│                KILL SWITCH INCIDENT PROTOCOL                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. IMMEDIATE (within 5 minutes)                                 │
│  ├── Confirm all workflows terminated                            │
│  ├── Verify merge queues frozen                                  │
│  ├── Confirm MCP credentials revoked                             │
│  └── Create incident channel #inc-kill-switch-{date}            │
│                                                                   │
│  2. ASSESS (within 15 minutes)                                   │
│  ├── Identify trigger reason                                     │
│  ├── Assess blast radius (affected runs, PRs)                    │
│  ├── Determine if secret rotation needed                         │
│  └── Classify severity                                           │
│                                                                   │
│  3. CONTAIN (as needed)                                          │
│  ├── Rotate compromised credentials (if security)                │
│  ├── Close orphaned PRs                                          │
│  ├── Revert any problematic merges                               │
│  └── Notify affected stakeholders                                │
│                                                                   │
│  4. RECOVER                                                       │
│  ├── Fix root cause                                              │
│  ├── Get security clearance (if security incident)               │
│  ├── Release kill switch via dashboard                           │
│  └── Resume or cleanup affected runs                             │
│                                                                   │
│  5. POSTMORTEM (required for all kill switch events)             │
│  ├── Document timeline                                            │
│  ├── Root cause analysis                                          │
│  ├── Action items for prevention                                  │
│  └── Share learnings                                              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Kill Switch Triggers

| Trigger | Auto/Manual | Actions |
|---------|-------------|---------|
| **Security scan critical** | Auto | Terminate, freeze, alert |
| **Cost circuit breaker** | Auto | Pause, notify, await approval |
| **Rate limit exhausted** | Auto | Pause, backoff, notify |
| **Manual activation** | Manual | Full halt, await recovery |
| **Credential leak detected** | Auto | Terminate, rotate, alert |

### Operator Mode Incident Roles

| Role | Responsibility |
|------|----------------|
| **Incident Commander** | Overall coordination (human) |
| **Platform Engineer** | Operator Mode infrastructure |
| **Security Engineer** | Security-related kill switch events |
| **GitHub Admin** | Repository and API issues |
| **Kill Switch Operator** | Authority to release kill switch |

---

## Related Documents

- `docs/00-overview/principles.md` — Operator Mode audit principles
- `docs/03-platform/portal-webapp.md` — Operator Mode dashboard and Kill Switch UI
- `docs/06-operations/runbooks.md` — Operator Mode failure runbooks
- `docs/06-operations/auto-remediation.md` — Automated response
- `docs/07-integrations/git-integration.md` — GitHub Automation Program
- `docs/07-integrations/webhooks-events.md` — Operator Mode events
- `docs/08-agents/agent-permissions.md` — Kill Switch permissions
- `templates/ops/POSTMORTEM.md` — Postmortem template

---

**Version**: 2.3.0 | **Date**: 2026-01-08
