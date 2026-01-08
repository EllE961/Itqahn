# Secure SDLC (NIST SSDF Mapping)

Itqahn implements a Secure Software Development Framework aligned with NIST SSDF (SP 800-218).

---

## SSDF Overview

The NIST Secure Software Development Framework defines practices across four groups:

| Group | Code | Description |
|-------|------|-------------|
| Prepare the Organization | PO | Security readiness |
| Protect the Software | PS | Protect code and artifacts |
| Produce Well-Secured Software | PW | Secure development practices |
| Respond to Vulnerabilities | RV | Vulnerability management |

---

## PO: Prepare the Organization

### PO.1: Security Requirements

| Practice | Itqahn Implementation |
|----------|----------------------|
| PO.1.1 - Identify security requirements | PRD template includes security NFRs |
| PO.1.2 - Identify third-party requirements | MCP allowlist, dependency policies |
| PO.1.3 - Update requirements | Continuous policy updates |

**Evidence**:
- `templates/product/PRD.md` (security section)
- `policies/opa/security/`
- `docs/05-compliance/compliance-tiers.md`

### PO.2: Roles and Responsibilities

| Practice | Itqahn Implementation |
|----------|----------------------|
| PO.2.1 - Define security roles | Agent roles with security responsibilities |
| PO.2.2 - Provide training | Agent prompts include security guidance |
| PO.2.3 - Continuous improvement | Red team feedback, postmortem learnings |

**Evidence**:
- `agents/08-security/` (all security agents)
- `agents/AGENT-CONTRACT.md` (security clauses)

### PO.3: Automation

| Practice | Itqahn Implementation |
|----------|----------------------|
| PO.3.1 - Automate security checks | CI/CD pipeline gates |
| PO.3.2 - Define criteria | Hard gates vs soft gates |
| PO.3.3 - Make tools available | Integrated tooling |

**Evidence**:
- `docs/03-platform/ci-cd-gitops.md`
- `policies/policy-catalog.md`

---

## PS: Protect the Software

### PS.1: Protect Code

| Practice | Itqahn Implementation |
|----------|----------------------|
| PS.1.1 - Store code securely | Git with branch protection |
| PS.1.2 - Protect development tools | Secured CI/CD, least privilege |

**Evidence**:
- `docs/07-integrations/git-integration.md`
- GitHub/GitLab security settings

### PS.2: Verify Integrity

| Practice | Itqahn Implementation |
|----------|----------------------|
| PS.2.1 - Verify third-party components | SBOM, dependency scanning |
| PS.2.2 - Archive and protect artifacts | Evidence Store, signed artifacts |
| PS.2.3 - Review and maintain provenance | SLSA L3, attestations |

**Evidence**:
- `docs/05-compliance/slsa-provenance.md`
- `docs/05-compliance/sbom-vex.md`
- `tools/validators/sbom_validator.py`

### PS.3: Archive and Protect

| Practice | Itqahn Implementation |
|----------|----------------------|
| PS.3.1 - Protect build processes | Hermetic builds, isolated runners |
| PS.3.2 - Archive release artifacts | Evidence Pack storage |

**Evidence**:
- `docs/05-compliance/evidence-pack.md`
- `docs/03-platform/ci-cd-gitops.md`

---

## PW: Produce Well-Secured Software

### PW.1: Design Software Securely

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.1.1 - Use secure design principles | Threat modeling required |
| PW.1.2 - Document security decisions | ADRs for security decisions |
| PW.1.3 - Evaluate third-party components | MCP allowlist, dependency review |

**Evidence**:
- `agents/08-security/threat-modeler.md`
- `docs/01-product/adr-policy.md`
- `templates/mcp/MCP-ALLOWLIST.yaml`

### PW.2: Review the Design

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.2.1 - Review design for security | Security agent review at Gate 2 |
| PW.2.2 - Use threat modeling | Threat Modeler agent |

**Evidence**:
- `docs/01-product/lifecycle-phase-gates.md` (Gate 2)
- `templates/security/THREAT-MODEL.md`

