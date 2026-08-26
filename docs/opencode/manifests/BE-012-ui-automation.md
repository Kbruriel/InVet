---
manifest_version: 1
slice: "012"
layer: ui-automation
generated_at: 2026-08-26T22:28:54+00:00
source_plan: docs/opencode/plans/BE-012-plan.md
source_plan_sha256: 65260d71a32cd8c0276f060281ad2f3b6915736c0db0a2921ef8786ad41c26da
source_task: docs/opencode/tasks/ui-automation/UIA-012.md
source_task_sha256: 8bac180d4bda3b34d9fa5e9a7517e51d6012649d0e025ccf7afd023c518371d7
---

# BE-012 - manifiesto compacto ui-automation

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
- Archivo: `docs/opencode/tasks/ui-automation/UIA-012.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-012-ui-automation.json`
- `docs/opencode/manifests/BE-012-ui-automation.md`
- `docs/opencode/plans/BE-012-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-012.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar los tres flujos UI del slice 012 — (a) propietario califica cita completada con 1-5 estrellas y comentario; (b) visitante ve promedio, distribución y reseñas en el perfil público de sucursal; (c) staff/clínico responde una reseña de su sucursal — con Playwright, cubriendo estados UX, permisos visibles, IDOR/BOLA UI, responsive y accesibilidad.
## Alcance
| Caso | Vista | Rol | Esperado |
| --- | --- | --- | --- |
| C1 formulario de calificación | `/portal/owner/appointments/[id]` (sección Calificar) | propietario | Estrellas 1-5, textarea comentario (máx 2048), botón "Calificar cita" |
| C2 validación inline | formulario | propietario | Error si `rating` vacío; si `comment > 2048` caracteres; si cita no está `COMPLETED` → banner 422 |
| C3 crear OK | formulario → success | propietario | Toast de éxito; sección "Calificar" sustituida por "Usted calificó esta cita: ⭐⭐⭐⭐⭐" |
| C4 cita pendiente | formulario | propietario | Estado disabled con motivo "La cita no está completada"; 422 superficialado si se fuerza |
| C5 repetición | formulario | propietario | Estado "ya califiqué esta cita" sin botón (409 superficialado) |
| C6 perfil público sin reseñas | `/clinics/[branchId]` (sección Reseñas) | anónimo | Tarjeta de promedio (— / 0 reseñas) + CTA "No hay reseñas aún"; estados empty |
| C7 perfil público con reseñas | `/clinics/[branchId]` | anónimo | Promedio (ej 4.3), distribución 5/4/3/2/1, listado paginado (page/size), respuesta clínica visible si existe, estados loading/success/empty |
| C8 respuesta desde portal clínico | `/clinic/reviews/[reviewId]/respond` | staff | Formulario respuesta (máx 2048), botón "Responder"; toast de éxito; banner "respondida" |
| C9 respuesta duplicada | `/clinic/reviews/[reviewId]/respond` | staff | Estado "ya respondida" (409 superficialado) |
| C10 staff de otra sucursal | `/clinic/reviews/[reviewId]/respond` | staff sucursal B | Banner 404 consistente "no puede responder una reseña de otra sucursal" |
| C11 propietario no responde | `/clinic/reviews/[reviewId]/respond` | propietario | Banner 403 "solo personal de la sucursal puede responder" |
| C12 IDOR: listado propietario A | — | propietario A | No ve detalle de reseña de cita de propietario B (`404` legible) |
| C13 responsive | formularios, listado, respuesta | todos | Usable en desktop (≥1024px) y mobile (≤640px) sin overflow |
| C14 acentos y eñes | todas las vistas | todos | Acentos, `ñ`, comillas tipográficas correctas (no mojibake `Ã`) |
| C15 accesibilidad | formulario de calificación | propietario | `label` asociada a input; `aria-live` para toast; foco visible; contraste AA |
| C16 sin token | formulario | sin sesión | Redirección a `/login` manteniendo `returnUrl` |
## Suite y archivos
- `frontend/playwright/tests/reviews/rating-form-happy.spec.ts` — C1, C3, C7.
- `frontend/playwright/tests/reviews/rating-form-states.spec.ts` — C2, C4, C5, C13.
- `frontend/playwright/tests/reviews/public-profile.spec.ts` — C6, C7.
- `frontend/playwright/tests/reviews/responsive.spec.ts` — C13, C14.
- `frontend/playwright/tests/reviews/access-a11y.spec.ts` — C15, C16.
- `frontend/playwright/tests/reviews/clinic-response.spec.ts` — C8, C9.
- `frontend/playwright/tests/reviews/clinic-response-access.spec.ts` — C10, C11, C12.
- `frontend/playwright/tests/reviews/access-no-auth.spec.ts` — C16.
## Ejecución
```powershell
docker compose up -d --build --force-recreate db backend frontend
cd frontend
$env:PLAYWRIGHT_START_FRONTEND="false"
npx playwright test fe-012-reviews --retries=0 --reporter=line
npx playwright test --project=chromium --retries=0 --reporter=line
npx tsc --noEmit
npx jest
```
Ejecutar Playwright contra el frontend publicado por Docker (no contra `next dev` del host).
## Criterios de aceptación
- Casos C1..C16 en `PASS`.
- Estados UX (`loading`, `submitting`, `empty`, `success`, `error`) observables en cada componente del slice.
- Sin links `#` en flujos implementados del slice.
- Sin `console.log` de datos sensibles (comment, respuesta, token).
- Responsive verificable en ambos breakpoints con sin overflow.
- Sin regresión de UIA-011 (regresión e2e de todo el repo).
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
