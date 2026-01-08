# Templates (Golden Paths)

Templates are the standard artifacts Itqahn produces and validates.

Use these templates to:
- Keep agents consistent
- Make reviews faster
- Make compliance repeatable
- Reduce drift between intent and implementation

Templates are referenced throughout `docs/` and `agents/`.

---

## Directory Structure

```
templates/
├── product/          # Product documentation
├── governance/       # Decisions and approvals
├── engineering/      # Service artifacts
├── design/           # Design system exports
├── testing/          # Test documentation
├── ops/              # Operations artifacts
├── compliance/       # Compliance templates
├── evidence/         # Evidence pack templates
├── backstage/        # Service catalog scaffolds
├── mcp/              # MCP specifications
├── security/         # Security templates
└── github/           # GitHub templates
```

---

## Template Categories

### Product (`product/`)
- `PRD.md` — Product Requirements Document
- `ACCEPTANCE-CRITERIA.md` — User story criteria
- `ROADMAP.md` — Product roadmap

### Governance (`governance/`)
- `PROJECT-CHARTER.md` — Project initiation
- `ADR.md` — Architecture Decision Record
- `RELEASE-PLAN.md` — Release planning
- `APPROVALS.md` — Approval workflow
- `CHANGELOG.md` — Change log format

### Engineering (`engineering/`)
- `SERVICE-README.md` — Service documentation
- `API-CONTRACT.md` — API specification
- `MIGRATION.md` — Database migration plan

### Design (`design/`)
- `tokens.json` — Design tokens
- `components.json` — Component registry
- `routes.map.json` — Route mappings
- `TOKENS.md` — Token documentation

### Testing (`testing/`)
- `TEST-PLAN.md` — Test strategy
- `E2E-JOURNEYS.md` — E2E test cases
- `VISUAL-REGRESSION.md` — Visual testing

### Operations (`ops/`)
- `SLO.md` — Service Level Objectives
- `RUNBOOK.md` — Operational runbook
- `POSTMORTEM.md` — Incident post-mortem

### Compliance (`compliance/`)
- `COMPLIANCE-TIER.md` — Tier classification
- `DATA-CLASSIFICATION.md` — Data handling
- `RETENTION-POLICY.md` — Data retention

### Evidence (`evidence/`)
- `EVIDENCE-PACK.md` — Evidence pack specification
- `evidence-pack-manifest.schema.json` — Manifest schema

### Backstage (`backstage/`)
- `service-template.yaml` — Service scaffold
- `api-template.yaml` — API scaffold
- `component-template.yaml` — UI component scaffold

### MCP (`mcp/`)
- `MCP-SPEC.md` — MCP specification
- `MCP-ALLOWLIST.yaml` — MCP permissions

### Security (`security/`)
- `SECRETS.md` — Secret handling guide

### GitHub (`github/`)
- `PULL_REQUEST_TEMPLATE.md` — PR template
- `CODEOWNERS` — Code ownership
- `ISSUE_TEMPLATE/` — Issue templates

---

## Related Documents

- `docs/99-appendix/templates-index.md` — Full template reference
- `docs/03-platform/backstage.md` — Backstage integration
- `docs/05-compliance/evidence-pack.md` — Evidence requirements

---

**Version**: 2.0.0 | **Date**: 2026-01-06
