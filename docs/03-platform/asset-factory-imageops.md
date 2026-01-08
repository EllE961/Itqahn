# Asset Factory (ImageOps)

Asset Factory is the **durable, governed image generation and manipulation pipeline** for Itqahn. It produces platform-correct visual assets—icons, logos, hero images, illustrations, banners—without human editing, governed by Design OS and auditable via Evidence Pack.

**Design OS governs all assets.** No asset may be generated or modified without compliance with the active Design OS palette, typography, and style constraints.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ASSET FACTORY ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                         DESIGN OS GOVERNANCE                        │     │
│  │   tokens.json │ components.json │ style-anchors/ │ brand-rules/   │     │
│  └───────────────────────────────┬────────────────────────────────────┘     │
│                                  │                                          │
│                                  ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                         ASSET REQUEST                               │     │
│  │   asset-spec.json (type, constraints, platform targets)            │     │
│  └───────────────────────────────┬────────────────────────────────────┘     │
│                                  │                                          │
│                                  ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                    TEMPORAL WORKFLOW (Durable)                      │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │     │
│  │  │ Generate │→ │  Refine  │→ │   Lint   │→ │ Platform │           │     │
│  │  │ (MCP)    │  │  (MCP)   │  │  (MCP)   │  │ Variants │           │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │     │
│  └───────────────────────────────┬────────────────────────────────────┘     │
│                                  │                                          │
│                                  ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                         ASSET OUTPUTS                               │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │     │
│  │  │   Web      │  │    iOS     │  │  Android   │  │ Marketing  │   │     │
│  │  │  Assets    │  │   Assets   │  │  Assets    │  │  Assets    │   │     │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │     │
│  └───────────────────────────────┬────────────────────────────────────┘     │
│                                  │                                          │
│                                  ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                      GIT + EVIDENCE PACK                            │     │
│  │   asset-manifest.json │ asset-evidence.json │ lint-reports/        │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

| Principle | Enforcement |
|-----------|-------------|
| **Design OS governs all assets** | Style anchors, palette rules, brand constraints enforced |
| **Assets are production artifacts with evidence** | Provenance, manifests, lint reports in Evidence Pack |
| **No human Photoshop** | Automation-first; human override requires risk-based approval |
| **Deterministic repair before regeneration** | Reduces cost and instability |
| **Asset drift is a release blocker** | Style drift detection blocks merges |
| **Platform-correct by default** | Auto-generate all density/size variants |

---

## Supported Asset Types

### Production Assets

| Asset Type | Description | Platforms | Formats |
|------------|-------------|-----------|---------|
| **App Icon** | Application launcher icon | iOS, Android, Web | PNG, SVG, ICNS |
| **UI Icons** | Interface icons (sets) | All | SVG, PNG |
| **Logo** | Brand logo variants | All | SVG, PNG, WebP |
| **Hero Image** | Landing page headers | Web, Marketing | WebP, AVIF, PNG |
| **Illustration** | Custom illustrations | All | SVG, PNG |
| **OG Image** | Social media preview | Web | PNG (1200×630) |
| **Product Photo** | Packshots, mockups | Marketing, Web | PNG, WebP |
| **Marketing Banner** | Ad creatives, banners | Marketing | PNG, WebP, GIF |
| **Favicon** | Browser favicon | Web | ICO, SVG, PNG |

### Not In Scope

| Category | Reason |
|----------|--------|
| 3D assets | Requires specialized pipeline (future roadmap) |
| Long-form video | Specialized editing tools (future roadmap) |
| Copyrighted character replication | Legal/IP constraints |
| User-uploaded content (raw) | Requires separate moderation pipeline |

---

## Asset Specification Schema

### asset-spec.json

**REQUIRED** for every asset request. Validated before workflow starts.

```json
{
  "$schema": "https://itqahn.io/schemas/asset-factory/spec/v1",
  "version": "1.0.0",
  "metadata": {
    "request_id": "asset-req-abc123",
    "tenant_id": "tenant-xyz",
    "workflow_id": "wf-789",
    "requested_by": "spiffe://itqahn.io/agent/ui-composer/tenant-xyz/wf-789",
    "timestamp": "2026-01-06T12:00:00Z"
  },
  "asset": {
    "type": "app-icon",
    "name": "my-app-icon",
    "description": "Main application icon with brand gradient",
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0"
  },
  "constraints": {
    "palette": {
      "source": "design-os",
      "allowed_tokens": ["color.brand.*", "color.semantic.*"]
    },
    "typography": {
      "allow_text": false
    },
    "style": {
      "anchor_similarity_threshold": 0.85,
      "forbidden_elements": ["text", "photo-realistic-faces"]
    }
  },
  "platforms": {
    "ios": {
      "enabled": true,
      "sizes": [1024, 180, 167, 152, 120, 87, 80, 76, 60, 58, 40, 29, 20]
    },
    "android": {
      "enabled": true,
      "adaptive_icon": true,
      "densities": ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
    },
    "web": {
      "enabled": true,
      "sizes": [512, 192, 180, 152, 144, 128, 96, 72, 48, 32, 16],
      "favicon": true
    }
  },
  "generation": {
    "max_candidates": 4,
    "max_regenerate_loops": 3,
    "prefer_deterministic_repair": true,
    "budget_tokens": 50000
  },
  "approval": {
    "required": true,
    "approvers": ["design-director", "brand-manager"]
  }
}
```

