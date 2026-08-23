# APIA-010 — Automatizacion contractual de prescripciones

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
