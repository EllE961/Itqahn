# Design OS

Design OS is the **versioned, enforceable foundation** for all visual interfaces in Itqahn. It defines the complete vocabulary of tokens, components, patterns, and rules that govern UI creation.

**Design Jail enforcement depends on Design OS.** Without a valid, versioned Design OS, no UI can be built.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DESIGN OS ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     DESIGN OS ARTIFACTS                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐     │   │
│  │  │  tokens   │  │ components│  │  patterns │  │   a11y    │     │   │
│  │  │   .json   │  │   .json   │  │    map    │  │   rules   │     │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     ENFORCEMENT LAYER                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │  CI Checks  │  │ OPA Policies│  │  Validators │               │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     BUILD OUTPUTS                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │  Web App    │  │   Admin     │  │   Mobile    │               │   │
│  │  │ (Next.js)   │  │ Dashboard   │  │(React Native│               │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principle

**Design OS is the Source of Truth for all UI.**

| Rule | Enforcement |
|------|-------------|
| Agents MUST NOT invent styles | Design Jail validator blocks |
| All visual values MUST come from tokens | Token lint in CI |
| All UI elements MUST use approved components | Component allowlist check |
| All layouts MUST use approved patterns | Pattern matcher |
| All releases MUST pin a Design OS version | OPA policy gate |

---

## Design OS Artifacts

### Canonical Artifact Locations

All Design OS artifacts live in the `design-os/` directory (per-repo or in a dedicated Design OS repository):

```
design-os/
├── tokens.json                # W3C Design Tokens format
├── components.json            # Approved component catalog
├── patterns/                  # Flow and pattern specifications
│   ├── auth-flow.json
│   ├── data-table.json
│   └── form-wizard.json
├── content-style.md           # Microcopy rules
├── a11y-rules.md              # WCAG AA requirements
├── visual-baselines/          # Reference screenshots
│   ├── web/
│   ├── mobile/
│   └── admin/
├── CHANGELOG.md               # Version history
└── VERSION                    # Current version
```

For documentation-only repositories like this one, artifacts are located in:
- `templates/design/tokens.json`
- `templates/design/components.json`
- `templates/design/routes.map.json`

### Artifact Specifications

#### tokens.json (W3C Design Tokens Format)

**REQUIRED.** The single source for all design values.

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/v1.0",
  "version": "1.2.0",
  "metadata": {
    "generated_from": "figma:abc123XYZ",
    "generated_at": "2026-01-06T12:00:00Z",
    "design_os_version": "1.2.0"
  },
  "color": {
    "brand": {
      "primary": {
        "$value": "#2563eb",
        "$type": "color",
        "$description": "Primary brand color for CTAs and accents"
      },
      "primary-hover": {
        "$value": "#1d4ed8",
        "$type": "color"
      }
    },
    "semantic": {
      "success": { "$value": "#16a34a", "$type": "color" },
      "warning": { "$value": "#ca8a04", "$type": "color" },
      "error": { "$value": "#dc2626", "$type": "color" },
      "info": { "$value": "#2563eb", "$type": "color" }
    },
    "surface": {
      "background": { "$value": "#ffffff", "$type": "color" },
      "elevated": { "$value": "#f8fafc", "$type": "color" },
      "overlay": { "$value": "rgba(0,0,0,0.5)", "$type": "color" }
    },
    "text": {
      "primary": { "$value": "#0f172a", "$type": "color" },
      "secondary": { "$value": "#475569", "$type": "color" },
      "disabled": { "$value": "#94a3b8", "$type": "color" },
      "inverse": { "$value": "#ffffff", "$type": "color" }
    },
    "border": {
      "default": { "$value": "#e2e8f0", "$type": "color" },
      "strong": { "$value": "#cbd5e1", "$type": "color" }
    }
  },
  "spacing": {
    "0": { "$value": "0px", "$type": "dimension" },
    "1": { "$value": "4px", "$type": "dimension" },
    "2": { "$value": "8px", "$type": "dimension" },
    "3": { "$value": "12px", "$type": "dimension" },
    "4": { "$value": "16px", "$type": "dimension" },
    "5": { "$value": "20px", "$type": "dimension" },
    "6": { "$value": "24px", "$type": "dimension" },
    "8": { "$value": "32px", "$type": "dimension" },
    "10": { "$value": "40px", "$type": "dimension" },
    "12": { "$value": "48px", "$type": "dimension" },
    "16": { "$value": "64px", "$type": "dimension" }
  },
  "radius": {
    "none": { "$value": "0px", "$type": "dimension" },
    "sm": { "$value": "4px", "$type": "dimension" },
    "md": { "$value": "8px", "$type": "dimension" },
    "lg": { "$value": "12px", "$type": "dimension" },
    "xl": { "$value": "16px", "$type": "dimension" },
    "full": { "$value": "9999px", "$type": "dimension" }
  },
  "typography": {
    "font-family": {
      "base": { "$value": "Inter, system-ui, sans-serif", "$type": "fontFamily" },
      "arabic": { "$value": "Cairo, sans-serif", "$type": "fontFamily" },
      "mono": { "$value": "JetBrains Mono, monospace", "$type": "fontFamily" }
    },
    "font-size": {
      "xs": { "$value": "12px", "$type": "dimension" },
      "sm": { "$value": "14px", "$type": "dimension" },
      "base": { "$value": "16px", "$type": "dimension" },
      "lg": { "$value": "18px", "$type": "dimension" },
      "xl": { "$value": "20px", "$type": "dimension" },
      "2xl": { "$value": "24px", "$type": "dimension" },
      "3xl": { "$value": "30px", "$type": "dimension" },
      "4xl": { "$value": "36px", "$type": "dimension" }
    },
    "font-weight": {
      "normal": { "$value": "400", "$type": "fontWeight" },
      "medium": { "$value": "500", "$type": "fontWeight" },
      "semibold": { "$value": "600", "$type": "fontWeight" },
      "bold": { "$value": "700", "$type": "fontWeight" }
    },
    "line-height": {
      "tight": { "$value": "1.25", "$type": "number" },
      "normal": { "$value": "1.5", "$type": "number" },
      "relaxed": { "$value": "1.75", "$type": "number" }
    }
  },
  "shadow": {
    "sm": { "$value": "0 1px 2px rgba(0,0,0,0.05)", "$type": "shadow" },
    "md": { "$value": "0 4px 6px rgba(0,0,0,0.1)", "$type": "shadow" },
    "lg": { "$value": "0 10px 15px rgba(0,0,0,0.1)", "$type": "shadow" },
    "xl": { "$value": "0 20px 25px rgba(0,0,0,0.15)", "$type": "shadow" }
  },
  "breakpoint": {
    "sm": { "$value": "640px", "$type": "dimension" },
    "md": { "$value": "768px", "$type": "dimension" },
    "lg": { "$value": "1024px", "$type": "dimension" },
    "xl": { "$value": "1280px", "$type": "dimension" },
    "2xl": { "$value": "1536px", "$type": "dimension" }
  },
  "motion": {
    "duration": {
      "fast": { "$value": "150ms", "$type": "duration" },
      "normal": { "$value": "250ms", "$type": "duration" },
      "slow": { "$value": "400ms", "$type": "duration" }
    },
    "easing": {
      "default": { "$value": "cubic-bezier(0.4, 0, 0.2, 1)", "$type": "cubicBezier" },
      "in": { "$value": "cubic-bezier(0.4, 0, 1, 1)", "$type": "cubicBezier" },
      "out": { "$value": "cubic-bezier(0, 0, 0.2, 1)", "$type": "cubicBezier" }
    }
  }
}
```

#### components.json (Component Catalog)

**REQUIRED.** The allowlist of approved UI components.

```json
{
  "$schema": "https://itqahn.io/schemas/design-os/components/v1",
  "version": "1.2.0",
  "metadata": {
    "generated_from": "figma:abc123XYZ",
    "generated_at": "2026-01-06T12:00:00Z",
    "design_os_version": "1.2.0"
  },
  "components": [
    {
      "name": "Button",
      "status": "stable",
      "category": "actions",
      "variants": ["primary", "secondary", "danger", "ghost", "link"],
      "sizes": ["sm", "md", "lg"],
      "props": {
        "disabled": { "type": "boolean", "default": false },
        "loading": { "type": "boolean", "default": false },
        "icon": { "type": "string", "optional": true },
        "iconPosition": { "type": "enum", "values": ["left", "right"], "default": "left" },
        "fullWidth": { "type": "boolean", "default": false }
      },
      "tokens_used": [
        "color.brand.primary",
        "color.surface.background",
        "spacing.2",
        "spacing.4",
        "radius.md",
        "typography.font-size.sm",
        "typography.font-size.base"
      ],
      "accessibility": {
        "role": "button",
        "focusable": true,
        "keyboard": ["Enter", "Space"],
        "aria_attributes": ["aria-disabled", "aria-busy"]
      },
      "platform_support": {
        "web": true,
        "mobile": true,
        "admin": true
      }
    },
    {
      "name": "Input",
      "status": "stable",
      "category": "forms",
      "variants": ["default", "filled", "outlined"],
      "sizes": ["sm", "md", "lg"],
      "props": {
        "label": { "type": "string", "required": true },
        "placeholder": { "type": "string", "optional": true },
        "error": { "type": "string", "optional": true },
        "disabled": { "type": "boolean", "default": false },
        "required": { "type": "boolean", "default": false },
        "type": { "type": "enum", "values": ["text", "email", "password", "tel", "url", "number"], "default": "text" }
      },
      "tokens_used": [
        "color.text.primary",
        "color.border.default",
        "color.semantic.error",
        "spacing.2",
        "spacing.3",
        "radius.md"
      ],
      "accessibility": {
        "role": "textbox",
        "focusable": true,
        "keyboard": ["Tab"],
        "aria_attributes": ["aria-label", "aria-describedby", "aria-invalid", "aria-required"]
      },
      "platform_support": {
        "web": true,
        "mobile": true,
        "admin": true
      }
    },
    {
      "name": "Card",
      "status": "stable",
      "category": "layout",
      "variants": ["default", "elevated", "outlined"],
      "props": {
        "padding": { "type": "enum", "values": ["none", "sm", "md", "lg"], "default": "md" },
        "interactive": { "type": "boolean", "default": false }
      },
      "tokens_used": [
        "color.surface.background",
        "color.surface.elevated",
        "color.border.default",
        "spacing.4",
        "spacing.6",
        "radius.lg",
        "shadow.md"
      ],
      "accessibility": {
        "role": "article",
        "focusable": "when interactive"
      },
      "platform_support": {
        "web": true,
        "mobile": true,
        "admin": true
      }
    },
    {
      "name": "Modal",
      "status": "stable",
      "category": "overlay",
      "sizes": ["sm", "md", "lg", "full"],
      "props": {
        "title": { "type": "string", "required": true },
        "onClose": { "type": "function", "required": true },
        "closeOnOverlayClick": { "type": "boolean", "default": true },
        "closeOnEsc": { "type": "boolean", "default": true }
      },
      "tokens_used": [
        "color.surface.background",
        "color.surface.overlay",
        "spacing.6",
        "radius.lg",
        "shadow.xl"
      ],
      "accessibility": {
        "role": "dialog",
        "focusable": true,
        "keyboard": ["Escape", "Tab"],
        "aria_attributes": ["aria-modal", "aria-labelledby", "aria-describedby"],
        "focus_trap": true
      },
      "platform_support": {
        "web": true,
        "mobile": true,
        "admin": true
      }
    },
    {
      "name": "DataTable",
      "status": "stable",
      "category": "data-display",
      "variants": ["default", "compact", "striped"],
      "props": {
        "columns": { "type": "array", "required": true },
        "data": { "type": "array", "required": true },
        "sortable": { "type": "boolean", "default": false },
        "selectable": { "type": "boolean", "default": false },
        "pagination": { "type": "boolean", "default": true }
      },
      "tokens_used": [
        "color.surface.background",
        "color.border.default",
        "color.text.primary",
        "color.text.secondary",
        "spacing.2",
        "spacing.4"
      ],
      "accessibility": {
        "role": "table",
        "keyboard": ["ArrowUp", "ArrowDown", "Space", "Enter"],
        "aria_attributes": ["aria-sort", "aria-selected", "aria-rowcount"]
      },
      "platform_support": {
        "web": true,
        "mobile": false,
        "admin": true
      }
    }
  ],
  "categories": [
    { "name": "actions", "description": "Interactive action components" },
    { "name": "forms", "description": "Form input components" },
    { "name": "layout", "description": "Layout and container components" },
    { "name": "overlay", "description": "Modal and overlay components" },
    { "name": "data-display", "description": "Data presentation components" },
    { "name": "navigation", "description": "Navigation components" },
    { "name": "feedback", "description": "User feedback components" }
  ]
}
```

#### patterns/ (Flow Specifications)

**REQUIRED for complex UIs.** Pre-approved interaction patterns.

```json
// patterns/auth-flow.json
{
  "$schema": "https://itqahn.io/schemas/design-os/pattern/v1",
  "name": "auth-flow",
  "version": "1.0.0",
  "description": "Authentication flow pattern for login/signup",
  "screens": [
    {
      "id": "login",
      "title": "Sign In",
      "components": [
        { "component": "Input", "props": { "label": "Email", "type": "email", "required": true } },
        { "component": "Input", "props": { "label": "Password", "type": "password", "required": true } },
        { "component": "Button", "props": { "variant": "primary", "fullWidth": true } }
      ],
      "transitions": {
        "success": "dashboard",
        "forgot_password": "reset-password",
        "signup": "register"
      }
    }
  ],
  "accessibility": {
    "focus_order": "top-to-bottom",
    "error_announcement": "live-region"
  }
}
```

#### content-style.md (Microcopy Rules)

**REQUIRED.** Voice and tone guidelines.

```markdown
# Content Style Guide

