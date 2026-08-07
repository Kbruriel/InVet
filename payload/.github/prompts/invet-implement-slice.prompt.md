# InVet: Implement Slice Layer

Use this prompt when implementing one layer of a slice with GitHub Copilot.

## Input

Layer: `backend`, `frontend`, `ui-automation`, or `api-automation`.

Slice ID: `BE-00X` or `FE-00X`.

## Task

Implement only the selected layer for the current slice.

## Required Context

Read:

- `docs/opencode/plans/BE-00X-plan.md`
- The layer task file:
  - backend: `docs/opencode/tasks/backend/BE-00X.md`
  - frontend: `docs/opencode/tasks/frontend/FE-00X.md`
  - ui-automation: `docs/opencode/tasks/ui-automation/UIA-00X.md`
  - api-automation: `docs/opencode/tasks/api-automation/APIA-00X.md`
- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/references/slice_task_context.md`

## Rules

- Implement only tasks for the selected layer.
- Reject compound tasks and recommend plan repair.
- Mark tasks `- [x]` only after running their validation.
- Replace `Evidencia: pending` with concrete files, commands, and results.
- Backend code lives in `backend/`.
- Frontend product UI lives in `frontend/` or the active frontend app.
- UI automation and API automation live in `InVet_UI_Automation/`.
- Product unit tests belong to backend or frontend implementers, not QA.

## Output

Report:

- Layer implemented.
- Tasks completed.
- Files changed.
- Tests or validations run.
- Remaining blockers.

End with the next gate:

- backend: `Siguiente paso recomendado: Run secure persistence validation for BE-00X`
- frontend: `Siguiente paso recomendado: Implement UI automation for FE-00X`
- ui-automation: `Siguiente paso recomendado: Implement API automation for BE-00X`
- api-automation: `Siguiente paso recomendado: Run QA for QA-00X`
