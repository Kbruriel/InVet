---
slice: "APIA-016"
title: API Automation para Administracion inicial del sistema
status: PLANNING
encoding: UTF-8
---

# APIA-016 — API Automation para Administracion inicial del sistema

## Alcance de la automatizacion HTTP/API

Este artefacto cubre pruebas directas sobre los contratos HTTP del slice 016 (administracion). No incluye navegacion UI (eso es `UIA-016`). Todas las pruebas se ejecutan via `httpx` / `requests` contra el backend corriendo en contenedor Docker con PostgreSQL real.

## Casos automatizados previstos

### Endpoint: /api/v1/admin/internal-users

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C01 | GET | `/api/v1/admin/internal-users?page=1&size=10` | bearer system_admin | 200; paginated | - |
| APIA-016-C02 | GET | `/api/v1/admin/internal-users?page=1&size=10` | bearer normal user | 403 | authz, no-listado global |
| APIA-016-C03 | GET | `/api/v1/admin/internal-users` | none (sin token) | 401 | authn missing |

### Endpoint: /api/v1/admin/internal-users/{user_id}

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C04 | GET | `/api/v1/admin/internal-users/999` | bearer system_admin | 404 (no existe user 999) | not-found behavior |
| APIA-016-C05 | PUT | `/api/v1/admin/internal-users/{user_id}` with JSON {email,role,name} | bearer system_admin | 200; fields updated | IDOR check: owner clinic match |
| APIA-016-C06 | PATCH | `/api/v1/admin/internal-users/{id}/deactivate` | bearer system_admin admin (not global) | 403 for non-admin global user | authz guard de rol |

### Endpoint: /api/v1/admin/clinics

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C07 | GET | `/api/v1/admin/clinics?page=1` | bearer system_admin | 200; paginated JSON. All clinics visible. | tenant isolation: global scope |
| APIA-016-C08 | POST | `/api/v1/admin/clinics` with JSON {name:"TestClinic", address:"Calle"} | bearer system_admin | 201; new clinic returned in response body. | input validation + DB persistence |
| APIA-016-C09 | POST | `/api/v1/admin/clinics` with empty JSON {} | bearer system_admin | 422 (missing required fields) | input validation |

### Endpoint: /api/v1/terms

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C10 | GET | `/api/v1/terms` | none (public) | 200; JSON with content (or null body if not yet set). | public read access. |
| APIA-016-C11 | PUT | `/api/v1/terms` with JSON {content: "..."} | bearer system_admin | 200; content persisted + published_at updated. | update guard. |
| APIA-016-C12 | PUT | `/api/v1/terms` with JSON {content: "..."} | bearer normal user (NOT admin) | 403 Forbidden (not authorized for terms update). | authz: only admin can modify. |

### Endpoint: /api/v1/privacy

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C13 | GET | `/api/v1/privacy` | none (public) | 200; JSON with content or null body. | public read access. |
| APIA-016-C14 | PUT | `/api/v1/privacy` with JSON {content: "..."} | bearer system_admin | 200; privacy policy persisted and accessible. | update guard on privacy endpoint. |

### Endpoint: /api/v1/admin/reports/tipo

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C15 | GET | `/api/v1/admin/reports/appointments?period_start=2024-01-01&period_end=2024-12-31` | bearer system_admin | 200; aggregated data across all clinics (not scoped to one clinic). | global aggregation: no tenant leakage |
| APIA-016-C16 | GET | `/api/v1/admin/reports/appointments?period_start=2024-13-01&period_end=2024-12-31` | bearer system_admin | 400 (invalid period: month > 12). | input validation |

### Endpoint: /api/v1/admin/support-tickets

| Caso | Metodo | Ruta/Params | Auth | Status esperado | Riesgo cubierto |
| --- | --- | --- | --- | --- | --- |
| APIA-016-C17 | GET | `/api/v1/admin/support-tickets?page=1&size=20` | bearer system_admin | 200; paginated list of tickets from all clinics. | global scope visibility |
| APIA-016-C18 | PUT | `/api/v1/admin/support-tickets/{ticket_id}` JSON {status: "resolved"} | bearer admin (assigned) | 200; ticket status updated. | state transition |
| APIA-016-C19 | PUT | `/api/v1/admin/support-tickets/{ticket_id}` JSON {status: "resolved"} | bearer admin (NOT assigned to that ticket's clinic) | 403 (not assigned, no cross-clinic access). | IDOR/BOLA isolation |

## Cobertura HTTP prevista

| Cobia | Detailado | Casos que cubre |
| --- | --- | --- |
| authn | Token bearer present/absent/expired/invalid. | C03/C12 all use cases need to test that authentication works properly. |
| authz | Role-based: system_admin vs regular admin vs owner/user tokens. | C02/C06/C09/C12; only system_admin can access global endpoints. |
| payloads | Validate request/response shapes for every endpoint (schemas from BE-016 schema). | All cases verify against Pydantic schemas. |
| errors | 400 for input validation; 401 for authn failure; 403 for authz; 404 for not-found; 422 for schema mismatch. | Every endpoint returns standardized JSON error response with detail. |
| pagination | page/page_size limits returned items correctly; total matches expected count across pages. | GET endpoints (C01/C07/C15/C17). |
| IDOR/BOLA | User of clinic A cannot access resources owned by clinic B or global admin scope without system_admin role. | C06/C09/C12/C19; key isolation test. |

## Exposicion de datos y seguridad

- **No data leakage**: response DTOs for users/clinics do not include raw passwords, hashed fields, or PII that exceeds what's necessary.
- **IDOR/BOLA mitigation**: every admin endpoint uses JWT-derived user info + explicit role guard; no clinic_id as a request parameter can expand access scope. The `clinic_admin` existing pattern is used for scoped endpoints, while global endpoints (`/api/v1/admin/*`) require `system_admin`.
- **Input validation**: All JSON bodies validated with Pydantic schemas before reaching use-cases. Invalid data returns 400 or 422 (no SQL errors leaked).

## Evidencia pendiente

Todos los casos quedan pendientes antes de ejecucion posterior. Tras ejecutar con el contenedor backend levantar:

```bash
pytest app/tests/integration/test_admin_api_a16.py -q --timeout=120
```

| Caso | Estado evidencia | Ruta evidencia (path en filesystem) |
| --- | --- | --- |
| C01-C19 | Pendiente ejecutar | `docs/opencode/qa/APIA-016-results.md` |

## Casos no automatizados en este slice

| Caso | Motivo exclusion manual o fuera de scope |
| --- | --- |
| Actualizacion estado terminos via UI (no HTTP) - Cubierto por UIA, no API. | Automatizacion visual (ver UIA-016-C05/C06), no requiere testing HTTP directo. |
| Performance/load testing de reportes globales bajo alta carga de datos cross-clinic. | Requiere benchmarking dedicado; fuera del alcance MVP/automasacion API baseline. |
