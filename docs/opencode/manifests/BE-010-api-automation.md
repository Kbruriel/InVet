---
manifest_version: 1
slice: "010"
layer: api-automation
generated_at: 2026-08-22T20:31:02+00:00
source_plan: docs/opencode/plans/BE-010-plan.md
source_plan_sha256: af794d2bbdf8683f4a31f941baae267569ca8d2fb817dcbfa6a27a487371887e
source_task: docs/opencode/tasks/api-automation/APIA-010.md
source_task_sha256: 6aaeda04ce0d2d86aaf05d3bb7d22686e02c97839938bb824f0ae518f00ff1ef
---

# BE-010 - manifiesto compacto api-automation

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
- Archivo: `docs/opencode/tasks/api-automation/APIA-010.md`

## Archivos permitidos

- `InVet_UI_Automation/tests/api/**`
- `docs/opencode/checkpoints/BE-010-api-automation.json`
- `docs/opencode/manifests/BE-010-api-automation.md`
- `docs/opencode/plans/BE-010-plan.md`
- `docs/opencode/tasks/api-automation/APIA-010.md`

## Tareas

- No hay tareas atomicas de esta capa en el plan canonico.
- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.
## Brief de capa

## Objetivo
Validar los contratos HTTP de prescripciones (creacion, detalle, listado) con pruebas contractualas HTTPX contra el backend Docker, cubriendo happy path, negative path y seguridad (401/403/404/409/422).
## Alcance
| Caso | Endpoint | Metodo | Token | Esperado |
| --- | --- | --- | --- | --- |
| C1 crear OK | POST `/api/v1/prescriptions` | Bearer veterinario | 201 + `PrescriptionRead` completo (items, tratamientos, recordatorios) |
| C2 consulta inexistente | POST `/api/v1/prescriptions` | Bearer veterinario | 422, sin registro parcial |
| C3 consulta no completed | POST `/api/v1/prescriptions` | Bearer veterinario | 422 |
| C4 duplicado por consulta | POST `/api/v1/prescriptions` dos veces | Bearer veterinario | la segunda 409 |
| C5 sin token | POST/GET `/api/v1/prescriptions*` | sin Bearer | 401 |
| C6 propietario crea | POST `/api/v1/prescriptions` | Bearer propietario | 403 |
| C7 veterinario ajeno lee | GET `/api/v1/prescriptions/{id}` | Bearer vet otra clinica | 404 o 403 consistente |
| C8 detalle OK | GET `/api/v1/prescriptions/{id}` | Bearer propietario | 200 secciones completas |
| C9 listado por mascota | GET `/api/v1/prescriptions?pet_id=` | Bearer propietario | 200 `{items, meta {page, page_size, total, pages}}` |
| C10 listado ajeno | GET `/api/v1/prescriptions?pet_id=otra` | Bearer propietario | 404/403 sin filtrar internas |
## Suite y archivos
- `backend/app/tests/api/test_prescriptions_create.py` — C1..C4, C5 (POST).
- `backend/app/tests/api/test_prescriptions_idor.py` — C6, C7, C10.
- `backend/app/tests/api/test_prescriptions_auth.py` — C5 (todos los endpoints).
- `backend/app/tests/api/test_prescriptions_read.py` — C8, C9.
## Ejecucion desde Docker
```
docker compose up -d db
docker compose run --rm backend pytest app/tests/api/test_prescriptions_create.py app/tests/api/test_prescriptions_idor.py app/tests/api/test_prescriptions_auth.py app/tests/api/test_prescriptions_read.py -q
```
## Criterios de aceptacion
- Todos los casos C1..C10 en `PASS`.
- Errores sin filtrado de stack traces ni informacion interna.
- Paginacion en listados con `meta` consistente.
- Sin regresion de APIA-009.
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
