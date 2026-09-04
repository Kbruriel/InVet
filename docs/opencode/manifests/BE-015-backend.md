---
manifest_version: 1
slice: "015"
layer: backend
generated_at: 2026-09-03T17:16:28+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: 4fa0fe7d2045859d27b217d05a7f1452f2c943e43365e347f157c5fce7a94c3c
source_task: docs/opencode/tasks/backend/BE-015.md
source_task_sha256: e83b59d332d0d70ba7a699f237f9fc83a137a0c2658f7169735b4f514fc021c3
---

# BE-015 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-015.md`

## Archivos permitidos

- `backend/app/api/v1/routers/reports_router.py`
- `backend/app/api/v1/schemas/report_schemas.py`
- `backend/app/application/usecases/reports/report_appointments.py`
- `backend/app/application/usecases/reports/report_consultations.py`
- `backend/app/application/usecases/reports/report_payments.py`
- `backend/app/application/usecases/reports/report_pets_count.py`
- `backend/app/application/usecases/reports/report_ratings_summary.py`
- `backend/app/application/usecases/reports/report_services.py`
- `backend/app/main.py`
- `backend/app/tests/**`
- `backend/app/tests/integration/test_reports_auth.py`
- `backend/app/tests/integration/test_reports_integration.py`
- `backend/app/tests/integration/test_reports_invalid_input.py`
- `backend/app/tests/integration/test_reports_tenant_isolation.py`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-015-backend.json`
- `docs/opencode/manifests/BE-015-backend.md`
- `docs/opencode/plans/BE-015-plan.md`

## Tareas

### BE-015-T01 - COMPLETADA
- Tipo: contrato
- Criterio: AC-015-03, AC-015-04
- Objetivo: Definir DTOs Pydantic para reportes.
- Depende de: Ninguna
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; contratos Endpoints esperados del plan; esquemasBE-008, BE-011, BE-012.
- Contratos: endpoints esperados del plan.
- Entregables: `backend/app/api/v1/schemas/report_schemas.py` con seis clases Pydantic (AppointmentSummaryDto, ServiceSummaryDto, PetCountDto, ConsultationSummaryDto, RatingSummaryDto, PaymentSummaryDto).
- Aceptacion: El modulo importa sin errores. Validacion pydantic pasa para payload dummy valido. Ningun campo expone datos personales completos.
- Validacion: `python -m ruff check backend/app/api/v1/schemas/report_schemas.py`; `python -c "from app.api.v1.schemas.report_schemas import *"` importa sin excepcion.
- Resultado: Modulo de esquemas Pydantic listo.

### BE-015-T02 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-03
- Objetivo: Consultar citas paginadas reutilizando repositorio BE-008.
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork en `backend/app/infrastructure/database/unit_of_work.py`; repos Appointment (BE-008).
- Contratos: schema AppointmentSummaryDto; criterio AC-015-03.
- Entregables: `backend/app/application/usecases/reports/report_appointments.py`.
- Aceptacion: Funcion consume UnitOfWork y retorna Lista[AppointmentSummaryDto]. Filtros period_start/period_end aplicados correctamente. No persiste datos nuevos.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_appointments_aggregation.py -q --timeout=30`.
- Resultado: Caso de uso citas disponible como funcion pura verificable.

### BE-015-T03 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-04
- Objetivo: Consultar servicios paginados reutilizando repositorio BE-006.
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Service (BE-006).
- Contratos: schema ServiceSummaryDto; criterio AC-015-04.
- Entregables: `backend/app/application/usecases/reports/report_services.py`.
- Aceptacion: Funcion retorna Lista[ServiceSummaryDto]. Filtros aplicados correctamente.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_services_aggregation.py -q --timeout=30`.
- Resultado: Caso de uso servicios disponible como funcion pura.

### BE-015-T04 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-05
- Objetivo: Contar mascotas activas reutilizando repositorio BE-007.
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Pet (BE-007).
- Contratos: schema PetCountDto; criterio AC-015-05.
- Entregables: `backend/app/application/usecases/reports/report_pets_count.py`.
- Aceptacion: Funcion retorna integer con conteo activo por clinic_id y periodo. No persiste datos nuevos.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_pets_count.py -q --timeout=30`.
- Resultado: Caso de uso mascotas disponible como funcion pura.

