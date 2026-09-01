---
manifest_version: 1
slice: "013"
layer: qa
generated_at: 2026-08-31T23:55:16+00:00
source_plan: docs/opencode/plans/BE-013-plan.md
source_plan_sha256: 642c5f6278818acb924edc251bd441cb236522a3b33398f4d0b9908df3289a42
source_task: docs/opencode/tasks/qa/QA-013.md
source_task_sha256: 3d51e97879972460d85c76103fa638ef607a92ea9aa55c137bf90d22bb2cee29
---

# BE-013 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-013.md`

## Archivos permitidos

- `backend/app/tests/**`
- `backend/app/tests/api/test_notifications_auth.py`
- `backend/app/tests/api/test_notifications_happy.py`
- `backend/app/tests/api/test_notifications_negative.py`
- `docs/opencode/checkpoints/BE-013-qa.json`
- `docs/opencode/manifests/BE-013-qa.md`
- `docs/opencode/plans/BE-013-plan.md`
- `docs/opencode/qa/**`
- `frontend/playwright/tests/notifications/center.spec.ts`

## Tareas

### QA-013-T01 - COMPLETADA
- Tipo: prueba
- Criterio: AC-013-01, AC-013-04
- Objetivo: Confirmar generacion de notificacion visible por cada evento.
- Depende de: BE-013-T04, BE-013-T05, FE-013-T02
- Contexto: Endpoints del plan; UIA-013 casos C1..C5; APIA-013 casos C1..C6.
- Contratos: AC-013-01, AC-013-04
- Entregables: `backend/app/tests/api/test_notifications_happy.py`; UIA-013 C1..C5; APIA C1.
- Aceptacion: POST emite notificacion con status 201 o 204 silencioso (no-body response); GET lista devuelve items correctos en primera pagina con meta `{page, page_size, total, pages}` correcto; marcacion individual reduce el conteo unread (verified via count endpoint); leer todas retorna `updated > 0` y list filtrada por unread_only=true vuelve vacio.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_happy.py -q`.
- Resultado: Flujo completo de creccion/listado/marcacion funcionando correctamente.

### QA-013-T02 - COMPLETADA
- Tipo: prueba
- Criterio: AC-013-03, AC-013-05
- Objetivo: Validar respuestas ante datos invalidos de paginacion.
- Depende de: BE-013-T02, BE-013-T04
- Contexto: Errores 422/409; constraint unico `notification_repo` dedup en use case.
- Contratos: AC-013-03, AC-013-05, AC-013-11
- Entregables: `backend/app/tests/api/test_notifications_negative.py`.
- Aceptacion: page < 1 → 422; page_size > 200 → 422 con detalle legible sin internals. Doble emision rapida en secuencia devuelve unico registro (no inserta duplicado). Marcacion leida sobre identificador inexistente → 404 consistente sin revelar existencia de otras entidades.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_negative.py -q`.
- Resultado: Reglas de paginacion y dedup confirmadas sin excepcion en los endpoints.

### QA-013-T03 - COMPLETADA
- Tipo: prueba
- Criterio: AC-013-06, AC-013-12
- Objetivo: Confirmar controles ante acceso cruzado con tokens de terceros ajenos.
- Depende de: BE-013-T05, BE-013-T06
- Contexto: Riesgos IDOR/BOLA del plan; guardas en routers T05.
- Contratos: AC-013-06, AC-013-12
- Entregables: `backend/app/tests/api/test_notifications_auth.py`, `test_notifications_idor_bola.py`.
- Aceptacion: Sin token → 401 en cuatro endpoints. Usuario A ve solo sus notificaciones y su conteo; intentar marcar leida una notificacion de otro usuario → 404 consistente (sin revelar existencia). User de clinica B nunca lista ni cuenta notificaciones de clinica A (sin enumeracion).
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_notifications_auth.py app/tests/api/test_notifications_idor_bola.py -q`.
- Resultado: Sin hallazgos de fugas IDOR o BOLA en notificaciones.

### QA-013-T04 - COMPLETADA
- Tipo: prueba
- Criterio: AC-013-07, AC-013-08
- Objetivo: Validar visualmente los cinco estados UX del centro de notificaciones.
- Depende de: FE-013-T02, FE-013-T03, BE-013-T05
- Contexto: UIA-013 casos C5..C11; componentes en frontend.
- Contratos: AC-013-07, AC-013-08
- Entregables: `frontend/playwright/tests/notifications/center.spec.ts`, `badge.spec.ts`.
- Aceptacion: loading visible durante peticion; empty centrado cuando lista vacia (mismo EmptyState); success con toast tras marcacion; error visible al forzar mock HTTP 500; badge muestra cero y >0 segun endpoint; responsive en breakpoints 320 y 1280 sin overflow; accesibilidad aria-label y foco claro.
- Validacion: `cd frontend && npx playwright test notifications --reporter=line --retries=0`.
- Resultado: Experiencia usable e informativa con feedback visual en todos los estados.

## Brief de capa

## Estado
**APPROVED** (2026-08-31)
## Objetivo
Validar eventos, lectura y no duplicados.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