## Voice
- Clear, not clever
- Professional, not formal
- Helpful, not condescending

## Button Labels
| DO | DON'T |
|----|-------|
| Save | Submit |
| Sign in | Login |
| Create account | Register now |
| Delete | Remove permanently |

## Error Messages
- State the problem
- Explain how to fix it
- Never blame the user

Example: "Email address is required" not "You forgot to enter your email"

## Dates and Numbers
- Use user's locale settings
- Relative time for recent events (<7 days)
- Full date for older events
```

#### a11y-rules.md (Accessibility Requirements)

**REQUIRED.** Non-negotiable accessibility rules.

```markdown
# Accessibility Rules (WCAG 2.1 AA)

## Hard Requirements (Blocking)

### Perceivable
- [ ] All images have alt text (or role="presentation" if decorative)
- [ ] Color contrast ≥ 4.5:1 for normal text
- [ ] Color contrast ≥ 3:1 for large text (18px+) and UI components
- [ ] Information not conveyed by color alone
- [ ] Text resizable to 200% without loss of content

### Operable
- [ ] All interactive elements keyboard accessible
- [ ] Visible focus indicator on all focusable elements
- [ ] Focus order follows logical reading order
- [ ] No keyboard traps
- [ ] Skip links for main content
- [ ] Touch targets ≥ 44x44px on mobile

