# Itqahn Continuous Improvement

> **Version:** 1.0.0
> **Status:** Normative
> **Last Updated:** 2026-01-08

## Overview

Itqahn Continuous Improvement enables the platform to improve itself safely over time. Improvements are sourced from operational data, validated through rigorous evaluation, and deployed with full rollback capability. This specification ensures autonomous improvement remains safe, observable, and reversible.

This specification defines:
- Improvement sources and collection
- The improvement pipeline and evaluation harness
- Guardrails preventing unsafe changes
- DORA-style metrics for Itqahn workflows
- Governance and approval requirements
- Edge cases and failure recovery

---

## 1. Improvement Sources

### 1.1 Source Categories

Itqahn collects improvement signals from five primary sources:

| Source | Signal Type | Collection Method | Frequency |
|--------|-------------|-------------------|-----------|
| **Operator Feedback** | Explicit ratings, corrections | Dashboard feedback widgets | Real-time |
| **Incident/Postmortem** | Failure patterns, root causes | Incident issue analysis | Per-incident |
| **Drift Review Outcomes** | Pattern recognition from drift | Track Assurance data | Per-review |
| **CI Failures** | Build/test failure patterns | GitHub Actions analysis | Per-run |
| **Product Analytics** | Usage patterns, drop-offs | Portal telemetry | Daily aggregate |

### 1.2 Operator Feedback Collection

Operators provide feedback through the Portal webapp:

```
┌─────────────────────────────────────────────────────────┐
│  RUN FEEDBACK                              run-abc123   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  How was this run?                                      │
│                                                         │
│  ☆ ☆ ☆ ☆ ☆   [1-5 rating]                             │
│                                                         │
│  What could be improved?                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ The generated auth code didn't handle refresh   │   │
│  │ tokens correctly. Had to manually fix.          │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Category:                                              │
│  ○ Code Quality    ○ Test Coverage    ● Missing Feature│
│  ○ Performance     ○ Documentation    ○ Other          │
│                                                         │
│  [Submit Feedback]              [Skip]                 │
└─────────────────────────────────────────────────────────┘
```

**Feedback Schema:**

```json
{
  "feedback_id": "fb-abc123",
  "run_id": "run-xyz789",
  "tenant_id": "tenant-acme",
  "rating": 3,
  "category": "missing_feature",
  "description": "The generated auth code didn't handle refresh tokens correctly.",
  "submitted_at": "2026-01-08T14:30:00Z",
  "context": {
    "workflow_stage": "build",
    "agent": "code-generator",
    "files_affected": ["src/auth/token.ts"]
  }
}
```

### 1.3 Incident/Postmortem Learnings

Incidents and postmortems are analyzed for improvement opportunities:

```yaml
# Extracted from incident postmortem
improvement_signal:
  source: incident
  incident_id: inc-20260108-001
  severity: P1
  root_cause: "Agent generated SQL query without parameterization"
  pattern_detected: "sql_injection_vulnerability"
  improvement_area: "code_generation_security"
  recommended_action: "Add SQL injection detection to code review agent"
  validation_approach: "Run SAST scanner on generated code samples"
```

### 1.4 Drift Review Pattern Recognition

Drift reviews are analyzed for recurring patterns:

```json
{
  "pattern_id": "drift-pattern-042",
  "pattern_name": "auth_implementation_gaps",
  "occurrences": 12,
  "first_seen": "2025-12-01",
  "last_seen": "2026-01-08",
  "common_drift_items": [
    "Missing CSRF protection",
    "OAuth state parameter not validated",
    "Session timeout not enforced"
  ],
  "improvement_hypothesis": "Auth spec template needs security checklist section"
}
```

### 1.5 CI Failure Analysis

Build and test failures are analyzed for patterns:

```json
{
  "failure_pattern_id": "ci-pattern-017",
  "pattern_name": "typescript_strict_mode_errors",
  "failure_count": 45,
  "failure_rate": 0.12,
  "common_errors": [
    "TS2345: Argument of type 'string | undefined' is not assignable",
    "TS2322: Type 'null' is not assignable to type"
  ],
  "improvement_hypothesis": "Code generator should default to strict null checks"
}
```

### 1.6 Product Analytics Signals

