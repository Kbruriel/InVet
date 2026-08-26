---
manifest_version: 1
slice: "012"
layer: qa
generated_at: 2026-08-26T22:28:54+00:00
source_plan: docs/opencode/plans/BE-012-plan.md
source_plan_sha256: 65260d71a32cd8c0276f060281ad2f3b6915736c0db0a2921ef8786ad41c26da
source_task: docs/opencode/tasks/qa/QA-012.md
source_task_sha256: fc27c34479c5e11e1f73c2bd617e37ed8fe01dbcfe1fc19f04857c47e49040cb
---

# BE-012 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-012.md`

## Archivos permitidos

- `backend/app/tests/**`
- `backend/app/tests/api/test_reviews_auth.py`
- `backend/app/tests/api/test_reviews_create.py`
- `backend/app/tests/api/test_reviews_idor.py`
- `backend/app/tests/api/test_reviews_negative.py`
- `backend/app/tests/api/test_reviews_public.py`
- `backend/app/tests/api/test_reviews_respond.py`
- `docs/opencode/checkpoints/BE-012-qa.json`
- `docs/opencode/manifests/BE-012-qa.md`
- `docs/opencode/plans/BE-012-plan.md`
- `docs/opencode/qa/**`
- `frontend/src/features/reviews/*.test.tsx`

## Tareas

### QA-012-T01 - COMPLETADA
- Tipo: prueba
- Criterio: AC-012-01, AC-012-07, AC-012-09
- Objetivo: Validar el happy path de calificar una cita.
- Depende de: BE-012-T05, BE-012-T06, FE-012-T05
- Contexto: `docs/opencode/tasks/qa/QA-012.md`; endpoints del plan; APIA-012; UIA-012
- Contratos: AC-012-01, AC-012-05, AC-012-07, AC-012-08
- Entregables: `backend/app/tests/api/test_reviews_create.py` (happy), `backend/app/tests/api/test_reviews_public.py`, `backend/app/tests/api/test_reviews_respond.py` (happy)
- Aceptacion: POST /reviews 201 con recálculo de RatingSummary; GET publico 200 con items y meta; POST respond 200; UI del propietario, publico y clinico muestran los flujos.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_create.py app/tests/api/test_reviews_public.py app/tests/api/test_reviews_respond.py -q`.
- Resultado: Flujo de reseñas funcional end-to-end.

### QA-012-T02 - COMPLETADA
- Tipo: prueba
- Criterio: AC-012-02, AC-012-03, AC-012-05, AC-012-15
- Objetivo: Validar rechazos de reseñas invalidas con errores claros.
- Depende de: QA-012-T01
- Contexto: `docs/opencode/tasks/qa/QA-012.md`; errores 422/409
- Contratos: AC-012-02, AC-012-03, AC-012-05
- Entregables: `backend/app/tests/api/test_reviews_negative.py`
- Aceptacion: 422 cita no COMPLETED; 422 rating fuera de rango; 422 comment >2048; 409 segunda reseña de la misma cita; 409 segunda respuesta de una reseña; errores claros sin filtrar internals.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_negative.py -q`.
- Resultado: Validaciones de negocio y consistencia de errores cubiertas.

### QA-012-T03 - COMPLETADA
- Tipo: prueba
- Criterio: AC-012-04, AC-012-06, AC-012-12, AC-012-13
- Objetivo: Validar controles de seguridad ante acceso cruzado a reseñas.
- Depende de: QA-012-T01
- Contexto: `docs/opencode/tasks/qa/QA-012.md`; riesgos IDOR/BOLA del plan
- Contratos: AC-012-06, AC-012-12, AC-012-13
- Entregables: `backend/app/tests/api/test_reviews_idor.py`, `backend/app/tests/api/test_reviews_auth.py`
- Aceptacion: 401 sin token en todos los endpoints; 403 propietario al responder; 404 staff de otra sucursal al responder/leer; 404 cita ajena al tenant al crear.
- Validacion: `docker compose run --rm backend pytest app/tests/api/test_reviews_idor.py app/tests/api/test_reviews_auth.py -q`.
- Resultado: Sin hallazgos de seguridad IDOR/BOLA/rol en reseñas.

### QA-012-T04 - COMPLETADA
- Tipo: prueba
- Criterio: AC-012-10, AC-012-11
- Objetivo: Validar los estados UI del flujo de reseñas.
- Depende de: BE-012-T05, FE-012-T05
- Contexto: `docs/opencode/tasks/qa/QA-012.md`; `docs/opencode/tasks/ui-automation/UIA-012.md`; `src/shared/ui`
- Contratos: AC-012-10, AC-012-11
- Entregables: `frontend/src/features/reviews/*.test.tsx` (Jest)
- Aceptacion: Calificar cita, listado publico, listado clinico y respuesta muestran los cinco estados (loading, submitting, empty, success, error); error banner legible; CTA en empty; responsive en desktop y mobile.
- Validacion: `cd frontend && npx jest src/features/reviews`.
- Resultado: Estados UX del flujo de reseñas verificados en UI.

## Brief de capa

## Objetivo
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
