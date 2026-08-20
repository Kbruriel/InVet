---
manifest_version: 1
slice: "009"
layer: backend
generated_at: 2026-08-19T23:46:58+00:00
source_plan: docs/opencode/plans/BE-009-plan.md
source_plan_sha256: c767e142f4beb6c6e703e79223d2709261d2a6c438e28005a57f341b5c39e332
source_task: docs/opencode/tasks/backend/BE-009.md
source_task_sha256: 98baaae7d48a12692aea392b679de44ae8adeb35ce57062cd177bf7317301238
---

# BE-009 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-009.md`

## Archivos permitidos

- `backend/alembic/versions/**`
- `backend/app/api/schemas/consultation_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/consultation_router.py`
- `backend/app/application/use_cases/consultation_use_cases.py`
- `backend/app/domain/entities/consultation.py`
- `backend/app/domain/repositories/consultation_repository.py`
- `backend/app/infrastructure/database/models/consultation.py`
- `backend/app/infrastructure/repositories/consultation_repository_impl.py`
- `backend/app/tests/**`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-009-backend.json`
- `docs/opencode/manifests/BE-009-backend.md`
- `docs/opencode/plans/BE-009-plan.md`

## Tareas

### BE-009-T01 - PENDIENTE
- Tipo: contrato
- Criterio: AC-009-01, AC-009-06
- Objetivo: Definir entidad de dominio Consultation con constraint unique appointment_id.
- Depende de: Ninguna
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; matriz del slice; `backend/app/domain/entities/appointment.py` (referencia BE-008)
- Contratos: AC-009-01, AC-009-06
- Entregables: `backend/app/domain/entities/consultation.py`
- Aceptacion: Clase Consultation con campos completos (id, appointment_id unique, pet_id, clinic_id, branch_id, veterinarian_id, history, diagnosis, recommendations, created_by, updated_at). Validacion en entidad.
- Validacion: `python -c "from app.domain.entities.consultation import Consultation; print(Consultation.model_fields.keys())"` verifica campos.
- Resultado: Entidad de dominio disponible para contrato repositorio.

### BE-009-T02 - PENDIENTE
- Tipo: contrato
- Criterio: AC-009-01, AC-009-06
- Objetivo: Definir protocolo abstracto de repositorio con metodos create, get_by_id, list_by_pet, list_by_clinic.
- Depende de: BE-009-T01
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio creada en T01
- Contratos: AC-009-01, AC-009-06
- Entregables: `backend/app/domain/repositories/consultation_repository.py` (protocolo/interface)
- Aceptacion: Protocolo con metodos create, get_by_id, list_by_pet, list_by_clinic. Tipos bien definidos.
- Validacion: `python -c "from app.domain.repositories.consultation_repository import ConsultationRepository; print(ConsultationRepository.__abstractmethods__)"` lista metodos.
- Resultado: Contrato repositorio disponible para implementacion de infraestructura.

### BE-009-T03 - PENDIENTE
- Tipo: persistencia
- Criterio: AC-009-06, AC-009-14
- Objetivo: Crear modelo SQLAlchemy para tabla consultations con indices.
- Depende de: BE-009-T01
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio; ORM pattern de BE-008 (`backend/app/infrastructure/database/models/appointment.py`)
- Contratos: AC-009-06, AC-009-14
- Entregables: `backend/app/infrastructure/database/models/consultation.py`, migracion Alembic en `alembic/versions/`
- Aceptacion: Modelo mapea campos correctamente. Indices compuestos en (pet_id), (clinic_id). Unique sobre (appointment_id). Migracion reversible con downgrade.
- Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores.
- Resultado: Tabla consultations disponible en base de datos.

### BE-009-T04 - PENDIENTE
- Tipo: persistencia
- Criterio: AC-009-01, AC-009-06
- Objetivo: Implementar ConsultationRepository con logica de persistencia.
- Depende de: BE-009-T02, BE-009-T03
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; contrato repositorio; modelo ORM creado en T03
- Contratos: AC-009-01, AC-009-06
- Entregables: `backend/app/infrastructure/repositories/consultation_repository_impl.py`
- Aceptacion: Implementa create, get_by_id, list_by_pet, list_by_clinic. Paginacion funcional en list_by_* sin error.
- Validacion: `python -c "from app.infrastructure.repositories.consultation_repository_impl import ConsultationRepositoryImpl; print('OK')"` + revisar codigo.
- Resultado: Repositorio disponible para casos de uso.

### BE-009-T05 - PENDIENTE
- Tipo: caso de uso
- Criterio: AC-009-01, AC-009-02, AC-009-06, AC-009-11
- Objetivo: Implementar caso de uso create_consultation con validacion de negocio.
- Depende de: BE-009-T02, BE-009-T04
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; contrato repositorio; reglas de negocio (solo para completed)
- Contratos: AC-009-01, AC-009-02, AC-009-06, AC-009-11
- Entregables: `backend/app/application/use_cases/consultation_use_cases.py`
- Aceptacion: create_consultation valida appointment.status == completed. Valida rol veterinario por clinica. Errores consistentes (422 invalid input, 409 duplicate).
- Validacion: `pytest backend/app/tests/test_consultation_use_cases.py -q` con coverage >= 80%.
- Resultado: Casos de uso listos para consumo por routers.

### BE-009-T06 - PENDIENTE
- Tipo: contrato
- Criterio: AC-009-07, AC-009-10
- Objetivo: Definir schemas Pydantic de request para endpoint de consulta.
- Depende de: BE-009-T01
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; entidad de dominio; pattern schema de BE-008
- Contratos: AC-009-07, AC-009-10
- Entregables: `backend/app/api/schemas/consultation_schemas.py`
- Aceptacion: Schema ConsultationCreate con validacion de campos requeridos y rangos.
- Validacion: `python -c "from app.api.schemas.consultation_schemas import ConsultationCreate; print('OK')"` + revisar schemas.
- Resultado: Schemas validados disponibles para implementacion de endpoint.

### BE-009-T07 - PENDIENTE
- Tipo: api
- Criterio: AC-009-01, AC-009-02, AC-009-07, AC-009-10
- Objetivo: Exponer endpoint POST para creacion de consultas que responde 201.
- Depende de: BE-009-T05, BE-009-T06
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; caso de uso de T05; schemas de T06; pattern router de BE-008 (`backend/app/api/v1/routers/appointment_router.py`)
- Contratos: AC-009-01, AC-009-02, AC-009-07, AC-009-10
- Entregables: `backend/app/api/v1/routers/consultation_router.py` (POST), registro en main router.
- Aceptacion: POST responde 201 con datos de consulta creada. Valida Bearer auth.
- Validacion: `pytest backend/app/tests/api/test_consultations_api.py::test_create_consultation -q` → PASS.
- Resultado: Endpoint de creacion disponible para frontend clinico.

### BE-009-T08 - PENDIENTE
- Tipo: api
- Criterio: AC-009-04, AC-009-05, AC-009-09, AC-009-12
- Objetivo: Exponer endpoint GET de lista paginada.
- Depende de: BE-009-T06, BE-009-T07
- Contexto: `docs/opencode/tasks/backend/BE-009.md`; schemas; router pattern de BE-008
- Contratos: AC-009-04, AC-009-05, AC-009-09, AC-009-12
- Entregables: GET `/api/v1/consultations` con paginacion en router.
- Aceptacion: Listado responde con meta paginacion. Filtros de ownership funcionen. Router registrado en app/api/main.py.
- Validacion: `pytest backend/app/tests/api/test_consultations_api.py -q` con unauthenticated=401, authorized=200/201.
- Resultado: Contrato API completo y documentado (OpenAPI).

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
