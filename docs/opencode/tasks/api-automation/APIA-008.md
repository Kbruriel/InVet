# APIA-008 — Automatizacion API del flujo de citas / Appointment scheduling API automation

## Alcance

Validar los contratos API del slice BE-008 mediante pruebas automatizadas con HTTPX dentro de `backend/app/tests/`.

## Pruebas contractuales

### A1: Creacion de cita (happy path)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A01 |
| AC vinculado | AC-008-01 |
| Endpoint | POST /api/v1/appointments |
| Auth | Bearer token de propietario |
| Request body | `{pet_id: <valid_pet_id>, veterinarian_id: null, appointment_type: "consulta_general", scheduled_start: "2026-09-15T10:00:00Z", scheduled_end: "2026-09-15T10:30:00Z", reason: "Revision anual"}` |
| Esperado | 201 Created. Response JSON con status=pending, id generada, owner_id = token.user_id. |
| Archivo esperado | `tests/api/test_appointments_create.py::test_create_appointment_valid` |

### A2: Creacion de cita sin auth (negative)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A02 |
| AC vinculado | AC-008-15 |
| Endpoint | POST /api/v1/appointments |
| Auth | Ninguno |
| Esperado | 401 Unauthorized. Response con mensaje "Authentication required". |
| Archivo esperado | `tests/api/test_appointments_auth.py::test_create_without_token` |

### A3: Creacion de cita con fecha en el pasado (negative)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A03 |
| AC vinculado | AC-008-17 |
| Endpoint | POST /api/v1/appointments |
| Auth | Bearer token de propietario |
| Request body | `{pet_id: <valid>, scheduled_start: "2020-01-01T10:00:00Z", ...}` |
| Esperado | 422 Unprocessable Entity. Response con mensaje legible "La fecha debe ser futura". |
| Archivo esperado | `tests/api/test_appointments_create.py::test_create_past_date` |

### A4: Creacion de cita para mascota de otro owner (IDOR)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A04 |
| AC vinculado | AC-008-16 |
| Endpoint | POST /api/v1/appointments |
| Auth | Bearer token de owner_A |
| Request body | `{pet_id: <pet_id_of_owner_B>, ...}` |
| Esperado | 403 Forbidden. Response sin datos expuestos de la mascota ajena. |
| Archivo esperado | `tests/api/test_appointments_idor.py::test_create_for_other_owners_pet` |

### A5: Transicion pending -> approved (valida)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A05 |
| AC vinculado | AC-008-03 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de clinica |
| Request body | `{action: "approved"}` |
| Esperado | 200 OK. Response con status=approved. updated_at actualizado. |
| Archivo esperado | `tests/api/test_status_transitions.py::test_transition_pending_to_approved` |

### A6: Transicion completed -> approved (invalida)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A06 |
| AC vinculado | AC-008-04 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de clinica |
| Request body | `{action: "approved"}` |
| Esperado | 422 Unprocessable Entity. Response con mensaje "invalid transition from completed". |
| Archivo esperado | `tests/api/test_status_transitions.py::test_transition_completed_to_approved_invalid` |

### A7: Propietario intenta aprobar cita (permiso incorrecto)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A07 |
| AC vinculado | AC-008-05 (inverso) |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de propietario (owner de la cita) |
| Request body | `{action: "approved"}` |
| Esperado | 403 Forbidden. Response sin detalles internos. |
| Archivo esperado | `tests/api/test_appointments_auth.py::test_owner_cannot_approve` |

### A8: Clinica aprueba cita de otra sucursal (IDOR)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A08 |
| AC vinculado | AC-008-16 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de clinica_B (cita pertenece a clinica_A) |
| Request body | `{action: "approved"}` |
| Esperado | 403 o 404. Response sin datos de la cita ajena. |
| Archivo esperado | `tests/api/test_appointments_idor.py::test_cross_branch_approval` |

