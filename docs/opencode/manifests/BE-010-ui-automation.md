---
manifest_version: 1
slice: "010"
layer: ui-automation
generated_at: 2026-08-22T20:31:02+00:00
source_plan: docs/opencode/plans/BE-010-plan.md
source_plan_sha256: af794d2bbdf8683f4a31f941baae267569ca8d2fb817dcbfa6a27a487371887e
source_task: docs/opencode/tasks/ui-automation/UIA-010.md
source_task_sha256: 897caf3ecbfd4599bb91215c63813f66f0d3743ab722c7c39f765e9da9b35339
---

# BE-010 - manifiesto compacto ui-automation

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
- Archivo: `docs/opencode/tasks/ui-automation/UIA-010.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-010-ui-automation.json`
- `docs/opencode/manifests/BE-010-ui-automation.md`
- `docs/opencode/plans/BE-010-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-010.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar el flujo UI de prescripciones (formulario clinico, historial por mascota y detalle read-only) con Playwright, cubriendo estados UX, validaciones, permisos visibles y responsive.
## Alcance
| Caso | Vista | Rol | Esperado |
| --- | --- | --- | --- |
| C1 acceso formulario | `clinic/appointments/[id]/prescription` | veterinario | Formulario con diagnosis, treatment_notes, items, tratamientos, recordatorios editables |
| C2 validacion inline | formulario | veterinario | Error inline si diagnosis vacio o excede 2000 chars |
| C3 crear OK | formulario → success | veterinario | Toast de exito y navegacion a detalle |
| C4 propietarios no ven create | `clinic/appointments/[id]/prescription` | propietario | Sin ruta/accion de creacion; 403 legible si accede por URL |
| C5 historial | `portal/owner/pets/[petId]/prescriptions` | propietario | Listado paginado con meta; estados loading/success/empty/error |
| C6 detalle | `portal/owner/prescriptions/[id]` | propietario | Secciones items, tratamientos, recordatorios legibles; sin botones de edicion |
| C7 receta ajena | `portal/owner/prescriptions/{id_otro}` | propietario | Estado empty/error legible sin filtrar internas |
| C8 responsive | formulario + listado + detalle | ambos | Usable en desktop y mobile |
| C9 acentos | todas las vistas | ambos | Acentos y e-ñ sin mojibake |
## Suite y archivos
- `frontend/playwright/tests/test_prescriptions_happy_path.py` — C1, C3, C5, C6.
- `frontend/playwright/tests/test_prescriptions_states.py` — C5, C6, C8, C9.
- `frontend/playwright/tests/test_prescriptions_access.py` — C2, C4, C7.
## Ejecucion
```
docker compose up -d --build --force-recreate db backend frontend
cd frontend && npx playwright test
```
## Criterios de aceptacion
- Todos los casos C1..C9 en `PASS`.
- Estados UX (loading, submitting, empty, success, error) observables por cada componente.
- Sin links `#` en flujos implementados del slice.
- No se loggean datos clinicos sensibles en consola.
- Responsive verificable en ambos breakpoints.
- Sin regresion de UIA-009.
## Evidencia requerida
- Comandos ejecutados y codigo de salida.
- Capturas o resumen textual de UI por caso.
- Defectos (si aplica) con pasos de reproduccion.
- Riesgo residual si aplica.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
