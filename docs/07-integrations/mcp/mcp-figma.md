# MCP Figma Integration

The Figma MCP provides read-only access to design files, enabling agents to extract design tokens, components, and baseline screenshots for Design Jail enforcement.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIGMA MCP FLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Agent  │───▶│  Figma MCP  │───▶│  Figma API  │             │
│  │         │    │             │    │             │             │
│  └─────────┘    └──────┬──────┘    └──────┬──────┘             │
│                        │                  │                     │
│         ┌──────────────┼──────────────────┤                    │
│         │              │                  │                    │
│         ▼              ▼                  ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐              │
│  │  Design  │  │  Export  │  │  Screenshot     │              │
│  │  Tokens  │  │  Assets  │  │  Baselines      │              │
│  └──────────┘  └──────────┘  └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capabilities

### Supported Operations

| Operation | Description | Rate Limit |
|-----------|-------------|------------|
| `file.read` | Read Figma file structure | 60/min |
| `file.versions` | List file versions | 30/min |
| `component.list` | List all components | 60/min |
| `component.export` | Export component as image | 30/min |
| `token.export` | Export design tokens | 30/min |
| `style.list` | List text and color styles | 60/min |
| `comment.read` | Read design comments | 60/min |
| `screenshot.capture` | Capture frame screenshot | 10/min |

### Read-Only Enforcement

The Figma MCP is **read-only by design**. Agents cannot:
- Modify design files
- Add or delete components
- Change styles or tokens
- Post comments (optional: can be enabled)

---

## Authentication

### OAuth Configuration

```yaml
figma:
  auth:
    method: oauth2
    token_source: vault
    vault_path: kv/mcp/figma/token
    scopes:
      - file_read
    token_refresh: true
    token_ttl: 4h
```

### Personal Access Token (Alternative)

```yaml
figma:
  auth:
    method: personal_access_token
    token_source: vault
    vault_path: kv/mcp/figma/pat
```

---

## Operations

### Read File

Retrieve file structure and metadata:

```json
{
  "operation": "file.read",
  "params": {
    "file_key": "abc123XYZ",
    "depth": 2
  }
}
```

Response:
```json
{
  "file": {
    "name": "Design System",
    "lastModified": "2026-01-06T12:00:00Z",
    "version": "456789",
    "document": {
      "children": [...]
    }
  }
}
```

### Export Design Tokens

Extract design tokens in standard format:

```json
{
  "operation": "token.export",
  "params": {
    "file_key": "abc123XYZ",
    "format": "json",
    "include": ["colors", "typography", "spacing", "shadows"]
  }
}
```

Response:
```json
{
  "tokens": {
    "colors": {
      "primary": {
        "value": "#0066FF",
        "type": "color"
      },
      "secondary": {
        "value": "#6B7280",
        "type": "color"
      }
    },
    "typography": {
      "heading-1": {
        "value": {
          "fontFamily": "Inter",
          "fontSize": 32,
          "fontWeight": 700,
          "lineHeight": 1.2
        },
        "type": "typography"
      }
    },
    "spacing": {
      "sm": {"value": 8, "type": "spacing"},
      "md": {"value": 16, "type": "spacing"},
      "lg": {"value": 24, "type": "spacing"}
    }
  }
}
```

### Export Component

Export component as image:

```json
{
  "operation": "component.export",
  "params": {
    "file_key": "abc123XYZ",
    "node_id": "1:234",
    "format": "png",
    "scale": 2
  }
}
```

Response:
```json
{
  "images": {
    "1:234": "https://figma-alpha-api.s3.amazonaws.com/..."
  },
  "metadata": {
    "format": "png",
    "scale": 2,
    "width": 400,
    "height": 300
  }
}
```

### Capture Screenshot

Capture frame for baseline comparison:

```json
{
  "operation": "screenshot.capture",
  "params": {
    "file_key": "abc123XYZ",
    "frame_id": "5:678",
    "viewport": {
      "width": 1440,
      "height": 900
    },
    "format": "png"
  }
}
```

---

## Design OS Extraction Pipeline

The Figma MCP extracts design artifacts into Design OS format. This is the authoritative pipeline for populating `tokens.json`, `components.json`, and visual baselines.

