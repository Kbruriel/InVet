---
schema_version: 3
slice: "001"
canonical_plan: BE-001
status: IN_PROGRESS
encoding: UTF-8
---

# BE-001 Plan - Base tecnica y design system

## Objetivo del slice

Establecer la base tecnica verificable de InVet con backend FastAPI operativo, configuracion centralizada, healthcheck, seguridad minima para rutas protegidas y base frontend preparada para evolucionar por slices verticales.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Base tecnica y design system |
| Descripcion | Preparar la base verificable del monolito backend, frontend Next.js y reglas visuales compartidas. |
| Entregables backend | Healthcheck, configuracion, estructura Clean Architecture, seguridad inicial, persistencia base y pruebas de arranque. |
| Entregables frontend | App base, layout inicial, Tailwind local, componentes UI base, estados comunes y configuracion frontend. |
| Criterios QA principales | Backend arranca, healthcheck responde, rutas base existen, seguridad minima rechaza acceso anonimo y estructura base queda trazable. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Backend FastAPI arrancable con `GET /`, `GET /health` y raiz versionada `GET /api/v1/`.
- Configuracion centralizada por entorno para nombre de proyecto, prefijo API, base de datos y secretos.
- Seguridad inicial con hashing de password, emision de JWT y validacion de credenciales.
- Contrato minimo de autenticacion bajo `/api/v1/auth`.
- Base frontend Next.js con layout, cliente API centralizado y componentes compartidos.
- QA reproducible para arranque, healthcheck, configuracion, autenticacion minima y estados UI base.

## Fuera de alcance

- Marketplace, carrito, checkout, pasarela de pago y facturacion.
- Flujo completo de administracion de clinicas.
- Sesiones avanzadas persistentes fuera del contrato minimo de tokens.
- Funcionalidad movil nativa.
- Automatizaciones, analitica avanzada o recomendaciones medicas.

## Suposiciones

- El backup schema v2 en `payload/docs/opencode/plans/BE-001-plan.md` se usa solo como contexto historico.
- Las tareas backend con evidencia de pruebas existentes se conservan completadas.
- Las tareas frontend y QA que no tienen evidencia canonica vigente quedan pendientes.
- La matriz BE/FE/QA activa contiene mojibake historico; este plan corrige la redaccion sin copiar ese encoding roto.

## Revision de gaps

- Fuente revisada: `payload/docs/opencode/plans/BE-001-plan.md`
- Gap: El backup usa schema v2 y no incluye campos obligatorios de tareas schema v3.
- Decision: Regenerar el plan canonico con schema v3, conservar solo contexto y evidencia verificable.
- Impacto en tareas: Backend queda dividido en tareas atomicas; frontend y QA quedan pendientes hasta evidencia nueva.