Portal usage patterns inform UX improvements:

```json
{
  "analytics_signal": {
    "metric": "wizard_completion_rate",
    "value": 0.72,
    "benchmark": 0.90,
    "drop_off_points": [
      {"step": "compliance_tier_selection", "drop_rate": 0.15},
      {"step": "integration_config", "drop_rate": 0.08}
    ],
    "improvement_hypothesis": "Simplify compliance tier selection with guided wizard"
  }
}
```

---

## 2. Improvement Pipeline

### 2.1 Pipeline Overview

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  Collect  │───▶│  Analyze  │───▶│ Candidate │───▶│  Evaluate │───▶│  Deploy   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
     │                │                │                │                │
     ▼                ▼                ▼                ▼                ▼
  Signals         Patterns         Improvement      Evaluator        Feature
  Database        & Clusters       Proposals        Harness          Flags
```

### 2.2 Improvement Candidate

An Improvement Candidate is a proposed change to Itqahn:

```json
{
  "candidate_id": "imp-2026-0108-001",
  "title": "Add refresh token handling to auth generator",
  "description": "Enhance code generator to include OAuth2 refresh token logic when auth specs include 'token_refresh: true'",

  "source": {
    "type": "operator_feedback",
    "signal_ids": ["fb-abc123", "fb-def456"],
    "pattern_id": "drift-pattern-042"
  },

  "category": "agent_behavior",
  "subcategory": "code_generation",

  "change_spec": {
    "component": "agents/code-generator",
    "files_modified": [
      "src/agents/code-generator/templates/auth.ts",
      "src/agents/code-generator/prompts/oauth.md"
    ],
    "estimated_impact": "medium"
  },

  "success_criteria": {
    "metric": "auth_drift_score",
    "baseline": 0.35,
    "target": 0.15,
    "measurement_window": "7d"
  },

  "rollback_trigger": {
    "metric": "auth_generation_failure_rate",
    "threshold": 0.05,
    "action": "auto_rollback"
  },

  "status": "pending_evaluation",
  "created_at": "2026-01-08T10:00:00Z"
}
```

### 2.3 Evaluator Harness

The Evaluator Harness validates improvements before deployment:

#### 2.3.1 Evaluation Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    EVALUATOR HARNESS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stage 1: STATIC ANALYSIS                                   │
│  ├── Syntax validation                                      │
│  ├── Type checking                                          │
│  ├── Security scan (SAST)                                   │
│  └── Dependency audit                                       │
│                                                              │
│  Stage 2: UNIT EVALUATION                                   │
│  ├── Run candidate in isolation                             │
│  ├── Compare output to baseline                             │
│  ├── Measure performance delta                              │
│  └── Check for regressions                                  │
│                                                              │
│  Stage 3: INTEGRATION EVALUATION                            │
│  ├── Deploy to shadow environment                           │
│  ├── Run against historical inputs                          │
│  ├── Compare outputs to recorded outputs                    │
│  └── Measure end-to-end metrics                             │
│                                                              │
│  Stage 4: CANARY EVALUATION                                 │
│  ├── Deploy to 5% of traffic                                │
│  ├── Monitor error rates                                    │
│  ├── Monitor success criteria metrics                       │
│  └── Duration: 24 hours minimum                             │
│                                                              │
│  Stage 5: GRADUAL ROLLOUT                                   │
│  ├── 5% → 25% → 50% → 100%                                  │
│  ├── 24h stabilization per stage                            │
│  ├── Automatic rollback on threshold breach                 │
│  └── Full deployment with feature flag                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3.2 Evaluation Dataset

The evaluator uses curated datasets:

```yaml
# .itqahn/evaluation/datasets.yaml
evaluation_datasets:
  - name: "golden_set_auth"
    description: "Verified auth generation examples"
    inputs: 50
    expected_outputs: verified
    source: "historical_runs_with_5star_ratings"

  - name: "regression_set_security"
    description: "Security vulnerability edge cases"
    inputs: 200
    expected_outputs: must_not_contain_vulnerabilities
    source: "security_team_curated"

  - name: "performance_baseline"
    description: "Performance benchmark scenarios"
    inputs: 100
    expected_outputs: timing_within_baseline
    source: "synthetic_generated"
