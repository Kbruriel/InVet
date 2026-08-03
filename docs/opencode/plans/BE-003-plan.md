---
schema_version: 2
slice: "003"
canonical_plan: BE-003
status: DONE
---

# BE-003 Plan - Landing publica y busqueda

## Objetivo del slice

Consolidar la landing publica y la busqueda inicial para clinicas y sucursales, con contratos backend y frontend verificables, estados UI claros y evidencia QA reproducible.

## Alcance MVP

- Backend con contratos de clinicas y sucursales bajo `/api/v1`.
- Listados paginados y perfiles publicos/protegidos de sucursales.
- Frontend con landing publica, buscador inicial y estados vacio/error/exito.
- QA reproducible sobre el estado actual del repo y del stack de Docker.

## Fuera de alcance

- Marketplace, carrito, checkout, pasarela de pago, inventario o facturacion.
- Recomendaciones automaticas o analitica avanzada.
- Flujos de citas, auth o permisos fuera de lo necesario para el slice 003.

## Revision de gaps

- Este plan reemplaza el contrato legacy de BE-003/FE-003/QA-003, que no estaba en schema v2.
- QA-002 debe estar aprobado explicitamente antes de iniciar QA-003.
- La evidencia debe distinguir entre bloqueos reales y resultados stale.

## Entidades y reglas de negocio

- **Clinic**: entidad administrativa con pagina de detalle y listado paginado.
- **Branch**: sucursal asociada a una clinica.
- **Public branch profile**: expone solo datos publicos de una sucursal.
- **Protected branch profile**: requiere autenticacion para la vista administrativa.
- **Landing public**: permite buscar por texto y categoria sin exponer modelos ORM.

## Endpoints esperados

Contratos esperados bajo `/api/v1`.

