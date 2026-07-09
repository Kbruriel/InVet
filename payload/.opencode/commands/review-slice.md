---
description: Revisa el plan y la implementacion de un slice BE/FE/QA.
agent: invet-slice-reviewer
---

Revisa el slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante o hay una decision critica sobre alcance/evidencia.
1. Normaliza el argumento a formato `BE-00X`.
2. Identifica `FE-00X` y `QA-00X` equivalentes.
3. Lee:
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `git diff` y archivos modificados del slice
4. Valida plan, implementacion, pruebas, arquitectura, permisos y alcance.
5. Si existen correcciones, crea `docs/opencode/reviews/BE-00X-review.md` con base en `docs/opencode/templates/review_findings_template.md`.
6. Si no hay hallazgos, reporta estado Aprobado.
7. No implementes codigo en este comando.