### Understandable
- [ ] Language declared in HTML
- [ ] Form inputs have visible labels
- [ ] Error messages identify the field and describe the error
- [ ] Consistent navigation across pages

### Robust
- [ ] Valid HTML
- [ ] ARIA used correctly or not at all
- [ ] Name, role, value exposed to assistive technology

## Component Requirements

| Component | Required |
|-----------|----------|
| Button | aria-disabled, aria-busy for loading |
| Input | aria-describedby for errors, aria-required |
| Modal | aria-modal, focus trap, Escape to close |
| Menu | aria-expanded, arrow key navigation |
| Toast | role="alert", auto-dismiss ≥5s |
```

#### visual-baselines/ (Reference Screenshots)

**REQUIRED for visual regression.** Golden master screenshots.

```
visual-baselines/
├── web/
│   ├── login-1440x900.png
│   ├── dashboard-1440x900.png
│   └── settings-1440x900.png
├── mobile/
│   ├── login-375x812.png
│   ├── dashboard-375x812.png
│   └── settings-375x812.png
└── admin/
    ├── users-list-1440x900.png
    └── user-detail-1440x900.png
```

---

## Allowed UI Vocabulary

Agents may ONLY use the following when building UI:

### Allowed

| Category | Source | Examples |
|----------|--------|----------|
| **Colors** | `tokens.json` → `color.*` | `color.brand.primary`, `color.text.secondary` |
| **Spacing** | `tokens.json` → `spacing.*` | `spacing.4`, `spacing.8` |
| **Typography** | `tokens.json` → `typography.*` | `typography.font-size.base` |
| **Radius** | `tokens.json` → `radius.*` | `radius.md`, `radius.lg` |
| **Shadows** | `tokens.json` → `shadow.*` | `shadow.md`, `shadow.lg` |
| **Components** | `components.json` → `components[]` | `Button`, `Input`, `Card` |
| **Patterns** | `patterns/*.json` | `auth-flow`, `data-table` |
| **Layout primitives** | Pre-approved | `Stack`, `Grid`, `Flex`, `Container` |

### Prohibited

| Category | Example | Enforcement |
|----------|---------|-------------|
| **Raw hex colors** | `#3b82f6` | Token lint |
| **Raw pixel values** | `padding: 16px` | Token lint |
| **Inline styles** | `style={{ color: 'red' }}` | Design Jail validator |
| **Custom CSS** | `.my-button { ... }` | Design Jail validator |
| **Unapproved components** | Custom `<FancyButton>` | Component allowlist |
| **Direct DOM styling** | `element.style.color = 'blue'` | Design Jail validator |

---

## Enforcement Hooks

### CI Checks

All UI changes trigger these mandatory checks:

#### 1. Token Usage Lint

```yaml
# .github/workflows/design-os.yml
- name: Token Lint
  run: |
    npx design-os-lint \
      --tokens design-os/tokens.json \
      --source "src/**/*.{tsx,css}" \
      --fail-on-violation
