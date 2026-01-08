# Application Security (OWASP ASVS)

Itqahn enforces OWASP Application Security Verification Standard (ASVS) requirements through automated gates and human review.

---

## ASVS Levels

| Level | Description | When Required |
|-------|-------------|---------------|
| **Level 1** | Opportunistic | All applications (automated) |
| **Level 2** | Standard | Production, sensitive data |
| **Level 3** | Advanced | Regulated, high-value targets |

### Level by Compliance Tier

| Compliance Tier | ASVS Level |
|-----------------|------------|
| Baseline | Level 1 |
| Sensitive | Level 2 |
| Regulated | Level 2+3 (selected controls) |

---

## V1: Architecture

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V1.1.1 - Secure SDLC | SSDF mapping | Hard |
| V1.2.1 - Threat model | Threat Modeler agent | Gate 2 |
| V1.5.1 - Input validation | SAST rules | Hard |

### Human Review

| Control | Trigger |
|---------|---------|
| V1.2.2 - Trust boundaries | New service architecture |
| V1.4.1 - Access control architecture | Auth/authz changes |

---

## V2: Authentication

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V2.1.1 - Password length | SAST | Hard |
| V2.2.1 - Anti-automation | Rate limiting config | Hard |
| V2.5.1 - Default credentials | Secret scan | Hard |

### Human Review (Always Required)

| Control | Reason |
|---------|--------|
| V2.4 - Credential storage | Security-critical |
| V2.6 - Password reset | Abuse potential |
| V2.8 - Session management | Complex attack surface |

### Policy Enforcement

```rego
# policies/opa/security/auth.rego
package security.auth

deny[msg] {
  input.password_min_length < 12
  msg := "V2.1.1: Password minimum length must be at least 12 characters"
}

deny[msg] {
  not input.mfa_enabled
  input.risk_tier == "regulated"
  msg := "V2.8.1: MFA required for regulated tier"
}
```

---

## V3: Session Management

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V3.1.1 - Session ID generation | SAST | Hard |
| V3.2.1 - Session timeout | Config validation | Hard |
| V3.3.1 - Session termination | Integration test | Hard |

### Configuration Requirements

```yaml
session:
  id_length: 128  # V3.2.2
  timeout_idle: 30m  # V3.3.2
  timeout_absolute: 8h  # V3.3.4
  secure_flag: true  # V3.4.1
  httponly_flag: true  # V3.4.2
  samesite: strict  # V3.4.3
```

---

## V4: Access Control

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V4.1.1 - Trusted service layer | Architecture review | Gate 2 |
| V4.1.3 - Deny by default | OPA policy | Hard |
| V4.2.1 - Sensitive data protection | SAST | Hard |

### Human Review (Always Required)

| Control | Reason |
|---------|--------|
| V4.1 - Access control design | Business logic |
| V4.2 - Operation level access | Authorization model |
| V4.3 - Administrative access | High privilege |

### OPA Policy

```rego
# policies/opa/security/access.rego
package security.access

# V4.1.3 - Deny by default
default allow = false

allow {
  # Explicit policy must exist
  policy_exists(input.resource, input.action)
  policy_allows(input.resource, input.action, input.subject)
}
```

---

## V5: Validation, Sanitization, Encoding

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V5.1.1 - HTTP parameter pollution | SAST | Hard |
| V5.2.1 - Input sanitization | SAST | Hard |
| V5.3.1 - Output encoding | SAST | Hard |
| V5.5.1 - Deserialization | SAST | Hard |

### SAST Rules

```yaml
# semgrep rules
rules:
  - id: v5.2.1-sql-injection
    patterns:
      - pattern: $DB.query($INPUT)
      - pattern-not: $DB.query($INPUT, $PARAMS)
    message: "V5.2.4: Use parameterized queries"
    severity: ERROR

  - id: v5.3.1-xss
    patterns:
      - pattern: dangerouslySetInnerHTML={{__html: $INPUT}}
    message: "V5.3.3: XSS via dangerouslySetInnerHTML"
    severity: ERROR
```

---

## V6: Cryptography

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V6.2.1 - Approved algorithms | SAST | Hard |
| V6.2.5 - Key rotation | Config check | Soft |
| V6.3.1 - Random values | SAST | Hard |

### Approved Algorithms

| Use Case | Algorithm | Key Size |
|----------|-----------|----------|
| Symmetric encryption | AES-GCM | 256 bits |
| Asymmetric encryption | RSA-OAEP | 2048+ bits |
| Hashing | SHA-256, SHA-3 | - |
| Password hashing | Argon2id | - |
| Signing | Ed25519, ECDSA P-256 | - |

### Prohibited

```rego
# policies/opa/security/crypto.rego
deny[msg] {
  input.algorithm in ["MD5", "SHA1", "DES", "3DES", "RC4"]
  msg := sprintf("V6.2.2: Prohibited algorithm: %v", [input.algorithm])
}
```

---

## V7: Error Handling and Logging

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V7.1.1 - Generic error messages | SAST | Hard |
| V7.2.1 - Log injection | SAST | Hard |
| V7.3.1 - Sensitive data in logs | SAST | Hard |

### Logging Requirements

```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARN|ERROR",
  "message": "Generic message",
  "correlation_id": "uuid",
  "user_id": "hashed_or_masked",
  "action": "action_type",
  "result": "success|failure"
}
```

---

## V8: Data Protection

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V8.1.1 - PII identification | Data classifier | Gate 2 |
| V8.2.1 - Encryption at rest | Config check | Hard |
| V8.3.1 - Encryption in transit | TLS check | Hard |

### Data Classification

See `docs/02-architecture/data-classification.md`.

---

## V9: Communications

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V9.1.1 - TLS required | Config check | Hard |
| V9.1.2 - TLS 1.2+ | SSL Labs scan | Hard |
| V9.2.1 - Certificate validation | SAST | Hard |

### TLS Configuration

```yaml
tls:
  min_version: "1.2"
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_CHACHA20_POLY1305_SHA256
    - TLS_AES_128_GCM_SHA256
  certificate_validation: strict
  hsts:
    enabled: true
    max_age: 31536000
    include_subdomains: true
```

---

## V10: Malicious Code

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V10.1.1 - Time bombs | SAST | Hard |
| V10.2.1 - Malicious dependencies | SCA | Hard |
| V10.3.1 - Auto-updates | Config check | Hard |

---

## V14: Configuration

### Automated Checks

| Control | Tool | Gate |
|---------|------|------|
| V14.1.1 - Server configuration | CIS benchmark | Soft |
| V14.2.1 - Dependency management | SBOM | Hard |
| V14.3.1 - Admin interface | Config check | Hard |

---

## Human Review Triggers

Code automatically requires human security review when:

| Trigger | ASVS Section |
|---------|--------------|
| Auth/authz logic | V2, V4 |
| Cryptographic code | V6 |
| Input validation changes | V5 |
| Session management | V3 |
| Admin interfaces | V14.3 |
| Payment flows | V4 (business logic) |

---

## AppSec Reviewer Agent

The AppSec Reviewer agent (`agents/08-security/appsec-reviewer.md`) performs:

1. ASVS checklist review for relevant sections
2. Code review for high-risk patterns
3. Architecture review for new services
4. Escalation to human for complex issues

---

## Related Documents

- `docs/04-security/security-model.md` — Threat model
- `agents/08-security/appsec-reviewer.md` — Review agent
- `policies/opa/security/` — Security policies

---

**Version**: 2.0.0 | **Date**: 2026-01-06