### Extraction Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIGMA → DESIGN OS PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                                                        │
│  │ Figma File   │  Source of truth for design                           │
│  │ (Design Sys) │                                                        │
│  └──────┬───────┘                                                        │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────┐                                                        │
│  │  Figma MCP   │  Authenticated, rate-limited access                   │
│  │              │                                                        │
│  └──────┬───────┘                                                        │
│         │                                                                │
│         ├─────────────────┬─────────────────┬─────────────────┐         │
│         ▼                 ▼                 ▼                 ▼         │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐     │
│  │  Extract   │   │  Extract   │   │  Export    │   │  Capture   │     │
│  │  Tokens    │   │ Components │   │   Assets   │   │ Baselines  │     │
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘     │
│        │                │                │                │            │
│        ▼                ▼                ▼                ▼            │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐     │
│  │ tokens.json│   │components  │   │  assets/   │   │visual-     │     │
│  │ (W3C fmt)  │   │.json       │   │            │   │baselines/  │     │
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘     │
│        │                │                │                │            │
│        └────────────────┴────────────────┴────────────────┘            │
│                                  │                                      │
│                                  ▼                                      │
│                         ┌──────────────┐                                │
│                         │   Validate   │                                │
│                         │   Schema     │                                │
│                         └──────┬───────┘                                │
│                                │                                        │
│                                ▼                                        │
│                         ┌──────────────┐                                │
│                         │  Commit to   │                                │
│                         │  Design OS   │                                │
│                         │  Repository  │                                │
│                         └──────────────┘                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Extraction Operations

#### 1. Token Extraction

```json
{
  "operation": "design_os.extract_tokens",
  "params": {
    "file_key": "abc123XYZ",
    "output_format": "w3c",
    "include": ["colors", "typography", "spacing", "shadows", "radius"],
    "output_path": "design-os/tokens.json"
  }
}
```

Transforms Figma styles to W3C Design Tokens format:

```json
// Input: Figma style "Primary/500"
// Output: W3C token
{
  "color": {
    "brand": {
      "primary": {
        "$value": "#2563eb",
        "$type": "color",
        "$description": "Primary brand color"
      }
    }
  }
}
```

#### 2. Component Extraction

```json
{
  "operation": "design_os.extract_components",
  "params": {
    "file_key": "abc123XYZ",
    "include_variants": true,
    "include_props": true,
    "output_path": "design-os/components.json"
  }
}
```

Generates component catalog with:
- Component name and category
- Variants (from Figma variant properties)
- Props (from component properties)
- Platform support flags
- Accessibility hints (from Figma layer names)

#### 3. Visual Baseline Capture

```json
{
  "operation": "design_os.capture_baselines",
  "params": {
    "file_key": "abc123XYZ",
    "frames": [
      { "name": "Login Page", "viewport": { "width": 1440, "height": 900 } },
      { "name": "Dashboard", "viewport": { "width": 1440, "height": 900 } },
      { "name": "Login Mobile", "viewport": { "width": 375, "height": 812 } }
    ],
    "output_path": "design-os/visual-baselines/"
  }
}
```

#### 4. Pattern Extraction

```json
{
  "operation": "design_os.extract_patterns",
  "params": {
    "file_key": "abc123XYZ",
    "page": "Patterns",
    "output_path": "design-os/patterns/"
  }
}
```

### Allowlisted Operations

| Operation | Allowed | Prohibited |
|-----------|---------|------------|
| `file.read` | ✅ Read file structure | |
| `token.export` | ✅ Extract tokens | |
| `component.list` | ✅ List components | |
| `component.export` | ✅ Export as image | |
| `screenshot.capture` | ✅ Capture baselines | |
| `file.write` | | ❌ Modify designs |
| `component.create` | | ❌ Add components |
| `style.create` | | ❌ Create styles |
| `comment.write` | | ❌ Post comments |

### Sync Automation

```yaml
# .github/workflows/design-os-sync.yml
name: Design OS Sync

on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am
  workflow_dispatch:      # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract Design OS
        run: |
          npx design-os-cli extract \
            --figma-file ${{ secrets.FIGMA_FILE_KEY }} \
            --output design-os/ \
            --format w3c

      - name: Validate Schema
        run: |
          npx design-os-cli validate \
            --tokens design-os/tokens.json \
            --components design-os/components.json

      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: sync Design OS from Figma"
          branch: design-os-sync
          commit-message: "chore: sync Design OS from Figma"
```

---

## Design Jail Integration

### Token Sync Flow

