---
schema_version: 2
slice: "002"
canonical_plan: BE-002
status: DONE
---

# BE-002 Plan - Autenticacion y sesion

## Objetivo del slice

Habilitar registro, login, refresh de token, perfil `/me` y sesion minima para el slice de autenticacion, con backend FastAPI funcional, cliente frontend ya integrado y QA ejecutable sobre PostgreSQL en Docker.

## Alcance MVP

- Backend con endpoints `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh` y `/api/v1/auth/me`.
- Emision de `access_token` y `refresh_token` con JWT.
- Registro de usuarios persistido en PostgreSQL usando la tabla `users` existente.
- Perfil autenticado con rol inicial derivado de `is_admin`.
- Frontend alineado al contrato HTTP real del slice.
- QA reproducible con evidencia actualizada y sin asumir resultados historicos validos.

## Fuera de alcance

- Revocacion persistente de refresh tokens.
- Recuperacion de contrasena por correo real.
- SSO, MFA o politicas avanzadas de sesion.
- Marketplace, checkout, pasarela de pago, inventario o facturacion.

## Suposiciones

- La tabla `users` existente es la base canonica para el slice y expone `email`, `username`, `hashed_password`, `is_active` e `is_admin`.
- El frontend actual de auth puede consumir campos extra en la respuesta sin romperse.
- El stack QA ejecutara pruebas sobre PostgreSQL en Docker y necesitara una base o schema de pruebas aislado antes de suites destructivas.

## Revision de gaps

- Se corrige el plan previo de `BE-002`, que no cumplia `schema_version: 2` ni el formato de tareas requerido por el validador actual.
- Se elimina la contradiccion entre un plan marcado como completado y un backend de auth inexistente a nivel de endpoints.
- Se explicita el riesgo operativo de ejecutar pruebas destructivas sobre la misma base usada por el stack levantado.

## Entidades y reglas de negocio

- **User**: usuario persistido en `users` con `email`, `username`, `hashed_password`, `is_active` e `is_admin`.
- **Auth session**: emite `access_token` corto y `refresh_token` reutilizable para renovar sesion.
- **Rol inicial**: `admin` si `is_admin=True`; `user` en cualquier otro caso.
- **Registro**: no permite correos duplicados y siempre almacena contrasena hasheada.
- **Login**: autentica por `email` + `password`.
- **Perfil**: `/me` responde solo datos publicos del usuario autenticado.

