---
manifest_version: 1
slice: "013"
layer: ui-automation
generated_at: 2026-08-31T23:55:16+00:00
source_plan: docs/opencode/plans/BE-013-plan.md
source_plan_sha256: 642c5f6278818acb924edc251bd441cb236522a3b33398f4d0b9908df3289a42
source_task: docs/opencode/tasks/ui-automation/UIA-013.md
source_task_sha256: 0c5aa7c616af02c6944950bb8586613e9a137982770022170f1b6b82855d262a
---

# BE-013 - manifiesto compacto ui-automation

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
- Archivo: `docs/opencode/tasks/ui-automation/UIA-013.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-013-ui-automation.json`
- `docs/opencode/manifests/BE-013-ui-automation.md`
- `docs/opencode/plans/BE-013-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-013.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar los flujos UI del slice 013: (a) centro de notificaciones con tabs paginacion, (b) marcacion leida individual y en bloque, (c) badge no leidas integrado en header nav — con Playwright cubriendo estados UX permisos IDOR visual responsive.
## Alcance
| Caso | Vista | Rol | Esperado |
| --- | --- | --- | --- |
| C1 centro vacio | `/portal/notifications` anónimo sin token | anonimo | Redireccion a /login con returnUrl correcto |
| C2 centro con datos | `/portal/notifications autentificado propietario | propietario | Listado paginado con tabs Todas/No leidas, items visualmente diferenciados |
| C3 marcacion individual item click → mark read inmediato; item cambia color (leido)
| C4 marcar todas leidas | Tab No leidas + boton Leer todo | propietario | Toast confirmacion update > 0; lista vacia tras accion |
| C5 badge sin conteo | Header nav | propietario | Badge oculto visible cuando count == 0 |
| C6 badge con conteo | Header nav | propietario | Badge rojo numero > 0 entre parentesis; decrementa tras marcar una leida |
| C7 tab filtrada No leidas | Tab No leidas | propietario | Solo muestra items si is_read=false |
| C8 marcacion IDOR visual usuario A intenta marcar notificacion de usuario B mediante cambio de URL o token mockeado → 404 sin revelar existencia ni datos ajenos |
| C9 error redierige / login | `/portal/notifications` con session expirada | propietario | Redirection /login manteniendo returnUrl |
| C10 responsive lista | Centro notificaciones todos | Usable en mobile (320px) y desktop (≥1024px) sin overflow horizontal ni elementos superpuestos |
| C11 accesibilidad Centro de notificaciones propietario | `aria-label` en region; foco visible; contraste AA; botones con labels semanticos |
| C12 sin token listados/api calls fallback → 401; componente muestra ErrorBanner |
## Suite y archivos
- `frontend/playwright/tests/notifications/center-happy.spec.ts` — C2, C3.
- `frontend/playwright/tests/notifications/mark-read-all.spec.ts` — C4.
- `frontend/playwright/tests/notifications/badge.spec.ts` — C5, C6.
- `frontend/playwright/tests/notifications/tabs-filter.spec.ts` — C7.
- `frontend/playwright/tests/notifications/idor-visual.spec.ts` — C3, C8.
- `frontend/playwright/tests/notifications/auth-flow.spec.ts` — C1, C9, C12.
- `frontend/playwright/tests/notifications/responsive.spec.ts` — C10.
- `frontend/playwright/tests/notifications/access-a11y.spec.ts` — C11.
## Ejecución
```powershell
docker compose up -d --build --force-recreate db backend frontend
cd frontend
$env:PLAYWRIGHT_START_FRONTEND="false"
npx playwright test notifications --retries=0 --reporter=line
npx playwright test --project=chromium --retries=0 --reporter=line
npx tsc --noEmit
npx jest src/features/notifications
```
Ejecutar Playwright contra el frontend publicado por Docker (no contra next dev del host).
## Criterios de aceptación
- Casos C1..C12 en PASS.
- Estados UI loading, empty, success, error, submitting observables en el centro.
- Badge actualiza correctamente tras marcacion individual o leer todo.
- Sin links # en flujos implementados del slice.
- Sin console.log de datos sensibles (tokens payloads notificacion).
- Responsive verifiable en breakpoints 320 y 1280 sin overflow.
- Sin regresion de UIA-012 (regresion e2e de todo el repo).
## Evidencia requerida
- Comandos ejecutados y codigo de salida.
- Capturas o resumen textual por caso (centro vacio con lista paginada, item clickeable).
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
