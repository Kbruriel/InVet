# InVet Command: run-ui-checks

Equivalent to OpenCode `/run-ui-checks`.

Input: `BE-00X`, `FE-00X`, or `QA-00X`; normalize to `UIA-00X`.

Use agent: `InVet Check Runner`.

Verify the affected compact manifests, then run UI automation and regression checks directly. Do not delegate or allow formal checks to proceed if UI checks fail.

Use only the Docker Compose `db`, `backend`, and `frontend` stack and set `PLAYWRIGHT_START_FRONTEND=false`. On PASS recommend `run-checks.prompt.md`; Docker unavailable is `BLOCKED`.
