---
description: Implementa una tarea backend InVet, por ejemplo BE-001.
agent: invet-backend-implementer
---

Implementa la tarea backend indicada por `$ARGUMENTS`.

Instrucciones:
1. Normaliza el argumento a `BE-00X`.
2. Lee `docs/opencode/tasks/backend/BE-00X.md`.
3. Revisa la matriz `docs/opencode/02_be_fe_qa_task_matrix.md`.
4. Implementa solo el alcance del slice.
5. Mantén Clean Architecture:
   - router/adapters en `app/api`.
   - use cases en `app/application`.
   - entidades/reglas/ports en `app/domain`.
   - ORM/repositorios/proveedores en `app/infrastructure`.
   - config/security/errors en `app/core`.
6. Agrega o actualiza migraciones Alembic si aplica.
7. Agrega pruebas Pytest/HTTPX.
8. No expongas modelos ORM.
9. Valida permisos y pertenencia de tenant/propietario/clínica/sucursal.
10. Resume archivos modificados, endpoints y pruebas ejecutadas.