---

## Asset Manifest

### asset-manifest.json

**REQUIRED** output. Documents all generated assets with hashes.

```json
{
  "$schema": "https://itqahn.io/schemas/asset-factory/manifest/v1",
  "version": "1.0.0",
  "metadata": {
    "spec_id": "asset-req-abc123",
    "workflow_id": "wf-789",
    "generated_at": "2026-01-06T12:05:00Z",
    "design_os_version": "1.2.0",
    "asset_factory_version": "2.1.0"
  },
  "assets": [
    {
      "name": "my-app-icon",
      "type": "app-icon",
      "platform": "ios",
      "variant": "1024x1024",
      "path": "assets/tenant-xyz/ui/icons/my-app-icon/ios/icon-1024.png",
      "format": "png",
      "dimensions": { "width": 1024, "height": 1024 },
      "size_bytes": 45678,
      "digest": "sha256:abc123...",
      "color_profile": "sRGB"
    },
    {
      "name": "my-app-icon",
      "type": "app-icon",
      "platform": "android",
      "variant": "xxxhdpi-foreground",
      "path": "assets/tenant-xyz/ui/icons/my-app-icon/android/ic_launcher_foreground.png",
      "format": "png",
      "dimensions": { "width": 432, "height": 432 },
      "size_bytes": 12345,
      "digest": "sha256:def456...",
      "adaptive_layer": "foreground"
    }
  ],
  "source_assets": [],
  "license_metadata": {
    "generator": "asset-factory",
    "model_license": "proprietary",
    "output_license": "tenant-owned",
    "third_party_sources": []
  },
  "totals": {
    "asset_count": 45,
    "total_size_bytes": 1234567,
    "platforms": ["ios", "android", "web"]
  }
}
```

---

## Asset Evidence

### asset-evidence.json

**REQUIRED** for Evidence Pack. Proves how assets were generated.

```json
{
  "$schema": "https://itqahn.io/schemas/asset-factory/evidence/v1",
  "version": "1.0.0",
  "provenance": {
    "manifest_digest": "sha256:xyz789...",
    "spec_digest": "sha256:abc123...",
    "workflow_id": "wf-789",
    "temporal_run_id": "run-456"
  },
  "generation": {
    "generator_id": "mcp-assets-generate",
    "generator_version": "2.1.0",
    "model_version": "stable-diffusion-xl-1.0",
    "prompt_template_id": "pt-app-icon-v3",
    "seed": 42,
    "candidates_generated": 4,
    "candidate_selected": 2,
    "regeneration_loops": 0
  },
  "transforms": [
    {
      "operation": "background_removal",
      "tool_id": "mcp-assets-bgremove",
      "tool_version": "1.2.0",
      "input_digest": "sha256:input123...",
      "output_digest": "sha256:output456...",
      "deterministic": true
    },
    {
      "operation": "upscale",
      "tool_id": "mcp-assets-upscale",
      "tool_version": "1.1.0",
      "scale_factor": 4,
      "input_digest": "sha256:output456...",
      "output_digest": "sha256:final789...",
      "deterministic": true
    }
  ],
  "validation": {
    "lint_report_path": "lint-reports/my-app-icon-lint.json",
    "lint_status": "passed",
    "style_drift_score": 0.08,
    "style_drift_threshold": 0.15,
    "palette_compliance": true,
    "safe_area_compliance": true,
    "accessibility_check": "passed"
  },
  "approvals": [
    {
      "type": "design_review",
      "approver": "design-director",
      "timestamp": "2026-01-06T12:10:00Z",
      "attestation": "attestations/design-review.sig"
    }
  ]
}
```

---

## Canonical Artifact Locations

### Repository Structure

```
assets/
├── {tenant}/
│   ├── ui/
│   │   ├── icons/
│   │   │   └── {name}/
│   │   │       ├── ios/
│   │   │       │   ├── icon-1024.png
│   │   │       │   ├── icon-180.png
│   │   │       │   └── Contents.json
│   │   │       ├── android/
│   │   │       │   ├── mipmap-xxxhdpi/
│   │   │       │   ├── mipmap-xxhdpi/
│   │   │       │   └── ic_launcher.xml
│   │   │       └── web/
│   │   │           ├── icon-512.png
│   │   │           ├── icon-192.png
│   │   │           └── favicon.ico
│   │   └── illustrations/
│   │       └── {name}/
│   ├── marketing/
│   │   ├── banners/
│   │   ├── og-images/
│   │   └── product-photos/
│   └── brand/
│       ├── logos/
│       │   └── {variant}/
│       └── hero-images/
├── style-anchors/
│   ├── brand-primary.json
│   ├── brand-secondary.json
│   └── illustration-style.json
├── manifests/
│   └── {request-id}/
│       ├── asset-manifest.json
│       └── asset-evidence.json
└── lint-reports/
    └── {request-id}/
```

