---
manifest_version: 1
slice: "015"
layer: ui-automation
generated_at: 2026-09-07T23:29:16+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: 2e65b3a8c877e97da8639d617e56613f701fa37ee145127a0da81ace38c52823
source_task: docs/opencode/tasks/ui-automation/UIA-015.md
source_task_sha256: 5bb591832e0de1c46d4faaee5a614839a5a2f25f9468016929a37904ee986b55
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
## Evidencia ejecutada
Implementacion unica en `InVet_UI_Automation/tests/e2e/be-015-reports.spec.ts` (9 tests UIA-C1..UIA-C9).
| Caso | US/AC | Estado evidencia | Resultado |
| --- | --- | --- | --- |
| UIA-C1 | US-015-01 AC-015-01 AC-015-02 | `npm run test:e2e` (chromium) | passed |
| UIA-C2 | US-015-02 AC-015-03 | `npm run test:e2e` (chromium) | passed |
| UIA-C3 | US-015-03 AC-015-04 | `npm run test:e2e` (chromium) | passed |
| UIA-C4 | US-015-04 AC-015-06 | `npm run test:e2e` (chromium) | passed |
| UIA-C5 | US-015-05 AC-015-07 | `npm run test:e2e` (chromium) | passed |
| UIA-C6 | US-015-06 AC-015-08 | `npm run test:e2e` (chromium) | passed |
| UIA-C7 | US-015-07 AC-015-04 AC-015-05 | `npm run test:e2e` (chromium) | passed |
| UIA-C8 | US-015-08 AC-015-09 | `npm run test:e2e` (chromium) | passed |
| UIA-C9 | US-015-09 AC-015-03 | `npm run test:e2e` (chromium) | passed |
### Resumen de ejecucion
- `npm run test:e2e` (`playwright test --project=chromium tests/e2e`): **112 passed, 7 skipped (JUSTIFIED_SKIP), 0 failed** (25.1s).
- `npm run test:regression` (`playwright test tests/e2e --grep @regression --project=chromium`): **100 passed, 2 skipped, 0 failed** (20.7s).
- Los 9 tests de `be-015-reports.spec.ts` (UIA-C1..UIA-C9) pasan en ambas corridas contra el stack Docker.
- Stack Docker (3/3 healthy): `invet-backend` :8000 (healthy), `invet-db` :5432 (healthy), `invet-frontend` :3000 (healthy).
- Frontend reusado del contenedor Docker (:3000, `reuseExistingServer` true en non-CI); no se levantó host alternativo.
- Artefactos generados: `InVet_UI_Automation/playwright-report/index.html` (HTML reporter) + `test-results/`.
## Casos no automatizados en este slice
- Integraciones con graficos/visualizaciones de reportes (fuerza externa).
- Flujos multi-pagina complejos de navegacion dentro del reporte.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
