# InVet Command: review-slice

Equivalent to OpenCode `/review-slice`.

Input: `BE-00X` or `FE-00X`.

Use agent: `InVet Slice Reviewer`.

Verify all five compact manifests, then use relevant QA evidence, diff, and review template. Do not delegate or modify product code.

Review the vertical slice and write the required functional review report.

Continuity rules:

- Run `python backend/scripts/validate_slice_plan.py BE-00X --stage review` before reviewing.
- Stop when any applicable plan task remains open; only an unchecked task with `Estado: CANCELLED` and verifiable evidence is exempt.
- If the preflight fails because QA is not approved or needs revalidation, do not create `BE-00X-review.md`; recommend `qa-task.prompt.md` with `QA-00X` when revalidation is needed, or `implement-findings.prompt.md` with `BE-00X` when findings are still `OPEN`/`IN_PROGRESS`.
- If the functional review runs and is `APPROVED`, recommend `clean-architecture-review.prompt.md` with `BE-00X`; do not recommend QA again.
- If the functional review runs and is `REJECTED`, recommend `implement-findings.prompt.md` with `BE-00X`.
- End with `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` before `Siguiente paso recomendado`.
