# QA-008 Findings — Solicitud y Gestión de Citas (Appointment Scheduling)

**Slice:** BE-008 / FE-008 / QA-008  
**Date:** 2026-08-16  
**Estado global:** OPEN

---

## Finding Q008-001: Mock Repository API Mismatch — transition_status missing parameters

| Campo | Valor |
|-------|-------|
| Severity | Critical |
| Categoría | Product Tests / Unit Test |
| Componente | `backend/app/tests/test_appointment_use_cases.py::MockAppointmentRepository` |
| Afecta Tests | test_pending_to_approved, test_confirmed_to_completed, test_confirmed_to_no_show |

**Descripción:**  
`MockAppointmentRepository.transition_status()` tiene la firma:
```python
async def transition_status(self, appointment_id, clinic_id, new_status, notes=None)
```
pero `TransitionAppointmentStatusUseCase.execute()` lo llama con parámetros adicionales:
```python
await self.repository.transition_status(
    appointment_id=appointment_id,
    clinic_id=clinic_id,
    new_status=new_status.value,
    notes=notes,
    scheduled_start=new_start,       # FALTANTE en mock
    duration_minutes=duration_minutes,  # FALTANTE en mock
)
```

**Evidencia:** 
```
TypeError: MockAppointmentRepository.transition_status() got an unexpected keyword argument 'scheduled_start'
```

**Reparación requerida:** Actualizar la firma del mock para aceptar `scheduled_start` y `duration_minutes`:
```python
async def transition_status(
    self, appointment_id: int, clinic_id: int, new_status: str, notes: str | None = None,
    scheduled_start: datetime | None = None, duration_minutes: int | None = None
) -> Appointment | None:
    # ... existing logic + update appt fields if provided
```

---

## Finding Q008-002: Mock Repository API Mismatch — list_by_owner missing clinic_id parameter

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | Product Tests / Unit Test |
| Componente | `backend/app/tests/test_appointment_use_cases.py::MockAppointmentRepository` |
| Afecta Tests | test_list_owner_appointments, test_empty_list |

**Descripción:**  
`MockAppointmentRepository.list_by_owner()` tiene la firma:
```python
async def list_by_owner(self, owner_id: int, page: int = 1, size: int = 20)
```
pero `ListAppointmentsByOwnerUseCase.execute()` lo llama con `clinic_id`:
```python
await self.repository.list_by_owner(owner_id=owner_id, clinic_id=clinic_id, page=page, size=size)
```

**Evidencia:**
```
TypeError: MockAppointmentRepository.list_by_owner() missing 1 required positional argument: 'clinic_id'
```

**Reparación requerida:** Agregar `clinic_id` a la firma del mock:
```python
async def list_by_owner(self, owner_id: int, clinic_id: int, page: int = 1, size: int = 20):
    items = [a for a in self._items.values() if a.owner_id == owner_id and a.clinic_id == clinic_id]
```

---

## Finding Q008-003: GetAvailabilityUseCase execute() Parameter Mismatch

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | Product Tests / Use Case Interface |
| Componente | `backend/app/application/use_cases/appointment_use_cases.py::GetAvailabilityUseCase` |
| Afecta Tests | test_get_availability_with_slots |

**Descripción:**  
El test llama:
```python
result = await use_case.execute(
    veterinarian_id=1, clinic_id=1, date=datetime(2025, 8, 15)
)
```
pero `GetAvailabilityUseCase.execute()` espera otros parámetros (probablemente `date_str` o `scheduled_start`).

**Evidencia:**
```
TypeError: GetAvailabilityUseCase.execute() got an unexpected keyword argument 'date'
```

**Reparación requerida:** Verificar que el test use la firma correcta del use case, O actualizar el use case para aceptar `date` como parámetro.

---

## Finding Q008-004: Test State Isolation — Mock not persistent across test methods

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | Product Tests / Test Infrastructure |
| Componente | `backend/app/tests/test_appointment_use_cases.py::TestTransitionAppointmentStatusUseCase` |
| Afecta Tests | test_approved_to_confirmed, test_confirmed_to_completed, test_confirmed_to_no_show, test_invalid_transition_completed_to_approved, test_cancel_from_pending |

**Descripción:**  
Cada método de prueba crea su propio mock `MockAppointmentRepository()` independiente con `self._items = {}`. Cuando el use case llama `get_by_id(appointment_id, clinic_id)` para una transición, la cita no existe en el mock porque fue creada en un test previo que usó un mock diferente.

**Evidencia:**
```
ValueError: Cita con ID 2 no encontrada.
ValueError: Cita con ID 3 no encontrada.
ValueError: Cita con ID 5 no encontrada.
ValueError: Cita con ID 6 no encontrada.
```

**Reparación requerida:** 
- Opción A: Cada test method debe crear las citas necesarias dentro del mismo mock
- Opción B: Usar `pytest.fixture` con scope para compartir el mock entre tests de la clase
- Opción C: Crear helper `setup_transition_state(use_case, appointment_id, status)` que persista en el mock del current test

---

## Finding Q008-005: API Test File Has Broken Import

| Campo | Valor |
|-------|-------|
| Severity | Major |
| Categoría | Product Tests / API Test Infrastructure |
| Componente | `backend/app/tests/api/test_appointments_api.py` line 8 |
| Afecta Tests | Todas las API tests de BE-008 |

**Descripción:**  
El archivo importa `from app.main import create_app` pero ese módulo no existe o no exporta esa función en el path actual del test runner.

**Evidencia:**
```
ImportError: No module named 'app.main'
```

**Reparación requerida:** 
1. Verificar si `backend/app/main.py` existe y exporta `create_app`
2. Actualizar el import correctamente, o usar una fixture directa de la app FastAPI

---

## Finding Q008-006: Frontend Tests for StatusBadge May Not Be Executed

| Campo | Valor |
|-------|-------|
| Severity | Minor |
| Categoría | Product Tests / Frontend |
| Componente | `frontend/src/features/appointments/components/StatusBadge.test.tsx` |
| Afecta Tests | FE-008 frontend test suite |

**Descripción:**  
El archivo de test para StatusBadge existe pero no hay evidencia de que se haya ejecutado `npm test` o `npx jest` en el frontend. El DoD de FE-008 marca "Tests" pero no hay output de pruebas.

**Reparación requerida:** Ejecutar `cd frontend && npm test -- --ci` y validar que pase.

---

## Summary of Findings

| Finding ID | Severity | Category | Status |
|------------|----------|----------|--------|
| Q008-001 | Critical | Unit Test API Mismatch | OPEN |
| Q008-002 | Major | Unit Test API Mismatch | OPEN |
| Q008-003 | Major | Use Case Interface | OPEN |
| Q008-004 | Major | Test State Isolation | OPEN |
| Q008-005 | Major | API Test Infrastructure | OPEN |
| Q008-006 | Minor | Frontend Tests | OPEN |

**Total:** 6 findings (1 Critical, 4 Major, 1 Minor) — All OPEN

---

*QA findings created by automated QA agent on 2026-08-16.*
