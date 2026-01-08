# Portal Web Application

The Portal is the primary user interface for interacting with Itqahn. It provides a guided experience for creating software through autonomous agents.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         PORTAL WEBAPP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Intake Wizard  │  │ Workflow Status │  │    Artifacts    │  │
│  │                 │  │                 │  │                 │  │
│  │ • Requirements  │  │ • Real-time     │  │ • PRDs          │  │
│  │ • Constraints   │  │ • Phase gates   │  │ • Code          │  │
│  │ • Approval      │  │ • Approvals     │  │ • Evidence      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    AUTHENTICATION                            ││
│  │        SSO (OIDC) | API Keys | Service Accounts             ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Backend APIs     │
                    │  (BFF + Services)   │
                    └─────────────────────┘
```

---

## Core Features

### 1. Phase 1: Adaptive Interview (Start a Project)

The Phase 1 Adaptive Interview is the entry point for all new projects. It replaces a traditional intake wizard with an intelligent, branching questionnaire that adapts based on user responses.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: ADAPTIVE INTERVIEW DASHBOARD                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐    ┌───────────────────────────────────────┐  │
│  │    MODULE PROGRESS      │    │           LIVE PREVIEW                 │  │
│  │                         │    │                                        │  │
│  │  ● Project Card    ✓   │    │  ┌─────────────────────────────────┐  │  │
│  │  ● Region Profile  ✓   │    │  │     [App Preview with          │  │  │
│  │  ○ Journeys & Scope    │    │  │      current palette,           │  │  │
│  │  ○ Design OS Draft     │    │  │      typography, and            │  │  │
│  │  ○ Wireframe Select    │    │  │      wireframe selection]       │  │  │
│  │  ○ Asset Manifest      │    │  │                                 │  │  │
│  │  ○ Assumptions         │    │  │                                 │  │  │
│  │                         │    │  └─────────────────────────────────┘  │  │
│  │  Progress: 28%          │    │                                        │  │
│  │  ████░░░░░░░░░░         │    │  Palette: Modern Blue                  │  │
│  └─────────────────────────┘    │  Typography: Inter / System            │  │
│                                  │  Layout: Card-based                    │  │
│  ┌─────────────────────────┐    └───────────────────────────────────────┘  │
│  │  CONFIDENCE METER       │                                               │
│  │                         │    ┌───────────────────────────────────────┐  │
│  │  Answered: 12/15        │    │         CURRENT QUESTION               │  │
│  │  "Not sure": 2          │    │                                        │  │
│  │  Risk: Low              │    │  What platforms will your app          │  │
│  │  ██████████░░  85%      │    │  support?                              │  │
│  └─────────────────────────┘    │                                        │  │
│                                  │  ☑ iOS                                 │  │
│  ┌─────────────────────────┐    │  ☑ Android                             │  │
│  │  BUDGET METER           │    │  ☐ Web (PWA)                           │  │
│  │                         │    │  ☐ Web (Traditional)                   │  │
│  │  Est. Tokens: 45K       │    │  ☐ Not sure                            │  │
│  │  Est. Cost: $12.50      │    │  ☐ Other...                            │  │
│  │  Est. Time: 3-5 days    │    │                                        │  │
│  │  ████████░░░░  65%      │    │  ⓘ Why we ask this                     │  │
│  └─────────────────────────┘    │                                        │  │
│                                  │  [Back]  [Skip/Not Sure]  [Continue]  │  │
│  [ Assumptions (2) ▾ ]          └───────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Module-Based Progress (Not Step 1/8)

Progress is shown as **modules completed**, not sequential steps. Users can:
- See which modules are complete, in progress, or pending
- Jump back to any completed module to revise
- Understand overall progress without feeling locked into a sequence

| Module | Icon | Status Indicators |
|--------|------|-------------------|
| Project Card | 📋 | ● Complete, ○ In Progress, ○ Pending |
| Region Profile | 🌍 | Checkmark or circle |
| Journeys & Scope | 🛤️ | Shows count (e.g., "3 journeys") |
| Design OS Draft | 🎨 | Shows palette preview |
| Wireframe Selection | 📐 | Shows selected template thumbnails |
| Asset Manifest | 🖼️ | Shows asset count needed |
| Assumptions | ❓ | Shows count (e.g., "2 assumptions") |

#### Live Preview Panel

The right side of the interview shows a **live preview** that updates as users make choices:

| Choice Made | Preview Updates |
|-------------|-----------------|
| Palette selected | Button colors, backgrounds, text in preview |
| Typography selected | Font rendering in preview |
| Wireframe selected | Layout structure in preview |
| Build type selected | Platform-appropriate preview (mobile frame, browser frame) |

**Preview Components:**
- Sample button with primary color
- Sample text on background (shows contrast)
- Sample card with surface color
- Sample form field
- Navigation preview (if wireframe selected)

#### Confidence Meter

Tracks user certainty across all answers:

```
CONFIDENCE METER
├── Total Questions: 28
├── Answered: 24
├── "Not sure": 3
├── "Other (custom)": 1
├── Confidence Score: 85%
└── Risk Level: Low
```

**Risk Level Thresholds:**
| "Not Sure" Count | Risk Level | Action |
|------------------|------------|--------|
| 0-10% | Low | Proceed to lock |
| 10-20% | Medium | Review assumptions before lock |
| 20-30% | High | Must resolve some before lock |
| >30% | Blocking | Cannot lock until resolved |

#### Budget Meter

Shows estimated resource consumption based on current choices:

```
BUDGET METER
├── Token Estimate: 45,000 tokens
├── Cost Estimate: $12.50
├── Time Estimate: 3-5 days
├── Tenant Limit: 100,000 tokens
└── Usage: 45%
```

**Budget Factors:**
| Choice | Budget Impact |
|--------|---------------|
| Build type | Base multiplier |
| Platform count | +30% per additional platform |
| Journey count | +15% per journey |
| Asset generation | +$2-10 per asset |
| Region complexity | +10-25% for multi-region |

#### Inline "Why We Ask This" Tooltips

Every question has an expandable explanation:

```
ⓘ Why we ask this
┌─────────────────────────────────────────────────────────────────────────────┐
│ Platform selection determines:                                               │
│ • Which app icon formats are needed (iOS, Android, Web)                     │
│ • Which wireframe templates are available                                   │
│ • Estimated build time and cost                                             │
│ • Required compliance checks (App Store, Play Store guidelines)             │
│                                                                              │
│ Choosing "Not sure" will default to the most common selection               │
│ (iOS + Android) and log this as an assumption.                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Assumptions Drawer

Collapsible panel showing all logged assumptions:

```
▾ Assumptions (2)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Platform Selection                                              [Edit]  │
│    You selected "Not sure" - defaulted to iOS + Android                     │
│    Risk: Low | Resolve by: Gate 2                                           │
│                                                                              │
│ 2. Data Residency                                                  [Edit]  │
│    No specific requirement selected - assuming no restrictions              │
│    Risk: Medium | Resolve by: Gate 1 (before lock)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Fast Path (2-4 Minutes)

For users who want to start quickly:

| Fast Path Module | Questions | Duration |
|------------------|-----------|----------|
| Project Card | 3 | 30 sec |
| Region Profile | 2 | 20 sec |
| Journeys (from templates) | 2 | 30 sec |
| Design OS (from presets) | 1 | 20 sec |
| Wireframe (auto-suggest) | 1 | 20 sec |
| Assets (auto-detect) | 1 | 20 sec |
| Confirm | 1 | 30 sec |
| **Total** | **11** | **2-4 min** |

**Fast Path Features:**
- Pre-populated defaults based on build type
- "Use recommended" button on every module
- Single confirmation at end
- Can expand to full interview at any time

#### Save and Resume

Users can pause at any point:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Your progress has been saved automatically.                                  │
│                                                                              │
│ You can close this tab and return anytime.                                  │
│ Your project: "Task Manager App" is saved as draft.                         │
│                                                                              │
│ [ Resume Later ]  [ Continue Now ]                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Auto-save Rules:**
- Save after every answer (30-second debounce)
- Save on navigation away
- Save on visibility change (tab switch)
- Resume shows exactly where user left off

#### Question Format Standards

All Phase 1 questions follow this format:

**Multiple Choice (Primary):**
```
What best describes your app?

