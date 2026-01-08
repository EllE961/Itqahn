# MCP Assets Integration

The Assets MCP provides controlled access to image generation, editing, and asset management operations for Itqahn agents. All operations are governed by Design OS constraints.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASSETS MCP FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────────────────────────────┐ │
│  │  Agent  │───▶│ Assets MCP  │───▶│  Generation Providers               │ │
│  │         │    │             │    │  ┌──────────┐ ┌─────────┐ ┌───────┐│ │
│  └─────────┘    └──────┬──────┘    │  │NanoBanana│ │Replicate│ │ RunPod ││ │
│                        │           │  │(Primary) │ │(Backup) │ │(Backup)││ │
│                        │           │  └──────────┘ └─────────┘ └───────┘│ │
│                        │           └─────────────────────────────────────┘ │
│         ┌──────────────┼──────────────────────────────────────┐            │
│         │              │                                      │            │
│         ▼              ▼                                      ▼            │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Design OS│  │   Generate   │  │  Edit    │  │     Registry         │  │
│  │ Validate │  │  (img2img,   │  │  (crop,  │  │  (store, version,    │  │
│  │          │  │   txt2img)   │  │  upscale)│  │   serve)             │  │
│  └──────────┘  └──────────────┘  └──────────┘  └──────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **NanoBanana** is the primary image generation provider for Itqahn Asset Factory. API credentials are stored in Vault and injected at runtime. See `docs/07-integrations/mcp/mcp-nanobanana.md` for full specification.

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level | Rate Limit |
|-----------|-------------|------------|------------|
| `asset.generate` | Generate new image from prompt | High | 10/min |
| `asset.edit` | Edit existing image (inpaint, outpaint) | High | 15/min |
| `asset.bgremove` | Remove background from image | Medium | 30/min |
| `asset.upscale` | Upscale image resolution | Medium | 20/min |
| `asset.vectorize` | Convert raster to SVG | Medium | 20/min |
| `asset.crop` | Crop and resize image | Low | 60/min |
| `asset.convert` | Convert between formats | Low | 60/min |
| `asset.lint` | Validate asset against Design OS | Low | 100/min |
| `asset.drift` | Check asset drift from style anchor | Low | 50/min |
| `registry.store` | Store asset in registry | Low | 60/min |
| `registry.get` | Retrieve asset from registry | Low | 200/min |
| `registry.list` | List assets in registry | Low | 100/min |
| `registry.search` | Search assets by metadata | Low | 50/min |
| `registry.delete` | Delete asset from registry | Medium | 10/min |

### Operation Categories

| Category | Operations | Requires |
|----------|------------|----------|
| **Generation** | generate, edit | Design OS validation, style anchor |
| **Transform** | bgremove, upscale, vectorize, crop, convert | Input asset exists |
| **Validation** | lint, drift | Design OS version |
| **Registry** | store, get, list, search, delete | Registry access |

---

## Authentication

### Provider Authentication

Each generation provider uses separate credentials stored in Vault:

```yaml
assets:
  providers:
    nanobanana:
      auth:
        method: api_key
        token_source: vault
        vault_path: kv/itqahn/services/nanobanana
        # Key is injected at MCP server runtime, NEVER exposed to agents
      priority: 1
      primary: true

    replicate:
      auth:
        method: api_key
        token_source: vault
        vault_path: kv/mcp/assets/replicate-key
      priority: 2
      fallback: true

    runpod:
      auth:
        method: api_key
        token_source: vault
        vault_path: kv/mcp/assets/runpod-key
      priority: 3
      fallback: true

    local:
      auth:
        method: none
        endpoint: http://comfyui.internal:8188
      priority: 4
      enabled: false  # Enterprise only
```

> **Security**: NanoBanana API key is injected at MCP server startup and NEVER visible to agents. Agents call MCP tools without credentials; the MCP server layer handles authentication.

### Agent Authentication

