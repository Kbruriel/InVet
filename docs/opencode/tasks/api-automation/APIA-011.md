# APIA-011 — Automatizacion contractual de pagos operativos

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
