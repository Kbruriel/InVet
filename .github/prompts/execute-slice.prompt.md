# InVet Command: execute-slice

Equivalent to OpenCode `/execute-slice`.

Input: `BE-00X`, `FE-00X`, or `QA-00X`.

Use agent: `InVet Orchestrator`.

Use only the currently selected model. Follow `.github/copilot-instructions.md`, compact manifests, and checkpoints. Do not invoke subagents. Stop at the first failed gate and report the exact resume step. The final gate is mandatory.
