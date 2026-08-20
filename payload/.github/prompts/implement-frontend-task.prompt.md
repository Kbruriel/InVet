# InVet Command: implement-frontend-task

Equivalent to OpenCode `/implement-frontend-task`.

Input: `BE-00X`, `FE-00X`, or `QA-00X`; normalize to `FE-00X`.

Use agent: `InVet Frontend Implementer`.

Regenerate and verify `docs/opencode/manifests/BE-00X-frontend.md`; use it as context and allowlist. Implement only frontend product UI and frontend tests with the selected model. UI automation belongs to its gate.
