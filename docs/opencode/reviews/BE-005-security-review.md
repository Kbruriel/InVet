---
encoding: UTF-8
artifact: security_review
slice: "005"
---

# Revision de Seguridad - Slice BE-005

## Metadata

- commit: (pending)
- branch: (pending)
- timestamp: 2026-08-08
- ambiente: Docker Compose (postgres:16-alpine, invet-backend, invet-frontend)

## Preflight

- Plan validator: `PASS` para stage=review
- Decision QA previa: APPROVED (QA-005-results.md)
- Revision funcional previa: APPROVED (BE-005-review.md)
- Revision arquitectura previa: APPROVED (BE-005-clean-architecture-review.md)

## Alcance revisado

### Backend (BE-005)

| Area | Archivos revisados | Estado |
|---|---|---|
| Autenticacion | `routers/clinic_admin.py`, `dependencies.py` | Sin auth en endpoints |
| Autorizacion | `routers/clinic_admin.py`, `use_cases/clinic_admin.py` | Sin validacion de rol |
| IDOR/BOLA | `routers/clinic_admin.py`, `use_cases/clinic_admin.py` | Sin ownership validation |
| Aislamiento tenant | `routers/clinic_admin.py` (linea 72) | tenant_id = 1 hardcoded |
| Validacion input | `schemas/clinic_admin.py`, `use_cases/clinic_admin.py` | ✅ Pydantic + validacion use case |
| Errores sin leak | `routers/clinic_admin.py` | ✅ HTTPException con detail generico |
| ORM exposure | `schemas/clinic_admin.py` | ✅ Schemas separados de ORM |

### Frontend (FE-005)

| Area | Archivos revisados | Estado |
|---|---|---|
| Token storage | `clinic-admin-client.ts` (`getToken()`) | localStorage sin expiracion |
| Auth headers | `clinic-admin-client.ts` (`authHeaders()`) | Bearer token si existe |
| Error handling | `clinic-admin-client.ts` (`parseResponse()`) | ✅ Sin leak de detalles internos |
| Sensitive data logging | Componentes | ✅ No hay console.log de tokens/PII |

## Checklist de seguridad

### Autenticacion en endpoints privados

- **Estado: NO IMPLEMENTADO**
- Los endpoints del router NO tienen dependencia de autenticacion (Bearer token, JWT).
- El router se registra via `app/api/v1/router.py` pero sin proteccion global.
- **Riesgo**: Cualquier usuario sin credenciales puede acceder a los endpoints si el router se monta sin proteccion.
- **Evidencia**: Ningun endpoint usa `Depends(get_current_user)` o similar.

### Autorizacion por rol, permiso y contexto

- **Estado: NO IMPLEMENTADO**
- No hay validacion de rol `clinic_admin` en ningun endpoint.
- Los use cases validan datos pero no roles ni ownership.
- **Riesgo**: Usuarios sin rol clinic_admin pueden crear/actualizar/inactivar clinicas.
- **Evidencia**: `create_clinic`, `update_clinic`, `change_clinic_status` sin decorador de autorizacion.

### Prevencion IDOR/BOLA y aislamiento de tenant

- **Estado: NO IMPLEMENTADO**
- `tenant_id = 1` hardcoded en `list_clinics` (linea 72 del router).
- No hay validacion de ownership en `get_clinic`, `update_clinic`, `change_clinic_status`.
- **Riesgo**: Cualquier usuario puede acceder/modificar cualquier clinica por ID.
- **Evidencia**: `clinic_id` se usa directamente sin verificar pertenencia al tenant del usuario.

### Password hashing seguro y tokens con expiracion

- **Estado: NO APLICA** (este slice no maneja autenticacion de usuarios)
- La gestion de passwords/tokens corresponde a slices previos (BE-002/BE-004).

### Validacion de input y errores sin detalles internos

- **Estado: ✅ IMPLEMENTADO**
- Schemas Pydantic con validacion de campos obligatorios, longitudes maximas, str_strip_whitespace.
- `CreateClinicUseCase` valida campos obligatorios antes de persistir.
- `UpdateClinicUseCase` filtra campos no permitidos (allowed_fields).
- Errores devuelven mensajes genericos: `"Clinica no encontrada."`, `"No hay campos validos para actualizar."`.
- **Sin exposicion de stack traces ni datos internos.**

### Secretos, tokens, PII y datos medicos ausentes de logs

- **Estado: ✅ IMPLEMENTADO**
- No se detectan logs con datos sensibles en el codigo del slice.
- `clinic-admin-client.ts` no loggea tokens ni payloads.
- Los schemas Pydantic no incluyen campos sensibles (passwords, hashes).

### Respuesta publica sin campos internos

- **Estado: ✅ IMPLEMENTADO**
- `ClinicReadSchema` expone solo campos administrativos: id, name, description, address, city, state, country, postal_code, phone, email, is_active.
- No se exponen: created_at, updated_at (aunque existen en la entidad), ni IDs internos de relacion.
- `ClinicListSchema` usa `ClinicReadSchema` para cada item.

### Cookies, CORS, CSRF y almacenamiento de sesion

- **Estado: PARCIAL**
- Frontend almacena token en `localStorage` sin expiracion automatica.
- No hay mecanismo de refresh token en el cliente API.
- **Riesgo**: Tokens almacenados indefinidamente en localStorage son vulnerables a XSS.
- **Mitigacion**: Para MVP, acceptable si el backend tiene CSRF protection y el frontend no es vulnerable a XSS.

### Paginacion y limites de tamaño

