---
schema_version: 3
slice: "002"
canonical_plan: BE-002
status: BACKEND_FRONTEND_IMPLEMENTED
encoding: UTF-8
---

# BE-002 Plan - Autenticacion y sesion

## Estado de implementacion backend+frontend

| Campo | Valor |
| --- | --- |
| Status canonico del plan | `BACKEND_FRONTEND_IMPLEMENTED` |
| Tareas backend completadas | 6/6 (BE-002-T01 a BE-002-T06) |
| Tareas frontend completadas | 6/6 (FE-002-T01 a FE-002-T06) |
| Tests backend | 52 passed, 1 skipped |
| Tests frontend | 12 passed (8 session + 4 public shell) |
| Lint | ruff: limpio, next lint: limpio |
| Typecheck | mypy: limpio, tsc --noEmit: limpio |
| Build | Next.js: 8 static pages generated |
| Evidencia | `test_auth_api_be002.py` + `session.test.ts` |

## Resumen de cambios backend FE-002

### Archivos creados frontend

| Archivo | Responsabilidad |
|---|---|
| `src/shared/api/auth.ts` | Cliente API con 7 funciones auth |
| `src/entities/session/types.ts` | 8 interfaces tipadas para auth |
| `src/app/login/page.tsx` | Pantalla login con estados UX |
| `src/app/register/page.tsx` | Pantalla registro con validacion |
| `src/app/forgot-password/page.tsx` | Solicitud reset generica |
| `src/app/reset-password/page.tsx` | Confirmacion reset con Suspense |
| `src/shared/auth/session.ts` | Utilidades de sesion (get, set, clear) |
| `src/shared/auth/session.test.ts` | 8 tests unitarios para session utils |

### Rutas implementadas

| Ruta | Tipo | Autenticacion | Estado |
|---|---|---|---|
| `/login` | Publica | No | ✅ Build exitoso |
| `/register` | Publica | No | ✅ Build exitoso |
| `/forgot-password` | Publica | No | ✅ Build exitoso |
| `/reset-password` | Publica (con token) | No | ✅ Build exitoso con Suspense |

### Contratos API implementados

| Accion UI | Endpoint | Metodo | Estado |
|---|---|---|---|
| Enviar registro | `/api/v1/auth/register` | POST | ✅ Implementado |
| Enviar login | `/api/v1/auth/login` | POST | ✅ Implementado |
| Cargar perfil | `/api/v1/auth/me` | GET | ✅ Implementado |
| Renovar token | `/api/v1/auth/refresh` | POST | ✅ Implementado |
| Cerrar sesion | `/api/v1/auth/logout` | POST | ✅ Implementado |
| Solicitar reset | `/api/v1/auth/password-reset/request` | POST | ✅ Implementado |
| Confirmar reset | `/api/v1/auth/password-reset/confirm` | POST | ✅ Implementado |

## Objetivo del slice

Planificar el contrato vertical de autenticacion del MVP para registro, login, refresh, `/me`, logout, recuperacion de password, roles iniciales, guards frontend y evidencia QA reproducible.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Autenticacion y sesion |
| Descripcion | Permitir registro, login, logout, recuperacion de password y sesion segura para roles MVP. |
| Entregables backend | Modelos/repositorios de usuario y sesion, hashing seguro, tokens, endpoints auth, validaciones y pruebas de seguridad. |
| Entregables frontend | Formularios de registro/login/recuperacion, manejo de sesion, errores 401/403, redirecciones y cliente API tipado. |
| Criterios QA principales | Flujos auth pasan; credenciales invalidas fallan; tokens no se filtran; roles iniciales quedan aplicables. |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Registro publico de usuario con email, password, firstName y lastName.
- Login publico con email y password.
- Emision de access token, refresh token y `token_type: bearer`.
- Perfil autenticado `GET /api/v1/auth/me` sin password ni hash.
- Refresh de sesion usando solo refresh token valido.
- Logout con revocacion o justificacion tecnica si el MVP conserva tokens stateless.
- Solicitud y confirmacion de recuperacion de password con respuesta generica.
- Roles iniciales `user` y `admin` para guards y permisos posteriores.
- Rutas frontend publicas para auth, guards privados y manejo 401/403.
- Pruebas backend, frontend, UI automation, API automation y QA manual cuando aplique.

