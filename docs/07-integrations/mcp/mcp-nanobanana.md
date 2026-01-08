# MCP NanoBanana

NanoBanana is the **primary image generation provider** for Itqahn Asset Factory. This MCP specification defines the secure, auditable interface for generating 2D assets via NanoBanana's API.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NANOBANANA MCP ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────────────────────────────────────────────────┐    │
│  │  Agent  │───▶│                 MCP SERVER                          │    │
│  │  (No    │    │  ┌────────────────────────────────────────────┐    │    │
│  │  creds) │    │  │           VAULT SECRET INJECTION            │    │    │
│  └─────────┘    │  │  API Key loaded at startup, never exposed  │    │    │
│                 │  └───────────────────────┬────────────────────┘    │    │
│                 │                          │                          │    │
│                 │  ┌───────────────────────▼────────────────────┐    │    │
│                 │  │              NANOBANANA API                 │    │    │
│                 │  │  https://api.nanobanana.io/v2               │    │    │
│                 │  │  • generate  • refine  • upscale           │    │    │
│                 │  │  • vectorize • bgremove • style_transfer   │    │    │
│                 │  └───────────────────────┬────────────────────┘    │    │
│                 │                          │                          │    │
│                 └──────────────────────────┼──────────────────────────┘    │
│                                            │                               │
│  ┌─────────────────────────────────────────▼───────────────────────────┐  │
│  │                        RESPONSE PIPELINE                             │  │
│  │  Raw Output → Content Moderation → Style Validation → Lint → Return │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Model

### API Key Handling

NanoBanana API credentials MUST follow these security requirements:

| Requirement | Enforcement |
|-------------|-------------|
| **Vault Storage** | API key stored in Vault at `kv/itqahn/services/nanobanana` |
| **Runtime Injection** | Key injected as environment variable at MCP server startup |
| **Agent Isolation** | Agents NEVER have access to API credentials |
| **Audit Logging** | All API calls logged with run_id, redacting credentials |
| **Rotation Support** | Keys rotatable without agent restart |

### Secret Injection Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     RUNTIME SECRET INJECTION                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Operator Mode starts new Run                                            │
│           │                                                                 │
│           ▼                                                                 │
│  2. Platform fetches NanoBanana credentials from Vault                     │
│     vault_path: kv/itqahn/tenants/{tenant_id}/nanobanana                   │
│           │                                                                 │
│           ▼                                                                 │
│  3. MCP Server process spawned with credentials as env vars                │
│     NANOBANANA_API_KEY=nb_prod_xxxx (process-only, not logged)            │
│     NANOBANANA_ENDPOINT=https://api.nanobanana.io/v2                       │
│           │                                                                 │
│           ▼                                                                 │
│  4. Agent calls MCP tool (no credentials in request)                       │
│     { "tool": "nanobanana.generate", "params": {...} }                     │
│           │                                                                 │
│           ▼                                                                 │
│  5. MCP Server adds auth header internally                                 │
│     Authorization: Bearer ${NANOBANANA_API_KEY}                            │
│           │                                                                 │
│           ▼                                                                 │
│  6. Response returned to agent (credentials never exposed)                 │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Vault Secret Schema

```yaml
# Vault path: kv/itqahn/services/nanobanana
secret:
  api_key: "nb_prod_xxxxxxxxxxxxxxxxxxxx"
  api_endpoint: "https://api.nanobanana.io/v2"
  rate_limit_tier: "enterprise"
  allowed_models:
    - "nanobanana-icon-v2"
    - "nanobanana-logo-v1"
    - "nanobanana-hero-v1"
    - "nanobanana-illustration-v1"
    - "nanobanana-social-v1"
    - "nanobanana-product-v1"
    - "nanobanana-banner-v1"
  content_moderation: true
  nsfw_threshold: 0.05
  violence_threshold: 0.05
```

---

## Capabilities

### Supported Operations

