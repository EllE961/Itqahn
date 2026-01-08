# Design System and Design Jail

Design Jail is the governance mechanism that ensures UI consistency, accessibility, and maintainability in Itqahn.

**Design Jail is enforced via Design OS artifacts.** Without a valid, versioned Design OS, Design Jail cannot function. See `docs/03-platform/design-os.md` for the complete Design OS specification.

---

## Relationship to Design OS

| Concept | Role |
|---------|------|
| **Design OS** | The versioned source of truth (tokens, components, patterns) |
| **Design Jail** | The enforcement mechanism that validates against Design OS |
| **Design Jail Warden** | The agent that reviews and blocks violations |

```
Design OS (Source)     →     Design Jail (Enforcement)     →     Compliant UI
  tokens.json                   Token lint                        Uses tokens only
  components.json               Component allowlist               Uses approved components
  a11y-rules.md                 Accessibility gate                Meets WCAG AA
  visual-baselines/             Visual regression                 Matches baselines
```

---

## Phase 1 Connection: Design OS Draft

Design Jail begins at **Phase 1 (Adaptive Interview)**. The Design OS Draft captured during the interview becomes the foundation for all subsequent UI work.

### Phase 1 → Design Jail Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1 TO DESIGN JAIL PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │
│  │  PHASE 1        │      │  DESIGN OS      │      │  DESIGN JAIL    │     │
│  │  Interview      │─────▶│  Generation     │─────▶│  Enforcement    │     │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘     │
│                                                                              │
│  User selects:            System generates:        Agents constrained by:   │
│  • Palette (or preset)    • tokens.json            • Token allowlist        │
│  • Typography             • components.json        • Component allowlist    │
│  • Density                • patterns/              • A11y gates             │
│  • Corner style           • a11y-rules.md          • Visual regression      │
│  • Theme modes            • baselines/                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Design OS Draft Schema (from Phase 1)

The Design OS Draft captured in Phase 1 follows this structure:

```yaml
design_os_draft:
  version: "draft-20260108"
  status: "draft" | "locked"

  # Color choices → become token values
  palette:
    generation_method: from_brand_asset | from_preset | custom_selection
    colors:
      primary: "#3B82F6"          # → color.brand.primary
      secondary: "#64748B"        # → color.brand.secondary
      background: "#FFFFFF"       # → color.bg.default
      surface: "#F8FAFC"          # → color.bg.surface
      text_primary: "#111827"     # → color.text.primary
      text_secondary: "#6B7280"   # → color.text.secondary
      error: "#EF4444"            # → color.semantic.error
      warning: "#F59E0B"          # → color.semantic.warning
      success: "#10B981"          # → color.semantic.success

  # Typography choices → become font tokens
  typography:
    heading_font: "Inter"         # → typography.font.heading
    body_font: "Inter"            # → typography.font.body
    scale: "standard"             # 1.25 ratio → typography.scale
    base_size: 16                 # → typography.size.base

  # Spacing/density → become spacing tokens
  density:
    mode: "comfortable"           # → spacing.scale multiplier

  # Radius → become radius tokens
  corner_style: "rounded"         # 8px → radius.md

  # Theme → determines which theme files to generate
  theme_modes: ["light", "dark"]
```

### From Draft to Locked Design OS

| Phase | Design OS State | What Happens |
|-------|-----------------|--------------|
| **Phase 1** | Draft | User makes visual choices via interview |
| **Concept Lock** | Draft → v0.1.0 | Choices become initial Design OS version |
| **Gate 2** | v0.1.0 → v1.0.0 | Design OS finalized, baselines captured |
| **Implementation** | v1.x.x | All UI built against locked Design OS |
| **Changes** | via CR | Updates create new Design OS versions |

### Palette Generation in Phase 1 (Constraint-Based)

Phase 1 palette selection is NOT random or free-form. It follows strict constraints:

