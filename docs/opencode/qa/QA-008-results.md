# QA-008 Results — Solicitud y Gestión de Citas (Appointment Scheduling)

**Slice:** BE-008 / FE-008 / QA-008  
**Date:** 2026-08-16  
**Reviewer:** QA Agent (automated)  
**Estado global:** REJECTED

---

## 1. Preflight Validation

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Plan existe y schema v3 | ✅ EXISTS | `docs/opencode/plans/BE-008-plan.md` (status: IN_PROGRESS) |
| Backend task con DoD checkboxes | ✅ EXISTS | `docs/opencode/tasks/backend/BE-008.md` (DoD: all checked) |
| Frontend task | ✅ EXISTS | `docs/opencode/tasks/frontend/FE-008.md` (DoD: not started) |
| QA task | ✅ EXISTS | `docs/opencode/tasks/qa/QA-008.md` (DoD: empty) |
| `validate_slice_plan.py` stage=qa | ✅ PASS | Exit code 0, all assertions passed |

---

## 2. Backend Implementation Inventory

| Componente | Estado | Archivo | Líneas |
|-----------|--------|---------|--------|
| Domain Entity | ✅ EXISTS | `backend/app/domain/entities/appointment.py` | ~120 |
| Repository Protocol | ✅ EXISTS | `backend/app/domain/repositories/appointment_repository.py` | 10 methods |
| ORM Model | ✅ EXISTS | `backend/infrastructure/database/models/appointment.py` | table: appointments |
| Use Cases (7) | ✅ EXISTS | `backend/app/application/use_cases/appointment_use_cases.py` | ~350 |
| Schemas (6) | ✅ EXISTS | `backend/app/api/schemas/appointment_schemas.py` | ~160 |
| Router (7 endpoints) | ✅ EXISTS | `backend/app/api/v1/routers/appointment_router.py` | registered |
| Migration | ✅ EXISTS | `backend/alembic/versions/a008_appointments.py` | 2026-08-16 corrected |
| Unit Tests (claimed 15+) | ⚠️ EXISTS but FAILING | `backend/app/tests/test_appointment_use_cases.py` | 6 passed, 9 failed |
| API Tests | ❌ MISSING valid import | `backend/app/tests/api/test_appointments_api.py` — ImportError: No module named 'app.main' |

---

## 3. Test Execution Evidence

### 3.1 Unit Tests — Appointment Use Cases

**Comando:** `python -m pytest app/tests/test_appointment_use_cases.py -v --tb=short`  
**Resultado:** 🚫 **FAILED — 9 de 15 tests fallaron (60% failure rate)**

| Test | Resultado | Causa Raíz |
|------|-----------|-----------|
| test_creates_appointment_success | ✅ PASSED | Mock interface coincide con use case create_appointment() |
| test_invalid_appointment_type | ✅ PASSED | Validación de tipo correcta |
| test_invalid_duration_too_short | ✅ PASSED | Validación de duración correcta |
| test_conflict_with_veterinarian | ✅ PASSED | Detección de conflictos funciona |
| test_pending_to_approved | ❌ FAILED | Mock.transition_status() no acepta parámetro `scheduled_start` |
| test_approved_to_confirmed | ❌ FAILED | Mock.get_by_id() devuelve None entre tests (mock stateless) |
| test_confirmed_to_completed | ❌ FAILED | Mismo issue: cita ID 3 not found en mock |
| test_confirmed_to_no_show | ❌ FAILED | Mismo issue: cita ID 4 not found |
| test_invalid_transition_completed_to_approved | ❌ FAILED | Mock no encuentra cita (None), error "Cita con ID 5 no encontrada" no match regex "no es válida para el estado actual" |
| test_cancel_from_pending | ❌ FAILED | Cita ID 6 not found en mock |
| test_nonexistent_appointment | ✅ PASSED | Manejo correcto de cita inexistente |
| test_list_owner_appointments | ❌ FAILED | Mock.list_by_owner() falta parámetro `clinic_id` |
| test_empty_list | ❌ FAILED | Mismo issue: clinic_id mismatch |
| test_get_availability_with_slots | ❌ FAILED | GetAvailabilityUseCase.execute() no acepta parámetro `date` |
| test_tenant_isolation | ✅ PASSED | Tenant isolation funciona correctamente |

### 3.2 API Tests — Appointments

**Comando:** `python -m pytest app/tests/api/test_appointments_api.py -v --tb=short`  
**Resultado:** ❌ **FAILED — ImportError: No module named 'app.main'**

El archivo de test intenta `from app.main import create_app` pero el módulo no existe en el path. Esto indica que el archivo de API tests fue creado sin validar las imports contra la estructura actual del proyecto.

### 3.3 Frontend Implementation Inventory