☐ Consumer app (B2C)
☐ Business app (B2B)
☐ Internal tool
☐ Marketplace (multi-sided)
☐ Not sure
☐ Other (describe)...
```

**Visual Selection:**
```
Choose a color palette:

[████ Modern Blue ]  [████ Warm Coral ]  [████ Forest Green ]
[████ Slate Gray  ]  [████ Upload brand asset... ]  [████ Custom... ]
```

**Guided Input (for "Other"):**
```
Describe your app type:
┌─────────────────────────────────────────────────────────────────────────────┐
│ A hybrid of consumer and business - we serve individual creators who sell  │
│ to businesses...                                                            │
│                                                                              │
│ (50/200 characters)                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Branching Depth Limits

To prevent interview fatigue:

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max branch depth | 3 levels | Prevents rabbit holes |
| Max questions per module | 8 | Focused modules |
| Max total (fast path) | 15 | Quick start |
| Max total (extended) | 45 | Comprehensive but bounded |
| Session timeout warning | 30 min | Prevent abandonment |

---

### 2. Workflow Status Dashboard

Real-time visibility into agent work:

| Component | Function |
|-----------|----------|
| **Phase indicator** | Current gate (Concept/Experience/RC/Post-Launch) |
| **Activity feed** | Real-time agent actions |
| **Approval queue** | Pending human decisions |
| **Budget meter** | Token consumption vs allocation |
| **Error panel** | Failed activities, policy denials |

**Update mechanism:**
- WebSocket connection to Temporal
- Server-sent events for notifications
- Polling fallback for reliability

### 3. Artifact Browser

Access to all generated artifacts:

| Artifact Type | Actions |
|---------------|---------|
| PRDs | View, edit, export |
| ADRs | View, approve |
| Code | View, link to Git |
| Tests | View results, rerun |
| Evidence Packs | View, download, verify |
| Runbooks | View, edit |

### 4. Change Request Dashboard

Interface for managing changes to locked Concept Lock artifacts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHANGE REQUEST DASHBOARD                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Project: Task Manager App                     Concept Lock v1.0.0           │
│                                                                              │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────┐  │
│  │  ACTIVE CHANGE REQUESTS             │  │  IMPACT PREVIEW            │  │
│  │                                      │  │                             │  │
│  │  CR-001 Add Payment Flow   [Review] │  │  Scope:      +3 journeys   │  │
│  │  Status: Under Review               │  │  Budget:     +$250         │  │
│  │  Type: Feature                       │  │  Timeline:   +3 days       │  │
│  │  Requested: 2 hours ago             │  │  Compliance: PCI upgrade    │  │
│  │                                      │  │  Re-gates:   Risk, Comp.   │  │
│  │  CR-002 Add Spanish locale  [Draft] │  │                             │  │
│  │  Status: Draft                       │  │  ▸ Full impact analysis    │  │
│  │  Type: Region                        │  │                             │  │
│  └─────────────────────────────────────┘  └─────────────────────────────┘  │
│                                                                              │
│  [ + New Change Request ]                                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  APPROVAL QUEUE                                                          ││
│  │                                                                          ││
│  │  CR-001: Awaiting approval from: Security, Compliance, FinOps           ││
│  │  ├── Security: Pending (assigned to @security-team)                     ││
│  │  ├── Compliance: Pending (assigned to @compliance-team)                 ││
│  │  └── FinOps: Approved ✓ (by @cfo-finops, 1 hour ago)                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Change Request Creation Flow

Users request changes through a guided flow:

| Step | Description | User Action |
|------|-------------|-------------|
| 1. Type | Select change type (Feature, Region, Brand, etc.) | Multiple choice |
| 2. Summary | Describe what to change and why | Text input |
| 3. Impact Preview | System shows estimated impact | Review |
| 4. Confirm | User confirms understanding of impact | Checkbox + Submit |

#### Impact Analysis (Automatic)

When a CR is submitted, the system automatically calculates:

| Impact Category | Calculation Method |
|-----------------|-------------------|
| **Scope** | Diff against locked journeys |
| **Budget** | Token/cost estimate for changes |
| **Timeline** | Estimate based on scope delta |
| **Compliance** | Check if tier upgrade needed |
| **Security** | Check if security review required |
| **Design** | Check if Design OS changes needed |
| **Assets** | Check if new assets needed |

#### Change Request States

| State | Description | Available Actions |
|-------|-------------|-------------------|
| **Draft** | User editing, not submitted | Edit, Submit, Discard |
| **Submitted** | Awaiting review | View (user), Assign (admin) |
| **Under Review** | Reviewers assigned | Approve, Reject, Request Info |
| **Approved** | All approvals complete | Implement |
| **Rejected** | Rejected with feedback | Clone (to revise), Close |
| **Implemented** | Changes applied to Concept Lock | View, Audit |

---

### 5. Assets Dashboard

Central interface for Asset Factory operations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ASSETS DASHBOARD                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  Asset Request  │  │  Generation     │  │  Asset Library              │ │
│  │                 │  │  Status         │  │                             │ │
│  │ • New icon      │  │ • In progress   │  │ • Search by name, tag      │ │
│  │ • New illust.   │  │ • Pending lint  │  │ • Filter by type, status   │ │
│  │ • Edit existing │  │ • Drift check   │  │ • Version history          │ │
│  │ • Batch request │  │ • Ready review  │  │ • Usage tracking           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────┐ │
│  │  Approval Queue                      │  │  Incidents                   │ │
│  │                                      │  │                             │ │
│  │ • Assets pending design review      │  │ • Drift alerts              │ │
│  │ • Style anchor approval             │  │ • Lint failures             │ │
│  │ • License verification              │  │ • Budget overruns           │ │
│  └─────────────────────────────────────┘  └─────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Asset Request UI

Submit new asset generation requests:

| Field | Required | Description |
|-------|----------|-------------|
| **Asset Type** | Yes | Icon, illustration, photo, graphic |
| **Style Anchor** | Yes | Select from approved anchors |
| **Description** | Yes | Natural language prompt |
| **Design OS Version** | Auto | Current or specified version |
| **Platforms** | Yes | iOS, Android, Web (multi-select) |
| **Constraints** | Optional | Max colors, aspect ratio, etc. |

**Request workflow:**
```
1. User fills Asset Request form
      │
      ▼
2. Form validates against Design OS
      │
      ▼
3. Request submitted to Asset Factory workflow
      │
      ▼
4. User redirected to Status view
      │
      ▼
5. Real-time updates via WebSocket
```

#### Generation Status Stream

Real-time tracking of asset generation:

| Status | Visual Indicator | User Action |
|--------|------------------|-------------|
| **Queued** | Gray, pending icon | Wait |
| **Generating** | Blue, spinner | Watch progress |
| **Validating** | Yellow, lint icon | Wait |
| **Drift Check** | Orange, similarity % | Review if warning |
| **Pending Review** | Purple, approval icon | Review and approve |
| **Approved** | Green, checkmark | Download/use |
| **Failed** | Red, error icon | View details, retry |