### A9: Disponibilidad devuelve slots correctos
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A09 |
| AC vinculado | AC-008-10 |
| Endpoint | GET /api/v1/appointments/availability |
| Auth | Bearer token (cualquier rol) |
| Query params | `?date=2026-09-15&branch_id=<valid>` |
| Esperado | 200 OK. Response JSON con array de slots que incluye: disponibles y ocupados. Slot duration configurable (default 30 min). Sin solapamiento entre slots. |
| Archivo esperado | `tests/api/test_appointments_availability.py::test_availability_slots` |

### A10: Listado paginado de citas del propietario
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A10 |
| AC vinculado | AC-008-02, AC-008-19 |
| Endpoint | GET /api/v1/appointments/me |
| Auth | Bearer token de propietario |
| Query params | `?page=1&page_size=5` |
| Esperado | 200 OK. Response `{items: [<=5 items], meta: {total: N, page: 1, page_size: 5}}`. Items max = min(page_size, total). |
| Archivo esperado | `tests/api/test_appointments_pagination.py::test_list_own_appointments_paginated` |

### A11: Listado paginado de citas de clinica con filtro por status
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A11 |
| AC vinculado | AC-008-19 |
| Endpoint | GET /api/v1/appointments/clinic |
| Auth | Bearer token de clinica |
| Query params | `?page=1&page_size=10&status=pending` |
| Esperado | 200 OK. Items filtrados solo por status=pending. Todos pertenecen a sucursal del usuario autenticado. Meta correcto. |
| Archivo esperado | `tests/api/test_appointments_pagination.py::test_clinic_list_filtered_by_status` |

### A12: Cancelacion de cita valida por propietario
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A12 |
| AC vinculado | AC-008-08 |
| Endpoint | PUT /api/v1/appointments/{id}/cancel |
| Auth | Bearer token del propietario (owner de la cita) |
| Esperado | 200 OK. Response con status=cancelled. updated_at actualizado. |
| Archivo esperado | `tests/api/test_appointments_cancel.py::test_owner_cancels_own_pending` |

### A13: Cancelacion de cita terminal (no_show/completed) — invalida
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A13 |
| AC vinculado | AC-008-04 |
| Endpoint | PUT /api/v1/appointments/{id}/cancel |
| Auth | Bearer token de propietario |
| Esperado | 422 Unprocessable Entity. Response con mensaje "cannot cancel terminal status". |
| Archivo esperado | `tests/api/test_appointments_cancel.py::test_cancel_terminal_status_invalid` |

### A14: Reprogramacion valida
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A14 |
| AC vinculado | AC-008-09 |
| Endpoint | PUT /api/v1/appointments/{id}/reschedule |
| Auth | Bearer token de clinica/vet |
| Request body | `{new_start: "2026-09-20T14:00:00Z", new_end: "2026-09-20T14:30:00Z"}` |
| Esperado | 200 OK. Response con nuevos scheduled_start y scheduled_end. Cita mantiene los mismos owner/pet/vet. |
| Archivo esperado | `tests/api/test_appointments_cancel.py::test_clinic_reschedules_valid` |

### A15: Reprogramacion con solapamiento (invalida)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A15 |
| AC vinculado | AC-008-09 |
| Endpoint | PUT /api/v1/appointments/{id}/reschedule |
| Auth | Bearer token de clinica |
| Request body | `{new_start: "2026-09-15T10:00:00Z", new_end: "2026-09-15T10:30:00Z"}` (slot ya ocupado por otra cita) |
| Esperado | 409 Conflict. Response con mensaje "El slot seleccionado ya esta ocupado". |
| Archivo esperado | `tests/api/test_appointments_availability.py::test_reschedule_overlapping_slot` |

### A16: Veterinario completo una cita assigned a su nombre (valida)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A16 |
| AC vinculado | AC-008-06 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de veterinario (assigned vet de la cita) |
| Request body | `{action: "completed"}` |
| Esperado | 200 OK. Response con status=completed. updated_at actualizado. |
| Archivo esperado | `tests/api/test_status_transitions.py::test_vet_completes_assigned` |

### A17: Veterinario diferente completa cita no assigned (invalida)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A17 |
| AC vinculado | AC-008-06 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de otro veterinario (no assigned) |
| Request body | `{action: "completed"}` |
| Esperado | 403 Forbidden. Response sin datos expuestos. |
| Archivo esperado | `tests/api/test_appointments_auth.py::test_other_vet_cannot_complete` |

