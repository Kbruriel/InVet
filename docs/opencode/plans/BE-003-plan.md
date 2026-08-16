---
schema_version: 3
slice: "003"
canonical_plan: BE-003
status: COMPLETED
encoding: UTF-8
---

# BE-003 Plan - Landing pública y búsqueda

## Objetivo del slice

Endpoints públicos de clínicas, servicios, sucursales, filtros y paginación para permitir búsqueda anónima.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Landing pública y búsqueda |
| Descripcion | Permitir busqueda anonima de clinicas, sucursales y servicios con filtros publicos |
| Entregables backend | Endpoints publicos de busqueda, filtros, paginacion, DTOs publicos, repositorios y pruebas de listados |
| Entregables frontend | Landing, buscador, filtros/chips, resultados, estados loading/error/empty/success y query params |
| Criterios QA principales | Busqueda anonima funciona; filtros y paginacion consistentes; datos privados no se exponen; UI responde en mobile/desktop |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Implementar únicamente capacidades necesarias para el slice `003`.
- Exponer contratos bajo `/api/v1`.
- Mantener separación API/Application/Domain/Infrastructure/Core.
- Agregar pruebas automatizadas aplicables.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal.
- Automatizaciones avanzadas o analítica avanzada salvo que este slice sea de hardening y solo como preparación documental.

## Suposiciones

- BE-002 (autenticacion) ya esta cerrado y los modelos de usuario/rol/clinica existen.
- Los datos publicos de clinicas/sucursales/servicios no requieren autenticacion.
- La paginacion usa offset/limit como estrategia MVP.

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, BE-003.md, FE-003.md, QA-003.md
- Gap: No se especifican entidades exactas de Clinica/Sucursal/Servicio en este plan; se asume que existen o se crean como parte de BE-003.
- Decision: Crear modelos minimos de Clinica, Sucursal y Servicio si no existen; exponer solo campos publicos via DTOs.
- Impacto en tareas: Tareas de dominio e infraestructura agregadas para entidades publicas.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Clinica (publica) | BE-003, FE-003 | Modelo con campos publicos; endpoint de listados y detalle | Repositorio + DTO sin datos sensibles |
| Sucursal (publica) | BE-003, FE-003 | Modelo con campos publicos; filtro por clinica | Repositorio + endpoint con paginacion |
| Servicio (publico) | BE-003, FE-003 | Modelo con precio/base; filtro por sucursal/clinica | Endpoint con filtros combinados |
| Busqueda publica | QA-003 | Filtros combinados + paginacion | Endpoints validan filtros y paginacion |
| Ownership/tenant | BE-002, QA-003 | Datos publicos no filtran informacion privada | Pruebas IDOR/BOLA en listados |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-003.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-003.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-003.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| AC-003-01 | BE/FE/QA | Busqueda anonima de clinicas | BE-003-T01 | Endpoint publico lista clinicas con paginacion | 200 OK con datos publicos, sin auth | CLOSED |
| AC-003-02 | BE/FE/QA | Filtro por nombre/ubicacion | BE-003-T02 | Endpoint acepta query params de filtro | Filtros aplicados correctamente | CLOSED |
| AC-003-03 | BE/FE/QA | Listado de sucursales por clinica | BE-003-T03 | Endpoint sucursales con paginacion | Paginacion consistente | CLOSED |
| AC-003-04 | BE/FE/QA | Listado de servicios publicos | BE-003-T04 | Endpoint servicios con filtros | Filtros combinados funcionan | CLOSED |
| AC-003-05 | FE-003 | Landing publica con buscador | FE-003-T01 | UI consume endpoints publicos | Estados loading/error/empty/success | CLOSED |
| AC-003-06 | QA-003 | Datos privados no se exponen | QA-003 | Pruebas IDOR/BOLA en listados | 404 o datos filtrados correctamente | CLOSED |
| AC-003-07 | QA-003 | Responsive y estados UI | FE-003/QA-003 | UI responsive + estados visuales | Captura textual de UI | CLOSED |

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Listar clinicas | GET | /clinicas | None | ?page=1&limit=20&search= | PaginatedClinicsResponse | 422 invalid params |
| Detalle clinica | GET | /clinicas/{id} | None | - | PublicClinicDTO | 404 no encontrado |
| Listar sucursales | GET | /sucursales | None | ?clinica_id=X&search=Y | PaginatedSucursalesResponse | 422 invalid params |
| Listar servicios | GET | /servicios | None | ?sucursal_id=X&clinica_id=Y | PaginatedServiciosResponse | 422 invalid params |