### Naming Conventions

| Rule | Example |
|------|---------|
| Kebab-case names | `my-app-icon`, `hero-landing-page` |
| Platform suffix | `icon-1024.png`, `ic_launcher_foreground.png` |
| Density suffix (Android) | `mipmap-xxxhdpi/` |
| Size suffix (Web) | `icon-512.png`, `icon-192.png` |
| Variant suffix | `logo-dark.svg`, `logo-light.svg` |

### Format Requirements

| Asset Type | Web | iOS | Android |
|------------|-----|-----|---------|
| **Icons** | SVG, PNG | PNG | PNG (adaptive XML) |
| **Logos** | SVG, WebP | PDF, PNG | SVG, PNG |
| **Hero Images** | WebP, AVIF | HEIC, PNG | WebP, PNG |
| **Illustrations** | SVG | PDF, PNG | SVG, PNG |
| **OG Images** | PNG (1200×630) | N/A | N/A |

---

## Design OS Integration

Asset Factory MUST consume and enforce Design OS constraints:

### Palette Rules

```json
// Design OS palette constraint
{
  "palette_rules": {
    "primary_colors": ["color.brand.primary", "color.brand.secondary"],
    "accent_colors": ["color.semantic.success", "color.semantic.warning"],
    "forbidden_colors": ["#FF0000", "#00FF00"],
    "max_colors": 6,
    "contrast_minimum": 4.5
  }
}
```

### Style Anchors

Style anchors define approved visual styles:

```json
// style-anchors/brand-primary.json
{
  "$schema": "https://itqahn.io/schemas/asset-factory/style-anchor/v1",
  "name": "brand-primary",
  "description": "Primary brand style for icons and illustrations",
  "style_embedding": "embeddings/brand-primary.npy",
  "reference_assets": [
    "assets/baseline/brand/logo-main.svg",
    "assets/baseline/ui/icons/reference-set/"
  ],
  "constraints": {
    "color_palette": ["color.brand.*"],
    "stroke_weight": { "min": 1.5, "max": 3.0 },
    "corner_radius": { "style": "rounded", "min": 4, "max": 16 },
    "fill_style": "gradient-allowed",
    "shadows": "subtle-only"
  },
  "forbidden": {
    "photo_realistic": true,
    "text_in_icons": true,
    "complex_gradients": true
  }
}
```

### Icon Grid Rules

```json
// Design OS icon geometry constraints
{
  "icon_grid": {
    "base_size": 24,
    "stroke_weight": 2,
    "corner_radius": 2,
    "safe_area_percent": 10,
    "keyline_shapes": ["circle", "square", "horizontal-rectangle", "vertical-rectangle"],
    "optical_correction": true
  }
}
```

---

## Workflow Execution

### Temporal Workflow Structure

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ASSET GENERATION WORKFLOW                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. VALIDATE                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │  • Parse asset-spec.json                                        │     │
│  │  • Validate schema                                              │     │
│  │  • Check Design OS version exists                               │     │
│  │  • Verify style anchor available                                │     │
│  │  • Check budget allocation                                      │     │
│  └───────────────────────────────────┬─────────────────────────────┘     │
│                                      │                                    │
│  2. GENERATE                         ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │  • Call mcp-assets-generate                                     │     │
│  │  • Apply style anchor constraints                               │     │
│  │  • Generate N candidates (max 4)                                │     │
│  │  • Score candidates against style anchor                        │     │
│  └───────────────────────────────────┬─────────────────────────────┘     │
│                                      │                                    │
│  3. REFINE (if needed)               ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │  • Deterministic repair preferred                               │     │
│  │  • Background removal (mcp-assets-bgremove)                     │     │
│  │  • Upscale if needed (mcp-assets-upscale)                       │     │
│  │  • Color correction to palette                                  │     │
│  └───────────────────────────────────┬─────────────────────────────┘     │
│                                      │                                    │
│  4. LINT                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │  • Call mcp-assets-lint                                         │     │
│  │  • Check format compliance                                      │     │
│  │  • Check size/dimension compliance                              │     │
│  │  • Check safe area compliance                                   │     │
│  │  • Check palette compliance                                     │     │
│  │  • Check style drift score                                      │     │
│  └───────────────────────────────────┬─────────────────────────────┘     │
│                                      │                                    │
│                          ┌───────────┴───────────┐                       │
│                          │ Lint passed?          │                       │
│                          └───────────┬───────────┘                       │
│                    No ◄──────────────┴──────────────► Yes                │
│                    │                                    │                 │
│                    ▼                                    ▼                 │
│  ┌────────────────────────┐              ┌────────────────────────┐      │
│  │ REPAIR or REGENERATE   │              │ 5. PLATFORM VARIANTS   │      │
│  │ (max 3 loops)          │              │                        │      │
│  │ └─► Back to Generate   │              │ • iOS asset catalog    │      │
│  └────────────────────────┘              │ • Android adaptive     │      │
│                                          │ • Web sizes + favicon  │      │
│                                          └───────────┬────────────┘      │
│                                                      │                    │
│  6. REGISTER + COMMIT                                ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │  • Generate asset-manifest.json                                 │     │
│  │  • Generate asset-evidence.json                                 │     │
│  │  • Register in mcp-assets-registry                              │     │
│  │  • Commit to Git (PR)                                           │     │
│  │  • Request approval if required                                 │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Dashboard Visibility

