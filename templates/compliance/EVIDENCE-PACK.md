# Evidence Pack Specification

## Manifest
The manifest is the index of all evidence items.

Required fields:
- pack_id
- git_commit
- build_id
- created_at
- compliance_tier
- artifacts (SBOM, provenance, scans, tests, approvals)
- signature_hash

## Signing
Evidence packs must be signed and verified before deployment.

## Storage
Evidence must be immutable and retained per retention policy.
