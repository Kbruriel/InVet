---
manifest_version: 1
slice: "013"
layer: api-automation
generated_at: 2026-08-31T23:55:16+00:00
source_plan: docs/opencode/plans/BE-013-plan.md
source_plan_sha256: 642c5f6278818acb924edc251bd441cb236522a3b33398f4d0b9908df3289a42
source_task: docs/opencode/tasks/api-automation/APIA-013.md
source_task_sha256: 3921cd391c08de6af0d19bde83c9778d7457e478e4d67b9830ab4b764964e6c3
---

# BE-013 - manifiesto compacto api-automation

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
- Archivo: `docs/opencode/tasks/api-automation/APIA-013.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/api/**`
- `docs/opencode/checkpoints/BE-013-api-automation.json`
- `docs/opencode/manifests/BE-013-api-automation.md`
- `docs/opencode/plans/BE-013-plan.md`
- `docs/opencode/tasks/api-automation/APIA-013.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar los contratos HTTP /api/v1/notifications* — listado paginado, conteo no leidas, marcacion individual, leer todas — con pruebas contractuales HTTPX contra el backend Docker, cubriendo happy path, negative path, permisos por rol, ownership/tenant/branch, IDOR/BOLA y estados 400/401/403/404/422/500.
## Alcance
| Caso | Endpoint | Metodo | Token | Esperado |
| --- | --- | --- | --- | --- |
| C1 list OK | `POST /api/v1/reviews` (appointment_created genero notificacion) | Bearer propietario dueño | 200 + NotificationRead con evento mapeado correctamente (evento APPOINTMENT_CREATED ref_type appointment ref_id cita_id) |
| C2 contenido vacío en tab | POST /api/v reenviado por stub email (solo log no error HTTP. | C3 lista paginada | `GET /api/v1/notifications?page=1&page_size=5` | Bearer propietario dueño | 200 `{items: [items count<=5], meta {page, page_size, total, pages}}` |
| C4 marcacion de error ID por token | `POST /api/v1/notifications/{id}/read` con id ajeno | Propietario A (no dueo) | 404 sin revelar existencia de notificacion de otro tenant |
| C5 marca OK | `POST /api/v1/notifications/{id}/read` | Bearer dueno | 200 `{status: success, is_read: true}` decrementa count unread |
| C6 read-all OK | `POST /api/v1/notifications/read-all` | Bearer dueno | 200 `{updated: n > 0}` todas marcadas leídas; tab filtrada vuelve vacía |
| C7 unread-count OK | `GET /api/v1/notifications/unread-count` | Bearer dueño | 200 `{count: n>0 o == 0}` decrements tras mark read individual |
| C8 dedup evento duplicado | Crear dos reseñas mismas cita (simula doble emision eventos) | Bearer propietario | Solo una notificacion existe; no error HTTP visible para caller del evento |
| C9 sin token list | `GET /api/v1/notifications` | Sin bearer | 401 consistente |
| C10 email stub loguea pero no envío real (no hay excepcion HTTP) | Post create review (evento APPOINTMENT_CREATED triggers notify + email send via stub) | Bearer propietario | No raise error; logging confirma que provee fue usado recipient/subject/provedor visibles en logs del test |
| C11 listado vacio | `GET /api/v1/notifications?page=1&page_size=20` sin datos previos | Bearer dueno | 200 con items [] y meta {page:1, page_size:20, total:0} |
| C12 invalid query params | `GET /api/v1/notifications?page=-1` o `page_size=300` | Bearer dueno | 422 detalle legible sin filtrar internals.
| C13 IDOR listing por clinica A | `GET /api/v1/notifications` con token de staff clinica B | Staff clinica B | 200 lista vacia (sin enumeracion ni counts que revelen datos ajenos) |
## Suite y archivos
- `backend/app/tests/api/test_notifications_list.py` — C1, C3, C9, C11.
- `backend/app/tests/api/test_notifications_mark_read.py` — C4, C5, C9.
- `backend/app/tests/api/test_notifications_read_all.py` — C6, C9.
- `backend/app/tests/api/test_notifications_unread_count.py` — C7, C9.
- `backend/app/tests/api/test_notifications_auth.py` — C2, C9 (401 en todos los endpoints).
- `backend/app/tests/api/test_notifications_idor_bola.py` — C4, C13 y mas IDOR/BOLA por tenant en los cinco endpoints.
- `backend/app/tests/application/test_notify_service.py` — reglas de negocio (dedup, stub email).
- `backend/app/tests/data/test_notification_repo.py` — persistencia, filtros, paginacion transaccional.
## Ejecución desde Docker
```powershell
docker compose up -d db
docker compose run --rm backend `
pytest app/tests/api/test_notifications_list.py `
app/tests/api/test_notifications_mark_read.py `
app/tests/api/test_notifications_read_all.py `
app/tests/api/test_notifications_unread_count.py `
app/tests/api/test_notifications_auth.py `
app/tests/api/test_notifications_idor_bola.py `
app/tests/application/test_notify_service.py `
app/tests/data/test_notification_repo.py -q
```
## Criterios de aceptación
- Casos C1..C13 en PASS.
- Errores consistentes (400/401/403/404/422) sin filtrar stack traces, ORM o nombre de base de datos.
- Paginacion consistente con meta {page, page_size, total, pages}.
- Unique por cita y por respuesta garantizada (dedup).
- IDOR/BOLA: listado publico no fuga tenant; detalle propio solo visible por dueño; marcacion solo por receptor.
- Sin regresion de APIA-012 (reviews).
## Evidencia requerida
- Comandos ejecutados y codigo de salida.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
