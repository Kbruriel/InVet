---
description: Implementa una tarea backend InVet, por ejemplo BE-001.
agent: invet-backend-implementer
---

Implementa la tarea backend indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de alcance/seguridad o se requiere una accion destructiva/migracion irreversible.
1. Normaliza el argumento a `BE-00X`.
2. Identifica el plan generado por `/plan-task`: `docs/opencode/plans/BE-00X-plan.md`.
3. Ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage backend` antes de editar codigo.
   - Si falla, deten la implementacion y reporta cada gap.
   - Si el plan es legacy o incompleto, indica `/plan-task BE-00X`.
4. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/02_be_fe_qa_task_matrix.md`
5. Selecciona solo tareas pendientes con `Capa: backend`.
6. Verifica los IDs de `Depende de`; cada dependencia debe estar `- [x]` y tener evidencia.
7. Implementa usando `Objetivo`, `Entregables` y `Criterios de aceptacion` como contrato.
8. Manten Clean Architecture:
   - router/adapters en `app/api`.
   - use cases en `app/application`.
   - entidades/reglas/ports en `app/domain`.
   - ORM/repositorios/proveedores en `app/infrastructure`.
   - config/security/errors en `app/core`.
9. Agrega o actualiza migraciones Alembic si aplica.
10. Agrega pruebas unitarias Pytest para todo archivo productivo nuevo o modificado y pruebas HTTPX cuando el criterio sea de API.
11. No delegues a QA las pruebas unitarias backend.
12. No expongas modelos ORM.
13. Valida permisos y pertenencia de tenant/propietario/clinica/sucursal.
14. Para tareas de ORM, repositorios, migraciones, base de datos, permisos, ownership, IDOR/BOLA o auditoria, ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence` antes de entregar backend.
15. Marca `- [x]` solo tras ejecutar `Validacion`; reemplaza `Evidencia: pending` con archivos, comandos y resultado.
16. Si una tarea no se completa, conserva `- [ ]`, `Evidencia: pending` y documenta el bloqueo.
17. Resume tareas completadas, archivos modificados, endpoints y pruebas ejecutadas.

Hook de cierre:
- Si Docker Compose esta disponible y el usuario no pidió omitirlo, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
- Si Docker Compose no esta disponible, registrar el skip con la causa exacta.
