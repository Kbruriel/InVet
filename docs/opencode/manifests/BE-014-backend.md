---
manifest_version: 1
slice: "014"
layer: backend
generated_at: 2026-09-02T01:17:03+00:00
source_plan: docs/opencode/plans/BE-014-plan.md
source_plan_sha256: 9e3e90dab12778e6b744a7c181f6e11a8ba381f82567ebce75e6d6f1dbe3b00c
source_task: docs/opencode/tasks/backend/BE-014.md
source_task_sha256: ce50dd5661b8111f20093f6437b24211474d16b221badca481d047af2f018515
---

# BE-014 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-014.md`

## Archivos permitidos

- `backend/alembic/versions/a014_support.py`
- `backend/app/api/schemas/support_ticket_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/support_ticket_router.py`
- `backend/app/application/support_ticket_use_cases.py`
- `backend/app/data/support_ticket_repo.py`
- `backend/app/infraestructure/database/models/support_ticket_model.py`
- `backend/app/infrastructure/database/models/__init__.py`
- `backend/app/infrastructure/database/models/support_ticket_model.py`
- `backend/app/tests/**`
- `backend/app/tests/api/test_support_ticket_api.py`
- `backend/app/tests/data/test_support_ticket_repo.py`
- `backend/app/tests/usecases/test_support_ticket_rules.py`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-014-backend.json`
- `docs/opencode/manifests/BE-014-backend.md`
- `docs/opencode/plans/BE-014-plan.md`

## Tareas

### BE-014-T01 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-01, AC-02, AC-06, AC-10
- Objetivo: Crear esquema persistente de soporte.
- Depende de: Ninguna
- Contexto: Entidades SupportTicket y SupportCategory.
- Contratos: Reglas de datos del slice.
- Entregables: `backend/app/infrastructure/database/models/support_ticket_model.py`, registro del modelo en `backend/app/infrastructure/database/models/__init__.py`, `backend/alembic/versions/a014_support.py`, eliminación del duplicado inválido `backend/app/infraestructure/database/models/support_ticket_model.py` y pruebas en `backend/app/tests/api/test_support_ticket_api.py`.
- Aceptacion: La migración crea tablas, unicidad por clínica y categorías activas.
- Validacion: Aplicar migración en base aislada.
- Resultado: Esquema disponible con reversión funcional.

### BE-014-T02 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-03, AC-04, AC-11
- Objetivo: Implementar repositorio seguro de tickets.
- Depende de: BE-014-T01
- Contexto: Modelo de tickets y contexto autenticado.
- Contratos: Consulta paginada de tickets.
- Entregables: Repositorio seguro en `backend/app/data/support_ticket_repo.py` y pruebas en `backend/app/tests/data/test_support_ticket_repo.py`.
- Aceptacion: El recurso ajeno no es visible para un actor no autorizado.
- Validacion: Pruebas de lectura propia, ajena e interna.
- Resultado: Consultas aisladas por clínica.

### BE-014-T03 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-01, AC-05
- Objetivo: Centralizar reglas de soporte.
- Depende de: BE-014-T01
- Contexto: Estados permitidos y ventana de duplicados.
- Contratos: TicketStatus y reglas de dominio.
- Entregables: Reglas de creación, deduplicación de 24 horas y transición en `backend/app/application/support_ticket_use_cases.py`, consulta de duplicados en `backend/app/data/support_ticket_repo.py` y pruebas en `backend/app/tests/usecases/test_support_ticket_rules.py` y `backend/app/tests/data/test_support_ticket_repo.py`.
- Aceptacion: Rechaza duplicados y transiciones inválidas.
- Validacion: Pruebas unitarias de reglas.
- Resultado: Reglas consistentes fuera de controladores.

### BE-014-T04 - COMPLETADA
- Tipo: api
- Criterio: AC-01, AC-02, AC-03, AC-04, AC-05, AC-07, AC-11
- Objetivo: Publicar API protegida de tickets.
- Depende de: BE-014-T02, BE-014-T03
- Contexto: Casos de uso, repositorio y autenticación existente.
- Contratos: Endpoints esperados del slice.
- Entregables: Rutas y manejo de errores en `backend/app/api/v1/routers/support_ticket_router.py`, DTOs y serializadores en `backend/app/api/schemas/support_ticket_schemas.py`, registro en `backend/app/api/v1/router.py` y pruebas en `backend/app/tests/api/test_support_ticket_api.py`.
- Aceptacion: Las rutas responden según actor, contrato y transición.
- Validacion: Pruebas API autenticadas.
- Resultado: API de soporte consumible por frontend.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
