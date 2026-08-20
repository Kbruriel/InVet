# InVet Command: run-checks

Equivalent to OpenCode `/run-checks`.

Input: optional diagnostic mode, or `BE-00X`, `FE-00X`, or `QA-00X` for formal slice checks.

Use agent: `InVet Check Runner`.

Verify the affected compact manifests, then use the checks matrix and relevant evidence. Execute checks and logs directly; do not delegate.

Run applicable backend, frontend, and DevOps checks. Write formal check evidence when a slice ID is provided.

The formal `checks` preflight must block applicable open tasks and `CANCELLED` tasks without verifiable evidence.
