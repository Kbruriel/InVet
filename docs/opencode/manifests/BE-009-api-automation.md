---
manifest_version: 1
slice: "009"
layer: api-automation
generated_at: 2026-08-21T17:54:21+00:00
source_plan: docs/opencode/plans/BE-009-plan.md
source_plan_sha256: e2f99a172c4892887dc10f998c345fd25a16a9644b3e3d7e64d335f42344688e
source_task: docs/opencode/tasks/api-automation/APIA-009.md
source_task_sha256: 88dd9cef62e3508a9df95e81eb9feb3053ecda29ec34d3c96dab0b4f9e9450fb
---

# BE-009 - manifiesto compacto api-automation

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Entorno Docker obligatorio

- El sistema bajo prueba es `db`, `backend` y `frontend` de Docker Compose.
- Docker ausente o un servicio no disponible produce `BLOCKED`; no existe fallback host.
- Ejecutar Playwright API contra el backend publicado por Docker.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/api-automation/APIA-009.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/api/**`
- `docs/opencode/checkpoints/BE-009-api-automation.json`
- `docs/opencode/manifests/BE-009-api-automation.md`
- `docs/opencode/plans/BE-009-plan.md`
- `docs/opencode/tasks/api-automation/APIA-009.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Alcance
Validar los contratos API del slice BE-009 mediante pruebas automatizadas con HTTPX dentro de `backend/app/tests/`. Cubre creación de consulta, lectura por propietario/clinica, authn/authz, IDOR/BOLA, paginación y duplicados.
## Pruebas contractuales
### A1: Creación de consulta válida (happy path)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A01 |
| AC vinculado | AC-009-01 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario (misma clínica de la cita) |
| Request body | `{appointment_id: <cita_completed>, pet_id: <pet_de_la_cita>, diagnosis: "Fiebre y apatia", history: "Cuatro dias de anorexia", recommendations: "Analisis de sangre"}` |
| Esperado | 201 Created. Response JSON con `id`, `appointment_id`, `pet_id`, campos clínicos, `created_by`, `updated_at`. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_create_consultation_valid` |
| Evidencia | pending |
### A2: Creación sin token (401)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A02 |
| AC vinculado | AC-009-12 |
| Endpoint | POST /api/v1/consultations |
| Auth | Ninguno |
| Esperado | 401 Unauthorized con mensaje "Authentication required". |
| Archivo esperado | `tests/api/test_consultations_auth.py::test_create_without_token` |
| Evidencia | pending |
### A3: Creación para cita no completed (422)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A03 |
| AC vinculado | AC-009-02 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario |
| Request body | `{appointment_id: <cita_pending>, pet_id: <valid>, diagnosis: "..."}` |
| Esperado | 422 con mensaje legible ("appointment not completed"). Sin registro creado. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_create_for_not_completed_appointment` |
| Evidencia | pending |
### A4: GET de detalle y listado sin token (401)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A04 |
| AC vinculado | AC-009-12 |
| Endpoint | GET /api/v1/consultations/{id}; GET /api/v1/consultations?pet_id= |
| Auth | Ninguno |
| Esperado | 401 en ambos endpoints. |
| Archivo esperado | `tests/api/test_consultations_auth.py::test_get_without_token` |
| Evidencia | pending |
### A5: GET de detalle propio por propietario (200)
| Campo | Valor |
| --- | --- |
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