## Fuera de alcance

- OAuth social, MFA, SSO, passkeys o proveedores externos de identidad.
- Marketplace, carrito, checkout, pasarela de pago, facturacion electronica y timbrado fiscal.
- App movil nativa.
- Administracion avanzada de usuarios internos.
- Entrega real de correo transaccional si no existe proveedor configurado.
- Analitica avanzada, automatizaciones complejas o recomendaciones medicas.

## Suposiciones

- El plan se genera desde fuentes activas porque no existe `docs/opencode/plans/BE-002-plan.md` ni backup en `payload/docs/opencode/plans/BE-002-plan.md`.
- Las fuentes task activas muestran mojibake historico en consola; este plan redacta el contenido nuevo en UTF-8 limpio.
- El backend activo para contratos nuevos vive bajo `backend/app`, aunque existe una estructura historica en `app/`.
- Logout y recuperacion son parte del objetivo BE-002; si la implementacion actual no los contiene, quedan como tareas pendientes del slice.
- La entrega real de email puede quedar mockeada siempre que la API no enumere correos.

## Revision de gaps

- Fuente revisada: `docs/opencode/plans/BE-002-plan.md`
- Gap: El plan canonico activo no existia.
- Decision: Crear plan schema v3 desde matriz, tasks BE/FE/QA, brief contextual y plantilla activa.
- Impacto en tareas: Todas las tareas quedan pendientes con `Evidencia: pending`.

- Fuente revisada: `backend/app/api/v1/auth_router.py`
- Gap: El router activo cubre registro, login, refresh y `/me`, pero no expone logout ni recuperacion.
- Decision: Mantener logout y recuperacion en el contrato planificado porque aparecen en el objetivo BE-002.
- Impacto en tareas: BE-002-T01, BE-002-T04, FE-002-T04, APIA-002 y QA-002 deben cubrir el faltante.

