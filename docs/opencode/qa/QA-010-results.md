# QA-010 Results — Recetas, tratamientos y recordatorios

**Slice:** BE-010 / FE-010 / QA-010
**Date:** 2026-08-22
**Reviewer:** InVet QA Validator
**Estado global:** APPROVED

- Decision: APPROVED (ver §8)

---

## 1. Preflight Validation

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Plan existe y schema v3 | ✅ EXISTS | `docs/opencode/plans/BE-010-plan.md` (AC-010-01..14) |
| Backend task con DoD | ✅ EXISTS | `docs/opencode/tasks/backend/BE-010.md` |
| Frontend task | ✅ EXISTS | `docs/opencode/tasks/frontend/FE-010.md` |
| QA task con DoD checkboxes | ✅ EXISTS | `docs/opencode/tasks/qa/QA-010.md` (DoD completado + evidencia 2026-08-22) |
| UIA-010 / APIA-010 / US-010 | ✅ EXISTS | `docs/opencode/tasks/ui-automation/UIA-010.md`, `api-automation/APIA-010.md`, `user-stories/US-010.md` |
| Stack de prueba | ✅ healthy | `docker compose` invet-db / invet-backend / invet-frontend; PostgreSQL `invet` |

---

## 2. Inventory del SUT

| Componente | Estado | Archivo |
|-----------|--------|---------|
| Domain Entity (4 entidades) | ✅ EXISTS | `backend/app/domain/entities/prescription.py` (Prescription, Item, Treatment, Reminder) |
| Repository contrato | ✅ EXISTS | `backend/app/domain/repositories/prescription_repository.py` |
| ORM Modelo | ✅ EXISTS | `backend/app/infrastructure/database/models/prescription.py` |
| Repositorio ORM | ✅ EXISTS | `backend/app/infrastructure/database/repositories/prescription_repository_impl.py` |
| Use Cases | ✅ EXISTS | `backend/app/application/use_cases/prescription_use_cases.py` (`CreatePrescriptionUseCase`, `ReadPrescriptionUseCase`, `DuplicatePrescriptionError`→409) |
| Schemas Pydantic | ✅ EXISTS | `backend/app/api/v1/schemas/prescription_schemas.py` (`PrescriptionCreate`, `PrescriptionRead`, `PrescriptionPage`) |
| Router POST+GET | ✅ EXISTS | `backend/app/api/v1/routers/prescription_router.py` (`_WRITE_ROLES` = {veterinarian, clinic, staff, admin}) |
| Migration | ✅ EXISTS | `backend/alembic/versions/a010_prescriptions.py` (`UniqueConstraint("consultation_id")`) |
| Cliente API FE | ✅ EXISTS | `frontend/src/shared/api/prescription.ts` (`createPrescription`, `getPrescription`, `listPrescriptions`) |
| Formulario clínico | ✅ EXISTS | `frontend/src/app/clinic/prescriptions/new/page.tsx` |
| Historial / Detalle | ✅ EXISTS | `frontend/src/app/portal/owner/...` (historial + detalle read-only) |

---

## 3. Evidencia de ejecución

### 3.1 Happy path (AC-010-01, AC-010-04, AC-010-05) — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| pytest prescriptions (create/read/idor/auth + use cases) | **25 passed** (0.96s) — `docker compose run --rm backend pytest ... test_prescriptions_create.py test_prescriptions_read.py test_prescriptions_idor.py test_prescriptions_auth.py test_prescription_use_cases.py -q` |
| UIA-010 e2e `fe-010-prescription-create.spec.ts` C1/C3/C5/C6 (chromium + mobile-chromium) | **8/8 PASS** — acceso formulario, crear 201 "Receta creada #id", historial, detalle read-only |
| APIA-010 (regresión FE) | **10/10 PASS** (C1 201, C8 200 lectura, C9 200+meta listado) — ver `QA-010.md` |

### 3.2 Negative / validaciones (AC-010-02, AC-010-07) — ✅ PASS

| Caso | Esperado | Obtenido |
|------|----------|----------|
| Cita no `completed` | 422 | ✅ 422 `ConsultationNotCompletedError` |
| Consulta inexistente | 422 | ✅ 422 `ConsultationInvalidError` |
| Duplicado por consulta | 409 | ✅ 409 `DuplicatePrescriptionError` — detalle "Ya existe una receta registrada para esta consulta." (`prescription_use_cases.py:93`) |
| Items inválidos / sin token | 422 / 401 | ✅ sin filtrar internals |

### 3.3 Permisos / IDOR / BOLA (AC-010-08, AC-010-09, AC-010-10) — ✅ PASS

| Caso | Resultado | Detalle |
|------|-----------|---------|
| POST sin token | ✅ 401 | guard auth |
| Owner crea receta (rol `user` ∉ `_WRITE_ROLES`) | ✅ 403 | `_require_write_role` |
| Vet otra clínica crea | ✅ 403 | cross-clinic rechazado |
| Owner lee receta ajena (GET) | ✅ 404 | BOLA/IDOR cerrado, sin datos expuestos |
| Admin → receta clínica ajena | ✅ 404 | aislamiento por tenant (verificado curl: 1000/1001) |
| APIA A02/A04 (unauth API) | ✅ 401 | endpoint protegido |
| UIA C4 propietario sin permiso | ✅ PASS | formulario clínico no expuesto al rol owner (chromium + mobile) |
| UIA C7 receta ajena no visible | ✅ PASS | owner no ve receta de otra mascota |

