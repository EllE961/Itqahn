# Backstage Integration

Backstage is the developer portal that provides service catalog, golden path templates, and documentation hosting for Itqahn.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         BACKSTAGE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Service Catalog │  │   Scaffolder    │  │    TechDocs     │  │
│  │                 │  │                 │  │                 │  │
│  │ • Services      │  │ • Templates     │  │ • This docs     │  │
│  │ • APIs          │  │ • Golden paths  │  │ • Service docs  │  │
│  │ • Dependencies  │  │ • Self-service  │  │ • API specs     │  │
│  │ • Ownership     │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      PLUGINS                                 ││
│  │  Kubernetes | GitHub | PagerDuty | Temporal | Vault         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Catalog

### What It Tracks

| Entity Type | Description |
|-------------|-------------|
| **Component** | Services, websites, libraries |
| **API** | REST, gRPC, GraphQL, events |
| **Resource** | Databases, queues, storage |
| **System** | Group of related components |
| **Domain** | Business domain grouping |

### Catalog Entity Example

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: user-service
  description: User management and authentication
  tags:
    - backend
    - auth
  annotations:
    github.com/project-slug: itqahn/user-service
    pagerduty.com/service-id: P123ABC
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: team:identity
  system: identity-system
  dependsOn:
    - component:auth-service
    - resource:users-database
  providesApis:
    - user-api
```

### Catalog Discovery

Backstage discovers entities from:

| Source | Method |
|--------|--------|
| Git repositories | `catalog-info.yaml` in each repo |
| GitHub org | Automatic component discovery |
| Kubernetes | Runtime discovery |
| Manual | API registration |

---

## Scaffolder (Golden Paths)

### Available Templates

| Template | Description |
|----------|-------------|
| `service` | Backend API/worker with standard structure |
| `webapp` | Frontend application with Design Jail setup |
| `mobile` | Mobile app (iOS/Android/cross-platform) |
| `integration` | Third-party connector module |
| `data-product` | Data pipeline or ML model |
| `infra` | Infrastructure module (Terraform) |
| `docs` | Documentation-only project |

### Template Structure

```yaml
# templates/backstage/service.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: service
  title: Backend Service
  description: Create a new backend service with standard structure
spec:
  owner: team:platform
  type: service

  parameters:
    - title: Service Info
      required:
        - name
        - description
        - owner
      properties:
        name:
          title: Name
          type: string
          pattern: '^[a-z0-9-]+$'
        description:
          title: Description
          type: string
        owner:
          title: Owner
          type: string
          ui:field: OwnerPicker

    - title: Technical Options
      properties:
        language:
          title: Language
          type: string
          enum: [typescript, python, go]
          default: typescript
        database:
          title: Database
          type: string
          enum: [postgres, none]
          default: postgres

  steps:
    - id: fetch
      name: Fetch template
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          description: ${{ parameters.description }}
          owner: ${{ parameters.owner }}

    - id: publish
      name: Create repository
      action: publish:github
      input:
        repoUrl: github.com?owner=itqahn&repo=${{ parameters.name }}
        description: ${{ parameters.description }}

    - id: register
      name: Register in catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml

  output:
    links:
      - title: Repository
        url: ${{ steps.publish.output.remoteUrl }}
      - title: Catalog
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

### Golden Path Benefits

| Benefit | Implementation |
|---------|----------------|
| **Consistency** | All services follow same structure |
| **Security by default** | Security configs included |
| **Observability built-in** | Metrics, logs, traces configured |
| **Documentation** | README, ADR template included |
| **CI/CD ready** | Workflows pre-configured |

---

## TechDocs

### Documentation Sources

| Source | Location |
|--------|----------|
| Platform docs | This docs/ directory |
| Service docs | `docs/` in each service repo |
| API docs | Generated from OpenAPI specs |
| ADRs | `docs/99-appendix/adrs/` |

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: Itqahn Documentation
nav:
  - Overview: 00-overview/index.md
  - Product: 01-product/
  - Architecture: 02-architecture/
  - Platform: 03-platform/
  - Security: 04-security/
  - Compliance: 05-compliance/
  - Operations: 06-operations/
  - Integrations: 07-integrations/
  - Agents: 08-agents/
  - Appendix: 99-appendix/

plugins:
  - techdocs-core
  - search

markdown_extensions:
  - tables
  - admonition
  - codehilite
```

### Documentation Requirements

Every service must have:

| Document | Location |
|----------|----------|
| README | Root of repo |
| API reference | `docs/api.md` or OpenAPI |
| Architecture | `docs/architecture.md` |
| Runbook | `docs/runbook.md` |
| SLOs | `docs/slo.md` |

---

## Backstage Plugins

### Core Plugins

| Plugin | Function |
|--------|----------|
| **Kubernetes** | Pod status, logs, deployments |
| **GitHub** | PRs, issues, actions |
| **PagerDuty** | On-call schedules, incidents |
| **TechDocs** | Documentation hosting |

### Custom Plugins

| Plugin | Function |
|--------|----------|
| **Temporal** | Workflow status, history |
| **Vault** | Secret access audit |
| **Itqahn Evidence** | Evidence Pack viewer |
| **Design System** | Token/component browser |

---

## Entity Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                         DOMAIN                                │
│                    (Business Domain)                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                      SYSTEM                             │  │
│  │              (Group of Components)                      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │  COMPONENT  │  │  COMPONENT  │  │   RESOURCE  │    │  │
│  │  │  (Service)  │  │   (Web)     │  │  (Database) │    │  │
│  │  │             │  │             │  │             │    │  │
│  │  │ providesApi │  │ consumesApi │  │             │    │  │
│  │  │      │      │  │      │      │  │             │    │  │
│  │  └──────┼──────┘  └──────┼──────┘  └─────────────┘    │  │
│  │         │                │                             │  │
│  │         ▼                ▼                             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │                      API                         │  │  │
│  │  │            (REST/gRPC/Events)                   │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Integration with Itqahn Agents

### Catalog Updates

| Agent | Catalog Action |
|-------|----------------|
| **Service Catalog Curator** | Maintain catalog accuracy |
| **API Contract Guardian** | Register/update APIs |
| **Documentation Librarian** | Update TechDocs |

### Scaffolder Triggers

When agents create new components:

1. Agent selects appropriate template
2. Scaffolder creates repository
3. Component registered in catalog
4. CI/CD workflows activated
5. TechDocs build triggered

---

## Search and Discovery

### Search Features

| Feature | Description |
|---------|-------------|
| **Full-text search** | Search across all docs and entities |
| **Entity search** | Find services, APIs, teams |
| **Filters** | By type, owner, lifecycle |
| **Saved searches** | Bookmark common queries |

### Discovery Patterns

| Pattern | Description |
|---------|-------------|
| "Who owns X?" | Find owner from catalog |
| "What depends on X?" | Dependency graph |
| "Is X healthy?" | Kubernetes + PagerDuty status |
| "How do I use X?" | TechDocs link |

---

## Related Documents

- `docs/03-platform/portal-webapp.md` — User portal
- `docs/08-agents/agent-catalog.md` — Agent documentation
- `templates/backstage/` — Scaffolder templates

---

**Version**: 2.0.0 | **Date**: 2026-01-06
