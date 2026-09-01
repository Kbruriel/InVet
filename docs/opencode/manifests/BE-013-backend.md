---
manifest_version: 1
slice: "013"
layer: backend
generated_at: 2026-08-31T23:55:16+00:00
source_plan: docs/opencode/plans/BE-013-plan.md
source_plan_sha256: 642c5f6278818acb924edc251bd441cb236522a3b33398f4d0b9908df3289a42
source_task: docs/opencode/tasks/backend/BE-013.md
source_task_sha256: 628545a80b376020daaee30a9f179119178aad146342bfcd8aaa6cb25ee0a223
---

# BE-013 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-013.md`

## Archivos permitidos

- `(async, try/except, no bloquea caller). Integracion en 5 lugares de 4 routers: appointment_router.py:280 (appointment_created), appointment_router.py:451 (appointment_confirmed/cancelled/completed/no_show/approved), payments_router.py:190 (payment_completed/cancelled), consultation_router.py:245 (consultation_completed), prescription_router.py:246 (prescription_created). Enum canonico`
- `alineado con los 10 event types emitidos (5 genericos del plan cubren los granulares: APPOINTMENT_STATUS_CHANGED -> 5 eventos, PAYMENT_RECEIVED -> completed/cancelled). Guard`
- `app/api/schemas/notification_schemas.py`
- `app/application/notification_use_cases.py`
- `backend/alembic/versions/a013_notifications.py`
- `backend/app/api/schemas/notification_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/_notify.py`
- `backend/app/api/v1/routers/notification_router.py`
- `backend/app/application/notification_use_cases.py`
- `backend/app/data/notification_repo.py`
- `backend/app/domain/entities/notification.py`
- `backend/app/tests/**`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-013-backend.json`
- `docs/opencode/manifests/BE-013-backend.md`
- `docs/opencode/plans/BE-013-plan.md`

## Tareas

### BE-013-T01 - COMPLETADA
- Tipo: contrato
- Criterio: AC-013-01, AC-013-10
- Objetivo: Definir la entidad de dominio Notification con su enum.
- Depende de: Ninguna
- Contexto: `backend/app/domain/entities/` (estructura existente del plan).
- Contratos: AC-013-01, AC-013-02, AC-013-09, AC-013-10
- Entregables: `backend/app/domain/entities/notification.py` (entidad, enum, puerto `EmailProvider`, stub `LoggingEmailSender`).
- Aceptacion: Clase `Notification` como entity con campos id/clinic_id/user_id/event_type/subject/body/ref_type/ref_id/is_read/read_at/created_at. Enum `NotificationEventType` con cinco valores. Clase base ABC `EmailProvider` con metodo `send(email, subject, body)`. Implementacion `LoggingEmailSender` escribe `recipient`, `subject`, `provider` via logger.info sin enviar por red.
- Validacion: `python -c "from app.domain.entities.notification import Notification, NotificationEventType, EmailProvider, LoggingEmailSender"` sin errores de importacion.
- Resultado: Entidades y puerto expuestos para consumo del application layer.

### BE-013-T02 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-013-09
- Objetivo: Crear la db table notifications con constraint unico.
- Depende de: BE-013-T01
- Contexto: `backend/alembic/versions/a012_reviews.py` (head actual); modelos de T01; `backend/core/config.py`.
- Contratos: AC-013-09
- Entregables: `backend/alembic/versions/a013_notifications.py`.
- Aceptacion: RevisionId `a013`, down_revision apunta a head actual. Tabla `notifications` con columnas id(UUID PK), clinic_id (UUID FK clinics), user_id (UUID FK internal_users), event_type (Varchar, value del enum), subject (Varchar 2048 no HTML), body (Text max 2048), ref_type (Varchar nullable), ref_id (UUID nullable), is_read (Boolean default False), read_at (DateTime nullable), created_at (DateTime UTC). Index unique `(user_id, event_type, ref_type, ref_id)`. Indexes sobre `user_id` e `is_read`. Downgrade sin perder datos de otras tablas.
- Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores de schema.
- Resultado: Esquema base de datos validado con migracion reversible.

### BE-013-T03 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-013-01, AC-013-04, AC-013-05
- Objetivo: Implementar capa repository para operacion de creacion.
- Depende de: BE-013-T02
- Contexto: Patrón repositorio existente en `backend/app/data/` (ejemplo payment_repo.py); ORM session factory del core.
- Contratos: AC-013-01, AC-013-04, AC-013-05
- Entregables: `backend/app/data/notification_repo.py` con ABC e implementacion SQLAlchemy; metodos `create_if_unique`, `list_by_user(user_id, page, page_size, unread_only)`, `get_by_id_for_user(id, user_id)`, `mark_read(id, user_id)`, `mark_all_read(user_id, clinic_id)`, `count_unread(user_id, clinic_id)`.
- Aceptacion: Todos los metodos cubren operaciones del plan; sin logica de negocio beyond persistencia. Filtros por receptor y tenant aplicados en todas las consultas.
- Validacion: `pytest app/tests/data/test_notification_repo.py -q` con session fake/mocked; todos PASSED.
- Resultado: Acceso a datos tipado, testeable, aislado del dominio directo.

### BE-013-T04 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-013-01, AC-013-02, AC-013-11
- Objetivo: Centralizar la logica de creacion de notificaciones.
- Depende de: BE-013-T03
- Contexto: Reglas de entidad del plan; puerto EmailProvider de T01; estructura de use cases en `backend/app/application/`.
- Contratos: AC-013-01, AC-013-02, AC-013-10, AC-013-11
- Entregables: `backend/app/application/notification_use_cases.py` con `NotificationService` metodos emit, list_for_user, get_by_id, mark_as_read, mark_all_as_read, count_unread. Nota: se ubico en notification_use_cases.py no en use_cases/notify_service.py. emit aplica dedup silenciosa via repo.create_if_unique y siempre llama email_provider.send tras crear; default LoggingEmailSender; fallback try/except sin propagar.
- Aceptacion: Emit verifica existencia por constraint unico antes de insertar. Si ya existe → retorna sin insertar y sin raise (dedup silencioso). EmailProvider.send se invoca siempre tras crear notificacion; el stub produce log verificable. Sin excepcion visible en caso de fallos del provider (try/except en el edge case).
- Validacion: `pytest app/tests/application/test_notify_service.py -q` con logs asserts y dedup scenarios.
- Resultado: Reglas de emision centralizadas, probadas unitariamente, sin exposicion de datos sensibles.

### BE-013-T05 - COMPLETADA
- Tipo: api
- Criterio: AC-013-04, AC-013-06
- Objetivo: Exponer endpoint de marcacion con guardas.
- Depende de: BE-013-T04
- Contexto: `backend/app/api/v1/routers/` (listado de routers); schema notification_schemas; patron router del plan; core security get_current_access_user.
- Contratos: AC-013-01, AC-013-04, AC-013-05, AC-013-06, AC-013-08, AC-013-12
- Entregables: `backend/app/api/v1/routers/notification_router.py`, `backend/app/api/schemas/notification_schemas.py`; registro en main router bajo `/api/v1/notifications`. (Nota: schemas viven en `app/application/notification_use_cases.py` — NotificationList, NotificationRead — no se creo `app/api/schemas/notification_schemas.py`).
- Aceptacion: GET paginado lista por receptor y tenant; GET unread-count entrega conteo entero sin revelar datos ajenos; POST read valida ownership (user_id match); POST read-all valida token activo scoping; errores 401 (sin token), 404 (no receptor/ajeno) legibles sin enumerar; 422 por params invalidos con detalle; 500 sin stack trace ni ORM leak.
- Validacion: `pytest app/tests/api/test_notification_api.py -q` todos PASSED.
- Resultado: Contrato API completo y validado con OpenAPI visible.

### BE-013-T06 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-013-01, AC-013-02
- Objetivo: Integrar evento de citas con emision de notificaciones.
- Depende de: BE-013-T04
- Contexto: Routers y use cases de citas, consultas, recetas y pagos (BE-012 APPROVED en matriz); porta `NotificationEmitter`; AC-013-01 como referencia.
- Contratos: AC-013-01, AC-013-02
- Entregables: Helper `backend/app/api/v1/routers/_notify.py` con `emit_notify()` (async, try/except, no bloquea caller). Integracion en 5 lugares de 4 routers: appointment_router.py:280 (appointment_created), appointment_router.py:451 (appointment_confirmed/cancelled/completed/no_show/approved), payments_router.py:190 (payment_completed/cancelled), consultation_router.py:245 (consultation_completed), prescription_router.py:246 (prescription_created). Enum canonico `NotificationEventType` alineado con los 10 event types emitidos (5 genericos del plan cubren los granulares: APPOINTMENT_STATUS_CHANGED -> 5 eventos, PAYMENT_RECEIVED -> completed/cancelled). Guard `is_valid_event_type` en `NotificationService.emit` (test nuevo validacion de 10 eventos).
- Aceptacion: Cada evento genera notificacion para el receptor sin alterar respuestas existentes del flujo principal. Dedup probado llamando dos veces al mismo evento (doble emit). EmailProvider llamado una sola vez por emision; errores del provider no propagan excepcion a caller. Sin regresion de la respuesta HTTP original del endpoint que dispara el evento.
- Validacion: `pytest app/tests/application/test_notify_emission_per_flow.py -q` con cobertura >= 80% cada flujo.
- Resultado: Emision automatica sin regresion en los flujos de negocio principales.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
