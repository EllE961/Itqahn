# Agent Catalog

This document provides an overview of all Itqahn agents organized by category. Detailed specifications for each agent are in `agents/`.

---

## Overview

Itqahn uses **102 specialized agents** organized into 11 categories, modeling a real enterprise org chart with enforceable boundaries.

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT ORGANIZATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    EXECUTIVE (6)                         │    │
│  │    CEO Orchestrator, Studio Coach, CRO, CPO, CISO, GC   │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                   │
│    ┌─────────────────────────┼─────────────────────────────┐    │
│    │                         │                             │    │
│    ▼                         ▼                             ▼    │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
│ │ Intake │  │ Design │  │  Arch  │  │  Eng   │  │  QA    │    │
│ │  (7)   │  │  (10)  │  │  (11)  │  │  (17)  │  │  (9)   │    │
│ └────────┘  └────────┘  └────────┘  └────────┘  └────────┘    │
│                                                                  │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
│ │Security│  │  SRE   │  │Complnce│  │ FinOps │  │  Meta  │    │
│ │  (15)  │  │  (9)   │  │  (10)  │  │  (5)   │  │  (3)   │    │
│ └────────┘  └────────┘  └────────┘  └────────┘  └────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Category 1: Executive (6 agents)

Command, coordination, and governance.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **CEO Orchestrator** | Chief Executive | Workflow orchestration, hard stops, escalation handling |
| **Studio Coach** | Delivery Lead | Phase transitions, quality gates, team coordination |
| **Chief Risk Officer** | Risk Management | Risk assessment, policy oversight, compliance sign-off |
| **Chief Product Officer** | Product Strategy | Feature prioritization, scope management, roadmap |
| **Chief Information Security Officer** | Security Oversight | Security strategy, incident escalation, threat briefings |
| **General Counsel** | Legal Oversight | Legal review, license compliance, contract approval |

**Location**: `agents/01-executive/`

---

## Category 2: Intake & Clarity (7 agents)

Requirements capture and scope definition.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Requirements Analyst** | Requirements | PRD creation, acceptance criteria, user stories |
| **Scope Guard** | Scope Control | Scope creep detection, change request evaluation |
| **Stakeholder Liaison** | Communication | Stakeholder updates, feedback collection |
| **PRD Author** | Documentation | Product requirements documentation |
| **Acceptance Criteria Writer** | Criteria | Test criteria, validation rules |
| **Question Clarifier** | Ambiguity | Ambiguity detection, clarification requests |
| **Build Type Classifier** | Classification | Project type, risk tier, compliance requirements |

**Location**: `agents/02-intake-and-clarity/`

---

## Category 3: Design Studio (10 agents)

Design system governance and UI composition.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Design System Guardian** | System Governance | Token management, component approval |
| **UI Composer** | Component Assembly | Page composition, layout design |
| **Accessibility Auditor** | A11y | WCAG compliance, screen reader testing |
| **Design Token Manager** | Tokens | Token creation, theming, dark mode |
| **Component Librarian** | Library | Component catalog, documentation |
| **Figma Bridge** | Design Import | Figma sync, design-to-code translation |
| **Visual Regression Tester** | Visual QA | Screenshot comparison, drift detection |
| **Design Reviewer** | Review | Design critique, consistency checks |
| **Responsive Layout Expert** | Responsive | Breakpoint management, mobile design |
| **Motion Designer** | Animation | Animation patterns, transitions |

**Location**: `agents/03-design-studio/`

---

## Category 4: Architecture & Platform (11 agents)

System design and platform engineering.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Solutions Architect** | Architecture | System design, technology selection |
| **API Designer** | API | OpenAPI specs, contract design |
| **Database Architect** | Data | Schema design, query optimization |
| **Platform Engineer** | Platform | Infrastructure automation, CI/CD |
| **Service Mesh Expert** | Networking | Service communication, traffic management |
| **Event Architect** | Events | Event schemas, async patterns |
| **Integration Specialist** | Integration | Third-party integrations, webhooks |
| **Caching Strategist** | Performance | Cache design, invalidation strategies |
| **Search Engineer** | Search | Search indexing, relevance tuning |
| **Data Pipeline Architect** | Data Eng | ETL design, streaming pipelines |
| **ADR Author** | Decisions | Architecture decision records |