**MUST Requirements:**
1. All palettes MUST pass WCAG AA contrast (4.5:1 for body text, 3:1 for UI elements)
2. Primary color MUST have sufficient contrast on both light and dark backgrounds
3. Error/warning/success colors MUST meet accessibility standards
4. Generated palettes MUST be validated before user sees them

**Generation Methods:**

| Method | Process | Validation |
|--------|---------|------------|
| **From Brand Asset** | Extract dominant colors from uploaded logo | Auto-adjust for contrast |
| **From Preset** | Select from Itqahn-curated accessible palettes | Pre-validated |
| **Custom Selection** | User picks individual colors | Real-time contrast validation |

**Palette Preview in Phase 1:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PALETTE PREVIEW                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │ Button        │  │ Text Sample   │  │ Card          │                   │
│  │ ┌───────────┐ │  │               │  │ ┌───────────┐ │                   │
│  │ │  Primary  │ │  │ Heading text  │  │ │  Surface  │ │                   │
│  │ │  Button   │ │  │ Body text in  │  │ │  content  │ │                   │
│  │ └───────────┘ │  │ the design.   │  │ │  here     │ │                   │
│  └───────────────┘  └───────────────┘  └───────────────┘                   │
│                                                                              │
│  Contrast Check:                                                             │
│  ├── Primary on Background: 5.2:1 ✓ (WCAG AA: 4.5:1)                       │
│  ├── Text on Background:    12.1:1 ✓                                        │
│  ├── Text on Surface:       11.8:1 ✓                                        │
│  └── Button Text:           4.8:1 ✓                                         │
│                                                                              │
│  ☑ All contrast checks passed                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Contrast Validation Policy:**
```rego
# policies/opa/design/palette_validation.rego
package itqahn.design.palette

import future.keywords.in

deny[msg] {
  # Check body text contrast
  contrast := calculate_contrast(input.colors.text_primary, input.colors.background)
  contrast < 4.5
  msg := sprintf("Body text contrast %v:1 below WCAG AA minimum 4.5:1", [contrast])
}

deny[msg] {
  # Check primary button text contrast
  contrast := calculate_contrast("#FFFFFF", input.colors.primary)
  contrast < 4.5
  msg := sprintf("Primary button text contrast %v:1 below WCAG AA minimum 4.5:1", [contrast])
}

deny[msg] {
  # Check UI element contrast
  contrast := calculate_contrast(input.colors.primary, input.colors.background)
  contrast < 3.0
  msg := sprintf("UI element contrast %v:1 below minimum 3.0:1", [contrast])
}
```

### Wireframe → Component Mapping

Wireframe selections in Phase 1 map to approved Design Jail components:

| Wireframe Element | Maps To Component | Design Jail Rule |
|-------------------|-------------------|------------------|
| Hero section | `Hero` | MUST use `Hero` component |
| Navigation bar | `Nav`, `NavItem` | MUST use navigation components |
| Card grid | `Card`, `Grid` | MUST use `Card` within `Grid` |
| Form inputs | `Input`, `Select`, `Checkbox` | MUST use form components |
| Buttons | `Button` | MUST use `Button` variants only |
| Modal dialogs | `Modal`, `Dialog` | MUST use overlay components |

### Token Pinning from Phase 1

When Concept Lock occurs, the Design OS Draft is pinned:

```json
// concept-lock.json
{
  "design_os_draft": {
    "version": "draft-20260108",
    "pinned_to_design_os": "v0.1.0",
    "tokens_digest": "sha256:abc123...",
    "components_digest": "sha256:def456...",
    "generated_at": "2026-01-08T12:00:00Z"
  }
}
```

All subsequent UI work MUST:
1. Reference the pinned Design OS version
2. Use only tokens defined in that version
3. Use only components defined in that version
4. Pass visual regression against that version's baselines

---

## The Problem

When agents create UI "freely", you get:

| Problem | Impact |
|---------|--------|
| **Inconsistency** | Different colors, spacing, fonts across screens |
| **Accessibility regressions** | Missing focus states, poor contrast |
| **Unmaintainable styling** | Arbitrary CSS values impossible to update |
| **Polish cycles** | Endless back-and-forth on visual details |
| **Brand dilution** | UI doesn't match brand guidelines |

---

## The Rule (Hard)

**Agents MUST NOT write free-form CSS.**

They may only:
- Compose **approved components** from Design OS `components.json`
- Reference **design tokens** from Design OS `tokens.json`
- Use **layout primitives** that are already validated
- Follow **patterns** from Design OS `patterns/`

Exceptions require:
1. Design OS change proposal (RFC)
2. Design Jail Warden approval
3. Addition to `components.json` or `tokens.json`
4. New Design OS version release

---

## Allowed UI Vocabulary

Agents may ONLY use the following when building UI:

| Category | Source | Examples |
|----------|--------|----------|
| **Colors** | `tokens.json` → `color.*` | `color.brand.primary`, `color.text.secondary` |
| **Spacing** | `tokens.json` → `spacing.*` | `spacing.4`, `spacing.8` |
| **Typography** | `tokens.json` → `typography.*` | `typography.font-size.base` |
| **Radius** | `tokens.json` → `radius.*` | `radius.md`, `radius.lg` |
| **Shadows** | `tokens.json` → `shadow.*` | `shadow.md`, `shadow.lg` |
| **Components** | `components.json` → `components[]` | `Button`, `Input`, `Card`, `Modal` |
| **Patterns** | `patterns/*.json` | `auth-flow`, `data-table`, `form-wizard` |
| **Layout** | Pre-approved primitives | `Stack`, `Grid`, `Flex`, `Container` |

### Prohibited

| Category | Example | Detection |
|----------|---------|-----------|
| Raw hex colors | `#3b82f6`, `rgb(59, 130, 246)` | Token lint |
| Raw pixel values | `padding: 16px`, `margin: 8px` | Token lint |
| Inline styles | `style={{ color: 'red' }}` | Design Jail validator |
| Custom CSS classes | `.my-button { ... }` | Design Jail validator |
| Unapproved components | `<FancyButton>` | Component allowlist |
| Tailwind arbitrary | `bg-[#1da1f2]`, `p-[13px]` | Token lint |

---

## Design Tokens

Design tokens are defined in Design OS `tokens.json` using the W3C Design Tokens format. See `docs/03-platform/design-os.md` for the full specification.

### Token Categories

| Category | Examples |
|----------|----------|
| **Colors** | `color.brand.primary`, `color.text.secondary` |
| **Spacing** | `spacing.4`, `spacing.8`, `spacing.16` |
| **Typography** | `typography.font-size.base`, `typography.font-weight.bold` |
| **Radius** | `radius.sm`, `radius.lg` |
| **Shadows** | `shadow.md`, `shadow.lg` |
| **Breakpoints** | `breakpoint.sm`, `breakpoint.lg` |

### Token Format

```json
// design-os/tokens.json (W3C Design Tokens format)
{
  "color": {
    "primary": {
      "50": "#eff6ff",
      "500": "#3b82f6",
      "900": "#1e3a8a"
    },
    "text": {
      "primary": "#111827",
      "secondary": "#6b7280"
    }
  },
  "space": {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem"
  },
  "font": {
    "size": {
      "xs": "0.75rem",
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem"
    }
  },
  "radius": {
    "sm": "0.25rem",
    "md": "0.375rem",
    "lg": "0.5rem",
    "full": "9999px"
  }
}
```

### Token Usage

```typescript
// Correct - using tokens
const Button = styled.button`
  background-color: var(--color-primary-500);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
`;

// WRONG - arbitrary values (will be rejected)
const Button = styled.button`
  background-color: #3b82f6;  // Should use token
  padding: 8px 16px;          // Should use token
  border-radius: 6px;         // Should use token
`;
```

---

