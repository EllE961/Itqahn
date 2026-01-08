# Legacy Project Rebuild

> **Version:** 1.0.0
> **Status:** Normative
> **Last Updated:** 2026-01-08

## Overview

Legacy Project Rebuild enables Itqahn to import existing, messy, or half-done repositories and systematically modernize them into well-structured, compliant projects. This specification defines the complete lifecycle from import through cutover, including automatic discovery, rebuild strategies, and parity verification.

This specification defines:
- Entry points and import methods
- Automatic discovery and analysis
- Rebuild strategies (Strangler-style vs Clean Rebuild)
- Git mechanics and branch conventions
- Parity and cutover verification
- Evidence Pack requirements
- Edge cases and failure recovery

---

## 1. Entry Points

### 1.1 Import Existing Project Wizard

The primary entry point is the **Import Existing Project** wizard in the Portal webapp:

**Dashboard Path:** `Projects > New Project > Import Existing`

**Wizard Steps:**

1. **Source Selection**
   - Git repository URL (HTTPS or SSH)
   - ZIP/archive upload
   - Monorepo subdirectory selection

2. **Authentication** (if required)
   - GitHub/GitLab OAuth connection
   - Deploy key configuration
   - Personal access token

3. **Analysis Preview**
   - Quick scan results (languages, frameworks, size)
   - Estimated analysis duration
   - Resource requirements

4. **Import Configuration**
   - Target project name
   - Compliance tier assignment
   - Rebuild strategy preference (auto-detect or explicit)

5. **Confirmation**
   - Import summary
   - Terms acknowledgment (for license scanning)

### 1.2 Git Repository URL Import

Direct URL import supports:

| Provider | URL Format | Auth Method |
|----------|------------|-------------|
| GitHub | `https://github.com/org/repo.git` | OAuth, PAT, Deploy Key |
| GitLab | `https://gitlab.com/org/repo.git` | OAuth, PAT, Deploy Key |
| Bitbucket | `https://bitbucket.org/org/repo.git` | App Password, SSH |
| Azure DevOps | `https://dev.azure.com/org/project/_git/repo` | PAT |
| Self-hosted | `https://git.example.com/repo.git` | PAT, SSH |

**Branch Selection:**
- Default branch is auto-detected
- Operator MAY specify alternate branch for import
- All branches are cloned; specified branch becomes `legacy-main`

### 1.3 ZIP/Archive Upload

For repositories not accessible via Git:

**Supported Formats:**
- `.zip`
- `.tar.gz`
- `.tar.bz2`

**Size Limits:**
- Maximum archive size: 2 GB
- Maximum extracted size: 10 GB
- Maximum file count: 100,000

**Process:**
1. Archive uploaded to secure staging
2. Integrity verification (checksum)
3. Extraction to temporary workspace
4. Git repository initialized from contents
5. Initial commit created with `legacy-snapshot` tag

### 1.4 Monorepo Subdirectory Selection

For monorepo imports:

```
┌─────────────────────────────────────────────────────────┐
│  SELECT SUBDIRECTORY                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Repository: github.com/acme/monorepo                   │
│                                                         │
│  ○ Import entire repository                            │
│  ● Import subdirectory:                                │
│                                                         │
│    📁 packages/                                         │
│       📁 frontend/     [Select]                        │
│       📁 backend/      [Select]                        │
│       📁 shared/       [Select]                        │
│    📁 services/                                         │
│       📁 auth-service/ [Select]                        │
│       📁 api-gateway/  [Select]                        │
│                                                         │
│  Selected: packages/frontend                            │
│                                                         │
│  ☑ Include shared dependencies (auto-detected)         │
│  ☐ Include root configuration files                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Automatic Discovery

### 2.1 Discovery Pipeline

Upon import, the Discovery Pipeline analyzes the codebase:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Ingest  │───▶│ Analyze │───▶│ Catalog │───▶│ Report  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
  Clone/       Language,      Build         Discovery
  Extract      Framework,     Manifest,     Report
               Structure      Dep Graph     Artifact
```

