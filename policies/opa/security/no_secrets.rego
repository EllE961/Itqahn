package itqahn.security

default allow := true

# Simple secret-detection based on findings produced by scanners.
# In practice, scanners should produce structured findings.
allow {
  input.action != "merge.request"
}

allow {
  input.action == "merge.request"
  count(input.findings.secrets) == 0
}

deny_reason[reason] {
  input.action == "merge.request"
  count(input.findings.secrets) > 0
  reason := "Secret findings present; block merge"
}
