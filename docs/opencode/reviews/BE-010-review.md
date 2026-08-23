---
encoding: UTF-8
artifact: review_findings
---

# Hallazgos de revisión de slice BE-010

## Resumen

- Slice: BE-010 — Recetas, tratamientos y recordatorios (prescriptions)
- Tipo de review: Revisión funcional (contrato BE/FE + seguridad + arquitectura + evidencia)
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado

- Backend:
  - `POST /api/v1/prescriptions` (201), `GET /api/v1/prescriptions/{id}` (200), `GET /api/v1/prescriptions?pet_id=&page=&page_size=` (listado 200 con `meta {page, page_size, size, total, pages}`).
  - Entidades de dominio (`Prescription`, `PrescriptionItem`, `PrescriptionTreatment`, `PrescriptionReminder` + `*Input` variants): `backend/app/domain/entities/prescription.py`.
  - Contrato de repositorio (interfaz): `backend/app/domain/repositories/prescription_repository.py`.
  - Implementación ORM con atomicidad: `backend/app/infrastructure/database/repositories/prescription_repository_impl.py`.
  - Migración Alembic `a010` con `UniqueConstraint("consultation_id")` e FKs: `backend/alembic/versions/a010_prescriptions.py` (referenciado por el ORM `backend/app/infrastructure/database/models/prescription.py`).
  - Casos de uso: `backend/app/application/use_cases/prescription_use_cases.py`.
  - Schemas Pydantic: `backend/app/api/schemas/prescription_schemas.py`.
  - Router: `backend/app/api/v1/routers/prescription_router.py`.
  - Pruebas: `backend/app/tests/test_prescription_use_cases.py`, `backend/app/tests/api/test_prescriptions_{create,read,idor,auth}.py`.
- Frontend:
  - Cliente API tipado: `frontend/src/shared/api/prescription.ts` (`createPrescription`, `getPrescription`, `listPrescriptions`).
  - Formulario clínico: `frontend/src/app/clinic/prescriptions/new/page.tsx`.
  - Historial por mascota: `frontend/src/app/portal/owner/pets/[petId]/prescriptions/page.tsx`.
  - Detalle read-only: `frontend/src/app/portal/owner/prescriptions/[id]/page.tsx`.
  - Pruebas unitarias: `frontend/src/shared/api/prescription.test.ts`.
- QA / QA-Automation:
  - `docs/opencode/qa/QA-010-results.md` (APPROVED) + `docs/opencode/qa/QA-010-findings.md` (Q010-001..Q010-004, todos RESOLVED).
  - Evidencia fresca de esta review: pytest 25 (use cases + API) + `tsc --noEmit` del frontend + UIA 18/18 (chromium + mobile-chromium) + APIA 10/10 (regresión FE).

## Resumen ejecutivo

La implementación es **completa, coherente y verde**. Los tres endpoints existen con contratos consistentes entre backend y frontend, la lógica de negocio vive en `application/use_cases` (los routers son adaptadores delgados con mapeo de excepciones de dominio a HTTP), el tenant isolation y el control de owner se aplican en los tres endpoints, y los cinco estados UX (loading, submitting, empty, success, error) están cubiertos en la UI.

La seguridad del flujo está alineada con el brief: `POST` restringido a roles clínicos (`_WRITE_ROLES` = `{veterinarian, clinic, staff, admin}`), 403 para propietario, 409 por duplicado por consulta, 404/403 en lectura de receta ajena, 401 sin token, y 422 si la cita no está `completed`.

Ningún defecto real (producto) fue encontrado en esta revisión. Los 4 findings de la sesión de QA (`Q010-001` mojibake en `PublicHeader`, `Q010-002` actor de prueba erróneo, `Q010-003` race de `LoadingSpinner`, `Q010-004` asunción 201 duro frente a 409) se corrigieron en la misma sesión y fueron revalidados por las suites verdaderas (UIA 18/18, pytest 25, APIA 10/10). El gate de revisión es **APPROVED**.

## Evidencia fresca de pruebas (ejecutada en esta revisión)