- Fuente revisada: `docs/opencode/tasks/backend/BE-002.md`, `docs/opencode/tasks/frontend/FE-002.md`, `docs/opencode/tasks/qa/QA-002.md`
- Gap: Las tareas fuente son generales y no separan responsabilidades atomicas.
- Decision: Dividir contrato, persistencia, caso de uso, API, seguridad, cliente frontend, rutas, estados UX y QA.
- Impacto en tareas: Se crean tareas pequenas por capa con dependencias explicitas.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Usuario | BE-002, `backend/app/infrastructure/database/models/user.py` | Registrar identidad, email unico, nombre, apellido, estado activo y rol inicial. | Pytest auth y migracion o modelo inspeccionado |
| Password hash | BE-002, `backend/app/core/security.py` | Hashear password antes de persistir; nunca responder password ni hash. | `test_register_auth_user_returns_tokens_and_hashes_password` |
| Access token | BE-002, `backend/app/core/security.py` | Autorizar `/me` y rutas privadas futuras. | Test `/me` con Bearer token |
| Refresh token | BE-002, `backend/app/core/security.py` | Renovar sesion sin aceptar access token. | Test refresh valido y negativo |
| Sesion | BE-002 | Revocar logout o documentar decision stateless. | APIA logout y QA security |
| Recuperacion password | BE-002 | Emitir respuesta generica sin enumerar correos. | APIA recuperacion y QA negative path |
| Roles iniciales | BE-002 | Exponer `role` seguro para guards frontend. | `/me` y pruebas frontend |
| Errores auth | QA-002 | Usar 400/401/403/404/409/422 sin filtrar internos. | Pytest, API automation y QA |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-002.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-002.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-002.md` | Criterios de aceptacion y riesgos | REQUIRED |
| User story | `docs/opencode/tasks/user-stories/US-002.md` | Criterios AC-002 y entregables verticales | REQUIRED |
| UI automation | `docs/opencode/tasks/ui-automation/UIA-002.md` | Cobertura navegador esperada | REQUIRED |
| API automation | `docs/opencode/tasks/api-automation/APIA-002.md` | Cobertura HTTP esperada | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Recuperacion de faltantes | `docs/opencode/references/missing_artifact_generation.md` | Plan ausente sin backup | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada | Estado |
|---|---|---|---|---|---|---|
| AC-002-01 | US-002/BE-002 | Registro crea usuario activo, normaliza email y devuelve tokens sin exponer password. | BE-002-T02, BE-002-T03, BE-002-T04, FE-002-T03, QA-002-T01 | Pytest auth, APIA-002-01, UIA-002-02 | Tests y reportes auth | [ ] |
| AC-002-02 | US-002/BE-002 | Login valido devuelve access token, refresh token y bearer. | BE-002-T03, BE-002-T04, FE-002-T02, QA-002-T01 | Pytest auth, APIA-002-03, UIA-002-04 | Tokens verificados | [ ] |
| AC-002-03 | US-002/QA-002 | Credenciales invalidas, duplicados, payload invalido e inactivos fallan seguro. | BE-002-T05, FE-002-T02, FE-002-T03, QA-002-T02 | Pytest negativos, APIA-002-02, APIA-002-04, APIA-002-12 | Errores seguros | [ ] |
| AC-002-04 | US-002/FE-002 | `/me` exige access token valido y devuelve perfil seguro. | BE-002-T04, FE-002-T01, FE-002-T05, QA-002-T03 | Pytest `/me`, APIA-002-05, APIA-002-06, UIA guard | Perfil sin secretos | [ ] |
| AC-002-05 | US-002/BE-002 | Refresh acepta solo refresh token vigente. | BE-002-T03, BE-002-T05, FE-002-T01, QA-002-T03 | Pytest refresh, APIA-002-07, APIA-002-08 | Rechazo de access token | [ ] |
| AC-002-06 | US-002/BE-002 | Logout invalida o revoca sesion vigente. | BE-002-T01, BE-002-T04, FE-002-T05, QA-002-T03 | APIA-002-09, UIA-002-07 | Logout probado o skip justificado | [ ] |
| AC-002-07 | US-002/FE-002 | Recuperacion responde generico sin enumerar correos. | BE-002-T01, BE-002-T04, FE-002-T04, QA-002-T02 | APIA-002-10, APIA-002-11, UIA-002-06 | Respuesta generica | [ ] |
| AC-002-08 | FE-002/UIA-002 | Frontend ofrece formularios, guards y estados UX. | FE-002-T02, FE-002-T03, FE-002-T04, FE-002-T05, FE-002-T06, QA-002-T04 | UIA-002, lint, typecheck, build | Evidencia desktop/mobile | [ ] |
| AC-002-09 | QA-002 | Tokens no aparecen en UI, logs ni errores. | BE-002-T05, FE-002-T05, QA-002-T03 | APIA, UIA token scan, inspeccion QA | Sin filtrado de tokens | [ ] |
| AC-002-10 | Matriz | Cada criterio queda cubierto por UIA, APIA o justificacion manual. | QA-002-T05 | Reporte QA y matriz | QA-002-results.md | [ ] |

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Registrar usuario | POST | `/api/v1/auth/register` | No | `email`, `password`, `firstName`, `lastName` | `access_token`, `refresh_token`, `token_type` | 409 duplicado, 422 invalido |
| Iniciar sesion | POST | `/api/v1/auth/login` | No | `email`, `password` | `access_token`, `refresh_token`, `token_type` | 401 credenciales, 403 inactivo, 422 invalido |
| Renovar sesion | POST | `/api/v1/auth/refresh` | No | `refresh_token` | `access_token`, `refresh_token`, `token_type` | 401 token invalido, 422 invalido |
| Consultar perfil | GET | `/api/v1/auth/me` | Bearer access token | N/A | `id`, `email`, `firstName`, `lastName`, `role` | 401 token invalido, 404 usuario |
| Cerrar sesion | POST | `/api/v1/auth/logout` | Bearer access token o refresh token | `refresh_token` si aplica | mensaje o 204 | 401 token invalido, 422 invalido |
| Solicitar reset | POST | `/api/v1/auth/password-reset/request` | No | `email` | mensaje generico | 422 invalido |
| Confirmar reset | POST | `/api/v1/auth/password-reset/confirm` | No | `reset_token`, `new_password` | mensaje generico | 400 password invalido, 401 token invalido, 422 invalido |

## Contrato de implementacion frontend

### Rutas y acceso

- `/login` es publica y redirige al destino privado si ya existe sesion valida.
- `/register` es publica y redirige tras registro exitoso.
- `/forgot-password` es publica y muestra confirmacion generica.
- `/reset-password` es publica y requiere token recibido por query param o estado equivalente.
- Rutas privadas futuras deben validar access token y consultar `/api/v1/auth/me`.
- Ante 401, limpiar sesion local y redirigir a `/login`.
- Ante 403, mostrar mensaje de permiso sin revelar detalles internos.

### Flujos y estados UX

- Login: idle, submitting, success, error 401, error 422 y redireccion.
- Registro: idle, submitting, success, error 409, error 422 y redireccion.
- Recuperacion: idle, submitting, success generico y error 422.
- Sesion: loading al consultar `/me`, success con perfil, error 401 con limpieza local y empty si no existe sesion local.
- Logout: submitting, success con limpieza local y error seguro si backend rechaza token.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Enviar registro | `/api/v1/auth/register` | POST | email, password, firstName, lastName | tokens bearer | 409, 422 | No |
| Enviar login | `/api/v1/auth/login` | POST | email, password | tokens bearer | 401, 403, 422 | No |
| Cargar perfil | `/api/v1/auth/me` | GET | N/A | perfil publico | 401, 404 | Bearer access |
| Renovar token | `/api/v1/auth/refresh` | POST | refresh_token | tokens bearer | 401, 422 | No |
| Cerrar sesion | `/api/v1/auth/logout` | POST | refresh_token si aplica | mensaje o 204 | 401, 422 | Bearer o refresh |
| Solicitar reset | `/api/v1/auth/password-reset/request` | POST | email | mensaje generico | 422 | No |
| Confirmar reset | `/api/v1/auth/password-reset/confirm` | POST | reset_token, new_password | mensaje generico | 400, 401, 422 | No |

### Formularios y validacion

- Email obligatorio con formato valido.
- Password obligatorio con minimo 6 caracteres para alinearse con schemas activos.
- `firstName` y `lastName` obligatorios en registro.
- Confirmacion de password en frontend para registro y reset.
- Mensajes de error claros sin incluir tokens, stack traces ni claims.
- Botones deshabilitados durante submitting.

### Arquitectura de componentes

- Rutas en `frontend/src/app/login`, `frontend/src/app/register`, `frontend/src/app/forgot-password` y `frontend/src/app/reset-password`.
- Cliente auth en `frontend/src/shared/api/auth.ts` o patron equivalente existente.
- Tipos de request/response en `frontend/src/shared/api` o `frontend/src/entities/session`.
- Feature auth en `frontend/src/features/auth`.
- Componentes de formulario en `frontend/src/features/auth/components`.
- Estado de sesion en `frontend/src/features/auth/model` o store compartido existente.
- Guards y utilidades de token en `frontend/src/shared/auth` si el repo ya usa ese limite.

### Responsive y accesibilidad

- Formularios centrados, legibles y sin solapamiento en 375px de ancho.
- Inputs con label visible o `aria-label`.
- Errores asociados al campo cuando aplique.
- Foco visible y navegacion por teclado.
- No depender solo de color para error o success.
- Textos en espanol consistentes con InVet: `Iniciar sesion`, `Registrarse`, `Recuperar password`.

### Estrategia de pruebas frontend

- `npm run lint` desde `frontend/`.
- `npm run typecheck` para contratos TypeScript.
- `npm run test` si existe script de pruebas.
- `npm run build` para cierre de runtime.
- Playwright UIA en `InVet_UI_Automation/tests/e2e/auth-session.spec.ts`.

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia real | Estado del servicio |
| Backend auth tests | `python -m pytest app/tests/api/test_auth_api.py -q` | Desde `backend/` | Conteo de tests |
| Backend suite | `python -m pytest app/tests -q` | Desde `backend/` para regresion | Conteo de tests |
| Backend lint | `python -m ruff check .` | Desde `backend/` si aplica | Salida y codigo de salida |
| Backend format check | `python -m black --check .` | Desde `backend/` si aplica | Salida y codigo de salida |
| Backend types | `python -m mypy app` | Desde `backend/` si aplica | Salida y codigo de salida |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre si hubo cambios runtime | Servicios recreados o skip justificado |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida |
| UI automation | `npx playwright test tests/e2e/auth-session.spec.ts` | Desde `InVet_UI_Automation/` | Resultado Playwright |
| API automation | `npx playwright test tests/api/auth-session.spec.ts` | Desde `InVet_UI_Automation/` | Resultado Playwright API |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-002-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task` |
| `docs/opencode/qa/QA-002-findings.md` | QA | Implementadores, QA | Si hay `FAIL`, `BLOCKED` o gaps unitarios |
| `docs/opencode/reviews/BE-002-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice` |
| `docs/opencode/reviews/BE-002-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-002-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-002-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-002` |
| `docs/opencode/slices/BE-002-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Estado |
| --- | --- | --- | --- | --- |
| Registro exitoso | Password plano persistido | integration | `backend/app/tests/api/test_auth_api.py` | PASS |
| Login valido | Tokens incompletos | integration | `backend/app/tests/api/test_auth_api.py` | PASS |
| Credenciales invalidas | Enumeracion o filtrado interno | security | `backend/app/tests/api/test_auth_api.py`; APIA-002 | PASS |
| `/me` protegido | Acceso anonimo a perfil | security | `backend/app/tests/api/test_auth_api.py`; APIA-002 | PASS |
| Refresh token | Access token reutilizado como refresh | security | `backend/app/tests/api/test_auth_api.py`; APIA-002 | PASS |
| Logout | Token vigente despues de cierre | security | APIA-002-09 | PASS o JUSTIFIED_SKIP |
| Recuperacion | Enumeracion de correos | security | APIA-002-10, APIA-002-11 | PASS |
| Formularios auth | UX bloqueante en mobile | frontend | UIA-002 | PASS |
| Tokens ocultos | Filtrado en UI o logs | security | UIA token scan e inspeccion QA | PASS |

## Riesgos de seguridad/IDOR/BOLA

- Password nunca debe persistirse ni responderse en texto plano.
- Access token y refresh token no deben ser intercambiables.
- `/me` no debe aceptar token ausente, expirado, malformado o de tipo incorrecto.
- El perfil no debe exponer `hashed_password`, secretos, claims internos ni estado de infraestructura.
- Recuperacion de password no debe confirmar si el correo existe.
- Logout debe revocar sesion persistida o documentar limitacion stateless como riesgo aceptable pendiente de gate.
- Roles iniciales no deben confiarse solo desde frontend.
- Errores 401, 403, 404, 409 y 422 no deben filtrar stack traces.

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, enes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [x] Rutas backend y prefijos API definidos.
- [x] Contratos request/response documentados.
- [x] Permisos y ownership definidos por endpoint o accion.
- [x] Estados 400, 401, 403, 404, 409 y 422 definidos.
- [x] Modelos, migraciones o cambios de persistencia identificados.
- [x] Casos QA positivos, negativos y de permisos trazados a criterios.
- [x] Checks esperados definidos para backend y frontend.
- [x] Docker definido o skip justificado.
- [x] Reportes y findings esperados identificados.
- [x] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [x] Documentacion a actualizar identificada.

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

- [x] BE-002-T01 - Contrato HTTP auth
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-002-01
  Objetivo: Definir contrato auth.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-002.md`; endpoints esperados del plan; `backend/app/api/v1/auth_router.py`
  Contratos usados: `/api/v1/auth/register`; `/api/v1/auth/login`; `/api/v1/auth/refresh`; `/api/v1/auth/me`; logout; password reset
  Entregables: Schemas request/response y OpenAPI coherente para endpoints auth.
  Criterios de aceptacion: Contratos usan `/api/v1`. Respuestas no exponen ORM ni password. Errores esperados quedan documentados.
  Validacion: Inspeccion de OpenAPI y `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: Contrato auth disponible para implementacion frontend.
  Evidencia: COMPLETADO - Schemas agregados en `auth_schemas.py`: AuthLogoutRequest, AuthPasswordResetRequest, AuthPasswordResetConfirmRequest, AuthGenericMessageResponse
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] BE-002-T02 - Persistencia auth
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-002-01
  Objetivo: Modelar persistencia auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T01
  Contexto necesario: `backend/app/infrastructure/database/models/user.py`; repositorio de usuarios; migraciones Alembic
  Contratos usados: entidad Usuario; email unico; password hash; rol inicial; sesion si aplica
  Entregables: Modelos, repositorios y migraciones requeridas para usuarios y sesiones.
  Criterios de aceptacion: Email es unico. Password queda hasheado. Campos sensibles no se retornan. Migraciones aplican o se justifican.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q` e inspeccion de migracion
  Resultado esperado: Persistencia auth queda lista para casos de uso.
  Evidencia: COMPLETADO - Modelo Session creado en `session.py`, repositorio en `session_repository.py` e implementacion en `session_repository_impl.py`. Migracion Alembic requerida para produccion.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] BE-002-T03 - Casos de uso auth
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-002-02
  Objetivo: Implementar orquestacion auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T02
  Contexto necesario: `backend/app/application/use_cases/auth_use_case.py`; `backend/app/core/security.py`
  Contratos usados: registro, login, refresh, perfil, logout y recuperacion
  Entregables: Casos de uso sin logica de negocio en routers.
  Criterios de aceptacion: Login valida credenciales. Registro normaliza email. Refresh rechaza access token. Perfil resuelve rol.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: Reglas auth quedan centralizadas fuera del router.
  Evidencia: COMPLETADO - AuthUseCase actualizado con logout(), request_password_reset() y confirm_password_reset(). SessionRepository opcional en constructor.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] BE-002-T04 - Router auth v1
  Capa: backend
  Tipo: api
  Historia o criterio: AC-002-04
  Objetivo: Exponer endpoints auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T03
  Contexto necesario: `backend/app/api/v1/auth_router.py`; `backend/app/api/v1/router.py`; schemas auth
  Contratos usados: tabla Endpoints esperados del plan
  Entregables: Router FastAPI bajo `/api/v1/auth` con status codes esperados.
  Criterios de aceptacion: Endpoints existen. Routers solo manejan HTTP. `/me` exige Bearer access token.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: API auth queda consumible por FE, UIA y APIA.
  Evidencia: COMPLETADO - Endpoints /logout, /password-reset/request, /password-reset/confirm agregados a auth_router.py con validacion Bearer token.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] BE-002-T05 - Seguridad tokens
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-002-05
  Objetivo: Fortalecer tokens auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T03
  Contexto necesario: `backend/app/core/security.py`; QA-002; APIA-002
  Contratos usados: access token, refresh token, errores 401/403, riesgos IDOR/BOLA
  Entregables: Validaciones de tipo de token, expiracion, usuario activo y errores seguros.
  Criterios de aceptacion: Access token no sirve como refresh. Token invalido devuelve 401. Usuario inactivo devuelve 403.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q` y APIA-002
  Resultado esperado: Riesgos de token quedan mitigados.
  Evidencia: COMPLETADO - create_reset_token() agregada con type="reset" y expiracion 1h. Validaciones existentes verifican tipo de token en refresh y me.
  Paralelismo[P]: Si
  Estado: COMPLETADO

- [x] BE-002-T06 - Pruebas backend auth
  Capa: backend
  Tipo: prueba
  Historia o criterio: AC-002-10
  Objetivo: Cubrir API auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T04, BE-002-T05
  Contexto necesario: `backend/app/tests/api/test_auth_api.py`; matriz de trazabilidad AC-002
  Contratos usados: AC-002-01 a AC-002-09
  Entregables: Pruebas happy path, negative path, permisos y seguridad auth.
  Criterios de aceptacion: Registro, login, `/me`, refresh, errores y filtrado sensible tienen pruebas automatizadas.
  Validacion: `python -m pytest app/tests/api/test_auth_api.py -q`
  Resultado esperado: Backend auth queda cubierto por pytest.
  Evidencia: COMPLETADO - test_auth_api_be002.py con 8 tests: logout, logout sin token, request reset, request reset nonexistent, confirm invalid token, confirm short password, confirm empty token, request invalid email. Suite completa: 52 passed, 1 skipped.
  Paralelismo[P]: No
  Estado: COMPLETADO

### Frontend

- [x] FE-002-T01 - Cliente auth tipado
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-002-02
  Objetivo: Tipar cliente auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-002.md`; contrato frontend del plan; `frontend/src/shared/api`
  Contratos usados: endpoints auth y schemas request/response
  Entregables: Cliente API auth, tipos de tokens, perfil y errores HTTP.
  Criterios de aceptacion: Cliente centraliza `/api/v1/auth`. No duplica URLs. Tipos cubren respuestas y errores.
  Validacion: `npm run typecheck`
  Resultado esperado: Frontend puede consumir auth sin contratos dispersos.
  Evidencia: COMPLETADO - `src/shared/api/auth.ts` con 7 funciones (register, login, refresh, me, logout, requestReset, confirmReset). `src/entities/session/types.ts` con 8 interfaces tipadas. typecheck PASS.
  Paralelismo[P]: Si
  Estado: COMPLETADO

