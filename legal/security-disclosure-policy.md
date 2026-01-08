# Security Disclosure Policy

**Effective Date:** 2026-01-06

This document describes Itqahn's security posture and vulnerability disclosure program.

---

## Security Posture

### Security Fundamentals

Itqahn implements defense-in-depth security:

| Control | Implementation |
|---------|----------------|
| **Policy-as-Code** | OPA and Kyverno governance |
| **Evidence-First Releases** | SBOM, provenance, signed evidence packs |
| **Secretless Access** | Workload identity (SPIFFE) + dynamic secrets (Vault) |
| **Multi-Tenant Isolation** | Namespace separation, RBAC, network policies |
| **Continuous Scanning** | SAST, SCA, secret scanning, container scanning |
| **Supply Chain Security** | SLSA Level 3 compliance, signed artifacts |

### Security Certifications

- SOC 2 Type II (in progress)
- ISO 27001 (planned)

### Incident Response

For incident response procedures, see `docs/06-operations/incident-response.md`.

---

## Vulnerability Disclosure Program

We welcome responsible disclosure of security vulnerabilities.

### Reporting Vulnerabilities

**Email:** security@itqahn.io

Include in your report:
- Affected component or service
- Detailed steps to reproduce
- Impact assessment
- Proof-of-concept (if available)
- Your contact information

### Safe Harbor

We will not pursue legal action against security researchers who:

- Act in good faith
- Avoid privacy violations and data access
- Avoid service disruption
- Comply with this policy
- Report findings promptly

### Our Commitment

Upon receiving a vulnerability report, we will:

| Step | Timeline |
|------|----------|
| Acknowledge receipt | 1 business day |
| Initial assessment | 3 business days |
| Severity classification | 5 business days |
| Remediation timeline | Based on severity |
| Researcher credit | Upon fix release |

### Severity Classification

| Severity | Response Time | Examples |
|----------|---------------|----------|
| Critical | 24 hours | RCE, auth bypass, data breach |
| High | 7 days | Privilege escalation, XSS with impact |
| Medium | 30 days | Information disclosure, CSRF |
| Low | 90 days | Minor issues, hardening recommendations |

### Prohibited Actions

Security researchers must NOT:

- Access or modify customer data
- Perform denial-of-service attacks
- Use social engineering against employees
- Test against production systems without authorization
- Publicly disclose before remediation

### Bug Bounty

We operate a private bug bounty program. Contact security@itqahn.io for details.

---

## Customer Responsibilities

Customers using Itqahn must:

- Configure SSO/MFA appropriately
- Enforce least privilege in their organization
- Review and validate generated Output before production use
- Report suspected security incidents promptly
- Keep integrations and dependencies updated
- Follow secure configuration guidelines

---

## Contact

| Purpose | Contact |
|---------|---------|
| Security vulnerabilities | security@itqahn.io |
| Security questions | security@itqahn.io |
| Compliance inquiries | compliance@itqahn.io |

---

**Note:** This is a template document. Adapt for your actual deployment and have legal counsel review before publication.

---

**Version**: 2.0.0 | **Date**: 2026-01-06