All workflow steps are visible in the Portal:

| Portal Section | Content |
|----------------|---------|
| **Asset Request UI** | Submit asset-spec via form |
| **Status Stream** | Real-time Temporal step progress |
| **Candidate Preview** | View generated candidates |
| **Approval Queue** | Approve/reject assets |
| **Asset Library** | Browse registered assets |
| **Where-Used** | Track asset usage in code |
| **Incident Page** | Failed generations, remediation |

---

## Enforcement Hooks

### CI Checks

All asset changes trigger these mandatory checks:

#### 1. Asset Spec Schema Validation

```yaml
- name: Asset Spec Validation
  run: |
    npx asset-factory-cli validate-spec \
      --spec assets/manifests/*/asset-spec.json \
      --schema https://itqahn.io/schemas/asset-factory/spec/v1 \
      --fail-on-error
```

**Blocks PR if spec is invalid.**

#### 2. Asset Manifest Validation

```yaml
- name: Asset Manifest Validation
  run: |
    npx asset-factory-cli validate-manifest \
      --manifest assets/manifests/*/asset-manifest.json \
      --verify-digests \
      --fail-on-mismatch
```

**Blocks PR if manifest digests don't match files.**

#### 3. Asset Lint Checks

```yaml
- name: Asset Lint
  run: |
    npx asset-factory-cli lint \
      --assets assets/ \
      --rules design-os/asset-lint-rules.json \
      --output lint-reports/ \
      --fail-on-error
```

Checks:
- Safe area compliance (icon padding)
- Format compliance (correct file types)
- Size budgets (max file sizes)
- Transparency requirements
- Palette compliance (Design OS colors only)
- No forbidden text in icons
- Dimension requirements per platform

**Blocks PR if any lint rule fails.**

#### 4. No Untracked Images Detector

```yaml
- name: No Untracked Images
  run: |
    npx asset-factory-cli scan-untracked \
      --source src/ \
      --registry assets/manifests/ \
      --allowlist config/allowed-external-urls.json \
      --fail-on-untracked
```

Detects:
- Remote image URLs not in allowlist
- Base64 inline images
- Images not in asset registry

**Blocks PR if untracked images found.**

#### 5. License Metadata Required

```yaml
- name: License Check
  run: |
    npx asset-factory-cli check-license \
      --manifests assets/manifests/ \
      --require-license-for-sources \
      --fail-on-missing
```

**Blocks PR if source assets lack license metadata.**

#### 6. Duplicate Detection

```yaml
- name: Duplicate Detection
  run: |
    npx asset-factory-cli detect-duplicates \
      --assets assets/ \
      --similarity-threshold 0.95 \
      --fail-on-duplicates
```

**Blocks PR if near-duplicate assets detected.**

### OPA Policy Gates

#### No Unregistered Assets in UI

```rego
# policies/opa/assets/registry_required.rego
package assets

deny[msg] {
  input.file_type in ["tsx", "jsx", "vue"]
  image_reference := extract_image_refs(input.content)
  not asset_in_registry(image_reference)
  msg := sprintf("Image '%s' is not in the asset registry", [image_reference])
}

asset_in_registry(ref) {
  data.asset_registry[_].path == ref
}
```

#### Evidence Pack Requires Asset Evidence

```rego
# policies/opa/assets/evidence_required.rego
package assets

deny[msg] {
  input.artifact_type == "webapp"
  contains_ui(input)
  not input.evidence_pack.asset_evidence
  msg := "UI releases MUST include asset evidence in Evidence Pack"
}

deny[msg] {
  input.artifact_type == "mobile-app"
  not input.evidence_pack.asset_evidence
  msg := "Mobile app releases MUST include asset evidence"
}
```

#### No Cross-Tenant Asset Reads

```rego
# policies/opa/assets/tenant_isolation.rego
package assets

deny[msg] {
  input.operation == "asset.read"
  input.asset_tenant != input.request_tenant
  not shared_asset(input.asset_path)
  msg := sprintf("Cross-tenant asset access denied: %s", [input.asset_path])
}

shared_asset(path) {
  startswith(path, "assets/baseline/")
}
```

#### No Regeneration Loop Abuse