## Approved Components

### Component Library

| Category | Components |
|----------|------------|
| **Layout** | Container, Stack, Grid, Flex |
| **Typography** | Heading, Text, Label |
| **Forms** | Input, Select, Checkbox, Radio, Switch |
| **Buttons** | Button, IconButton, ButtonGroup |
| **Feedback** | Alert, Toast, Progress, Spinner |
| **Navigation** | Nav, Tabs, Breadcrumb, Pagination |
| **Data Display** | Table, Card, Badge, Avatar |
| **Overlay** | Modal, Drawer, Dropdown, Tooltip |

### Component Registration

```json
// design/components.json
{
  "components": [
    {
      "name": "Button",
      "variants": ["primary", "secondary", "danger", "ghost"],
      "sizes": ["sm", "md", "lg"],
      "props": ["disabled", "loading", "icon"],
      "accessibility": {
        "role": "button",
        "focusable": true,
        "keyboard": ["Enter", "Space"]
      }
    }
  ]
}
```

### Using Components

```tsx
// Correct - using approved component
import { Button, Stack, Heading } from '@itqahn/design-system';

function Page() {
  return (
    <Stack spacing="md">
      <Heading level={1}>Dashboard</Heading>
      <Button variant="primary" size="md">
        Create Project
      </Button>
    </Stack>
  );
}

// WRONG - custom styling (will be rejected)
function Page() {
  return (
    <div style={{ display: 'flex', gap: '16px' }}>
      <h1 style={{ fontSize: '24px' }}>Dashboard</h1>
      <button style={{ backgroundColor: 'blue' }}>
        Create Project
      </button>
    </div>
  );
}
```

---

## Enforcement Mechanisms

### 1. Static Validation

```python
# tools/validators/design_jail_validator.py
def validate_file(filepath: str) -> list[Violation]:
    violations = []

    # Check for raw CSS values
    raw_patterns = [
        r'color:\s*#[0-9a-fA-F]+',
        r'padding:\s*\d+px',
        r'font-size:\s*\d+px',
        r'margin:\s*\d+px',
    ]

    # Check for inline styles
    inline_patterns = [
        r'style=\{.*\}',
        r'style=".*"',
    ]

    # Validate against allowed tokens/components
    # ...

    return violations
```

### 2. CI Linting

```yaml
# .github/workflows/design-jail.yml
- name: Design Jail Check
  run: |
    python tools/validators/design_jail_validator.py \
      --config design/tokens.json \
      --components design/components.json \
      --source src/
```

### 3. Visual Regression Testing

```yaml
# Storybook + Chromatic
- name: Visual Regression
  run: |
    npx chromatic \
      --project-token=${{ secrets.CHROMATIC_TOKEN }} \
      --exit-zero-on-changes=false
```

### 4. Accessibility Testing

```yaml
- name: Accessibility Check
  run: |
    npx axe-core \
      --exit-on-violation \
      --tags wcag2aa
```

### 5. Policy Gate

```rego
# policies/opa/ui/design_jail.rego
package itqahn.ui

deny[msg] {
  input.file_type == "tsx"
  contains(input.content, "style=")
  msg := "Inline styles are not allowed. Use design system components."
}

deny[msg] {
  input.file_type == "css"
  regex.match(`#[0-9a-fA-F]{6}`, input.content)
  msg := "Raw hex colors are not allowed. Use design tokens."
}
```

---

## Visual Regression Standard

### How It Works

1. **Storybook** renders all components
2. **Screenshots** captured for each story
3. **Compared** against golden masters
4. **Diff** generated for changes
5. **Review** required for visual changes

### Configuration

```javascript
// .storybook/test-runner.js
module.exports = {
  async postVisit(page, context) {
    await expect(page).toHaveScreenshot(
      `${context.id}.png`,
      {
        threshold: 0.01,  // 1% tolerance
        animations: 'disabled',
      }
    );
  },
};
```

### Allowed Tolerances

| Content Type | Tolerance |
|--------------|-----------|
| Static UI | 0% (pixel-perfect) |
| Dynamic timestamps | Masked |
| Avatars | 5% |
| Charts/graphs | 10% |

---

## Accessibility Standard

### Requirements

| Requirement | Standard |
|-------------|----------|
| **WCAG Level** | AA (minimum) |
| **Keyboard navigation** | All interactive elements |
| **Focus management** | Visible focus indicators |
| **Color contrast** | 4.5:1 for text, 3:1 for UI |
| **Screen reader** | All content accessible |

### Automated Checks

```typescript
// axe-core integration
import { axe } from '@axe-core/playwright';

