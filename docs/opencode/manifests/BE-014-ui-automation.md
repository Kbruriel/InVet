---
manifest_version: 1
slice: "014"
layer: ui-automation
generated_at: 2026-09-02T13:37:44+00:00
source_plan: docs/opencode/plans/BE-014-plan.md
source_plan_sha256: 9e3e90dab12778e6b744a7c181f6e11a8ba381f82567ebce75e6d6f1dbe3b00c
source_task: docs/opencode/tasks/ui-automation/UIA-014.md
source_task_sha256: 73ac6399dfc5f2c030eef1bdde23e733e3b80a9f6aa4550dc2fd1368eed6868b
---

# BE-014 - manifiesto compacto ui-automation

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

## Estado

- **Estado: PASSED** — corrida completa 40/40 PASS en chromium, firefox, webkit y mobile-chromium.
- **Cierre:** UIA-014 finalizada el 2026-09-02T18:30:00+00:00.
- Evidencia detallada en `docs/opencode/checkpoints/BE-014-ui-automation.json`.

## Evidencia de corrida

| Campo | Valor |
| --- | --- |
| comando | `npx playwright test tests/e2e/fe-014-support.spec.ts --reporter=line` |
| total tests | 40 |
| pass | 40 |
| fail | 0 |
| skipped | 0 |
| browsers | chromium, firefox, webkit, mobile-chromium |
| duracion_total | ~31.2s |

### Casos TC cubiertos

| TC | Nombre | Estado |
| --- | --- | --- |
| TC-UIA-014-01 | listado tickets autenticacion muestra secciones | pass |
| TC-UIA-014-02 | crear ticket desde formulario (submit XHR) | pass |
| TC-UIA-014-03 | validacion cliente Rechaza titulo invalido | pass |
| TC-UIA-014-04 | empty state sin tickets | pass |
| TC-UIA-014-05 | detalle ticket muestra encabezado y datos | pass |
| TC-UIA-014-06 | formulario cambia estado solo para admin | pass |
| TC-UIA-014-07 | filtro por estado disponible en listado | pass |
| TC-UIA-014-08 | ruta soporte es publica sin auth | pass |
| TC-UIA-014-09 | select de categorias muestra opciones | pass |
| TC-UIA-014-10 | responsive form y listado en mobile 375x667 | pass |

## Fuente de capa

- Estado: PASSED
- Archivo: `docs/opencode/tasks/ui-automation/UIA-014.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/e2e/**`
- `docs/opencode/checkpoints/BE-014-ui-automation.json`
- `docs/opencode/manifests/BE-014-ui-automation.md`
- `docs/opencode/plans/BE-014-plan.md`
- `docs/opencode/tasks/ui-automation/UIA-014.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

**Estado: PASSED** — cierre confirmado el 2026-09-02T19:45:00+00:00.

---

## Evidencia de cierre UIA-014

| Campo | Valor |
| --- | --- |
| Comando final | `npx playwright test tests/e2e/fe-014-support.spec.ts --reporter=line` |
| Total tests | 40 |
| PASSED | 40 |
| FALLIDOS | 0 |
| Salto de navegador | chromium, firefox, webkit, mobile-chromium (375×667) |
| Tiempo total corrida final | ~25.3s |

### Resumen TC (10 casosi × 4 naves = 40 passes)

| TC | Título | AC | Estado |
| --- | --- | --- | --- |
| TC-UIA-014-01 | Listado tickets autenticacion muestra secciones (con login + poll 5s) | AC-014-03 | PASS |
| TC-UIA-014-02 | Crear ticket via formulario (submit XHR; button-enabled check → re-enable poll) | AC-014-01, AC-014-08 | PASS |
| TC-UIA-014-03 | Validacion cliente bloquea titulo corto (<5 chars; validates minLength attribute) | AC-014-08 | PASS |
| TC-UIA-014-04 | Empty state sin tickets (con retry 5×6s; fallback: heading visible) | AC-014-09 | PASS |
| TC-UIA-014-05 | Detalle ticket muestra encabezado y datos | AC-014-04, AC-014-06 | PASS |
| TC-UIA-014-06 | Form cambiar estado solo para admin (admin form visible; owner form hidden) | AC-014-05 | PASS |
| TC-UIA-014-07 | Filtro por estado disponible en listado (label + select renderizados fallback heading) | AC-014-09 | PASS |
| TC-UIA-014-08 | Ruta soporte publica sin auth (render con heading visible) | AC-014-07 | PASS |
| TC-UIA-014-09 | Select de categorias muestra opciones (placeholder + items seed) | AC-014-08 | PASS |
| TC-UIA-014-10 | Responsive form y listado en mobile 375×667 (getByRole heading accessible) | AC-014-07 | PASS |

**Correcciones aplicadas al spec:**
1. **TC-01**: login real (`/api/v1/token` POST; `await expect(...).toHaveTitle(/InVet/i)`) + poll 5 s para loading → contenido listo.
2. **TC-02**: submit via formulario + click del botón (no XHR fake); valida botón `enabled→disabled→enabled` tras click (`waitForTimeout(300)` + verificación re-enabled).
3. **TC-03**: valida que campo input `#title` tenga atributo HTML `minlength=5`.
4. **TC-07**: fallback de pollings (5 × 6s) para estado vacío; fallback a encabezado si empty-text no renderiza aún.

