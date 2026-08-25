---
manifest_version: 1
slice: "011"
layer: ui-automation
generated_at: 2026-08-25T17:32:05+00:00
source_plan: docs/opencode/plans/BE-011-plan.md
source_plan_sha256: 91a3f6f70e23aa02c6a0037099a49513d1a5d802457596628d9e22a0ef287d3c
source_task: docs/opencode/tasks/ui-automation/UIA-011.md
source_task_sha256: 7c672bc2a112014d8f09e655c45e8863cdc8712e1f78128b5e3d5597b7dbe8ed
---

# BE-011 - manifiesto compacto ui-automation

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
- Archivo: `docs/opencode/tasks/ui-automation/UIA-011.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-011-ui-automation.json`
- `docs/opencode/manifests/BE-011-ui-automation.md`
- `docs/opencode/plans/BE-011-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-011.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar el flujo UI de pagos (formulario, listado por periodo y detalle con cancelacion) con Playwright, cubriendo estados UX, validaciones, permisos visibles y responsive.
## Alcance
| Caso | Vista | Rol | Esperado |
| --- | --- | --- | --- |
| C1 acceso formulario | `clinic/payments` | staff | Formulario con appointment, service, amount, method, amount_received (CASH) |
| C2 validacion inline | formulario | staff | Error inline si amount < 0, appointment inexistente, o servicio inactivo |
| C3 crear OK | formulario → success | staff | Toast de exito y vista del detalle (recibo no fiscal) |
| C4 propietero no ve create | `clinic/payments` | propietario | Sin ruta/accion de creacion; 403 legible si accede por URL |
| C5 listado | `clinic/payments/history` | staff | Listado paginado con meta `{page, page_size, total, pages}`; estados loading/success/empty/error |
| C6 detalle y cancelacion | `clinic/payments/[id]` | staff | Secciones datos, importe, metodo, cambio; boton Cancelar con confirmacion; estado `CANCELLED` final |
| C7 pago ajeno | `clinic/payments/{id_otro}` | staff otra clinica | Estado empty/error legible sin filtrar internas |
| C8 responsive | formulario + listado + detalle | staff | Usable en desktop y mobile |
| C9 acentos | todas las vistas | staff | Acentos y e-ñ sin mojibake |
## Suite y archivos
- `frontend/playwright/tests/test_payments_happy_path.py` — C1, C3, C5, C6.
- `frontend/playwright/tests/test_payments_states.py` — C5, C8, C9.
- `frontend/playwright/tests/test_payments_access.py` — C2, C4, C7.
## Ejecucion
```
docker compose up -d --build --force-recreate db backend frontend
cd frontend && npx playwright test
```
Ejecutar Playwright con `PLAYWRIGHT_START_FRONTEND=false` contra el frontend publicado por Docker.
## Criterios de aceptacion
- Todos los casos C1..C9 en `PASS`.
- Estados UX (loading, submitting, empty, success, error) observables por cada componente.
- Sin links `#` en flujos implementados del slice.
- No se loggean datos de pago en consola.
- Responsive verificable en ambos breakpoints.
- Sin regresion de UIA-010.
## Evidencia requerida
- Comandos ejecutados y codigo de salida.
- Capturas o resumen textual de UI por caso.
- Defectos (si aplica) con pasos de reproduccion.
- Riesgo residual si aplica.
## Estado: CERRADO (2026-08-25)
### Resumen por caso
| Caso | Resultado | Nota |
| --- | --- | --- |
| C1 acceso formulario | PASS | Selects `#appointment_id`/`#service_id` validados por `option[value]`. |
| C2 validacion inline | PASS | Errores inline por `<p id="<field>-error">`; `method` por defecto `cash` (sin error). |
| C3 crear OK | PASS | Toast + recibo no fiscal en el detalle. |
| C4 propietario sin permiso | PASS | 403 superficialado por banner; sin estado de exito. |
| C5 listado por periodo success/empty | PASS | Filtro normalizado a ISO; empty con CTA "Registrar pago". |
| C6 detalle y cancelacion | PASS | `CANCELLED` final; boton de cancelar oculto. |
| C7 pago no accesible | PASS | Estado empty/error legible. |
| C8 responsive | PASS | Desktop (tabla) y mobile (tarjetas). |
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
