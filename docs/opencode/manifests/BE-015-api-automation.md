---
manifest_version: 1
slice: "015"
layer: api-automation
generated_at: 2026-09-02T21:43:43+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: f2d8b7e3c7dbba5f0b9967c5a8e6998a36b593d1fda23b958ce78eda940cff6b
source_task: docs/opencode/tasks/api-automation/APIA-015.md
source_task_sha256: a93a9454b7417b5166760427dc9cd9cef1544938685b195dc027e296e9dcb12a
---

# BE-015 - manifiesto compacto api-automation

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
- Archivo: `docs/opencode/tasks/api-automation/APIA-015.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/api/**`
- `docs/opencode/checkpoints/BE-015-api-automation.json`
- `docs/opencode/manifests/BE-015-api-automation.md`
- `docs/opencode/plans/BE-015-plan.md`
- `docs/opencode/tasks/api-automation/APIA-015.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Proposito
Ejecutar pruebas automatizadas contra endpoints del backend (Docker container `backend` con PostgreSQL `db`) para verificar contratos, estados HTTP, seguridad y validaciones de todos los criterios AC del slice 015.
## Endpoints esperados bajo `/api/v1`
| Endpoint | Metodo | Descripcion |
| --- | --- | --- |
| `/api/v1/reports/appointments` | GET | Reporte agregado de citas por periodo |
| `/api/v1/reports/services` | GET | Reporte agregado de servicios realizados por periodo |
| `/api/v1/reports/pets` | GET | Conteo de mascotas activas por clinica |
| `/api/v1/reports/consultations` | GET | Reporte agregado de consultas medicas por periodo |
| `/api/v1/reports/ratings` | GET | Resumen de calificaciones promedios por veterinario |
| `/api/v1/reports/payments` | GET | Reporte agregado de pagos operativos por periodo |
## Cobertura HTTP
| Caso | Cubre criterio(s) | Endpoint | Accion esperada | Estado HTTP |
| --- | --- | --- | --- | --- |
| APIA-C1 | AC-015-01, AC-015-02 | GET `/api/v1/reports/appointments` con period_start y period_end validos | Recibir 200 con estructura paginada | 200 + `paginate.total > 0` |
| APIA-C2 | AC-015-03 | GET `/api/v1/reports/services?page=1&page_size=20` | Recibir <= 20 items en list | 200 + len(items) <= 20 |
| APIA-C3 | AC-015-04 | GET `/api/v1/pets` con filtro clinica válida | Recibir conteo correctos | 200 |
| APIA-C4 | AC-015-05 | GET `/api/v1/reports/consultations?page_size=50&period_start=YYYY-MM-DD` | Recibir datos resumidos | 200 |
| APIA-C5 | AC-015-06 | GET `/api/v1/reports/ratings?clinic_id=X` | Verificar promedio calculado | 200 |
| APIA-C6 | AC-015-07 | GET `/api/v1/reports/payments?period_start=YYYY-MM-DD&period_end=YYYY-MM-DD` | Recibir totales correctos | 200 |
| APIA-C7 | AC-015-08 | GET `/api/v1/reports/invalid_type` | Recibir 422, mensaje claro | 422 |
| APIA-C8 | AC-015-09 | GET sin Bearer token a cualquiera de los endpoints | Recibir 401 | 401 |
| APIA-C9 | AC-015-10 | POST a endpoints solamente GET | Recibir 405 o 404 | 405/404 |
## Pruebas de autenticacion y autorización
| Caso | Endpoint | Condicion | Esperado |
| --- | --- | --- | --- |
| AUTH-C1 | Todos los endpoints | Token valido de admin mismo clinica | 200 - data visible |
| AUTH-C2 | Todos los endpoints | Token valido de clinica B (no autorizada) | 403 o 404 seguro |
| AUTH-C3 | Todos los endpoints | Token expirado/invalido | 401 |
| AUTH-C4 | Todos los endpoints | Sin token | 401 |
## Pruebas de IDOR/BOLA
| Caso | Endpoint | Condicion | Esperado |
| --- | --- | --- | --- |
| BOLA-C1 | GET por periodo sin clinic_id | Usuario admin propia clinica solo ve sus datos | 200 - solo datos propio tenant |
| BOLA-C2 | GET con filtro clinic_id ajeno | Intentar acceder datos de clinica Diferente | 403 o sin datos filtrados |
## Evidencia pendiente
| Caso | Estado evidencia | Comandos |
| --- | --- | --- |
| APIA-C1-APIA-C9 | pending | `python -m pytest backend/tests/integration/test_reports_api.py -v --timeout=60` |
| AUTH-C1-AUTH-C4 | pending | Mismo archivo de prueba con parametrizaciones auth |
| BOLA-C1-BOLA-C2 | pending | Mismo archivo de prueba con multi-tenant fixtures |
## Riesgos IDOR/BOLA identificados
- `GET /api/v1/reports/{type}` debe validar que el usuario solo ve datos de su propia clinica/tenant.
- El filtro opcional `clinic_id` en request body no debe usarse como fuente de verdad de autoridad — debe derivarse del token JWT (sub + clinic_id).
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
