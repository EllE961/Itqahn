package itqahn.finops

default allow := true

allow {
  input.action != "workflow.continue"
}

allow {
  input.action == "workflow.continue"
  input.context.token_budget_remaining > 0
}

deny_reason[reason] {
  input.action == "workflow.continue"
  input.context.token_budget_remaining <= 0
  reason := "Token budget exhausted; pause workflow"
}
