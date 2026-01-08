# Security Model

This document defines the threat model, security architecture, and hard requirements for Itqahn.

---

## Threat Model Baseline

Itqahn must assume adversarial inputs at all layers:

| Threat Source | Attack Vector | Impact |
|---------------|---------------|--------|
| **User prompts** | Prompt injection | Tool abuse, data exfiltration |
| **Documents** | RAG poisoning | Malicious code generation |
| **Dependencies** | Typosquatting, supply chain | Backdoors, malware |
| **Tenants** | Cross-tenant access | Data breach |
| **Insiders** | Privilege escalation | Full system compromise |

---

## Primary Risk Domains

### 1. Auth/Authz Flaws (Highest Risk)

| Risk | Mitigation |
|------|------------|
| Authentication bypass | OIDC/OAuth with strong IdP |
| Authorization bypass | OPA policy enforcement everywhere |
| Token theft | Short-lived tokens, rotation |
| Session hijacking | Secure cookies, fingerprinting |

### 2. Prompt Injection → Tool Abuse

| Risk | Mitigation |
|------|------------|
| Direct injection | Input sanitization, structured prompts |
| Indirect injection (RAG) | Document scanning, allowlists |
| Tool manipulation | Tool output validation, allowlists |

See `docs/04-security/prompt-injection-defense.md`.

### 3. Supply Chain

| Risk | Mitigation |
|------|------------|
| Typosquatting | Dependency allowlists |
| Compromised packages | SBOM analysis, vulnerability scanning |
| Build tampering | Hermetic builds, SLSA provenance |
| Artifact substitution | Signature verification |

### 4. Multi-Tenant Isolation Failures

| Risk | Mitigation |
|------|------------|
| Data leakage | Row-level security, namespace isolation |
| Context leakage | Separate vector namespaces |
| Resource abuse | Quotas, rate limiting |
| Privilege escalation | Tenant-scoped RBAC |

### 5. Secret Leakage

| Risk | Mitigation |
|------|------------|
| Secrets in code | Pre-commit scanning, CI gates |
| Secrets in logs | Log scrubbing, structured logging |
| Secrets in prompts | Prompt sanitization |
| Long-lived credentials | Dynamic secrets, short TTL |

### 6. Unsafe Deployments

| Risk | Mitigation |
|------|------------|
| Unsigned artifacts | Signature verification at admission |
| Missing evidence | Evidence Pack requirement |
| No rollback | Canary deployments, GitOps |
| Drift from approved state | Continuous reconciliation |

### 7. Denial-of-Wallet

| Risk | Mitigation |
|------|------------|
| LLM cost explosion | Token budgets, circuit breakers |
| Cloud cost explosion | Resource quotas, anomaly detection |
| Storage abuse | TTL enforcement, cleanup jobs |

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Identity   │  │   Policy    │  │  Supply     │             │
│  │  (SPIFFE)   │  │   (OPA)     │  │  Chain      │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐             │
│  │  Secrets    │  │  Admission  │  │  AppSec     │             │
│  │  (Vault)    │  │  (Kyverno)  │  │  (SAST/SCA) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    OBSERVABILITY                          │   │
│  │         Audit logs | Security events | Anomaly detection │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Authentication

| Method | Use Case |
|--------|----------|
| OIDC/OAuth | User authentication |
| SPIFFE SVID | Workload authentication |
| API keys | Programmatic access |
| mTLS | Service-to-service |

### Authorization

| Layer | Enforcement |
|-------|-------------|
| API Gateway | Token validation, rate limiting |
| Service | OPA sidecar or library |
| Database | Row-level security |
| Kubernetes | RBAC + Kyverno |

### Tenant Isolation

| Control | Implementation |
|---------|----------------|
| Data isolation | Namespace per tenant, RLS |
| Network isolation | Network policies |
| Compute isolation | Resource quotas, optional node pools |
| Context isolation | Separate vector stores |

---

## Hard Requirements

These requirements **cannot be bypassed** under any circumstances:

| Requirement | Enforcement |
|-------------|-------------|
| No cross-tenant data access | RLS, policy, code review |
| No plaintext secrets in code/logs/prompts | Scanning, structured logging |
| No deployment without signed evidence | Admission webhook |
| No privileged containers in data plane | Kyverno policy |
| No network egress from builds except curated registries | Network policy |

---

## Security Gates

### CI Pipeline Gates

| Gate | Tool | Blocks On |
|------|------|-----------|
| SAST | Semgrep | High/Critical findings |
| SCA | Dependabot, Snyk | High/Critical CVEs |
| Secret scan | Gitleaks | Any detection |
| Container scan | Trivy | High/Critical findings |
| License scan | Licensee | Disallowed licenses |

### Human Review Triggers

Code requires human security review when:

- Auth/authz logic changes
- Cryptographic code changes
- Input validation changes
- External API integration
- Infrastructure changes
- Policy changes

---

## Security Monitoring

### Real-Time Detection

| Signal | Detection |
|--------|-----------|
| Anomalous API calls | Rate limiting, pattern matching |
| Privilege escalation attempts | Audit log analysis |
| Cross-tenant access attempts | Policy denial logs |
| Secret access patterns | Vault audit logs |

### Security Dashboards

| Dashboard | Metrics |
|-----------|---------|
| Authentication | Failed logins, MFA usage, session duration |
| Authorization | Policy denials, escalation attempts |
| Vulnerabilities | Open CVEs, MTTR, scan coverage |
| Secrets | Rotation status, access frequency |

---

## Incident Response

Security incidents trigger:

1. **Automatic containment** (revoke credentials, isolate workload)
2. **Alert** to security on-call
3. **Workflow pause** for affected tenant
4. **Forensic data collection**

See `docs/06-operations/incident-response.md`.

---

## Related Documents

- `docs/04-security/identity-spiffe.md` — Workload identity
- `docs/04-security/secrets-vault.md` — Secret management
- `docs/04-security/prompt-injection-defense.md` — AI security
- `docs/04-security/appsec-asvs.md` — Application security
- `docs/04-security/red-team-program.md` — Adversarial testing

---

**Version**: 2.0.0 | **Date**: 2026-01-06
