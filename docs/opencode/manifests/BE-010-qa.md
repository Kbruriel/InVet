---
manifest_version: 1
slice: "010"
layer: qa
generated_at: 2026-08-22T20:31:02+00:00
source_plan: docs/opencode/plans/BE-010-plan.md
source_plan_sha256: af794d2bbdf8683f4a31f941baae267569ca8d2fb817dcbfa6a27a487371887e
source_task: docs/opencode/tasks/qa/QA-010.md
source_task_sha256: 647b9bf1dc6afb107b5649518166985e2db4df8820d098022bd2d1432ec32344
---

# BE-010 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-010.md`

## Archivos permitidos

- `backend/app/tests/**`
- `backend/app/tests/api/test_prescriptions_auth.py`
- `backend/app/tests/api/test_prescriptions_create.py`
- `backend/app/tests/api/test_prescriptions_idor.py`
- `backend/app/tests/api/test_prescriptions_negative.py`
- `docs/opencode/checkpoints/BE-010-qa.json`
- `docs/opencode/manifests/BE-010-qa.md`
- `docs/opencode/plans/BE-010-plan.md`
- `docs/opencode/qa/**`
- `tests/ui/test_prescriptions_happy_path.py`
- `tests/ui/test_prescriptions_states.py`

## Tareas

### QA-010-T01 - COMPLETADA
- Tipo: prueba
- Criterio: AC-010-01, AC-010-02, AC-010-04, AC-010-05
- Objetivo: Validar el happy path del flujo de prescripciones.
- Depende de: BE-010-T07, BE-010-T09, FE-010-T05
- Contexto: `docs/opencode/tasks/qa/QA-010.md`; endpoints del plan; contratos GET/POST prescripciones; `docs/opencode/tasks/api-automation/APIA-010.md`; `docs/opencode/tasks/ui-automation/UIA-010.md`
- Contratos: AC-010-01, AC-010-02, AC-010-04, AC-010-05
- Entregables: `backend/app/tests/api/test_prescriptions_create.py` (happy path) y `tests/ui/test_prescriptions_happy_path.py`
- Aceptacion: POST valida consulta completed, items, tratamientos y recordatorios; GET detalle 200; GET listado por mascota 200 con meta; UI muestra creacion y listado.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_create.py -q` y Playwright happy path.
- Resultado: Flujo clinico de prescripciones funcional end-to-end.

### QA-010-T02 - COMPLETADA
- Tipo: prueba
- Criterio: AC-010-02, AC-010-07
- Objetivo: Validar rechazos de prescripciones invalidas con errores claros.
- Depende de: QA-010-T01
- Contexto: `docs/opencode/tasks/qa/QA-010.md`; errores 400/422/409; risks BOLA del plan
- Contratos: AC-010-02, AC-010-07
- Entregables: `backend/app/tests/api/test_prescriptions_negative.py` (400, 422, 409)
- Aceptacion: 422 consulta no existe; 422 consulta no completed; 409 duplicado por consulta; 422 items invalidos; errores claros sin filtrar internals.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_negative.py -q` con 402/409/422 esperados.
- Resultado: Validaciones de negocio y consistencia de errores cubiertas.

### QA-010-T03 - COMPLETADA
- Tipo: prueba
- Criterio: AC-010-08, AC-010-09, AC-010-10
- Objetivo: Validar controles de seguridad ante acceso cruzado a recetas.
- Depende de: QA-010-T01
- Contexto: `docs/opencode/tasks/qa/QA-010.md`; riesgos IDOR/BOLA; `backend/app/tests/api/test_prescriptions_idor.py` (si existe ya)
- Contratos: AC-010-08, AC-010-09, AC-010-10
- Entregables: `backend/app/tests/api/test_prescriptions_idor.py`, `backend/app/tests/api/test_prescriptions_auth.py`
- Aceptacion: 401 sin token en todos los endpoints; 403 propietario al crear; 403 veterinario de otra clinica; 404/403 lectura de receta ajena.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_prescriptions_idor.py app/tests/api/test_prescriptions_auth.py -q` (PASS).
- Resultado: Sin hallazgos de seguridad IDOR/BOLA/rol en prescripciones.

### QA-010-T04 - COMPLETADA
- Tipo: prueba
- Criterio: AC-010-11
- Objetivo: Validar los estados UI del flujo de prescripciones.
- Depende de: BE-010-T09, FE-010-T05
- Contexto: `docs/opencode/tasks/qa/QA-010.md`; `docs/opencode/tasks/ui-automation/UIA-010.md`; `src/shared/ui`
- Contratos: AC-010-11
- Entregables: `tests/ui/test_prescriptions_states.py`
- Aceptacion: Formulario y listado muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
- Validacion: `cd frontend && npx playwright test tests/ui/test_prescriptions_states.py` (PASS).
- Resultado: Estados UX del flujo de prescripciones verificados en UI.

## Brief de capa

## Objetivo
Validar creación, estados y notificaciones mínimas.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