- Use-cases: `pytest app/tests/test_prescription_use_cases.py` → PASS.
- API (HTTPX): `pytest app/tests/api/test_prescriptions_{create,read,idor,auth}.py` → PASS.
- **Total fresco de esta revisión**: `docker compose run --rm backend pytest app/tests/test_prescription_use_cases.py app/tests/api/test_prescriptions_{create,read,idor,auth}.py -q` → **25 passed (1.11s)**.
- Frontend: `npx tsc --noEmit` (desde `frontend/`) → **sin errores**.
- UIA-010 (2 baselines, limpio y con residuos): **18/18 PASS** (chromium + mobile-chromium, 8.4s).
- APIA-010 (regresión FE): **10/10 PASS**.
- Plan cerrado: `python backend/scripts/validate_slice_plan.py BE-010 --stage review` → **[PASS] BE-010/FE-010/QA-010 stage=review**.
- QA Gate: `docs/opencode/qa/QA-010-results.md` → **APPROVED** (§8); `docs/opencode/qa/QA-010-findings.md` → Q010-001..Q010-004 **RESOLVED**.

## Hallazgos por severidad

### Blocker

- Ninguno.

### Critical

- Ninguno.

### Major

- **M1 (cierre en esta revisión) — QA-010-results.md §7/§3.4/§8 referencia "F1–F3" mientras el finding file usa "Q010-001..Q010-004".**
  `docs/opencode/qa/QA-010-results.md:81,123,134` citaba `F1`, `F1–F3` y `Findings F1–F3` contra 4 findings reales en `QA-010-findings.md` (`Q010-001..Q010-004`). Inconsistencia de trazabilidad QA.
  Corrección aplicada en esta revisión: reescribirse a `Q010-001` (referencia puntual en la tabla §3.4) y a `Q010-001..Q010-004` (en §7 Findings y §8 Gate). El texto "3 findings" se corrigió a "4 findings" para reflejar el total real.
  Evidencia post-fijación: `grep -H "F[123]\|Q010-" docs/opencode/qa/QA-010-results.md` → solo `Q010-001`, `Q010-001..Q010-004`. Sin "F1/F2/F3" restantes.

### Minor

- **m1 — Cobertura UI de proyectos firefox/webkit no disponible en este entorno (`spawn UNKNOWN`).**
  La cobertura E2E se ejercita sobre **chromium + mobile-chromium** (2 proyectos). Los asserts textuales/estados son agnósticos de motor, así que el riesgo es residual (no funcional). Documentado en `QA-010-results.md` §6 Riesgo residual y `QA-010-findings.md` (contexto).
  Recomendación: al habilitar firefox/webkit en el CI, re-lanzar `fe-010-prescription-*.spec.ts` sin cambios.

- **m2 — Ruta del formulario en el plan.**
  `BE-010-plan.md` (T02) referencia `frontend/src/app/clinic/appointments/[id]/prescription/page.tsx`, pero la implementación usa `frontend/src/app/clinic/prescriptions/new/page.tsx` como ruta de la vista nueva (más simple y alineado con `src/shared/api/prescription.ts` y el cliente). La ruta no cambia el comportamiento (mismo `createPrescription(...)`), así que es una desviación aceptada y verificable en `page.tsx` y en la UIA (C3 usa la ruta viva).
  Corrección: el plan ya se marca como `COMPLETED` con evidencia; la implementación es canónica.

- **m3 — `Prescription.treatments` usa `instructions` por defecto vacío (`instructions=""`).**
  En `schema` (`backend/app/api/schemas/prescription_schemas.py:41`) y en dominio (`PrescriptionTreatment.input` default `""`), es consistente con el contrato y la UI (`instructions` es opcional pero se serializa como cadena). Ningún problema.

## Archivos afectados

