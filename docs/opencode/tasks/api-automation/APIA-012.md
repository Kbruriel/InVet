# APIA-012 — Automatización contractual de calificaciones, comentarios y respuesta clínica

## Objetivo

Validar los contratos HTTP `/api/v1/reviews*` — creación, listado público, detalle, respuesta clínica — con pruebas contractuales HTTPX contra el backend Docker, cubriendo happy path, negative path, permisos por rol, ownership/tenant/branch, IDOR/BOLA y estados `400/401/403/404/409/422/500`.

## Alcance

| Caso | Endpoint | Método | Token | Esperado |
| --- | --- | --- | --- | --- |
| C1 crear OK | `POST /api/v1/reviews` | Bearer propietario | 201 + `ReviewRead` (`rating∈[1..5]`, `comment`, `branch_id`, `clinic_id`, `appointment_id`) |
| C2 rating fuera de rango | `POST /api/v1/reviews` `rating=0` o `6` | Bearer propietario | 422 (Pydantic `ge=1, le=5`) |
| C3 cita sin completar | `POST /api/v1/reviews` cita `PENDING` | Bearer propietario | 422 con detalle legible |
| C4 repetición cita | `POST /api/v1/reviews` misma `appointment_id` dos veces | Bearer propietario | la segunda 409 |
| C5 cita ajena (BOLA) | `POST /api/v1/reviews` cita de otro tenant | Bearer propietario A | 404 consistente |
| C6 sin token | `POST /api/v1/reviews` | sin Bearer | 401 |
| C7 comment overflow | `POST /api/v1/reviews` `comment` 2049 caracteres | Bearer propietario | 422 con detalle legible |
| C8 detalle propio | `GET /api/v1/reviews/{id}` | Bearer propietario dueño | 200 `ReviewRead` |
| C9 detalle ajeno (IDOR) | `GET /api/v1/reviews/{id}` | Bearer propietario B (no dueño) | 404 consistente |
| C10 listado público | `GET /api/v1/reviews?branch_id={b}&page=1&page_size=20` | anónimo | 200 `{items, meta {page, page_size, total, pages}}` sin filtrado de tenant |
| C11 listado sucursal inexistente | `GET /api/v1/reviews?branch_id=999999` | anónimo | 404 |
| C12 resumen sucursal | `GET /api/v1/clinics/branches/{branch_id}` campo `rating_summary` | anónimo | 200 con `average_rating`, `total_reviews`, `review_distribution` |
| C13 respuesta OK | `POST /api/v1/reviews/{id}/respond` | Bearer staff sucursal | 200 con `response.body` y `responded_by` |
| C14 respuesta repetida | `POST /api/v1/reviews/{id}/respond` dos veces | Bearer staff | la segunda 409 |
| C15 propietario responde | `POST /api/v1/reviews/{id}/respond` | Bearer propietario | 403 |
| C16 staff sucursal ajena (BOLA) | `POST /api/v1/reviews/{id}/respond` | Bearer staff sucursal B | 404 (con la convención anti-enum de slice 004) |
| C17 sin token responde | `POST /api/v1/reviews/{id}/respond` | sin Bearer | 401 |
| C18 sin filtrado interno | todos los casos de error | — | detalle legible, sin stack trace, sin modelo ORM, sin nombre de base de datos |
| C19 resumen se actualiza | `POST /api/v1/reviews` (rating=5) → `GET /api/v1/clinics/branches/{branch_id}` | Bearer propietario → anónimo | `average_rating` y `total_reviews` coherentes post-creación |
| C20 validación body | `POST /api/v1/reviews` `{} vacío` | Bearer propietario | 422 con detalle por campo |

## Suite y archivos

- `backend/app/tests/api/test_reviews_create.py` — C1..C7, C20.
- `backend/app/tests/api/test_reviews_read.py` — C8, C9, C10, C11, C12.
- `backend/app/tests/api/test_reviews_respond.py` — C13..C17.
- `backend/app/tests/api/test_reviews_auth.py` — C6, C17 (401).
- `backend/app/tests/api/test_reviews_idor_bola.py` — C5, C9, C15, C16, C18.
- `backend/app/tests/application/test_review_service.py` — reglas de negocio (rating rango, cita COMPLETED, uniqueness, respuesta uniqueness, actualización de resumen).
- `backend/app/tests/data/test_review_repo.py` — persistencia, filtros, resumen agregado y actualización transaccional.

## Ejecución desde Docker

```powershell
docker compose up -d db
docker compose run --rm backend `
  pytest app/tests/api/test_reviews_create.py `
         app/tests/api/test_reviews_read.py `
         app/tests/api/test_reviews_respond.py `
         app/tests/api/test_reviews_auth.py `
         app/tests/api/test_reviews_idor_bola.py `
         app/tests/application/test_review_service.py `
         app/tests/data/test_review_repo.py -q
```

## Criterios de aceptación

- Casos C1..C20 en `PASS`.
- Errores consistentes (`400/401/403/404/409/422`) sin filtrar stack traces, ORM o nombre de base de datos.
- Paginación consistente: `items` + `meta {page, page_size, total, pages}`.
- Unicidad por cita y por respuesta garantizada (409).
- IDOR/BOLA: listado público no fuga tenant; detalle propio solo visible por dueño; respuesta clínica solo por staff de la sucursal.
- Sin regresión de APIA-011 (pagos).

## Evidencia requerida

- Comandos ejecutados y código de salida.
- Resultados esperados vs obtenidos por caso.
- Defectos (si aplica) con pasos de reproducción.
- Riesgo residual si aplica.

## Casos no automatizados

- Reseñas de sucursales con +1000 reseñas (no se simula el volumen; solo la paginación).
- Reseñas con adjuntos (fuera de alcance del MVP).
- Moderación avanzada por keyword (fuera de alcance del MVP).
