---
manifest_version: 1
slice: "014"
layer: qa
generated_at: 2026-09-02T01:17:03+00:00
source_plan: docs/opencode/plans/BE-014-plan.md
source_plan_sha256: 9e3e90dab12778e6b744a7c181f6e11a8ba381f82567ebce75e6d6f1dbe3b00c
source_task: docs/opencode/tasks/qa/QA-014.md
source_task_sha256: 8f125c8f15fcb8ebc4350d779b50da4f0bb7786bd586ff727d7ff028c0f154af
---

# BE-014 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-014.md`

## Archivos permitidos

- `backend/alembic/versions/a014_support.py`
- `backend/app/tests/**`
- `backend/app/tests/api/test_support_ticket_api.py`
- `backend/app/tests/data/test_support_ticket_repo.py`
- `backend/app/tests/usecases/test_support_ticket_rules.py`
- `backend/tests/api/test_support_ticket_migration.py`
- `docs/opencode/checkpoints/BE-014-qa.json`
- `docs/opencode/manifests/BE-014-qa.md`
- `docs/opencode/plans/BE-014-plan.md`
- `docs/opencode/qa/**`

## Tareas

### QA-014-T01 - COMPLETADA
- Tipo: qa
- Criterio: AC-01, AC-02, AC-05
- Objetivo: Confirmar reglas de tickets.
- Depende de: BE-014-T04
- Contexto: API desplegable con datos aislados.
- Contratos: Creación, categorías y estados.
- Entregables: `backend/app/tests/api/test_support_ticket_api.py`, `backend/app/tests/data/test_support_ticket_repo.py` y `backend/app/tests/usecases/test_support_ticket_rules.py`.
- Aceptacion: Límites, duplicados y transiciones están cubiertos.
- Validacion: Ejecutar suite API.
- Resultado: Reglas verificadas con evidencia.

### QA-014-T02 - COMPLETADA
- Tipo: prueba
- Criterio: AC-03, AC-06, AC-10
- Objetivo: Confirmar migración reversible.
- Depende de: BE-014-T01
- Contexto: Base de datos efímera.
- Contratos: Esquema persistente de soporte.
- Entregables: `backend/tests/api/test_support_ticket_migration.py` y migración `backend/alembic/versions/a014_support.py`.
- Aceptacion: Aplicar y revertir mantiene la integridad esperada.
- Validacion: Ejecutar migración hacia adelante y atrás.
- Resultado: Persistencia apta para despliegue.

### QA-014-T03 - COMPLETADA
- Tipo: seguridad
- Criterio: AC-07, AC-11
- Objetivo: Confirmar seguridad de tickets.
- Depende de: BE-014-T04
- Contexto: Usuarios de dos clínicas y un actor interno.
- Contratos: Lectura, listado y cambio de estado.
- Entregables: Casos de autorización en `backend/app/tests/api/test_support_ticket_api.py` y `backend/app/tests/data/test_support_ticket_repo.py`.
- Aceptacion: Ningún actor accede a recursos fuera de autorización.
- Validacion: Ejecutar matriz de autorización.
- Resultado: Aislamiento demostrado por pruebas.

### QA-014-T04 - COMPLETADA
- Tipo: prueba
- Criterio: AC-08, AC-09
- Objetivo: Confirmar experiencia de soporte.
- Depende de: FE-014-T02, FE-014-T03
- Contexto: Interfaz conectada a respuestas simuladas.
- Contratos: Estados UX y validación de formulario.
- Entregables: Pruebas frontend de `frontend/src/app/support` y `frontend/src/features/support/ui`.
- Aceptacion: Carga, vacío, error y validación son comprensibles.
- Validacion: Ejecutar pruebas frontend.
- Resultado: Flujo usable por teclado y lector de pantalla.

## Brief de capa

## Objetivo
Validar estados y acceso por rol.
## Dependencias
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
