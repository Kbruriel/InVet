---
encoding: UTF-8
artifact: review_findings
slice: "004"
type: security_review
decision: APPROVED
---

# Revisión de Seguridad - BE-004: Perfil público clínica/sucursal

## Resumen

- **Slice**: BE-004 / FE-004 / QA-004
- **Tipo de review**: Seguridad (OWASP Top 10, IDOR/BOLA, exposición de datos)
- **Estado**: `RESOLVED`
- Decision: APPROVED

## Alcance revisado

- **Backend**: Endpoints públicos y protegidos de perfil de sucursal, servicios, horarios, rating summary, disponibilidad.
- **Frontend**: Ruta pública `/clinics/[id]`, ruta protegida `/clinics/[clinicId]/branches/[branchId]`.
- **QA**: QA-004 results APPROVED, findings RESOLVED.

## Evidencia

| Fuente | Estado |
|---|---|
| `docs/opencode/plans/BE-004-plan.md` (security section) | Plan con riesgos documentados |
| `backend/app/api/v1/routers/branch_profile.py` | Endpoints públicos y protegidos implementados |
| `backend/app/api/v1/routers/public_branches.py` | Endpoint público de listado con paginación |
| `backend/app/api/v1/schemas/branch_public.py` | DTOs públicos sin campos sensibles |
| `backend/app/api/v1/schemas/branch_protected.py` | DTOs protegidos sin campos sensibles |
| `backend/app/application/use_cases/branch_profile.py` | Use cases con validación de acceso |
| `backend/app/core/security.py` | JWT validation, password hashing (bcrypt) |
| `backend/app/infrastructure/database/repositories/branch_repository.py` | is_branch_accessible() con tenant isolation |
| `backend/app/domain/entities/branch.py` | Entidades del dominio |
| `backend/app/core/config/settings.py` | Configuración de seguridad |
| `docker-compose.yml` | SECRET_KEY con fallback production-ready |
| `docs/opencode/qa/QA-004-results.md` | APPROVED |
| `docs/opencode/reviews/BE-004-review.md` | APPROVED |
| `backend/app/tests/test_branch_profile.py` | 4/4 tests PASSED (incluye test de denegación) |

---

## Análisis de Seguridad por Categoría

### 1. Autenticación en Endpoints Privados

**Estado: APROBADO**

- El endpoint protegido `GET /clinics/branches/{clinic_id}/{branch_id}` utiliza `Depends(get_current_access_user)` que requiere un token Bearer JWT válido.
- `get_current_access_user()` valida el tipo de token (`access`), verifica el `sub` claim, y convierte a user_id.
- Tokens inválidos o sin `type=access` retornan 401 con mensaje genérico "Token inválido".
- El endpoint público `GET /clinics/branches/{branch_id}` no requiere autenticación (comportamiento esperado).

**Evidencia**: `backend/app/core/security.py` — `get_current_access_user()`, `verify_access_token()`.

### 2. Autorización por Rol y Contexto

**Estado: APROBADO**

- `is_branch_accessible()` en `BranchRepositoryImpl` valida:
  - Si el usuario tiene rol `admin`, permite acceso directo.
  - Para usuarios no-admin, verifica que exista un `Owner` activo vinculado a la clínica con el email del usuario.
  - La consulta SQL filtra por `clinic_id` y `email` simultáneamente.
- El use case `GetBranchProtectedProfileUseCase.execute()` realiza doble validación: primero `is_branch_accessible()`, luego verifica que `branch.clinic_id == clinic_id`.

**Evidencia**: `backend/app/infrastructure/database/repositories/branch_repository.py` — `is_branch_accessible()`.

### 3. Prevención IDOR/BOLA

**Estado: APROBADO**

- El endpoint protegido devuelve **404** (no 403) cuando el usuario no tiene acceso, previniendo la enumeración de recursos existentes.
- La validación verifica tanto `branch_id` como `clinic_id` en la consulta SQL:
  ```python
  BranchModel.id == branch_id AND BranchModel.clinic_id == clinic_id
  ```
