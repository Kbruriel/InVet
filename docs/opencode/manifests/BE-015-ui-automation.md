---
manifest_version: 1
slice: "015"
layer: ui-automation
generated_at: 2026-09-02T21:43:43+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: f2d8b7e3c7dbba5f0b9967c5a8e6998a36b593d1fda23b958ce78eda940cff6b
source_task: docs/opencode/tasks/ui-automation/UIA-015.md
source_task_sha256: 166fbf3045c3d825762444ff7697f04467c63033e2ae0ce58bebc38f277b1cfa
---

# BE-015 - manifiesto compacto ui-automation

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
- Archivo: `docs/opencode/tasks/ui-automation/UIA-015.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-015-ui-automation.json`
- `docs/opencode/manifests/BE-015-ui-automation.md`
- `docs/opencode/plans/BE-015-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-015.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Proposito
Ejecutar pruebas E2E con Playwright contra el frontend (`http://localhost:3000`) para verificar que las pantallas de reportes operativos muestran filtros, tablas resumidas, estados UX y respuestas correctas por periodo.
## Alcance y cobertura
| Caso | Cubre criterio(s) | Ruta | Accion esperada | Estado UX |
| --- | --- | --- | --- | --- |
| UIA-C1 | AC-015-01, AC-015-02 | `/portal/admin/reports` | Seleccionar tip de reporte y fechas; verificar tabla carga sin error | success |
| UIA-C2 | AC-015-03 | `/portal/admin/reports?type=appointments&page=1&limit=20` | Recibir paginacion con <=20 elementos | success / empty |
| UIA-C3 | AC-015-04 | `/portal/admin/reports?type=services&page=1` | Ver campos resumidos de servicios en tabla | success |
| UIA-C4 | AC-015-06 | `/portal/admin/reports?type=pets&clinic_id=VALID_CLINIC_ID` | Mostrar conteo total correcto | data loaded |
| UIA-C5 | AC-015-07 | `/portal/admin/reports?type=ratings&period_start=YYYY-MM-DD&period_end=YYYY-MM-DD` | Ver promedio de calificaciones | success / empty |
| UIA-C6 | AC-015-08 | `/portal/admin/reports?type=payments&page=1` | Ver totales de pagos en tabla resumida | success / empty |
| UIA-C7 | AC-015-04, AC-015-05 | Invalid date range | mostrar invalid date message | error |
| UIA-C8 | AC-015-09 | `/portal/admin/reports` sin token auth navegar a login | 403 → redirigir /login | auth block |
| UIA-C9 | Responsive | Todas las vistas de reportes | Verificar en viewport mobile (375px) y desktop (1366px) | responsive ok |
## Estados UX cubiertos
- **loading**: spinner visible mientras se cargan los datos del endpoint.
- **empty**: mensaje "No hay datos para este periodo" cuando no hay registros.
- **error**: banner de error al recibir 500/422.
- **success**: tabla renderizada correctamente con datos.
## Rutas cubiertas
- `/portal/admin/reports` — Panel principal de reportes.
- `/portal/clinic/reports` — Vista alternativa para clinic admin (si existe ruta separada).
## Evidencia pendiente
| Caso | Estado evidencia | Comandos |
| --- | --- | --- |
| UIA-C1 | pending | npx playwright test tests/e2e/report-summary.spec.ts |
| UIA-C2 | pending | npx playwright test tests/e2e/reports-pagination.spec.ts |
| UIA-C3 | pending | npx playwright test tests/e2e/reports-services.spec.ts |
| UIA-C4 | pending | npx playwright test tests/e2e/reports-pets.spec.ts |
| UIA-C5 | pending | npx playwright test tests/e2e/reports-ratings.spec.ts |
| UIA-C6 | pending | npx playwright test tests/e2e/reports-payments.spec.ts |
| UIA-C7 | pending | npx playwright test tests/e2e/reports-invalid-input.spec.ts |
| UIA-C8 | pending | npx playwright test tests/e2e/reports-auth.spec.ts |
| UIA-C9 | pending | npx playwright test --project=chromium tests/e2e/reports-responsive.spec.ts |
## Casos no automatizados en este slice
- Integraciones con graficos/visualizaciones de reportes (fuerza externa).
- Flujos multi-pagina complejos de navegacion dentro del reporte.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
