# QA-015 - Findings del slice BE-015 (reportes agregados)

- Estado global: `RESOLVED`

Se documentan las desviaciones observadas durante la validaci[oó]n QA-015
contra PostgreSQL real. Ninguno queda en estado bloqueante al cierre.

## QF-015-01 - Paginación no determinista en reportes paginados

- Estado: `RESOLVED`
- Severidad: high
- Ámbito: backend (use-cases de agregación)
- Criterio afectado: `QA-015-T02`
- Síntoma: en la primera ejecución del script, `appointments_p1p2` falló por
  **overlap** de IDs entre páginas y **rows ausentes** en la unión de
  `p1∪p2` sobre un total de 12 registros. Root cause: los 5 use-cases
  paginados ordenaban por una única columna sin tiebreaker.
- Afectados:
  - `backend/app/application/usecases/reports/report_appointments.py` → `order_by(Appointment.scheduled_start.desc(), Appointment.id.desc())`
  - `backend/app/application/usecases/reports/report_services.py` → `order_by(Service.name.asc(), Service.id.asc())`
  - `backend/app/application/usecases/reports/report_consultations.py` → `order_by(Consultation.updated_at.desc(), Consultation.id.desc())`
  - `backend/app/application/usecases/reports/report_payments.py` → `order_by(Payment.paid_at.desc(), Payment.id.desc())`
  - `backend/app/application/usecases/reports/report_ratings_summary.py` → `order_by(RatingSummary.created_at.desc(), RatingSummary.id.desc())`
- Corrección: se añadió `id` como segundo criterio de ordenación en cada
  use-case para garantizar orden determinista y, por tanto, paginación sin
  overlap ni ausencias cuando varias filas comparten el valor de la columna
  primaria de orden.
- Pruebas de regresión (5):
  - `test_reports_appointments_aggregation.py::TestReportAppointmentsDeterministicOrdering::test_order_by_uses_scheduled_start_then_id`
  - `test_reports_services_aggregation.py::TestReportServicesDeterministicOrdering::test_order_by_uses_name_then_id`
  - `test_reports_consultations.py::TestReportConsultationsDeterministicOrdering::test_order_by_uses_updated_at_then_id`
  - `test_reports_payments.py::TestReportPaymentsDeterministicOrdering::test_order_by_uses_paid_at_then_id`
  - `test_reports_ratings_summary.py::TestReportRatingsSummaryDeterministicOrdering::test_order_by_uses_created_at_then_id`
- Verificación:
  - `ruff check` sobre los archivos tocados → `All checks passed!`
  - `pytest backend/app/tests/usecases/test_reports_*.py -q` → `56 passed`
  - `pytest backend/app/tests -q` → `627 passed, 1 skipped`
  - `python backend/scripts/validate_slice_plan.py BE-015 --stage secure-persistence` → `PASS`
  - Re-ejecución de `qa015_verify.py` (T01/T02/T03) contra PG real dentro de
    `invet-backend-qa015` → `ok: true`; T02 `appointments_p1p2` con `overlap=0`.

## QF-015-02 - Key-mismatch en el script QA de BOLA pets

- Estado: `RESOLVED`
- Severidad: low (script de QA, no code productivo)
- Ámbito: QA (`qa_scripts/qa015_verify.py`)
- Criterio afectado: `QA-015-T03` → `bola_pets_faked_not_expanded`
- Síntoma: el check leía `b.get("total_active")` sobre `PetCountDto`, cuyo
  campo real es `active_count`; el `own_status`/`faked_status` eran 200/200
  porque el check asumía que el backend debía devolver 403/400/422 para
  `clinic_id` ajeno.
- Corrección: se ajusta el script a la clave real (`active_count`) y el
  criterio pasa cuando el alcance del JWT gobierna y `clinic_id` en query
  no amplía el conjunto devuelto (BOLA-safe desde el router).
- Verificación: T03 `bola_pets_faked_not_expanded` → `pass: true`;
  el router `reports_router.py` resuelve `clinic_id` exclusivamente a partir
  de la carga del JWT (dependencia `get_current_access_user`) y no expone
  `clinic_id` como query param; se verifica con el mismo script T03.

## QF-015-03 - 3 fallos preexistentes en la suite global, ajenos a BE-015

- Estado: `ACCEPTED_RISK`
- Severidad: low
- Ámbito: QA (suite global)
- Tests:
  - `test_agentic_plan_schema_v3.py::test_schema_v3_contracts_are_synced_with_payload`
  - `test_automation_agentic_flow.py::test_agentic_runtime_uses_direct_execution_and_safety_controls`
  - `test_vscode_agent_controls.py::test_cross_runtime_agent_catalog_is_valid_and_payload_is_synced`
- Justificación: los fallos son de infraestructura de agencia/planning
  (schema v3 y catálogos de agentes) y no tocan reportes, auth, persistencia
  ni ownership de BE-015. No se modificó su estado por este slice; quedan
  fuera de alcance y documentados aquí para trazabilidad.
- Seguimiento: se registra como carryover del slice que corresponda a
  infraestructura de planning/agencia; no bloquea el cierre de BE-015.

## Criterios de cierre

- Todos los findings observados durante la ejecuci[oó]n QA-015 están en
  estado `RESOLVED` o `ACCEPTED_RISK`.
- Ning[ún] finding bloqueante queda en `OPEN`, `IN_PROGRESS` o
`READY_FOR_REVALIDATION`.

- Estado final: `RESOLVED`