### PW.4: Review Code

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.4.1 - Review code for vulnerabilities | SAST, AppSec Reviewer agent |
| PW.4.2 - Human review for high-risk | CODEOWNERS, security review triggers |
| PW.4.4 - Verify code provenance | Signed commits, Git integration |

**Evidence**:
- `agents/08-security/appsec-reviewer.md`
- `docs/04-security/appsec-asvs.md`

### PW.5: Test Code

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.5.1 - Test for vulnerabilities | SAST, DAST, fuzzing |
| PW.5.2 - Test security requirements | Security tests in Evidence Pack |

**Evidence**:
- `docs/05-compliance/evidence-pack.md`
- `agents/07-quality-and-testing/fuzz-tester.md`

### PW.6: Build Securely

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.6.1 - Use hardened build environments | Hermetic builds |
| PW.6.2 - Verify build outputs | SLSA provenance |

**Evidence**:
- `docs/05-compliance/slsa-provenance.md`
- `docs/03-platform/ci-cd-gitops.md`

### PW.7: Deploy Securely

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.7.1 - Configure environments securely | GitOps, policy enforcement |
| PW.7.2 - Ensure artifact integrity | Signature verification at deploy |

**Evidence**:
- `policies/kyverno/`
- `docs/03-platform/ci-cd-gitops.md`

### PW.8: Support Vulnerability Disclosure

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.8.1 - Receive vulnerability reports | security-disclosure-policy.md |
| PW.8.2 - Process reports | Incident response workflow |

**Evidence**:
- `legal/security-disclosure-policy.md`
- `docs/06-operations/incident-response.md`

### PW.9: Archive Software

| Practice | Itqahn Implementation |
|----------|----------------------|
| PW.9.1 - Archive release artifacts | Evidence Pack storage |
| PW.9.2 - Maintain artifact traceability | Provenance attestations |

**Evidence**:
- `docs/05-compliance/evidence-pack.md`
- `docs/05-compliance/slsa-provenance.md`

---

## RV: Respond to Vulnerabilities

### RV.1: Identify Vulnerabilities

| Practice | Itqahn Implementation |
|----------|----------------------|
| RV.1.1 - Monitor vulnerability sources | Dependency Sentinel agent |
| RV.1.2 - Gather vulnerability information | SBOM + vulnerability feeds |
| RV.1.3 - Track known vulnerabilities | VEX statements |

**Evidence**:
- `agents/08-security/dependency-sentinel.md`
- `docs/05-compliance/sbom-vex.md`

### RV.2: Assess Vulnerabilities

| Practice | Itqahn Implementation |
|----------|----------------------|
| RV.2.1 - Evaluate vulnerability severity | CVE scoring, context analysis |
| RV.2.2 - Determine exposure | Impact analysis, blast radius |

**Evidence**:
- `docs/06-operations/incident-response.md`
- VEX integration

### RV.3: Remediate Vulnerabilities

| Practice | Itqahn Implementation |
|----------|----------------------|
| RV.3.1 - Remediate vulnerabilities | Automated PRs, patches |
| RV.3.2 - Notify stakeholders | Incident communication |
| RV.3.3 - Prevent recurrence | Postmortem, policy updates |

**Evidence**:
- `docs/06-operations/incident-response.md`
- `templates/ops/POSTMORTEM.md`

---

## Compliance Mapping

| SSDF Practice | Itqahn Document |
|---------------|-----------------|
| PO.1 | `docs/01-product/requirements-schema.md` |
| PO.2 | `agents/08-security/` |
| PO.3 | `docs/03-platform/ci-cd-gitops.md` |
| PS.1 | `docs/07-integrations/git-integration.md` |
| PS.2 | `docs/05-compliance/slsa-provenance.md` |
| PS.3 | `docs/05-compliance/evidence-pack.md` |
| PW.1 | `agents/08-security/threat-modeler.md` |
| PW.4 | `docs/04-security/appsec-asvs.md` |
| PW.5 | `agents/07-quality-and-testing/` |
| PW.6 | `docs/05-compliance/slsa-provenance.md` |
| PW.7 | `docs/03-platform/ci-cd-gitops.md` |
| RV.* | `docs/06-operations/incident-response.md` |

---

**Version**: 2.0.0 | **Date**: 2026-01-06