## Endpoints esperados

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /auth/login`
- `GET /auth/register`
- Rutas publicas para login y registro.
- Rutas protegidas futuras dependen de `access_token` valido y `AuthProvider`.

### Flujos y estados UX

- Login: submitting, success, credenciales invalidas, error de servidor.
- Register: submitting, success, correo duplicado, validacion de campos, error de servidor.
- Perfil: carga inicial, usuario autenticado, 401 con limpieza de sesion.

### Contratos API por accion

- Login envia `email` y `password`; recibe `access_token`, `refresh_token` y `token_type`.
- Register envia `email`, `password`, `firstName` y `lastName`; recibe `access_token`, `refresh_token` y `token_type`.
- Refresh envia `refresh_token`; recibe nuevo `access_token`, nuevo `refresh_token` y `token_type`.
- `/me` responde `id`, `email`, `firstName`, `lastName` y `role`.

### Formularios y validacion

- Email obligatorio y con formato valido.
- Password obligatoria con longitud minima de 6 caracteres.
- `firstName` y `lastName` obligatorios en registro.
- Errores backend visibles sin filtrar detalles internos.

### Arquitectura de componentes

- Paginas en `frontend/src/app/auth/...`
- Formularios en `frontend/src/features/auth/components`
- API client en `frontend/src/shared/api/auth.ts`
- Estado de sesion en `frontend/src/shared/context/AuthProvider.tsx`

### Responsive y accesibilidad

- Formularios utilizables en desktop y mobile.
- Inputs etiquetados correctamente.
- Mensajes de error visibles y asociados al flujo.

### Estrategia de pruebas frontend

- Pruebas unitarias o de componente para formularios y `AuthProvider`.
- Typecheck, lint y test del frontend en la corrida del slice.

## Pruebas QA

- Happy path de registro, login y `/me`.
- Negative path para credenciales invalidas, correo duplicado y refresh invalido.
- Permisos: `/me` requiere autenticacion.
- Regresion: smoke de backend base y frontend auth.
- Evidencia actualizada en `docs/opencode/qa/QA-002-results.md`.

## Riesgos de seguridad/IDOR/BOLA

- Tokens invalidos o expirados deben responder 401.
- `/me` no debe exponer `hashed_password`.
- Register y login no deben filtrar si una cuenta existe mas alla del error funcional esperado.
- El refresh token no debe aceptar un `access_token` en su lugar.
- No deben quedar suites destructivas apuntando a la base compartida del stack.

## Checklist tecnico

- [x] Rutas `/api/v1/auth/*` implementadas en backend.
- [x] Password hashing aplicado en persistencia de usuarios.
- [x] `refresh_token` soportado por backend.
- [x] `/me` devuelve perfil consistente con el frontend.
- [x] Frontend auth alineado con la respuesta real del backend.
- [x] QA-002 deja de depender de un plan legacy y genera evidencia actual.
- [x] Las pruebas con DB usan un contexto aislado de la base compartida del stack.

## Checklist de tareas

### Backend

- [x] BE-002-T01 - Normalizar contrato auth del backend
  Capa: backend
  Objetivo: Definir schemas, reglas y respuestas HTTP del slice de autenticacion.
  Depende de: Ninguna
  Entregables: backend/app/api/schemas/auth_schemas.py; backend/app/api/v1/auth_router.py; actualizacion de router v1.
  Criterios de aceptacion: Existen payloads para register, login, refresh y /me; los errores devuelven 400, 401 o 409 segun corresponda; OpenAPI expone el contrato real.
  Validacion: python -m pytest app/tests/test_main.py -q
  Evidencia: `docker compose run --rm backend pytest app/tests/test_main.py -q` -> 4 passed
  Paralelismo[P]: No

- [x] BE-002-T02 - Persistir usuarios y emitir tokens funcionales
  Capa: backend
  Objetivo: Crear el flujo real de registro, autenticacion y refresh sobre PostgreSQL.
  Depende de: BE-002-T01
  Entregables: use case o servicio auth; repositorio de usuario actualizado; helpers JWT extendidos.
  Criterios de aceptacion: Register persiste usuarios con password hasheada; login autentica por email y password; refresh emite nuevos tokens; /me responde perfil del usuario autenticado.
  Validacion: docker compose run --rm backend pytest app/tests/api/test_auth_api.py -q
  Evidencia: `docker compose run --rm backend pytest app/tests/api/test_auth_api.py -q` -> 8 passed
  Paralelismo[P]: No

### Frontend

- [x] FE-002-T01 - Alinear formularios auth con el contrato backend real
  Capa: frontend
  Objetivo: Consumir el backend de auth sin mocks ni contratos obsoletos.
  Depende de: BE-002-T02
  Entregables: frontend/src/shared/api/auth.ts; formularios login/register; AuthProvider si aplica.
  Criterios de aceptacion: Login y register consumen endpoints reales; la sesion guarda `access_token` y `refresh_token` si el backend los devuelve; /me maneja 401 de forma clara.
  Validacion: npm test -- --run
  Evidencia: `npm run typecheck` -> PASS; `npm test -- --run` -> 25 archivos / 36 pruebas passed; `docker compose build frontend` -> PASS
  Paralelismo[P]: No

### QA

- [x] QA-002-T01 - Corregir artefactos legacy del slice 002
  Capa: qa
  Objetivo: Dejar QA-002 con preflight valido y con evidencia util cuando el slice falle.
  Depende de: Ninguna
  Entregables: plan schema v2; findings QA actualizados cuando aplique; resultados QA sin conclusiones stale.
  Criterios de aceptacion: validate_slice_plan.py QA-002 --stage qa deja de fallar por contrato; los resultados viejos quedan invalidados o reemplazados; el bloqueo documenta causa concreta.
  Validacion: python backend/scripts/validate_slice_plan.py QA-002 --stage qa
  Evidencia: `python backend/scripts/validate_slice_plan.py QA-002 --stage qa` -> PASS; `docs/opencode/qa/QA-002-results.md` reemplazado con evidencia actual
  Paralelismo[P]: Si

- [x] QA-002-T02 - Ejecutar validacion funcional del slice auth
  Capa: qa
  Objetivo: Validar happy path, negative path y permisos del flujo de autenticacion.
  Depende de: BE-002-T02, FE-002-T01
  Entregables: docs/opencode/qa/QA-002-results.md; findings si hubiera defects.
  Criterios de aceptacion: Existen comandos reproducibles, evidencia actual y una decision final trazada a criterios; /me, login, register y refresh quedan cubiertos.
  Validacion: docker compose run --rm backend pytest app/tests/api/test_auth_api.py -q
  Evidencia: `docker compose run --rm backend pytest app/tests/api/test_auth_api.py -q` -> 8 passed; smoke HTTP `/api/v1/auth/me` sin token -> 401
  Paralelismo[P]: No

## Definition of Done

- [x] Backend auth implementado y verificable en Docker.
- [x] Frontend auth alineado al contrato real del backend.
- [x] QA-002 ejecutable con plan valido y evidencia actualizada.
- [x] Sin contradicciones entre plan, tasks y resultados del slice 002.