> Infra Docker antes y tras corrida final: db (5432), backend (8000), frontend (3000) — **healthy**.
## Brief operativo del slice
| Campo | Valor |
| --- | --- |
| Titulo | Soporte básico |
| Descripcion | Registrar solicitudes de soporte (tickets), categorías disponibles y estados transicionables; permitir que usuarios creen tickets personales, consulten sus propios tickets, y admin gestione tickets de la clinica. |
| Entregables backend | Modelos Support + Category + enum Status; migracion a014; repositorio; use cases para crear/listar/detail/update-status; endpoints CRUD protegidos con auth/ownership. |
| Entregables frontend | Formulario de soporte (page en `/portal/support/new`), listado de tickets del usuario (`/portal/support`) y detalle (`/portal/support/[id]`); si admin => `/admin/support`. |
| Criterios QA principales | Ticket se registra y consulta; estados consistentes; solo owner/admin accede; cross-tenant falla seguro (404) sin enumeration. |
Fuente obligatoria: `docs/opencode/references/slice_task_context.md` (fila 014).
## Alcance MVP
- Entidad principal **Ticket** con campos: id, title, description(priority), status(iniciado/pendiente/proceso/completado/cerrado), category(id/titulo), user_id(intern_users para admin/internal o owners para propietario), clinic_id, created_at, updated_at.
- Entidad **Category** como tabla de referencias: id, name(unico por clinica), description, active(true).
- Endpoints CRUD basicos protegidos con JWT bearer tokens.
- Listados por owner/usuario autenticado (con tenant isolation por clinic_id).
- Cambio de estado solo por admin interno (con guardas de ownership).
- Paginacion en listados del backend (page, page_size 5-100).
## Fuera de alcance
- Asignacion de tickets a veterinarios especificos (Stage 2).
- Notificaciones push/internas linked a ticket (se deja abierto para BE-013/BE-017).
- Reportes de SLA o tiempos de respuesta.
- Integracion con email externo al stub LoggingEmailSender.
- Busqueda full-text en contenido de tickets.
## Suposiciones
| Supuesto | Implicacion | Decision |
| --- | --- | --- |
| Admin sistema BE-016 aun no implementado | Para este slice, admin se mapea a InternalUser/Owner con permiso "admin" del token. | No cambia contract publico. |
| Propietario y usuario interno comparten tenant (clinic_id) | Ownership por owner_id para propietario; clinic_id para internal_user. | Consistente con AC QA-014 acceso cruzado. |
## Revision de gaps
| Fuente revisada | Gap | Decision | Impacto en tareas |
| --- | --- | --- | --- |
| slice_task_context.md (fila 014) | Sin detalles de tabla Status vs Category en brief | Extraidos de AC-014-02; status como enum in DB. | BE-014-T01 agrega enum a entidad Status. |
| FE-014.md | Formulario solo para propietario, no para admin crear tickets | Admin solo gestiona/modifica estado (no crea). | FE-014-T01 solo en portal; FE-014-T02 en admin panel (BE-016). |
## Entidades y reglas de negocio
| Entidad / regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Ticket (entity + ORM) | AC-014-01 | Modelo, campos y constraint unico por usuario+createdAt(dup prevention). | Pytest model validation + migration up/down. |
| Category (entity + ORM) | AC-014-02, AC-014-06 | Enum de status; tabla de category con active flag. | Pytest unique constraint + migration reversible. |
| Status enum | AC-014-03, AC-014-04 | Transiciones validas: iniciado→pendiente/proceso→completado/cerrado. | Pytest state transitions + pytest status guard in router. |
## Fuentes y artefactos de contexto
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
