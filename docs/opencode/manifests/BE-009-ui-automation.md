---
manifest_version: 1
slice: "009"
layer: ui-automation
generated_at: 2026-08-21T17:54:21+00:00
source_plan: docs/opencode/plans/BE-009-plan.md
source_plan_sha256: e2f99a172c4892887dc10f998c345fd25a16a9644b3e3d7e64d335f42344688e
source_task: docs/opencode/tasks/ui-automation/UIA-009.md
source_task_sha256: ef797e282077006eee42f53687e3951c32b7dcd98c562bed7da8799d17d15449
---

# BE-009 - manifiesto compacto ui-automation

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Entorno Docker obligatorio

- El sistema bajo prueba es `db`, `backend` y `frontend` de Docker Compose.
- Docker ausente o un servicio no disponible produce `BLOCKED`; no existe fallback host.
- Ejecutar Playwright con `PLAYWRIGHT_START_FRONTEND=false` contra el frontend publicado.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/ui-automation/UIA-009.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-009-ui-automation.json`
- `docs/opencode/manifests/BE-009-ui-automation.md`
- `docs/opencode/plans/BE-009-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-009.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Alcance
Validar el flujo de consultas mediante pruebas automatizadas con Playwright dentro de `InVet_UI_Automation/tests/`. Cubre los criterios frontend del slice BE-009: registro de consulta (veterinario), historial por mascota y detalle individual (propietario), incluyendo estados UX y accesibilidad básica.
## Casos de prueba
### C1: Veterinario registra consulta válida desde cita completed
| Campo | Valor |
| --- | --- |
| ID | UIA-009-C01 |
| AC vinculado | AC-009-01 |
| Objetivo | Verificar que un veterinario puede crear una consulta asociada a una cita completed. |
| Precondicion | Veterinario autenticado; cita con `status=completed` sin consulta previa (BE-008). |
| Pasos | 1. Navegar a `/clinic/appointments/[id]/consultation`. 2. Completar `diagnosis`. 3. Completar `history` y `recommendations` opcionales. 4. Click en "Registrar consulta". |
| Esperado | Estado submitting visible. Success toast. Redirección o confirmación con datos de la consulta creada (201 en API). |
| Archivo esperado | `InVet_UI_Automation/tests/test_009_consultation_form.ts::consultation_form_creates` |
| Evidencia | pending |
### C2: Veterinario no registra consulta para cita no completed
| Campo | Valor |
| --- | --- |
| ID | UIA-009-C02 |
| AC vinculado | AC-009-02 |
| Objetivo | Verificar que el flujo bloquea o muestra error claro al intentar registrar sobre una cita no completed. |
| Precondicion | Veterinario autenticado; cita en estado pending/confirmed. |
| Pasos | 1. Forzar la URL `/clinic/appointments/[id]/consultation` de una cita no completed. 2. Intentar completar y enviar. |
| Esperado | Error banner legible (mismo mensaje de 422) sin datos internos. Sin creación de registro. |
| Archivo esperado | `InVet_UI_Automation/tests/test_009_consultation_form.ts::consultation_form_rejects_not_completed` |
| Evidencia | pending |
| Justificacion complementaria | La validación dura se verifica en APIA-009 (A3); la UI verifica el feedback visual del 422. |
### C3: Propietario ve historial de consultas de su mascota
| Campo | Valor |
| --- | --- |
| ID | UIA-009-C03 |
| AC vinculado | AC-009-03, AC-009-09 |
| Objetivo | Verificar que el propietario ve el listado paginado de consultas de su mascota en read-only. |
| Precondicion | Propietario autenticado; mascota con ≥ 2 consultas registradas. |
| Pasos | 1. Navegar a `/portal/owner/pets/[id]/consultations`. 2. Verificar listado ordenado por fecha descendente. 3. Usar paginación. |
| Esperado | Loading spinner inicial. Lista con items y meta de paginación. Sin botones de edición. |
| Archivo esperado | `InVet_UI_Automation/tests/test_009_owner_history.ts::owner_history_lists_consultations` |
| Evidencia | pending |
### C4: Propietario ve detalle de consulta en solo lectura
| Campo | Valor |
| --- | --- |
| ID | UIA-009-C04 |
| AC vinculado | AC-009-04, AC-009-13 |
| Objetivo | Verificar que el detalle muestra los campos clínicos legibles y el estado empty cuando no existe. |
| Precondicion | Propietario autenticado; una consulta válida y una mascota sin consultas. |
| Pasos | 1. Navegar a `/portal/owner/consultations/[id]`. 2. Verificar etiquetas legibles (diagnóstico, historia, recomendaciones). 3. Navegar a `/portal/owner/pets/[sin-consultas]/consultations`. |
| Esperado | Detalle read-only sin controles de edición. Estado empty visible para mascota sin consultas con texto descriptivo. |
| Archivo esperado | `InVet_UI_Automation/tests/test_009_consultation_detail.ts::owner_detail_shows_readonly` |
| Evidencia | pending |
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
