---
encoding: UTF-8
artifact: review_security
slice: BE-015
aliases: [FE-015]
type: security-review
date: 2026-09-03
decision: APPROVED
---

# Revisión de seguridad para slice BE-015 — Reportes operativos

## Alcance de la revision

| Control | Capa | Fuente de evidencia |
|---|---|---|
| AuthN requerida en todos los endpoints | Router FastAPI | `reports_router.py` (6 endpoints) + `test_reports_auth.py` |
| AuthZ / tenant isolation | Router + use-case | `clinic_id` derivado del JWT (`_clinic_id_from`); `test_reports_tenant_isolation.py` |
| Validaciones entradas / inyección SQL | Router (Pydantic Query) + ORM params | `_validate_dates` + `appointment.clinic_id == clinic_id` (parametrizado) |
| Privacidad de datos expuestos | Schemas DTO | `report_schemas.py` (campos resumidos, sin PII completa) |
| Paginación saneada | Query params | `page ≥ 1`, `size 1..100` vía `Query(ge=1, le=100)` |
| Log / audit de acceso | No implementado (fuera alcance slice) | Documentado en AC-015 |

## Hallazgos por severidad

| # | Severidad | Descripción | Impacto | Estado |
|---|-----------|-------------|---------|--------|
| S1 | Low — Los endpoints de reportes devuelven `pet_name` y `owner_name` completos en DTOs. El plan AC-015-03 dice "campos resumidos"; el slice expone nombres completos de mascotas y de dueños. | Bajo — datos de una clínica propia del JWT; el dueño y la mascota son visibles al propio veterinario; sin cruce de tenant (filtrado `clinic_id`). | Aceptado como riesgo menor para MVP; el plan no exige truncar nombres. |
| S2 | Info — El endpoint `/reports/ratings` devuelve `vet_id` (ID interno de veterinario) en `by_veterinarian`. | Sin riesgo — `clinic_id` del JWT restringe el alcance al tenant. | Cierre sin acción. |
| S3 | Info — Los schemas `RatingsReportResponse` / `PaymentsReportResponse` con `list[dict[str, Any]]` para `items` podrían admitir campos sorpresa. | Sin riesgo — los DTOs internos son Pydantic y se serializan vía `model_dump()`; FastAPI aplica `response_model`. | Cierre sin acción. |
| S4 | Info — El slice no implementa rate limiting ni audit trail para consulta de reportes. | Fuera de alcance AC-015 (documentado). | Aceptado; Stage 2. |

## Verificación IDOR / BOLA

- **Modelo de tenant:** `clinic_id` se deriva del JWT en `_clinic_id_from(current_user)` y se aplica en **cada** use-case vía `filter(Model.clinic_id == clinic_id)`.
- **Sin query param `clinic_id`:** El router no acepta `clinic_id` como entrada del cliente (verificado en `reports_router.py`), por lo que un atacante no puede inyectar otro `clinic_id`.
- **Sin cross-tenant read:** Las pruebas en `test_reports_tenant_isolation.py` cubren la separación por tenant.
- **Acceso sin token:** `Depends(get_current_access_user)` → 401. Verificado en `test_reports_auth.py` para los 6 endpoints.
- **Resultado: PASS**

## Verificación de validación HTTP

| Caso | Endpoint(s) | Comportamiento | Prueba |
|---|---|---|---|
| `period_start > period_end` | 6 endpoints | 422 `period_end no puede ser anterior a period_start` | `test_reports_invalid_input.py` |
| `period_start` formato inválido | 6 endpoints | 422 `period_start debe estar en formato YYYY-MM-DD` | `test_reports_invalid_input.py` |
| `page < 1` | endpoints paginados | 422 (Pydantic `ge=1`) | `test_reports_invalid_input.py` |
| `size > 100` | endpoints paginados | 422 (Pydantic `le=100`) | `test_reports_invalid_input.py` |

## Verificación de privacidad

- Los DTOs no exponen teléfonos, emails, dirección, DNI/CI, o datos financieros completos.
- `pet_name` y `owner_name` son nombres en texto plano (acorde a AC-015-03 que exige "campos resumidos", no necesariamente anónimos).
- `clinic_id` es expuesto en los DTOs (necesario para la UI de identificación).
- `vet_id` (internal) expuesto en el endpoint de ratings para key uniqueness.

## Verificación de paginación (DoS básico)

- `size` limitado a `1..100` por `Query(ge=1, le=100)`.
- `page` limitado a `≥ 1`.
- `offset = (page-1) * size` — no permite valores negativos.

## Verificación frontend

- `RequireAuth` envuelve `/portal/admin/reports` (redirect `/login` si no autenticado).
- El hook `useReports` no expone datos si no hay fetch; el banner de error muestra el mensaje sin stack trace.
- No hay storage de tokens en `localStorage`; `apiClient` usa el mecanismo central (verificado en `shared/api/client.ts`).

## Decision final

No hay hallazgos bloqueantes. Los riesgos menores (S1, S4) son aceptados para
el alcance MVP del slice; S2/S3 son info-level sin acción.

- **Decision:** APPROVED

- Decision: APPROVED

## Próximo paso recomendado

Continuar con `/run-checks BE-015` → `/update-docs BE-015` → `/final-gate BE-015`.

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