Agents authenticate via SPIFFE:

```yaml
assets:
  agent_auth:
    method: spiffe
    trust_domain: itqahn.io
    allowed_spiffe_ids:
      - "spiffe://itqahn.io/agent/asset-generator"
      - "spiffe://itqahn.io/agent/design-guardian"
```

---

## Operations

### Generate Asset

Generate a new image with Design OS constraints:

```json
{
  "operation": "asset.generate",
  "params": {
    "prompt": "Modern app icon for task management",
    "negative_prompt": "text, watermark, blurry",
    "asset_type": "app-icon",
    "style_anchor": "icons/modern-flat",
    "design_os_version": "1.2.0",
    "constraints": {
      "palette": "brand-primary",
      "max_colors": 5,
      "aspect_ratio": "1:1"
    },
    "output": {
      "format": "png",
      "width": 1024,
      "height": 1024
    },
    "provider": "replicate",
    "model": "sdxl-1.0"
  }
}
```

Response:
```json
{
  "asset_id": "ast-abc123",
  "status": "completed",
  "output": {
    "url": "s3://assets/generated/ast-abc123.png",
    "format": "png",
    "width": 1024,
    "height": 1024,
    "hash": "sha256:abc123..."
  },
  "validation": {
    "palette_compliant": true,
    "style_similarity": 0.92,
    "drift_score": 0.08
  },
  "metadata": {
    "provider": "replicate",
    "model": "sdxl-1.0",
    "generation_time_ms": 4500,
    "cost_usd": 0.02,
    "seed": 42
  },
  "provenance": {
    "workflow_id": "wf-xyz789",
    "agent_id": "asset-generator",
    "timestamp": "2026-01-06T12:00:00Z"
  }
}
```

### Edit Asset

Edit existing image with inpainting/outpainting:

```json
{
  "operation": "asset.edit",
  "params": {
    "source_asset": "ast-abc123",
    "edit_type": "inpaint",
    "mask": "base64://...",
    "prompt": "Replace background with gradient",
    "design_os_version": "1.2.0",
    "constraints": {
      "preserve_palette": true
    }
  }
}
```

Response:
```json
{
  "asset_id": "ast-def456",
  "status": "completed",
  "output": {
    "url": "s3://assets/edited/ast-def456.png",
    "format": "png",
    "hash": "sha256:def456..."
  },
  "lineage": {
    "parent_asset": "ast-abc123",
    "edit_type": "inpaint"
  }
}
```

### Remove Background

```json
{
  "operation": "asset.bgremove",
  "params": {
    "source": "s3://assets/input/photo.jpg",
    "output_format": "png",
    "edge_refinement": "high"
  }
}
```

Response:
```json
{
  "asset_id": "ast-ghi789",
  "status": "completed",
  "output": {
    "url": "s3://assets/processed/ast-ghi789.png",
    "format": "png",
    "has_alpha": true
  }
}
```

### Upscale Asset

```json
{
  "operation": "asset.upscale",
  "params": {
    "source": "ast-abc123",
    "scale": 4,
    "model": "real-esrgan",
    "denoise": 0.3
  }
}
```

Response:
```json
{
  "asset_id": "ast-jkl012",
  "status": "completed",
  "output": {
    "url": "s3://assets/upscaled/ast-jkl012.png",
    "width": 4096,
    "height": 4096
  },
  "lineage": {
    "parent_asset": "ast-abc123",
    "operation": "upscale",
    "scale": 4
  }
}
```

### Vectorize Asset

Convert raster to SVG:

```json
{
  "operation": "asset.vectorize",
  "params": {
    "source": "ast-abc123",
    "color_mode": "palette",
    "palette_source": "design-os",
    "simplify": 0.5,
    "corner_threshold": 60
  }
}
```

