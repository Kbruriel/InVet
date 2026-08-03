---
schema_version: 2
slice: "001"
canonical_plan: BE-001
status: DONE
---

# BE-001 Plan - Base tecnica y design system

## Objetivo del slice

Establecer la base tecnica del proyecto con backend FastAPI operativo, configuracion centralizada, healthcheck, seguridad minima para rutas protegidas y una base frontend ejecutable para la evolucion del producto.

## Alcance MVP

- Backend FastAPI arrancable con rutas base `GET /`, `GET /health` y `GET /api/v1`.
- Utilidades de seguridad para hash, JWT y validacion de token.
- Configuracion centralizada por entorno para backend y frontend.
- Frontend con shell publica inicial, cliente API centralizado y componentes base alineados a InVet.
- QA reproducible de arranque, configuracion, healthcheck y controles de autenticacion.

## Fuera de alcance

- Login y registro persistidos con flujo completo.
- Refresh tokens persistentes y sesiones avanzadas.
- Dependencia de una base de datos externa para validar la base tecnica del slice.
- Productos, marketplace, carrito, checkout, pasarela de pago y facturacion.

## Revision de gaps

- El plan legacy no cumplia `schema_version: 2` ni el formato actual de tareas.
- Se explicita la compatibilidad temporal de autenticacion para no bloquear pruebas existentes mientras converge el contrato JWT.
- La evidencia QA debe distinguir entre arranque local y validacion sobre Docker.

## Entidades y reglas de negocio

- **Settings**: centraliza `PROJECT_NAME`, `API_V1_STR`, `DATABASE_URL`, `SECRET_KEY` y expiracion de tokens.
- **Security helpers**: generan y validan JWT para endpoints protegidos.
- **Public shell**: pagina base que puede cargar sin autenticacion.
- **Frontend env**: centraliza `NEXT_PUBLIC_API_BASE_URL` y variables publicas de runtime.
- **Regla de autenticacion minima**: un endpoint protegido debe rechazar solicitudes sin credenciales validas.

## Endpoints esperados

- `GET /` - raiz del backend.
- `GET /health` - healthcheck del servicio.
- `GET /api/v1` - raiz del API versionado.
- Cualquier recurso protegido del slice debe exigir autenticacion.

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /` para el shell publico inicial.
- `GET /auth/login` y `GET /auth/register` como rutas publicas base.
- Rutas protegidas futuras dependientes de token valido y provider de sesion.

### Flujos y estados UX

- Carga inicial con contenido visible y CTA claros.
- Estado de error si el backend no responde.
- Estado de autenticacion requerida cuando una ruta protegida no tiene sesion.

### Contratos API por accion

- Healthcheck consume `GET /health`.
- Configuracion inicial consume las variables publicas del entorno.
- Futuras acciones auth consumiran `POST /api/v1/auth/login` y `POST /api/v1/auth/register`.

### Formularios y validacion

- Email obligatorio y con formato valido.
- Password obligatorio con longitud minima razonable para el MVP.
- Mensajes de error visibles sin filtrar detalles internos.

### Arquitectura de componentes

- Shell publica en `frontend/src/app`.
- Componentes compartidos en `frontend/src/shared/ui`.
- Cliente HTTP reusable en `frontend/src/shared/api`.
- Estado de sesion centralizado cuando el slice de auth este disponible.

### Responsive y accesibilidad

- Layout utilizable en desktop y mobile.
- Inputs etiquetados correctamente.
- Estados vacio y error legibles sin depender solo de color.

### Estrategia de pruebas frontend

- Pruebas de componente para shell, estados y cliente API.
- Typecheck, lint y test como parte de la corrida del slice.

## Pruebas QA

- Happy path: arranque del backend, healthcheck y shell publico.
- Negative path: error de configuracion o backend no disponible.
- Permisos: endpoints protegidos rechazan acceso sin autenticacion.
- Regresion: smoke de backend base y frontend shell.

## Riesgos de seguridad/IDOR/BOLA

- Exposicion de secretos de entorno en logs o respuestas.
- Endpoints protegidos sin validacion consistente.
- Falsa sensacion de completitud si la ruta responde pero la seguridad no esta aplicada.

## Checklist tecnico

- [x] Rutas base del backend definidas.
- [x] Settings y seguridad minima centralizados.
- [x] Shell frontend publico disponible.
- [x] QA de arranque y healthcheck reproducible.

## Checklist de tareas

### Backend

- [x] BE-001-T01 - Normalizar arranque y configuracion del backend
  Capa: backend
  Objetivo: Dejar FastAPI, settings y healthcheck ejecutables.
  Depende de: Ninguna
  Entregables: backend/app/main.py; backend/app/core/settings.py; backend/app/api/v1/router.py.
  Criterios de aceptacion: El backend expone `GET /`, `GET /health` y `GET /api/v1`; la configuracion se lee por entorno; los errores no filtran secretos.
  Validacion: python -m pytest app/tests/test_main.py -q
  Evidencia: `python -m pytest app/tests/test_main.py -q` -> PASS
  Paralelismo[P]: No

- [x] BE-001-T02 - Consolidar seguridad y helpers de token
  Capa: backend
  Objetivo: Reutilizar hash, JWT y validacion minima para rutas protegidas.
  Depende de: BE-001-T01
  Entregables: backend/app/core/security.py; helpers de autenticacion; pruebas unitarias basicas.
  Criterios de aceptacion: Existe hash seguro; los JWT se pueden generar y validar; un endpoint protegido rechaza peticiones sin credenciales.
  Validacion: python -m pytest app/tests/test_security.py -q
  Evidencia: `python -m pytest app/tests/test_security.py -q` -> PASS
  Paralelismo[P]: No

### Frontend

- [x] FE-001-T01 - Crear shell publica y cliente API base
  Capa: frontend
  Objetivo: Entregar una base visual y tecnica que el resto de los slices pueda reutilizar.
  Depende de: BE-001-T01
  Entregables: frontend/src/app/page.tsx; frontend/src/shared/api/client.ts; componentes de shell y layout.
  Criterios de aceptacion: La app abre sin errores; el cliente API centraliza la base URL; la vista publica soporta desktop y mobile.
  Validacion: npm run build
  Evidencia: `npm run build` -> PASS
  Paralelismo[P]: Si

### QA

- [x] QA-001-T01 - Validar el baseline tecnico del proyecto
  Capa: qa
  Objetivo: Confirmar arranque, healthcheck y seguridad minima.
  Depende de: BE-001-T01, BE-001-T02, FE-001-T01
  Entregables: resultados QA del baseline; evidencia de smoke checks.
  Criterios de aceptacion: El backend arranca, el healthcheck responde y las rutas protegidas no aceptan acceso anonimo.
  Validacion: python backend/scripts/validate_slice_plan.py BE-001 --stage plan
  Evidencia: Validacion de plan v2 y smoke tecnico en Docker
  Paralelismo[P]: No

## Definition of Done

- [x] Backend base y seguridad minima implementados.
- [x] Frontend shell y cliente API base listos.
- [x] QA del baseline tecnico trazable y reproducible.
- [x] El plan cumple el esquema V2.
