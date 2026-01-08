# Privacy Policy (Template)

**Effective date:** 2026-01-06

> This template must be reviewed by qualified legal counsel before use.

## 1. Overview
This Privacy Policy describes how the Itqahn Service collects, uses, and protects personal information.

## 2. Information We Collect
Depending on configuration, we may process:
- account identifiers (name, email, org identifiers)
- authentication metadata (SSO attributes)
- usage telemetry (events, logs, metrics)
- support communications
- limited content required to provide the Service (e.g., prompts, documents) as configured by Customer

## 3. How We Use Information
We use information to:
- provide and operate the Service
- secure the Service (fraud prevention, access control)
- generate auditability artifacts (Evidence Packs, policy decisions)
- respond to support requests
- improve reliability and quality (aggregated analytics)

## 4. Data Minimization
The Service is designed to minimize sensitive data exposure:
- dynamic secrets (Vault) prevent static key storage
- prompts can be stored as hashes or encrypted depending on Customer preference
- Evidence Packs can reference inputs without storing full content

## 5. Sharing
We do not sell personal information.
We may share information with:
- subprocessors needed to operate the Service (e.g., hosting, email)
- third-party integrations activated by Customer (e.g., Git providers)

## 6. Retention
Retention is controlled by Customer policy profiles and configured schedules.
See `templates/compliance/RETENTION-POLICY.md`.

## 7. Security
We use administrative, technical, and physical safeguards, including:
- least privilege access,
- encryption in transit and at rest,
- audit logs,
- vulnerability management.

## 8. Your Rights
Depending on jurisdiction, Users may have rights to access, correct, delete, or restrict processing.
Customer is the controller in most enterprise deployments; requests should go through Customer’s admin.

## 9. International Transfers
To be defined based on hosting and customer location.

## 10. Contact
To be defined.