| Componente | Estado | Archivo |
|-----------|--------|---------|
| Types | ✅ EXISTS | `frontend/src/features/appointments/types.ts` (types: Appointment, AppointmentCreate, StatusTransition, etc.) |
| API Client | ✅ EXISTS | `frontend/src/features/appointments/api.ts` (getAppointment, listMyAppointments, listClinicAppointments) |
| OwnerAgenda | ✅ EXISTS | `frontend/src/features/appointments/components/OwnerAgenda.tsx` |
| AppointmentForm | ✅ EXISTS | `frontend/src/features/appointments/components/AppointmentForm.tsx` |
| StatusBadge | ✅ EXISTS | `frontend/src/features/appointments/components/StatusBadge.tsx` (+ test) |
| Owner Appointments Page | ✅ EXISTS | `frontend/src/app/portal/owner/appointments/page.tsx` |
| New Appointment Page | ✅ EXISTS | `frontend/src/app/portal/owner/appointments/new/page.tsx` |
| Clinic Appointments Page | ✅ EXISTS | `frontend/src/app/clinic/appointments/page.tsx` |

---

## 4. QA Acceptance Criteria Matrix

| # | Criterio de Aceptación | Estado | Evidencia |
|---|----------------------|--------|-----------|
| AC-01 | Crear cita pendiente con datos mínimos (owner_id, scheduled_start, scheduled_end) | ✅ APPROVED | test_creates_appointment_success PASSED |
| AC-02 | Validar appointment_type no permitido genera error | ✅ APPROVED | test_invalid_appointment_type PASSED |
| AC-03 | Validar duración mínima (>0) | ✅ APPROVED | test_invalid_duration_too_short PASSED |
| AC-04 | Detección de conflictos de veterinario | ✅ APPROVED | test_conflict_with_veterinarian PASSED |
| AC-05 | Transición pending→approved con validación de permisos | ❌ REJECTED | Mock interface mismatch: scheduled_start parámetro faltante |
| AC-06 | Transición approved→confirmed | ❌ REJECTED | Mock stateless: citas no persisten entre tests |
| AC-07 | Transición confirmed→completed | ❌ REJECTED | Mismo issue que AC-06 |
| AC-08 | Transición confirmed→no_show | ❌ REJECTED | Mismo issue que AC-06 |
| AC-09 | Validar transición inválida (completed→approved rejected) | ❌ REJECTED | Mock no encuentra cita, error message wrong |
| AC-10 | Cancelar cita desde pending | ❌ REJECTED | Mock stateless: cita ID 6 not found |
| AC-11 | Listar citas por owner con tenant isolation | ❌ REJECTED | list_by_owner mock falta clinic_id parámetro |
| AC-12 | Lista vacía retorna items=[], total=0 | ❌ REJECTED | Mismo issue que AC-11 |
| AC-13 | Endpoint get_availability con slots | ❌ REJECTED | Use case execute() no acepta 'date' param |
| AC-14 | Tenant isolation — no acceder citas de otra clínica | ✅ APPROVED | test_tenant_isolation PASSED |

**Resumen de Aceptación:** 5/14 APPROVED, 9/14 REJECTED (64% rejection rate on acceptance criteria)

---

## 5. QA Gate Decision

### Estado: **REJECTED**

**Motivo:** 9 de 15 pruebas unitarias fallaron por API mismatches entre use cases, mock repository y assertions de tests. Esto es una falla de calidad en el código del producto — los tests no coinciden con la implementación real.

Adicionalmente:
- El archivo `test_appointments_api.py` tiene import roto (`app.main`), lo que indica que las API tests nunca se ejecutaron correctamente.
- FE-008 existe en filesystem pero no está versionado en Git (no hay evidencia de build/lint/tests frontend).

**Criterio aplicado:** "QA no implementa las pruebas unitarias faltantes de una capa productiva: registra el gap para que lo corrija el implementador."

---

## 6. Recommended Next Steps

1. Corregir `MockAppointmentRepository` para que coincida con la interfaz real del use case:
   - `transition_status()` debe aceptar `scheduled_start`, `duration_minutes`
   - Mock debe mantener estado entre test methods (o cada test debe recrear citas)
   - `list_by_owner()` requiere parámetro `clinic_id`

2. Corregir `test_appointments_api.py`:
   - Import correcto de `app.main` o usar fixture/app factory directa
   - Validar que los imports existan antes de ejecutar

3. Ejecutar build/lint de frontend para verificar FE-008:
   ```powershell
   cd frontend; npx next build 2>&1; npx next lint 2>&1
   ```

4. Rerun QA después de correcciones.

**Comando recomendado para resolver hallazgos:** `/implement-findings BE-008`  
**Motivo:** Las pruebas del producto layer fallan — el implementador debe corregir la discrepancia entre mock, use cases y tests antes de que QA pueda aprobar.

---

## 7. Evidence Files

- Test output: `python -m pytest app/tests/test_appointment_use_cases.py -v --tb=short` → 9 failed
- Test output: `python -m pytest app/tests/api/test_appointments_api.py -v --tb=short` → ImportError
- Product code: `backend/app/application/use_cases/appointment_use_cases.py` (lines 130-250)
- Mock code: `backend/app/tests/test_appointment_use_cases.py` (MockAppointmentRepository definition)
- API test: `backend/app/tests/api/test_appointments_api.py` (line 8: wrong import)

---

*QA Gate executed by automated QA agent on 2026-08-16.*
