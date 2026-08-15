# InVet: QA, Review, And Close Gates

Use this prompt when validating or closing a slice after implementation.

## Input

Gate: `qa`, `functional-review`, `clean-architecture-review`, `security-review`, `ui-checks`, `checks`, `docs`, or `final-gate`.

Slice ID: `BE-00X`, `FE-00X`, or `QA-00X`.

## Task

Run the selected gate and write the expected evidence artifact.

## Gate Outputs

- QA: `docs/opencode/qa/QA-00X-results.md` and, when needed, `docs/opencode/qa/QA-00X-findings.md`.
- For QA gate sequencing and handoff rules, use `docs/opencode/qa/README.md`.
- Functional review: `docs/opencode/reviews/BE-00X-review.md`.
- Clean architecture review: `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
- Security review: `docs/opencode/reviews/BE-00X-security-review.md`.
- UI checks: UI automation evidence in `docs/opencode/tasks/ui-automation/UIA-00X.md` or check report.
- Formal checks: `docs/opencode/checks/BE-00X-checks.md`.
- Docs: updated `docs/opencode` artifacts.
- Final gate: `docs/opencode/reviews/BE-00X-final-review.md`.

## Rules

- Use `APPROVED` only with reproducible evidence.
- Use `REJECTED` for product defects, regressions, missing unit tests, security defects, or applicable checks that fail.
- Use `BLOCKED` only when the environment or missing evidence prevents a reliable decision.
- Do not fix product code in QA or review gates.
- If findings are found, document them and recommend the findings workflow.
- For QA, write `- Estado global: ...` in `QA-00X-findings.md` when findings exist.
- For QA, recommend functional review only after `Decision: APPROVED` and no blocking findings; use findings resolution for `OPEN`/`IN_PROGRESS`, and treat `READY_FOR_REVALIDATION` as a findings state that must flow through the resolver before QA revalidation.
- For functional review, recommend clean architecture review after `APPROVED`; do not send the flow back to QA unless preflight prevented the review because QA is not approved.
- End with `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` before `Siguiente paso recomendado`.

## Output

Report:

- Gate executed.
- Decision.
- Evidence artifacts.
- Findings.
- Commands run.

End with the next gate from `docs/opencode/14_github_copilot_agentic_flow.md`, applying the QA/review continuity rules above.
