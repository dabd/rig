# API Documentation Checklist

Additional checks for API documentation (endpoint specs, OpenAPI descriptions, integration guides). Apply these alongside the base audit checklist.

## Endpoint Consistency

- Every endpoint listed in overview/index documents exists in the detailed spec, and vice versa
- HTTP methods match between overview and detail (e.g., overview says GET but detail says POST)
- URL paths are consistent — watch for prefix drift (`/api/v1/` vs `/api/v2/` vs `/v1/`)
- Path parameters use the same names across documents (`:id` vs `:userId` vs `{id}`)

## Request/Response Schemas

- Request body fields match between examples and schema definitions
- Response body fields match between examples and schema definitions
- Required vs optional fields are consistent between schema and description
- Field types (string, number, array, object) match between schema and examples
- Nested object structures match their type definitions

## Authentication and Authorization

- Auth requirements (Bearer token, API key, OAuth) are stated consistently
- Endpoints that require auth are consistently marked
- Role/permission requirements don't contradict each other across documents
- Error responses for auth failures (401, 403) are documented consistently

## Status Codes and Error Handling

- Documented status codes match what examples show
- Error response formats are consistent across endpoints
- Error codes/messages don't contradict between overview and detail
- Edge cases (empty results, not found, validation errors) are consistent

## Examples

- Example requests use correct content types and headers
- Example request bodies match the documented schema
- Example responses match the documented response schema
- Example curl/code snippets use the correct endpoint paths and methods
- Placeholder values in examples are clearly marked and consistent (e.g., `:id` vs `123`)

## Versioning and Deprecation

- API version references are consistent (v1 everywhere, not mixed v1/v2)
- Deprecated endpoints are marked consistently and have migration guidance
- Breaking changes are noted where version differs from prior documentation
