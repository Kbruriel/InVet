# InVet Command: implement-backend-task

Equivalent to OpenCode `/implement-backend-task`.

Input: `BE-00X`.

Use agent: `InVet Backend Implementer`.

Regenerate and verify `docs/opencode/manifests/BE-00X-backend.md`; use it as context and allowlist. Implement only backend slice tasks, including required backend unit tests and evidence. Execute applicable backend/persistence validators internally and return `/implement-frontend-task BE-00X` only after they pass. Do not delegate or expose an internal script as a user-facing phase.
