---
manifest_version: 1
slice: "015"
layer: api-automation
generated_at: 2026-09-07T23:29:16+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: 2e65b3a8c877e97da8639d617e56613f701fa37ee145127a0da81ace38c52823
source_task: docs/opencode/tasks/api-automation/APIA-015.md
source_task_sha256: b267be8b719fe3981cb721c2280070e975a7ce664d400af2f817f0c879a0a650
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
## Evidencia ejecutada (APIA-015)
| Caso | Estado evidencia | Comando |
| --- | --- | --- |
| APIA-C1, C2, C3, C4, C5, C6 | passed (200 + contratos) | `npm run test:api -- --grep "APIA-015"` |
| APIA-C7 (422 date/bounds) | passed (422) | `npm run test:api -- --grep "APIA-015"` |
| APIA-C8 (401 no/bad token) | passed (401) | `npm run test:api -- --grep "APIA-015"` |
| APIA-C9 (405/404 metodo/ruta) | passed (405/404) | `npm run test:api -- --grep "APIA-015"` |
| AUTH-C1 (tenant valido) | passed | `npm run test:api -- --grep "APIA-015"` |
| AUTH-C2 (tenant ajeno) | passed (solo datos propio tenant) | `npm run test:api -- --grep "APIA-015"` |
| BOLA-C1, C2 | passed (tenant isolation por JWT clinic_id) | `npm run test:api -- --grep "APIA-015"` |
| LEAK (sin stack/ORM/DB expuesto) | passed | `npm run test:api -- --grep "APIA-015"` |
Resumen corrida APIA-015: 13/13 passed (2.6s) en `InVet_UI_Automation/tests/api/apia-015-reports.spec.ts` contra el backend Docker. En `npm run test:api` completo: 134 passed / 46 failed — los 46 fallos pertenecen a specs de OTROS slices (BE-006/008/009/012/003) con expectativas contractuales desactualizadas vs el backend actual; fuera del alcance de APIA-015 y fuera de su allowlist (no se corrigen en esta fase).
## Contrato real observado (APIA-015)
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