Backend (implementación viva):
- `backend/app/domain/entities/prescription.py`
- `backend/app/domain/repositories/prescription_repository.py`
- `backend/app/infrastructure/database/models/prescription.py`
- `backend/app/infrastructure/database/repositories/prescription_repository_impl.py`
- `backend/alembic/versions/a010_prescriptions.py`
- `backend/app/application/use_cases/prescription_use_cases.py`
- `backend/app/api/schemas/prescription_schemas.py`
- `backend/app/api/v1/routers/prescription_router.py`
- `backend/app/tests/test_prescription_use_cases.py`
- `backend/app/tests/api/test_prescriptions_{create,read,idor,auth}.py`

Frontend (implementación viva):
- `frontend/src/shared/api/prescription.ts`
- `frontend/src/shared/api/prescription.test.ts`
- `frontend/src/app/clinic/prescriptions/new/page.tsx` (formulario)
- `frontend/src/app/portal/owner/pets/[petId]/prescriptions/page.tsx` (historial)
- `frontend/src/app/portal/owner/prescriptions/[id]/page.tsx` (detalle read-only)

QA / tracking:
- `docs/opencode/plans/BE-010-plan.md` (cerrado en esta revisión)
- `docs/opencode/qa/QA-010-results.md` (IDs de findings alineados)
- `docs/opencode/qa/QA-010-findings.md` (Q010-001..Q010-004)
- `docs/opencode/reviews/BE-010-review.md` (este documento)

## Notas de seguridad

- **Autenticación**: los tres endpoints dependen de `get_current_access_user`; `_extract_user_id` lanza 401 si no hay `user_id` (`prescription_router.py:108-116`).
- **Autorización (escritura)**: `_WRITE_ROLES = {"veterinarian","clinic","staff","admin"}` (`prescription_router.py:36`). `_require_write_role` (108-116 vs. 141-148) lanza 403 si el rol no está en el conjunto.
- **IDOR/BOLA en creación**: `clinic_id` se resuelve del usuario autenticado en `_get_clinic_id_from_user` y se pasa a `CreatePrescriptionUseCase`; `ConsultationRepository.get_by_id(consultation_id, clinic_id)` filtra por tenant. `OwnershipError` → 403 si `consultation.pet_id != data.pet_id`. `DuplicatePrescriptionError` → 409 por `consultation_id`. `ConsultationNotCompletedError` → 422 si la cita no está `completed`.
- **Tenant isolation en lectura**: `GetPrescriptionUseCase` y `ListPrescriptionsUseCase` filtran por `clinic_id`. En `GET /{id}` y `GET ""`, si el usuario es owner (`_get_owner_id_from_user` + `_assert_owner_pet`), se fuerza `pet.owner_id == owner_id` → 404 en caso contrario (no se expone información de ajenos).
- **Validación de entrada**: Pydantic con longitudes (`PrescriptionItemCreate.name` min1/max200, `PrescriptionCreate.diagnosis` min1/max2000, `treatment_notes` max3000, `items/treatments/reminders` max50, `page_size` ge1/le100). Los errores de validación de Pydantic se mapean al contrato HTTP estándar.
- **No filtrado de info interna**: los mensajes de error son genéricos y estables ("La receta no existe.", "Ya existe una receta registrada para esta consulta.", "Solo un veterinario o staff de clínica puede prescribir.", "La mascota no coincide con la consulta."). Sin stack traces ni detalles de esquema.

## Clean architecture

- **Domain**: `Prescription` / `PrescriptionItem` / `PrescriptionTreatment` / `PrescriptionReminder` (+ `*Input` variants) como modelos Pydantic puros; sin dependencia de ORM ni framework.
- **Application**: los 3 casos de uso (`Create/Get/List`) inyectan repositorios por constructor; `CreatePrescriptionUseCase` inyecta `PrescriptionRepository`, `ConsultationRepository` y `AppointmentRepository` — desacoplado correctamente.
- **Infrastructure**: implementación ORM aislada en `prescription_repository_impl.py`; `UniqueConstraint("consultation_id")` como backstop en migración `a010` + `exists_by_consultation` en la app.
- **API**: routers como adaptadores delgados; mapeo de excepciones de dominio a códigos HTTP (`401/403/404/409/422`); **no se exponen modelos ORM** (siempre `PrescriptionRead.model_validate(...)`); listado paginado con `meta {page, page_size, size, total, pages}`.