```

#### 2.3.3 Evaluation Report

```json
{
  "evaluation_id": "eval-abc123",
  "candidate_id": "imp-2026-0108-001",
  "status": "PASSED",
  "completed_at": "2026-01-08T18:00:00Z",

  "stages": {
    "static_analysis": {
      "status": "PASSED",
      "duration_seconds": 45,
      "findings": []
    },
    "unit_evaluation": {
      "status": "PASSED",
      "duration_seconds": 180,
      "baseline_comparison": {
        "outputs_improved": 42,
        "outputs_unchanged": 8,
        "outputs_regressed": 0
      }
    },
    "integration_evaluation": {
      "status": "PASSED",
      "duration_seconds": 1200,
      "historical_replay": {
        "runs_replayed": 500,
        "success_rate": 0.998,
        "regression_detected": false
      }
    },
    "canary_evaluation": {
      "status": "PASSED",
      "duration_hours": 24,
      "traffic_percentage": 5,
      "metrics": {
        "error_rate": 0.001,
        "success_criteria_met": true,
        "rollback_triggered": false
      }
    }
  },

  "recommendation": "APPROVE_FOR_GRADUAL_ROLLOUT",
  "confidence_score": 0.94
}
```

### 2.4 Improvement PR

Approved improvements are deployed via Pull Request:

```markdown
## [Itqahn Improvement] Add refresh token handling to auth generator

### Improvement Summary
- **Candidate ID:** imp-2026-0108-001
- **Category:** Agent Behavior / Code Generation
- **Source:** Operator Feedback (12 signals), Drift Pattern Analysis

### Problem Statement
Auth code generation does not include refresh token handling when OAuth2
is specified, causing drift in 35% of auth-related workflows.

### Solution
Enhanced code generator templates and prompts to include refresh token
logic when `token_refresh: true` is specified in auth specs.

### Evaluation Results
- **Static Analysis:** PASSED
- **Unit Evaluation:** PASSED (42 improved, 0 regressed)
- **Integration Evaluation:** PASSED (500 runs, 99.8% success)
- **Canary Evaluation:** PASSED (24h, 5% traffic, 0.1% error rate)

### Success Criteria
- **Metric:** auth_drift_score
- **Baseline:** 0.35
- **Target:** 0.15
- **Measurement Window:** 7 days

### Rollback Plan
1. Disable feature flag: `improvement.auth_refresh_token`
2. Revert to previous template version
3. Monitor for 24h

### Feature Flag
```yaml
feature_flag:
  name: improvement.auth_refresh_token
  default: false
  rollout_percentage: 5
```

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Itqahn Improvement Pipeline <noreply@itqahn.dev>
```

---

## 3. Guardrails

### 3.1 No Silent Changes

**Rule:** All improvements MUST be visible and auditable.

**Enforcement:**
- Every improvement creates an Improvement PR
- PR includes full evaluation report
- Change is linked to source signals
- Feature flag controls deployment
- Audit log records all state transitions

```yaml
# OPA Policy: No silent changes
package improvement.guardrails

deny[msg] {
    input.improvement.has_pr == false
    msg := "Improvement must have associated PR"
}

deny[msg] {
    input.improvement.evaluation_report == null
    msg := "Improvement must have evaluation report"
}

deny[msg] {
    input.improvement.feature_flag == null
    msg := "Improvement must have feature flag"
}
```

### 3.2 Rollback Strategy

**Rule:** Every improvement MUST have a defined rollback strategy.

**Rollback Mechanisms:**

| Mechanism | Trigger | Speed | Risk |
|-----------|---------|-------|------|
| **Feature Flag** | Manual or automatic | Immediate | None |
| **Version Revert** | PR revert | Minutes | Low |
| **Config Rollback** | Configuration restore | Immediate | None |
| **Full Rollback** | Deployment rollback | Minutes | Medium |

**Automatic Rollback Triggers:**

```yaml
rollback_triggers:
  error_rate:
    threshold: 0.05  # 5% error rate increase
    window: 15m
    action: disable_feature_flag

  latency:
    threshold: 2.0  # 2x latency increase
    window: 15m
    action: disable_feature_flag

  success_criteria_regression:
    threshold: -0.1  # 10% regression from baseline
    window: 24h
    action: disable_feature_flag

  user_reports:
    threshold: 3  # 3 negative reports
    window: 1h
    action: alert_and_review
