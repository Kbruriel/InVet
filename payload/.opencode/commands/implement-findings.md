---
description: Implementa hallazgos de revision y documenta el cierre de correcciones.
agent: invet-findings-implementer
---

Implementa los hallazgos indicados por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si el hallazgo es ambiguo, falta informacion bloqueante, cambia el alcance o se requiere una accion destructiva o migracion irreversible.
1. Acepta un indice `BE-00X`, `FE-00X` o la ruta de un archivo de hallazgos.
2. Si recibe `FE-00X`, deriva el `BE-00X` equivalente y corrige el mismo slice vertical sin remapear silenciosamente a otro indice.
3. Deriva el slice y ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage findings`; si el plan es invalido, corrige primero el contrato con `/plan-task BE-00X`.
4. Lee los findings QA y de review, arquitectura y seguridad del slice.
5. Corrige codigo, configuracion y pruebas unitarias necesarias en la capa responsable.
6. Documenta el cierre en `docs/opencode/reviews/BE-00X-corrections.md`.
7. Reejecuta checks relevantes.
8. Si corriges un finding QA, cambia su estado a `READY_FOR_REVALIDATION`, nunca a `RESOLVED`.
9. Indica `/qa-task QA-00X` como siguiente gate; solo QA puede cerrar el finding.
10. No amplie el alcance fuera del slice ni inventes funcionalidad nueva.

Hook de cierre:
- Si las correcciones quedaron listas y el usuario no pidió omitirlo, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
- Si Docker Compose no esta disponible, registrar el skip con la causa exacta.
