# Templates Index

Templates are Golden Path artifacts that Itqahn produces and validates. They ensure consistency, speed reviews, enable repeatable compliance, and reduce drift between intent and implementation.

---

## Overview

```
templates/
├── product/          # Product requirements
├── governance/       # Decisions and approvals
├── engineering/      # Service artifacts
├── design/           # Design system exports
├── testing/          # Test documentation
├── ops/              # Operations artifacts
├── evidence/         # Compliance evidence
├── backstage/        # Service catalog scaffolds
├── mcp/              # MCP specifications
└── github/           # GitHub templates
```

---

## Product Templates

**Location**: `templates/product/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `PRD.md` | Product Requirements Document | Requirements Analyst, PRD Author |
| `ACCEPTANCE-CRITERIA.md` | User story acceptance criteria | Acceptance Criteria Writer |
| `ROADMAP.md` | Product roadmap format | Chief Product Officer |
| `FEATURE-BRIEF.md` | Feature specification | Product Team |
| `USER-STORY.md` | User story format | Requirements Analyst |

### PRD Template Summary

```markdown
# PRD: [Feature Name]

## Overview
[One-paragraph summary]

## Problem Statement
[What problem does this solve?]

## Goals
- [Goal 1]
- [Goal 2]

## Non-Goals
- [Non-goal 1]

## User Stories
| As a... | I want to... | So that... |

## Requirements
### Functional
### Non-Functional

## Success Metrics
| Metric | Target | Measurement |

## Timeline
## Dependencies
## Risks
```

---

## Governance Templates

**Location**: `templates/governance/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `ADR.md` | Architecture Decision Record | Solutions Architect, ADR Author |
| `PROJECT-CHARTER.md` | Project initiation document | Studio Coach |
| `APPROVAL-REQUEST.md` | Approval request form | All agents requiring approval |
| `RELEASE-PLAN.md` | Release planning document | Release Manager |
| `CHANGE-REQUEST.md` | Change request form | Change Advisory Board |

### ADR Template Summary

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[Why is this decision needed?]

## Decision
[What did we decide?]

## Consequences
### Positive
### Negative
### Risks

## Alternatives Considered
| Alternative | Reason Rejected |
```

---

## Engineering Templates

**Location**: `templates/engineering/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `SERVICE-README.md` | Service documentation | Backend Builder, Frontend Builder |
| `API-CONTRACT.yaml` | OpenAPI specification template | API Designer |
| `MIGRATION.md` | Database migration plan | Database Architect |
| `RUNBOOK-LINK.md` | Service runbook reference | SRE Team |
| `DEPENDENCY-RATIONALE.md` | Dependency justification | Engineering Team |

### Service README Template Summary

```markdown
# [Service Name]

## Overview
[What does this service do?]

## Architecture
[Architecture diagram or description]

## API
[API reference or link]

## Dependencies
| Dependency | Version | Purpose |

## Configuration
| Variable | Description | Default |

## Development
### Local Setup
### Testing
### Deployment

## Operations
### Monitoring
### Runbooks
### Contacts
```

---

## Design Templates

**Location**: `templates/design/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `tokens.json` | Design token schema | Design Token Manager |
| `components.json` | Component registry schema | Component Librarian |
| `routes.map.json` | Route-to-layout mapping | UI Composer |
| `DESIGN-JAIL-CHECKLIST.md` | UI compliance checklist | Design System Guardian |
| `VISUAL-REGRESSION.md` | Visual test documentation | Visual Regression Tester |

### Design Token Schema

```json
{
  "colors": {
    "primary": {"value": "#0066FF", "type": "color"},
    "secondary": {"value": "#6B7280", "type": "color"}
  },
  "typography": {
    "heading-1": {
      "value": {
        "fontFamily": "Inter",
        "fontSize": 32,
        "fontWeight": 700
      },
      "type": "typography"
    }
  },
  "spacing": {
    "sm": {"value": 8, "type": "spacing"},
    "md": {"value": 16, "type": "spacing"}
  }
}
```

---

## Testing Templates

**Location**: `templates/testing/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `TEST-PLAN.md` | Test strategy document | Test Architect |
| `TEST-JOURNEY.md` | User journey test case | E2E Test Writer |
| `CONTRACT-TEST.md` | API contract test spec | Contract Tester |
| `PERFORMANCE-TEST.md` | Performance test plan | Performance Tester |
| `TEST-DATA-SPEC.md` | Test data requirements | Test Data Generator |

### Test Plan Template Summary

