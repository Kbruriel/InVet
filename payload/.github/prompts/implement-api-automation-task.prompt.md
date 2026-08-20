# InVet Command: implement-api-automation-task

Equivalent to OpenCode `/implement-api-automation-task`.

Input: `BE-00X`.

Use agent: `InVet API Automation Implementer`.

Regenerate and verify `docs/opencode/manifests/BE-00X-api-automation.md`; use it as context and allowlist. Do not delegate.

Run API automation only against the backend published by the Docker Compose stack. On PASS recommend `qa-task.prompt.md` with `QA-00X`; Docker unavailable is `BLOCKED`.

Preflight:
- Validate the slice plan through `backend/scripts/validate_slice_plan.py --stage qa` before closing the task.
- Recover missing dependencies first, and use Docker when the slice depends on PostgreSQL or the repo runtime.
- Treat stale evidence as invalid and confirm Docker containers were updated or recreated when Docker applies.

Implement only API/HTTP automation under `InVet_UI_Automation/`.
