---
manifest_version: 1
slice: "011"
layer: backend
generated_at: 2026-08-25T17:32:05+00:00
source_plan: docs/opencode/plans/BE-011-plan.md
source_plan_sha256: 91a3f6f70e23aa02c6a0037099a49513d1a5d802457596628d9e22a0ef287d3c
source_task: docs/opencode/tasks/backend/BE-011.md
source_task_sha256: 131abd7df288c407aec4ec3462707925d1e69bf12df427940278c7d1b35d59f0
---

# BE-011 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-011.md`

## Archivos permitidos

- `backend/alembic/versions/a011_payments.py`
- `backend/app/api/schemas/payment_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/payments_router.py`
- `backend/app/data/payment_repo.py`
- `backend/app/domain/entities/payment.py`
- `backend/app/infrastructure/database/models/payment.py`
- `backend/app/services/payment_service.py`
- `backend/app/tests/**`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-011-backend.json`
- `docs/opencode/manifests/BE-011-backend.md`
- `docs/opencode/plans/BE-011-plan.md`

## Tareas

### BE-011-T01 - COMPLETADA
- Tipo: persistencia
- Criterio: BE-011: modelo y reglas de negocio
- Objetivo: Definir las entidades de dominio e ORM de Payment.
- Depende de: Ninguna
- Contexto: `backend/app/domain/entities/*`, `backend/app/infrastructure/database/models/*`
- Contratos: AC-011-01, AC-011-03, AC-011-07
- Entregables: `backend/app/domain/entities/payment.py`, `backend/app/infrastructure/database/models/payment.py`
- Aceptacion: Campos id, appointment_id, service_id, clinic_id, amount, method, amount_received, change_amount, status, paid_at, cancelled_at, created_at, updated_at. Constraint check FK a appointments, services, clinics. Enum method y status.
- Validacion: `pytest backend/app/tests -q` y `import` del modulo sin errores.
- Resultado: Entidad Payment modelada y tipada.

### BE-011-T02 - COMPLETADA
- Tipo: persistencia
- Criterio: BE-011: tabla payments
- Objetivo: Crear la tabla payments con sus indices en base de datos.
- Depende de: BE-011-T01
- Contexto: `backend/alembic/versions/a010_*`; modelos de T01
- Contratos: AC-011-01, AC-011-02
- Entregables: `backend/alembic/versions/a011_payments.py`
- Aceptacion: RevisionId `a011`, `down_revision` apunta a `a010` (o la actual head). Tabla payments con PK/FK e indices en appointment_id, service_id, clinic_id, status. Reversible.
- Validacion: `alembic upgrade head` y `alembic downgrade -1 && alembic upgrade head` sin errores.
- Resultado: Tabla creada y reversible.

### BE-011-T03 - COMPLETADA
- Tipo: persistencia
- Criterio: BE-011: consulta por tenant y periodo
- Objetivo: Implementar repositorio de pagos con filtros de tenant, periodo, estado.
- Depende de: BE-011-T02
- Contexto: `backend/app/infrastructure/repositories/` (patron repositorio del proyecto)
- Contratos: AC-011-01, AC-011-04
- Entregables: `backend/app/data/payment_repo.py` (ABC + SqlAlchemy impl.)
- Aceptacion: Metodos create, get_by_id (con clinic_id), list (appointment_id, from, to, status, page, page_size) -> items + total, cancel. Sin logic de negocio.
- Validacion: Test unitario de repo con session fake.
- Resultado: Acceso a datos tipado y testeado.

### BE-011-T04 - COMPLETADA
- Tipo: caso de uso
- Criterio: BE-011: registro, cancelacion, cambio
- Objetivo: Implementar use cases de registro, cancelacion, calculo de cambio.
- Depende de: BE-011-T03
- Contexto: `backend/app/services/` (patron use-case), reglas de negocio del plan
- Contratos: AC-011-02, AC-011-03, AC-011-05
- Entregables: `backend/app/services/payment_service.py`
- Aceptacion: Validar existencia de cita y servicio activos en tenant; calcular change_amount solo cuando method=CASH; estado PAID por defecto; 409 si cancela un pago ya CANCELLED.
- Validacion: `pytest backend/app/tests/test_payment_service.py -q`.
- Resultado: Reglas de negocio centralizadas en service.

### BE-011-T05 - COMPLETADA
- Tipo: api
- Criterio: BE-011: endpoints POST/GET/POST cancel
- Objetivo: Exponer endpoints de registro, listado, detalle, cancelacion de pagos.
- Depende de: BE-011-T04
- Contexto: `backend/app/api/v1/routers/*` (patron router + dependencias), schemas
- Contratos: AC-011-01..AC-011-06
- Entregables: `backend/app/api/v1/routers/payments_router.py`, `backend/app/api/schemas/payment_schemas.py`; registro en main router
- Aceptacion: POST 201, GET 200 con meta, GET /{id} 200, POST /{id}/cancel 200. Errores 401/403/404/409/422 consistentes. Sin logic de negocio en router.
- Validacion: `pytest backend/app/tests/api/test_payments_*.py -q`.
- Resultado: Contrato API completo y documentado (OpenAPI).

### BE-011-T06 - COMPLETADA
- Tipo: seguridad
- Criterio: BE-011: permisos por rol y tenant
- Objetivo: Aplicar guardas de rol, ownership por tenant en pagos.
- Depende de: BE-011-T05
- Contexto: `backend/app/api/v1/routers/prescription_router.py` (guard `_require_write_role`), riesgos del plan
- Contratos: AC-011-06, AC-011-07
- Entregables: `_require_write_role` en `payments_router.py` y uso de ownership por `clinic_id` en service
- Aceptacion: 403 a propietario al crear/cancelar; 404/403 clinico de otra clinica al leer/cancelar; 401 sin token.
- Validacion: `pytest backend/app/tests/api/test_payments_idor.py -q` y `test_payments_auth.py`.
- Resultado: Sin hallazgos IDOR/BOLA en pagos.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