**Location**: `agents/04-architecture-and-platform/`

---

## Category 5: Engineering (17 agents)

Code implementation across all layers.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Backend Builder** | Backend | Service implementation, business logic |
| **Frontend Builder** | Frontend | UI implementation, state management |
| **Full-Stack Builder** | Full-Stack | End-to-end feature implementation |
| **API Implementer** | API | Endpoint implementation, validation |
| **Database Developer** | Database | Queries, migrations, stored procedures |
| **Microservices Builder** | Microservices | Service decomposition, inter-service comm |
| **Queue Worker Builder** | Async | Background jobs, message processing |
| **WebSocket Developer** | Real-time | Real-time features, connection management |
| **CLI Builder** | CLI | Command-line tool development |
| **SDK Builder** | SDK | Client library development |
| **Mobile Builder** | Mobile | iOS/Android development |
| **GraphQL Developer** | GraphQL | Schema design, resolver implementation |
| **Batch Processing Engineer** | Batch | Scheduled jobs, bulk operations |
| **Migration Specialist** | Migration | Data migration, schema evolution |
| **Refactoring Agent** | Refactoring | Code cleanup, technical debt |
| **Documentation Writer** | Docs | Code documentation, guides |
| **Code Reviewer** | Review | PR review, best practices |

**Location**: `agents/05-engineering/`

---

## Category 6: Quality Assurance (9 agents)

Testing and quality enforcement.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Test Architect** | Test Strategy | Test strategy, framework selection |
| **Unit Test Writer** | Unit Tests | Unit test implementation |
| **Integration Test Writer** | Integration | Integration test implementation |
| **E2E Test Writer** | E2E | End-to-end test scenarios |
| **Performance Tester** | Performance | Load testing, benchmarking |
| **Contract Tester** | Contracts | API contract testing |
| **Regression Guard** | Regression | Regression detection, flaky tests |
| **Test Data Generator** | Test Data | Fixture creation, data factories |
| **Coverage Analyst** | Coverage | Coverage tracking, gap analysis |

**Location**: `agents/06-quality-assurance/`

---

## Category 7: Security (15 agents)

Security engineering and compliance.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Threat Modeler** | Threat Modeling | STRIDE analysis, attack trees |
| **AppSec Scanner** | SAST/DAST | Security scanning, vulnerability detection |
| **Dependency Auditor** | SCA | Dependency analysis, CVE tracking |
| **Secret Scanner** | Secrets | Secret detection, rotation |
| **Penetration Tester** | Pentesting | Security testing, exploitation |
| **Security Code Reviewer** | Code Review | Security-focused code review |
| **IAM Specialist** | Identity | Authentication, authorization |
| **Encryption Expert** | Crypto | Encryption, key management |
| **Security Gate** | Gating | Security approvals, release blocking |
| **Incident Responder** | IR | Security incident handling |
| **Forensics Analyst** | Forensics | Evidence collection, analysis |
| **Red Team Operator** | Red Team | Adversarial testing |
| **Blue Team Defender** | Blue Team | Detection, defense |
| **Security Trainer** | Training | Security awareness |
| **Compliance Validator** | Validation | Security compliance checks |

**Location**: `agents/07-security/`

---

## Category 8: SRE & Operations (9 agents)

Reliability and operational excellence.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **SRE Lead** | SRE Strategy | Reliability strategy, SLO definition |
| **Incident Commander** | Incidents | Incident coordination, war rooms |
| **Runbook Author** | Runbooks | Operational documentation |
| **Auto-Remediation Bot** | Remediation | Automated incident response |
| **Capacity Planner** | Capacity | Resource forecasting, scaling |
| **On-Call Scheduler** | Scheduling | Rotation management |
| **Post-Mortem Facilitator** | Learning | Incident review, action items |
| **Chaos Engineer** | Chaos | Failure injection, resilience testing |
| **Observability Engineer** | Observability | Monitoring, alerting, dashboards |

**Location**: `agents/09-sre-and-ops/`

---