### 2.2 Discovery Outputs

All discovery outputs are stored as artifacts in `.itqahn/legacy-discovery/`:

#### 2.2.1 Language Analysis

```json
{
  "languages": [
    {
      "name": "TypeScript",
      "version_detected": "5.0",
      "file_count": 245,
      "line_count": 48000,
      "percentage": 65.2
    },
    {
      "name": "JavaScript",
      "version_detected": "ES2022",
      "file_count": 52,
      "line_count": 8400,
      "percentage": 11.4
    },
    {
      "name": "Python",
      "version_detected": "3.11",
      "file_count": 38,
      "line_count": 6200,
      "percentage": 8.4
    }
  ]
}
```

#### 2.2.2 Framework Detection

```json
{
  "frameworks": [
    {
      "name": "React",
      "version": "18.2.0",
      "confidence": 0.98,
      "evidence": ["package.json", "jsx files", "react-dom import"]
    },
    {
      "name": "Express",
      "version": "4.18.2",
      "confidence": 0.95,
      "evidence": ["package.json", "app.listen pattern"]
    },
    {
      "name": "Django",
      "version": "4.2",
      "confidence": 0.92,
      "evidence": ["requirements.txt", "settings.py", "urls.py"]
    }
  ]
}
```

#### 2.2.3 Dependency Graph

```json
{
  "dependencies": {
    "production": {
      "total": 142,
      "direct": 38,
      "transitive": 104
    },
    "development": {
      "total": 86,
      "direct": 24,
      "transitive": 62
    }
  },
  "vulnerability_summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 8
  },
  "outdated_summary": {
    "major_behind": 8,
    "minor_behind": 23,
    "patch_behind": 45
  }
}
```

#### 2.2.4 Code Structure Analysis

```json
{
  "structure": {
    "architecture_pattern": "monolith",
    "module_count": 12,
    "circular_dependencies": 3,
    "dead_code_files": 8,
    "test_coverage_estimated": 0.42
  },
  "concerns": [
    {
      "type": "circular_dependency",
      "location": "src/auth <-> src/users",
      "severity": "medium"
    },
    {
      "type": "dead_code",
      "location": "src/legacy/",
      "severity": "low"
    }
  ]
}
```

#### 2.2.5 Configuration Detection

```json
{
  "build_system": {
    "tool": "webpack",
    "config_files": ["webpack.config.js", "webpack.prod.js"],
    "npm_scripts": ["build", "dev", "test"]
  },
  "ci_cd": {
    "detected": "GitHub Actions",
    "config_files": [".github/workflows/ci.yml"],
    "status": "partially_configured"
  },
  "environment": {
    "env_files": [".env.example", ".env.local"],
    "required_vars": ["DATABASE_URL", "API_KEY", "JWT_SECRET"],
    "secrets_detected": false
  }
}
```

#### 2.2.6 Security Scan Summary

```json
{
  "security": {
    "sast_findings": {
      "critical": 1,
      "high": 3,
      "medium": 8,
      "low": 15
    },
    "secrets_detected": [
      {
        "type": "aws_access_key",
        "file": "config/aws.js",
        "line": 12,
        "status": "likely_placeholder"
      }
    ],
    "license_compliance": {
      "compatible": 134,
      "review_required": 6,
      "incompatible": 2
    }
  }
}
```

### 2.3 Discovery Report

The complete discovery report is generated at `.itqahn/legacy-discovery/report.md`:

```markdown
# Legacy Discovery Report

**Project:** acme-legacy-app
**Imported:** 2026-01-08T10:30:00Z
**Source:** github.com/acme/legacy-app

## Executive Summary

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Files | 892 | Medium complexity |
| Lines of Code | 73,600 | Significant codebase |
| Languages | 3 | Multi-language |
| Frameworks | 4 | Modern stack |
| Security Issues | 27 | Requires attention |
| Test Coverage | ~42% | Below target |

## Recommended Strategy

Based on analysis: **Strangler-Style Modernization**

Rationale:
- Working production deployment exists
- Core business logic is sound
- Infrastructure and tooling need updates
- Incremental migration reduces risk

## Action Items

1. [ ] Address 2 critical security vulnerabilities
2. [ ] Update 8 major-version-behind dependencies
3. [ ] Resolve 3 circular dependencies
4. [ ] Remove 8 dead code files
5. [ ] Add tests to reach 80% coverage target
```