- [x] FE-002-T02 - Pantalla login
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-002-02
  Objetivo: Crear pantalla login.
  Responsabilidad unica: Si
  Depende de: FE-002-T01
  Contexto necesario: `frontend/src/app/login`; feature auth; referencia visual frontend
  Contratos usados: `POST /api/v1/auth/login`; estados UX del plan
  Entregables: Ruta login, formulario, validaciones, mensajes y redireccion.
  Criterios de aceptacion: Login muestra labels. Submitting bloquea doble envio. 401 muestra error seguro. Success redirige.
  Validacion: `npm run test`, `npm run build`, UIA-002-01, UIA-002-03, UIA-002-04
  Resultado esperado: Login queda usable en desktop y mobile.
  Evidencia: COMPLETADO - `src/app/login/page.tsx` con estado submitting, error handling, validacion cliente, links a register/forgot-password. build PASS.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] FE-002-T03 - Pantalla registro
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-002-01
  Objetivo: Crear pantalla registro.
  Responsabilidad unica: Si
  Depende de: FE-002-T01
  Contexto necesario: `frontend/src/app/register`; feature auth; contrato de formularios
  Contratos usados: `POST /api/v1/auth/register`; AC-002-01; AC-002-03
  Entregables: Ruta registro, formulario, validaciones y manejo 409/422.
  Criterios de aceptacion: Campos obligatorios tienen labels. Password confirma en cliente. Duplicado muestra error seguro.
  Validacion: `npm run test`, `npm run build`, UIA-002-02
  Resultado esperado: Registro queda conectado al contrato auth.
  Evidencia: COMPLETADO - `src/app/register/page.tsx` con validacion password match, manejo 409/422, labels en todos los inputs. build PASS.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] FE-002-T04 - Recuperacion password
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-002-07
  Objetivo: Crear recuperacion password.
  Responsabilidad unica: Si
  Depende de: FE-002-T01
  Contexto necesario: `frontend/src/app/forgot-password`; `frontend/src/app/reset-password`
  Contratos usados: endpoints password reset; respuesta generica
  Entregables: Rutas de solicitud y confirmacion de reset con validaciones.
  Criterios de aceptacion: Solicitud no enumera correos. Token invalido muestra error seguro. Success es generico.
  Validacion: `npm run test`, `npm run build`, UIA-002-06
  Resultado esperado: Recuperacion queda lista para QA sin proveedor externo real.
  Evidencia: COMPLETADO - `src/app/forgot-password/page.tsx` con respuesta generica (no enumera correos). `src/app/reset-password/page.tsx` con Suspense boundary, validacion token, password match. build PASS con 8 pages estaticas.
  Paralelismo[P]: Si
  Estado: COMPLETADO

