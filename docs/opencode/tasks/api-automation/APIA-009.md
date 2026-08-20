# APIA-009 — Automatización API del flujo de consultas / Medical consultation API automation

## Alcance

Validar los contratos API del slice BE-009 mediante pruebas automatizadas con HTTPX dentro de `backend/app/tests/`. Cubre creación de consulta, lectura por propietario/clinica, authn/authz, IDOR/BOLA, paginación y duplicados.

## Pruebas contractuales

### A1: Creación de consulta válida (happy path)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A01 |
| AC vinculado | AC-009-01 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario (misma clínica de la cita) |
| Request body | `{appointment_id: <cita_completed>, pet_id: <pet_de_la_cita>, diagnosis: "Fiebre y apatia", history: "Cuatro dias de anorexia", recommendations: "Analisis de sangre"}` |
| Esperado | 201 Created. Response JSON con `id`, `appointment_id`, `pet_id`, campos clínicos, `created_by`, `updated_at`. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_create_consultation_valid` |
| Evidencia | pending |

### A2: Creación sin token (401)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A02 |
| AC vinculado | AC-009-12 |
| Endpoint | POST /api/v1/consultations |
| Auth | Ninguno |
| Esperado | 401 Unauthorized con mensaje "Authentication required". |
| Archivo esperado | `tests/api/test_consultations_auth.py::test_create_without_token` |
| Evidencia | pending |

### A3: Creación para cita no completed (422)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A03 |
| AC vinculado | AC-009-02 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario |
| Request body | `{appointment_id: <cita_pending>, pet_id: <valid>, diagnosis: "..."}` |
| Esperado | 422 con mensaje legible ("appointment not completed"). Sin registro creado. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_create_for_not_completed_appointment` |
| Evidencia | pending |

### A4: GET de detalle y listado sin token (401)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A04 |
| AC vinculado | AC-009-12 |
| Endpoint | GET /api/v1/consultations/{id}; GET /api/v1/consultations?pet_id= |
| Auth | Ninguno |
| Esperado | 401 en ambos endpoints. |
| Archivo esperado | `tests/api/test_consultations_auth.py::test_get_without_token` |
| Evidencia | pending |

### A5: GET de detalle propio por propietario (200)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A05 |
| AC vinculado | AC-009-04 |
| Endpoint | GET /api/v1/consultations/{id} |
| Auth | Bearer token del propietario de la mascota |
| Esperado | 200 con campos clínicos legibles. Sin campos sensibles del owner (email, teléfono). |
| Archivo esperado | `tests/api/test_consultations_create.py::test_owner_get_detail` |
| Evidencia | pending |

### A6: Duplicación de consulta por appointment_id (409)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A06 |
| AC vinculado | AC-009-06 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario |
| Request body | Segundo POST con el mismo `appointment_id` del A1. |
| Esperado | 409 Conflict con mensaje claro "consulta ya existe". Unique constraint respeta el registro original. |
| Archivo esperado | `tests/api/test_consultations_duplicate.py::test_duplicate_appointment_conflict` |
| Evidencia | pending |