```rego
# policies/opa/assets/regeneration_limit.rego
package assets

deny[msg] {
  input.operation == "asset.regenerate"
  input.regeneration_count > 3
  not input.escalation_approved
  msg := "Regeneration limit exceeded. Escalation required."
}
```

### Drift Detection

#### Style Drift Scoring

```python
# tools/asset-drift/style_drift.py
def calculate_style_drift(asset_path: str, style_anchor_path: str) -> float:
    """
    Returns drift score 0.0 (perfect match) to 1.0 (complete divergence).
    Uses embedding similarity against style anchor.
    """
    asset_embedding = compute_embedding(asset_path)
    anchor_embedding = load_anchor_embedding(style_anchor_path)

    similarity = cosine_similarity(asset_embedding, anchor_embedding)
    drift_score = 1.0 - similarity

    return drift_score
```

#### Drift Thresholds

| Drift Score | Action |
|-------------|--------|
| 0.0 - 0.10 | Pass |
| 0.10 - 0.15 | Warning, review recommended |
| 0.15 - 0.25 | Fail, deterministic repair required |
| 0.25+ | Fail, regeneration with anchor reinforcement |

---

## Cost Circuit Breakers

### Budget Limits

| Limit | Value | Enforcement |
|-------|-------|-------------|
| Max candidates per request | 4 | Workflow config |
| Max regenerate loops | 3 | OPA policy |
| Token budget per workflow | 50,000 | FinOps circuit breaker |
| Cost per workflow (USD) | $5.00 | FinOps circuit breaker |
| Hourly tenant spend limit | $50.00 | FinOps hard stop |

### Circuit Breaker Configuration

```yaml
asset_factory:
  circuit_breakers:
    generation:
      max_candidates: 4
      max_regenerate_loops: 3
      prefer_deterministic_repair: true

    cost:
      token_budget_per_workflow: 50000
      usd_budget_per_workflow: 5.00
      usd_hourly_tenant_limit: 50.00

    failure:
      consecutive_failure_threshold: 5
      recovery_timeout_seconds: 300
```

---

## Governance and Lifecycle

### Roles and Responsibilities

| Role | Responsibility | Permissions |
|------|----------------|-------------|
| **Design Director** | Approve style anchor changes | Approve breaking changes |
| **Design OS Maintainer** | Tokens, components, brand rules | Write to design-os/ |
| **Asset Factory Maintainer** | ImageOps pipelines, lint rules | Write to asset-factory config |
| **Design Jail Warden** | Enforce Design Jail + asset compliance | Block violations |
| **Accessibility Specialist** | Contrast, a11y checks for assets | Block accessibility failures |
| **Legal/Compliance** | License, provenance verification | Block missing license metadata |
| **FinOps Enforcer** | Budget gates, cost monitoring | Halt runaway workflows |

### Change Process

```
1. Asset Factory Capability RFC
       │
       ▼
2. Design Director + Frontend Architect Review
       │
       ▼
3. Implementation + Policy Tests
       │
       ▼
4. CI Validation Passes
       │
       ▼
5. Style Anchor Updates (if needed)
       │
       ▼
6. Asset Factory Version Tag
       │
       ▼
7. Tenant Adoption (opt-in or baseline)
```

### Versioning (SemVer)

| Change Type | Version Bump | Examples |
|-------------|--------------|----------|
| **Breaking** | MAJOR | Manifest schema change, path convention change |
| **Feature** | MINOR | New asset type, new transform operation |
| **Fix** | PATCH | Lint rule fix, repair step improvement |

### Backwards Compatibility

1. **Manifest schema changes**: Must provide migration tooling
2. **Path changes**: Must provide redirect/alias for 2 minor versions
3. **Lint rule changes**: New rules are warnings for 1 minor version before becoming errors

---

## Multi-Tenancy

### Baseline Asset Factory

Itqahn provides a baseline Asset Factory for all tenants:

- Standard style anchors
- Default lint rules
- Shared baseline assets (opt-in)
- Standard platform variant generation

### Tenant Asset Factory

Tenants may customize:

```yaml
tenant_asset_factory:
  tenant_id: tenant-xyz

  # Custom style anchors
  style_anchors:
    source: "tenant-xyz/design-os/style-anchors/"
    inherit_baseline: false

  # Custom brand rules
  brand_rules:
    palette: "tenant-xyz/design-os/brand-palette.json"
    logo_constraints: "tenant-xyz/design-os/logo-rules.json"

  # Custom lint rules (extends baseline)
  lint_rules:
    extend_baseline: true
    custom_rules: "tenant-xyz/config/asset-lint-rules.json"

  # Isolated registry namespace
  registry_namespace: "tenant-xyz"
```

### Security Boundaries

| Boundary | Enforcement |
|----------|-------------|
| **Asset isolation** | Tenant cannot read other tenant assets (except baseline) |
| **Registry isolation** | Each tenant has namespaced registry |
| **Style anchor isolation** | Tenant anchors not visible to others |
| **No shared baselines** | Unless explicitly sanitized and opted-in |
| **EXIF/metadata stripping** | All uploaded assets stripped of metadata |
| **Content moderation** | User-uploaded assets scanned before processing |