**Live updates include:**
- Generation progress (provider status)
- Lint check results (palette, format, dimensions)
- Drift score with visual similarity preview
- Cost accumulation meter

#### Asset Library

Browse and manage all tenant assets:

| View | Description |
|------|-------------|
| **Grid** | Thumbnail gallery with filters |
| **List** | Table with metadata columns |
| **Detail** | Full asset info, versions, usage |

**Search and filter:**
- Name, tags, description (full-text)
- Asset type (icon, illustration, photo)
- Status (draft, approved, deprecated)
- Date range (created, modified)
- Style anchor reference
- Design OS version

**Asset detail view:**
- Full-size preview with zoom
- All platform variants (iOS, Android, Web)
- Version history with diff view
- Where-used (which apps/pages reference)
- Provenance (generation params, model, seed)
- Download options (original, variants, all)

#### Where-Used Tracking

Track asset references across codebase:

```
Asset: task-manager-icon@1.0.0
├── apps/task-manager/ios/Assets.xcassets/AppIcon.appiconset/
├── apps/task-manager/android/app/src/main/res/mipmap-*/
├── apps/task-manager/web/public/favicon.ico
├── apps/task-manager/web/public/apple-touch-icon.png
└── docs/marketing/app-store-listing.md
```

**Use cases:**
- Impact analysis before asset update
- Deprecation planning
- Compliance audit (which versions deployed where)

#### Asset Incidents

Surface and resolve asset-related issues:

| Incident Type | Trigger | Resolution |
|---------------|---------|------------|
| **Drift Alert** | Drift score > 0.15 | Review, repair, or approve exception |
| **Lint Failure** | Palette/format violation | Fix asset or update Design OS |
| **Stale Asset** | No update > 90 days | Review for deprecation |
| **License Issue** | Model license conflict | Regenerate with compliant model |
| **Budget Overrun** | Cost exceeded threshold | Approve extension or cancel |

**Incident workflow:**
1. Alert appears in dashboard
2. User reviews details and recommendations
3. User takes action (approve, repair, regenerate, deprecate)
4. Resolution logged in audit trail

---

### 6. Operator Mode Dashboard

Operator Mode provides fully automated execution using Claude Code Max subscription. The dashboard is the **only interface**—no terminal interaction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPERATOR MODE DASHBOARD                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │  ACTIVE RUNS                     │  │  KILL SWITCH                    │  │
│  │                                  │  │                                  │  │
│  │  run-01J5ABCD... [Building] ●   │  │  ┌──────────────────────────┐   │  │
│  │  run-01J5EFGH... [Testing]  ●   │  │  │   🛑 EMERGENCY STOP      │   │  │
│  │  run-01J5IJKL... [Merging]  ●   │  │  │                          │   │  │
│  │                                  │  │  │   Stop all workflows     │   │  │
│  │  Workers: 3 / 5 allocated       │  │  │   Freeze all merges      │   │  │
│  │  Cost today: $47.20 / $200      │  │  │   Revoke tool access     │   │  │
│  │                                  │  │  └──────────────────────────┘   │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  RUN DETAIL: run-01J5ABCD                                               ││
│  │                                                                          ││
│  │  Project: Task Manager App          Concept Lock: v1.2.0                ││
│  │  Phase: Build                       Progress: ████████░░░░ 67%         ││
│  │                                                                          ││
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           ││
│  │  │ Interview  │→│   Plan     │→│   Build    │→│   Test     │→ ...      ││
│  │  │     ✓      │ │     ✓      │ │     ●      │ │     ○      │           ││
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘           ││
│  │                                                                          ││
│  │  GitHub Status:                                                         ││
│  │  ├── Issue: #42 (Work Item)                      [View]                 ││
│  │  ├── Branch: feat/run-01J5ABCD-user-auth        [View]                 ││
│  │  ├── PR: #156 (3 commits)                        [View]                 ││
│  │  ├── Checks: 4/5 passing                         [Details]              ││
│  │  └── Merge Queue: Position 2                     [Monitor]              ││
│  │                                                                          ││
│  │  Live Log:                                                               ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ 14:32:01 [agent:backend-builder] Generating user auth module...    │││
│  │  │ 14:32:15 [agent:backend-builder] Writing src/auth/login.ts         │││
│  │  │ 14:32:18 [ci:lint] Running ESLint on changed files...              │││
│  │  │ 14:32:22 [ci:lint] 0 errors, 2 warnings                            │││
│  │  │ 14:32:25 [agent:backend-builder] Committing: feat(auth): add login │││
│  │  │ ▌                                                                   │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [ + Start New Run ]  [ View History ]  [ Cost Report ]  [ Audit Log ]      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Starting a Run

Users initiate runs from the dashboard:

| Step | User Action | System Action |
|------|-------------|---------------|
| 1. Select Project | Choose from dropdown | Load Concept Lock |
| 2. Select Work Items | Choose journeys/features | Generate work plan |
| 3. Confirm | Click "Start Run" | Launch Temporal workflow |
| 4. Monitor | Watch dashboard | Execute via Claude Code |

**Start Run Form:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  START NEW RUN                                                               │
│                                                                              │
│  Project:         [Task Manager App ▾]                                       │
│  Concept Lock:    v1.2.0 (locked 2026-01-05)                                │
│                                                                              │
│  Work Items:                                                                 │
│  ☑ User Authentication     (3 journeys, ~2 hours)                           │
│  ☑ Dashboard Home          (2 journeys, ~1 hour)                            │
│  ☐ Payment Integration     (5 journeys, ~4 hours)                           │
│  ☐ Admin Panel             (4 journeys, ~3 hours)                           │
│                                                                              │
│  Estimated:                                                                  │
│  ├── Duration: 3-4 hours                                                     │
│  ├── Cost: $45-60                                                            │
│  └── Tokens: ~150,000                                                        │
│                                                                              │
│  [ Cancel ]                                        [ Start Run → ]           │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Run Phases and Visibility

Each run progresses through visible phases:

| Phase | What Happens | Dashboard Shows |
|-------|--------------|-----------------|
| **Interview** | Concept Lock loaded | Project summary |
| **Plan** | PRD generated, work items created | PRD link, GitHub issues |
| **Build** | Code generated per work item | Live log, file changes |
| **Test** | Tests run, coverage reported | Test results, coverage % |
| **Review** | Security scan, linting, drift check | Scan results, drift scores |
| **PR** | PR created with Evidence Pack | PR link, check status |
| **Merge** | Enter merge queue, auto-merge | Queue position, merge status |
| **Deploy** | (Optional) Trigger deployment | Deploy status |

#### Live Log Stream

Real-time visibility into Claude Code execution:

```
Live Log Filters: [All ▾] [Agents ▾] [CI ▾] [GitHub ▾]

14:32:01 [agent:backend-builder] Starting activity: generate_auth_module
14:32:05 [agent:backend-builder] Reading Design OS tokens v1.2.0
14:32:08 [agent:backend-builder] Checking Pattern Library for auth-flow
14:32:12 [agent:backend-builder] Generating: src/auth/login.ts
14:32:15 [mcp:github] Creating file: src/auth/login.ts
14:32:18 [ci:lint] ESLint check triggered
14:32:22 [ci:lint] Result: 0 errors, 2 warnings (non-blocking)
14:32:25 [mcp:github] Commit: feat(auth): add login [run-01J5ABCD #42]
14:32:28 [agent:backend-builder] Activity complete: generate_auth_module
```

**Log Features:**
- Filter by source (agent, CI, MCP, GitHub)
- Search within logs
- Download full log
- Jump to related artifact

#### GitHub Integration Panel

Live view of GitHub artifacts created by the run:

```
GitHub Status for run-01J5ABCD
├── Epic Issue: #40 "Task Manager MVP"          [Open]
├── Work Item: #42 "User Authentication"        [In Progress]
├── Branch: feat/run-01J5ABCD-user-auth
│   ├── Commits: 3
│   ├── Files changed: 8
│   └── Lines: +245 / -12
├── PR: #156 "feat(auth): user authentication"
│   ├── Status: Open
│   ├── Checks: 4/5 passing
│   │   ├── ✓ lint
│   │   ├── ✓ test
│   │   ├── ✓ security-scan
│   │   ├── ✓ design-jail
│   │   └── ● build (running)
│   ├── Reviews: 0 required (auto-merge enabled)
│   └── Merge Queue: Position 2 of 3
└── Evidence Pack: evidence-run-01J5ABCD.json   [View]
```

#### Cost and Budget Panel

Real-time cost tracking:

```
Cost Breakdown for run-01J5ABCD
├── Claude Code Tokens: 127,450 (~$38.24)
├── Asset Generation: $4.50 (3 icons)
├── CI Compute: $2.10 (45 min)
└── Total: $44.84

Budget Status:
├── Run Budget: $44.84 / $75.00 (60%)
├── Daily Budget: $147.20 / $200.00 (74%)
└── Monthly Budget: $1,247.00 / $3,000.00 (42%)

⚠ Alert at $60 | 🛑 Hard stop at $75
```

#### Failure Handling UI

When failures occur, the dashboard surfaces them clearly:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠ FAILURE DETECTED: run-01J5ABCD                                           │
│                                                                              │
│  Type: CI Check Failed                                                       │
│  Check: test                                                                 │
│  Details: 3 test failures in src/auth/__tests__/login.test.ts               │
│                                                                              │
│  Auto-Remediation:                                                           │
│  ├── Attempt 1: Regenerate test file (Failed)                               │
│  ├── Attempt 2: Fix type errors (Failed)                                    │
│  └── Attempt 3: Quarantine flaky test (In Progress)                         │
│                                                                              │
│  If auto-fix fails:                                                          │
│  [ Retry Run ]  [ View Logs ]  [ Manual Fix ]  [ Abort Run ]                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Failure Categories and Auto-Remediation:**

| Failure Type | Auto-Remediation | User Escalation |
|--------------|------------------|-----------------|
| **Test failure** | Retry → Regenerate → Quarantine | Manual fix required |
| **Lint error** | Auto-fix → Regenerate | Review lint config |
| **Merge conflict** | Auto-rebase → Split PR | Manual resolution |
| **Check timeout** | Retry (3x) | Investigate CI |
| **Rate limit** | Backoff → Retry | Wait or increase quota |
| **Budget exceeded** | Pause | Approve budget extension |
| **Security scan fail** | Block | Security review required |
| **Asset drift** | Repair → Regenerate | Design review |

#### Kill Switch

Emergency control for immediate halt:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🛑 EMERGENCY STOP                                                           │
│                                                                              │
│  This will immediately:                                                      │
│  ☑ Stop all active Operator Mode runs                                       │
│  ☑ Pause all pending workflows                                              │
│  ☑ Freeze all merge queues                                                  │
│  ☑ Revoke active MCP tool permissions                                       │
│  ☐ Rotate API credentials (optional)                                        │
│                                                                              │
│  Reason (required):                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Security incident detected                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [ Cancel ]                              [ CONFIRM EMERGENCY STOP ]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Kill Switch Actions:**
- Terminates all Temporal workflows in `operator-mode` namespace
- Sets GitHub branch protection to block all merges
- Revokes short-lived MCP credentials
- Logs emergency stop with reason and timestamp
- Notifies configured alert channels
- Optional: triggers secret rotation via Vault

**Recovery from Kill Switch:**
1. Investigate and resolve root cause
2. Admin reviews audit log
3. Admin explicitly re-enables Operator Mode
4. Paused workflows can be resumed or abandoned

#### Rare Failure Resolution UI

For failures that auto-remediation cannot resolve:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MANUAL INTERVENTION REQUIRED                                                │
│                                                                              │
│  Run: run-01J5ABCD                                                          │
│  Failure: Merge Conflict (cannot auto-resolve)                              │
│                                                                              │
│  Conflict in: src/shared/types.ts                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ <<<<<<< HEAD                                                            ││
│  │ export type User = { id: string; email: string; }                       ││
│  │ =======                                                                 ││
│  │ export type User = { id: string; email: string; name: string; }         ││
│  │ >>>>>>> feat/run-01J5ABCD-user-auth                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Options:                                                                    │
│  ○ Accept incoming (our changes)                                            │
│  ○ Accept current (their changes)                                           │
│  ○ Accept both (merge manually)                                             │
│  ● Open in GitHub (resolve in browser)                                      │
│                                                                              │
│  [ Apply Resolution ]  [ Abort and Retry Later ]                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rare Failure Types:**
| Failure | Dashboard Action |
|---------|------------------|
| **Merge conflict** | Show diff, offer resolution options |
| **Flaky test (repeated)** | Show test history, offer quarantine |
| **Security finding (critical)** | Block, require security team review |
| **Asset generation stuck** | Show provider status, offer retry/skip |
| **GitHub rate limit** | Show retry time, offer pause |
| **Corrupted artifact** | Show validation errors, offer regenerate |

#### Run History and Audit

Complete visibility into past runs:

```
Run History                                              [Export Audit Log]
┌─────────────────────────────────────────────────────────────────────────────┐
│ Run ID           │ Project          │ Status    │ Duration │ Cost   │ PRs  │
├─────────────────────────────────────────────────────────────────────────────┤
│ run-01J5MNOP... │ Task Manager     │ ✓ Success │ 2h 34m   │ $52.10 │ 2    │
│ run-01J5IJKL... │ Task Manager     │ ✓ Success │ 1h 12m   │ $28.40 │ 1    │
│ run-01J5EFGH... │ E-Commerce       │ ✗ Failed  │ 45m      │ $15.20 │ 0    │
│ run-01J5ABCD... │ Task Manager     │ ● Running │ 1h 05m   │ $44.84 │ 1    │
└─────────────────────────────────────────────────────────────────────────────┘

Click any row to view:
├── Full execution log
├── All GitHub artifacts (issues, PRs, commits)
├── Evidence Pack
├── Policy decisions made
├── Cost breakdown
└── Audit trail (all actions taken)
```

---

### 7. Parallel Runs UI

Operator Mode executes **multiple Claude Code sessions in parallel** using Git worktrees. The dashboard provides full visibility into all concurrent tasks.