| Operation | Description | Risk Level | Rate Limit |
|-----------|-------------|------------|------------|
| `nanobanana.generate` | Generate new image from prompt | High | 10/min |
| `nanobanana.refine` | Refine existing image | High | 15/min |
| `nanobanana.upscale` | Increase image resolution | Medium | 20/min |
| `nanobanana.background_remove` | Remove background | Medium | 30/min |
| `nanobanana.style_transfer` | Apply style anchor | Medium | 15/min |
| `nanobanana.vectorize` | Convert raster to SVG | Medium | 20/min |
| `nanobanana.moderate` | Check content policy | Low | 100/min |

### Supported Models

| Model | Asset Types | Resolution | Description |
|-------|-------------|------------|-------------|
| `nanobanana-icon-v2` | App Icon, UI Icons | Up to 1024x1024 | Optimized for iconography |
| `nanobanana-logo-v1` | Logo, Brand marks | Up to 2048x2048 | Brand-aware generation |
| `nanobanana-hero-v1` | Hero Images | Up to 4096x2048 | High-res marketing images |
| `nanobanana-illustration-v1` | Illustrations | Up to 2048x2048 | Style-consistent illustrations |
| `nanobanana-social-v1` | OG Images, Social | 1200x630 fixed | Social media optimized |
| `nanobanana-product-v1` | Product Photos | Up to 2048x2048 | E-commerce focused |
| `nanobanana-banner-v1` | Banners, Ads | Variable | Marketing creatives |

---

## Operations

### Generate

Generate a new image with Design OS constraints:

**Request:**
```json
{
  "tool": "nanobanana.generate",
  "params": {
    "prompt": "Modern minimalist app icon for task management, blue gradient",
    "negative_prompt": "text, watermark, blurry, complex, photo-realistic",
    "model": "nanobanana-icon-v2",
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0",
    "output": {
      "format": "png",
      "width": 1024,
      "height": 1024
    },
    "candidates": 4,
    "seed": null
  }
}
```

