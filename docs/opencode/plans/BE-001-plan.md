# BE-001 Plan - Base tecnica y design system

## Objetivo del slice
Establecer la base tecnica del proyecto con backend FastAPI operativo, configuracion centralizada, healthcheck, manejo de tokens para flujos protegidos y una base frontend ejecutable para la evolucion del producto.

## Alcance MVP
- **Backend**: Aplicacion FastAPI arrancable, rutas base (`/`, `/health`, `/api/v1/`), utilidades de seguridad (`hash`, `JWT`, validacion de token) y estructura por capas.
- **Frontend**: Workspace ejecutable con Next.js, TypeScript y Tailwind local, shell publica inicial, cliente API centralizado y componentes base alineados a InVet.
- **QA**: Validacion reproducible de arranque, configuracion, healthcheck, utilidades de token y requerimiento de autenticacion en endpoints protegidos.

## Fuera de alcance
- Login/registro de usuarios con persistencia real, refresh tokens, recuperacion de contrasena y sesiones completas.
- Dependencia de una base de datos externa para validar la base tecnica del slice 001.
- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturacion electronica y timbrado fiscal.

## Entidades y reglas de negocio
- **Settings**: centraliza `PROJECT_NAME`, `API_V1_STR`, `DATABASE_URL`, `SECRET_KEY` y expiracion de tokens.
- **Security helpers**: generan y validan JWT para endpoints protegidos.
- **Frontend env**: centraliza `NEXT_PUBLIC_API_BASE_URL` y rutas conocidas para el cliente.
- **Regla de autenticacion minima**: un endpoint protegido debe rechazar solicitudes sin credenciales validas.
- **Compatibilidad temporal**: las rutas protegidas heredadas pueden aceptar el bearer numerico usado por pruebas existentes mientras convergen a JWT.

## Endpoints esperados (`/api/v1`)
- `GET /` - raiz del backend.
- `GET /health` - healthcheck del servicio.
- `GET /api/v1/` - raiz del API versionado.
- Endpoints protegidos existentes bajo `/api/v1/clinics`, `/api/v1/owners`, `/api/v1/pets`, etc., deben exigir autenticacion.

## Componentes frontend esperados
- Shell base de aplicacion.
- Tokens visuales de marca.
- Layouts iniciales y componentes compartidos implementados en `FE-001`.
- Landing publica base y rutas placeholder sin enlaces `#`.
- Cliente HTTP reusable en `src/shared/api`.

## Pruebas QA
- **Happy path**: arranque del backend, `healthcheck` y raiz versionada responden correctamente.
- **Negative path**: token invalido devuelve 401 sin filtrar detalles internos.
- **Seguridad**: endpoints protegidos rechazan acceso sin autenticacion.
- **Configuracion**: settings por defecto permiten ejecutar las pruebas tecnicas del slice sin depender de infraestructura externa.
- **Frontend smoke**: lint, typecheck, test y build del frontend pasan localmente.

## Riesgos de seguridad/IDOR/BOLA
- Tokens invalidos o sin `sub` deben rechazarse con 401.
- Los endpoints protegidos no deben aceptar acceso anonimo.
- La compatibilidad temporal con bearer numerico debe mantenerse solo como puente para pruebas heredadas.
- El cliente frontend no debe loggear datos sensibles ni asumir autorizacion por si solo.

## Revision de gaps
- Se elimino la contradiccion que trataba `FE-001` como un entregable solo documental.
- El slice ahora exige un workspace frontend real para que `/implement-frontend-task FE-001` pueda ejecutarse de forma verificable.

## Checklist tecnico
- [x] Rutas backend base definidas (`/`, `/health`, `/api/v1/`).
- [x] Configuracion centralizada en `app.core.config`.
- [x] Utilidades JWT y hashing con pruebas automatizadas.
- [x] Rechazo consistente de autenticacion faltante o invalida.
- [x] Workspace frontend ejecutable con `package.json`, scripts y `src/`.
- [x] Contrato base de FE-001 implementado y verificable.
- [x] QA-001 documentado con evidencia reproducible.

## Checklist de Tareas

### Backend (BE-001)
- [x] 1.0 Verificar arranque basico del backend y rutas base.
  `Objetivo: Confirmar que la aplicacion responde sin infraestructura externa.`
  `Criterios de aceptacion: /, /health y /api/v1/ responden 200 con payload esperado.`
  `Paralelismo[P]: Si`
- [x] 1.1 Mantener configuracion centralizada y defaults seguros para desarrollo.
  `Objetivo: Evitar bloqueos falsos por variables de entorno ausentes en QA tecnica.`
  `Criterios de aceptacion: Settings expone PROJECT_NAME, API_V1_STR, DATABASE_URL y SECRET_KEY.`
  `Paralelismo[P]: Si`
- [x] 1.2 Validar helpers de seguridad y compatibilidad minima de autenticacion.
  `Objetivo: Probar hash, generacion de JWT, verificacion y rechazo de tokens invalidos.`
  `Criterios de aceptacion: Existen pruebas unitarias para security.py y rutas protegidas requieren autenticacion.`
  `Paralelismo[P]: No`

### Frontend (FE-001)
- [x] 2.0 Crear la base ejecutable del frontend en `frontend/`.
  `Objetivo: Dejar un workspace real para que /implement-frontend-task FE-001 pueda operar sin bootstrap manual posterior.`
  `Criterios de aceptacion: Existe frontend/package.json; scripts lint/typecheck/test/build ejecutables; Next.js, TypeScript y Tailwind local quedan configurados.`
  `Paralelismo[P]: No`
- [x] 2.1 Implementar shell publica, tokens y componentes compartidos iniciales.
  `Objetivo: Materializar el design system base del slice 001 con una UI navegable y reusable.`
  `Criterios de aceptacion: Existen rutas publicas reales, shared UI inicial y estilos alineados a frontend_visual_alignment.md sin usar Tailwind CDN ni links '#'.`
  `Paralelismo[P]: No`
- [x] 2.2 Centralizar consumo API y dejar evidencia automatizada del frontend.
  `Objetivo: Preparar el slice para iteraciones posteriores con contratos y checks reproducibles.`
  `Criterios de aceptacion: src/shared/api encapsula llamadas base y errores HTTP; existe al menos una prueba frontend; run-checks ejecuta lint, typecheck, test y build del frontend.`
  `Paralelismo[P]: No`

### QA (QA-001)
- [x] 3.0 Validar arranque y healthcheck del slice base.
  `Objetivo: Confirmar la base tecnica del backend.`
  `Criterios de aceptacion: Las pruebas de smoke del backend pasan.`
  `Paralelismo[P]: Si`
- [x] 3.1 Validar tokens y autenticacion minima sin base de datos externa.
  `Objetivo: Eliminar bloqueos falsos de infraestructura para QA-001.`
  `Criterios de aceptacion: Las pruebas unitarias de seguridad y las de endpoints protegidos pasan localmente.`
  `Paralelismo[P]: No`
- [x] 3.2 Generar evidencia QA reproducible.
  `Objetivo: Dejar trazabilidad clara para el slice 001.`
  `Criterios de aceptacion: Existe docs/opencode/qa/QA-001-results.md con comandos, resultados y decision final.`
  `Paralelismo[P]: No`

## Definition of Done
- [x] Base tecnica backend verificada con pruebas automaticas.
- [x] Healthcheck, raiz y API v1 verificados.
- [x] Utilidades de token y autenticacion minima verificadas.
- [x] Frontend ejecutable implementado en este workspace.
- [x] QA-001 documentado con evidencia reproducible y sin bloqueo falso de infraestructura.