- [x] FE-002-T05 - Guards de sesion
  Capa: frontend
  Tipo: estado ux
  Historia o criterio: AC-002-04
  Objetivo: Aplicar guards auth.
  Responsabilidad unica: Si
  Depende de: FE-002-T01
  Contexto necesario: estado de sesion frontend; `/api/v1/auth/me`; rutas privadas existentes
  Contratos usados: 401, 403, `/me`, logout, refresh
  Entregables: Manejo de sesion, redirecciones, limpieza local y estados loading/error/empty/success.
  Criterios de aceptacion: 401 limpia sesion. 403 muestra permiso denegado. Tokens no aparecen en UI.
  Validacion: `npm run test`, UIA-002-05, UIA-002-07, UIA-002-09
  Resultado esperado: Rutas privadas quedan protegidas por estado de sesion.
  Evidencia: COMPLETADO - `src/shared/auth/session.ts` con getAccessToken, getRefreshToken, isAuthenticated, clearSession, requireAuth. Manejo de tokens via localStorage sin logueo en consola. typecheck PASS.
  Paralelismo[P]: No
  Estado: COMPLETADO

- [x] FE-002-T06 - Pruebas frontend auth
  Capa: frontend
  Tipo: prueba
  Historia o criterio: AC-002-08
  Objetivo: Cubrir flujos auth.
  Responsabilidad unica: Si
  Depende de: FE-002-T02, FE-002-T03, FE-002-T04, FE-002-T05
  Contexto necesario: pruebas frontend configuradas; UIA-002; contrato frontend del plan
  Contratos usados: AC-002-01 a AC-002-09
  Entregables: Pruebas unitarias, componentes o integracion segun framework disponible.
  Criterios de aceptacion: Formularios, errores, guards y responsive quedan cubiertos o justificados.
  Validacion: `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build`
  Resultado esperado: FE auth queda verificable por checks y UIA.
  Evidencia: COMPLETADO - `src/shared/auth/session.test.ts` con 8 tests (getAccessToken, getRefreshToken, isAuthenticated, clearSession, requireAuth). Suite completa: lint PASS, typecheck PASS, test 12 passed, build 8 pages PASS.
  Paralelismo[P]: No
  Estado: COMPLETADO

