# Visual Regression Template

## Baselines
- Baselines are stored under `design/baselines/`.
- Each baseline must map to a user journey.

## CI steps
1. Build Storybook
2. Render snapshots
3. Compare against baselines
4. Post diff artifacts on PR

## Acceptance
- No diffs on stable components
- Controlled diffs require approval from Design Jail Warden
