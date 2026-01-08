# Supported Build Types

This document definitively answers: **"What can Itqahn build?"**

---

## Build Type Matrix

| Build Type | Description | Golden Path Template | Risk Tier Default |
|------------|-------------|---------------------|-------------------|
| **Service** | API, worker, scheduler, event processor | `templates/backstage/service.yaml` | Baseline |
| **Web App** | UI + API, portal, dashboard, marketplace | `templates/backstage/webapp.yaml` | Baseline |
| **Mobile App** | iOS, Android, or cross-platform | `templates/backstage/mobile.yaml` | Sensitive |
| **Integration** | Payment, email/SMS, CRM, ERP connector | `templates/backstage/integration.yaml` | Sensitive |
| **Data Product** | Pipeline, warehouse, analytics, ML model | `templates/backstage/data-product.yaml` | Sensitive |
| **Infrastructure** | IaC, GitOps manifests, platform config | `templates/backstage/infra.yaml` | Regulated |
| **Documentation** | ADRs, policies, runbooks, specs | `templates/backstage/docs.yaml` | Baseline |
| **Asset Production** | Icons, illustrations, photos, graphics | `templates/backstage/assets.yaml` | Baseline |

---

## Detailed Build Types

### 1. Service (API/Worker)

**What it includes:**
- REST or gRPC API with OpenAPI/protobuf contracts
- Background workers and schedulers
- Event processors (Kafka, SQS, Pub/Sub consumers)
- Database migrations and schema

**Constraints:**
- Must define API contract before implementation
- Must have health check endpoints
- Must define SLOs before production deploy
- Must follow Design Jail for any admin UI

**Evidence required:**
- API contract validation
- Unit + integration tests (coverage thresholds)
- Security scan (SAST, dependency)
- SBOM + provenance

---

### 2. Web Application

**What it includes:**
- Frontend (React, Vue, or similar)
- Backend-for-frontend (BFF) or direct API calls
- Authentication/authorization integration
- Responsive design

**Constraints:**
- **Design Jail enforced**: Only approved components and tokens
- Must pass accessibility audit (WCAG 2.1 AA)
- Must pass visual regression tests
- No inline styles or arbitrary CSS

**Evidence required:**
- All Service requirements, plus:
- Visual regression baseline
- Accessibility audit results
- Lighthouse performance scores

---

### 3. Mobile Application

**What it includes:**
- iOS (Swift/SwiftUI) or Android (Kotlin/Compose)
- Cross-platform (React Native, Flutter)
- App store metadata and assets
- Push notification integration

**Constraints:**
- Must follow platform design guidelines
- Must handle offline/poor connectivity
- Must implement secure storage for credentials
- App store compliance (content, privacy)

**Evidence required:**
- All Service requirements, plus:
- Platform-specific security review
- Privacy manifest (iOS) / Data safety section (Android)
- App store screenshot validation

---

### 4. Integration Module

**What it includes:**
- Third-party API connectors
- Payment processors (Stripe, Adyen, etc.)
- Communication (Twilio, SendGrid, etc.)
- Business systems (Salesforce, SAP, etc.)

**Constraints:**
- Must use MCP for external access (allowlisted only)
- Must handle rate limits and retries
- Must not store third-party credentials (use Vault)
- Must log all external calls for audit

**Evidence required:**
- All Service requirements, plus:
- MCP allowlist verification
- Integration test with mock/sandbox
- Credential rotation verification

---

### 5. Data Product

**What it includes:**
- ETL/ELT pipelines
- Data warehouses and marts
- Analytics dashboards
- ML model training and serving

**Constraints:**
- Must follow data classification rules
- Must implement data retention policies
- Must handle PII according to tier
- Must have lineage tracking

**Evidence required:**
- All Service requirements, plus:
- Data classification documentation
- Lineage diagram
- Retention policy compliance check
- PII handling verification (if applicable)

---

### 6. Infrastructure Change