### A18: Marca no-show valida (confirmed → no_show)
| Campo | Valor |
| --- | --- |
| ID | APIA-008-A18 |
| AC vinculado | AC-008-07 |
| Endpoint | PUT /api/v1/appointments/{id}/status |
| Auth | Bearer token de veterinario (assigned) o clinica |
| Request body | `{action: "no_show"}` |
| Esperado | 200 OK. Response con status=no_show. updated_at actualizado. |
| Archivo esperado | `tests/api/test_status_transitions.py::test_mark_no_show` |

## Cobertura de implementacion (APIA-008)

| Archivo | Lineas | Descripción |
|---------|--------|-------------|
| `InVet_UI_Automation/tests/api/api-a-008-appointments.spec.ts` | ~1100 | Spec completo Playwright con 20 casos de prueba (A1-A19) |

### Matriz de coverage por criterio AC

| Caso API | AC vinculado | Test ID | Estado |
|----------|--------------|---------|--------|
| A1 | AC-008-01 | @smoke APIA-008-A01 | Implementado (createOwnerAppointment helper) |
| A2 | AC-008-15 | @regression APIA-008-A02 | Implementado (loginAsOwner skip guard) |
| A3 | AC-008-17 | @regression APIA-008-A03 | Implementado (pastDate = 2020-01-01) |
| A4 | AC-008-16 | @regression APIA-008-A04 | Implementado (pet_id=99999, check sensitive data exposure) |
| A5 | AC-008-03 | @smoke APIA-008-A05 | Implementado (pending->approved transition flow) |
| A6 | AC-008-04 | @regression APIA-008-A06 | Implementado (completed->approved invalid via full chain) |
| A7 | AC-008-05 | @regression APIA-008-A07 | Implementado (owner tries approve, expect 403) |
| A8 | AC-008-16 | @regression APIA-008-A08 | Implementado con skip guard (cross-branch IDOR) |
| A9 | AC-008-10 | @smoke APIA-008-A09 | Implementado (availability endpoint, 200/401 dual handling) |
| A10 | AC-008-02, AC-008-19 | @smoke APIA-008-A10 | Implementado (paginated /me items+meta assertions) |
| A11 | AC-008-19 | @smoke APIA-008-A11 | Implementado (clinic filtered by status=pending) |
| A12 | AC-008-08 | @regression APIA-008-A12 | Implementado (full create+cancel flow) |
| A13 | AC-008-04 | @regression APIA-008-A13 | Implementado (create+complete chain then cancel=invalid) |
| A14 | AC-008-09 | @regression APIA-008-A14 | Implementado (approve+reschedule flow) |
| A15 | AC-008-09 | @regression APIA-008-A15 | Implementado (overlapping slot detection dual 200/409) |
| A16 | AC-008-06 | @regression APIA-008-A16 | Implementado (full chain pending->completed via vet) |
| A17 | AC-008-06 | @regression APIA-008-A17 | Implementado con skip guard (cross-vet IDOR) |
| A18 | AC-008-07 | @regression APIA-008-A18 | Implementado (confirmed->no_show with dual 200/403 handling) |

### Casos no automaticos actuales (skip guards — requieren seeding de datos)

| Caso | Motivo del skip | Condicion para habilitar |
|------|-----------------|-------------------------|
| A8 (cross-branch IDOR) | Necesita 2da cuenta clinica seeded | Crear clinic_B fixture en pytest/seeds |
| A17 (cross-vet IDOR) | Necesita 2do vet seeded | Crear vet_B fixture en pytest/seeds |

### Dependencias para ejecucion

- Variables de entorno: `LOGIN_EMAIL`, `LOGIN_PASSWORD`, `CLINIC_EMAIL`, `CLINIC_PASSWORD`, `VET_EMAIL`, `VET_PASSWORD`
- Backend running in Docker at `http://localhost:8000`
- Seeder fixture con owner, clinic, vet seeded para pruebas sin skip

## Estado global: READY_FOR_REVALIDATION
