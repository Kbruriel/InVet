# BE-014 - Revisión funcional del slice de soporte

**Slice:** BE-014 / FE-014 / QA-014  
**Fecha:** 2026-09-01  
**Revisor:** InVet Slice Reviewer  

---

## Resumen ejecutivo

El slice BE-014 (tickets de soporte básico) presenta una implementación coherente y completa que cubre todas las capas involucradas: backend API + casos de uso + repositorio, migración alembic con seed idempotente, frontend Next.js con rutas `/support` y `[ticketId]`, clientes API tipados y pruebas automatizadas. La validación del plan (`validate_slice_plan.py --stage review`) devuelve `PASS`, el QA-014 está `APPROVED`/`RESOLVED` sin hallazgos abiertos, y las 55+ pruebas backend, 7 suites + 23 pruebas frontend están reportadas como aprobadas.

## Hallazgos por severidad

| # | Severidad | Descripción | Estado |
|---|-----------|-------------|--------|
| F1 | **Minor** — `status` del modelo tiene `nullable=True` mientras el AC indica `iniciado` como valor por defecto y migration usa `server_default`. Se evita inconsistencia porque el repositorio (`SupportTicket` → create) setea explícitamente `status = "iniciado"` en la entidad antes de insertar. | Aceptado |
| F2 | **Minor** — `description` del modelo tiene `nullable=True` aunque la migración también lo marca nullable. El AC-014 admite descripción opcional; se valida longitud máxima (≤ 2000) en el caso de uso. | Aceptado |
| F3 | **Minor** — `TicketStatus` enum define valores como `"proceso"` pero la UI usa etiquetas `"En proceso"`. El mapeo está en componentes (`ticket-status-updater.tsx`) y no se expone raw enum al HTTP; sin riesgo de ruptura. | Aceptado |

No se identificaron hallazgos **High** ni **Critical**.

## Archivos afectados por el slice

| Archivo | Capa | Propósito |
|---------|------|-----------|
| `backend/app/api/v1/routers/support_ticket_router.py` | BE | Endpoints protegidos |
| `backend/app/application/support_ticket_use_cases.py` | BE | Máquina de estados `_TRANSITIONS` |
| `backend/app/data/support_ticket_repo.py` | BE | Repositorio con aislamiento IDOR/BOLA |
| `backend/app/api/schemas/support_ticket_schemas.py` | BE | DTOs y serialización |
| `backend/app/infrastructure/database/models/support_ticket_model.py` | BE | ORM models + enum de estados |
| `backend/alembic/versions/a014_support.py` | BE | Migración con seed (AC-014-02) |
| `backend/app/tests/api/test_support_ticket_api.py` | QA-API | 13 criterios C1-C13 |
| `backend/app/tests/data/test_support_ticket_repo.py` | QA-repo | Aislamiento por clínica/owner |
| `backend/app/tests/usecases/test_support_ticket_rules.py` | QA-UC | Deduplicación, transiciones |
| `frontend/src/shared/api/support.ts` | FE | Client API tipado |
| `frontend/src/app/support/page.tsx` | FE | Lista y creación |
| `frontend/src/app/support/[ticketId]/page.tsx` | FE | Detalle autorizado |
| `frontend/src/features/support/ui/ticket-form.tsx` | FE | Formulario |
| `frontend/src/features/support/ui/ticket-list.tsx` / `ticket-list-filtered.tsx` | FE | Listado y filtro de estados |
| `frontend/src/app/support/[ticketId]/ticket-status-updater.tsx` | FE | Cambio de estado con transiciones válidas |
| Frontend tests: `*.test.tsx` (6 archivos, 23 pruebas) | FE-Automation | Estados UX cubiertos |

## Correcciones requeridas

No se requieren correcciones bloqueantes. Los hallazgos menores (F1-F3) son aceptados porque los contratos y la capa de aplicación previenen inconsistencias en producción.

## Checklist de revisión

- [x] `validate_slice_plan.py BE-014 --stage review` → PASS  
- [x] Migración a/descendente verificada (`a014_support.py`); seed idempotente por `WHERE NOT EXISTS`; índices presentes  
- [x] Modelo ORM `SupportTicket` / `TicketCategory` alineado con migración (únicamente `uq_ticket_category_clinic`)  
- [x] Motor de transiciones `_TRANSITIONS` en use-cases: iniciado→[pendiente,proceso]; proceso→[completado,cerrado]  
- [x] Repositorio aplica `clinic_id` y `owner_id`; 404 para recursos ajenos (IDOR/BOLA cubierto por pruebas)  
- [x] Router protege con dependency de sesión; errores devuelven 401/403/409 según contrato  
- [x] Schemas tipan request/response (POST body, pagination limits 5–100, status enum validación)  
- [x] Frontend: rutas `/support` y `[ticketId]`, client `support.ts`, TicketForm valida título/descripción/categoría  
- [x] Frontend: `TicketStatusUpdater` solo renderiza transiciones permitidas; bloquea en `cerrado`  
- [x] Frontend: `TicketListFiltered` soporta filtro por estado con reinicio a `page=1`; paginación numérica  
- [x] Frontend tests (6 suites, 23 casos): cover load/empty/error/retry/ID inválido/404/transiciones  
- [x] QA-014 results: APPROVED, hallazgos únicos RESOLVED, sin bloqueantes abiertos  
- [x] No hay carryovers detectados (no se requiere referencia a `carryovers_governance.md`)  

## Decision final

El slice BE-014 cumple con todos los criterios de aceptación, el flujo de QA está cerrado (`APPROVED`), la migración y el seed son correctos, el aislamiento IDOR/BOLA probado, y los componentes frontend cubren estados de carga/empty/error/transiciones. No hay bloqueantes ni regresiones detectadas.

- Decision: APPROVED

---

## Siguiente paso recomendado

1. `/clean-architecture-review BE-014` — Revisión vertical de arquitectura del slice.
2. Si la arquitectura es `APPROVED`, continuar por: `/security-review BE-014` → `/run-ui-checks BE-014` → `/final-gate BE-014`.