#### Parallel Runs Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PARALLEL RUNS DASHBOARD                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Project: Task Manager App                      Concept Lock: v1.2.0        │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  PARALLEL EXECUTION STATUS                                              │ │
│  │                                                                         │ │
│  │  Active Worktrees: 3 / 5 max                                            │ │
│  │  Tasks Queued: 2                                                        │ │
│  │  Cost This Session: $127.50 / $200.00 budget                            │ │
│  │  ████████████████░░░░  64%                                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  ACTIVE TASKS                                                           │ │
│  │  ───────────────────────────────────────────────────────────────────── │ │
│  │                                                                         │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  🟢 User Authentication            run-01J5ABCD                   │  │ │
│  │  │  ────────────────────────────────────────────────────────────────│  │ │
│  │  │  Status: Testing (4/5 checks passed)                             │  │ │
│  │  │  Branch: feat/run-01J5ABCD-user-auth                             │  │ │
│  │  │  PR: #156 (Auto-merge enabled)                                   │  │ │
│  │  │  Queue Position: 1 of 3                                          │  │ │
│  │  │  Duration: 45m | Cost: $32.10                                    │  │ │
│  │  │  Progress: ████████████████████░░░░  85%                         │  │ │
│  │  │  [View Logs] [View PR] [View Worktree]                           │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  🟡 Dashboard Components           run-01J5EFGH                   │  │ │
│  │  │  ────────────────────────────────────────────────────────────────│  │ │
│  │  │  Status: Building (generating components)                        │  │ │
│  │  │  Branch: feat/run-01J5EFGH-dashboard                             │  │ │
│  │  │  PR: Pending                                                      │  │ │
│  │  │  Duration: 32m | Cost: $24.80                                    │  │ │
│  │  │  Progress: ████████████████░░░░░░░░  65%                         │  │ │
│  │  │  [View Logs] [View Worktree]                                     │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  🟡 Settings Page                  run-01J5IJKL                   │  │ │
│  │  │  ────────────────────────────────────────────────────────────────│  │ │
│  │  │  Status: Building (writing tests)                                │  │ │
│  │  │  Branch: feat/run-01J5IJKL-settings                              │  │ │
│  │  │  PR: Pending                                                      │  │ │
│  │  │  🔒 Lock: src/api/routes/** (exclusive)                          │  │ │
│  │  │  Duration: 15m | Cost: $18.40                                    │  │ │
│  │  │  Progress: ████████░░░░░░░░░░░░░░░░  35%                         │  │ │
│  │  │  [View Logs] [View Worktree]                                     │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  QUEUED TASKS                                                           │ │
│  │  ───────────────────────────────────────────────────────────────────── │ │
│  │                                                                         │ │
│  │  ○ Notifications System      Waiting for: concurrency slot             │ │
│  │  ○ Profile Page              Waiting for: Settings Page (dependency)   │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [ + Add Task ]  [ Manage Locks ]  [ View Merge Queue ]  [ Kill Switch ]   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Task Status Indicators

| Indicator | Meaning | User Action |
|-----------|---------|-------------|
| 🟢 Green | Task progressing normally | Monitor |
| 🟡 Yellow | Task in progress, building/testing | Monitor |
| 🔴 Red | Task failed, needs attention | Review failure |
| ⚪ Gray | Task queued, waiting | Wait or prioritize |
| 🔒 Lock | Task holds exclusive file lock | Shows lock details |
| ⏳ Waiting | Task blocked by dependency | View dependency graph |

#### File Locks Panel

View and manage file locks across parallel tasks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FILE LOCKS                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Active Locks: 3                                                             │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  File/Pattern         │ Type      │ Held By       │ Expires  │ Action │  │
│  │  ─────────────────────┼───────────┼───────────────┼──────────┼─────── │  │
│  │  package-lock.json    │ Exclusive │ run-01J5EFGH  │ 15m      │ [View] │  │
│  │  src/api/routes/**    │ Exclusive │ run-01J5IJKL  │ 30m      │ [View] │  │
│  │  src/shared/types/**  │ Shared    │ 2 tasks       │ -        │ [View] │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Pending Lock Requests: 1                                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Notifications (run-01J5MNOP) waiting for: package-lock.json          │  │
│  │  Estimated wait: ~15 minutes                                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ⚠ Warning: Long-held locks may indicate stuck tasks                        │
│                                                                              │
│  [ Force Release Lock ]  [ View Lock History ]                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Merge Queue Panel

Live view of the GitHub merge queue:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MERGE QUEUE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Queue Status: Active | 3 PRs in queue | Est. completion: 25 min            │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Position │ PR     │ Task            │ Status      │ Checks           │  │
│  │  ─────────┼────────┼─────────────────┼─────────────┼───────────────── │  │
│  │     1     │ #156   │ User Auth       │ Merging     │ ✓✓✓✓✓ (5/5)     │  │
│  │     2     │ #158   │ API Endpoints   │ CI Running  │ ✓✓✓○○ (3/5)     │  │
│  │     3     │ #157   │ Dashboard       │ Waiting     │ ✓✓✓✓✓ (5/5)     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Merge Conflicts Detected:                                                   │
│  ⚠ #157 and #158 may conflict on src/shared/types.ts                        │
│    Resolution: #158 will rebase after #157 merges                           │
│                                                                              │
│  [ View Full Queue ]  [ Reorder ]  [ Emergency Bypass ]                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Dependency Graph View

Visualize task dependencies:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TASK DEPENDENCY GRAPH                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌─────────────────┐                                       │
│                    │  Database Setup │ ✓ Complete                            │
│                    └────────┬────────┘                                       │
│                             │                                                │
│              ┌──────────────┴──────────────┐                                │
│              ▼                              ▼                                │
│  ┌─────────────────┐            ┌─────────────────┐                         │
│  │   API Endpoints │ 🟡 Running │   Auth System   │ 🟢 Testing               │
│  │   run-01J5IJKL  │            │   run-01J5ABCD  │                         │
│  └────────┬────────┘            └────────┬────────┘                         │
│           │                               │                                  │
│           └──────────────┬───────────────┘                                  │
│                          ▼                                                   │
│              ┌─────────────────────┐                                        │
│              │   Dashboard UI      │ ⏳ Blocked                              │
│              │   run-01J5EFGH      │                                        │
│              │   Waiting for:      │                                        │
│              │   - API Endpoints   │                                        │
│              └─────────────────────┘                                        │
│                          │                                                   │
│                          ▼                                                   │
│              ┌─────────────────────┐                                        │
│              │   Profile Page      │ ○ Queued                               │
│              │   Waiting for:      │                                        │
│              │   - Dashboard UI    │                                        │
│              └─────────────────────┘                                        │
│                                                                              │
│  Legend: ✓ Complete  🟢 Testing  🟡 Building  ⏳ Blocked  ○ Queued          │
│                                                                              │
│  [ Zoom In ]  [ Full Screen ]  [ Export Graph ]                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Rare Failure Resolution for Parallel Tasks

When auto-remediation fails on a parallel task, the dashboard presents safe options:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠ INTERVENTION REQUIRED: run-01J5EFGH (Dashboard Components)               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Failure: Merge Conflict (auto-rebase failed)                               │
│  Conflicting File: src/shared/types.ts                                      │
│  Caused By: PR #156 merged, changed same file                               │
│                                                                              │
│  Auto-remediation attempts:                                                  │
│  ├── Attempt 1: Auto-rebase                    ✗ Failed (conflict)          │
│  ├── Attempt 2: Regenerate conflicting file   ✗ Failed (type mismatch)     │
│  └── Attempt 3: Split PR                       ✗ N/A (single-file conflict)│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Conflict Preview                                                        ││
│  │                                                                          ││
│  │  <<<<<<< HEAD (main)                                                     ││
│  │  export type User = { id: string; email: string; role: UserRole; }      ││
│  │  =======                                                                 ││
│  │  export type User = { id: string; email: string; name: string; }        ││
│  │  >>>>>>> feat/run-01J5EFGH-dashboard                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Choose Resolution:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ○ Accept main (discard our name field, keep role field)                ││
│  │    Risk: Low | Our changes will need to be re-added                      ││
│  │                                                                          ││
│  │  ○ Accept ours (keep our name field, lose role field)                   ││
│  │    Risk: Medium | May break other code relying on role                   ││
│  │                                                                          ││
│  │  ● Merge both (add both role and name fields)     [RECOMMENDED]         ││
│  │    Risk: Low | Both changes preserved                                    ││
│  │                                                                          ││
│  │  ○ Regenerate with updated context                                       ││
│  │    Risk: Medium | Claude Code will regenerate with latest main          ││
│  │                                                                          ││
│  │  ○ Open in GitHub (manual resolution)                                    ││
│  │    Risk: Low | Full control, but requires manual work                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Other Affected Tasks:                                                       │
│  ├── run-01J5IJKL (Settings) - may conflict if not resolved                │
│  └── run-01J5MNOP (Notifications) - waiting for this resolution            │
│                                                                              │
│  [ Apply Resolution ]    [ Abort Task ]    [ View Full Conflict ]           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Worktree Conflict Storm Resolution

When multiple worktrees have cascading conflicts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔴 CONFLICT STORM DETECTED                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Multiple parallel tasks have interconnected conflicts.                      │
│  Auto-remediation cannot resolve without potential data loss.                │
│                                                                              │
│  Affected Tasks: 3                                                           │
│  ├── run-01J5EFGH (Dashboard) - conflicts with main                         │
│  ├── run-01J5IJKL (Settings) - conflicts with Dashboard                     │
│  └── run-01J5MNOP (Notifications) - conflicts with Settings                 │
│                                                                              │
│  Conflicting Files:                                                          │
│  ├── src/shared/types.ts        (3 tasks)                                   │
│  ├── src/api/routes/index.ts    (2 tasks)                                   │
│  └── package.json               (2 tasks)                                   │
│                                                                              │
│  Recommended Resolution Strategy:                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ● Serialize conflicting tasks                         [RECOMMENDED]    ││
│  │    1. Pause all conflicting tasks                                        ││
│  │    2. Complete run-01J5EFGH first (highest priority)                     ││
│  │    3. Rebase and resume run-01J5IJKL                                     ││
│  │    4. Rebase and resume run-01J5MNOP                                     ││
│  │    Estimated additional time: +45 minutes                                ││
│  │                                                                          ││
│  │  ○ Abort conflicting tasks, retry later                                  ││
│  │    All progress in conflicting tasks will be saved as draft PRs          ││
│  │    Estimated cost saved: $35.00                                          ││
│  │                                                                          ││
│  │  ○ Resolve each conflict manually (advanced)                             ││
│  │    Opens conflict resolution UI for each file                            ││
│  │    Requires manual Git knowledge                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [ Apply Strategy ]    [ Activate Kill Switch ]    [ Contact Support ]      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Flaky Test Detection UI

When the system detects flaky tests:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠ FLAKY TEST DETECTED                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Test: src/auth/__tests__/login.test.ts → "should redirect after login"    │
│  Task: run-01J5ABCD (User Authentication)                                   │
│                                                                              │
│  Flakiness Score: 67% (passed 2/3 runs in last 24 hours)                    │
│                                                                              │
│  History:                                                                    │
│  ├── 2 hours ago:  ✗ Failed  (timeout after 30s)                            │
│  ├── 1 hour ago:   ✓ Passed  (1.2s)                                         │
│  └── Just now:     ✗ Failed  (timeout after 30s)                            │
│                                                                              │
│  Flaky Test Budget:                                                          │
│  ├── Quarantined tests: 3 / 10 max                                          │
│  └── This run retries used: 4 / 5 max                                       │
│                                                                              │
│  Options:                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ● Quarantine test (test runs but doesn't block merge)  [RECOMMENDED]  ││
│  │    Test will be marked as flaky and tracked separately                   ││
│  │                                                                          ││
│  │  ○ Retry with extended timeout (60s instead of 30s)                      ││
│  │    May fix timeout-related flakiness                                     ││
│  │                                                                          ││
│  │  ○ Skip test for this run                                                ││
│  │    Test will not run, PR proceeds without this coverage                  ││
│  │                                                                          ││
│  │  ○ Investigate and fix                                                   ││
│  │    Claude Code will analyze test and attempt fix                         ││
│  │    Estimated time: +15 minutes                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [ Apply Decision ]    [ View Test Details ]    [ View Test History ]       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Ship Flow (Single Merge Point)

When all parallel tasks complete, the dashboard presents a unified "Ship" flow:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          READY TO SHIP                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  All tasks complete for: Task Manager MVP v1.0.0                            │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  COMPLETED TASKS                                                        │ │
│  │                                                                         │ │
│  │  ✓ User Authentication          PR #156  Merged ✓                       │ │
│  │  ✓ Dashboard Components         PR #157  Merged ✓                       │ │
│  │  ✓ Settings Page                PR #158  Merged ✓                       │ │
│  │  ✓ Notifications                PR #159  Merged ✓                       │ │
│  │  ✓ Profile Page                 PR #160  Merged ✓                       │ │
│  │                                                                         │ │
│  │  Total: 5 PRs merged | 127 commits | 2,450 lines added                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  VALIDATION SUMMARY                                                     │ │
│  │                                                                         │ │
│  │  ✓ All CI checks passed                                                 │ │
│  │  ✓ Security scan clean (0 critical, 0 high)                             │ │
│  │  ✓ Design Jail compliance verified                                      │ │
│  │  ✓ Test coverage: 87.3% (threshold: 80%)                                │ │
│  │  ✓ Evidence Pack complete and signed                                    │ │
│  │  ⚠ 2 quarantined flaky tests (non-blocking)                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  COST SUMMARY                                                           │ │
│  │                                                                         │ │
│  │  Claude Code tokens: 425,000                     $127.50                │ │
│  │  Asset generation: 8 icons                       $12.00                 │ │
│  │  CI compute: 3.5 hours                           $8.75                  │ │
│  │  ─────────────────────────────────────────────────────                  │ │
│  │  Total:                                          $148.25                │ │
│  │  Budget:                                         $200.00                │ │
│  │  Remaining:                                      $51.75                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Ready to create release?                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Release Version: v1.0.0                                                 ││
│  │  Tag: v1.0.0                                                             ││
│  │  Changelog: Auto-generated from commit messages                          ││
│  │  Evidence Pack: Will be attached to release                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [ Preview Changelog ]  [ Preview Release Notes ]  [ 🚀 Create Release ]   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 8. Track Assurance Panel

The Track Assurance panel provides real-time visibility into drift detection and review workflow status.

#### Assurance Summary Card (Project Dashboard)

```
┌─────────────────────────────────────────────────────────┐
│  TRACK ASSURANCE                              [●] Live  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Drift Score:  ████████░░  0.18 (Yellow)               │
│                                                         │
│  Plan:     ██░░░░░░░░  0.12                            │
│  Code:     ███░░░░░░░  0.22                            │
│  UI:       █░░░░░░░░░  0.08                            │
│  Behavior: ██░░░░░░░░  0.15                            │
│                                                         │
│  Last Check: 2 min ago    Next: Post-Build             │
│                                                         │
│  [Stop & Review]                    [View History]     │
└─────────────────────────────────────────────────────────┘
```

#### Review Checkpoint Modal

When workflow enters `PAUSED_FOR_REVIEW`, operator sees:

```
┌─────────────────────────────────────────────────────────┐
│  REVIEW CHECKPOINT                          ckpt-abc123 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⚠️ Drift threshold exceeded (Orange: 0.42)             │
│                                                         │
│  Trigger: Automatic (post-build checkpoint)            │
│  Paused At: 2026-01-08 14:30:00 UTC                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ DRIFT ITEMS (3)                                 │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ● Code: src/auth/login.ts                       │   │
│  │   Expected: OAuth2 PKCE flow                    │   │
│  │   Actual: Basic token exchange                  │   │
│  │   Severity: HIGH                                │   │
│  │                                                 │   │
│  │ ● Code: src/api/users.ts                        │   │
│  │   Expected: Rate limiting per spec 4.1          │   │
│  │   Actual: No rate limiting implemented          │   │
│  │   Severity: MEDIUM                              │   │
│  │                                                 │   │
│  │ ● Behavior: POST /api/login                     │   │
│  │   Expected: 401 on invalid credentials          │   │
│  │   Actual: 500 error thrown                      │   │
│  │   Severity: HIGH                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Resume: Replan]  [Resume: As-Is]  [Rollback]  [End]  │
│                                                         │
│  ○ As-Is requires justification (min 50 chars)         │
└─────────────────────────────────────────────────────────┘
```

#### Resume As-Is Justification

```
┌─────────────────────────────────────────────────────────┐
│  RESUME AS-IS JUSTIFICATION                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  You are resuming without addressing drift items.       │
│  This action will be recorded in the audit trail.       │
│                                                         │
│  Justification (required, min 50 characters):           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Drift in auth module is acceptable; PKCE will   │   │
│  │ be added in follow-up ticket ACME-1234. Rate    │   │
│  │ limiting deferred to v2 per product decision.   │   │
│  │                                                 │   │
│  │ (142/50 characters)                    ✓        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Acknowledged Risks:                                    │
│  ☑ code:src/auth/login.ts:no_pkce                      │
│  ☑ code:src/api/users.ts:no_rate_limit                 │
│  ☑ behavior:login:500_error                            │
│                                                         │
│  [ Cancel ]                      [ Confirm Resume ]     │
└─────────────────────────────────────────────────────────┘
```

#### Drift History Timeline

```
┌─────────────────────────────────────────────────────────┐
│  DRIFT HISTORY                               run-abc123 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Drift Score Over Time                                  │
│  ─────────────────────────────────────────────────────  │
│  1.0 ┤                                                  │
│      │                                                  │
│  0.5 ┤                              ●──────● PAUSED     │
│      │                           ╱                      │
│  0.3 ┤- - - - - - - - - - - - -╱- - - - - (threshold)  │
│      │                      ╱                           │
│      │                   ╱                              │
│  0.0 ┼──●────●────●───●─                               │
│      └──┬────┬────┬───┬────┬────┬───                   │
│        Init Plan Build Build Test  Now                  │
│                   :1    :2                              │
│                                                         │
│  Checkpoints:                                           │
│  ├── ckpt-001  Post-Plan   0.08  ✓ Passed              │
│  ├── ckpt-002  Post-Build  0.22  ✓ Passed              │
│  ├── ckpt-003  Post-Build  0.42  ⚠ Soft Pause          │
│  └── ckpt-004  Post-Test   -     ○ Pending             │
│                                                         │
│  [ Export Report ]                    [ Configure ]     │
└─────────────────────────────────────────────────────────┘
```

---

### 9. Legacy Rebuild Panel

The Legacy Rebuild panel guides operators through importing and modernizing existing projects.

#### Import Wizard Summary

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

#### Rebuild Progress Panel

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

#### Parity Results Panel

```
┌─────────────────────────────────────────────────────────┐
│  PARITY VERIFICATION                    rebuild-abc123  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Overall Parity Score: ████████████████████  0.97       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PARITY BY CATEGORY                              │   │
│  │                                                 │   │
│  │ API Parity:       ████████████████████  0.99   │   │
│  │   45/45 endpoints match                         │   │
│  │   Avg response time: -29% (improvement)         │   │
│  │                                                 │   │
│  │ Database Parity:  ████████████████████  1.00   │   │
│  │   12/12 tables verified                         │   │
│  │   50,000 rows compared, 0 discrepancies         │   │
│  │                                                 │   │
│  │ UI Parity:        ████████████████░░░░  0.88   │   │
│  │   14/15 pages match                             │   │
│  │   ⚠ /settings: 0.88 (new design system fonts)  │   │
│  │                                                 │   │
│  │ Behavior Parity:  ████████████████████  1.00   │   │
│  │   120/120 scenarios passed                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ⚠ 1 warning: UI parity on /settings page below 0.95  │
│    Reason: New design system fonts applied             │
│    [Acknowledge Warning]                               │
│                                                         │
│  [Export Report]                       [Plan Cutover]  │
└─────────────────────────────────────────────────────────┘
```

#### Cutover Panel

```
┌─────────────────────────────────────────────────────────┐
│  CUTOVER CHECKLIST                      rebuild-abc123  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Scheduled: 2026-01-15 02:00 UTC (low traffic window)  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PRE-CUTOVER CHECKLIST                           │   │
│  │                                                 │   │
│  │ ✓ Final parity verification passed             │   │
│  │ ✓ Stakeholder sign-off obtained                │   │
│  │ ✓ Rollback procedure tested                    │   │
│  │ ● Monitoring dashboards ready                  │   │
│  │ ○ Final security scan                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ CUTOVER STEPS                                   │   │
│  │                                                 │   │
│  │ 1. Enable maintenance mode           ~1 min    │   │
│  │ 2. Database migration (if needed)    ~5 min    │   │
│  │ 3. Switch DNS/routing                ~2 min    │   │
│  │ 4. Smoke test critical paths         ~5 min    │   │
│  │ 5. Disable maintenance mode          ~1 min    │   │
│  │                                                 │   │
│  │ Total estimated: 14 minutes                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Rollback triggers (automatic):                         │
│  • Error rate spike >5%                                │
│  • Response time >2x baseline                          │
│  • Critical endpoint failure                           │
│                                                         │
│  [Run Final Checks]  [Preview Rollback]  [Start Cutover]│
└─────────────────────────────────────────────────────────┘
```

---

### 10. Improvement Pipeline Panel

The Improvement Pipeline panel provides visibility into Itqahn's self-improvement system.

#### Pipeline Overview

```
┌─────────────────────────────────────────────────────────┐
│  IMPROVEMENT PIPELINE                          [Filter] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SIGNALS (Last 7 Days)                                  │
│  ├── Operator Feedback: 47 signals                      │
│  ├── Drift Reviews: 23 patterns                         │
│  ├── CI Failures: 12 patterns                           │
│  └── Analytics: 8 signals                               │
│                                                         │
│  CANDIDATES                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ● imp-2026-0108-001  Auth refresh tokens        │   │
│  │   Status: Canary (5%)   Eval: PASSED            │   │
│  │   Source: 12 feedback signals                   │   │
│  │                                        [Details]│   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ● imp-2026-0107-003  TypeScript strict mode     │   │
│  │   Status: Rollout (50%)   Eval: PASSED          │   │
│  │   Source: CI failure analysis                   │   │
│  │                                        [Details]│   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ○ imp-2026-0108-002  Wizard UX simplification   │   │
│  │   Status: Evaluation   Stage: Integration       │   │
│  │   Source: Product analytics                     │   │
│  │                                        [Details]│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [View All Candidates]              [Signal Analysis]  │
└─────────────────────────────────────────────────────────┘
```

#### Candidate Detail View

```
┌─────────────────────────────────────────────────────────┐
│  IMPROVEMENT CANDIDATE              imp-2026-0108-001   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Add refresh token handling to auth generator           │
│                                                         │
│  Status: ████████████░░░░░░░░ Canary (5%)              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ EVALUATION PIPELINE                             │   │
│  │                                                 │   │
│  │ ✓ Static Analysis      45s   PASSED            │   │
│  │ ✓ Unit Evaluation      3m    PASSED            │   │
│  │ ✓ Integration Eval     20m   PASSED            │   │
│  │ ● Canary Evaluation    18h   IN PROGRESS       │   │
│  │ ○ Gradual Rollout      -     PENDING           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ CANARY METRICS (Last 18h)                       │   │
│  │                                                 │   │
│  │ Error Rate:     0.1%  (threshold: 5%)    ✓     │   │
│  │ Auth Drift:     0.18  (target: <0.15)    ○     │   │
│  │ Latency p99:    120ms (baseline: 115ms)  ✓     │   │
│  │ User Feedback:  4.5/5 (baseline: 4.2/5)  ✓     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Pause Rollout]  [View PR]  [Trigger Rollback]        │
└─────────────────────────────────────────────────────────┘
```

#### Improvement Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  ITQAHN IMPROVEMENT METRICS                    Last 30 Days │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DORA METRICS                                               │
│  ┌────────────────┬────────────────┬────────────────┐      │
│  │ Deploy Freq    │ Lead Time      │ Failure Rate   │      │
│  │ 2.3/day ↑      │ 4.2 days ↓     │ 2.1% ↓         │      │
│  │ (target: 1/day)│ (target: <7d)  │ (target: <5%)  │      │
│  └────────────────┴────────────────┴────────────────┘      │
│                                                              │
│  WORKFLOW PERFORMANCE                                        │
│  ┌────────────────┬────────────────┬────────────────┐      │
│  │ Run Success    │ Drift Detect   │ Satisfaction   │      │
│  │ 96.2% ↑        │ 92.1% ↑        │ 4.3/5.0 ↑      │      │
│  │ (target: >95%) │ (target: >90%) │ (target: >4.0) │      │
│  └────────────────┴────────────────┴────────────────┘      │
│                                                              │
│  IMPROVEMENT PIPELINE                                        │
│  ├── Signals Collected (30d):     1,247                     │
│  ├── Candidates Generated:        23                        │
│  ├── Candidates in Evaluation:    5                         │
│  ├── Candidates Deployed:         18                        │
│  └── Candidates Rolled Back:      1                         │
│                                                              │
│  [View Details]  [Export Report]  [Configure Alerts]        │
└─────────────────────────────────────────────────────────────┘
```

#### Feedback Collection Widget

```
┌─────────────────────────────────────────────────────────┐
│  RUN FEEDBACK                              run-abc123   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  How was this run?                                      │
│                                                         │
│  ★ ★ ★ ★ ☆   [4/5 rating]                             │
│                                                         │
│  What could be improved?                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ The generated auth code didn't handle refresh   │   │
│  │ tokens correctly. Had to manually fix.          │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Category:                                              │
│  ○ Code Quality    ○ Test Coverage    ● Missing Feature│
│  ○ Performance     ○ Documentation    ○ Other          │
│                                                         │
│  [Submit Feedback]              [Skip]                 │
└─────────────────────────────────────────────────────────┘
```

---

## Background Execution Model

The portal is a **thin client** over background workflows:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Browser    │    │     BFF      │    │   Temporal   │
│   (React)    │    │   (Node.js)  │    │   (Workers)  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │ 1. Create request │                   │
       │──────────────────▶│                   │
       │                   │ 2. Start workflow │
       │                   │──────────────────▶│
       │                   │                   │
       │                   │ 3. Return ID      │
       │◀──────────────────│◀──────────────────│
       │                   │                   │
       │ 4. Subscribe      │                   │
       │──────────────────▶│ 5. Query workflow │
       │                   │──────────────────▶│
       │                   │                   │
       │ 6. Stream updates │                   │
       │◀─ ─ ─ ─ ─ ─ ─ ─ ─│◀─ ─ ─ ─ ─ ─ ─ ─ ─│
```

**Key principle**: Users don't wait for agent work. They submit requests and monitor progress.

### Long-Running Operations

| Operation | Duration | User Experience |
|-----------|----------|-----------------|
| PRD generation | 1-5 min | Progress indicator, can navigate away |
| Full feature | Hours-days | Email/Slack notifications at gates |
| Code review | 5-15 min | Notification when ready |
| Deploy | 10-30 min | Canary progress visualization |
| Asset generation | 30s-5 min | Real-time status stream in Assets Dashboard |
| Batch asset generation | 5-30 min | Batch progress view, per-asset status |

---

## User Roles

| Role | Capabilities |
|------|--------------|
| **Owner** | Full access to all projects, billing |
| **Admin** | Manage team, configure integrations |
| **Developer** | Create projects, view all artifacts |
| **Viewer** | Read-only access to assigned projects |
| **Approver** | Can approve gates, no edit access |

---

## Authentication

### Supported Methods

| Method | Use Case |
|--------|----------|
| **OIDC/SSO** | Enterprise users (Okta, Azure AD, Google) |
| **API Keys** | Programmatic access, CI integration |
| **Service Accounts** | Agent-to-API communication |

### Session Management

```yaml
session:
  duration: 8h
  refresh_window: 1h
  max_concurrent: 5
  idle_timeout: 30m
```

### MFA Requirements

| Risk Level | MFA Required |
|------------|--------------|
| Baseline | Recommended |
| Sensitive | Required for approvals |
| Regulated | Required always |

---

## Real-Time Updates

### WebSocket Protocol

```javascript
// Connect to workflow updates
const ws = new WebSocket(`wss://portal/ws/workflows/${workflowId}`);

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  switch (update.type) {
    case 'ACTIVITY_STARTED':
      // Show activity in progress
      break;
    case 'ACTIVITY_COMPLETED':
      // Update progress
      break;
    case 'APPROVAL_REQUIRED':
      // Show approval UI
      break;
    case 'GATE_PASSED':
      // Update phase indicator
      break;
  }
};
```

### Notification Channels

| Channel | Events |
|---------|--------|
| **In-app** | All workflow updates |
| **Email** | Gate approvals, completions, failures |
| **Slack** | Configurable per project |
| **Webhook** | Programmatic integration |

---

## API Integration

### REST API

```yaml
openapi: 3.0.0
paths:
  /api/v1/projects:
    post:
      summary: Create new project
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectRequest'

  /api/v1/workflows/{id}/status:
    get:
      summary: Get workflow status

  /api/v1/workflows/{id}/approve:
    post:
      summary: Approve pending gate
```

### GraphQL (Optional)

For complex queries across artifacts:

```graphql
query ProjectStatus($id: ID!) {
  project(id: $id) {
    status
    currentPhase
    budget {
      allocated
      consumed
    }
    artifacts {
      prds { id, status }
      code { repository, branch }
      evidence { id, signed }
    }
  }
}
```

---

## UI Architecture

### Technology Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18+ |
| State | React Query + Zustand |
| Styling | Design tokens (CSS variables) |
| Components | Design system components |
| Testing | Vitest + Playwright |

### Design Jail Compliance

The portal itself follows Design Jail rules:

- All styling via design tokens
- Only approved components
- Visual regression tests
- Accessibility (WCAG AA)

---

## Offline Support

Limited offline capability:

| Feature | Offline Support |
|---------|-----------------|
| View cached artifacts | Yes |
| Submit new requests | Queued |
| Approve gates | No (requires auth) |
| View real-time status | No |

---

## Related Documents

- `docs/00-overview/principles.md` — Operator Mode audit principles
- `docs/01-product/lifecycle-phase-gates.md` — Phase 1 definition and Concept Lock
- `docs/01-product/requirements-schema.md` — Phase 1 output schemas
- `docs/03-platform/backstage.md` — Developer portal integration
- `docs/03-platform/design-system-design-jail.md` — UI constraints and Phase 1 connection
- `docs/03-platform/asset-factory-imageops.md` — Asset Factory specification
- `docs/03-platform/track-assurance.md` — Track Assurance specification
- `docs/03-platform/legacy-rebuild.md` — Legacy Rebuild specification
- `docs/04-security/security-model.md` — Portal security
- `docs/06-operations/runbooks.md` — Operator Mode failure runbooks
- `docs/06-operations/incident-response.md` — Kill switch and incident handling
- `docs/06-operations/itqahn-continuous-improvement.md` — Self-improvement specification
- `docs/07-integrations/git-integration.md` — GitHub Automation Program
- `docs/07-integrations/mcp/mcp-assets.md` — Assets MCP integration

---

**Version**: 2.4.0 | **Date**: 2026-01-08
