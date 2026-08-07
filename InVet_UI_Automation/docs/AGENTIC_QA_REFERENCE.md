# Agentic QA Reference

## Goal

This project gives InVet a dedicated automation workspace for UI and API evidence.

## Agent split

- `invet-ui-automation-implementer`: browser flows, visible validations, routes, redirects, role visibility, traces, screenshots, videos.
- `invet-api-automation-implementer`: HTTP methods, payloads, schemas, authn, authz, IDOR/BOLA, mass assignment, tenant isolation, sensitive data exposure.

## Traceability rule

```text
User story -> acceptance criterion -> implementation -> automated test -> evidence
```

## Core artifacts

- `docs/templates/US-00X.template.md`
- `docs/templates/UIA-00X.template.md`
- `docs/templates/APIA-00X.template.md`
- `docs/templates/TRACEABILITY_REPORT.template.md`

## Required evidence

- Playwright report
- JUnit report in CI
- Trace on failure
- Screenshot on failure
- Video on failure