```
1. Figma MCP extracts tokens via design_os.extract_tokens
       │
       ▼
2. Tokens written to design-os/tokens.json (W3C format)
       │
       ▼
3. Design Jail validator loads tokens from Design OS
       │
       ▼
4. Build-time validation against Design OS version
       │
       ▼
5. Violations block merge
```

### Component Registry

```json
{
  "operation": "component.list",
  "params": {
    "file_key": "abc123XYZ",
    "include_variants": true
  }
}
```

Response stored in `design/components.json`:
```json
{
  "components": {
    "Button": {
      "id": "1:100",
      "variants": ["primary", "secondary", "ghost"],
      "props": ["size", "disabled", "loading"]
    },
    "Input": {
      "id": "1:200",
      "variants": ["default", "error"],
      "props": ["label", "placeholder", "error"]
    }
  }
}
```

### Screenshot Baselines

```json
{
  "operation": "screenshot.capture",
  "params": {
    "file_key": "abc123XYZ",
    "frames": ["Login Page", "Dashboard", "Settings"],
    "viewport": {"width": 1440, "height": 900}
  }
}
```

Baselines stored in `design/baselines/`:
```
design/baselines/
├── login-page.png
├── dashboard.png
└── settings.png
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  figma:
    enabled: true
    base_url: "https://api.figma.com/v1"

    auth:
      method: oauth2
      token_source: vault
      vault_path: kv/mcp/figma/token

    rate_limits:
      default: 60
      export: 30
      screenshot: 10

    cache:
      enabled: true
      ttl_minutes: 60

    allowed_files:
      - "abc123XYZ"  # Design System
      - "def456ABC"  # App Designs

    export:
      default_format: png
      default_scale: 2
      max_scale: 4
```

### Allowlist Entry

```yaml
roles:
  frontend-builder:
    mcps:
      figma:
        operations:
          - file.read
          - component.list
          - component.export
          - token.export
          - screenshot.capture
        constraints:
          files: ["abc123XYZ", "def456ABC"]
          max_exports_per_request: 20
```

---

## Caching

### Cache Strategy

| Data Type | Cache TTL | Invalidation |
|-----------|-----------|--------------|
| File structure | 1 hour | Version change |
| Components | 1 hour | Version change |
| Tokens | 1 hour | Version change |
| Exports | 24 hours | Manual |
| Screenshots | 24 hours | Manual |

### Cache Configuration

```yaml
figma:
  cache:
    enabled: true
    backend: redis
    prefix: "figma:"
    ttl:
      file: 3600
      component: 3600
      token: 3600
      export: 86400
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `FIGMA_AUTH_FAILED` | Authentication failed | Refresh token |
| `FIGMA_FILE_NOT_FOUND` | File doesn't exist | Check file key |
| `FIGMA_NODE_NOT_FOUND` | Node doesn't exist | Check node ID |
| `FIGMA_RATE_LIMITED` | Rate limit exceeded | Back off |
| `FIGMA_EXPORT_FAILED` | Export failed | Retry |

### Fallback Behavior

```yaml
figma:
  fallback:
    on_auth_failure:
      action: use_cached
      notify: true

    on_rate_limit:
      action: queue_and_retry
      max_wait_seconds: 300

    on_export_failure:
      action: retry
      max_retries: 3
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `figma_mcp_requests_total` | Total requests by operation |
| `figma_mcp_latency` | Request latency |
| `figma_mcp_cache_hits` | Cache hit ratio |
| `figma_mcp_exports_total` | Export operations |
| `figma_token_sync_status` | Token sync health |

### Alerts

```yaml
alerts:
  - name: figma_auth_failures
    condition: rate(figma_mcp_requests_total{status="auth_failed"}[5m]) > 0
    severity: warning

  - name: figma_token_sync_stale
    condition: time() - figma_token_sync_timestamp > 86400
    severity: warning
```

---

## Security Considerations

### Access Control

- Only whitelisted Figma files are accessible
- Personal access tokens stored in Vault
- OAuth tokens auto-refreshed
- All requests logged with audit trail

### Data Handling

- Exported images stored temporarily
- Screenshots compared locally, not persisted
- Design tokens committed to repository
- No PII extracted from designs

---

## Related Documents

- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/05-compliance/evidence-pack.md` — Design evidence requirements
- `templates/design/` — Design OS artifacts

---

**Version**: 2.0.0 | **Date**: 2026-01-06
