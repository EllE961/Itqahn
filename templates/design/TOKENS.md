# Design Tokens

## Rules
- Tokens must have semantic names (e.g., `color.brand.primary`).
- No raw values in application code; tokens only.
- Deprecate tokens; do not rename silently.

## Export
Tokens are exported from design source via `figma-mcp-bridge`.

Files:
- `design/tokens.json`
- `design/components.json`
