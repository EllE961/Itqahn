# Backstage Scaffolder Templates

This directory contains Backstage Scaffolder templates for creating new Itqahn-compliant components.

## Available Templates

| Template | Purpose |
|----------|---------|
| `service-template.yaml` | Create a new backend service |
| `api-template.yaml` | Create a new API service with OpenAPI spec |
| `component-template.yaml` | Create a new Design Jail-compliant UI component |

## Usage

These templates are used via the Backstage Software Templates feature:

1. Navigate to Backstage → Create
2. Select the appropriate template
3. Fill in the required parameters
4. Review and create

## Template Features

### Service Template
- Language selection (TypeScript, Python, Go)
- Compliance tier configuration
- Database and queue options
- Automatic catalog registration

### API Template
- OpenAPI spec generation
- Authentication method configuration
- Rate limiting setup
- API documentation links

### Component Template
- Design Jail compliance built-in
- Storybook story generation
- Test file scaffolding
- Accessibility review flag

## Customization

Templates can be customized by modifying:

1. **Parameters**: Add/modify input fields
2. **Steps**: Add/modify scaffolding actions
3. **Skeleton**: Modify the generated files

## Skeleton Directories

Each template references a skeleton directory containing the actual files to generate:

```
skeleton/           # Service template files
skeleton-api/       # API template files
skeleton-component/ # Component template files
openapi-template/   # OpenAPI spec template
storybook-template/ # Storybook stories template
test-template/      # Test files template
```

## Related

- `docs/03-platform/backstage.md` — Backstage documentation
- `docs/03-platform/design-system-design-jail.md` — Design Jail rules
- `templates/design/` — Design tokens and components

---

**Version**: 2.0.0 | **Date**: 2026-01-06