**Response:**
```json
{
  "status": "success",
  "candidates": [
    {
      "candidate_id": "cand-001",
      "url": "s3://assets/generated/run-xxx/cand-001.png",
      "format": "png",
      "width": 1024,
      "height": 1024,
      "digest": "sha256:abc123...",
      "style_drift_score": 0.08,
      "palette_compliant": true,
      "moderation": {
        "nsfw_score": 0.001,
        "violence_score": 0.000,
        "passed": true
      }
    }
  ],
  "selected_candidate": "cand-001",
  "metadata": {
    "model": "nanobanana-icon-v2",
    "generation_time_ms": 3500,
    "cost_usd": 0.02,
    "seed": 42
  },
  "provenance": {
    "run_id": "run-01J5ABCD...",
    "workflow_id": "wf-xyz789",
    "agent_id": "asset-generator",
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

### Refine

Refine an existing image:

**Request:**
```json
{
  "tool": "nanobanana.refine",
  "params": {
    "source": "s3://assets/generated/run-xxx/cand-001.png",
    "refinement_prompt": "Make the gradient more subtle, increase contrast",
    "preserve_structure": 0.8,
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": {
    "url": "s3://assets/refined/run-xxx/refined-001.png",
    "format": "png",
    "digest": "sha256:def456...",
    "style_drift_score": 0.05
  },
  "lineage": {
    "parent_asset": "s3://assets/generated/run-xxx/cand-001.png",
    "operation": "refine"
  }
}
```

### Upscale

Increase image resolution:

**Request:**
```json
{
  "tool": "nanobanana.upscale",
  "params": {
    "source": "s3://assets/generated/run-xxx/cand-001.png",
    "scale_factor": 4,
    "preserve_quality": true,
    "denoise": 0.3
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": {
    "url": "s3://assets/upscaled/run-xxx/upscaled-001.png",
    "format": "png",
    "width": 4096,
    "height": 4096,
    "digest": "sha256:ghi789..."
  },
  "lineage": {
    "parent_asset": "s3://assets/generated/run-xxx/cand-001.png",
    "operation": "upscale",
    "scale_factor": 4
  }
}
```

### Background Remove

Remove background from image:

**Request:**
```json
{
  "tool": "nanobanana.background_remove",
  "params": {
    "source": "s3://assets/generated/run-xxx/product.png",
    "edge_refinement": "high",
    "output_format": "png"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": {
    "url": "s3://assets/processed/run-xxx/nobg-001.png",
    "format": "png",
    "has_alpha": true,
    "digest": "sha256:jkl012..."
  }
}
```

### Style Transfer

Apply style anchor to existing image:

**Request:**
```json
{
  "tool": "nanobanana.style_transfer",
  "params": {
    "source": "s3://assets/uploaded/reference.png",
    "style_anchor": "style-anchors/brand-primary.json",
    "strength": 0.7,
    "preserve_content": 0.8,
    "design_os_version": "1.2.0"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": {
    "url": "s3://assets/styled/run-xxx/styled-001.png",
    "format": "png",
    "style_drift_score": 0.06,
    "digest": "sha256:mno345..."
  }
}
```

### Vectorize

Convert raster to SVG:

**Request:**
```json
{
  "tool": "nanobanana.vectorize",
  "params": {
    "source": "s3://assets/generated/run-xxx/icon.png",
    "color_mode": "palette",
    "palette_source": "design-os",
    "design_os_version": "1.2.0",
    "simplify": 0.5,
    "corner_threshold": 60
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": {
    "url": "s3://assets/vector/run-xxx/icon.svg",
    "format": "svg",
    "paths": 24,
    "colors": 5,
    "palette_compliant": true,
    "digest": "sha256:pqr678..."
  }
}
```

---

## Content Moderation

All generated outputs MUST pass content moderation before returning to agents:

### Moderation Checks

| Check | Threshold | Action on Fail |
|-------|-----------|----------------|
| **NSFW** | > 0.05 | Reject, log, alert |
| **Violence** | > 0.05 | Reject, log, alert |
| **Trademark** | Detected | Reject, escalate |
| **Photo-realistic faces** | Detected (if forbidden) | Reject, regenerate |
| **Copyright** | Detected | Reject, escalate |

### Moderation Response

When content moderation fails:

```json
{
  "status": "moderation_failed",
  "error": {
    "code": "CONTENT_POLICY_VIOLATION",
    "reason": "NSFW content detected",
    "score": 0.12,
    "threshold": 0.05
  },
  "action": "request_rejected",
  "logged": true,
  "alert_sent": true
}
```

---

## Design OS Integration

### Constraint Enforcement

All generation operations enforce Design OS constraints:

```yaml
design_os_enforcement:
  enabled: true

  palette:
    mode: strict
    source: "design-os/tokens.json"
    allowed_variance_delta_e: 5

  style_anchor:
    required: true
    similarity_threshold: 0.85
    drift_thresholds:
      pass: 0.10
      warn: 0.15
      fail: 0.25

  forbidden_elements:
    check: true
    list:
      - "photo-realistic-faces"
      - "text-in-icons"
      - "complex-gradients"
```

### Prompt Augmentation

Prompts are automatically augmented with Design OS constraints:

```python
def augment_prompt(prompt: str, spec: AssetSpec) -> str:
    """Augment user prompt with Design OS constraints."""

    # Load style anchor
    anchor = load_style_anchor(spec.style_anchor)

    # Load palette tokens
    palette = load_design_os_palette(spec.design_os_version)

    # Build augmented prompt
    augmented = f"""
    {prompt}

    Style constraints:
    - Follow style anchor: {anchor.description}
    - Color palette: {', '.join(palette.primary_colors)}
    - Forbidden: {', '.join(anchor.forbidden)}

    Quality requirements:
    - Clean, professional output
    - No artifacts or noise
    - Consistent with brand guidelines
    """

    # Add negative prompt
    negative = spec.negative_prompt or ""
    negative += f" {' '.join(anchor.forbidden)}"

    return augmented, negative