---

## 3. Rebuild Strategies

### 3.1 Strategy Selection

Itqahn supports two primary rebuild strategies:

| Factor | Strangler-Style | Clean Rebuild |
|--------|-----------------|---------------|
| **Production deployment** | Exists and working | None or broken |
| **Code quality** | Salvageable core | Fundamentally broken |
| **Business logic** | Documented in code | Lost/undocumented |
| **Timeline pressure** | Gradual OK | Urgent replacement |
| **Risk tolerance** | Conservative | Aggressive |

**Auto-Detection Logic:**

```python
def recommend_strategy(discovery):
    if discovery.build_success and discovery.tests_pass > 0.3:
        if discovery.security_critical == 0:
            return "strangler"
    if discovery.code_quality_score < 0.3:
        return "clean_rebuild"
    if discovery.documentation_score > 0.6:
        return "clean_rebuild"  # Spec exists, can rebuild from scratch
    return "strangler"  # Default to safer option
```

### 3.2 Strangler-Style Modernization

The Strangler pattern incrementally replaces legacy components while maintaining a working system.

#### 3.2.1 Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    STRANGLER WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. FACADE CREATION                                         │
│     ┌─────────────────┐                                     │
│     │  Legacy System  │◄──── Existing Traffic               │
│     └─────────────────┘                                     │
│              │                                               │
│              ▼                                               │
│     ┌─────────────────┐                                     │
│     │    Facade       │◄──── Route Traffic Here             │
│     └─────────────────┘                                     │
│                                                              │
│  2. COMPONENT MIGRATION                                     │
│     ┌─────────────────┐      ┌─────────────────┐           │
│     │    Facade       │─────▶│  New Component  │           │
│     └─────────────────┘      └─────────────────┘           │
│              │                                               │
│              ▼                                               │
│     ┌─────────────────┐                                     │
│     │  Legacy System  │ (gradually shrinks)                 │
│     └─────────────────┘                                     │
│                                                              │
│  3. CUTOVER                                                  │
│     ┌─────────────────┐                                     │
│     │  New System     │◄──── All Traffic                    │
│     └─────────────────┘                                     │
│              │                                               │
│              ▼                                               │
│     ┌─────────────────┐                                     │
│     │  Legacy Archive │ (preserved for reference)           │
│     └─────────────────┘                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Migration Order

Itqahn determines component migration order based on:

1. **Dependency depth** - Leaf nodes first
2. **Risk score** - Lower risk components first
3. **Business value** - High-value components prioritized
4. **Test coverage** - Well-tested components easier to verify

```json
{
  "migration_order": [
    {
      "component": "utils/date-helpers",
      "priority": 1,
      "rationale": "Leaf node, no dependencies, well-tested"
    },
    {
      "component": "services/email",
      "priority": 2,
      "rationale": "Single dependency, isolated functionality"
    },
    {
      "component": "api/users",
      "priority": 3,
      "rationale": "Core business logic, high test coverage"
    },
    {
      "component": "auth/login",
      "priority": 4,
      "rationale": "Security-sensitive, requires careful migration"
    }
  ]
}
```

### 3.3 Clean Rebuild

Complete rebuild from specification, using legacy code as reference only.