```markdown
# Test Plan: [Feature/Service]

## Scope
### In Scope
### Out of Scope

## Test Strategy
### Unit Tests
### Integration Tests
### E2E Tests
### Performance Tests

## Test Environment
## Test Data Requirements
## Success Criteria
## Schedule
## Risks
```

---

## Operations Templates

**Location**: `templates/ops/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `SLO.yaml` | Service Level Objective | SRE Lead |
| `RUNBOOK.md` | Operational runbook | Runbook Author |
| `POSTMORTEM.md` | Incident post-mortem | Post-Mortem Facilitator |
| `ALERT.yaml` | Alert definition | Observability Engineer |
| `CAPACITY-PLAN.md` | Capacity planning | Capacity Planner |

### SLO Template

```yaml
service: user-service
slos:
  - name: availability
    description: "Service returns successful responses"
    target: 0.999
    window: 30d
    sli:
      type: availability
      good: http_requests_total{status!~"5.."}
      total: http_requests_total

  - name: latency
    description: "P99 latency under 500ms"
    target: 0.99
    window: 30d
    sli:
      type: latency
      threshold_ms: 500
```

### Runbook Template Summary

```markdown
# Runbook: [Service] - [Issue Type]

## Purpose and Scope
## Detection Signals
## Prerequisites
## Severity Assessment
## Safe Mitigation Steps
### Step 1: Verify
### Step 2: Mitigate
### Step 3: Rollback (if needed)
## Escalation Criteria
## Verification Steps
## Post-Resolution
```

---

## Evidence Templates

**Location**: `templates/evidence/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `EVIDENCE-PACK.md` | Evidence pack contents | Evidence Curator |
| `evidence-pack-manifest.schema.json` | Manifest schema | SBOM Generator |
| `DATA-CLASSIFICATION.md` | Data classification form | Data Privacy Officer |
| `RETENTION-POLICY.md` | Data retention document | Compliance Mapper |

### Evidence Pack Manifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "service", "build", "artifacts"],
  "properties": {
    "version": {"type": "string"},
    "service": {"type": "string"},
    "build": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "commit": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"}
      }
    },
    "artifacts": {
      "type": "object",
      "properties": {
        "sbom": {"type": "string"},
        "provenance": {"type": "string"},
        "scans": {"type": "array", "items": {"type": "string"}},
        "tests": {"type": "string"}
      }
    }
  }
}
```

---

## Backstage Templates

**Location**: `templates/backstage/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `service-template.yaml` | New service scaffold | Platform Engineer |
| `component-template.yaml` | UI component scaffold | Frontend Builder |
| `api-template.yaml` | API service scaffold | API Designer |

### Service Template (Backstage Scaffolder)

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: itqahn-service
  title: Itqahn Service
  description: Create a new Itqahn-compliant service
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service Information
      required: [name, description, owner]
      properties:
        name:
          title: Service Name
          type: string
        description:
          title: Description
          type: string
        owner:
          title: Owner Team
          type: string
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
    - id: publish
      action: publish:github
    - id: register
      action: catalog:register
```

---

## MCP Templates

**Location**: `templates/mcp/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `MCP-SPEC.md` | MCP specification template | Platform Engineer |
| `MCP-ALLOWLIST.yaml` | MCP allowlist configuration | Security Team |

---

## GitHub Templates

**Location**: `templates/github/`

| Template | Purpose | Used By |
|----------|---------|---------|
| `PULL_REQUEST_TEMPLATE.md` | PR description template | All developers |
| `CODEOWNERS` | Code ownership definition | Platform Team |
| `ISSUE_TEMPLATE/bug.md` | Bug report template | All users |
| `ISSUE_TEMPLATE/feature.md` | Feature request template | All users |

### PR Template Summary

```markdown
## Summary
<!-- Brief description -->

## Related
- Issue: #
- PRD:

## Changes
- [ ] Change 1

## Testing
- [ ] Unit tests
- [ ] Integration tests

## Security Checklist
- [ ] No secrets in code
- [ ] Input validation

## Evidence
<!-- CI adds evidence summary -->
```

---

## Using Templates

### Template Discovery

```bash
# List all templates
ls -la templates/

# Find specific template
find templates/ -name "*.md" | grep -i "prd"
```

### Template Validation

Templates are validated during CI:
- Markdown linting
- Schema validation for JSON/YAML
- Required sections check

### Template Updates

1. Propose change via PR to `templates/`
2. Review by template owner
3. Update documentation if schema changes
4. Notify dependent agents

---

## Related Documents

- `docs/08-agents/agent-catalog.md` — Agents using templates
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/03-platform/backstage.md` — Service catalog

---

**Version**: 2.0.0 | **Date**: 2026-01-06