## Contrato BE↔FE

- `Prescription` TS (`prescription.ts:42-57`) ≡ `PrescriptionRead` (`prescription_schemas.py:86-104`): `id`, `consultation_id`, `pet_id`, `clinic_id`, `branch_id`, `veterinarian_id`, `diagnosis`, `treatment_notes`, `created_by`, `items`, `treatments`, `reminders`, `created_at`, `updated_at`.
- `PrescriptionListResponse { items, meta }` (`prescription.ts:79-82`) ≡ `PrescriptionPage { items, meta: dict }` (`prescription_schemas.py:107-111`); `meta` incluye `page`, `page_size`, `size`, `total`, `pages` — consistente con el router (`prescription_router.py:302-310`).
- Query params: el router usa `pet_id` (obligatorio), `page` (≥1), `page_size` (1..100) (`prescription_router.py:274-279`); el frontend envía `page`, `page_size`, `pet_id` vía `URLSearchParams` (`prescription.ts:104-118`) — coincidente.
- `PrescriptionCreateData` (frontend) ⊂ `PrescriptionCreate` (schema API): los campos opcionales (`clinic_id`, `veterinarian_id`, `treatment_notes`, `items`, `treatments`, `reminders`) derivan/resuelven del backend según la cita — validado por `pytest app/tests/api/test_prescriptions_create.py` (201).

## Comparison con criterios (task `BE-010.md`)

| Criterio | Estado |
|---|---|
| Endpoints POST/GET detalle/GET listado con contratos | ✅ 3 endpoints + cliente API tipado |
| Routers sin lógica de negocio | ✅ Lógica en `prescription_use_cases.py` |
| No se exponen modelos ORM | ✅ Siempre `PrescriptionRead.model_validate` |
| Listado paginado con `meta {page, page_size, total, pages}` | ✅ `prescription_router.py:302-310` |
| Errores consistentes, sin info interna | ✅ 401/403/404/409/422 estables (mensajes genéricos) |
| Seguridad IDOR/BOLA por rol y clínica | ✅ `_require_write_role`, `_get_clinic_id_from_user`, `_assert_owner_pet` |
| Pruebas happy + negative + seguridad | ✅ 25 pytest (create, read, idor, auth, use cases) + UIA 18/18 + APIA 10/10 |
| Estados UX 5 (loading/submitting/empty/success/error) | ✅ `page.tsx` + `PrescriptionHistory` + `PrescriptionDetail` + UIA C2/C8/C9 |
| Migración `a010` reversible | ✅ `UniqueConstraint("consultation_id")`, FKs, índices `pet_id`/`created_at` |

## Checklist de revisión

- [x] Contrato BE validado.
- [x] Contrato FE validado.
- [x] Casos QA validados (re-ejecutados: pytest 25).
- [x] Arquitectura revisada (clean architecture + contratos).
- [x] Permisos e IDOR/BOLA revisados.
- [x] Evidencia documentada (fresh pytest + tsc + UIA + APIA + plan cerrado).
- [x] Findings de QA alineados (M1 de esta revisión corregido; `Q010-001..Q010-004` coherentes en `QA-010-{results,findings}.md`).

## Decision final

- Decision: `APPROVED`
- Evidencia: pytest **25 passed** (use cases + API — create/read/idor/auth), frontend `tsc --noEmit` **sin errores**, UIA **18/18** (chromium + mobile-chromium, 2 baselines), APIA **10/10**, contrato BE↔FE consistente, seguridad (authz + tenant isolation + IDOR/BOLA + validación + no filtrado de info interna) verificada en código, migración `a010` reversible, plan `BE-010` cerrado (`[PASS] stage=review`), QA APPROVED con 4 findings RESOLVED.
- El único finding de esta revisión (M1, trazabilidad F1–F3 → Q010-001..Q010-004) fue corregido inmediatamente y verificado. No queda abierto ningún find bloqueante.

## Política UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