Response:
```json
{
  "asset_id": "ast-mno345",
  "status": "completed",
  "output": {
    "url": "s3://assets/vector/ast-mno345.svg",
    "format": "svg",
    "paths": 24,
    "colors": 5
  }
}
```

### Lint Asset

Validate asset against Design OS rules:

```json
{
  "operation": "asset.lint",
  "params": {
    "asset": "ast-abc123",
    "design_os_version": "1.2.0",
    "rules": ["palette", "contrast", "sizing", "format"]
  }
}
```

Response:
```json
{
  "asset_id": "ast-abc123",
  "status": "completed",
  "lint_result": {
    "passed": false,
    "violations": [
      {
        "rule": "palette",
        "severity": "error",
        "message": "Color #FF5733 not in approved palette",
        "suggestion": "Use var(--color-brand-accent) #F97316"
      },
      {
        "rule": "contrast",
        "severity": "warning",
        "message": "Contrast ratio 3.8:1 below WCAG AA (4.5:1)",
        "location": "center region"
      }
    ],
    "summary": {
      "errors": 1,
      "warnings": 1,
      "passed": 2
    }
  }
}
```

### Check Drift

Check asset drift from style anchor:

```json
{
  "operation": "asset.drift",
  "params": {
    "asset": "ast-abc123",
    "style_anchor": "icons/modern-flat",
    "threshold": 0.15
  }
}
```

Response:
```json
{
  "asset_id": "ast-abc123",
  "status": "completed",
  "drift_result": {
    "similarity_score": 0.87,
    "drift_score": 0.13,
    "threshold": 0.15,
    "verdict": "pass",
    "recommendation": "Asset within acceptable drift range"
  }
}
```

### Store in Registry

```json
{
  "operation": "registry.store",
  "params": {
    "asset": "ast-abc123",
    "namespace": "tenant-acme/app-icons",
    "name": "task-manager-icon",
    "version": "1.0.0",
    "tags": ["production", "ios", "primary"],
    "metadata": {
      "design_os_version": "1.2.0",
      "style_anchor": "icons/modern-flat",
      "approved_by": "design-guardian"
    }
  }
}
```

Response:
```json
{
  "registry_id": "reg-abc123",
  "namespace": "tenant-acme/app-icons",
  "name": "task-manager-icon",
  "version": "1.0.0",
  "digest": "sha256:abc123...",
  "url": "registry.itqahn.io/tenant-acme/app-icons/task-manager-icon:1.0.0"
}
```

### Search Registry

```json
{
  "operation": "registry.search",
  "params": {
    "namespace": "tenant-acme/*",
    "query": "icon",
    "tags": ["production"],
    "asset_type": "app-icon",
    "limit": 20
  }
}
```

Response:
```json
{
  "results": [
    {
      "registry_id": "reg-abc123",
      "name": "task-manager-icon",
      "version": "1.0.0",
      "tags": ["production", "ios", "primary"],
      "created_at": "2026-01-06T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## Design OS Integration

### Constraint Enforcement

All generation operations enforce Design OS constraints:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DESIGN OS CONSTRAINT FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Agent submits asset.generate request                                    │
│           │                                                                  │
│           ▼                                                                  │
│  2. MCP loads Design OS version specified                                   │
│           │                                                                  │
│           ▼                                                                  │
│  3. Style anchor embedding loaded                                           │
│           │                                                                  │
│           ▼                                                                  │
│  4. Prompt augmented with Design OS constraints                             │
│     - Palette tokens injected                                               │
│     - Typography rules added                                                │
│     - Style keywords from anchor added                                      │
│           │                                                                  │
│           ▼                                                                  │
│  5. Generation executed with constraints                                    │
│           │                                                                  │
│           ▼                                                                  │
│  6. Output validated:                                                       │
│     - Palette compliance (color extraction)                                 │
│     - Style similarity (embedding distance)                                 │
│     - Accessibility (contrast ratios)                                       │
│           │                                                                  │
│           ├── Pass → Return asset                                           │
│           │                                                                  │
│           └── Fail → Regenerate (up to limit) or error                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Palette Enforcement

```yaml
palette_enforcement:
  enabled: true
  mode: strict  # strict | warn | off

  extraction:
    method: k-means
    max_colors: 10

  validation:
    allowed_variance: 5  # deltaE units
    require_primary: true
    require_brand: true

  on_violation:
    action: reject  # reject | warn | auto-correct
