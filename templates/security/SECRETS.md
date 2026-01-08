# Secrets & Key Management

## Principles
- Prefer workload identity (SPIFFE/OIDC) over static keys.
- Use dynamic secrets from Vault where needed.
- Never store secrets in:
  - Git
  - logs
  - prompts
  - screenshots
  - tickets

## Patterns
- Database credentials: dynamic, short TTL
- Third-party API keys: stored in Vault, rotated, scoped per tenant
- Encryption keys: managed KMS, never exportable

## Incident handling
If a secret is exposed:
1. revoke/rotate immediately
2. assess blast radius
3. scrub history where applicable
4. document in postmortem and evidence pack