### 3.4 Estados UX y responsive (AC-010-11) — ✅ PASS

| Suite | Resultado |
|-------|-----------|
| UIA-010 `fe-010-prescription-states.spec.ts` C2 (validación inline diagnosis) | **2/2 PASS** (chromium + mobile) |
| UIA-010 C8 (responsive mobile) | **2/2 PASS** |
| UIA-010 C9 (acentes sin mojibake) | **2/2 PASS** (tras fix de `PublicHeader.tsx`, ver QA-010-findings Q010-001) |
| UIA-010 `fe-010-prescription-access.spec.ts` C4/C7 | **4/4 PASS** |
| **UIA-010 TOTAL** | **18/18 PASS** (9 casos × 2 proyectos: chromium, mobile-chromium) — 8.4s |

---

## 4. Migración Alembic (AC-010-14) — ✅ PASS

- **Migration:** `a010_prescriptions.py`, `revision=a010` ← `down_revision=a009`.
- **Estructura:** 4 tablas (prescriptions, items, treatments, reminders); `UniqueConstraint("consultation_id")`; FK a `consultations`/`pets`/`clinics`/`veterinarians`; índices `pet_id`/`created_at`. `upgrade()`/`downgrade()` reversibles.
- **Cobertura de datos:** sin pérdida (tablas nuevas, FK `CASCADE`/`SET NULL` coherentes).

---

## 5. Cobertura de aceptación (AC-010-*)

| AC | Criterio | Evidencia | Estado |
|----|----------|-----------|--------|
| AC-010-01 | Crear receta atómica sobre consulta completed | pytest 201 + UIA C1/C3 | ✅ |
| AC-010-02 | 422 si consulta inexistente / no completed | use case + APIA C2/C3 | ✅ |
| AC-010-04 | Detalle por id visible (clínica/vet/owner) | pytest 200 + UIA C6 | ✅ |
| AC-010-05 | Listado paginado por mascota | pytest `meta` + UIA C5 | ✅ |
| AC-010-07 | Única receta por consulta (unique) | use case 409 + UIA C3 (tolerante 409) + `a010` unique | ✅ |
| AC-010-08 | 403 owner/vet otra clínica al crear | pytest 403 + UIA C4 | ✅ |
| AC-010-09 | 404/403 lectura receta ajena | pytest 404 + UIA C7 | ✅ |
| AC-010-10 | 401 sin token en todos endpoints | pytest 401 (3 endpoints) + UIA | ✅ |
| AC-010-11 | Estados UX completos (loading/submitting/success/error/empty) | UIA C2/C8/C9 + jest `prescription.test.ts` | ✅ |
| AC-010-14 | Migración `a010` con FK/unique/índices | `a010` vigente, reversible | ✅ |

> Nota: el plan no define AC-010-03, 06, 12 ni 13; todos los ACs definidos están cubiertos con evidencia reproducible.

---

## 6. Riesgo residual / evidencia-gaps

- **Envío real de correos de recordatorios** fuera de alcance MVP (`due_at` como dato informativo); queda pendiente en backlog. No es defecto.
- **Proyectos firefox/webkit** de Playwright no disponibles en este entorno (`spawn UNKNOWN`). La cobertura UI se ejerce sobre **chromium + mobile-chromium** (2 proyectos), suficiente para el gate dado que los casos son cross-browser agnósticos (asserts de texto/estado, no de motor). Riesgo residual: ninguno material.

---

## 7. Findings

- Se registraron **4 findings** durante la sesión de QA (Q010-001..Q010-004), todos **RESOLVED** en esta sesión. Ver `docs/opencode/qa/QA-010-findings.md`.
- Ningún finding queda abierto al momento del gate.

---

## 8. Gate Decision

- 10/10 ACs definidos cubiertos con evidencia reproducible (pytest 25 + UIA 18 + APIA 10).
- UIA 18/18 PASS en **dos baselines** (limpio y con datos residuales), eliminando la dependencia del estado previo de `prescriptions`.
- Sin hallazgos de seguridad IDOR/BOLA/rol abiertos en el flujo de prescripciones.
- Migración `a010` vigente, reversible, sin pérdida de datos.
- Findings Q010-001..Q010-004 RESOLVED, revalidados por las suites verdes.

### Decision: **APPROVED**

---

## 9. Evidence Log

- pytest prescriptions (create/read/idor/auth + use cases): **25 passed** (0.96s)
- UIA-010 e2e (`--project chromium --project mobile-chromium`): **18/18 PASSED** (8.4s) — re-ejecutado en baseline limpio y con residuos de `prescriptions` (ambos verde)
- APIA-010 (regresión FE): **10/10 PASSED** (C1–C10) — `QA-010.md`
- frontend `jest` suite completa: **28 suites / 157 tests PASSED** (incl. `prescription.test.ts`) — `QA-010.md`
- frontend `tsc --noEmit` / `next lint`: **0 errores**
- alembic `heads`: **`a010 (head)`**
- E2E `curl` ground-truth: admin→404 (1000/1001), vet→200, owner1→200/404, owner2→404/200 (BOLA aislamiento CORRECTO)

---

*Estado de ejecución: APPROVED*
*Siguiente paso: `/review-slice BE-010` — QA aprobado sin findings abiertos.*
