# Requirements Schema

This document defines the **format contracts** for all requirements artifacts in Itqahn. Artifacts that don't follow these schemas will fail validation at their respective gates.

---

## Phase 1 Output Schemas (Concept Lock)

Phase 1 (Adaptive Interview) produces seven structured artifacts that together form the **Concept Lock**. Each artifact has a strict schema with required fields and defined behavior for uncertainty.

### Schema Overview (Phase 1)

| Artifact | Purpose | Required | Schema Path |
|----------|---------|----------|-------------|
| **Project Card** | Basic project identity and type | Yes | `schemas/project-card.json` |
| **Region Profile** | Operational constraints by geography | Yes | `schemas/region-profile.json` |
| **Journeys & Scope** | User journeys and MVP boundaries | Yes | `schemas/journeys-scope.json` |
| **Design OS Draft** | Visual design baseline (tokens, typography) | Yes | `schemas/design-os-draft.json` |
| **Wireframe Choice Set** | Selected layout templates | Yes | `schemas/wireframe-choices.json` |
| **Asset Requirements Manifest** | Required brand assets and specifications | Yes | `schemas/asset-requirements.json` |
| **Assumptions Register** | Explicit unknowns and deferred decisions | Yes | `schemas/assumptions-register.json` |

---

## Phase 1: Project Card

The foundational identity of the project.

```yaml
project_card:
  name: string (required, 3-60 characters, unique within tenant)
  slug: string (auto-generated from name, kebab-case)
  one_liner: string (required, 10-140 characters)
  build_type: enum (required)
    - web_app
    - mobile_app
    - service
    - data_product
    - integration
    - infrastructure
    - documentation
    - asset_production
  platforms: array[enum] (required for web/mobile)
    - ios
    - android
    - web
    - pwa
  primary_persona:
    name: string (required)
    description: string (required, 20-200 characters)
    goals: array[string] (required, 1-5 items)
  owner:
    email: string (required, valid email)
    name: string (required)
  created_at: datetime (auto)
  tenant_id: string (auto, from session)
```

**Validation Rules:**
- `name` must be unique within tenant namespace
- `build_type` determines which subsequent modules are shown
- `platforms` required only for `web_app` and `mobile_app` types
- At least one platform must be selected for applicable types

**"Not sure" Behavior:**
- `primary_persona`: Suggest "Generic User" with default goals, log assumption
- `platforms`: Default to `web` for web_app, `[ios, android]` for mobile_app

---

## Phase 1: Region Profile

Operational constraints based on target regions. NOT "cultural preferences"—these are enforceable requirements.

```yaml
region_profile:
  primary_region: enum (required)
    - us
    - eu
    - uk
    - middle_east
    - asia_pacific
    - latam
    - africa
    - global
  additional_regions: array[enum] (optional)
  locale:
    default_language: string (required, ISO 639-1, e.g., "en")
    supported_languages: array[string] (optional)
    rtl_required: boolean (auto-computed from languages)
  compliance:
    gdpr_required: boolean (auto-computed from regions)
    ccpa_required: boolean (auto-computed from regions)
    data_residency: array[string] (optional, ISO 3166-1 alpha-2)
  currency:
    default: string (optional, ISO 4217, e.g., "USD")
    supported: array[string] (optional)
  timezone:
    default: string (optional, IANA timezone)
    user_selectable: boolean (default: true)
```

**Validation Rules:**
- If `primary_region` is `eu`, `gdpr_required` auto-set to `true`
- If any language in `supported_languages` is RTL (ar, he, fa, ur), `rtl_required` auto-set to `true`
- `data_residency` must be subset of region countries

**"Not sure" Behavior:**
- `primary_region`: Prompt "Where will most users access from?", suggest `global` as safe default
- `data_residency`: Log assumption "No specific data residency requirement"

---

## Phase 1: Journeys & Scope v0

Defines the MVP scope through user journeys—what the user can DO, not features.

