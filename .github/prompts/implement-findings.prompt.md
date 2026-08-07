# InVet Command: implement-findings

Equivalent to OpenCode `/implement-findings`.

Input: `BE-00X`, `FE-00X`, or a findings file path.

Use agent: `InVet Findings Implementer`.

Before acting, read:

- `.opencode/commands/implement-findings.md`
- `.opencode/agents/invet-findings-implementer.md`
- `docs/opencode/templates/corrections_checklist_template.md`
- `docs/opencode/14_github_copilot_agentic_flow.md`

Fix findings in the owning layer and prepare QA revalidation. Do not mark QA findings as `RESOLVED`.