**What it includes:**
- Terraform/Pulumi/CloudFormation modules
- Kubernetes manifests and Helm charts
- GitOps configurations (ArgoCD/Flux)
- Platform configurations

**Constraints:**
- **Highest scrutiny**: All changes require human approval
- Must use policy-as-code (OPA/Kyverno)
- Must not create public endpoints without explicit approval
- Must follow least-privilege for IAM

**Evidence required:**
- All Service requirements, plus:
- Policy compliance scan
- Blast radius analysis
- Rollback plan
- Human approval record

---

### 7. Documentation Only

**What it includes:**
- Architecture Decision Records (ADRs)
- Policy documents
- Runbooks and playbooks
- API specifications (without implementation)

**Constraints:**
- Must follow template formats
- Must link to related artifacts
- Must be reviewed by relevant owner

**Evidence required:**
- Template compliance check
- Reviewer approval
- Version tracking

---

### 8. Asset Production

**What it includes:**
- App icons (iOS, Android, web favicons)
- Illustrations (hero images, feature graphics, onboarding)
- Marketing photos (product shots, lifestyle, stock)
- UI graphics (badges, avatars, decorative elements)
- Vector assets (logos, diagrams, charts)

**Constraints:**
- **Design OS enforced**: All assets must comply with Design OS tokens (palette, style)
- Must reference a valid style anchor for drift detection
- Must pass lint checks (palette, contrast, format, dimensions)
- Must be registered in Asset Registry before production use
- Platform-correct outputs required (iOS asset catalog, Android adaptive icons, web variants)
- License verification required (model license, training data)

**Generation workflow:**
1. Asset spec submitted via Portal or PRD
2. Style anchor selected from approved anchors
3. Generation constrained by Design OS palette and style rules
4. Output validated (lint, drift, accessibility)
5. If drift exceeds threshold: repair or regenerate
6. Approved assets registered with provenance
7. Platform-specific variants generated automatically

**Evidence required:**
- Asset manifest with provenance
- Style anchor reference and drift score
- Lint report (palette compliance, format, dimensions)
- License verification
- Approval record

**Canonical artifact locations:**
- Specs: `assets/specs/{asset-id}/asset-spec.json`
- Outputs: `assets/outputs/{asset-id}/`
- Manifests: `assets/manifests/{asset-id}/asset-manifest.json`
- Evidence: `evidence/{workflow-id}/assets/asset-evidence.json`
- Registry: `registry.itqahn.io/{tenant}/{namespace}/{asset-name}:{version}`

See `docs/03-platform/asset-factory-imageops.md` for full specification.

---

## Risk Tiers

Each build type has a default risk tier, but actual risk is determined by:

| Factor | Increases Risk Tier |
|--------|---------------------|
| Handles PII | Baseline → Sensitive |
| Handles payment data | Sensitive → Regulated |
| Handles health data | Sensitive → Regulated |
| Public-facing | +1 tier |
| External integrations | +1 tier |
| Infrastructure changes | Always Regulated |

### Tier Definitions

| Tier | Description | Human Approval |
|------|-------------|----------------|
| **Baseline** | Internal tools, prototypes, non-sensitive data | Standard PR review |
| **Sensitive** | PII, customer data, enterprise auth | Security review required |
| **Regulated** | PCI, HIPAA, FedRAMP, financial data | Security + Compliance review |

See `docs/05-compliance/compliance-tiers.md` for full control mappings.

---

## Hard Boundaries (What Itqahn Will NOT Build)

Itqahn must refuse requests that are:

1. **Illegal**: Anything violating law or facilitating crime
2. **Harmful**: Malware, phishing, exploitation tools
3. **Policy violations**: Against corporate/jurisdictional policy
4. **Ungoverned**: "Deploy without review" or "bypass security gates"

These refusals are enforced by:
- **Domain Policy Filter** agent at intake
- **OPA policies** at execution
- **Human escalation** for ambiguous cases

---

**Version**: 2.1.0 | **Date**: 2026-01-08