```yaml
journeys_scope:
  journeys: array[Journey] (required, 1-8 items)
  mvp_boundary:
    included_journeys: array[string] (required, journey_ids)
    excluded_journeys: array[string] (optional, journey_ids)
    rationale: string (optional)
  non_goals: array[string] (required, 1-10 items)

Journey:
  journey_id: string (auto-generated)
  name: string (required, 5-60 characters)
  actor: string (required, must match persona)
  goal: string (required, 10-200 characters)
  priority: enum (required)
    - must_have
    - should_have
    - could_have
    - wont_have
  steps: array[JourneyStep] (required, 2-10 steps)
  success_criteria: string (required)
  triggers_modules: array[string] (auto-computed)

JourneyStep:
  step_number: integer (auto)
  user_action: string (required)
  system_response: string (required)
  requires_auth: boolean (default: false)
  requires_payment: boolean (default: false)
  data_classification: enum (default: internal)
    - public
    - internal
    - confidential
    - regulated
```

**Validation Rules:**
- At least one journey must have `priority: must_have`
- All `must_have` journeys must be in `mvp_boundary.included_journeys`
- `wont_have` journeys must be in `mvp_boundary.excluded_journeys` or omitted from included
- Journey steps with `requires_payment: true` trigger payment module
- Journey steps with `requires_auth: true` trigger auth module

**"Not sure" Behavior:**
- `success_criteria`: Prompt for goal completion indicator, log assumption if skipped
- `steps`: Minimum 2 steps required; cannot skip entirely

**Question Format Example:**
```
What journeys should your app support?

☑ User can sign up and log in
☑ User can browse items
☑ User can search for specific items
☐ User can make a purchase
☐ User can leave reviews
☐ User can track orders
☐ Other (describe)...
☐ Not sure (we'll start with basics)
```

---

## Phase 1: Design OS Draft

Baseline visual design decisions that become the foundation for the Design OS version used in implementation.

```yaml
design_os_draft:
  version: string (auto, e.g., "draft-20260108")
  palette:
    generation_method: enum (required)
      - from_brand_asset     # User uploaded logo/brand guide
      - from_preset          # Selected from Itqahn presets
      - custom_selection     # User picked individual colors
    source: string (optional, path to brand asset if uploaded)
    preset_id: string (optional, if from_preset)
    colors:
      primary: string (required, hex color, validated for accessibility)
      secondary: string (required, hex color)
      accent: string (optional, hex color)
      background: string (required, hex color)
      surface: string (required, hex color)
      text_primary: string (required, hex color)
      text_secondary: string (required, hex color)
      error: string (required, hex color)
      warning: string (required, hex color)
      success: string (required, hex color)
    accessibility_validated: boolean (auto, true if all contrasts pass)
    contrast_ratios: object (auto-computed)

  typography:
    heading_font: string (required, from approved fonts)
    body_font: string (required, from approved fonts)
    scale: enum (required)
      - compact     # 1.125 ratio
      - standard    # 1.25 ratio
      - spacious    # 1.333 ratio
    base_size: integer (required, 14-18)

  density:
    mode: enum (required)
      - compact     # Tight spacing, more content
      - comfortable # Balanced
      - spacious    # More whitespace

  corner_style: enum (required)
    - sharp        # radius: 0
    - subtle       # radius: 4px
    - rounded      # radius: 8px
    - pill         # radius: 9999px (for buttons)

  theme_modes: array[enum] (required, at least 1)
    - light
    - dark
    - auto         # System preference
```

**Validation Rules:**
- All color pairs must pass WCAG AA contrast (4.5:1 for text, 3:1 for UI)
- `primary` and `text_primary` on `background` must pass contrast
- If any contrast fails, palette is marked invalid and user prompted to adjust
- Fonts must be from Design OS approved font list

**"Not sure" Behavior:**
- `palette`: Offer 4-6 pre-generated accessible palettes based on build type
- `typography`: Default to system-safe fonts (Inter, System UI)
- `density`: Default to `comfortable`
- `corner_style`: Default to `rounded`

