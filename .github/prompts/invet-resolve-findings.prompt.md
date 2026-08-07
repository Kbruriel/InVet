# InVet: Resolve Findings

Use this prompt when QA, reviews, UI checks, or formal checks found blocking issues.

## Input

Slice ID: `BE-00X` or `FE-00X`, or a path to a findings file.

## Task

Fix the findings in the owning layer and prepare them for revalidation.

## Required Context

Read all existing findings for the slice:

- `docs/opencode/qa/QA-00X-findings.md`
- `docs/opencode/reviews/BE-00X-review.md`
- `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
- `docs/opencode/reviews/BE-00X-security-review.md`
- `docs/opencode/checks/BE-00X-checks.md`

Also read:

- `docs/opencode/plans/BE-00X-plan.md`
- Relevant BE, FE, QA, UIA, and APIA task files.

## Rules

- Fix code, tests, configuration, or docs only inside the current slice scope.
- Change QA findings to `READY_FOR_REVALIDATION`, never `RESOLVED`.
- Only QA or the owning review gate can confirm resolution.
- Write correction evidence to `docs/opencode/reviews/BE-00X-corrections.md`.
- Rerun relevant tests before closing.
- Close with `Estado de ejecucion: READY_FOR_REVALIDATION|BLOCKED|COMPLETED` before `Siguiente paso recomendado`.

## Output

Report:

- Findings addressed.
- Files changed.
- Tests run.
- Findings moved to `READY_FOR_REVALIDATION`.
- Any remaining blockers.

End with:

```text
Siguiente paso recomendado: Run QA for QA-00X
Motivo: QA debe revalidar los findings antes de continuar con reviews, UI checks o checks.
```
