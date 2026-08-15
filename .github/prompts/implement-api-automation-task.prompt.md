# InVet Command: implement-api-automation-task

Equivalent to OpenCode `/implement-api-automation-task`.

Input: `BE-00X`.

Use agent: `InVet API Automation Implementer`.

Before acting, read:

- `.opencode/commands/implement-api-automation-task.md`
- `.opencode/agents/invet-api-automation-implementer.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Preflight:
- Validate the slice plan through `backend/scripts/validate_slice_plan.py --stage qa` before closing the task.
- Recover missing dependencies first, and use Docker when the slice depends on PostgreSQL or the repo runtime.
- Treat stale evidence as invalid and confirm Docker containers were updated or recreated when Docker applies.

Implement only API/HTTP automation under `InVet_UI_Automation/`.
