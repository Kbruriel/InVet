# InVet Command: implement-findings

Equivalent to OpenCode `/implement-findings`.

Input: `BE-00X`, `FE-00X`, or a findings file path.

Use agent: `InVet Findings Implementer`.

Verify all five compact manifests, then read blocking findings and the manifest for the owning layer. Do not delegate.

Fix findings in the owning layer and prepare QA revalidation. Do not mark QA findings as `RESOLVED`.