```

### Style Anchor Matching

```yaml
style_anchor_matching:
  enabled: true

  embedding:
    model: clip-vit-large
    dimension: 768

  thresholds:
    pass: 0.10      # drift < 0.10 = pass
    warn: 0.15      # drift 0.10-0.15 = warn
    repair: 0.25    # drift 0.15-0.25 = repair
    regenerate: 1.0 # drift > 0.25 = regenerate

  max_regenerate_loops: 3
```

---

## Configuration

### MCP Configuration

```yaml
mcp:
  assets:
    enabled: true

    providers:
      nanobanana:
        enabled: true
        api_base: "https://api.nanobanana.io/v2"
        models:
          - nanobanana-icon-v2
          - nanobanana-logo-v1
          - nanobanana-hero-v1
          - nanobanana-illustration-v1
          - nanobanana-social-v1
          - nanobanana-product-v1
          - nanobanana-banner-v1
        priority: 1
        primary: true

      replicate:
        enabled: true
        api_base: "https://api.replicate.com/v1"
        models:
          - sdxl-1.0
          - flux-schnell
          - real-esrgan
        priority: 2
        fallback: true

      runpod:
        enabled: true
        api_base: "https://api.runpod.ai/v2"
        models:
          - sdxl-comfy
        priority: 3
        fallback: true

      local:
        enabled: false
        endpoint: "http://comfyui.internal:8188"
        priority: 4

    registry:
      backend: s3
      bucket: itqahn-asset-registry
      cdn_url: "https://assets.itqahn.io"

    design_os:
      enforce: true
      default_version: "1.2.0"
      style_anchors_path: "design-os/style-anchors/"

    rate_limits:
      generate:
        per_minute: 10
        per_hour: 100
      transform:
        per_minute: 30
        per_hour: 500

    cost_limits:
      per_workflow:
        max_usd: 5.00
      per_tenant_daily:
        max_usd: 100.00

    cache:
      enabled: true
      backend: redis
      ttl_hours: 24
```

### Allowlist Entry

```yaml
roles:
  asset-generator:
    mcps:
      assets:
        operations:
          - asset.generate
          - asset.edit
          - asset.bgremove
          - asset.upscale
          - asset.vectorize
          - asset.crop
          - asset.convert
          - asset.lint
          - asset.drift
          - registry.store
          - registry.get
          - registry.list
          - registry.search
        constraints:
          providers: ["replicate", "runpod"]
          max_resolution: 4096
          max_generations_per_request: 4
          require_style_anchor: true
          require_design_os_version: true

  design-guardian:
    mcps:
      assets:
        operations:
          - asset.lint
          - asset.drift
          - registry.get
          - registry.list
          - registry.search
        constraints:
          read_only: true

  frontend-builder:
    mcps:
      assets:
        operations:
          - registry.get
          - registry.list
          - registry.search
        constraints:
          read_only: true
          namespaces: ["$tenant/*"]
```

---

## Cost Management

### Token Budget Enforcement

```yaml
cost_enforcement:
  enabled: true

  budgets:
    per_generation:
      max_usd: 0.50
      warn_at: 0.25

    per_workflow:
      max_usd: 5.00
      warn_at: 3.00
      pause_at: 4.50

    per_tenant_daily:
      max_usd: 100.00
      warn_at: 75.00
      pause_at: 95.00

  circuit_breaker:
    enabled: true
    trigger: budget_exceeded
    action: pause_workflow
    notify: ["finops-team", "workflow-owner"]