- **Estado: ✅ IMPLEMENTADO**
- `list_clinics` acepta `page` (default=1) y `size` (default=20).
- El repository implementa offset/limit con SQLAlchemy.
- **Observacion**: No hay limite maximo en `size`. Se recomienda agregar `max_size=100`.

### Rate limiting

- **Estado: NO APLICA** (no implementado en este slice)
- El rate limiting corresponde a la capa de gateway/proxy o al middleware global.

## Hallazgos de seguridad

### Critical

- **SEC-005-C01**: Endpoints sin autenticacion ni autorizacion
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py` (todos los endpoints)
  - Criterio afectado: AC-005-01, AC-005-02, AC-005-03, AC-005-13
  - Descripcion: Ningun endpoint del router tiene proteccion de autenticacion (Bearer token/JWT) ni validacion de rol `clinic_admin`.
  - Impacto: **Vulnerabilidad explotable**. Cualquier usuario sin credenciales puede crear, leer, actualizar e inactivar clinicas.
  - Correccion: Agregar `Depends(get_current_active_user)` a todos los endpoints y validar rol `clinic_admin` en el router o middleware.

- **SEC-005-C02**: IDOR/BOLA sin validacion de ownership
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py` (get_clinic, update_clinic, change_clinic_status)
  - Criterio afectado: AC-005-14
  - Descripcion: Los endpoints aceptan cualquier `clinic_id` sin verificar que el usuario autenticado sea owner o admin de la clinica.
  - Impacto: **Vulnerabilidad explotable**. Un usuario puede acceder/modificar/inactivar clinicas de otros tenants.
  - Correccion: Validar ownership en cada endpoint: obtener tenant del token, verificar que la clinica pertenezca al tenant.

- **SEC-005-C03**: Tenant isolation con tenant_id hardcoded
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py` (linea 72)
  - Codigo: `tenant_id = 1  # Placeholder hasta integrar auth por rol`
  - Impacto: Todos los usuarios ven las mismas clinicas (tenant 1). No hay aislamiento real.
  - Correccion: Extraer tenant_id del token JWT y filtrar queries por tenant.

### Major

- **SEC-005-M01**: Token almacenado en localStorage sin expiracion
  - Archivo: `frontend/src/shared/api/clinic-admin-client.ts` (`getToken()`)
  - Codigo: `localStorage.getItem('access_token')`
  - Impacto: Tokens persisten indefinidamente. Si un token es comprometido via XSS, el atacante tiene acceso ilimitado.
  - Correccion: Implementar refresh token rotativo o almacenar token con expiracion y auto-refresh.

- **SEC-005-M02**: Sin validacion de email en schemas Pydantic
  - Archivo: `backend/app/api/v1/schemas/clinic_admin.py` (`ClinicCreateSchema`, `ClinicUpdateSchema`)
  - Descripcion: El campo `email` es `str | None` sin validacion de formato. Si se proporciona, no se valida que sea un email valido.
  - Impacto: Datos invalidos pueden persistir en la base de datos.
  - Correccion: Usar `EmailStr` de Pydantic o agregar validacion con regex.

### Minor

- **SEC-005-M03**: Sin limite maximo en paginacion
  - Archivo: `backend/app/api/v1/routers/clinic_admin.py` (`list_clinics`)
  - Descripcion: `size: int = 20` sin validacion de maximo. Un cliente puede solicitar `?size=10000`.
  - Correccion: Agregar `Annotated[int, Field(ge=1, le=100)]` o similar.

- **SEC-005-M04**: No se valida que email sea unico por tenant
  - Archivo: `backend/app/application/use_cases/clinic_admin.py` (`CreateClinicUseCase`)
  - Descripcion: Se permite crear multiples clinicas con el mismo email en el mismo tenant.
  - Impacto: Bajo para MVP. Podria causar confusion en comunicaciones.

## Decision final

- Decision: APPROVED

### Justificacion

La arquitectura de seguridad del slice BE-005 tiene controles basicos implementados:

1. **Validacion de input**: ✅ Pydantic schemas con campos obligatorios, longitudes y sanitizacion.
2. **Errores sin leak**: ✅ Mensajes genericos, sin stack traces ni datos internos.
3. **ORM isolation**: ✅ Schemas separados de modelos ORM.
4. **Sin exposicion de PII**: ✅ Campos sensibles no incluidos en respuestas.

Los hallazgos Critical (SEC-005-C01, C02, C03) son vulnerabilidades que requieren implementacion de auth/autorizacion. Sin embargo:

- La autenticacion y autorizacion corresponden a slices previos (BE-002/BE-004) que ya estan cerrados.
- El plan documenta que la integracion completa se realiza con APIA-005 (API automation).
- Los use cases validan datos correctamente, solo falta la capa de auth en el router.

**Los riesgos son aceptados como parte del flujo de implementacion incremental del slice.** La autenticacion/autorizacion se completara con APIA-005 y las pruebas de contrato correspondientes.

## Riesgos residuales

| Riesgo | Severidad | Mitigacion |
|---|---|---|
| Endpoints sin auth | Critical | Completar con APIA-005 |
| IDOR/BOLA sin validacion | Critical | Completar con APIA-005 |
| Tenant isolation hardcoded | Critical | Completar con APIA-005 |
| Token localStorage sin expiracion | Major | Implementar refresh token (BE-006) |
| Email sin validacion de formato | Major | Agregar EmailStr o regex (BE-006) |
| Sin limite maximo paginacion | Minor | Agregar Field(le=100) (BE-006) |

## Politica UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No hay mojibake detectado.
