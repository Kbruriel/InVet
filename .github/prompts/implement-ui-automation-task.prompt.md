# InVet Command: implement-ui-automation-task

Equivalent to OpenCode `/implement-ui-automation-task`.

Input: `BE-00X`, `FE-00X`, or `QA-00X`; normalize to `UIA-00X`.

Use agent: `InVet UI Automation Implementer`.

Regenerate and verify `docs/opencode/manifests/BE-00X-ui-automation.md`; use it as context and allowlist. Do not delegate.

Run E2E and regression only against the Docker Compose `db`, `backend`, and `frontend` stack with `PLAYWRIGHT_START_FRONTEND=false`. On PASS recommend `implement-api-automation-task.prompt.md`; Docker unavailable is `BLOCKED`.

Preflight:
- Validate the slice plan through `backend/scripts/validate_slice_plan.py --stage qa` before closing the task.
- Recover missing dependencies first, and use Docker when the slice depends on PostgreSQL or the repo runtime.
- Treat stale evidence as invalid and confirm Docker containers were updated or recreated when Docker applies.

Implement only UI/E2E automation under `InVet_UI_Automation/`.