### BE-015-T05 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-06
- Objetivo: Listar consultas paginadas reutilizando repositorio BE-009.
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Consultation (BE-009).
- Contratos: schema ConsultationSummaryDto; criterio AC-015-06.
- Entregables: `backend/app/application/usecases/reports/report_consultations.py`.
- Aceptacion: Funcion retorna Lista[ConsultationSummaryDto]. Filtros aplicados correctamente.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_consultations_aggregation.py -q --timeout=30`.
- Resultado: Caso de uso consultas disponible como funcion pura.

### BE-015-T06 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-07
- Objetivo: Consultar promedio de ratings reutilizando repositorio BE-012.
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos rating_summary (BE-012).
- Contratos: schema RatingSummaryDto; criterio AC-015-07.
- Entregables: `backend/app/application/usecases/reports/report_ratings_summary.py`.
- Aceptacion: Funcion retorna lista by_veterinarian con avg_rating. No persiste datos nuevos.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_ratings_aggregation.py -q --timeout=30`.
- Resultado: Caso de uso ratings disponible como funcion pura.

### BE-015-T07 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-015-08
- Objetivo: Consultar pagos paginados reutilizando repositorio Payment (BE-011).
- Depende de: BE-015-T01
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; UnitOfWork; repos Payment (BE-011).
- Contratos: schema PaymentSummaryDto; criterio AC-015-08.
- Entregables: `backend/app/application/usecases/reports/report_payments.py`.
- Aceptacion: Funcion retorna Lista[PaymentSummaryDto] con totales y campos resumidos.
- Validacion: `python -m pytest backend/app/tests/usecases/test_reports_payments_aggregation.py -q --timeout=30`.
- Resultado: Caso de uso pagos disponible como funcion pura.

### BE-015-T08 - COMPLETADA
- Tipo: api
- Criterio: AC-015-03, AC-015-04
- Objetivo: Crear router con prefijo api-v1-reports.
- Depende de: BE-015-T02, BE-015-T03, BE-015-T04, BE-015-T05, BE-015-T06, BE-015-T07
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; FastAPI app registration en `backend/app/main.py`; schemas report_schemas.py.
- Contratos: contratos API por accion del plan; esquemas de reportes.
- Entregables: archivo `backend/app/api/v1/routers/reports_router.py` con prefix /api/v1/reports/. Archivo `backend/app/main.py` actualizado con include_router adicional.
- Aceptacion: Endpoints GET devuelven JSON estructurado correctamente en todos los tipos de reporte. Paginacion respetada donde corresponde. Sin logica de negocio en el router.
- Validacion: `python -m pytest backend/app/tests/integration/test_reports_router.py -q --timeout=30`; `alembic current` muestra sin nuevas migraciones pending.
- Resultado: Endpoints /api/v1/reports/* listos para consumo HTTP.

### BE-015-T09 - COMPLETADA
- Tipo: seguridad
- Criterio: AC-015-11, AC-015-09
- Objetivo: Verificar que solo se acceden datos propios por Clinica JWT.
- Depende de: BE-015-T02
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; fixtures multi-tenant; autentificacion JWT en `backend/app/core/security.py`.
- Contratos: criterios AC-015-09 y AC-015-11.
- Entregables: archivo `backend/app/tests/integration/test_reports_tenant_isolation.py` con usuarios dos clinicas diferentes. Archivo `backend/app/tests/integration/test_reports_auth.py`.
- Aceptacion: Sin token retorna 401. Token de Clinica A no expone datos de Clinica B. Campo clinic_id request acota scope sin amplfiarlo mas alla del token. Token expirado retorna 401.
- Validacion: `python -m pytest backend/app/tests/integration/test_reports_tenant_isolation.py backend/app/tests/integration/test_reports_auth.py -q --timeout=30`.
- Resultado: Proteccion tenant asegurada y comprobada por tests.

### BE-015-T10 - COMPLETADA
- Tipo: prueba
- Criterio: AC-015-03, AC-015-05, AC-015-10
- Objetivo: Comprobar contract endpoint eliminando tipos invalidos del reporte.
- Depende de: BE-015-T08
- Contexto: `docs/opencode/tasks/backend/BE-015.md`; HTTPX client fixture; schema respuesta plan; router reports_router.py resultado de T08.
- Contratos: contratos API endpoints del plan.
- Entregables: archivo `backend/app/tests/integration/test_reports_integration.py` parametrizado por tipo reporte. Archivo `backend/app/tests/integration/test_reports_invalid_input.py`.
- Aceptacion: Cada endpoint retorna al menos un caso positivo 200 valido. invalid report_type genera codigo 422. period_start mayor que period_end genera codigo 422. Paginacion respeta page_size.
- Validacion: `python -m pytest backend/app/tests/integration/test_reports_integration.py backend/app/tests/integration/test_reports_invalid_input.py -q --timeout=60`.
- Resultado: Contrato HTTP verificado en todos los endpoints expuestos al frontend.

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