```

### 3.3 Feature Flags

**Rule:** All improvements MUST be deployed behind feature flags.

**Feature Flag Lifecycle:**

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  Created  │───▶│  Canary   │───▶│  Rollout  │───▶│  Stable   │
│  (0%)     │    │  (5%)     │    │ (5→100%)  │    │  (100%)   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
                      │                │
                      ▼                ▼
                ┌───────────┐    ┌───────────┐
                │ Disabled  │    │ Disabled  │
                │(Rollback) │    │(Rollback) │
                └───────────┘    └───────────┘
```

**Feature Flag Schema:**

```json
{
  "flag_id": "improvement.auth_refresh_token",
  "improvement_id": "imp-2026-0108-001",
  "status": "rollout",
  "rollout_percentage": 25,
  "rollout_schedule": {
    "2026-01-09T00:00:00Z": 5,
    "2026-01-10T00:00:00Z": 25,
    "2026-01-11T00:00:00Z": 50,
    "2026-01-12T00:00:00Z": 100
  },
  "targeting": {
    "include_tenants": [],
    "exclude_tenants": ["tenant-beta-sensitive"]
  },
  "kill_switch": {
    "enabled": true,
    "triggered": false
  }
}
```

### 3.4 Change Categories and Approval

| Category | Auto-Deploy Allowed | Approval Required |
|----------|---------------------|-------------------|
| **Prompt Tuning** | Yes (with evaluation) | None |
| **Template Update** | Yes (with evaluation) | None |
| **Agent Behavior** | Yes (with canary) | Platform team review |
| **API Change** | No | Platform team + tenant notice |
| **Security Fix** | Expedited | Security team review |
| **Breaking Change** | No | Platform team + all tenant notice |

---

## 4. Metrics (DORA-Style for Itqahn)

### 4.1 Core Metrics

Itqahn tracks DORA-inspired metrics for its own workflows:

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Deployment Frequency** | How often improvements ship | Daily | Improvement PRs merged / day |
| **Lead Time** | Signal to production | < 7 days | Time from signal to 100% rollout |
| **Change Failure Rate** | Improvements requiring rollback | < 5% | Rollbacks / total deployments |
| **Time to Restore** | Rollback completion time | < 15 min | Time from trigger to stable |

### 4.2 Workflow Performance Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Run Success Rate** | Runs completing without intervention | > 95% |
| **Drift Detection Rate** | Drift caught before merge | > 90% |
| **Mean Time to First Run** | New project to first successful run | < 1 hour |
| **Operator Satisfaction** | Average feedback rating | > 4.0 / 5.0 |
| **Improvement Adoption** | Improvements reaching 100% rollout | > 80% |

### 4.3 Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  ITQAHN IMPROVEMENT METRICS                    Last 30 Days │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DORA METRICS                                               │
│  ┌────────────────┬────────────────┬────────────────┐      │
│  │ Deploy Freq    │ Lead Time      │ Failure Rate   │      │
│  │ 2.3/day ↑      │ 4.2 days ↓     │ 2.1% ↓         │      │
│  │ (target: 1/day)│ (target: <7d)  │ (target: <5%)  │      │
│  └────────────────┴────────────────┴────────────────┘      │
│                                                              │
│  WORKFLOW PERFORMANCE                                        │
│  ┌────────────────┬────────────────┬────────────────┐      │
│  │ Run Success    │ Drift Detect   │ Satisfaction   │      │
│  │ 96.2% ↑        │ 92.1% ↑        │ 4.3/5.0 ↑      │      │
│  │ (target: >95%) │ (target: >90%) │ (target: >4.0) │      │
│  └────────────────┴────────────────┴────────────────┘      │
│                                                              │
│  IMPROVEMENT PIPELINE                                        │
│  ├── Signals Collected (30d):     1,247                     │
│  ├── Candidates Generated:        23                        │
│  ├── Candidates in Evaluation:    5                         │
│  ├── Candidates Deployed:         18                        │
│  └── Candidates Rolled Back:      1                         │
│                                                              │
│  [View Details]  [Export Report]  [Configure Alerts]        │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Trend Analysis