## Category 9: Compliance & Legal (10 agents)

Regulatory compliance and legal.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Evidence Curator** | Evidence | Evidence pack assembly |
| **Compliance Mapper** | Mapping | Control mapping, framework alignment |
| **Audit Liaison** | Audits | Audit preparation, evidence gathering |
| **License Compliance Officer** | Licensing | Open source license compliance |
| **Data Privacy Officer** | Privacy | GDPR, CCPA compliance |
| **SBOM Generator** | SBOM | Software bill of materials |
| **Provenance Signer** | Provenance | Artifact signing, attestation |
| **Policy Enforcer** | Enforcement | Policy violation detection |
| **Regulatory Analyst** | Regulations | Regulatory requirement analysis |
| **Contract Reviewer** | Contracts | Vendor contract review |

**Location**: `agents/08-compliance-and-legal/`

---

## Category 10: FinOps & Cost Control (5 agents)

Cost management and optimization.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **CFO FinOps** | Cost Governance | Budget oversight, cost policy |
| **Token Budget Enforcer** | Token Costs | AI cost tracking, limits |
| **Cloud Cost Optimizer** | Cloud Costs | Cloud spend optimization |
| **Denial of Wallet Detector** | Anomalies | Cost anomaly detection |
| **Janitor TTL Reaper** | Cleanup | Resource cleanup, TTL enforcement |

**Location**: `agents/11-finops-and-cost-control/`

---

## Category 11: Meta & Evaluation (3 agents)

System improvement and evaluation.

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **Drift Detector** | Drift | Configuration drift detection |
| **Evaluation Harness** | Evaluation | Agent performance evaluation |
| **Model Router** | Routing | Model selection, optimization |

**Location**: `agents/10-meta-and-evaluation/`

---

## Agent Triggers

Agents are invoked by various triggers:

| Trigger Type | Examples | Agents Invoked |
|--------------|----------|----------------|
| **Workflow stage** | Phase transition | Studio Coach, relevant builders |
| **Repo events** | PR opened, CI failed | Code Reviewer, Test Writers |
| **Policy failures** | OPA denial | Policy Enforcer, Security Gate |
| **Budget alerts** | Threshold reached | CFO FinOps, Token Budget Enforcer |
| **Incidents** | Alert fired | Incident Commander, Auto-Remediation |
| **Schedule** | Cron jobs | Janitor TTL Reaper, Drift Detector |

---

## Agent Invocation

### Direct Invocation

```yaml
# Example: Invoke Backend Builder
invocation:
  agent: backend-builder
  task:
    type: implement_feature
    spec:
      feature_id: "feat-123"
      requirements: "requirements/auth.md"
      constraints:
        - no_raw_sql
        - use_orm
```

### Workflow Invocation

```yaml
# Example: Phase triggers multiple agents
workflow:
  phase: experience
  stages:
    - stage: implementation
      agents:
        - backend-builder
        - frontend-builder
        - api-implementer
      parallel: true

    - stage: testing
      agents:
        - unit-test-writer
        - integration-test-writer
      parallel: true
```

---

## Agent Communication

### Inter-Agent Protocol

```json
{
  "from": "backend-builder",
  "to": "code-reviewer",
  "type": "review_request",
  "payload": {
    "pr_url": "https://github.com/org/repo/pull/123",
    "files_changed": ["src/auth.ts", "src/middleware/jwt.ts"],
    "context": {
      "workflow_id": "wf-xyz789",
      "feature_id": "feat-123"
    }
  }
}
```

### Escalation Protocol

```json
{
  "from": "backend-builder",
  "to": "studio-coach",
  "type": "escalation",
  "payload": {
    "reason": "Ambiguous requirement",
    "context": {
      "requirement": "Make authentication more secure",
      "question": "Which auth method? OAuth, SAML, or passwordless?"
    }
  }
}
```

---

## Related Documents

- `docs/08-agents/agent-system-contract.md` — Contract rules
- `docs/08-agents/agent-permissions.md` — Permission model
- `docs/08-agents/agent-quality-bar.md` — Quality standards
- `agents/` — Individual agent specifications

---

**Version**: 2.0.0 | **Date**: 2026-01-06
