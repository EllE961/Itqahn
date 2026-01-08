# Security Disclosure (Template)

**Effective date:** 2026-01-06

This document summarizes the security posture of the Itqahn Service.

## Security fundamentals
- policy-as-code governance (OPA/Kyverno)
- evidence-first releases (SBOM + provenance + signed evidence packs)
- secretless access (workload identity + dynamic secrets)
- multi-tenant isolation controls
- continuous vulnerability management

## Incident response
See `docs/19-incident-response.md`.

## Customer responsibilities
Customers must:
- configure SSO/MFA appropriately,
- enforce least privilege in their org,
- review and validate generated Output before production use,
- report suspected incidents promptly.

This is a template and should be adapted for your actual deployment.
