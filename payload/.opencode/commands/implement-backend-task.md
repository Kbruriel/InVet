---
description: Implementa una tarea backend InVet, por ejemplo BE-001.
agent: invet-backend-implementer
---

Implementa la tarea backend indicada por `$ARGUMENTS`.

Instrucciones:
1. Normaliza el argumento a `BE-00X`.
2. Identifica el plan generado por `/plan-task`: `docs/opencode/plans/BE-00X-plan.md`.
3. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
4. Selecciona solo tareas pendientes `- [ ]` del plan que correspondan a backend, API, dominio, persistencia, migraciones, seguridad backend o pruebas backend.
5. Respeta `Paralelismo[P]`: si una tarea marca `No`, verifica que sus dependencias previas esten completas antes de implementarla.
6. Implementa cada tarea usando su `Objetivo` y `Criterios de aceptacion` como contrato de alcance.
7. Manten Clean Architecture:
   - router/adapters en `app/api`.
   - use cases en `app/application`.
   - entidades/reglas/ports en `app/domain`.
   - ORM/repositorios/proveedores en `app/infrastructure`.
   - config/security/errors en `app/core`.
8. Agrega o actualiza migraciones Alembic si aplica.
9. Agrega pruebas Pytest/HTTPX que validen los criterios de aceptacion aplicables.
10. No expongas modelos ORM.
11. Valida permisos y pertenencia de tenant/propietario/clinica/sucursal.
12. Marca como completadas en `docs/opencode/plans/BE-00X-plan.md` solo las tareas backend cuyos criterios de aceptacion quedaron verificados, cambiando `- [ ]` por `- [x]`.
13. Si una tarea no se puede completar, dejala como `- [ ]` y documenta el bloqueo debajo de la tarea o en el resumen final.
14. Resume tareas completadas, archivos modificados, endpoints y pruebas ejecutadas.