### Enterprise Mode

For dedicated instances:

```yaml
enterprise_asset_factory:
  mode: dedicated

  # Dedicated resources
  compute:
    namespace: "tenant-enterprise-assets"
    gpu_allocation: "dedicated"

  # Dedicated credentials
  credentials:
    vault_path: "kv/enterprise/tenant-xyz/assets"
    rate_limits: "unlimited"

  # Full isolation
  isolation:
    shared_nothing: true
    dedicated_registry: true
    custom_model_endpoints: true
```

---

## Platform-Correct Outputs

### iOS Asset Catalog

```
ios/
├── AppIcon.appiconset/
│   ├── Contents.json
│   ├── icon-1024.png
│   ├── icon-180.png     # iPhone @3x
│   ├── icon-167.png     # iPad Pro @2x
│   ├── icon-152.png     # iPad @2x
│   ├── icon-120.png     # iPhone @2x
│   └── ...
└── Assets.xcassets/
    └── Images/
```

### Android Adaptive Icons

```
android/
├── mipmap-xxxhdpi/
│   ├── ic_launcher.png
│   ├── ic_launcher_foreground.png
│   └── ic_launcher_background.png
├── mipmap-xxhdpi/
├── mipmap-xhdpi/
├── mipmap-hdpi/
├── mipmap-mdpi/
└── ic_launcher.xml
```

### Web Assets

```
web/
├── icons/
│   ├── icon-512.png
│   ├── icon-192.png
│   ├── icon-180.png    # Apple touch icon
│   ├── icon-152.png
│   ├── icon-144.png
│   └── ...
├── favicon.ico
├── favicon.svg
└── manifest.json
```

---

## NanoBanana Integration

Asset Factory uses **NanoBanana** as the primary image generation provider for all 2D asset types.

### Provider Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      NANOBANANA INTEGRATION ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        OPERATOR MODE WORKFLOW                            │ │
│  │                                                                          │ │
│  │  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐  │ │
│  │  │  Asset     │    │  MCP       │    │  Vault     │    │ NanoBanana │  │ │
│  │  │  Request   │ →  │  Server    │ ←  │  Secret    │ →  │  API       │  │ │
│  │  │  (Spec)    │    │  (Runtime) │    │  Injection │    │  (Gen)     │  │ │
│  │  └────────────┘    └────────────┘    └────────────┘    └────────────┘  │ │
│  │                           │                                  │          │ │
│  │                           ▼                                  ▼          │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │                      GENERATED ASSET                             │   │ │
│  │  │  Raw Output → Content Moderation → Lint → Platform Variants     │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  KEY: API key NEVER exposed to agents. Injected at MCP server runtime only.  │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Supported Asset Types via NanoBanana

| Asset Type | NanoBanana Model | Quality Gate |
|------------|------------------|--------------|
| **App Icon** | `nanobanana-icon-v2` | Style drift < 0.15 |
| **UI Icons** | `nanobanana-icon-v2` | SVG export required |
| **Logo** | `nanobanana-logo-v1` | Brand compliance check |
| **Hero Image** | `nanobanana-hero-v1` | Resolution ≥ 1920x1080 |
| **Illustration** | `nanobanana-illustration-v1` | Style anchor match |
| **OG Image** | `nanobanana-social-v1` | 1200×630 exact |
| **Product Photo** | `nanobanana-product-v1` | Background transparency |
| **Marketing Banner** | `nanobanana-banner-v1` | Format compliance |

### API Key Management

NanoBanana API key MUST be stored in Vault and NEVER exposed to agents.

```yaml
# Vault secret structure
vault_path: "kv/itqahn/services/nanobanana"
secret_schema:
  api_key: "nb_prod_..."
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
```

### Runtime Secret Injection

Operator Mode injects the NanoBanana API key at MCP server startup ONLY:

```python
# mcp-nanobanana server initialization
# Key is injected via environment, never visible to agent prompts

def start_nanobanana_mcp_server(run_id: str, tenant_id: str):
    """
    Start MCP server with NanoBanana credentials.
    API key is injected from Vault, never exposed to agents.
    """
    # Fetch from Vault at server startup
    vault_client = get_vault_client()
    secret = vault_client.read(f"kv/itqahn/tenants/{tenant_id}/nanobanana")

    # Inject as environment variable to MCP process
    env = {
        "NANOBANANA_API_KEY": secret["api_key"],
        "NANOBANANA_ENDPOINT": secret["api_endpoint"],
        "ITQAHN_RUN_ID": run_id,
        "ITQAHN_TENANT_ID": tenant_id,
    }

    # Start MCP server with credentials
    process = subprocess.Popen(
        ["mcp-nanobanana-server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return process
```

### Agent Interaction Model

Agents call MCP tools WITHOUT access to API credentials:

