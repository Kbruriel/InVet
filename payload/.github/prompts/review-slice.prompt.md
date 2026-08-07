# InVet Command: review-slice

Equivalent to OpenCode `/review-slice`.

Input: `BE-00X` or `FE-00X`.

Use agent: `InVet Slice Reviewer`.

Before acting, read:

- `.opencode/commands/review-slice.md`
- `.opencode/agents/invet-slice-reviewer.md`
- `docs/opencode/templates/review_findings_template.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Review the vertical slice and write the required functional review report.

Continuity rules:

- Run `python backend/scripts/validate_slice_plan.py BE-00X --stage review` before reviewing.
- If the preflight fails because QA is not approved or needs revalidation, do not create `BE-00X-review.md`; recommend `qa-task.prompt.md` with `QA-00X` when revalidation is needed, or `implement-findings.prompt.md` with `BE-00X` when findings are still `OPEN`/`IN_PROGRESS`.
- If the functional review runs and is `APPROVED`, recommend `clean-architecture-review.prompt.md` with `BE-00X`; do not recommend QA again.
- If the functional review runs and is `REJECTED`, recommend `implement-findings.prompt.md` with `BE-00X`.
- End with `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` before `Siguiente paso recomendado`.