```

### Cost Tracking

Each operation returns cost information:

```json
{
  "cost": {
    "operation_usd": 0.02,
    "workflow_total_usd": 0.15,
    "tenant_daily_usd": 12.50,
    "budget_remaining_usd": 4.85
  }
}
```

---

## Rate Limiting

### Per-Operation Limits

| Operation | Per Agent | Per Workflow | Per Tenant |
|-----------|-----------|--------------|------------|
| generate | 10/min | 50/hour | 500/day |
| edit | 15/min | 75/hour | 750/day |
| transform | 30/min | 150/hour | 1500/day |
| lint | 100/min | 500/hour | 5000/day |
| registry | 200/min | 1000/hour | 10000/day |

### Rate Limit Response

```json
{
  "error": "RATE_LIMITED",
  "message": "Rate limit exceeded for asset.generate",
  "retry_after_seconds": 45,
  "limits": {
    "limit": 10,
    "remaining": 0,
    "reset_at": "2026-01-06T12:01:00Z"
  }
}
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `ASSET_GENERATION_FAILED` | Provider failed to generate | Retry with different seed |
| `ASSET_VALIDATION_FAILED` | Asset failed Design OS validation | Review violations, adjust prompt |
| `ASSET_DRIFT_EXCEEDED` | Drift above threshold | Regenerate or adjust style anchor |
| `ASSET_NOT_FOUND` | Asset ID doesn't exist | Check ID |
| `PROVIDER_UNAVAILABLE` | Generation provider down | Fallback to alternate provider |
| `PROVIDER_RATE_LIMITED` | Provider rate limit hit | Back off |
| `BUDGET_EXCEEDED` | Cost budget exceeded | Request budget extension |
| `PALETTE_VIOLATION` | Colors outside Design OS palette | Use Design OS colors |
| `STYLE_ANCHOR_MISSING` | Required style anchor not found | Provide valid anchor |
| `REGISTRY_CONFLICT` | Asset version already exists | Bump version |

### Retry Configuration

```yaml
assets:
  retry:
    max_attempts: 3
    initial_delay_ms: 2000
    max_delay_ms: 30000
    retry_on:
      - PROVIDER_UNAVAILABLE
      - PROVIDER_RATE_LIMITED
      - ASSET_GENERATION_FAILED

    no_retry_on:
      - BUDGET_EXCEEDED
      - PALETTE_VIOLATION
      - STYLE_ANCHOR_MISSING
```

### Fallback Behavior

```yaml
assets:
  fallback:
    provider_failover:
      enabled: true
      order: ["nanobanana", "replicate", "runpod", "local"]
      # NanoBanana is primary; fallback to Replicate/RunPod if unavailable

    on_validation_fail:
      max_regenerations: 3
      adjust_prompt: true

    on_drift_exceed:
      action: repair_first
      repair_attempts: 2
      then: regenerate
```

---

## Security Considerations

### Prompt Injection Defense

All prompts are sanitized before sending to providers:

```yaml
security:
  prompt_sanitization:
    enabled: true
    rules:
      - strip_system_prompts
      - remove_injection_patterns
      - enforce_content_policy

    blocked_patterns:
      - "ignore previous"
      - "system:"
      - "jailbreak"
```

### Provider Isolation

Providers are isolated from sensitive data:

```yaml
security:
  provider_isolation:
    no_tenant_data_in_prompts: true
    strip_metadata_before_send: true
    use_presigned_urls: true
    presigned_url_ttl_seconds: 300
```

### License Compliance

Generated assets are checked for license issues:

```yaml
security:
  license_check:
    enabled: true
    check_model_licenses: true
    require_commercial_license: true
    blocked_models:
      - "model-with-nc-license"
```

### Content Policy

```yaml
security:
  content_policy:
    nsfw_filter: true
    violence_filter: true
    pii_detection: true
    brand_impersonation_check: true
```