```

**MUST be implemented.** Checks:
- No raw hex colors (detects `#[0-9a-fA-F]{3,8}`)
- No raw pixel values (detects `\d+px` outside tokens)
- No raw rem/em values (detects `\d+rem|\d+em`)
- All color references resolve to tokens

#### 2. Component Allowlist Check

```yaml
- name: Component Allowlist
  run: |
    npx design-os-lint \
      --components design-os/components.json \
      --source "src/**/*.tsx" \
      --check-imports \
      --fail-on-unknown
```

**MUST be implemented.** Checks:
- All imported components exist in `components.json`
- Component props match allowed props
- Component variants match allowed variants

#### 3. No Raw CSS Detector

```yaml
- name: No Raw CSS
  run: |
    python tools/validators/design_jail_validator.py \
      --config design-os/tokens.json \
      --components design-os/components.json \
      --source src/ \
      --strict
```

**MUST be implemented.** Detects:
- `style=` attributes in JSX
- CSS files with arbitrary values
- Tailwind arbitrary values `[...]`
- styled-components with hardcoded values

#### 4. Visual Regression Gate

```yaml
- name: Visual Regression
  run: |
    npx playwright test --project=visual-regression
    # Or: npx chromatic --exit-zero-on-changes=false
```

**MUST be implemented.** Configuration:

```typescript
// playwright.config.ts (visual regression)
export default defineConfig({
  testMatch: '**/*.visual.spec.ts',
  snapshotDir: 'design-os/visual-baselines',
  expect: {
    toHaveScreenshot: {
      threshold: 0.01,  // 1% tolerance
      animations: 'disabled',
      caret: 'hide',
    },
  },
});
```

#### 5. Accessibility Gate (axe)

```yaml
- name: Accessibility Check
  run: |
    npx playwright test --project=a11y
    # Runs axe-core on all pages
```

**MUST be implemented.** Configuration:

```typescript
// a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('page meets WCAG AA', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

### OPA Policy Gates

#### Design OS Version Required

```rego
# policies/opa/design_os/version_required.rego
package design_os

deny[msg] {
  input.artifact_type == "ui"
  not input.design_os_version
  msg := "UI artifacts MUST pin a Design OS version"
}

deny[msg] {
  input.artifact_type == "ui"
  input.design_os_version
  not version_exists(input.design_os_version)
  msg := sprintf("Design OS version %s does not exist", [input.design_os_version])
}

deny[msg] {
  input.artifact_type == "ui"
  input.design_os_version
  version_deprecated(input.design_os_version)
  msg := sprintf("Design OS version %s is deprecated", [input.design_os_version])
}
```

#### No Unknown Components

```rego
# policies/opa/design_os/component_allowlist.rego
package design_os

