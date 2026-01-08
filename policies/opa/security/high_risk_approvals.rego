package itqahn.security

default allow := true

# High-risk changes require explicit human approval attestation.
high_risk {
  input.context.touches_auth == true
} 
high_risk {
  input.context.destructive_migration == true
}
high_risk {
  input.context.payments == true
}

allow {
  input.action != "merge.request"
}

allow {
  input.action == "merge.request"
  not high_risk
}

allow {
  input.action == "merge.request"
  high_risk
  input.evidence.human_approval.present == true
}

deny_reason[reason] {
  input.action == "merge.request"
  high_risk
  input.evidence.human_approval.present != true
  reason := "High-risk change requires human approval attestation"
}
