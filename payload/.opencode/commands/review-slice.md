---
description: Revisa el plan y la implementacion de un slice BE/FE/QA.
agent: invet-slice-reviewer
subtask: false
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
   - Si existe una tarea aplicable en `- [ ]`, deten el review y devuelve el plan al agente responsable; solo `Estado: CANCELLED` con evidencia verificable queda exento.
   - Si el gate falla porque `QA-00X` no esta `APPROVED` o sus findings siguen bloqueantes, no crees `BE-00X-review.md` y recomienda el comando que destraba QA: `/qa-task QA-00X` cuando haya findings en `READY_FOR_REVALIDATION`, o `/implement-findings BE-00X` cuando sigan `OPEN`/`IN_PROGRESS`.
3.1. Ejecuta `manifest BE-00X --layer all` y `verify BE-00X --layer all`; usa los manifiestos para delimitar alcance, pero conserva QA, diff y evidencia real como fuentes de decision.
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
Cierre requerido:
- El reporte final debe incluir `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` antes de `Siguiente paso recomendado`.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Si el review se ejecuto y queda `APPROVED`, recomienda `/clean-architecture-review BE-00X`; no recomiendes volver a `/qa-task`.
- Si el review se ejecuto y queda `REJECTED`, recomienda `/implement-findings BE-00X`.
- Solo recomienda `/qa-task QA-00X` cuando el preflight de review no haya permitido revisar porque QA aun no esta aprobado o necesita revalidacion.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
