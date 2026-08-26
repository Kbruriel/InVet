---
manifest_version: 1
slice: "012"
layer: backend
generated_at: 2026-08-25T22:05:16+00:00
source_plan: docs/opencode/plans/BE-012-plan.md
source_plan_sha256: 21c5a19467d164db2591bc62b3be7a6829e0501a1f84b7742a3a3e6d8fac58da
source_task: docs/opencode/tasks/backend/BE-012.md
source_task_sha256: d1d8f4ec482a36d2a86001895824ccdb5f8a12397dc49c84986e61e39a629665
---

# BE-012 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-012.md`

## Archivos permitidos

- `backend/alembic/versions/a012_reviews.py`
- `backend/app/api/schemas/review_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/review_router.py`
- `backend/app/application/use_cases/review.py`
- `backend/app/data/review_repo.py`
- `backend/app/domain/entities/review.py`
- `backend/app/infrastructure/database/models/review.py`
- `backend/app/tests/**`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-012-backend.json`
- `docs/opencode/manifests/BE-012-backend.md`
- `docs/opencode/plans/BE-012-plan.md`

## Tareas

### BE-012-T01 - PENDIENTE
- Tipo: persistencia
- Criterio: AC-012-01, AC-012-14, AC-012-15
- Objetivo: Definir la entidad de dominio Review.
- Depende de: Ninguna
- Contexto: `backend/app/domain/entities/*`, `backend/app/infrastructure/database/models/*`, `backend/app/domain/entities/appointment.py`
- Contratos: AC-012-01, AC-012-03, AC-012-15
- Entregables: `backend/app/domain/entities/review.py`, `backend/app/infrastructure/database/models/review.py`
- Aceptacion: Campos id, appointment_id (unique), branch_id, clinic_id, user_id, rating 1..5, comment max 2048, created_at, updated_at. ReviewResponse con id, review_id (unique), branch_id, user_id, body max 2048, timestamps.
- Validacion: `python -c "from app.domain.entities import review"` y `pytest backend/app/tests -q` sin errores de import.
- Resultado: Entidades Review y ReviewResponse modeladas y tipadas.

### BE-012-T02 - PENDIENTE
- Tipo: persistencia
- Criterio: AC-012-14
- Objetivo: Crear la tabla reviews con su constraint unico.
- Depende de: BE-012-T01
- Contexto: `backend/alembic/versions/a011_payments.py`; modelos de T01
- Contratos: AC-012-03, AC-012-05, AC-012-14
- Entregables: `backend/alembic/versions/a012_reviews.py`
- Aceptacion: RevisionId `a012`, `down_revision` apunta a la head actual. Tablas reviews (unique appointment_id, FK appointments, branches, clinics, internal_users) y review_responses (unique review_id, FK reviews, branches, internal_users). Reversible.
- Validacion: `alembic upgrade head`, `alembic downgrade -1 && alembic upgrade head` sin errores.
- Resultado: Tablas creadas con constraints y reversible.

### BE-012-T03 - PENDIENTE
- Tipo: persistencia
- Criterio: AC-012-04, AC-012-07
- Objetivo: Implementar el repositorio de reseñas por sucursal.
- Depende de: BE-012-T02
- Contexto: `backend/app/data/payment_repo.py` (patrón repositorio del proyecto)
- Contratos: AC-012-04, AC-012-07
- Entregables: `backend/app/data/review_repo.py` (ABC + impl. SQLAlchemy)
- Aceptacion: Metodos create, get_by_id (con ownership), exists_by_appointment, list_public_by_branch (page, page_size, total), list_by_clinic, create_response, get_response_by_review. Sin logic de negocio.
- Validacion: `pytest backend/app/tests/data/test_review_repo.py -q`.
- Resultado: Acceso a datos tipado y testeado.

### BE-012-T04 - PENDIENTE
- Tipo: caso de uso
- Criterio: AC-012-02, AC-012-05, AC-012-09
- Objetivo: Implementar el use case de crear reseña.
- Depende de: BE-012-T03
- Contexto: `backend/app/application/use_cases/branch_profile.py` (patrón), `backend/app/infrastructure/database/models/rating_summary.py`, reglas de negocio del plan
- Contratos: AC-012-01..AC-012-06, AC-012-09
- Entregables: `backend/app/application/use_cases/review.py`
- Aceptacion: Create valida cita `COMPLETED` del owner (si no, 422), cita ajena al tenant (404), reseña previa (409), rating 1..5 y comment <=2048, y recalcula RatingSummary en la misma transaccion (AC-012-09). Respond valida rol clinico de la misma sucursal (403/404) y respuesta previa (409).
- Validacion: `pytest backend/app/tests/application/test_review_service.py -q`.
- Resultado: Reglas de negocio centralizadas en use cases.

### BE-012-T05 - PENDIENTE
- Tipo: api
- Criterio: AC-012-01, AC-012-07, AC-012-08
- Objetivo: Exponer endpoints de crear, lectura, publico, respuesta de reseñas.
- Depende de: BE-012-T04
- Contexto: `backend/app/api/v1/routers/payments_router.py` (patrón), `backend/app/api/schemas/payment_schemas.py`
- Contratos: AC-012-01, AC-012-05, AC-012-07
- Entregables: `backend/app/api/v1/routers/review_router.py`, `backend/app/api/schemas/review_schemas.py`; registro en main router
- Aceptacion: POST /reviews 201; GET /reviews/{id} 200; GET /reviews/public/{branchId} 200 con meta; GET /reviews?branch_id= 200 con meta; POST /reviews/{id}/respond 200; errores 401/403/404/409/422 consistentes. Sin logic de negocio en router.
- Validacion: `pytest backend/app/tests/api/test_reviews_*.py -q`.
- Resultado: Contrato API completo y documentado (OpenAPI).

### BE-012-T06 - PENDIENTE
- Tipo: seguridad
- Criterio: AC-012-04, AC-012-06, AC-012-12, AC-012-13
- Objetivo: Aplicar la guardia de rol para responder reseñas.
- Depende de: BE-012-T05
- Contexto: `backend/app/api/v1/routers/payments_router.py` (guard `_require_write_role`), `backend/core/security.py`
- Contratos: AC-012-06, AC-012-12, AC-012-13
- Entregables: Guardas `_require_respond_role` y `_require_owner_role` en `review_router.py` + ownership por `clinic_id` en use cases
- Aceptacion: 403 propietario al responder; 404 staff de otra sucursal al responder/leer; 401 sin token en endpoints no publicos; 404 cita ajena al tenant al crear.
- Validacion: `pytest backend/app/tests/api/test_reviews_idor.py -q` y `test_reviews_auth.py`.
- Resultado: Sin hallazgos IDOR/BOLA en reseñas.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