**Palette Generation Constraints (MUST):**
- All palettes MUST pass WCAG AA minimum (4.5:1 for body text)
- Primary color MUST have sufficient contrast on both light and dark backgrounds
- Generated palettes come with preview: button, text on background, card

---

## Phase 1: Wireframe Choice Set

Visual selection of layout templates for key screen types.

```yaml
wireframe_choices:
  selections: array[WireframeSelection] (required, 1+ items)
  template_set_id: string (auto, from selected templates)

WireframeSelection:
  screen_type: enum (required)
    - home
    - listing
    - detail
    - form
    - auth_login
    - auth_signup
    - dashboard
    - settings
    - profile
    - search
    - checkout
    - empty_state
    - error
    - onboarding
  template_id: string (required, from available templates)
  template_variant: string (optional, e.g., "A", "B", "C")
  customizations: object (optional)
    header_style: enum [standard, minimal, hero]
    navigation_style: enum [top, bottom, sidebar, hamburger]
    content_layout: enum [single, two_column, grid, list]
```

**Validation Rules:**
- At least `home` screen type required
- If journeys include auth, `auth_login` and `auth_signup` required
- If journeys include payment, `checkout` required
- Users can mix-and-match templates (Home=A, Listing=B)

**"Not sure" Behavior:**
- Show 3-6 visual wireframe variants per screen type
- Suggest most popular template as default
- Allow "Use same template for all" shortcut

**Selection Interface:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SELECT LAYOUT FOR: Home Screen                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Template A │  │  Template B │  │  Template C │  │  Template D │        │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │        │
│  │ │  HERO   │ │  │ │ NAV BAR │ │  │ │ SIDEBAR │ │  │ │ MINIMAL │ │        │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │        │
│  │ │  CARDS  │ │  │ │  LIST   │ │  │ │  GRID   │ │  │ │  FOCUS  │ │        │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │        │
│  │    ☐ A     │  │    ☐ B     │  │    ☑ C     │  │    ☐ D     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                              │
│  [ Use C for all screens ]  [ Not sure - recommend for me ]                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Asset Requirements Manifest

Captures all visual assets needed BEFORE build begins. This ensures Asset Factory readiness.

