package itqahn.deploy

default allow := false
default reasons := ["Deployment requires a valid Evidence Pack reference"]

# Allow deployments only when evidence pack is present and signed.
allow {
  input.action == "deploy.request"
  input.evidence.pack_id != ""
  input.evidence.signature_hash != ""
  reasons := []
}

reasons[reason] {
  input.action == "deploy.request"
  input.evidence.pack_id == ""
  reason := "Missing evidence.pack_id"
}

reasons[reason] {
  input.action == "deploy.request"
  input.evidence.signature_hash == ""
  reason := "Missing evidence.signature_hash"
}