- `GET /api/v1/clinics`
- `POST /api/v1/clinics`
- `GET /api/v1/clinics/{clinic_id}`
- `PUT /api/v1/clinics/{clinic_id}`
- `DELETE /api/v1/clinics/{clinic_id}`
- `GET /api/v1/clinics/branches/{branch_id}`
- `GET /api/v1/clinics/{clinic_id}/{branch_id}`
- `GET /api/v1/branches`
- `POST /api/v1/branches`
- `GET /api/v1/branches/{branch_id}`
- `PUT /api/v1/branches/{branch_id}`
- `DELETE /api/v1/branches/{branch_id}`
- `GET /api/v1/branches/{branch_id}/hours`
- `POST /api/v1/branches/{branch_id}/hours`
- `PUT /api/v1/branches/{branch_id}/hours/{hour_id}`
- `DELETE /api/v1/branches/{branch_id}/hours/{hour_id}`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /` para el shell public de entrada.
- `GET /clinicas` para la busqueda publica inicial.
- Rutas publicas sin autenticacion para explorar la landing.
- La navegacion debe mantener los query params de busqueda y categoria.

### Flujos y estados UX

- Estado inicial con contenido visible y CTA claros.
- Estado de busqueda con filtros por texto y categoria.
- Estado vacio cuando no hay coincidencias.
- Estado de error cuando la fuente de datos no esta disponible.
- Estado de exito cuando existen resultados.

### Contratos API por accion

- El explorador publico consume la coleccion de clinicas y sucursales definida por el slice.
- El perfil publico de sucursal usa `GET /api/v1/clinics/branches/{branch_id}`.
- El detalle protegido usa `GET /api/v1/clinics/{clinic_id}/{branch_id}`.
- El shell actual usa `mockClinics` como dataset local mientras se valida el contrato extremo a extremo.

### Formularios y validacion

- La busqueda recorta espacios al inicio y al final.
- La categoria se normaliza antes de filtrar.
- Los mensajes de error deben ser claros y no filtrar detalles internos.

### Arquitectura de componentes

- `frontend/src/app/clinicas/page.tsx` para el shell de busqueda publica.
- `frontend/src/features/public-landing/components/clinic-card.tsx` para tarjetas de clinica.
- `frontend/src/shared/layout/public-shell.tsx` para el marco visual.
- `frontend/src/shared/ui/state-panel.tsx` para estados vacio y error.

### Responsive y accesibilidad

- La grilla debe adaptarse a mobile, tablet y desktop.
- Los elementos interactivos deben conservar nombres y roles accesibles.
- Los estados vacio/error deben ser legibles sin depender de color solamente.

### Estrategia de pruebas frontend

- Pruebas de componente para la landing, tarjetas y estados de UI.
- Lint, typecheck, test y build como regresion del slice.
- Evidencia de build estable antes de cerrar QA.

## Pruebas QA

- Happy path de landing y busqueda publica.
- Negative path para busquedas vacias o sin coincidencias.
- Permisos por rol en el detalle protegido.
- IDOR/BOLA cuando se accede a sucursales ajenas.
- Regresion del flujo principal de landing y consulta.

## Riesgos de seguridad/IDOR/BOLA

- No exponer modelos ORM en respuestas.
- No revelar trazas internas en errores HTTP.
- Mantener datos publicos y protegidos separados.
- Evitar que un ID ajeno devuelva informacion administrativa.

## Checklist tecnico

### Backend

- [x] Rutas backend definidas para clinics, branches y branch hours.
- [x] Contratos request/response documentados con schemas Pydantic.
- [x] El endpoint publico de sucursal no expone datos sensibles.
- [x] Los listados responden con paginacion y errores consistentes.
- [x] Las pruebas backend cubren happy path y negative path.

### Frontend

- [x] Landing publica y buscador inicial implementados.
- [x] Componentes publicos reutilizables integrados.
- [x] Estados vacio, error, exito y responsive cubiertos.
- [x] Pruebas y build del frontend pasan en la corrida actual.

### QA

- [x] QA-002 esta aprobado explicitamente antes de QA-003.
- [x] La validacion del slice usa evidencia actual y no un baseline stale.
- [x] La corrida de checks actual pasa en backend, frontend y Docker.

## Checklist de tareas

### Backend

- [x] BE-003-T01 - Normalizar contratos publicos y administrativos de clinics
  Capa: backend
  Objetivo: Definir y consolidar los endpoints de clinics, branches y hours con respuestas consistentes.
  Depende de: Ninguna
  Entregables: backend/app/api/clinic_router.py; backend/app/api/schemas/clinic_schemas.py; use cases y pruebas asociadas.
  Criterios de aceptacion: Existen rutas publicas y administrativas documentadas; las respuestas no exponen ORM; los errores son consistentes y los listados son paginados.
  Validacion: python -m pytest app/tests/test_clinic_api.py -q
  Evidencia: `python -m pytest app/tests/test_clinic_api.py -q` -> 18 passed
  Paralelismo[P]: No

- [x] BE-003-T02 - Aislar persistencia y fixtures para pruebas publicas
  Capa: backend
  Objetivo: Garantizar que las pruebas del slice puedan ejecutarse sobre PostgreSQL sin depender de datos residuales.
  Depende de: BE-003-T01
  Entregables: backend/app/tests/conftest.py; backend/app/infrastructure/database/bootstrap.py; fixtures y seeds de prueba.
  Criterios de aceptacion: La suite corre contra un esquema aislado; branch_id=1 y clinic_id=1 existen para las rutas del slice; no hay colisiones entre ejecuciones.
  Validacion: python -m pytest app/tests -q
  Evidencia: `python -m pytest app/tests -q` -> 191 passed; `run-checks.ps1` -> backend pytest, ruff, black y mypy en pass
  Paralelismo[P]: Si

### Frontend

- [x] FE-003-T01 - Construir landing publica y buscador inicial
  Capa: frontend
  Objetivo: Entregar la pagina publica del slice con tarjetas, busqueda y query params.
  Depende de: BE-003-T01
  Entregables: frontend/src/app/clinicas/page.tsx; frontend/src/features/public-landing/components/clinic-card.tsx; shell public y dataset local.
  Criterios de aceptacion: La ruta publica muestra resultados, vacio y estados basicos; la busqueda filtra por texto y categoria; el shell funciona en desktop y mobile.
  Validacion: npm test -- --run
  Evidencia: `npm test -- --run` -> 25 files / 36 tests passed
  Paralelismo[P]: No

- [x] FE-003-T02 - Consolidar estados visuales y accesibilidad del explorador
  Capa: frontend
  Objetivo: Asegurar que el explorador publico conserve estados visuales, accesibilidad y build estable.
  Depende de: FE-003-T01
  Entregables: frontend/src/shared/layout/public-shell.tsx; frontend/src/shared/ui/state-panel.tsx; tests de componente.
  Criterios de aceptacion: Los estados vacio/error/exito son legibles y accesibles; el build de produccion no falla; no se introducen enlaces rotos en el flujo.
  Validacion: npm run build
  Evidencia: `npm run build` -> PASS; `run-checks.ps1` -> frontend lint, typecheck, test y build en pass
  Paralelismo[P]: Si

### QA

- [x] QA-003-T01 - Revalidar el slice 003 con evidencia actual
  Capa: qa
  Objetivo: Confirmar que la implementacion actual del slice 003 es verificable y que el reporte stale queda reemplazado.
  Depende de: BE-003-T01, BE-003-T02, FE-003-T01, FE-003-T02
  Entregables: docs/opencode/qa/QA-003-results.md; trazabilidad por criterio; decision final.
  Criterios de aceptacion: El plan valida en modo QA; QA-002 aparece aprobado; backend y frontend pasan sus regresiones; no hay bloqueo por infraestructura.
  Validacion: python backend/scripts/validate_slice_plan.py QA-003 --stage qa
  Evidencia: `python backend/scripts/validate_slice_plan.py QA-003 --stage qa` -> PASS; `run-checks.ps1` -> all checks pass y hook Docker ejecutado
  Paralelismo[P]: No

## Definition of Done

- [x] Backend, frontend y QA del slice 003 tienen contrato v2.
- [x] QA-002 se reconoce como aprobado en el gate previo.
- [x] La evidencia del slice 003 es actual y reproducible.
- [x] No quedan contradicciones entre plan, resultados y estado del repo.