- El use case realiza una segunda verificación: `branch.clinic_id != clinic_id` retorna None.
- QA-004-T02 (cross-tenant) aprobada con evidencia de test en `test_branch_profile.py`.

**Evidencia**: `backend/app/api/v1/routers/branch_profile.py` — comentario "IDOR mitigation"; `backend/app/application/use_cases/branch_profile.py` — doble validación.

### 4. Aislamiento por Tenant

**Estado: APROBADO**

- La consulta de acceso filtra por `clinic_id` en el repositorio.
- El Owner model verifica la relación entre clínica y email del usuario.
- No hay forma de acceder a datos de otra clínica sin ser admin.

**Evidencia**: `backend/app/infrastructure/database/repositories/branch_repository.py` — `is_branch_accessible()`.

### 5. Password Hashing y Tokens

**Estado: APROBADO con observaciones**

- **Password hashing**: Se usa `CryptContext(schemes=["bcrypt"])` en `core/security.py`. Bcrypt es aceptable para MVP (Argon2id sería preferible para producción).
- **Access tokens**: Expiran en 30 minutos (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Refresh tokens**: Expiran en 7 días.
- **Reset tokens**: Expiran en 1 hora.
- **Algoritmo**: HS256 (HMAC-SHA256). Aceptable para MVP; RS256 sería preferible para producción.

**Evidencia**: `backend/app/core/security.py` — `pwd_context`, `create_access_token()`, `create_refresh_token()`.

### 6. Validación de Input y Errores sin Detalles Internos

**Estado: APROBADO**

- Todos los endpoints usan Pydantic para validación de schemas.
- Los errores HTTP retornan mensajes genéricos ("Sucursal no encontrada", "Token inválido").
- No se exponen stack traces ni información SQL en las respuestas.
- El endpoint `public_branches.py` captura `ValueError` y `Exception` con mensajes genéricos.
- `branch_id` y `clinic_id` son validados como `int` por FastAPI automáticamente.

**Evidencia**: `backend/app/api/v1/routers/branch_profile.py`, `backend/app/api/v1/routers/public_branches.py`.

### 7. Exposición de Datos Sensibles en Respuestas Públicas

**Estado: APROBADO**

- Los DTOs públicos (`BranchPublicProfile`, `ServicePublic`, `BranchSchedulePublic`, `RatingSummaryPublic`, `AvailabilitySummaryPublic`) solo incluyen campos necesarios para la visualización pública.
- **No se exponen**: passwords, internal_notes, role, email del propietario, IDs internos de Owner, created_at/updated_at (excepto en rating summary como metadata agregada).
- Los DTOs protegidos tienen el mismo conjunto de campos que los públicos — no hay filtración adicional de datos sensibles.

**Evidencia**: `backend/app/api/v1/schemas/branch_public.py`, `backend/app/api/v1/schemas/branch_protected.py`.

### 8. SQL Injection

**Estado: APROBADO**

- Todas las consultas usan SQLAlchemy ORM con filtros posicionales (`==`, `.filter()`).
- La búsqueda por nombre/ciudad usa `ilike(f"%{search_lower}%")` que es seguro en SQLAlchemy (parameterized).
- No hay queries crudas ni f-strings directos en SQL.

**Evidencia**: `backend/app/infrastructure/database/repositories/branch_repository.py`.

### 9. CORS

**Estado: OBSERVACION — Sin configuración explícita de CORS**

- No se encontró `CORSMiddleware` configurado en el código del backend.
- Los comentarios en los routers mencionan que CORS debe configurarse en `main.py` con el origen del frontend.
- En producción, esto debe resolverse antes de desplegar si el frontend y backend están en dominios diferentes.
- Para MVP con frontend/backend en el mismo dominio o desarrollo local, no es un bloqueo.

**Evidencia**: Comentarios en `public_branches.py`, `public_clinics.py`, `public_services.py`.

### 10. Rate Limiting

**Estado: OBSERVACION — No implementado explícitamente**

- El endpoint de listado público menciona "Rate limit: 60 requests per minute" en el comentario, pero no hay evidencia de implementación real.
- Para MVP es aceptable; debe implementarse antes de producción (middleware como slowapi o nginx).

**Evidencia**: Comentario en `backend/app/api/v1/routers/public_branches.py` línea 35.

### 11. Secretos y Configuración

**Estado: OBSERVADO — Clave de desarrollo por defecto**

- `SECRET_KEY` tiene valor `"secret-key-for-dev"` como default en `settings.py`.
- `.env.example` también muestra `"secret-key-for-dev"`.
- `docker-compose.yml` usa `${SECRET_KEY:-change-me-in-production}` para el contenedor backend (mejor práctica).
- Para producción, se requiere una clave fuerte generada criptográficamente.

**Evidencia**: `backend/app/core/config/settings.py` línea 16; `backend/.env.example`; `docker-compose.yml`.

### 12. Logs sin Datos Sensibles

**Estado: OBSERVADO — No hay evidencia de sanitización de logs**

- El LOG_LEVEL está configurado en INFO.
- No se encontró middleware o configuración explícita que filtre datos sensibles de los logs.
- Para MVP es aceptable; debe implementarse antes de producción (filtros de logging para PII, tokens, passwords).

### 13. Cookies, CSRF y Almacenamiento de Sesión

**Estado: OBSERVADO — No aplica para MVP con JWT**

- La aplicación usa JWT en header Authorization (OAuth2PasswordBearer), no cookies.
- Por lo tanto, CSRF no es un riesgo directo para la API.
- El frontend debe evitar almacenar tokens en localStorage si hay XSS risk; sessionStorage o httpOnly cookies serían preferibles.

---

## Hallazgos por Severidad

### Minor

| ID | Descripción | Nivel | Estado |
|---|---|---|---|
| FIND-004-S1 | SECRET_KEY con valor de desarrollo por defecto en settings.py | Minor | ACCEPTED_RISK (MVP) |
| FIND-004-S2 | Sin middleware CORS explícito configurado | Minor | ACCEPTED_RISK (MVP) |
| FIND-004-S3 | Sin rate limiting implementado para endpoints públicos | Minor | ACCEPTED_RISK (MVP) |
| FIND-004-S4 | Sin sanitización explícita de logs para PII/tokens | Minor | ACCEPTED_RISK (MVP) |

### Critical/Major/Blocker

**Ninguno.** No se encontraron vulnerabilidades explotables.

---

## OWASP Top 10 Coverage

| Vulnerabilidad | Riesgo en BE-004 | Mitigación |
|---|---|---|
| A01: Broken Access Control | Bajo | is_branch_accessible() + doble validación + 404 para unauthorized |
| A02: Cryptographic Failures | Bajo-Medio | Bcrypt para passwords; JWT HS256 con expiración |
| A03: Injection | Bajo | SQLAlchemy ORM (parameterized); no queries crudas |
| A04: Insecure Design | Bajo | DTOs sin datos sensibles; separación público/protegido |
| A05: Security Misconfiguration | Bajo-Medio | SECRET_KEY dev por defecto; CORS pendiente |
| A06: Vulnerable Components | No aplica | Sin dependencias conocidas con CVE crítico |
| A07: Auth Failures | Bajo | JWT validation con type check + sub claim verification |
| A08: Data Integrity | Bajo | Pydantic validation en todos los endpoints |
| A09: Logging Failures | Bajo | Sin evidencia de filtración; pendiente sanitización |
| A10: SSRF | No aplica | No hay funcionalidad de URL fetching |

---

## Decision Final

- **Decision**: `APPROVED`
- **Evidencia**: 
  - QA-004 results APPROVED con todos los criterios PASS.
  - Endpoints públicos sin auth, protegidos con auth + access validation.
  - IDOR mitigado con 404 para unauthorized access.
  - DTOs excluyen campos sensibles (password, internal_notes, role, email).
  - SQLAlchemy ORM previene SQL injection.
  - JWT tokens con expiración y validación de tipo.
  - Tests unitarios cubren happy path y denegación de acceso.
- **Riesgos aceptados para MVP**: SECRET_KEY dev, CORS pendiente, rate limiting pendiente, sanitización de logs pendiente.

---

## Politica UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
