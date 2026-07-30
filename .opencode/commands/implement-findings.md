---
description: Implementa hallazgos de revision y documenta el cierre de correcciones.
agent: invet-findings-implementer
---

Implementa los hallazgos indicados por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si el hallazgo es ambiguo, falta informacion bloqueante, cambia el alcance o se requiere una accion destructiva o migracion irreversible.
1. Acepta un indice `BE-00X`, `FE-00X` o la ruta de un archivo de hallazgos.
2. Si recibe `FE-00X`, deriva el `BE-00X` equivalente y corrige el mismo slice vertical sin remapear silenciosamente a otro indice.
3. Si el origen es QA, lee `docs/opencode/qa/QA-00X-findings.md`; si el origen es review, lee `docs/opencode/reviews/BE-00X-review.md`; si el origen es un gate global, lee tambien `docs/opencode/reviews/BE-00X-clean-architecture-review.md` y `docs/opencode/reviews/BE-00X-security-review.md`; si aplica, revisa tambien las tareas relacionadas.
4. Corrige la implementacion necesaria en backend, frontend o QA.
5. Documenta el cierre en `docs/opencode/reviews/BE-00X-corrections.md` siguiendo `docs/opencode/templates/corrections_checklist_template.md`.
6. Incluye un checklist de correcciones completadas.
7. Reejecuta checks relevantes si estan disponibles.
8. No amplie el alcance fuera del slice ni inventes funcionalidad nueva.