- Fuente revisada: `docs/opencode/02_be_fe_qa_task_matrix.md`
- Gap: La matriz activa contiene mojibake historico.
- Decision: Usar el sentido funcional del slice y redactar el plan nuevo en UTF-8 limpio.
- Impacto en tareas: Se evita copiar texto corrupto al plan canonico.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| FastAPI app | `docs/opencode/tasks/backend/BE-001.md` | Exponer rutas base y API versionada. | `python -m pytest app/tests/test_main.py -q` |
| Settings | `docs/opencode/tasks/backend/BE-001.md` | Centralizar `PROJECT_NAME`, `API_V1_STR`, `DATABASE_URL`, `SECRET_KEY` y expiracion de tokens. | `test_project_name_config` |
| Security helpers | Backup legacy y tests auth | Hashear passwords, emitir tokens y validar credenciales. | `python -m pytest app/tests/api/test_auth_api.py -q` |
| Persistencia base | `docs/opencode/tasks/backend/BE-001.md` | Preparar infraestructura de base de datos para usuarios y autenticacion. | `python -m pytest app/tests/test_database.py -q` |
| Public shell | `docs/opencode/tasks/frontend/FE-001.md` | Renderizar base publica reutilizable. | `npm run build` |
| Frontend API client | `docs/opencode/tasks/frontend/FE-001.md` | Centralizar consumo de `/api/v1`. | `npm run typecheck` |
| Autenticacion minima | `docs/opencode/tasks/qa/QA-001.md` | Rechazar acceso anonimo en recursos protegidos. | `test_me_requires_authorization` |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-001.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-001.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-001.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios | REQUIRED |
| Backup legacy | `payload/docs/opencode/plans/BE-001-plan.md` | Contexto historico schema v2 | LEGACY |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Recuperacion de faltantes | `docs/opencode/references/missing_artifact_generation.md` | Migracion de backups legacy | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
|---|---|---|---|---|---|---|
| AC-001-01 | BE-001 | Backend expone raiz, healthcheck y API versionada. | BE-001-T01 | `python -m pytest app/tests/test_main.py -q` | Tests main PASS | [x] |
| AC-001-02 | BE-001 | Configuracion centralizada disponible por entorno. | BE-001-T02 | `python -m pytest app/tests/test_main.py -q` | Settings verificados | [x] |
| AC-001-03 | BE-001/QA-001 | Seguridad minima rechaza acceso anonimo. | BE-001-T03 | `python -m pytest app/tests/api/test_auth_api.py -q` | Auth API PASS | [x] |
| AC-001-04 | BE-001 | Persistencia base preparada para autenticacion. | BE-001-T04 | `python -m pytest app/tests/test_database.py -q` | DB tests PASS | [x] |
| AC-001-05 | FE-001 | Frontend base renderiza shell publico. | FE-001-T01 | `npm run build` | Build PASS | [x] |
| AC-001-06 | FE-001 | Cliente API centraliza consumo de backend. | FE-001-T02 | `npm run typecheck` | Typecheck PASS | [x] |
| AC-001-07 | FE-001/QA-001 | Estados comunes son visibles y accesibles. | FE-001-T03 | pruebas de componentes | Estados UX PASS | [x] |
| AC-001-08 | QA-001 | QA documenta happy path, negative path y permisos. | QA-001-T01 | `docs/opencode/qa/QA-001-results.md` | Decision QA | [x] |

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Healthcheck backend | GET | `/health` fuera del prefijo versionado | No | N/A | `{ "status": "healthy" }` | 500 si servicio falla |
| Raiz backend | GET | `/` fuera del prefijo versionado | No | N/A | Mensaje de API | 500 si servicio falla |
| Raiz API v1 | GET | `/api/v1/` | No | N/A | Mensaje de bienvenida | 500 si servicio falla |
| Registro minimo | POST | `/api/v1/auth/register` | No | email, password, firstName, lastName | access token, refresh token, token type | 409 duplicado, 422 invalido |
| Login minimo | POST | `/api/v1/auth/login` | No | email, password | access token, refresh token, token type | 401 credenciales invalidas |
| Perfil autenticado | GET | `/api/v1/auth/me` | Si | Bearer token | perfil de usuario | 401 sin token |
| Refresh minimo | POST | `/api/v1/auth/refresh` | No | refresh token | access token, refresh token, token type | 401 token invalido |

## Contrato de implementacion frontend

### Rutas y acceso

- `/` es publica y debe cargar sin autenticacion.
- Rutas futuras de login y registro permanecen publicas cuando se implementen.
- Rutas protegidas futuras deben redirigir o bloquear cuando no exista token valido.

### Flujos y estados UX

- Carga inicial muestra contenido publico estable.
- Error de backend no filtra detalles internos.
- Estado empty se usa cuando una lista base no tiene datos.
- Estado success confirma respuesta obtenida.
- Estado submitting aplica a futuros formularios auth.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Verificar servicio | `/health` | GET | N/A | status healthy | 500 | No |
| Consumir API base | `/api/v1/` | GET | N/A | mensaje API | 500 | No |
| Preparar login | `/api/v1/auth/login` | POST | email, password | tokens | 401, 422 | No |
| Consultar perfil | `/api/v1/auth/me` | GET | Bearer token | perfil | 401 | Si |