#### 3.3.1 Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CLEAN REBUILD WORKFLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SPECIFICATION EXTRACTION                                │
│     ┌─────────────────┐      ┌─────────────────┐           │
│     │  Legacy Code    │─────▶│  Derived Spec   │           │
│     └─────────────────┘      └─────────────────┘           │
│                                                              │
│  2. CONCEPT LOCK CREATION                                   │
│     ┌─────────────────┐      ┌─────────────────┐           │
│     │  Derived Spec   │─────▶│  Concept Lock   │           │
│     │  + Operator     │      │  (Approved)     │           │
│     │    Refinement   │      └─────────────────┘           │
│     └─────────────────┘                                     │
│                                                              │
│  3. GREENFIELD BUILD                                        │
│     ┌─────────────────┐      ┌─────────────────┐           │
│     │  Concept Lock   │─────▶│  New Codebase   │           │
│     └─────────────────┘      └─────────────────┘           │
│                                                              │
│  4. PARITY VERIFICATION                                     │
│     ┌─────────────────┐      ┌─────────────────┐           │
│     │  Legacy System  │◄────▶│  New System     │           │
│     └─────────────────┘      └─────────────────┘           │
│              │                       │                      │
│              └───────────┬───────────┘                      │
│                          ▼                                   │
│                 ┌─────────────────┐                         │
│                 │  Parity Report  │                         │
│                 └─────────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3.2 Specification Extraction

Itqahn extracts specifications from legacy code:

1. **API Contract Extraction**
   - OpenAPI/Swagger generation from routes
   - GraphQL schema extraction
   - Request/response examples from tests

2. **Data Model Extraction**
   - Database schema from migrations/ORM
   - Entity relationships
   - Validation rules

3. **Business Logic Extraction**
   - Function signatures and documentation
   - Test cases as behavior specification
   - Error handling patterns

4. **UI Extraction**
   - Component hierarchy
   - State management patterns
   - User flows from integration tests

---

## 4. Git Mechanics

### 4.1 Branch Conventions

Legacy rebuild uses specific branch naming:

| Branch Pattern | Purpose |
|----------------|---------|
| `legacy-snapshot` | Tag marking original import state |
| `legacy-main` | Preserved copy of original main branch |
| `rebuild/main` | Primary rebuild development branch |
| `rebuild/strangler/{component}` | Per-component migration branches |
| `rebuild/clean/{module}` | Clean rebuild module branches |
| `rebuild/parity-tests` | Parity verification test suite |

### 4.2 Legacy Snapshot Tag

On import, Itqahn creates an immutable snapshot:

```bash
# Automatically created on import
git tag -a legacy-snapshot \
  -m "Legacy snapshot at import

Imported: 2026-01-08T10:30:00Z
Source: github.com/acme/legacy-app
Commit: abc123...
Discovery Report: .itqahn/legacy-discovery/report.md"
```

**Snapshot Contents:**
- Full repository state at import
- Discovery artifacts
- Initial security scan results

### 4.3 Rebuild Branch Workflow

```
legacy-main (preserved)
    │
    └── legacy-snapshot (tag)

main
    │
    ├── rebuild/main
    │       │
    │       ├── rebuild/strangler/utils
    │       │       └── PR → rebuild/main
    │       │
    │       ├── rebuild/strangler/auth
    │       │       └── PR → rebuild/main
    │       │
    │       └── rebuild/parity-tests
    │               └── PR → rebuild/main
    │
    └── PR: rebuild/main → main (cutover)
```

### 4.4 Pull Request Workflow

#### 4.4.1 Component Migration PR

```markdown
## [Rebuild] Migrate utils/date-helpers

### Migration Summary
- **Strategy:** Strangler-style
- **Component:** utils/date-helpers
- **Legacy Location:** src/utils/date.js
- **New Location:** src/utils/date-helpers.ts

### Changes
- Converted to TypeScript
- Added comprehensive type definitions
- Updated to use date-fns instead of moment.js
- Added unit tests (coverage: 98%)

### Parity Verification
- [x] All legacy tests pass
- [x] Parity harness comparison: PASS
- [x] No behavioral differences detected

### Evidence
- Legacy comparison: .itqahn/evidence/rebuild/date-helpers-parity.json
- Test results: .itqahn/evidence/rebuild/date-helpers-tests.json

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

#### 4.4.2 Cutover PR

```markdown
## [Rebuild] Cutover: Complete Migration

### Cutover Summary
- **Project:** acme-legacy-app
- **Strategy:** Strangler-style
- **Duration:** 3 weeks
- **Components Migrated:** 12/12

