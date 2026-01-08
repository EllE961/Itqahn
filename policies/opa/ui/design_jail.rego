package itqahn.ui

default allow := true

# Block merges that violate Design Jail rules when UI is touched.
ui_touched {
  input.context.ui_change == true
}

allow {
  input.action != "merge.request"
}

allow {
  input.action == "merge.request"
  not ui_touched
}

allow {
  input.action == "merge.request"
  ui_touched
  input.findings.design_jail.violations == 0
}

deny_reason[reason] {
  input.action == "merge.request"
  ui_touched
  input.findings.design_jail.violations > 0
  reason := "Design Jail violations present; block merge"
}