## Contrato de implementacion frontend

### Rutas y acceso

- Ruta publica: `/` (landing) o `/clinicas` para listados.
- Sin autenticacion requerida.

### Flujos y estados UX

Debe cubrir `loading`, `submitting`, `error`, `empty` y `success` cuando apliquen.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Buscar clinicas | /api/v1/clinicas | GET | ?search= | PaginatedClinicsResponse | 422 | None |
| Ver detalle clinica | /api/v1/clinicas/{id} | GET | - | PublicClinicDTO | 404 | None |
| Filtrar sucursales | /api/v1/sucursales | GET | ?clinica_id= | PaginatedSucursalesResponse | 422 | None |
| Filtrar servicios | /api/v1/servicios | GET | ?sucursal_id= | PaginatedServiciosResponse | 422 | None |

### Formularios y validacion

- Buscador con debounce minimo.
- Chips de filtros como query params.

### Arquitectura de componentes

- Reutilizar componentes desde `src/shared/ui`.
- Centralizar API en `src/shared/api`.

### Responsive y accesibilidad

- Desktop y mobile responsive.
- Accesibilidad basica (ARIA labels, contraste).

### Estrategia de pruebas frontend

- Pruebas de componentes si el repo tiene framework configurado.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| Backend tests | `pytest backend/tests/ -v` | Host local con PostgreSQL contenedor | Tests pasan |
| Type check | `mypy backend/app/` | Entorno virtual | Sin errores nuevos |
| Lint | `ruff check backend/app/` | Entorno virtual | Sin violations |
| Frontend build | `npm run build --prefix frontend` | Node.js | Build limpio |
| Frontend lint | `npm run lint --prefix frontend` | Node.js | Sin errors |

## Plan de reportes y findings

- Reporte QA: `docs/opencode/reports/QA-003-results.md`
- Hallazgos QA: `docs/opencode/reports/QA-003-findings.md` (si aplica)
- Estado global de findings: `OPEN|IN_PROGRESS|READY_FOR_REVALIDATION|RESOLVED|ACCEPTED_RISK`

## Pruebas QA

- Happy path: busqueda anonima de clinicas con filtros y paginacion.
- Negative path: inputs invalidos, datos privados no expuestos.
- Permisos: endpoints publicos sin auth; protegidos con 401/403.
- IDOR/BOLA: acceso cruzado a sucursales de otras clinicas falla.
- Responsive: UI responde en mobile y desktop.

## Pruebas QA

- Happy path: busqueda anonima de clinicas con filtros y paginacion.
- Negative path: inputs invalidos, datos privados no expuestos.
- Permisos: endpoints publicos sin auth; protegidos con 401/403.
- IDOR/BOLA: acceso cruzado a sucursales de otras clinicas falla.
- Responsive: UI responde en mobile y desktop.

## Pruebas qa

Comandos de validacion:

- Backend: `pytest backend/app/tests/ -v --tb=short`
- Security: `pytest backend/app/tests/api/test_branch_profile_security.py -v`
- Type check: `mypy backend/app/`
- Lint: `ruff check backend/app/`
- Frontend build: `npm run build --prefix frontend`
- Frontend lint: `npm run lint --prefix frontend`

Criterios de aprobacion QA:

- Todos los tests de backend pasan sin errores.
- Pruebas de seguridad (IDOR/BOLA) pasan con 401/403 correctos.
- Endpoints publicos responden 200 sin autenticacion.
- Frontend build y lint sin errores.
- Evidencia documentada en QA-003-results.md.

## Riesgos de seguridad/idor/bola

| Riesgo | Mitigacion | Tarea validacion |
| --- | --- | --- |
| Exposicion datos privados en listados publicos | DTOs solo campos publicos; pruebas sin auth | QA-003 IDOR/BOLA |
| Filtros abiertos a datos internos | Validar que filtros publicos no acepten IDs privados | BE-003-T02/T03/T04 |
| Paginacion sin limites | Limit maximo en query params | BE-003-T01 |

## Politica utf-8

Todos los archivos de este slice se crean y modifican con encoding UTF-8. No se usan caracteres que puedan corromperse con codificaciones alternativas.

## Checklist tecnico