deny[msg] {
  component := input.components_used[_]
  not component_approved(component)
  msg := sprintf("Component '%s' is not in the approved component list", [component])
}

component_approved(name) {
  data.approved_components[_] == name
}
```

#### No Token Drift

```rego
# policies/opa/design_os/token_drift.rego
package design_os

deny[msg] {
  token := input.tokens_used[_]
  not token_exists(token)
  msg := sprintf("Token '%s' does not exist in Design OS", [token])
}

warn[msg] {
  token := input.tokens_used[_]
  token_deprecated(token)
  msg := sprintf("Token '%s' is deprecated, migrate to '%s'", [token, token_replacement(token)])
}
```

### Merge/Release Blocking

| Gate | Failure Action |
|------|----------------|
| Token lint | PR blocked |
| Component allowlist | PR blocked |
| Raw CSS detector | PR blocked |
| Visual regression (diff) | PR blocked until approved |
| Accessibility (critical) | PR blocked |
| Accessibility (serious) | Warning, can proceed |
| Design OS version check | Release blocked |

---

## Governance and Lifecycle

### Roles and Responsibilities

| Role | Responsibility | Permissions |
|------|----------------|-------------|
| **Design Director** | Design OS strategy, major version approval | Approve breaking changes |
| **Design OS Maintainer** | Token/component curation, Figma sync | Write to `design-os/` |
| **Design Jail Warden** | Enforce Design Jail rules, review violations | Block UI PRs |
| **Accessibility Specialist** | WCAG compliance, a11y rules | Write to `a11y-rules.md` |
| **Frontend Architect** | Platform mapping, build integration | Write to patterns |

### Agent Permissions

| Agent Role | Design OS Permissions |
|------------|----------------------|
| Design System Guardian | Read tokens/components, propose changes |
| UI Composer | Read only, compose using approved components |
| Frontend Builder | Read only, build using components |
| Accessibility Auditor | Read all, write a11y findings |
| Design Jail Warden | Read all, block violations |

**No agent may write CSS directly.** All styling must flow through tokens → components.

### Change Process

```
┌──────────────────────────────────────────────────────────────────┐
│                    DESIGN OS CHANGE FLOW                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Proposal                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  RFC with justification, Figma link, impact assessment      │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  2. Review                       ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Design Director + Accessibility + Frontend Architect       │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  3. Figma Export                 ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  MCP Figma → tokens.json, components.json                   │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  4. CI Validation                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Token schema, component contract, a11y rules               │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  5. Visual Regression            ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Generate new baselines, diff against existing              │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  6. Release Tag                  ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  SemVer tag, CHANGELOG update, deprecation notices          │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                  │                                │
│  7. Adoption                     ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Consuming apps upgrade, migration if breaking              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Versioning Strategy (SemVer)