test('page is accessible', async ({ page }) => {
  await page.goto('/');
  const results = await axe(page);
  expect(results.violations).toHaveLength(0);
});
```

### Accessibility Props

Components must support:

```tsx
interface AccessibleProps {
  'aria-label'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-controls'?: string;
  role?: string;
}
```

---

## Adding New Components

### Process

1. **Proposal**: Design team creates RFC
2. **Design review**: UX, accessibility review
3. **Implementation**: Build with tokens only
4. **Testing**: Unit, visual, accessibility
5. **Documentation**: Storybook stories
6. **Approval**: Design Jail Warden signs off
7. **Registration**: Add to `components.json`

### RFC Template

```markdown
# New Component: [Name]

## Purpose
Why is this component needed?

## Design
Link to Figma designs

## Props
| Prop | Type | Description |
|------|------|-------------|

## Accessibility
- Keyboard interactions
- ARIA attributes
- Screen reader behavior

## Examples
Usage examples

## Alternatives Considered
Why not use existing components?
```

---

## Design System Sources

| Source | Integration |
|--------|-------------|
| **Figma** | MCP bridge extracts tokens |
| **Storybook** | Component documentation |
| **Git** | Version control for tokens |

### Figma MCP Bridge

```yaml
# Extract tokens from Figma
mcp:
  figma:
    file_id: "abc123"
    outputs:
      - type: tokens
        path: design/tokens.json
      - type: components
        path: design/components.json
```

---

## Asset Usage Rules

Design Jail extends to **generated assets** through the Asset Factory. All visual assets (icons, illustrations, photos) must comply with Design OS constraints.

### Asset Governance Relationship

```
Design OS (Source)     →     Asset Factory (Generation)     →     Compliant Assets
  tokens.json                   Palette constraints               Uses brand colors
  style-anchors/                Style matching                    Matches style anchor
  a11y-rules.md                 Contrast validation               Meets WCAG AA