- [ ] Modelos de dominio para entidades publicas (Clinica, Sucursal, Servicio)
- [ ] Repositorios SQLAlchemy con soporte de paginacion
- [ ] DTOs Pydantic sin datos sensibles
- [ ] Routers FastAPI publicos en `/api/v1/`
- [ ] Migraciones Alembic si nuevas entidades
- [ ] Pruebas pytest/HTTPX para endpoints
- [ ] Filtros y paginacion validados
- [ ] Permisos/ownership/IDOR verificados
- [ ] OpenAPI consistente
- [ ] Sin alcance fuera del MVP

## Checklist de tareas

La lista canonica, el estado y la evidencia de cada tarea se mantienen en `Tareas planificadas`; no se duplica un segundo checklist resumido.

## Definition of done

- [x] Plan canonico creado con schema v3.
- [x] Modelo de dominio implementado.
- [x] Repositorios con paginacion implementados.
- [x] DTOs publicos sin datos sensibles.
- [x] Endpoints expuestos y documentados en OpenAPI.
- [x] Migraciones Alembic aplicadas o justificadas.
- [x] Pruebas backend pasan (68/68).
- [x] Permisos/ownership/IDOR validados.
- [x] Frontend implementado con estados UX completos.
- [x] QA valida happy path, negative path, permisos, IDOR/BOLA.
- [x] Reviews aprobadas (functional, clean architecture, security).
- [x] Checks pasan (lint, type check, build).
- [x] Documentacion actualizada.

## Tareas planificadas

### Backend tasks

- [x] BE-003-T01 - Modelos dominio Clinica/Sucursal/Servicio
  capa: backend
  tipo: persistencia
  historia o criterio: AC-003-01/AC-003-02
  objetivo: Definir entidades publicas de dominio con campos minimos
  responsabilidad unica: Si
  depende de: Ninguna
  contexto necesario: BE-003.md, domain entities existentes
  contratos usados: Clinic, Branch, Service entities
  entregables: Modelos ORM y value objects en domain/entities
  criterios de aceptacion: Entidades existen con campos publicos validos
  validacion: Inspeccion de modelos y migraciones Alembic
  resultado esperado: Modelos persisten datos publicos correctamente
  evidencia: Migraciones alembic history verificadas
  paralelismo[p]: No

- [x] BE-003-T02 - Repositorios con paginacion
  capa: backend
  tipo: persistencia
  historia o criterio: AC-003-01
  objetivo: Implementar repositorios con soporte de paginacion
  responsabilidad unica: Si
  depende de: BE-003-T01
  contexto necesario: Repository interfaces, SQLAlchemy patterns
  contratos usados: ClinicRepository, BranchRepository, ServiceRepository
  entregables: Repositorios con search_clinics y list_sucursales paginados
  criterios de aceptacion: Paginacion funciona con page/size validos
  validacion: Pruebas unitarias del repositorio con mocks
  resultado esperado: Listados devuelven datos paginados correctamente
  evidencia: test_clinic_repository.py pasa con paginacion
  paralelismo[p]: No

- [x] BE-003-T03 - DTOs publicos validaciones
  capa: backend
  tipo: contrato
  historia o criterio: AC-003-01
  objetivo: Crear DTOs Pydantic sin datos sensibles
  responsabilidad unica: Si
  depende de: BE-003-T01
  contexto necesario: Schemas existentes, slice_task_context.md
  contratos usados: ClinicSearchResponse, BranchPublicProfile
  entregables: Schemas Pydantic en api/v1/schemas/
  criterios de aceptacion: DTOs no exponen campos sensibles (password, internal_id)
  validacion: Inspeccion de schemas y pruebas de serializacion
  resultado esperado: DTOs serializan solo campos publicos
  evidencia: test_clinic_search.py valida schemas
  paralelismo[p]: No

- [x] BE-003-T04 - Routers FastAPI endpoints
  capa: backend
  tipo: api
  historia o criterio: AC-003-01
  objetivo: Exponer endpoints publicos de busqueda
  responsabilidad unica: Si
  depende de: BE-003-T02,BE-003-T03
  contexto necesario: Routers existentes, FastAPI patterns
  contratos usados: ClinicSearchResponse, BranchPublicProfile, OpenAPI spec
  entregables: public_clinics.py, public_branches.py, public_services.py registrados en v1
  criterios de aceptacion: Endpoints responden 200/404/422 correctamente sin auth
  validacion: Pruebas HTTPX con AsyncClient contra endpoints (15 contract tests)
  resultado esperado: API expone busqueda anonima funcional
  evidencia: test_public_clinics.py, test_public_branches.py, test_public_services.py pasan (15/15)
  paralelismo[p]: No
  estado: COMPLETED
  notas: Tests reescritos para httpx.AsyncClient porque endpoints son async