### Formularios y validacion

- Email obligatorio con formato valido.
- Password obligatorio con longitud minima de 8 caracteres.
- Mensajes de error claros sin revelar secretos.
- Validaciones de auth se implementan en el slice de autenticacion completo.

### Arquitectura de componentes

- Layout base en `src/app/layout.tsx`.
- Rutas publicas en `src/app`.
- Cliente compartido en `src/shared/api`.
- Componentes base en `src/shared/ui/components`.
- Estados visuales reutilizables para loading, error y empty.

### Responsive y accesibilidad

- La shell publica debe ser usable en mobile y desktop.
- Inputs futuros deben tener label asociado.
- Estados visuales no deben depender solo de color.
- Componentes compartidos deben mantener contraste y foco visible.

### Estrategia de pruebas frontend

- `npm run lint` para reglas estaticas.
- `npm run typecheck` para contratos TypeScript.
- `npm run test` para componentes compartidos.
- `npm run build` para cierre de runtime.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia real | Estado del servicio |
| Backend base | `python -m pytest app/tests/test_main.py -q` | Desde `backend/` | Conteo de tests |
| Auth API | `python -m pytest app/tests/api/test_auth_api.py -q` | Desde `backend/` con DB de prueba | Conteo de tests |
| Database | `python -m pytest app/tests/test_database.py -q` | Desde `backend/` | Conteo de tests |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre si hubo cambios runtime | Servicios recreados o skip justificado |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde raiz frontend configurada | Salida y codigo de salida |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-001-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task` |
| `docs/opencode/qa/QA-001-findings.md` | QA | Implementadores, QA | Si hay `FAIL`, `BLOCKED` o gaps unitarios |
| `docs/opencode/reviews/BE-001-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice` |
| `docs/opencode/reviews/BE-001-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-001-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-001-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-001` |
| `docs/opencode/slices/BE-001-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Decision esperada |
| --- | --- | --- | --- | --- |
| Rutas base responden | Backend no arranca | integration | `backend/app/tests/test_main.py` | PASS |
| Configuracion centralizada existe | Entorno inconsistente | unit | `backend/app/tests/test_main.py` | PASS |
| Auth rechaza anonimos | Ruta protegida abierta | security | `backend/app/tests/api/test_auth_api.py` | PASS |
| DB base inicializa | Persistencia rota | integration | `backend/app/tests/test_database.py` | PASS |
| Shell publica renderiza | Frontend no usable | frontend | pruebas de componente | PASS |
| Estados comunes existen | UX incompleta | frontend | pruebas de shared UI | PASS |

## Riesgos de seguridad/IDOR/BOLA

- `SECRET_KEY` no debe aparecer en logs ni respuestas.
- Tokens JWT deben distinguir access token y refresh token.
- Recursos protegidos deben rechazar solicitudes sin credenciales.
- Errores 401 y 403 no deben filtrar detalles internos.
- La base de usuarios debe hashear password antes de persistir.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, enes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [x] Rutas backend y prefijos API definidos.
- [x] Contratos request/response documentados.
- [x] Permisos y ownership definidos por endpoint o accion base.
- [x] Estados 401, 409 y 422 cubiertos en auth minima.
- [x] Modelos, repositorios o cambios de persistencia identificados.
- [ ] Casos QA positivos, negativos y de permisos trazados en reporte QA.
- [ ] Checks esperados definidos para backend y frontend con evidencia final.
- [ ] Docker actualizado o skip justificado.
- [ ] Reportes y findings esperados escritos por gates responsables.
- [x] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [ ] Documentacion final del slice actualizada.

## Checklist de tareas

Reglas:
- Cada tarea tiene una sola responsabilidad verificable.
- Cada tarea apunta a una sola capa y a un tipo de trabajo.
- Si mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, dividir en tareas `TNN` consecutivas.
- `Responsabilidad unica` debe ser `Si`.
- `Objetivo` debe ser corto, sin objetivos compuestos.
- `Contexto necesario` debe listar archivos o decisiones que el implementador debe leer.
- `Contratos usados` debe mapear la tarea con endpoints, criterios, referencias o reportes.
- `Resultado esperado` debe describir el outcome observable que otro agente puede validar.