### Pre-Cutover Checklist
- [x] All component migrations complete
- [x] Full parity verification passed
- [x] Performance benchmarks within tolerance
- [x] Security scan clean
- [x] Rollback procedure documented
- [x] Stakeholder sign-off obtained

### Rollback Plan
1. Revert this PR
2. Redeploy legacy-main branch
3. DNS/routing switch (< 5 min)

### Evidence Pack
- Complete rebuild evidence: .itqahn/evidence-pack/rebuild-evidence.json
- Parity report: .itqahn/evidence/parity-final.json
- Performance comparison: .itqahn/evidence/perf-comparison.json

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 5. Parity and Cutover Verification

### 5.1 Parity Harness

The Parity Harness ensures behavioral equivalence between legacy and rebuilt systems:

#### 5.1.1 API Parity Testing

```yaml
# .itqahn/parity/api-parity.yaml
parity_tests:
  - name: "User CRUD Operations"
    legacy_endpoint: "http://legacy:3000/api/users"
    rebuild_endpoint: "http://rebuild:3000/api/users"
    operations:
      - method: POST
        path: /
        body_schema: user_create.json
        compare:
          - status_code
          - response_schema
          - response_time_tolerance: 1.5x

      - method: GET
        path: /{id}
        compare:
          - status_code
          - response_body
          - cache_headers
```

#### 5.1.2 Database Parity Testing

```yaml
# .itqahn/parity/db-parity.yaml
database_parity:
  legacy_db: "postgresql://legacy-db:5432/app"
  rebuild_db: "postgresql://rebuild-db:5432/app"

  comparisons:
    - table: users
      compare_columns: [id, email, created_at, updated_at]
      ignore_columns: [password_hash]  # Implementation may differ

    - table: orders
      compare_columns: all
      row_match_key: [order_id]
```

#### 5.1.3 UI Parity Testing

```yaml
# .itqahn/parity/ui-parity.yaml
visual_parity:
  tool: playwright

  comparisons:
    - page: /login
      viewport: [1920, 1080]
      threshold: 0.95  # 95% visual similarity
      ignore_regions:
        - selector: ".timestamp"  # Dynamic content

    - page: /dashboard
      viewport: [1920, 1080]
      threshold: 0.90
      interactions:
        - click: "#show-chart"
        - wait: 1000
```

### 5.2 Parity Report

```json
{
  "parity_report": {
    "generated_at": "2026-01-08T15:00:00Z",
    "overall_status": "PASS",
    "overall_score": 0.97,

    "api_parity": {
      "status": "PASS",
      "endpoints_tested": 45,
      "endpoints_passed": 45,
      "response_time_comparison": {
        "average_legacy_ms": 120,
        "average_rebuild_ms": 85,
        "improvement": "29%"
      }
    },

    "database_parity": {
      "status": "PASS",
      "tables_compared": 12,
      "rows_compared": 50000,
      "discrepancies": 0
    },

    "ui_parity": {
      "status": "PASS_WITH_WARNINGS",
      "pages_tested": 15,
      "pages_passed": 14,
      "warnings": [
        {
          "page": "/settings",
          "score": 0.88,
          "reason": "New design system fonts"
        }
      ]
    },

    "behavior_parity": {
      "status": "PASS",
      "scenarios_tested": 120,
      "scenarios_passed": 120
    }
  }
}
```

### 5.3 Cutover Plan

#### 5.3.1 Cutover Checklist