---

## Audit Trail

### Operation Logging

Every operation is logged:

```json
{
  "timestamp": "2026-01-06T12:00:00Z",
  "mcp": "assets",
  "operation": "asset.generate",
  "agent_id": "asset-generator",
  "workflow_id": "wf-xyz789",
  "tenant_id": "tenant-acme",
  "request": {
    "asset_type": "app-icon",
    "style_anchor": "icons/modern-flat",
    "design_os_version": "1.2.0"
  },
  "result": {
    "status": "success",
    "asset_id": "ast-abc123",
    "validation_passed": true,
    "drift_score": 0.08
  },
  "cost": {
    "usd": 0.02
  },
  "provider": {
    "name": "replicate",
    "model": "sdxl-1.0",
    "duration_ms": 4500
  }
}
```

### Evidence Generation

Asset operations contribute to Evidence Pack:

```json
{
  "asset_evidence": {
    "asset_id": "ast-abc123",
    "workflow_id": "wf-xyz789",
    "generation": {
      "prompt_hash": "sha256:abc...",
      "model": "sdxl-1.0",
      "seed": 42,
      "timestamp": "2026-01-06T12:00:00Z"
    },
    "validation": {
      "design_os_version": "1.2.0",
      "style_anchor": "icons/modern-flat",
      "drift_score": 0.08,
      "palette_compliant": true,
      "lint_passed": true
    },
    "signatures": {
      "generation": "sigstore://...",
      "validation": "sigstore://..."
    }
  }
}
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `assets_mcp_requests_total` | Total requests by operation |
| `assets_mcp_latency` | Request latency |
| `assets_generation_duration` | Generation time |
| `assets_generation_cost_usd` | Cost per generation |
| `assets_validation_pass_rate` | % passing Design OS validation |
| `assets_drift_score` | Histogram of drift scores |
| `assets_regeneration_count` | Regenerations due to validation |
| `assets_registry_size_bytes` | Total registry size |
| `assets_budget_utilization` | Budget usage percentage |

### Dashboards

| Dashboard | Purpose |
|-----------|---------|
| Asset Factory Overview | Generation volume, success rates |
| Cost Analytics | Spend by tenant, workflow, provider |
| Quality Metrics | Drift scores, validation pass rates |
| Provider Health | Provider latency, availability |

### Alerts

```yaml
alerts:
  - name: assets_provider_down
    condition: up{job="assets-mcp"} == 0
    severity: critical

  - name: assets_high_cost
    condition: sum(assets_generation_cost_usd) > 50
    for: 1h
    severity: warning

  - name: assets_low_validation_rate
    condition: assets_validation_pass_rate < 0.8
    for: 15m
    severity: warning

  - name: assets_drift_spike
    condition: histogram_quantile(0.95, assets_drift_score) > 0.2
    for: 10m
    severity: warning
```

---

## Multi-Tenancy

### Tenant Isolation

```yaml
multi_tenancy:
  enabled: true

  isolation:
    registry_namespace: "tenant-{tenant_id}/"
    style_anchors: "tenant-{tenant_id}/style-anchors/"
    cost_tracking: per_tenant

  defaults:
    inherit_baseline_anchors: true
    allow_custom_anchors: true
```

### Enterprise Mode

```yaml
enterprise_mode:
  enabled: false

  when_enabled:
    private_providers: true
    custom_models: true
    dedicated_registry: true
    custom_cost_limits: true
```

---

## Related Documents

- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification with NanoBanana
- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/04-security/prompt-injection-defense.md` — Asset prompt hardening
- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/07-integrations/mcp/mcp-nanobanana.md` — NanoBanana MCP specification
- `docs/07-integrations/mcp/mcp-security-model.md` — MCP security
- `docs/05-compliance/evidence-pack.md` — Evidence requirements

---

**Version**: 2.3.0 | **Date**: 2026-01-08