```
Improvement Impact Over Time (6 months)
─────────────────────────────────────────────────────────────
100% ┤
     │                                    ●────●────●
 95% ┤                          ●────●────
     │                    ●────●
 90% ┤              ●────●
     │        ●────●
 85% ┤  ●────●
     │
 80% ┼──────────────────────────────────────────────────────
     Jul    Aug    Sep    Oct    Nov    Dec    Jan

     ─── Run Success Rate
```

---

## 5. Governance

### 5.1 Improvement Review Board

The Improvement Review Board (IRB) oversees high-impact improvements:

**Composition:**
- Platform Engineering Lead
- Security Representative
- Tenant Advisory Representative (rotating)

**Review Triggers:**
- Breaking changes
- Security-related improvements
- Improvements affecting >50% of workflows
- Improvements with >$1000 cost impact

### 5.2 Tenant Notification

Tenants MUST be notified of improvements affecting them:

| Change Type | Notification | Lead Time |
|-------------|--------------|-----------|
| Non-breaking | In-app banner | At deployment |
| Behavior change | Email + banner | 7 days |
| Breaking change | Email + banner + acknowledgment | 30 days |
| Emergency fix | Email + banner | Immediate |

### 5.3 Opt-Out Mechanism

Tenants MAY opt out of specific improvements:

```yaml
# Tenant configuration
tenant_id: tenant-acme
improvement_settings:
  auto_adopt: true
  opt_outs:
    - improvement_id: imp-2026-0108-001
      reason: "Conflicts with custom auth implementation"
      expires: "2026-03-01"
  notification_preferences:
    email: true
    in_app: true
    require_acknowledgment: false
```

---

## 6. Edge Cases and Failure Recovery

### 6.1 Improvement Regression Detected

**Scenario:** Deployed improvement causes regression after full rollout.

**Resolution:**
1. Automatic rollback triggered by metrics
2. Feature flag disabled within 15 minutes
3. Incident created with regression details
4. Improvement status changed to `ROLLED_BACK`
5. Post-incident analysis:
   - Why did evaluation miss regression?
   - Update evaluation datasets
   - Consider additional evaluation stage

### 6.2 Self-Improvement Thrash

