---
manifest_version: 1
slice: "010"
layer: backend
generated_at: 2026-08-22T20:31:02+00:00
source_plan: docs/opencode/plans/BE-010-plan.md
source_plan_sha256: af794d2bbdf8683f4a31f941baae267569ca8d2fb817dcbfa6a27a487371887e
source_task: docs/opencode/tasks/backend/BE-010.md
source_task_sha256: a127e99380ca0cae781f37f4ce1325ecd98fc08acbc53116f8e000df49b26e17
---

# BE-010 - manifiesto compacto backend

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/backend/BE-010.md`

## Archivos permitidos

- ``
- `backend/alembic/versions/a010_prescriptions.py`
- `backend/app/api/schemas/prescription_schemas.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/routers/prescription_router.py`
- `backend/app/application/use_cases/prescription_use_cases.py`
- `backend/app/domain/entities/prescription.py`
- `backend/app/domain/repositories/prescription_repository.py`
- `backend/app/infrastructure/database/models/prescription.py`
- `backend/app/infrastructure/database/repositories/prescription_repository_impl.py`
- `backend/app/tests/**`
- `backend/tests/**`
- `docs/opencode/checkpoints/BE-010-backend.json`
- `docs/opencode/manifests/BE-010-backend.md`
- `docs/opencode/plans/BE-010-plan.md`

## Tareas

### BE-010-T01 - COMPLETADA
- Tipo: contrato
- Criterio: AC-010-01
- Objetivo: Definir entidades de prescripcion (item, tratamiento, recordatorio) como parte del dominio.
- Depende de: Ninguna
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/domain/entities/consultation.py` (referencia BE-009); `docs/opencode/references/backend_clean_architecture.md`
- Contratos: AC-010-01
- Entregables: `backend/app/domain/entities/prescription.py`
- Aceptacion: Entidades Prescription, PrescriptionItem, PrescriptionTreatment, PrescriptionReminder con campos completos; validacion de relaciones en entidad.
- Validacion: `python -c "from app.domain.entities.prescription import Prescription; print(Prescription.model_fields.keys())"` verifica campos.
- Resultado: Entidades de dominio disponibles para contratos de repositorio.

### BE-010-T02 - COMPLETADA
- Tipo: contrato
- Criterio: AC-010-01, AC-010-07
- Objetivo: Definir protocolo de repositorio con crear, obtener, listar por mascota.
- Depende de: BE-010-T01
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; entidad de T01; `backend/app/domain/repositories/consultation_repository.py` (referencia)
- Contratos: AC-010-01, AC-010-07
- Entregables: `backend/app/domain/repositories/prescription_repository.py`
- Aceptacion: Protocolo con metodos create, get_by_id, list_by_pet, exists_by_consultation. Tipos bien definidos.
- Validacion: `python -c "from app.domain.repositories.prescription_repository import PrescriptionRepository; print(1)"` sin error de import.
- Resultado: Contrato de repositorio disponible para implementacion.

### BE-010-T03 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-010-07, AC-010-14
- Objetivo: Crear modelos ORM de recetas con unique consultation_id e indices.
- Depende de: BE-010-T01
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/infrastructure/database/models/consultation.py`; `backend/alembic/versions/a009_consultations.py`
- Contratos: AC-010-07, AC-010-14
- Entregables: `backend/app/infrastructure/database/models/prescription.py`; migracion `backend/alembic/versions/a010_prescriptions.py`
- Aceptacion: Cuatro tablas mapeadas; unique sobre `consultation_id`; FK a consultation, pet, clinic; indices en `pet_id` y `created_at`; migracion reversible.
- Validacion: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` sin errores.
- Resultado: Tablas de recetas disponibles en base de datos.

### BE-010-T04 - COMPLETADA
- Tipo: persistencia
- Criterio: AC-010-01, AC-010-07
- Objetivo: Implementar repositorio ORM con creacion atomica de recetas.
- Depende de: BE-010-T02, BE-010-T03
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; contrato de T02; modelo ORM de T03
- Contratos: AC-010-01, AC-010-07
- Entregables: `backend/app/infrastructure/database/repositories/prescription_repository_impl.py`
- Aceptacion: Implementa create (atomico), get_by_id, list_by_pet con paginacion, exists_by_consultation. Sin error de import.
- Validacion: `python -c "from app.infrastructure.database.repositories.prescription_repository_impl import PrescriptionRepositoryImpl; print(1)"`.
- Resultado: Repositorio disponible para casos de uso.

### BE-010-T05 - COMPLETADA
- Tipo: caso de uso
- Criterio: AC-010-01, AC-010-02, AC-010-07
- Objetivo: Implementar create_prescription atomico con validacion de consulta completed.
- Depende de: BE-010-T02, BE-010-T04
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; reglas: consulta completed, unica por consulta, solo clinica del token
- Contratos: AC-010-01, AC-010-02, AC-010-07
- Entregables: `backend/app/application/use_cases/prescription_use_cases.py`
- Aceptacion: create_prescription valida existencia de consulta y `status=completed`; valida rol clinico por clinica; 422 invalid, 409 duplicate; read y list by pet.
- Validacion: `pytest backend/app/tests/test_prescription_use_cases.py -q` con coverage >= 80%.
- Resultado: Casos de uso listos para consumo por routers.

### BE-010-T06 - COMPLETADA
- Tipo: contrato
- Criterio: AC-010-01, AC-010-02
- Objetivo: Definir schemas Pydantic de prescripciones de request para la API.
- Depende de: BE-010-T01
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; `backend/app/api/schemas/consultation_schemas.py` (referencia)
- Contratos: AC-010-01, AC-010-02
- Entregables: `backend/app/api/schemas/prescription_schemas.py`
- Aceptacion: PrescriptionCreate con validacion de campos, items, tratamientos, recordatorios; PrescriptionRead; PrescriptionPage(items, meta).
- Validacion: `python -c "from app.api.schemas.prescription_schemas import PrescriptionCreate; print(1)"` + revisar validaciones.
- Resultado: Schemas validados disponibles para endpoints.

### BE-010-T07 - COMPLETADA
- Tipo: api
- Criterio: AC-010-01, AC-010-10
- Objetivo: Exponer POST de creacion de receta que responde 201 con Bearer.
- Depende de: BE-010-T05, BE-010-T06
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; caso de uso de T05; schemas de T06; `backend/app/api/v1/routers/consultation_router.py` (referencia)
- Contratos: AC-010-01, AC-010-10
- Entregables: `backend/app/api/v1/routers/prescription_router.py` (POST); registro en main router
- Aceptacion: POST responde 201 con receta completa; 401 sin token; 403 rol; 422 invalido; 409 duplicado.
- Validacion: `pytest backend/app/tests/api/test_prescriptions_api.py::test_create_prescription -q` → PASS.
- Resultado: Endpoint de creacion disponible para frontend clinico.

### BE-010-T08 - COMPLETADA
- Tipo: seguridad
- Criterio: AC-010-08, AC-010-09, AC-010-10
- Objetivo: Restringir creacion de recetas al veterinario de la clinica.
- Depende de: BE-010-T07
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; `_require_write_role` de BE-009; riesgos IDOR/BOLA del plan
- Contratos: AC-010-08, AC-010-09, AC-010-10
- Entregables: Aplicar `_require_write_role` y validacion de ownership por `clinic_id`/`pet_id` en `backend/app/api/v1/routers/prescription_router.py` y use case
- Aceptacion: 403 a propietario al crear; 403 a veterinario de otra clinica; 404/403 al leer receta ajena; 401 sin token en todos los endpoints.
- Validacion: `pytest backend/app/tests/api/test_prescriptions_idor.py -q` y `test_prescriptions_auth.py` → PASS.
- Resultado: Permisos y ownership sin hallazgos de seguridad.

### BE-010-T09 - COMPLETADA
- Tipo: api
- Criterio: AC-010-04, AC-010-05, AC-010-09
- Objetivo: Exponer GET de detalle de receta con validacion de ownership.
- Depende de: BE-010-T06, BE-010-T07
- Contexto: `docs/opencode/tasks/backend/BE-010.md`; schemas de T06; router de T07
- Contratos: AC-010-04, AC-010-05, AC-010-09
- Entregables: GET `/api/v1/prescriptions/{id}` y GET `/api/v1/prescriptions?pet_id=` en `prescription_router.py`
- Aceptacion: Detalle 200 con items, tratamientos, recordatorios; listado 200 con meta de paginacion; 404 receta ajena; 401 sin token.
- Validacion: `pytest backend/app/tests/api/test_prescriptions_api.py -q` con 401/403/404 y 200.
- Resultado: Contrato API de lectura completo y documentado (OpenAPI).

## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