```python
# Agent perspective - no credentials visible
mcp_call = {
    "tool": "nanobanana.generate",
    "parameters": {
        "prompt": "Modern app icon, gradient blue to purple, minimalist",
        "model": "nanobanana-icon-v2",
        "style_anchor": "style-anchors/brand-primary.json",
        "design_os_version": "1.2.0",
        "output_format": "png",
        "width": 1024,
        "height": 1024,
        "candidates": 4,
    }
}
# API key is handled by MCP server layer, invisible to agent
```

### NanoBanana MCP Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `nanobanana.generate` | Generate new asset | prompt, model, style_anchor, dimensions |
| `nanobanana.refine` | Refine existing asset | asset_path, refinement_prompt, preserve_structure |
| `nanobanana.upscale` | Increase resolution | asset_path, scale_factor, preserve_quality |
| `nanobanana.background_remove` | Remove background | asset_path, edge_refinement |
| `nanobanana.style_transfer` | Apply style anchor | asset_path, style_anchor, strength |
| `nanobanana.vectorize` | Convert to SVG | asset_path, color_count, smoothing |

### Generation Workflow with NanoBanana

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    NANOBANANA GENERATION WORKFLOW                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. PROMPT CONSTRUCTION                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Load style anchor constraints                                    │   │
│  │  • Apply Design OS palette tokens                                   │   │
│  │  • Construct sanitized prompt (injection defense)                   │   │
│  │  • Add negative prompts (forbidden elements)                        │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  2. API CALL (via MCP)               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • MCP server adds API key (from Vault)                             │   │
│  │  • Send generation request to NanoBanana API                        │   │
│  │  • Receive N candidates                                              │   │
│  │  • Log request/response (redact API key)                            │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  3. CONTENT MODERATION               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • NSFW check (threshold: 0.05)                                     │   │
│  │  • Violence check (threshold: 0.05)                                 │   │
│  │  • Trademark/copyright scan                                          │   │
│  │  • Reject and log if fails                                          │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  4. STYLE VALIDATION                 ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Compute style drift score vs anchor                              │   │
│  │  • Check palette compliance                                          │   │
│  │  • Rank candidates by drift score                                   │   │
│  │  • Select best candidate or trigger remediation                     │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                      │
│  5. POST-PROCESSING                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Apply deterministic repairs (color correction, bg removal)       │   │
│  │  • Generate platform variants                                        │   │
│  │  • Run asset lint                                                    │   │
│  │  • Compute final digests                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Edge Case Handling

| Edge Case | Detection | Auto-Remediation | Escalation |
|-----------|-----------|------------------|------------|
| **API rate limit** | 429 response | Exponential backoff (max 5 retries) | Pause workflow, alert |
| **API timeout** | Response > 60s | Retry with smaller resolution | Manual retry |
| **Low quality output** | Style drift > 0.25 | Regenerate with stronger anchor | After 3 failures |
| **Content policy violation** | Moderation score > threshold | Rewrite prompt, remove triggers | Security alert |
| **API key invalid** | 401/403 response | None (cannot auto-fix) | Kill switch, credential rotation |
| **Quota exhausted** | 402 response | None | Budget approval required |
| **Model unavailable** | 503 response | Fallback to alternate model | After 3 failures |
| **Palette violation** | Lint failure | Auto color-correct to nearest token | After 2 failures |
| **Resolution too low** | Output < spec | Upscale via nanobanana.upscale | If still fails after upscale |

### Auto-Remediation Workflow

```python
async def generate_with_remediation(spec: AssetSpec) -> GenerationResult:
    """Generate asset with automatic remediation for common failures."""

    max_attempts = spec.generation.max_regenerate_loops  # Default: 3

    for attempt in range(max_attempts):
        try:
            # Generate candidates
            candidates = await nanobanana_generate(spec)

            # Content moderation
            for candidate in candidates:
                moderation = await moderate_asset(candidate)
                if not moderation.allowed:
                    candidates.remove(candidate)
                    log_moderation_failure(candidate, moderation)

            if not candidates:
                # All candidates failed moderation
                spec = rewrite_prompt_for_safety(spec)
                continue

            # Style validation
            best_candidate = None
            best_drift = float('inf')

            for candidate in candidates:
                drift = calculate_style_drift(candidate, spec.style_anchor)
                if drift < best_drift:
                    best_drift = drift
                    best_candidate = candidate

            # Check drift threshold
            if best_drift > spec.constraints.style.anchor_similarity_threshold:
                if attempt < max_attempts - 1:
                    # Try deterministic repair first
                    if spec.generation.prefer_deterministic_repair:
                        repaired = await deterministic_repair(best_candidate, spec)
                        new_drift = calculate_style_drift(repaired, spec.style_anchor)
                        if new_drift <= spec.constraints.style.anchor_similarity_threshold:
                            return GenerationResult(asset=repaired, drift=new_drift)

                    # Regenerate with stronger anchor
                    spec = strengthen_anchor_constraints(spec)
                    continue
                else:
                    # Final attempt failed
                    return GenerationResult(
                        asset=best_candidate,
                        drift=best_drift,
                        warning="Style drift exceeds threshold, requires manual review"
                    )

            return GenerationResult(asset=best_candidate, drift=best_drift)

        except RateLimitError:
            await exponential_backoff(attempt)
        except APITimeoutError:
            spec = reduce_resolution(spec)
        except QuotaExhaustedError:
            raise EscalationRequired("Budget approval needed")
        except APIKeyError:
            raise KillSwitchRequired("API credential failure")

    raise GenerationFailed(f"Failed after {max_attempts} attempts")
```

