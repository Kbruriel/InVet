# InVet Command: qa-task

Equivalent to OpenCode `/qa-task`.

Input: `QA-00X`.

Use agent: `InVet QA Validator`.

Verify all five compact manifests and use them as the slice index. Read only the QA templates, current evidence, and files needed for each criterion. Do not delegate.

Run QA and write reproducible evidence. Do not modify product code to make QA pass.

Continuity rules:

- If QA writes `docs/opencode/qa/QA-00X-findings.md`, include `- Estado global: OPEN|IN_PROGRESS|READY_FOR_REVALIDATION|RESOLVED|ACCEPTED_RISK`.
- Recommend `review-slice.prompt.md` with `BE-00X` only when `QA-00X-results.md` ends in `Decision: APPROVED` and findings are absent or globally `RESOLVED`/`ACCEPTED_RISK`.
- If QA is `REJECTED` or findings are `OPEN`/`IN_PROGRESS`, recommend `implement-findings.prompt.md` with `BE-00X`.
- If findings are `READY_FOR_REVALIDATION`, treat that as a findings state and recommend `implement-findings.prompt.md` with `BE-00X`; the revalidation rerun comes from the findings workflow, not from QA closing itself.

End with `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` before `Siguiente paso recomendado`.