```

---

## Rate Limiting

### Per-Tier Limits

| Tier | Requests/min | Requests/hour | Max Resolution | Concurrent |
|------|--------------|---------------|----------------|------------|
| **Standard** | 30 | 500 | 2048x2048 | 4 |
| **Professional** | 60 | 2000 | 4096x4096 | 8 |
| **Enterprise** | 120 | 10000 | 8192x8192 | 16 |

### Rate Limit Response

```json
{
  "status": "rate_limited",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for nanobanana.generate",
    "retry_after_seconds": 45,
    "limits": {
      "limit": 30,
      "remaining": 0,
      "reset_at": "2026-01-08T12:01:00Z"
    }
  }
}
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `NANOBANANA_UNAVAILABLE` | API service down | Fallback to alternate provider |
| `NANOBANANA_RATE_LIMITED` | Rate limit exceeded | Exponential backoff |
| `NANOBANANA_TIMEOUT` | Request timeout (>60s) | Retry with smaller resolution |
| `NANOBANANA_INVALID_MODEL` | Unknown model requested | Check allowed models |
| `NANOBANANA_QUOTA_EXHAUSTED` | Account quota exceeded | Request budget approval |
| `NANOBANANA_AUTH_FAILED` | Invalid API key | Kill switch, rotate credentials |
| `CONTENT_POLICY_VIOLATION` | Moderation failed | Rewrite prompt, regenerate |
| `STYLE_DRIFT_EXCEEDED` | Drift above threshold | Deterministic repair or regenerate |
| `PALETTE_VIOLATION` | Colors outside Design OS | Auto color-correct |

### Retry Configuration

```yaml
nanobanana:
  retry:
    max_attempts: 3
    initial_delay_ms: 2000
    max_delay_ms: 30000
    exponential_base: 2

    retry_on:
      - NANOBANANA_UNAVAILABLE
      - NANOBANANA_RATE_LIMITED
      - NANOBANANA_TIMEOUT

    no_retry_on:
      - NANOBANANA_AUTH_FAILED
      - NANOBANANA_QUOTA_EXHAUSTED
      - CONTENT_POLICY_VIOLATION
```

### Fallback Behavior

```yaml
nanobanana:
  fallback:
    enabled: true
    providers:
      - replicate
      - runpod

    trigger_on:
      - NANOBANANA_UNAVAILABLE
      - consecutive_failures: 3

    notify:
      - platform-team
      - asset-factory-oncall
```

---

## Cost Management

### Pricing Model

| Operation | Cost per Request |
|-----------|-----------------|
| `generate` (1024x1024) | $0.02 |
| `generate` (2048x2048) | $0.08 |
| `generate` (4096x4096) | $0.32 |
| `refine` | $0.015 |
| `upscale` (4x) | $0.04 |
| `background_remove` | $0.01 |
| `style_transfer` | $0.02 |
| `vectorize` | $0.015 |
| `moderate` | $0.001 |

### Budget Enforcement

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

### Cost Response

Every response includes cost information:

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

## Audit Trail

### Operation Logging

Every NanoBanana operation is logged:

```json
{
  "timestamp": "2026-01-08T12:00:00Z",
  "mcp": "nanobanana",
  "operation": "generate",
  "run_id": "run-01J5ABCD...",
  "workflow_id": "wf-xyz789",
  "tenant_id": "tenant-acme",
  "agent_id": "asset-generator",
  "request": {
    "model": "nanobanana-icon-v2",
    "prompt_hash": "sha256:...",
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0",
    "dimensions": "1024x1024"
  },
  "result": {
    "status": "success",
    "candidates_generated": 4,
    "selected_candidate": "cand-001",
    "style_drift_score": 0.08,
    "moderation_passed": true
  },
  "cost": {
    "usd": 0.02
  },
  "duration_ms": 3500
}
```

### Evidence Pack Contribution

NanoBanana operations contribute to the Evidence Pack:

