# InVet: Plan Slice

Use this prompt when starting or repairing a slice plan in GitHub Copilot.

## Input

Slice ID: `BE-00X`, `FE-00X`, or `QA-00X`.

## Task

Plan the slice once, using a single canonical plan at `docs/opencode/plans/BE-00X-plan.md`.

## Required Steps

1. Normalize the ID to the same vertical slice: `BE-00X`, `FE-00X`, `QA-00X`, `US-00X`, `UIA-00X`, and `APIA-00X`.
2. Run `python backend/scripts/validate_slice_plan.py BE-00X --stage previous` before creating a new plan.
3. Read the matrix, task files, user story, automation artifacts, slice context, missing artifact guidance, and plan template.
4. Create or update `docs/opencode/plans/BE-00X-plan.md` with schema v3.
5. Create or update `docs/opencode/tasks/user-stories/US-00X.md`.
6. Create or update `docs/opencode/tasks/ui-automation/UIA-00X.md`.
7. Create or update `docs/opencode/tasks/api-automation/APIA-00X.md`.
8. Validate with `python backend/scripts/validate_slice_plan.py BE-00X --stage plan`.

## Output

Summarize:

- Normalized slice IDs.
- Artifacts created or updated.
- Validation command and result.
- Any assumptions or blockers.

End with:

```text
Siguiente paso recomendado: Implement backend for BE-00X
Motivo: El plan canonico quedo valido y el siguiente gate es backend.
```

If blocked, end with:

```text
Comando recomendado para desbloquear el gate: Plan Slice for BE-00X
Motivo: <missing or invalid artifact>
```