| Change Type | Version Bump | Examples |
|-------------|--------------|----------|
| **Breaking** | MAJOR | Token renamed, component removed, prop removed |
| **Additive** | MINOR | New token, new component, new prop (optional) |
| **Fix** | PATCH | Token value tweak, bug fix, docs update |

#### What Constitutes Breaking

| Breaking | Not Breaking |
|----------|--------------|
| Rename `color.primary` → `color.brand` | Add `color.brand.secondary` |
| Remove `Button.variant.outlined` | Add `Button.variant.subtle` |
| Change `spacing.4` from `16px` to `20px` | Add `spacing.5` = `20px` |
| Remove required prop | Make required prop optional |
| Change prop type | Add new optional prop |

### Backwards Compatibility Policy

1. **Deprecation Period**: Tokens/components MUST be deprecated for 2 minor versions before removal
2. **Migration Path**: Breaking changes MUST include migration guide
3. **Codemods**: SHOULD provide automated migration scripts
4. **Dual Support**: MAY support old + new during transition

```json
// Deprecation in tokens.json
{
  "color": {
    "primary": {
      "$value": "#2563eb",
      "$type": "color",
      "$deprecated": {
        "since": "1.1.0",
        "removeIn": "2.0.0",
        "replacement": "color.brand.primary",
        "migration": "npx design-os-migrate --token color.primary"
      }
    }
  }
}
```

---

## Tenants and Multi-Tenancy

### Baseline Design OS

Itqahn provides a **Baseline Design OS** that all tenants inherit:

```
baseline-design-os/
├── tokens.json         # Core tokens
├── components.json     # Standard components
├── patterns/           # Common patterns
├── a11y-rules.md       # WCAG AA requirements
└── VERSION             # e.g., "1.0.0"
```

**Baseline rules apply to all tenants.** No tenant can bypass a11y requirements or remove components.

### Tenant Design OS Overrides

Tenants MAY customize via **token overrides** and **component variants**:

```json
// tenant-design-os/tokens.json
{
  "$extends": "baseline:1.0.0",
  "overrides": {
    "color.brand.primary": { "$value": "#7c3aed" },
    "color.brand.secondary": { "$value": "#a78bfa" }
  },
  "additions": {
    "color.tenant.accent": { "$value": "#fbbf24", "$type": "color" }
  }
}
```

#### Allowed Overrides

| Category | Allowed | Not Allowed |
|----------|---------|-------------|
| **Brand colors** | ✅ Primary, secondary, accent | ❌ Semantic colors (error, success) |
| **Typography** | ✅ Font family | ❌ Base sizes (breaks a11y) |
| **Spacing** | ❌ Core scale | ✅ Custom additions |
| **Components** | ✅ Add variants | ❌ Remove required props |

### Enterprise Mode

For dedicated instances, tenants may operate a **fully independent Design OS**:

```yaml
# tenant-config.yaml
design_os:
  mode: enterprise  # standard | enterprise
  source:
    type: git
    repo: "tenant-org/design-os"
    branch: main
    path: /
  validation:
    baseline_compatibility: false  # Opt out of baseline
    a11y_rules: strict             # Still enforced
    visual_regression: tenant      # Tenant baselines
```

**Enterprise mode requirements**:
- Dedicated Figma workspace
- Dedicated Design OS repository
- Tenant-managed visual baselines
- Still subject to a11y enforcement

### Security Boundaries

| Boundary | Enforcement |
|----------|-------------|
| **Token isolation** | Tenants cannot read other tenants' tokens |
| **Visual baseline isolation** | Each tenant has isolated baselines |
| **Component registry** | Tenant components namespaced |
| **No cross-tenant styling** | CSS scoped by tenant ID |

```yaml
# Multi-tenant CSS isolation
.tenant-abc123 {
  --color-brand-primary: var(--tenant-abc123-brand-primary);
}

.tenant-def456 {
  --color-brand-primary: var(--tenant-def456-brand-primary);
}
```