```yaml
asset_requirements:
  manifest_id: string (auto)
  manifest_version: string (default: "1.0.0")

  brand_assets:
    logo:
      variants_needed: array[enum] (required)
        - primary           # Full logo, light background
        - inverted          # Full logo, dark background
        - mono_light        # Single color, light
        - mono_dark         # Single color, dark
        - icon_only         # Mark/symbol without text
      formats: array[enum] (required)
        - svg               # Vector, required for all
        - png               # Raster fallback
      source_provided: boolean
      source_path: string (optional, if user uploads)
      generation_required: boolean (auto, true if not provided)

    favicon:
      required: boolean (auto, true for web_app)
      sizes: array[integer] (auto)  # [16, 32, 48, 180, 192, 512]

  app_icons:
    required: boolean (auto, true for mobile_app)
    platforms:
      ios:
        required: boolean
        sizes: array[string] (auto) # ["1024x1024", "180x180", "120x120", ...]
        adaptive: boolean (default: false)
      android:
        required: boolean
        adaptive_icon: boolean (default: true)
        foreground_layer: boolean (default: true)
        background_type: enum [solid, gradient, image]
      web:
        pwa_icons: boolean (default: true for pwa)

  marketing_assets:
    app_store_screenshots:
      required: boolean (auto, true for mobile_app)
      platforms: array[enum] [ios, android]
      screen_sizes: array[string]  # ["6.5", "5.5"] for iOS
      count_per_size: integer (default: 5)
    feature_graphic:
      required: boolean (auto, true for android)
      dimensions: string (default: "1024x500")
    og_images:
      required: boolean (auto, true for web_app)
      dimensions: string (default: "1200x630")
      variants: array[string] (optional) # ["home", "share", "article"]

  ui_icons:
    icon_set_policy: enum (required)
      - use_system          # Platform native icons
      - use_library         # Lucide, Heroicons, etc.
      - custom_generation   # Generate via Asset Factory
    library_name: string (optional, if use_library)
    style: enum (required)
      - outline
      - solid
      - duotone
    stroke_width: number (optional, for outline, 1-3)
    sizes_needed: array[integer] (default: [16, 20, 24])
    custom_icons_list: array[string] (optional, names of custom icons needed)

  illustrations:
    required: boolean
    style_preference: enum (optional)
      - line_art
      - flat
      - isometric
      - 3d_render
      - hand_drawn
    scenes_needed: array[string] (optional)
      # e.g., ["onboarding_welcome", "empty_state", "error_page"]

  photos:
    required: boolean
    subjects: array[string] (optional)
      # e.g., ["team_collaboration", "workspace", "product_shots"]
    style: enum (optional)
      - lifestyle
      - product
      - abstract
      - people

  output_specifications:
    format_priorities: array[enum] (default: [svg, webp, png])
      - svg
      - png
      - webp
      - jpg
      - ico
    background_rules:
      transparent_required: boolean (default: true for icons)
      solid_fallback_color: string (optional, hex)
    safe_area:
      enforce: boolean (default: true for app icons)
      padding_percent: integer (default: 10)
    max_file_sizes:
      icon_kb: integer (default: 100)
      illustration_kb: integer (default: 500)
      photo_kb: integer (default: 1000)

  quality_requirements:
    consistency_check: boolean (default: true)
    background_cleanup: boolean (default: true)
    upscaling_policy: enum (default: preserve)
      - preserve           # Never upscale, regenerate if needed
      - allow_2x           # Allow up to 2x upscaling
      - ai_enhance         # Use AI enhancement for upscaling

  ownership:
    all_assets_owner: string (auto, from project owner)
    storage_location: string (auto, computed from tenant)
    versioning: boolean (default: true)
```

**Validation Rules:**
- If `build_type: mobile_app`, `app_icons.required` auto-set to `true`
- If `build_type: web_app`, `favicon.required` and `og_images.required` auto-set to `true`
- If logo not provided, `generation_required` set to `true`
- `custom_icons_list` items must be unique

**"Not sure" Behavior:**
- `logo`: Prompt for upload, offer generation if none
- `icon_set_policy`: Default to `use_library` with Lucide
- `illustrations`: Default to not required, can add later via Change Request
- `photos`: Default to not required

---

## Phase 1: Assumptions Register

Explicit tracking of all uncertainty and deferred decisions.

```yaml
assumptions_register:
  assumptions: array[Assumption] (auto-populated)
  total_not_sure_count: integer (auto)
  resolution_required_by: string (default: "gate_2")

Assumption:
  assumption_id: string (auto)
  source_module: string (required)  # Which interview module
  source_question: string (required) # Which question
  original_answer: string (required) # "Not sure" or similar
  default_applied: object (optional)
    field: string
    value: any
    rationale: string
  risk_level: enum (auto-computed)
    - low              # Safe default exists
    - medium           # May affect implementation
    - high             # Blocks key decisions
  requires_resolution_by: enum
    - before_lock      # Must resolve before Concept Lock
    - gate_2           # Must resolve before Experience Lock
    - gate_3           # Must resolve before RC
    - post_launch      # Can defer to post-launch
  resolution:
    resolved: boolean (default: false)
    resolved_at: datetime (optional)
    resolved_by: string (optional)
    final_value: any (optional)
    resolution_method: enum (optional)
      - user_decision
      - discovered_during_build
      - change_request
```

**Validation Rules:**
- Assumptions with `risk_level: high` and `requires_resolution_by: before_lock` MUST be resolved before Concept Lock
- Maximum 30% of total questions can be "Not sure" to proceed to lock
- Each assumption tracks lineage back to interview question

