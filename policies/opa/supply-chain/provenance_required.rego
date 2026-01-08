package itqahn.supplychain

default allow := false
default reasons := ["Build provenance is required for release candidate artifacts"]

allow {
  input.action == "release.candidate"
  input.evidence.provenance.present == true
  reasons := []
}

reasons[reason] {
  input.action == "release.candidate"
  input.evidence.provenance.present != true
  reason := "Missing provenance"
}
