# policies/opa/operator/audit_required.rego
#
# Operator Mode Audit Requirements Policy for Itqahn
#
# This policy ensures all Operator Mode runs maintain audit trails
# even when running with --dangerously-skip-permissions.
#
# Version: 1.0.0
# Date: 2026-01-08

package operator.audit

import future.keywords.in

# Default: deny run without audit
default allow_run = false

# Allow run if all audit requirements are met
allow_run {
    has_valid_run_id
    has_tenant_context
    has_workflow_context
    audit_logging_enabled
    evidence_pack_configured
    not kill_switch_active
}

# Run must have valid run ID
has_valid_run_id {
    startswith(input.run_id, "run-")
    count(input.run_id) > 4
}

# Run must have tenant context
has_tenant_context {
    input.tenant_id != ""
    input.tenant_id != null
}

# Run must have workflow context
has_workflow_context {
    startswith(input.workflow_id, "wf-")
}

# Audit logging must be enabled
audit_logging_enabled {
    input.audit.enabled == true
    input.audit.destination != ""
}

# Evidence pack must be configured
evidence_pack_configured {
    input.evidence_pack.enabled == true
    input.evidence_pack.output_path != ""
}

# Kill switch must not be active
kill_switch_active {
    input.kill_switch.status == "active"
}

# -----------------------------------------------------------------------------
# Audit Trail Requirements
# -----------------------------------------------------------------------------

# All actions must be logged
require_action_logging {
    input.action.type != ""
}

# Actions must include correlation IDs
action_has_correlation {
    require_action_logging
    input.action.run_id == input.run_id
    input.action.workflow_id == input.workflow_id
}

# MCP calls must be logged
mcp_call_logged {
    input.action.type == "mcp_call"
    input.action.mcp_server != ""
    input.action.tool != ""
    input.action.timestamp != ""
}

# Tool calls must include input/output hashes
tool_call_auditable {
    input.action.type == "tool_call"
    input.action.input_hash != ""
    input.action.output_hash != ""
}

# Git operations must be logged
git_operation_logged {
    input.action.type == "git_operation"
    input.action.operation in ["commit", "push", "pr_create", "merge"]
    input.action.ref != ""
}

# -----------------------------------------------------------------------------
# Bypass Constraints
# -----------------------------------------------------------------------------

# --dangerously-skip-permissions does NOT bypass these
mandatory_requirements := [
    "audit_logging",
    "evidence_pack",
    "run_id_tracking",
    "tenant_isolation",
    "cost_tracking"
]

# Verify mandatory requirements are met
all_mandatory_met {
    audit_logging_enabled
    evidence_pack_configured
    has_valid_run_id
    has_tenant_context
    cost_tracking_enabled
}

cost_tracking_enabled {
    input.cost_tracking.enabled == true
    input.cost_tracking.budget_id != ""
}

# -----------------------------------------------------------------------------
# Evidence Pack Requirements
# -----------------------------------------------------------------------------

# Evidence pack must be generated at run completion
evidence_pack_required {
    input.run.status in ["completed", "failed"]
}

# Evidence pack must include required artifacts
evidence_pack_complete {
    evidence_pack_required
    evidence_has_run_record
    evidence_has_git_record
    evidence_has_policy_verdicts
}

evidence_has_run_record {
    input.evidence_pack.artifacts.run_record != null
}

evidence_has_git_record {
    input.evidence_pack.artifacts.git_evidence != null
}

evidence_has_policy_verdicts {
    input.evidence_pack.artifacts.policy_verdicts != null
}

# -----------------------------------------------------------------------------
# Kill Switch Rules
# -----------------------------------------------------------------------------

# Kill switch activation requires immediate halt
kill_switch_halt_required {
    kill_switch_active
}

# Actions blocked when kill switch active
action_blocked_by_kill_switch {
    kill_switch_active
    input.action.type != "audit_log"
}

# Only audit logging allowed during kill switch
allow_during_kill_switch {
    kill_switch_active
    input.action.type == "audit_log"
}

# -----------------------------------------------------------------------------
# Credential Handling
# -----------------------------------------------------------------------------

# Credentials must never be logged
credential_exposure_blocked {
    input.action.output
    contains_credential(input.action.output)
}

contains_credential(output) {
    patterns := [
        "api_key",
        "secret",
        "password",
        "token",
        "credential"
    ]
    some pattern in patterns
    contains(lower(output), pattern)
}

# Credentials must be injected via Vault
credential_injection_valid {
    input.credential_source == "vault"
    input.credential_path != ""
}

# -----------------------------------------------------------------------------
# Deny Reasons (for error messages)
# -----------------------------------------------------------------------------

deny[msg] {
    not has_valid_run_id
    msg := "Run ID is required for audit trail"
}

deny[msg] {
    not has_tenant_context
    msg := "Tenant context is required for audit trail"
}

deny[msg] {
    not audit_logging_enabled
    msg := "Audit logging must be enabled for Operator Mode runs"
}

deny[msg] {
    not evidence_pack_configured
    msg := "Evidence pack must be configured for Operator Mode runs"
}

deny[msg] {
    kill_switch_active
    input.action.type != "audit_log"
    msg := "Kill switch is active - all actions blocked except audit logging"
}

deny[msg] {
    credential_exposure_blocked
    msg := "Credential exposure detected in action output - blocked"
}

deny[msg] {
    evidence_pack_required
    not evidence_pack_complete
    msg := "Evidence pack is incomplete - missing required artifacts"
}

# -----------------------------------------------------------------------------
# Warnings (non-blocking)
# -----------------------------------------------------------------------------

warn[msg] {
    not cost_tracking_enabled
    msg := "Cost tracking is recommended for Operator Mode runs"
}

warn[msg] {
    input.run.duration_seconds > 3600
    msg := "Run has exceeded 1 hour duration - consider checkpointing"
}

warn[msg] {
    input.cost_tracking.current_cost > input.cost_tracking.budget * 0.8
    msg := sprintf("Run has used %.0f%% of budget", [
        input.cost_tracking.current_cost / input.cost_tracking.budget * 100
    ])
}

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------

metadata := {
    "policy_name": "operator.audit_required",
    "version": "1.0.0",
    "description": "Enforces audit requirements for Operator Mode runs",
    "enforcement": "blocking",
    "bypasses": "NONE - audit is mandatory even with --dangerously-skip-permissions"
}