### Content Moderation

All NanoBanana outputs MUST pass content moderation:

```python
async def moderate_asset(asset_path: str) -> ModerationResult:
    """Check generated asset for content policy violations."""

    # NSFW detection
    nsfw_score = await nanobanana_nsfw_check(asset_path)
    if nsfw_score > 0.05:
        return ModerationResult(
            allowed=False,
            reason="NSFW content detected",
            score=nsfw_score,
            action="reject_and_log"
        )

    # Violence detection
    violence_score = await nanobanana_violence_check(asset_path)
    if violence_score > 0.05:
        return ModerationResult(
            allowed=False,
            reason="Violent content detected",
            score=violence_score,
            action="reject_and_log"
        )

    # Trademark detection
    trademark_result = await trademark_scan(asset_path)
    if trademark_result.detected:
        return ModerationResult(
            allowed=False,
            reason=f"Trademark detected: {trademark_result.trademark}",
            action="reject_and_escalate"
        )

    # Face detection (for assets that forbid faces)
    if asset_spec.constraints.style.forbidden_elements:
        if "photo-realistic-faces" in asset_spec.constraints.style.forbidden_elements:
            face_result = await face_detection(asset_path)
            if face_result.faces_detected:
                return ModerationResult(
                    allowed=False,
                    reason="Photo-realistic faces detected in icon",
                    action="reject_and_regenerate"
                )

    return ModerationResult(allowed=True)
```

### Rate Limits and Quotas

| Tier | Requests/min | Requests/hour | Max Resolution | Concurrent |
|------|--------------|---------------|----------------|------------|
| **Standard** | 30 | 500 | 2048×2048 | 4 |
| **Professional** | 60 | 2000 | 4096×4096 | 8 |
| **Enterprise** | 120 | 10000 | 8192×8192 | 16 |

### Cost Tracking

All NanoBanana API calls are tracked for FinOps:

```json
{
  "nanobanana_usage": {
    "run_id": "run-01J5ABCD...",
    "tenant_id": "tenant-xyz",
    "requests": [
      {
        "tool": "nanobanana.generate",
        "model": "nanobanana-icon-v2",
        "tokens_input": 1500,
        "tokens_output": 0,
        "images_generated": 4,
        "cost_usd": 0.08,
        "timestamp": "2026-01-08T12:00:00Z"
      }
    ],
    "total_cost_usd": 0.45,
    "budget_remaining_usd": 4.55
  }
}
```

### Audit Trail

Every NanoBanana interaction is logged in the Evidence Pack:

```json
{
  "nanobanana_evidence": {
    "request_id": "nb-req-abc123",
    "run_id": "run-01J5ABCD...",
    "timestamp": "2026-01-08T12:00:00Z",
    "tool": "nanobanana.generate",
    "model": "nanobanana-icon-v2",
    "prompt_hash": "sha256:...",
    "prompt_sanitized": true,
    "style_anchor": "style-anchors/brand-primary.json",
    "design_os_version": "1.2.0",
    "candidates_generated": 4,
    "candidate_selected": 2,
    "moderation": {
      "nsfw_score": 0.001,
      "violence_score": 0.000,
      "trademark_check": "passed"
    },
    "style_drift_score": 0.08,
    "output_digest": "sha256:...",
    "cost_usd": 0.08
  }
}
```

### Failure Modes and Kill Switch

| Failure | Severity | Action |
|---------|----------|--------|
| API key compromised | P0 | Kill switch → Rotate credentials |
| Repeated content violations | P1 | Pause tenant → Security review |
| Budget exceeded | P2 | Pause workflow → Approval required |
| Model degradation | P2 | Fallback model → Alert engineering |
| Rate limit exhaustion | P3 | Backoff → Notify |

---

## Related Documents

- `docs/03-platform/design-os.md` — Design OS specification
- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/04-security/prompt-injection-defense.md` — Asset prompt hardening
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/07-integrations/mcp/mcp-assets.md` — MCP assets integration
- `docs/07-integrations/mcp/mcp-nanobanana.md` — NanoBanana MCP specification
- `docs/07-integrations/git-integration.md` — Asset versioning
- `docs/08-agents/agent-permissions.md` — Asset agent restrictions
- `docs/06-operations/runbooks.md` — Asset incident runbook

---

**Version**: 2.3.0 | **Date**: 2026-01-08
