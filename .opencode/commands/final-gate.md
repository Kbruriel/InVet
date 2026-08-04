---
description: Ejecuta el gate final de release con un reviewer de alta capacidad.
agent: invet-final-reviewer
---

Ejecuta el gate final del slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Requiere `BE-00X`, `FE-00X` o `QA-00X` y normaliza el mismo indice vertical.
1. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage docs`.
   - Si falla, reporta `BLOCKED` y no declares cierre final.
2. Revisa:
   - `docs/opencode/qa/QA-00X-results.md`
   - `docs/opencode/qa/QA-00X-findings.md`
   - `docs/opencode/reviews/BE-00X-review.md`
   - `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
   - `docs/opencode/reviews/BE-00X-security-review.md`
   - `docs/opencode/checks/BE-00X-checks.md`
   - `docs/opencode` actualizado para el slice
   - `git diff` y logs relevantes
3. Si faltan comandos, logs o evidencias mecanicas, delega reintentos a `invet-command-executor`.
4. Crea siempre `docs/opencode/reviews/BE-00X-final-review.md` usando `docs/opencode/templates/review_findings_template.md` como base.
5. Usa `APPROVED` solo si `QA-00X-results.md` esta `APPROVED`, `QA-00X-findings.md` no existe o esta en estado resuelto, las tres revisiones, checks y docs estan cerrados y no hay findings abiertos.
6. Usa `REJECTED` o `BLOCKED` si hay gaps, inconsistencias o verificaciones imposibles.
7. No modifiques codigo de producto.