```yaml
# .itqahn/cutover/plan.yaml
cutover_plan:
  name: "acme-legacy-app-cutover"
  scheduled_at: "2026-01-15T02:00:00Z"  # Low traffic window

  pre_cutover:
    - task: "Final parity verification"
      status: pending
      required: true

    - task: "Stakeholder sign-off"
      status: pending
      required: true
      approvers: ["@product-owner", "@tech-lead"]

    - task: "Rollback procedure test"
      status: pending
      required: true

    - task: "Monitoring dashboards ready"
      status: pending
      required: true

  cutover_steps:
    - step: 1
      action: "Enable maintenance mode"
      duration: "1 min"
      rollback: "Disable maintenance mode"

    - step: 2
      action: "Database migration (if needed)"
      duration: "5 min"
      rollback: "Restore from snapshot"

    - step: 3
      action: "Switch DNS/routing"
      duration: "2 min"
      rollback: "Revert DNS"

    - step: 4
      action: "Smoke test critical paths"
      duration: "5 min"
      rollback: "Initiate full rollback"

    - step: 5
      action: "Disable maintenance mode"
      duration: "1 min"
      rollback: "Re-enable maintenance"

  post_cutover:
    - task: "Monitor error rates (30 min)"
    - task: "Monitor performance metrics (30 min)"
    - task: "User feedback collection"
    - task: "Legacy system decommission (7 days)"
```

#### 5.3.2 Rollback Triggers

Automatic rollback is triggered if:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Error rate spike | >5% increase | Immediate rollback |
| Response time | >2x baseline | Warn, rollback if persists 5 min |
| Critical endpoint failure | Any 5xx | Immediate rollback |
| Database errors | Any connection failure | Immediate rollback |
| User-reported critical | 3+ reports in 10 min | Manual review, likely rollback |

---

## 6. Evidence Pack Requirements

### 6.1 Legacy Rebuild Evidence

The Evidence Pack MUST include:

```json
{
  "evidence_type": "legacy_rebuild",
  "rebuild_id": "rebuild-abc123",
  "project_id": "proj-xyz789",

  "import_evidence": {
    "source": "github.com/acme/legacy-app",
    "imported_at": "2026-01-08T10:30:00Z",
    "legacy_snapshot_tag": "legacy-snapshot",
    "legacy_snapshot_sha": "abc123...",
    "discovery_report_hash": "sha256:def..."
  },

  "strategy_evidence": {
    "strategy": "strangler",
    "rationale": "Working production system with salvageable core",
    "operator_approval": {
      "approved_by": "operator@acme.com",
      "approved_at": "2026-01-08T11:00:00Z"
    }
  },

  "migration_evidence": {
    "components_migrated": 12,
    "component_evidence": [
      {
        "component": "utils/date-helpers",
        "migration_pr": "PR #123",
        "parity_result": "PASS",
        "tests_added": 45,
        "coverage": 0.98
      }
    ]
  },

  "parity_evidence": {
    "final_parity_score": 0.97,
    "parity_report_hash": "sha256:ghi...",
    "api_parity": "PASS",
    "database_parity": "PASS",
    "ui_parity": "PASS_WITH_WARNINGS",
    "behavior_parity": "PASS"
  },

  "cutover_evidence": {
    "cutover_executed_at": "2026-01-15T02:00:00Z",
    "cutover_duration_minutes": 14,
    "rollback_required": false,
    "post_cutover_metrics": {
      "error_rate": 0.001,
      "response_time_p99_ms": 95,
      "user_reports": 0
    }
  },

  "security_evidence": {
    "legacy_vulnerabilities_fixed": 27,
    "new_system_scan_result": "CLEAN",
    "dependency_audit_result": "PASS"
  }
}
```

### 6.2 Audit Trail

All rebuild actions MUST be logged:

| Event | Required Fields |
|-------|-----------------|
| `rebuild.import_started` | project_id, source, timestamp |
| `rebuild.discovery_completed` | project_id, discovery_report_ref |
| `rebuild.strategy_selected` | project_id, strategy, rationale, operator |
| `rebuild.component_migration_started` | project_id, component, branch |
| `rebuild.component_migration_completed` | project_id, component, parity_result, pr_number |
| `rebuild.parity_test_executed` | project_id, test_type, result, report_ref |
| `rebuild.cutover_started` | project_id, timestamp, operator |
| `rebuild.cutover_completed` | project_id, duration, rollback_required |
| `rebuild.rollback_executed` | project_id, reason, timestamp |

---

## 7. Edge Cases and Failure Recovery

### 7.1 Broken Build on Import

**Scenario:** Legacy code doesn't build on import.

