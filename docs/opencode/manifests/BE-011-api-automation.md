---
manifest_version: 1
slice: "011"
layer: api-automation
generated_at: 2026-08-25T17:32:05+00:00
source_plan: docs/opencode/plans/BE-011-plan.md
source_plan_sha256: 91a3f6f70e23aa02c6a0037099a49513d1a5d802457596628d9e22a0ef287d3c
source_task: docs/opencode/tasks/api-automation/APIA-011.md
source_task_sha256: 1e060e3c88cda9462b5e92fb3dbeaf58ca3422267d34e4029c729e012d5a40c3
---

# BE-011 - manifiesto compacto api-automation

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
- Archivo: `docs/opencode/tasks/api-automation/APIA-011.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/api/**`
- `docs/opencode/checkpoints/BE-011-api-automation.json`
- `docs/opencode/manifests/BE-011-api-automation.md`
- `docs/opencode/plans/BE-011-plan.md`
- `docs/opencode/tasks/api-automation/APIA-011.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar los contratos HTTP de pagos (creacion, detalle, listado, cancelacion) con pruebas contractuales HTTPX contra el backend Docker, cubriendo happy path, negative path y seguridad (401/403/404/409/422).
## Alcance
| Caso | Endpoint | Metodo | Token | Esperado |
| --- | --- | --- | --- | --- |
| C1 crear OK | POST `/api/v1/payments` | Bearer staff | 201 + `PaymentRead` (`method`, `amount`, `amount_received`, `change_amount`, `status=PAID`) |
| C2 cita inexistente | POST `/api/v1/payments` | Bearer staff | 422, sin registro parcial |
| C3 servicio inactivo | POST `/api/v1/payments` | Bearer staff | 422 |
| C4 cambio invalido | POST `/api/v1/payments` `method=CASH` `amount_received < amount` | Bearer staff | 422 |
| C5 sin token | POST/GET/POST cancel `/api/v1/payments*` | sin Bearer | 401 |
| C6 propietario crea | POST `/api/v1/payments` | Bearer propietario | 403 |
| C7 clinico ajeno lee | GET `/api/v1/payments/{id}` | Bearer staff otra clinica | 404 o 403 consistente |
| C8 detalle OK | GET `/api/v1/payments/{id}` | Bearer staff | 200 `PaymentRead` completo |
| C9 listado paginado | GET `/api/v1/payments?status=PAID&page=1&page_size=20` | Bearer staff | 200 `{items, meta {page, page_size, total, pages}}` |
| C10 cancelar OK | POST `/api/v1/payments/{id}/cancel` | Bearer staff | 200 `status=CANCELLED`, `cancelled_at` poblado |
| C11 cancelar dos veces | POST `/api/v1/payments/{id}/cancel` dos veces | Bearer staff | la segunda 409 |
| C12 listado periodo | GET `/api/v1/payments?from=&to=&page=&page_size=` | Bearer staff | 200 solo pagos dentro del rango |
## Suite y archivos
- `backend/app/tests/api/test_payments_create.py` — C1..C4, C5 (POST), C6.
- `backend/app/tests/api/test_payments_read.py` — C8, C9, C12.
- `backend/app/tests/api/test_payments_cancel.py` — C10, C11.
- `backend/app/tests/api/test_payments_auth.py` — C5 (todos endpoints), C6, C7.
- `backend/app/tests/api/test_payments_idor.py` — C7, BOLA por tenant.
## Ejecucion desde Docker
```
docker compose up -d db
docker compose run --rm backend pytest app/tests/api/test_payments_create.py app/tests/api/test_payments_read.py app/tests/api/test_payments_cancel.py app/tests/api/test_payments_auth.py app/tests/api/test_payments_idor.py -q
```
## Criterios de aceptacion
- Todos los casos C1..C12 en `PASS`.
- Errores sin filtrado de stack traces ni informacion interna.
- Paginacion en listados con `meta` consistente.
- Sin regresion de APIA-010.
## Evidencia requerida
- Comandos ejecutados y codigo de salida.
- Resultados esperados vs obtenidos por caso.
- Defectos (si aplica) con pasos de reproduccion.
- Riesgo residual si aplica.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