### A7: Campo requerido ausente (422)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A07 |
| AC vinculado | AC-009-07, AC-009-10 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario |
| Request body | `{appointment_id: <valid>, pet_id: <valid>}` (sin `diagnosis`) |
| Esperado | 422 con `detail` indicando el campo inválido. Sin detalles internos del stack. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_create_missing_required_field` |
| Evidencia | pending |

### A8: IDOR — veterinario de otra clínica crea sobre cita ajena (403)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A08 |
| AC vinculado | AC-009-11 |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de veterinario de clínica B |
| Request body | `{appointment_id: <cita_de_clinica_A>, pet_id: <pet_A>, diagnosis: "..."}` |
| Esperado | 403 Forbidden. Response sin datos de la cita o mascota ajena. |
| Archivo esperado | `tests/api/test_consultations_idor.py::test_cross_clinic_create_forbidden` |
| Evidencia | pending |

### A9: BOLA — propietario A lista consultas de mascota de propietario B
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A09 |
| AC vinculado | AC-009-05 |
| Endpoint | GET /api/v1/consultations?pet_id=<pet_de_B> |
| Auth | Bearer token de owner A |
| Esperado | 403 o 404. Response sin items de owner B. |
| Archivo esperado | `tests/api/test_consultations_idor.py::test_owner_cannot_list_other_owners_pet` |
| Evidencia | pending |

### A10: BOLA — propietario A abre detalle de consulta ajena
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A10 |
| AC vinculado | AC-009-05 |
| Endpoint | GET /api/v1/consultations/{id_de_B} |
| Auth | Bearer token de owner A |
| Esperado | 403 o 404. Sin exposición de campos clínicos de owner B. |
| Archivo esperado | `tests/api/test_consultations_idor.py::test_owner_cannot_read_other_consultation` |
| Evidencia | pending |

### A11: Listado por mascota con paginación
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A11 |
| AC vinculado | AC-009-03, AC-009-09 |
| Endpoint | GET /api/v1/consultations?pet_id=<pet> |
| Auth | Bearer token del propietario de la mascota |
| Query params | `?page=1&page_size=2` |
| Esperado | 200. `{items: [<=2], meta: {total: N, page: 1, page_size: 2}}`. Página 2 continua correctamente. Orden por fecha descendente. |
| Archivo esperado | `tests/api/test_consultations_pagination.py::test_list_by_pet_paginated` |
| Evidencia | pending |

### A12: Listado por clínica con paginación
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A12 |
| AC vinculado | AC-009-03, AC-009-09 |
| Endpoint | GET /api/v1/consultations?clinic_id=<clinic> |
| Auth | Bearer token de clinica/veterinario de esa clínica |
| Query params | `?page=1&page_size=5` |
| Esperado | 200 con `{items, meta}`. Solo consultas de esa clínica. |
| Archivo esperado | `tests/api/test_consultations_pagination.py::test_list_by_clinic_paginated` |
| Evidencia | pending |

### A13: Propietario intenta crear consulta (403)
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A13 |
| AC vinculado | AC-009-11 (inverso) |
| Endpoint | POST /api/v1/consultations |
| Auth | Bearer token de propietario |
| Esperado | 403 Forbidden. El owner es read-only. |
| Archivo esperado | `tests/api/test_consultations_auth.py::test_owner_cannot_create` |
| Evidencia | pending |

### A14: Consulta inexistente devuelve 404
| Campo | Valor |
| --- | --- |
| ID | APIA-009-A14 |
| AC vinculado | AC-009-04 (inverso) |
| Endpoint | GET /api/v1/consultations/999999 |
| Auth | Bearer token de propietario |
| Esperado | 404 Not Found con mensaje legible. |
| Archivo esperado | `tests/api/test_consultations_create.py::test_get_nonexistent_404` |
| Evidencia | pending |

## Cobertura de criterios

| Criterio | Caso APIA | Observaciones |
| --- | --- | --- |
| AC-009-01 | A1 | Creación válida. |
| AC-009-02 | A3 | 422 cita no completed. |
| AC-009-03 | A11, A12 | Listado paginado por mascota y clínica. |
| AC-009-04 | A5, A14 | Detalle 200 y 404. |
| AC-009-05 | A9, A10 | BOLA owner ajenos. |
| AC-009-06 | A6 | Unique constraint → 409. |
| AC-009-07 | A7 | Validación de schema. |
| AC-009-08 | — | Criterio de estados UI; cobertura exclusiva de UIA-009 C5/C8. |
| AC-009-09 | A11, A12 | Contratos de paginación subyacentes a la UI. |
| AC-009-10 | A7 | 422 legible por campo. |
| AC-009-11 | A8, A13 | IDOR clínica y rol owner. |
| AC-009-12 | A2, A4 | 401 en POST y GET. |
| AC-009-13 | — | Estado empty de UI; cobertura exclusiva de UIA-009 C4/C8 (backend responde 200 con `items: []`). |
| AC-009-14 | — | Migración Alembic; validación exclusiva del gate QA-009-T05 (upgrade/downgrade). |

## Estado global: OPEN