**"Not sure" Handling Flow:**
```
1. User selects "Not sure" for a question
       │
       ▼
2. System identifies safe default (if available)
       │
       ├── Safe default exists → Apply default, log assumption
       │
       └── No safe default → Mark as high-risk assumption
       │
       ▼
3. Assumption added to register with:
   - Source question
   - Default applied (if any)
   - Risk level
   - Resolution deadline
       │
       ▼
4. At Concept Lock:
   - Show summary of all assumptions
   - Block if >30% "Not sure"
   - Block if any high-risk unresolved
       │
       ▼
5. User confirms assumptions acceptable
```

---

## PRD Schema Overview

In addition to Phase 1 outputs, traditional PRDs are generated/refined in Gate 2. Every PRD must contain these sections:

| Section | Required | Validated By |
|---------|----------|--------------|
| Summary | Yes | Schema validator |
| Problem Statement | Yes | Schema validator |
| Goals | Yes | Must be measurable |
| Non-Goals | Yes | Schema validator |
| Users & Personas | Yes | Schema validator |
| User Journeys | Yes | Minimum 1 journey |
| Functional Requirements | Yes | Numbered list |
| Non-Functional Requirements | Yes | Standard categories |
| Data & Tenancy | Yes | Classification required |
| Dependencies | Yes | Schema validator |
| Acceptance Criteria | Yes | Linked or embedded |
| Risks & Mitigations | Yes | Schema validator |
| Launch Plan | Yes | Schema validator |
| Open Questions | No | Schema validator |

---

## Section Specifications

### 1. Summary (Required)

```yaml
summary:
  product_name: string (required)
  owner: string (required, must match agent/human ID)
  date: date (required, ISO 8601)
  status: enum [Draft, In Review, Approved, Deprecated]
  risk_tier: enum [Baseline, Sensitive, Regulated]
  compliance_tier: enum [Tier 0, Tier 1, Tier 2]
```

**Validation rules:**
- `product_name` must be unique within the project
- `owner` must be a valid agent or human identifier
- `risk_tier` determines security gates applied
- `compliance_tier` determines compliance controls applied

---

### 2. Problem Statement (Required)

```yaml
problem_statement:
  description: string (required, min 50 characters)
  affected_users: array[string] (required, min 1)
  current_state: string (required)
  desired_state: string (required)
```

**Validation rules:**
- Must clearly articulate the problem, not the solution
- Must identify who experiences the problem
- Current and desired states must be distinct

---

### 3. Goals (Required)

```yaml
goals:
  - metric: string (required)
    current: number | string (required)
    target: number | string (required)
    timeframe: string (required)
```

**Validation rules:**
- Minimum 3 goals, maximum 7
- Each goal must be measurable (has a metric)
- Targets must be different from current state
- Timeframe must be specified

**Example:**
```yaml
goals:
  - metric: "User onboarding completion rate"
    current: "45%"
    target: "80%"
    timeframe: "30 days post-launch"
```

---

### 4. Non-Goals (Required)

```yaml
non_goals:
  - description: string (required)
    rationale: string (optional)
```

**Validation rules:**
- Minimum 1 non-goal
- Must explicitly state what is out of scope
- Prevents scope creep during implementation

---

### 5. Users & Personas (Required)

```yaml
users:
  primary:
    - persona: string (required)
      description: string (required)
      needs: array[string] (required)
  secondary:
    - persona: string (required)
      description: string (required)
```

**Validation rules:**
- At least 1 primary user required
- Secondary users are optional but recommended

---

### 6. User Journeys (Required)

```yaml
journeys:
  - name: string (required)
    actor: string (required, must match persona)
    preconditions: array[string] (required)
    steps:
      - action: string (required)
        system_response: string (required)
    postconditions: array[string] (required)
    success_criteria: string (required)
```

**Validation rules:**
- Minimum 1 journey, recommend top 3
- Actor must reference a defined persona
- Each step must have action and system response

---

### 7. Functional Requirements (Required)

