# API Contract Template

## OpenAPI
Place OpenAPI files under `openapi/` and ensure CI validates them.

## Versioning
- Backward compatible changes: additive fields, new endpoints
- Breaking changes: new major version + deprecation plan

## Error model
Standard error envelope:
- code
- message
- details
- trace_id