**Scenario:** Improvements oscillate (A improves X, B degrades X, A' improves X...).

**Detection:**
```python
def detect_thrash(improvements, metric, window_days=30):
    changes = get_metric_changes(improvements, metric, window_days)
    if alternating_pattern(changes) and len(changes) > 4:
        return ThrashDetected(metric, changes)
    return None
```

**Resolution:**
1. Thrash detection triggers automatic freeze
2. Alert sent to Improvement Review Board
3. Conflicting improvements analyzed together
4. Consolidated improvement created
5. Thrash prevention rule added

### 6.3 Metrics Gaming

**Scenario:** Improvement optimizes for metric but degrades actual experience.

**Prevention:**
1. Multiple correlated metrics required for success criteria
2. Operator satisfaction as mandatory secondary metric
3. Qualitative review of improvements with suspiciously good metrics
4. A/B testing with holdout groups for major improvements

### 6.4 Tenant Privacy in Analytics

**Scenario:** Improvement signals contain tenant-specific information.

**Resolution:**
1. All feedback is anonymized before analysis:
   - Tenant ID replaced with hash
   - Code snippets redacted
   - File paths generalized
2. Aggregation minimum: signals only analyzed with n >= 5 occurrences
3. Tenant MAY opt out of signal collection entirely
4. Signals are retained for 90 days, then aggregated/deleted

### 6.5 Evaluation Environment Drift

**Scenario:** Shadow environment differs from production, causing false positives.

**Resolution:**
1. Shadow environment synced weekly from production config
2. Data anonymization preserves distribution patterns
3. Canary evaluation in actual production (5%)
4. Regular validation: shadow results vs production outcomes
5. Alert if shadow/production divergence > 10%

### 6.6 Improvement Dependency Conflicts

**Scenario:** Two improvements in pipeline conflict with each other.

**Resolution:**
1. Dependency analysis before evaluation
2. Conflicting candidates evaluated sequentially, not parallel
3. If both pass individually, combined evaluation required
4. Conflict resolution options:
   - Merge into single improvement
   - Prioritize by signal volume
   - IRB decision

### 6.7 Runaway Improvement Costs

**Scenario:** Evaluation harness costs exceed budget.

**Resolution:**
1. Per-candidate evaluation budget cap: $100
2. Per-day pipeline budget cap: $500
3. Cost-aware scheduling: expensive evaluations batched off-peak
4. Cached evaluation results for unchanged components
5. Budget alerts at 80% threshold

---

## 7. Dashboard UX

### 7.1 Improvement Pipeline Panel

```
┌─────────────────────────────────────────────────────────┐
│  IMPROVEMENT PIPELINE                          [Filter] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SIGNALS (Last 7 Days)                                  │
│  ├── Operator Feedback: 47 signals                      │
│  ├── Drift Reviews: 23 patterns                         │
│  ├── CI Failures: 12 patterns                           │
│  └── Analytics: 8 signals                               │
│                                                         │
│  CANDIDATES                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ● imp-2026-0108-001  Auth refresh tokens        │   │
│  │   Status: Canary (5%)   Eval: PASSED            │   │
│  │   Source: 12 feedback signals                   │   │
│  │                                        [Details]│   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ● imp-2026-0107-003  TypeScript strict mode     │   │
│  │   Status: Rollout (50%)   Eval: PASSED          │   │
│  │   Source: CI failure analysis                   │   │
│  │                                        [Details]│   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ○ imp-2026-0108-002  Wizard UX simplification   │   │
│  │   Status: Evaluation   Stage: Integration       │   │
│  │   Source: Product analytics                     │   │
│  │                                        [Details]│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [View All Candidates]              [Signal Analysis]  │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Candidate Detail View

```
┌─────────────────────────────────────────────────────────┐
│  IMPROVEMENT CANDIDATE              imp-2026-0108-001   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Add refresh token handling to auth generator           │
│                                                         │
│  Status: ████████████░░░░░░░░ Canary (5%)              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ EVALUATION PIPELINE                             │   │
│  │                                                 │   │
│  │ ✓ Static Analysis      45s   PASSED            │   │
│  │ ✓ Unit Evaluation      3m    PASSED            │   │
│  │ ✓ Integration Eval     20m   PASSED            │   │
│  │ ● Canary Evaluation    18h   IN PROGRESS       │   │
│  │ ○ Gradual Rollout      -     PENDING           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ CANARY METRICS (Last 18h)                       │   │
│  │                                                 │   │
│  │ Error Rate:     0.1%  (threshold: 5%)    ✓     │   │
│  │ Auth Drift:     0.18  (target: <0.15)    ○     │   │
│  │ Latency p99:    120ms (baseline: 115ms)  ✓     │   │
│  │ User Feedback:  4.5/5 (baseline: 4.2/5)  ✓     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Pause Rollout]  [View PR]  [Trigger Rollback]        │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Audit and Compliance

### 8.1 Audit Trail

All improvement pipeline actions MUST be logged:

| Event | Required Fields |
|-------|-----------------|
| `improvement.signal_collected` | signal_id, source_type, tenant_id (hashed) |
| `improvement.candidate_created` | candidate_id, source_signals, category |
| `improvement.evaluation_started` | candidate_id, stage, timestamp |
| `improvement.evaluation_completed` | candidate_id, stage, result, duration |
| `improvement.pr_created` | candidate_id, pr_number, pr_url |
| `improvement.flag_updated` | candidate_id, flag_id, old_value, new_value |
| `improvement.rollout_progressed` | candidate_id, from_percentage, to_percentage |
| `improvement.rollback_triggered` | candidate_id, trigger_reason, metrics |
| `improvement.stable` | candidate_id, total_duration, final_metrics |

### 8.2 Evidence Pack Integration

Improvement evidence MUST be included in Evidence Packs for affected runs:

```json
{
  "evidence_type": "improvement_context",
  "run_id": "run-xyz789",
  "active_improvements": [
    {
      "improvement_id": "imp-2026-0108-001",
      "flag_status": "enabled",
      "rollout_percentage": 25,
      "enabled_for_run": true
    }
  ],
  "improvement_history": [
    {
      "improvement_id": "imp-2026-0101-005",
      "deployed_at": "2026-01-05T00:00:00Z",
      "status": "stable"
    }
  ]
}
```

