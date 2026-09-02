# InVet Command: clean-architecture-review

Equivalent to OpenCode `/clean-architecture-review`.

Input: `BE-00X` or `FE-00X`.

Use agent: `InVet Clean Architecture Reviewer`.

Verify all five compact manifests, then use the architecture reference, relevant diff, QA evidence, and review template. Do not delegate or modify product code.

PowerShell 5.1 rule: configure `C:\InVet` as the working directory on every
command and execute commands separately. Never chain with `&&`; use
`if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }` for fail-fast behavior.
The preflight must include plan/backend validation, manifest verification,
Alembic migration tests, directed slice tests, and `git diff --check`.
Normalize `FE-00X` to its equivalent `BE-00X` plan and AC matrix before the
final diff review.

Docker portability: the backend container workdir is `/app`, so use paths such
as `tests/api/...` inside `docker compose run`, not `backend/tests/...`. Rebuild
the backend image after changing tests or copied source (`docker compose build
backend`) before collecting evidence. Never assume `/backend` in tests; derive
paths from `Path(__file__)` so host and container runs agree.

Review architecture boundaries and write the required report.