---

## Platform Support

### Web (Next.js)

```typescript
// Design token consumption
import { tokens } from '@itqahn/design-os';

const theme = createTheme({
  colors: {
    primary: tokens.color.brand.primary.$value,
  },
  spacing: tokens.spacing,
});
```

### Admin Dashboards

Admin dashboards use the same Design OS with **extended data components**:

```json
// Additional admin components
{
  "components": [
    { "name": "DataTable", "platform_support": { "admin": true, "web": false } },
    { "name": "MetricsCard", "platform_support": { "admin": true, "web": false } },
    { "name": "FilterPanel", "platform_support": { "admin": true, "web": false } }
  ]
}
```

### Mobile (React Native)

Token mapping for React Native:

```json
// design-os/platform-mappings/react-native.json
{
  "mapping": {
    "spacing.4": { "web": "16px", "native": 16 },
    "radius.md": { "web": "8px", "native": 8 },
    "shadow.md": {
      "web": "0 4px 6px rgba(0,0,0,0.1)",
      "native": {
        "shadowColor": "#000",
        "shadowOffset": { "width": 0, "height": 4 },
        "shadowOpacity": 0.1,
        "shadowRadius": 6,
        "elevation": 4
      }
    }
  }
}
```

### Marketing Sites

Marketing sites MAY use extended visual flexibility but MUST still:
- Use tokens for all values
- Pass a11y checks
- Include in Evidence Pack

```json
// marketing-design-os/tokens.json (extends baseline)
{
  "$extends": "baseline:1.0.0",
  "additions": {
    "color.marketing.hero-gradient": {
      "$value": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      "$type": "gradient"
    }
  }
}
```

---

## Design OS in Evidence Pack

Design OS artifacts are **required** in the Evidence Pack for any UI release:

```json
// Evidence Pack manifest (UI release)
{
  "artifacts": {
    "design_os": {
      "version": "1.2.0",
      "tokens_digest": "sha256:abc123...",
      "components_digest": "sha256:def456...",
      "tokens_path": "design-os/tokens.json",
      "components_path": "design-os/components.json"
    },
    "visual_regression": {
      "path": "visual-regression-report.html",
      "digest": "sha256:ghi789...",
      "status": "passed",
      "screenshots_changed": 0,
      "screenshots_total": 45
    },
    "accessibility": {
      "path": "a11y-report.json",
      "digest": "sha256:jkl012...",
      "status": "passed",
      "violations": 0,
      "warnings": 3
    }
  }
}
```

See `docs/05-compliance/evidence-pack.md` for full specification.

---

## Drift Detection

The Drift Checker measures divergence between Design OS and implementation:

### Design Drift Score

```python
# tools/drift-checker/design_drift.py
def calculate_design_drift(design_os: dict, implementation: dict) -> float:
    """
    Returns drift score 0.0 (perfect) to 1.0 (complete divergence).
    """
    token_drift = check_token_usage(design_os['tokens'], implementation['styles'])
    component_drift = check_component_usage(design_os['components'], implementation['components'])
    pattern_drift = check_pattern_adherence(design_os['patterns'], implementation['flows'])

    return weighted_average([
        (token_drift, 0.4),
        (component_drift, 0.4),
        (pattern_drift, 0.2)
    ])
```

### Drift Thresholds

| Drift Score | Action |
|-------------|--------|
| 0.0 - 0.1 | Pass |
| 0.1 - 0.25 | Warning, review recommended |
| 0.25+ | Fail, PR blocked |

---

## Related Documents

- `docs/03-platform/design-system-design-jail.md` — Design Jail enforcement
- `docs/05-compliance/evidence-pack.md` — Evidence requirements
- `docs/07-integrations/mcp/mcp-figma.md` — Figma integration
- `docs/07-integrations/git-integration.md` — Versioning model
- `docs/08-agents/agent-permissions.md` — Agent restrictions
- `templates/design/` — Token and component artifacts

---

**Version**: 2.0.0 | **Date**: 2026-01-06
