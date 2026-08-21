---
manifest_version: 1
slice: "009"
layer: qa
generated_at: 2026-08-21T17:54:21+00:00
source_plan: docs/opencode/plans/BE-009-plan.md
source_plan_sha256: e2f99a172c4892887dc10f998c345fd25a16a9644b3e3d7e64d335f42344688e
source_task: docs/opencode/tasks/qa/QA-009.md
source_task_sha256: ee1c180ea2b2686d0b514e3556503ceaf3b6bea44132ce325218d39995d35cd4
---

# BE-009 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-009.md`

## Archivos permitidos

- `backend/app/tests/**`
- `docs/opencode/checkpoints/BE-009-qa.json`
- `docs/opencode/manifests/BE-009-qa.md`
- `docs/opencode/plans/BE-009-plan.md`
- `docs/opencode/qa/**`
- `docs/opencode/qa/QA-009-findings.md`
- `docs/opencode/qa/QA-009-results.md`

## Tareas

### QA-009-T01 - COMPLETADA
- Tipo: qa
- Criterio: AC-009-01, AC-009-03, AC-009-04
- Objetivo: Validar el happy path del flujo de consultas.
- Depende de: BE-009-T08, FE-009-T04
- Contexto: plan canonico; `docs/opencode/tasks/qa/QA-009.md`; sidecars `US-009.md`, `UIA-009.md`, `APIA-009.md`; contrato Docker y pruebas
- Contratos: AC-009-01, AC-009-03, AC-009-04
- Entregables: Seccion happy path en `docs/opencode/qa/QA-009-results.md` con comandos y salidas.
- Aceptacion: POST crea consulta 201; owner ve historial paginado; owner ve detalle en solo lectura; evidencia reproducible de cada paso.
- Validacion: `docker compose run --rm backend pytest app/tests/ -q -k consultation` + ejecucion de UIA-009 C1/C2/C3; salida registrada en results.
- Resultado: Happy path PASS con evidencia de API y UI.

### QA-009-T02 - COMPLETADA
- Tipo: qa
- Criterio: AC-009-02, AC-009-06, AC-009-10
- Objetivo: Validar que los negative paths fallan con errores claros sin exponer detalles internos.
- Depende de: QA-009-T01
- Contexto: `docs/opencode/tasks/qa/QA-009.md`; APIA-009 casos de errores; endpoints del plan
- Contratos: AC-009-02, AC-009-06, AC-009-10
- Entregables: Seccion negative path en `docs/opencode/qa/QA-009-results.md` con codigos HTTP y mensajes.
- Aceptacion: cita no completed → 422; duplicado appointment_id → 409; campo requerido ausente → 422 legible sin detalles internos.
- Validacion: `docker compose run --rm backend pytest app/tests/ -q -k "consultations"` con los casos negativos; salidas registradas en results.
- Resultado: Negative paths PASS con errores consistentes y sin filtracion de datos internos.

### QA-009-T03 - COMPLETADA
- Tipo: qa
- Criterio: AC-009-05, AC-009-11, AC-009-12
- Objetivo: Validar los controles de seguridad ante acceso cruzado a consultas.
- Depende de: QA-009-T01
- Contexto: `docs/opencode/tasks/qa/QA-009.md`; APIA-009 casos IDOR/auth; riesgos del plan
- Contratos: AC-009-05, AC-009-11, AC-009-12
- Entregables: Seccion permisos en `docs/opencode/qa/QA-009-results.md`; findings en `docs/opencode/qa/QA-009-findings.md` si hay FAIL.
- Aceptacion: sin token → 401; vet de otra clinica → 403; owner A no ve mascotas de owner B; respuestas sin datos ajenos expuestos.
- Validacion: `docker compose run --rm backend pytest app/tests/ -q -k "consultations_idor or consultations_auth"`; salidas registradas en results.
- Resultado: Permisos y IDOR/BOLA PASS sin hallazgos OPEN de seguridad.

### QA-009-T04 - COMPLETADA
- Tipo: qa
- Criterio: AC-009-07, AC-009-08, AC-009-09, AC-009-13
- Objetivo: Validar los estados UI del flujo principal de consultas.
- Depende de: QA-009-T01
- Contexto: `docs/opencode/tasks/frontend/FE-009.md`; UIA-009; contrato frontend del plan
- Contratos: AC-009-07, AC-009-08, AC-009-09, AC-009-13
- Entregables: Seccion UI/regresion en `docs/opencode/qa/QA-009-results.md` con capturas textuales o resumen de UI.
- Aceptacion: formulario con loading/submitting/success/error; listado con loading/success/empty; detalle read-only; flujo principal sin regresion.
- Validacion: `npx playwright test --project=chromium` para UIA-009 + `cd frontend && npm run test && npm run lint && npm run typecheck` sin errores nuevos.
- Resultado: Estados UI y regresion PASS con evidencia de navegador.

### QA-009-T05 - COMPLETADA
- Tipo: reporte
- Criterio: AC-009-14
- Objetivo: Validar la migracion Alembic del schema de consultas.
- Depende de: QA-009-T02, QA-009-T03, QA-009-T04
- Contexto: `docs/opencode/qa/QA-009-results.md` parcial; `backend/alembic/versions/`; contrato Docker
- Contratos: AC-009-14
- Entregables: `docs/opencode/qa/QA-009-results.md` completo con Decision APPROVED/REJECTED y seccion de migracion; `docs/opencode/qa/QA-009-findings.md` solo si hay FAIL.
- Aceptacion: `alembic upgrade head` y `alembic downgrade -1 && alembic upgrade head` sin errores; results file con Decision y evidencias de todas las areas.
- Validacion: `python backend/scripts/validate_slice_plan.py BE-009 --stage qa` → PASS.
- Resultado: QA-009 APPROVED con evidencias completas o findings registrados.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
