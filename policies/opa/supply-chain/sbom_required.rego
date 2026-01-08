package itqahn.supplychain

default allow := false
default reasons := ["SBOM is required for release candidate artifacts"]

allow {
  input.action == "release.candidate"
  input.evidence.sbom.present == true
  reasons := []
}

reasons[reason] {
  input.action == "release.candidate"
  input.evidence.sbom.present != true
  reason := "Missing SBOM"
}