- [x] BE-003-T05 - Migraciones Alembic
  capa: backend
  tipo: persistencia
  historia o criterio: AC-003-01
  objetivo: Generar migraciones para nuevas tablas
  responsabilidad unica: Si
  depende de: BE-003-T01
  contexto necesario: alembic.ini, migration history existente
  contratos usados: Alembic migration commands
  entregables: Migraciones en alembic/versions/
  criterios de aceptacion: Migraciones aplican sin errores en PostgreSQL
  validacion: alembic upgrade head exitoso en entorno QA
  resultado esperado: Base de datos refleja esquema de entidades publicas
  evidencia: Migraciones existentes verificadas en alembic history
  paralelismo[p]: No
  estado: COMPLETED

- [x] BE-003-T06 - Pruebas backend seguridad
  capa: backend
  tipo: seguridad
  historia o criterio: AC-003-06
  objetivo: Validar que datos privados no se exponen
  responsabilidad unica: Si
  depende de: BE-003-T04
  contexto necesario: QA-003.md, IDOR/BOLA patterns
  contratos usados: Pruebas HTTPX con AsyncClient sin auth
  entregables: test_public_clinics.py, test_public_branches.py, test_public_services.py
  criterios de aceptacion: DTOs no exponen campos sensibles; datos cruzados no se filtran
  validacion: pytest app/tests/api/test_public_*.py (15/15 contract tests)
  resultado esperado: Todos los casos de seguridad pasan
  evidencia: 15 contract tests pasando, ruff/black/mypy clean
  paralelismo[p]: No
  estado: COMPLETED

### Frontend tasks

- [x] FE-003-T01 - Landing buscador UI
  capa: frontend
  tipo: componente
  historia o criterio: AC-003-05
  objetivo: Implementar landing publica con buscador
  responsabilidad unica: Si
  depende de: BE-003-T04
  contexto necesario: FE-003.md, frontend_visual_alignment.md
  contratos usados: ClinicSearchResponse endpoint
  entregables: page.tsx (landing), HeroSection, PublicSearchBar
  criterios de aceptacion: UI renderiza buscador y resultados iniciales
  validacion: Build Next.js exitoso; ESLint sin errores
  resultado esperado: Landing muestra buscador funcional conectado a API
  evidencia: npx next build PASS (9/9 pages), ESLint PASS
  paralelismo[p]: Si
  estado: COMPLETED

- [x] FE-003-T02 - Filtros resultados
  capa: frontend
  tipo: componente
  historia o criterio: AC-003-02
  objetivo: Implementar filtros con chips
  responsabilidad unica: Si
  depende de: FE-003-T01,BE-003-T04
  contexto necesario: FE-003.md, query params patterns
  contratos usados: Endpoints de busqueda con query params
  entregables: CategoryChips, ClinicsPage con paginacion
  criterios de aceptacion: Filtros actualizan query params y resultados
  validacion: Inspeccion visual de UI con filtros activos
  resultado esperado: Usuario puede filtrar y navegar paginacion
  evidencia: /clinicas?page=1&category=veterinaria funciona correctamente
  paralelismo[p]: Si
  estado: COMPLETED

- [x] FE-003-T03 - Estados UX responsive
  capa: frontend
  tipo: estado ux
  historia o criterio: AC-003-07
  objetivo: Implementar estados loading error empty success
  responsabilidad unica: Si
  depende de: FE-003-T01,FE-003-T02
  contexto necesario: FE-003.md, frontend_visual_alignment.md
  contratos usados: Estados UX pattern, Tailwind responsive classes
  entregables: ClinicsPage con loading/error/empty/success states
  criterios de aceptacion: UI responde en mobile/desktop; estados visibles
  validacion: Inspeccion responsive y build Next.js
  resultado esperado: Landing usable en desktop y mobile con feedback visual
  evidencia: npx next build PASS, TypeScript type check PASS
  paralelismo[p]: No
  estado: COMPLETED

### QA tasks

- [x] QA-003-T01 - Validacion completa slice
  capa: qa
  tipo: qa
  historia o criterio: QA-003.md completo
  objetivo: Validar busqueda anonima con filtros
  responsabilidad unica: Si
  depende de: BE-003-T06,FE-003-T03
  contexto necesario: QA-003.md, casos minimos QA
  contratos usados: Criterios de aceptacion QA-003
  entregables: docs/opencode/reports/QA-003-results.md, findings RESOLVED
  criterios de aceptacion: Happy path, negative path, permisos, IDOR/BOLA pasan
  validacion: Ejecucion de pruebas QA con evidencia documentada
  resultado esperado: Slice BE-003/FE-003 aprobado por QA
  evidencia: QA-003-results.md con decision APPROVED, findings RESOLVED
  paralelismo[p]: No
  estado: COMPLETED