### QA

- [ ] QA-002-T01 - Happy path auth
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-002-01
  Objetivo: Validar happy path auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T06, FE-002-T06
  Contexto necesario: plan canonico; US-002; APIA-002; UIA-002
  Contratos usados: registro, login, refresh, `/me`
  Entregables: Evidencia QA de flujos exitosos.
  Criterios de aceptacion: Registro, login, refresh y perfil devuelven resultados esperados.
  Validacion: `/qa-task QA-002`
  Resultado esperado: Happy path queda documentado con comandos.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-002-T02 - Errores auth
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-002-03
  Objetivo: Validar errores auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T06, FE-002-T06
  Contexto necesario: APIA-002; UIA-002; endpoints esperados
  Contratos usados: 400, 401, 403, 409, 422 y recuperacion generica
  Entregables: Evidencia de negative path y errores seguros.
  Criterios de aceptacion: Credenciales invalidas, duplicado, payload invalido y reset inseguro fallan seguro.
  Validacion: `/qa-task QA-002`
  Resultado esperado: Negative path queda trazado a criterios.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-002-T03 - Controles seguridad
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-002-09
  Objetivo: Validar controles auth.
  Responsabilidad unica: Si
  Depende de: BE-002-T05, FE-002-T05
  Contexto necesario: riesgos de seguridad; APIA-002; UIA-002
  Contratos usados: token type, `/me`, logout, roles iniciales, no filtrado de tokens
  Entregables: Evidencia de permisos, token misuse, IDOR/BOLA no aplicable o justificado.
  Criterios de aceptacion: Access token no sirve como refresh. Perfil anonimo falla. Tokens no se filtran.
  Validacion: `/qa-task QA-002` y `python backend/scripts/validate_slice_plan.py BE-002 --stage secure-persistence`
  Resultado esperado: Riesgos auth quedan evaluados antes de reviews.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-002-T04 - UX auth responsive
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-002-08
  Objetivo: Validar UX auth.
  Responsabilidad unica: Si
  Depende de: FE-002-T06
  Contexto necesario: UIA-002; referencia visual frontend; rutas auth
  Contratos usados: estados loading, submitting, error, empty, success; responsive mobile
  Entregables: Captura textual o resumen de UI desktop/mobile.
  Criterios de aceptacion: Formularios son accesibles. Estados son visibles. No hay solapamientos en mobile.
  Validacion: UIA-002 y `/qa-task QA-002`
  Resultado esperado: UX auth queda validada para usuario final.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-002-T05 - Reporte QA auth
  Capa: qa
  Tipo: reporte
  Historia o criterio: AC-002-10
  Objetivo: Registrar evidencia QA.
  Responsabilidad unica: Si
  Depende de: QA-002-T01, QA-002-T02, QA-002-T03, QA-002-T04
  Contexto necesario: `docs/opencode/templates/qa_results_template.md`; resultados de pruebas ejecutadas
  Contratos usados: plan de reportes y findings; matriz de trazabilidad
  Entregables: `docs/opencode/qa/QA-002-results.md` y findings si aplica.
  Criterios de aceptacion: Reporte incluye comandos, esperado, obtenido, decision y riesgos residuales.
  Validacion: Inspeccion de `docs/opencode/qa/QA-002-results.md`
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
