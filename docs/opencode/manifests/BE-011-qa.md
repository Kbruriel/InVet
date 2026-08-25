---
manifest_version: 1
slice: "011"
layer: qa
generated_at: 2026-08-25T17:32:05+00:00
source_plan: docs/opencode/plans/BE-011-plan.md
source_plan_sha256: 91a3f6f70e23aa02c6a0037099a49513d1a5d802457596628d9e22a0ef287d3c
source_task: docs/opencode/tasks/qa/QA-011.md
source_task_sha256: 9e7088d40a3cfb7be4ab064a1b56d889db382b41d15019beca6d4d5891603b6d
---

# BE-011 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-011.md`

## Archivos permitidos

- `backend/app/tests/**`
- `backend/app/tests/api/test_payments_auth.py`
- `backend/app/tests/api/test_payments_create.py`
- `backend/app/tests/api/test_payments_idor.py`
- `backend/app/tests/api/test_payments_negative.py`
- `backend/app/tests/api/test_payments_read.py`
- `docs/opencode/checkpoints/BE-011-qa.json`
- `docs/opencode/manifests/BE-011-qa.md`
- `docs/opencode/plans/BE-011-plan.md`
- `docs/opencode/qa/**`
- `frontend/playwright/tests/test_payments_happy_path.py`
- `frontend/playwright/tests/test_payments_states.py`

## Tareas

### QA-011-T01 - COMPLETADA
- Tipo: prueba
- Criterio: QA-011: C1, C7
- Objetivo: Validar el happy path del flujo de pagos.
- Depende de: BE-011-T05, BE-011-T06, FE-011-T05
- Contexto: `docs/opencode/tasks/qa/QA-011.md`; endpoints del plan; APIA-011; UIA-011
- Contratos: AC-011-01, AC-011-04, AC-011-05
- Entregables: `backend/app/tests/api/test_payments_create.py` (happy), `backend/app/tests/api/test_payments_read.py`, `frontend/playwright/tests/test_payments_happy_path.py`
- Aceptacion: POST valida cita y servicio, change_amount correcto; GET detalle 200; GET listado 200 con meta; UI muestra creacion y listado.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_create.py app/tests/api/test_payments_read.py -q`.
- Resultado: Flujo operativo de pagos funcional end-to-end.

### QA-011-T02 - COMPLETADA
- Tipo: prueba
- Criterio: QA-011: C5
- Objetivo: Validar rechazos de pagos invalidos con errores claros.
- Depende de: QA-011-T01
- Contexto: `docs/opencode/tasks/qa/QA-011.md`; errores 400/422/409
- Contratos: AC-011-02, AC-011-05
- Entregables: `backend/app/tests/api/test_payments_negative.py` (409, 422)
- Aceptacion: 422 cita inexistente; 422 servicio inactivo; 422 cambio negativo; 409 cancelar pago ya cancelado; errores claros sin filtrar internals.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_negative.py -q`.
- Resultado: Validaciones de negocio y consistencia de errores cubiertas.

### QA-011-T03 - COMPLETADA
- Tipo: prueba
- Criterio: QA-011: C2, C3, C4
- Objetivo: Validar controles de seguridad ante acceso cruzado a pagos.
- Depende de: QA-011-T01
- Contexto: `docs/opencode/tasks/qa/QA-011.md`; riesgos IDOR/BOLA del plan
- Contratos: AC-011-06, AC-011-07
- Entregables: `backend/app/tests/api/test_payments_idor.py`, `backend/app/tests/api/test_payments_auth.py`
- Aceptacion: 401 sin token en todos los endpoints; 403 propietario al crear/cancelar; 404/403 clinico de otra clinica al leer/cancelar.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_payments_idor.py app/tests/api/test_payments_auth.py -q`.
- Resultado: Sin hallazgos de seguridad IDOR/BOLA/rol en pagos.

### QA-011-T04 - COMPLETADA
- Tipo: prueba
- Criterio: QA-011: C6, C8
- Objetivo: Validar los estados UI del flujo de pagos.
- Depende de: BE-011-T05, FE-011-T05
- Contexto: `docs/opencode/tasks/qa/QA-011.md`; `docs/opencode/tasks/ui-automation/UIA-011.md`; `src/shared/ui`
- Contratos: AC-011-08
- Entregables: `frontend/playwright/tests/test_payments_states.py`
- Aceptacion: Formulario, listado y detalle muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
- Validacion: `cd frontend && npx playwright test tests/ui/test_payments_states.py`.
- Resultado: Estados UX del flujo de pagos verificados en UI.

## Brief de capa

## Objetivo
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