## Resultados de Gates

| Gate | Estado | Evidencia |
|------|--------|-----------|
| QA-003 | ✅ APPROVED | 13/13 criteria PASS, 28 tests passing |
| Functional Review | ✅ APPROVED | docs/opencode/reviews/BE-003-review.md |
| Clean Architecture Review | ✅ APPROVED (re-revision) | docs/opencode/reviews/BE-003-clean-architecture-review.md |
| Security Review | ✅ APPROVED | docs/opencode/reviews/BE-003-security-review.md |
| UI Checks | ✅ APPROVED | UIA-003: 12/12 PASSED, total 24/29 PASSED |
| Technical Checks | ✅ APPROVED | 68/68 tests, ruff/black/mypy clean, frontend build OK |

## Evidencia de Implementacion

### Backend (BE-003)
- **Endpoints**: `/api/v1/clinicas`, `/api/v1/sucursales`, `/api/v1/servicios`
- **Tests**: 68 total (15 contract tests + 53 existentes)
- **Contract Tests**: 15/15 pasando (httpx.AsyncClient con ASGITransport)
- **Linting**: ruff PASS, black PASS, mypy PASS

### Frontend (FE-003)
- **Paginas**: `/`, `/clinicas`, `/clinicas/[id]`
- **Componentes**: HeroSection, PublicSearchBar, CategoryChips, HowItWorksSection, ProfessionalCtaSection
- **Build**: 9/9 pages generated successfully
- **Linting**: ESLint PASS (2 warnings), TypeScript PASS

### QA (QA-003)
- **Criteria**: 13/13 PASS
- **Tests**: 28 passing
- **Findings**: Todos RESOLVED o ACCEPTED_RISK

## Changelog del Slice

### Version: BE-003/FE-003/QA-003 - COMPLETED (2026-08-08)

**Nuevos archivos backend**:
- `app/api/v1/routers/public_clinics.py` — Listado y detalle de clinicas publicas
- `app/api/v1/routers/public_branches.py` — Listado de sucursales publicas con paginacion
- `app/api/v1/routers/public_services.py` — Listado de servicios publicos con filtros
- `app/application/use_cases/public_clinics.py` — ListPublicClinicsUseCase
- `app/application/use_cases/public_branches.py` — ListPublicBranchesUseCase
- `app/application/use_cases/public_services.py` — ListPublicServicesUseCase
- `app/api/v1/schemas/public_clinic.py` — DTOs publicos para clinicas
- `app/api/v1/schemas/public_branch.py` — DTOs publicos para sucursales
- `app/api/v1/schemas/public_service.py` — DTOs publicos para servicios
- `app/tests/api/test_public_clinics.py` — 6 contract tests (async)
- `app/tests/api/test_public_branches.py` — 4 contract tests (async)
- `app/tests/api/test_public_services.py` — 5 contract tests (async)

**Nuevos archivos frontend**:
- `src/features/public-landing/components/HeroSection.tsx` — Hero con buscador
- `src/features/public-landing/components/PublicSearchBar.tsx` — Barra de busqueda
- `src/features/public-landing/components/CategoryChips.tsx` — Chips de categorias
- `src/features/public-landing/components/HowItWorksSection.tsx` — Seccion instructiva
- `src/features/public-landing/components/ProfessionalCtaSection.tsx` — CTA profesional
- `src/features/public-landing/components/HeroBentoVisual.tsx` — Visual decorativo
- `src/features/public-landing/components/CategoryChipsWrapper.tsx` — Wrapper con Suspense

**Decisiones tecnicas**:
1. Contract tests usan `httpx.AsyncClient` porque endpoints son async y TestClient hace llamadas sincronicas
2. Dependencias se mockean sobre funciones del router, no clases
3. `useSearchParams()` envuelto en Suspense boundaries para evitar errores de prerendering
4. `export const dynamic = 'force-dynamic'` en paginas con query params

## Estado Final

```text
Estado de ejecucion: APPROVED
Siguiente paso recomendado: Release BE-003/FE-003/QA-003 to staging
Motivo: All gates passed successfully, all findings resolved, documentation updated
```