### Backend

- [x] BE-001-T01 - Rutas base FastAPI
  Capa: backend
  Tipo: api
  Historia o criterio: AC-001-01
  Objetivo: Definir rutas base FastAPI.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-001.md`; `backend/app/api/main.py`; `backend/app/api/v1/router.py`
  Contratos usados: `GET /`; `GET /health`; `GET /api/v1/`
  Entregables: `backend/app/api/main.py`; `backend/app/api/v1/router.py`
  Criterios de aceptacion: Rutas base responden 200. Respuestas no filtran secretos.
  Validacion: `python -m pytest app/tests/test_main.py -q`
  Resultado esperado: Backend base responde a smoke tests.
  Evidencia: `backend/app/tests/test_main.py` cubre root, health y API v1.
  Paralelismo[P]: No

- [x] BE-001-T02 - Settings backend
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-001-02
  Objetivo: Centralizar configuracion backend.
  Responsabilidad unica: Si
  Depende de: BE-001-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-001.md`; `backend/app/core/config/settings.py`; `backend/app/core/database.py`
  Contratos usados: settings de proyecto, API, secretos y base de datos
  Entregables: `backend/app/core/config/settings.py`; `backend/app/core/database.py`
  Criterios de aceptacion: Settings exponen nombre, prefijo API, expiracion y base de datos. DB de prueba inicializa.
  Validacion: `python -m pytest app/tests/test_main.py app/tests/test_database.py -q`
  Resultado esperado: Configuracion backend queda disponible para runtime y pruebas.
  Evidencia: `backend/app/tests/test_main.py`; `backend/app/tests/test_database.py`
  Paralelismo[P]: No

- [x] BE-001-T03 - Seguridad JWT
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-001-03
  Objetivo: Consolidar seguridad JWT.
  Responsabilidad unica: Si
  Depende de: BE-001-T02
  Contexto necesario: `docs/opencode/tasks/backend/BE-001.md`; `backend/app/core/security.py`; `backend/app/api/v1/auth_router.py`
  Contratos usados: `/api/v1/auth/register`; `/api/v1/auth/login`; `/api/v1/auth/me`; `/api/v1/auth/refresh`
  Entregables: `backend/app/core/security.py`; `backend/app/api/v1/auth_router.py`; schemas auth
  Criterios de aceptacion: Password se hashea. Tokens se emiten. Perfil protegido rechaza anonimos.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: Auth minima queda verificable por API tests.
  Evidencia: `backend/app/tests/api/test_auth_api.py`
  Paralelismo[P]: No

- [x] BE-001-T04 - Pruebas backend base
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-001-04
  Objetivo: Cubrir baseline backend.
  Responsabilidad unica: Si
  Depende de: BE-001-T01, BE-001-T02, BE-001-T03
  Contexto necesario: `backend/app/tests/test_main.py`; `backend/app/tests/test_database.py`; `backend/app/tests/api/test_auth_api.py`
  Contratos usados: matriz de trazabilidad AC-001-01 a AC-001-04
  Entregables: pruebas backend de arranque, DB y auth minima
  Criterios de aceptacion: Happy path y negative path backend tienen pruebas automatizadas.
  Validacion: `python -m pytest app/tests/test_main.py app/tests/test_database.py app/tests/api/test_auth_api.py -q`
  Resultado esperado: Baseline backend queda cubierto por pytest.
  Evidencia: suites existentes en `backend/app/tests`
  Paralelismo[P]: No

### Frontend