```json
{
  "nanobanana_evidence": {
    "request_id": "nb-req-abc123",
    "run_id": "run-01J5ABCD...",
    "timestamp": "2026-01-08T12:00:00Z",
    "operation": "generate",
    "model": "nanobanana-icon-v2",
    "prompt_hash": "sha256:...",
    "prompt_sanitized": true,
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0",
    "generation": {
      "candidates": 4,
      "selected": 2,
      "seed": 42
    },
    "validation": {
      "style_drift_score": 0.08,
      "palette_compliant": true,
      "moderation": {
        "nsfw_score": 0.001,
        "violence_score": 0.000,
        "trademark_check": "passed"
      }
    },
    "output": {
      "digest": "sha256:...",
      "format": "png",
      "dimensions": "1024x1024"
    },
    "cost_usd": 0.02,
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
| `nanobanana_requests_total` | Total requests by operation |
| `nanobanana_request_duration_seconds` | Request latency |
| `nanobanana_generation_cost_usd` | Cost per generation |
| `nanobanana_style_drift_score` | Histogram of drift scores |
| `nanobanana_moderation_failures` | Content moderation failures |
| `nanobanana_rate_limit_hits` | Rate limit violations |
| `nanobanana_api_errors` | API errors by type |

### Alerts

```yaml
alerts:
  - name: nanobanana_unavailable
    condition: up{job="nanobanana-mcp"} == 0
    for: 5m
    severity: critical
    action: failover_to_replicate

  - name: nanobanana_high_error_rate
    condition: rate(nanobanana_api_errors[5m]) / rate(nanobanana_requests_total[5m]) > 0.1
    for: 10m
    severity: warning

  - name: nanobanana_moderation_spike
    condition: rate(nanobanana_moderation_failures[1h]) > 10
    for: 5m
    severity: warning
    action: security_review

  - name: nanobanana_budget_exceeded
    condition: sum(nanobanana_generation_cost_usd{tenant_id="$tenant"}) > 95
    severity: warning
    action: pause_tenant_workflows
```

---

## Configuration

### MCP Server Configuration

```yaml
mcp:
  nanobanana:
    enabled: true

    api:
      base_url: "https://api.nanobanana.io/v2"
      timeout_seconds: 60
      retry:
        max_attempts: 3
        backoff_multiplier: 2

    credentials:
      source: vault
      vault_path: "kv/itqahn/services/nanobanana"
      rotation_enabled: true

    models:
      allowed:
        - nanobanana-icon-v2
        - nanobanana-logo-v1
        - nanobanana-hero-v1
        - nanobanana-illustration-v1
        - nanobanana-social-v1
        - nanobanana-product-v1
        - nanobanana-banner-v1

    moderation:
      enabled: true
      nsfw_threshold: 0.05
      violence_threshold: 0.05
      trademark_check: true

    design_os:
      enforce: true
      default_version: "1.2.0"
      style_anchors_path: "design-os/style-anchors/"

    rate_limits:
      per_minute: 30
      per_hour: 500
      concurrent: 4

    cost_limits:
      per_generation_usd: 0.50
      per_workflow_usd: 5.00
      per_tenant_daily_usd: 100.00

    fallback:
      enabled: true
      providers: ["replicate", "runpod"]
```

### Agent Allowlist

```yaml
roles:
  asset-generator:
    mcps:
      nanobanana:
        operations:
          - nanobanana.generate
          - nanobanana.refine
          - nanobanana.upscale
          - nanobanana.background_remove
          - nanobanana.style_transfer
          - nanobanana.vectorize
        constraints:
          max_resolution: 4096
          max_candidates: 4
          require_style_anchor: true
          require_design_os_version: true

  design-guardian:
    mcps:
      nanobanana:
        operations:
          - nanobanana.moderate
        constraints:
          read_only: true
```

---

## Kill Switch Integration

### Kill Switch Triggers

| Trigger | Detection | Action |
|---------|-----------|--------|
| API key compromised | 401/403 response | Kill switch → Rotate credentials |
| Repeated moderation failures | >10 in 1 hour | Pause tenant → Security review |
| Budget exceeded | 100% budget used | Pause workflow → Approval required |
| Credential leak detected | Security scan | Kill switch → Full credential rotation |

### Kill Switch Protocol

When kill switch is activated for NanoBanana:

1. **Terminate** all active NanoBanana requests
2. **Revoke** current API credentials via Vault
3. **Pause** all workflows using NanoBanana MCP
4. **Alert** security team and platform oncall
5. **Log** incident with full context
6. **Rotate** credentials before resuming

---

## Related Documents

- `docs/03-platform/asset-factory-imageops.md` — Asset Factory with NanoBanana integration
- `docs/04-security/prompt-injection-defense.md` — Asset prompt hardening
- `docs/07-integrations/mcp/mcp-overview.md` — MCP basics
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/06-operations/incident-response.md` — Kill switch incident protocol

---

**Version**: 1.0.0 | **Date**: 2026-01-08