**Resolution:**
1. Discovery continues in "analysis-only" mode
2. Build failures are cataloged in discovery report
3. Operator is notified with failure details
4. Options presented:
   - Provide build instructions/environment
   - Proceed with Clean Rebuild (spec extraction from code analysis)
   - Manual intervention to fix build

### 7.2 Hardcoded Secrets Detected

**Scenario:** Discovery finds hardcoded credentials.

**Resolution:**
1. Secrets are redacted in discovery report
2. Files containing secrets are flagged
3. Warning displayed: "Secrets detected - review before proceeding"
4. Options:
   - Acknowledge and proceed (secrets remain in legacy-snapshot)
   - Provide cleaned branch/commit
   - Rotate secrets before migration

**Evidence:** Secret detection is logged but content is NOT recorded.

### 7.3 Git LFS Content

**Scenario:** Repository uses Git LFS for large files.

**Resolution:**
1. LFS content is fetched during import
2. LFS files are cataloged separately
3. Rebuild strategy considers LFS handling:
   - Migrate LFS to new system
   - Move assets to external storage (S3, etc.)
   - Evaluate if LFS is still needed

### 7.4 Mixed Language Codebase

**Scenario:** Legacy system has 4+ languages with unclear boundaries.

**Resolution:**
1. Discovery identifies language boundaries
2. Each language component analyzed separately
3. Migration order considers language dependencies
4. Parity testing spans all languages
5. Operator may choose to consolidate languages in rebuild

### 7.5 Incomplete Requirements Recovery

**Scenario:** Cannot extract complete specification from code.

**Resolution:**
1. Discovery generates partial specification
2. Gaps are flagged with "REQUIRES_INPUT" markers
3. Operator completes missing requirements via dashboard
4. Completed specification becomes Concept Lock
5. Clean Rebuild proceeds from hybrid spec

### 7.6 Licensing Issues Detected

**Scenario:** Discovery finds incompatible licenses.

**Resolution:**
1. License scan results included in discovery report
2. Incompatible licenses highlighted with severity:
   - **Critical:** GPL in proprietary context
   - **Warning:** License unclear, review needed
   - **Info:** License change recommended
3. Rebuild plan includes license remediation:
   - Replace incompatible dependencies
   - Obtain commercial licenses
   - Restructure to isolate licensed code

### 7.7 Cutover Failure and Rollback

**Scenario:** Post-cutover metrics exceed rollback thresholds.

**Resolution:**
1. Automatic rollback initiated
2. Steps executed in reverse:
   - Re-enable legacy routing
   - Restore database snapshot (if modified)
   - Enable legacy system
   - Disable maintenance mode
3. Incident created with rollback details
4. Evidence Pack updated with:
   - Rollback trigger reason
   - Metrics at time of rollback
   - Rollback execution log
5. Post-incident review scheduled

### 7.8 Operator Abandons Rebuild

**Scenario:** Rebuild started but not completed for >30 days.

**Resolution:**
1. System sends reminder at 7, 14, 21 days
2. At 30 days: "Stale rebuild" warning
3. Options presented:
   - Resume rebuild
   - Archive rebuild (preserve state)
   - Terminate rebuild (cleanup branches)
4. Archived rebuilds can be resumed within 90 days
5. After 90 days, rebuild branches are auto-deleted (legacy-snapshot preserved)

---

## 8. Dashboard UX

### 8.1 Import Wizard Summary

After import, dashboard shows:

```
┌─────────────────────────────────────────────────────────┐
│  LEGACY IMPORT COMPLETE                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Project: acme-legacy-app                               │
│  Source: github.com/acme/legacy-app                     │
│  Imported: 2026-01-08 10:30 UTC                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ DISCOVERY SUMMARY                               │   │
│  │                                                 │   │
│  │ Languages: TypeScript (65%), JS (11%), Py (8%) │   │
│  │ Frameworks: React, Express, Django              │   │
│  │ Lines of Code: 73,600                          │   │
│  │ Security Issues: 27 (2 critical)               │   │
│  │ Test Coverage: ~42%                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ RECOMMENDED: Strangler-Style Migration          │   │
│  │                                                 │   │
│  │ Rationale: Working production system with       │   │
│  │ salvageable core. Incremental approach reduces  │   │
│  │ risk and allows continuous operation.           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Start Rebuild]  [View Full Report]  [Change Strategy] │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Rebuild Progress Panel

```
┌─────────────────────────────────────────────────────────┐
│  LEGACY REBUILD PROGRESS                    Strangler   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Overall: ████████████░░░░░░░░  60% (7/12 components)  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ COMPONENTS                                      │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ✓ utils/date-helpers      Migrated   PR #123   │   │
│  │ ✓ utils/validation        Migrated   PR #124   │   │
│  │ ✓ services/email          Migrated   PR #125   │   │
│  │ ✓ services/storage        Migrated   PR #126   │   │
│  │ ✓ api/health              Migrated   PR #127   │   │
│  │ ✓ api/users               Migrated   PR #128   │   │
│  │ ● api/orders              In Progress          │   │
│  │ ○ api/payments            Pending              │   │
│  │ ○ auth/login              Pending              │   │
│  │ ○ auth/oauth              Pending              │   │
│  │ ○ ui/dashboard            Pending              │   │
│  │ ○ ui/settings             Pending              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Parity Score: 0.94          [Run Parity Tests]        │
│  Last Activity: 5 min ago    [View Timeline]           │
│                                                         │
│  [Pause Rebuild]                        [Plan Cutover] │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Permissions and Access Control

### 9.1 Required Permissions

| Action | Required Role |
|--------|---------------|
| Import legacy project | `org:write` |
| View discovery report | `project:read` |
| Start rebuild | `project:admin` |
| Approve component migration | `project:write` |
| Execute cutover | `project:admin` |
| Trigger rollback | `project:admin` |
| Modify rebuild strategy | `project:admin` |

### 9.2 Operator Mode Permissions

When Operator Mode is enabled with `--dangerously-skip-permissions`:

- All rebuild steps execute without interactive approval
- Strategy selection is auto-confirmed
- Component migrations are auto-merged (if CI passes)
- Cutover still requires explicit trigger (safety)
- Rollback can be automatic based on thresholds

---

## 10. Related Documentation

- [Track Assurance](./track-assurance.md) - Drift detection during rebuild
- [Git Integration](../07-integrations/git-integration.md) - Branch conventions
- [Evidence Pack](../05-compliance/evidence-pack.md) - Rebuild evidence requirements
- [Workflow Architecture](../02-architecture/workflow-architecture.md) - Rebuild workflow design
- [Runbooks](../06-operations/runbooks.md) - Rebuild incident response

---

## Appendix A: Legacy Rebuild Report Template

```markdown
# Legacy Rebuild Report

## Project Information
- **Project Name:** {project_name}
- **Rebuild ID:** {rebuild_id}
- **Strategy:** {strategy}
- **Start Date:** {start_date}
- **Completion Date:** {completion_date}

## Import Summary
- **Source:** {source_url}
- **Legacy Snapshot:** {legacy_snapshot_sha}
- **Lines of Code:** {loc}
- **Languages:** {languages}

## Discovery Findings
### Security
- Critical: {critical_count}
- High: {high_count}
- Medium: {medium_count}
- Resolved: {resolved_count}

### Code Quality
- Test Coverage (Before): {coverage_before}%
- Test Coverage (After): {coverage_after}%
- Technical Debt Items: {debt_items}

## Migration Summary
| Component | Status | PR | Parity |
|-----------|--------|-----|--------|
{component_table}

## Parity Results
- **Overall Score:** {parity_score}
- **API Parity:** {api_parity}
- **Database Parity:** {db_parity}
- **UI Parity:** {ui_parity}

## Cutover Summary
- **Executed At:** {cutover_time}
- **Duration:** {cutover_duration}
- **Rollback Required:** {rollback_required}

## Lessons Learned
{lessons_learned}

---
Generated: {timestamp}
```