- [ ] FE-001-T01 - Shell publica
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-001-05
  Objetivo: Configurar shell Next.
  Responsabilidad unica: Si
  Depende de: BE-001-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-001.md`; `src/app/layout.tsx`; `src/app`
  Contratos usados: ruta publica `/`; referencia visual frontend
  Entregables: layout base y pagina publica ejecutable
  Criterios de aceptacion: Shell carga en desktop y mobile. No depende de CDN critica.
  Validacion: `npm run build`
  Resultado esperado: Frontend base renderiza sin errores.
  Evidencia: pending
  Paralelismo[P]: Si

- [ ] FE-001-T02 - Cliente API base
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-001-06
  Objetivo: Centralizar cliente API.
  Responsabilidad unica: Si
  Depende de: BE-001-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-001.md`; `src/shared/api`
  Contratos usados: `/health`; `/api/v1/`; auth minima futura
  Entregables: cliente API tipado y configuracion de base URL
  Criterios de aceptacion: Cliente reutilizable no duplica URLs. Errores HTTP son manejables.
  Validacion: `npm run typecheck`
  Resultado esperado: Contrato API queda consumible por UI.
  Evidencia: pending
  Paralelismo[P]: Si

- [ ] FE-001-T03 - Estados UI base
  Capa: frontend
  Tipo: componente
  Historia o criterio: AC-001-07
  Objetivo: Cubrir estados UI.
  Responsabilidad unica: Si
  Depende de: FE-001-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-001.md`; `src/shared/ui/components`
  Contratos usados: estados loading, error, empty, success y submitting
  Entregables: componentes compartidos para estados base
  Criterios de aceptacion: Estados son accesibles y reutilizables. Textos no se solapan.
  Validacion: `npm run test`
  Resultado esperado: UI base queda lista para slices posteriores.
  Evidencia: pending
  Paralelismo[P]: Si

### QA

- [ ] QA-001-T01 - Validacion baseline
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-001-08
  Objetivo: Validar baseline tecnico.
  Responsabilidad unica: Si
  Depende de: BE-001-T04, FE-001-T01, FE-001-T02, FE-001-T03
  Contexto necesario: plan canonico; `docs/opencode/tasks/qa/QA-001.md`; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: `docs/opencode/qa/QA-001-results.md`
  Criterios de aceptacion: Happy path, negative path, permisos y regresion minima tienen decision trazable.
  Validacion: `/qa-task QA-001`
  Resultado esperado: QA emite decision `APPROVED`, `REJECTED` o `BLOCKED`.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-001-T02 - Seguridad QA
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-001-03
  Objetivo: Verificar controles auth.
  Responsabilidad unica: Si
  Depende de: BE-001-T03
  Contexto necesario: `backend/app/tests/api/test_auth_api.py`; riesgos de seguridad del plan
  Contratos usados: `/api/v1/auth/me`; tokens; errores 401
  Entregables: evidencia QA de auth minima
  Criterios de aceptacion: Acceso anonimo falla. Tokens invalidos fallan sin filtrar datos.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: Riesgos auth base quedan evaluados por QA.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-001-T03 - Evidencia de cierre
  Capa: qa
  Tipo: reporte
  Historia o criterio: AC-001-08
  Objetivo: Registrar evidencia QA.
  Responsabilidad unica: Si
  Depende de: QA-001-T01, QA-001-T02
  Contexto necesario: `docs/opencode/templates/qa_results_template.md`; resultados de pruebas ejecutadas
  Contratos usados: plan de reportes y findings
  Entregables: resultados QA y findings si aplica
  Criterios de aceptacion: Reporte incluye comandos, esperado, obtenido, decision y riesgos residuales.
  Validacion: inspeccion de `docs/opencode/qa/QA-001-results.md`
  Resultado esperado: El siguiente gate puede consumir evidencia QA.
  Evidencia: pending
  Paralelismo[P]: No

## Definition of Done

- [x] Plan schema v3 valido.
- [ ] Todas las tareas aplicables estan en `- [x]` con evidencia reproducible.
- [ ] QA termina `APPROVED`.
- [ ] Findings inexistentes o `RESOLVED|ACCEPTED_RISK`.
- [ ] Reviews funcional, arquitectura y seguridad terminan `APPROVED`.
- [ ] Checks terminan `APPROVED`.
- [ ] Docker actualizado o skip justificado.
- [ ] Reporte de cierre del slice escrito en UTF-8.
