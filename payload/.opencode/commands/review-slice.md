---
description: Revisa el plan y la implementacion de un slice BE/FE/QA.
agent: invet-slice-reviewer
---

Revisa el slice indicado por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante o hay una decision critica sobre alcance/evidencia.
1. Acepta argumentos `BE-00X` o `FE-00X`.
   - Si recibe `BE-00X`, usa ese indice como slice base y deriva `FE-00X` y `QA-00X`.
   - Si recibe `FE-00X`, usa ese indice frontend como entrada valida, deriva el `BE-00X` equivalente y revisa el mismo slice vertical completo.
   - Si recibe `QA-00X`, no lo remapees silenciosamente a review de slice; explica que para ejecutar validacion corresponde `/qa-task QA-00X`.
2. Identifica `BE-00X`, `FE-00X` y `QA-00X` equivalentes.
3. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage review`.
   - Si QA no esta aprobado o el plan es invalido, deten el review y reporta el gate.
4. Lee:
   - `docs/opencode/plans/BE-00X-plan.md` cuando exista.
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `git diff` y archivos modificados del slice
5. Valida plan, implementacion, pruebas, arquitectura, permisos y alcance.
6. Crea siempre `docs/opencode/reviews/BE-00X-review.md` con decision `APPROVED` o `REJECTED`.
7. Si hay correcciones, usa `docs/opencode/templates/review_findings_template.md`.
8. No implementes codigo en este comando.
