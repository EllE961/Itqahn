# policies/opa/github/merge_requirements.rego
#
# GitHub Merge Requirements Policy for Itqahn
#
# This policy enforces merge requirements for Pull Requests
# created by Operator Mode automation.
#
# Version: 1.0.0
# Date: 2026-01-08

package github.merge

import future.keywords.in

# Default: deny merge
default allow_merge = false

# Allow merge if all requirements are met
allow_merge {
    all_checks_passed
    required_reviews_obtained
    no_merge_conflicts
    branch_up_to_date
    evidence_pack_complete
    not blocked_by_policy
}

# All CI checks must pass
all_checks_passed {
    input.pr.checks.conclusion == "success"
}

# Required reviews must be obtained
required_reviews_obtained {
    count(input.pr.reviews.approved) >= input.repository.required_approvals
}

# No merge conflicts
no_merge_conflicts {
    input.pr.mergeable == true
    input.pr.mergeable_state == "clean"
}

# Branch must be up to date with base
branch_up_to_date {
    input.pr.base_up_to_date == true
}

# Evidence pack required for T3/T4 compliance tiers
evidence_pack_complete {
    input.compliance_tier in ["T1", "T2"]
}

evidence_pack_complete {
    input.compliance_tier in ["T3", "T4"]
    input.evidence_pack.status == "complete"
    input.evidence_pack.policy_verdict == "pass"
}

# Not blocked by any policy gate
blocked_by_policy {
    some policy in input.policy_gates
    policy.verdict == "deny"
}

# -----------------------------------------------------------------------------
# Operator Mode Specific Rules
# -----------------------------------------------------------------------------

# Auto-merge allowed for Operator Mode PRs
allow_auto_merge {
    allow_merge
    input.pr.created_by == "itqahn-bot"
    input.pr.labels[_] == "operator-mode"
    input.auto_merge_enabled == true
}

# Merge queue enrollment allowed
allow_merge_queue {
    allow_merge
    input.pr.base == "main"
    input.repository.merge_queue_enabled == true
}

# -----------------------------------------------------------------------------
# High Risk Merge Rules
# -----------------------------------------------------------------------------

# High risk PRs require additional approvals
high_risk_pr {
    input.risk_flags[_] in ["auth", "payments", "regulated_data", "security"]
}

# Require security review for high risk
require_security_review {
    high_risk_pr
    not security_review_approved
}

security_review_approved {
    some review in input.pr.reviews.approved
    review.team == "security-team"
}

# T4 compliance requires CAB approval
require_cab_approval {
    input.compliance_tier == "T4"
    not cab_approval_obtained
}

cab_approval_obtained {
    input.approvals.cab == true
}

# -----------------------------------------------------------------------------
# Deny Reasons (for error messages)
# -----------------------------------------------------------------------------

deny[msg] {
    not all_checks_passed
    msg := "CI checks have not passed"
}

deny[msg] {
    not required_reviews_obtained
    msg := sprintf("Required approvals not obtained (%d/%d)", [
        count(input.pr.reviews.approved),
        input.repository.required_approvals
    ])
}

deny[msg] {
    not no_merge_conflicts
    msg := "PR has merge conflicts"
}

deny[msg] {
    not branch_up_to_date
    msg := "Branch is not up to date with base"
}

deny[msg] {
    input.compliance_tier in ["T3", "T4"]
    input.evidence_pack.status != "complete"
    msg := "Evidence pack is required for T3/T4 compliance"
}

deny[msg] {
    require_security_review
    msg := "Security team review required for high-risk changes"
}

deny[msg] {
    require_cab_approval
    msg := "Change Advisory Board approval required for T4 compliance"
}

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------

metadata := {
    "policy_name": "github.merge_requirements",
    "version": "1.0.0",
    "description": "Enforces merge requirements for Operator Mode PRs",
    "enforcement": "blocking"
}