```yaml
functional_requirements:
  - id: string (required, format: FR-XXX)
    description: string (required)
    priority: enum [Must, Should, Could, Won't]
    acceptance_criteria: array[string] (required)
    dependencies: array[string] (optional)
```

**Validation rules:**
- IDs must be unique and follow FR-XXX format
- At least 1 "Must" priority requirement
- Each requirement must have acceptance criteria

---

### 8. Non-Functional Requirements (Required)

```yaml
non_functional_requirements:
  performance:
    latency_p50: string (required for APIs)
    latency_p99: string (required for APIs)
    throughput: string (optional)
  reliability:
    availability_target: string (required, e.g., "99.9%")
    rto: string (required for production)
    rpo: string (required for production)
  security:
    authentication: string (required)
    authorization: string (required)
    data_encryption: enum [at-rest, in-transit, both]
  accessibility:
    wcag_level: enum [A, AA, AAA] (required for web/mobile)
  observability:
    logging: boolean (default: true)
    metrics: boolean (default: true)
    tracing: boolean (default: true)
  internationalization:
    supported_locales: array[string] (optional)
    rtl_support: boolean (optional)
```

---

### 9. Data & Tenancy (Required)

```yaml
data:
  classification: enum [Public, Internal, Confidential, Regulated]
  pii_fields: array[string] (required if classification >= Confidential)
  retention_policy: string (required)
  tenant_model: enum [Single, Multi-namespace, Multi-cluster]
  data_residency: array[string] (optional, e.g., ["US", "EU"])
```

**Validation rules:**
- Classification determines compliance tier minimum
- PII fields must be listed if handling personal data
- Retention policy must reference a valid policy document

---

### 10. Dependencies (Required)

```yaml
dependencies:
  internal_services:
    - service: string
      contract: string (link to OpenAPI spec)
  external_providers:
    - provider: string
      mcp_server: string (must be allowlisted)
      purpose: string
  infrastructure:
    - resource: string
      justification: string
```

---

### 11. Acceptance Criteria (Required)

```yaml
acceptance_criteria:
  link: string (path to ACCEPTANCE-CRITERIA.md)
  # OR embedded:
  criteria:
    - id: string (format: AC-XXX)
      given: string
      when: string
      then: string
```

**Validation rules:**
- Must link to or embed acceptance criteria
- All functional requirements must have corresponding AC
- Format follows Given/When/Then pattern

---

### 12. Risks & Mitigations (Required)

```yaml
risks:
  - id: string (format: RISK-XXX)
    description: string
    likelihood: enum [Low, Medium, High]
    impact: enum [Low, Medium, High]
    mitigation: string
    owner: string
```

---

### 13. Launch Plan (Required)

```yaml
launch_plan:
  rollout_strategy: enum [Big Bang, Canary, Blue-Green, Feature Flag]
  canary_percentage: number (required if Canary)
  monitoring_dashboard: string (link)
  rollback_plan: string (link to runbook)
  success_criteria: array[string]
```

---

### 14. Open Questions (Optional)

```yaml
open_questions:
  - question: string
    owner: string
    due_date: date
    status: enum [Open, Answered, Blocked]
    answer: string (required if Answered)
```

---

## Validation

PRDs are validated by:
1. **Schema validator** (`tools/validators/prd_validator.py`)
2. **Requirements Writer agent** (at intake)
3. **Gate 1 approval workflow**

Validation errors block progression to Gate 2.

---

## Template

Use `templates/product/PRD.md` as the starting point for all PRDs.

---

## Related Documents

- `docs/01-product/lifecycle-phase-gates.md` — Phase gates and Concept Lock
- `docs/03-platform/portal-webapp.md` — Phase 1 dashboard UX
- `docs/03-platform/design-system-design-jail.md` — Design OS integration
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory for asset generation
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `templates/product/PRD.md` — PRD template
- `schemas/concept-lock.json` — Concept Lock schema

---

**Version**: 2.2.0 | **Date**: 2026-01-08