```

### Asset Constraints from Design OS

| Constraint | Source | Enforcement |
|------------|--------|-------------|
| **Palette** | `tokens.json` → `color.brand.*` | Asset lint extracts colors, validates against palette |
| **Style** | `style-anchors/*.json` | Embedding similarity check (CLIP) |
| **Contrast** | `a11y-rules.md` | Minimum 4.5:1 for icons with text |
| **Format** | Asset spec schema | Required formats per platform |

### Asset Lint Rules

Asset lint validates generated assets against Design OS:

```yaml
# Asset lint configuration (from Design OS)
asset_lint:
  palette:
    mode: strict
    allowed_variance: 5  # deltaE units from nearest Design OS color
    require_primary: true

  contrast:
    min_ratio: 4.5
    check_regions: ["text", "foreground"]

  format:
    app_icon:
      required: ["png", "svg"]
      max_file_size_kb: 500
      dimensions:
        - 1024x1024 (source)
        - platform-specific variants (auto-generated)

    illustration:
      required: ["svg", "png@2x"]
      max_file_size_kb: 2000
```

### Prohibited Asset Practices

| Practice | Violation | Detection |
|----------|-----------|-----------|
| Off-palette colors | Using #FF5733 when not in `tokens.json` | Color extraction + palette check |
| Missing style anchor | Generating without referencing anchor | Spec validation |
| Low contrast | Icon with < 3:1 contrast ratio | Contrast analysis |
| Unversioned Design OS | Asset spec without Design OS version | Schema validation |
| Unapproved formats | Delivering .psd instead of .png | Format lint |

### Asset Drift Detection

Generated assets are compared against their style anchor:

```
1. Asset generated by Asset Factory
      │
      ▼
2. CLIP embedding computed for output
      │
      ▼
3. Embedding compared to style anchor embedding
      │
      ▼
4. Drift score calculated (cosine distance)
      │
      ├── < 0.10 → Pass (within style)
      │
      ├── 0.10-0.15 → Warn (acceptable, monitor)
      │
      ├── 0.15-0.25 → Repair (attempt edit to correct)
      │
      └── > 0.25 → Regenerate (style mismatch)
```

### Style Anchor Management

Style anchors are versioned in Design OS:

```
design-os/
├── style-anchors/
│   ├── icons/
│   │   ├── modern-flat.json        # Style definition + embedding
│   │   ├── modern-flat.png         # Reference image
│   │   └── gradient-app.json
│   ├── illustrations/
│   │   ├── line-art.json
│   │   └── isometric.json
│   └── photos/
│       ├── lifestyle-bright.json
│       └── product-minimal.json
```

### Policy Enforcement

```rego
# policies/opa/assets/asset_jail.rego
package itqahn.assets

deny[msg] {
  input.asset_spec.design_os_version == ""
  msg := "Asset spec must reference a Design OS version"
}

deny[msg] {
  input.asset_spec.style_anchor == ""
  msg := "Asset spec must reference a style anchor"
}

deny[msg] {
  input.lint_result.palette_violations > 0
  msg := sprintf("Asset has %d palette violations", [input.lint_result.palette_violations])
}

deny[msg] {
  input.drift_score > 0.25
  msg := sprintf("Asset drift %f exceeds threshold 0.25", [input.drift_score])
}
```

### Using Assets in UI

Assets from the Asset Registry integrate with Design Jail compliant UI:

```tsx
// Correct - using registered asset with version
import { AppIcon } from '@itqahn/design-system';

function Header() {
  return (
    <AppIcon
      asset="task-manager-icon"
      version="1.0.0"
      size="md"  // Uses Design OS sizing token
    />
  );
}

// WRONG - hardcoded image URL (will be rejected)
function Header() {
  return (
    <img
      src="/assets/icon.png"  // No version, no registry reference
      style={{ width: '48px' }}  // Raw pixel value
    />
  );
}
```

### Asset Evidence in Design Jail

Design Jail validation includes asset compliance:

| Check | Artifact | Gate |
|-------|----------|------|
| Asset spec valid | `asset-spec.json` | CI |
| Palette compliant | Asset lint report | CI |
| Style anchor matched | Drift score | CI |
| Registered in registry | Registry lookup | Deploy |
| Evidence complete | `asset-evidence.json` | Release |

See `docs/03-platform/asset-factory-imageops.md` for full Asset Factory specification.

---

## Templates

- Design tokens: `templates/design/TOKENS.md`
- Visual regression: `templates/testing/VISUAL-REGRESSION.md`

---

## Related Documents

- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 and Concept Lock
- `docs/01-product/requirements-schema.md` — Design OS Draft schema
- `docs/03-platform/design-os.md` — Design OS specification (source of truth)
- `docs/03-platform/portal-webapp.md` — Phase 1 interview UI
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/05-compliance/evidence-pack.md` — Design evidence requirements
- `docs/07-integrations/mcp/mcp-figma.md` — Figma to Design OS extraction
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration
- `docs/08-agents/agent-catalog.md` — Design Jail Warden agent
- `docs/08-agents/agent-permissions.md` — UI agent restrictions
- `templates/design/` — Design OS artifacts

---

**Version**: 2.2.0 | **Date**: 2026-01-08