---

## 9. Configuration

### 9.1 Global Configuration

```yaml
# config/improvement-pipeline.yaml
improvement_pipeline:
  enabled: true

  signal_collection:
    feedback_enabled: true
    incident_analysis_enabled: true
    drift_pattern_enabled: true
    ci_failure_analysis_enabled: true
    analytics_enabled: true

  evaluation:
    static_analysis:
      enabled: true
      timeout_seconds: 300
    unit_evaluation:
      enabled: true
      timeout_seconds: 600
      dataset: "golden_set"
    integration_evaluation:
      enabled: true
      timeout_seconds: 3600
      replay_count: 500
    canary:
      enabled: true
      duration_hours: 24
      traffic_percentage: 5

  rollout:
    stages: [5, 25, 50, 100]
    stabilization_hours: 24
    auto_advance: true

  guardrails:
    require_pr: true
    require_feature_flag: true
    require_rollback_plan: true
    max_evaluation_cost: 100

  rollback:
    auto_enabled: true
    error_rate_threshold: 0.05
    latency_multiplier_threshold: 2.0
```

### 9.2 Tenant Override Configuration

```yaml
# Per-tenant override
tenant_id: tenant-acme
improvement_overrides:
  pipeline:
    canary_duration_hours: 48  # Longer canary
    rollout_stages: [5, 10, 25, 50, 100]  # More gradual

  notifications:
    require_acknowledgment: true
    lead_time_days: 14  # More notice

  opt_outs:
    - category: "agent_behavior"
      reason: "Custom agent modifications"
```

---

## 10. Related Documentation

- [Track Assurance](../03-platform/track-assurance.md) - Drift pattern source
- [Evidence Pack](../05-compliance/evidence-pack.md) - Improvement evidence
- [Agent Quality Bar](../08-agents/agent-quality-bar.md) - Quality gates for improvements
- [Runbooks](./runbooks.md) - Improvement incident response
- [Git Integration](../07-integrations/git-integration.md) - Improvement PR workflow

---

## Appendix A: Improvement Candidate Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ImprovementCandidate",
  "type": "object",
  "required": ["candidate_id", "title", "description", "source", "category", "change_spec", "success_criteria", "rollback_trigger"],
  "properties": {
    "candidate_id": {
      "type": "string",
      "pattern": "^imp-\\d{4}-\\d{4}-\\d{3}$"
    },
    "title": {
      "type": "string",
      "maxLength": 100
    },
    "description": {
      "type": "string",
      "maxLength": 1000
    },
    "source": {
      "type": "object",
      "required": ["type", "signal_ids"],
      "properties": {
        "type": {
          "enum": ["operator_feedback", "incident", "drift_pattern", "ci_failure", "analytics"]
        },
        "signal_ids": {
          "type": "array",
          "items": { "type": "string" }
        },
        "pattern_id": { "type": "string" }
      }
    },
    "category": {
      "enum": ["prompt_tuning", "template_update", "agent_behavior", "api_change", "security_fix", "breaking_change"]
    },
    "change_spec": {
      "type": "object",
      "required": ["component", "files_modified"],
      "properties": {
        "component": { "type": "string" },
        "files_modified": {
          "type": "array",
          "items": { "type": "string" }
        },
        "estimated_impact": {
          "enum": ["low", "medium", "high"]
        }
      }
    },
    "success_criteria": {
      "type": "object",
      "required": ["metric", "baseline", "target"],
      "properties": {
        "metric": { "type": "string" },
        "baseline": { "type": "number" },
        "target": { "type": "number" },
        "measurement_window": { "type": "string" }
      }
    },
    "rollback_trigger": {
      "type": "object",
      "required": ["metric", "threshold", "action"],
      "properties": {
        "metric": { "type": "string" },
        "threshold": { "type": "number" },
        "action": {
          "enum": ["auto_rollback", "alert_and_review", "manual"]
        }
      }
    },
    "status": {
      "enum": ["pending_evaluation", "evaluating", "approved", "deploying", "stable", "rolled_back", "rejected"]
    }
  }
}
```
