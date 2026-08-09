# Revisión de Seguridad - Slice BE-006 (Servicios, Veterinarios y Usuarios Internos)

## Resumen

- **Slice:** BE-006
- **Tipo de review:** Seguridad (autenticación, autorización, IDOR/BOLA, aislamiento tenant, tokens, logs, exposición)
- **Estado:** `RESOLVED`
- **Decision:** `APPROVED` con observaciones menores

## Alcance revisado

- **Backend:**
  - `backend/app/api/v1/routers/services.py` — CRUD servicios
  - `backend/app/api/v1/routers/veterinarians.py` — CRUD veterinarios + asignaciones
  - `backend/app/api/v1/routers/internal_users.py` — CRUD usuarios internos + sucursales
  - `backend/app/core/security.py` — autenticación JWT
  - `backend/app/core/config/settings.py` — configuración de secretos
  - `backend/app/application/use_cases/service_use_cases.py` — lógica servicios
  - `backend/app/application/use_cases/veterinarian_use_cases.py` — lógica veterinarios
  - `backend/app/application/use_cases/internal_user_use_cases.py` — lógica usuarios internos
  - Schemas Pydantic: `service_schemas.py`, `veterinarian_schemas.py`, `internal_user_schemas.py`

- **QA:** QA-006 (aprobado previamente)

## Checklist de revisión

- [x] Autenticación en endpoints privados.
- [x] Autorización por rol, permiso y contexto.
- [x] Prevención IDOR/BOLA y aislamiento tenant.
- [x] Password hashing seguro (bcrypt).
- [x] Access tokens con expiración (30 min) + refresh tokens rotativos (7 días).
- [x] Validación de input con Pydantic.
- [x] Logs sin datos sensibles (no se encontró logging en routers).
- [x] Respuesta pública sin campos internos (schemas limpios).
- [x] Paginación y límites de tamaño (max 100).
- [x] Manejo consistente de errores HTTP.

## Hallazgos por severidad

### Blocker

Ninguno.

### Critical

Ninguno.

### Major

**MJR-006-001: Clave secreta hardcoded en configuración de desarrollo**

- **Archivo:** `backend/app/core/config/settings.py` (línea 16)
- **Descripción:** El archivo de configuración contiene `SECRET_KEY: str = "secret-key-for-dev"`. Esta clave se usa para firmar todos los tokens JWT (`create_access_token`, `create_refresh_token`, `create_reset_token`). Si esta configuración llega a producción, cualquier persona con acceso al código puede forjar tokens de acceso y refresh tokens para cualquier usuario.
- **Impacto:** Alto — compromete toda la autenticación del sistema en entornos no desarrollados.
- **Recomendación:** Migrar `SECRET_KEY` a variable de entorno (`os.environ.get("SECRET_KEY")`) con un valor por defecto seguro solo para desarrollo. Documentar que el archivo `.env` debe estar en `.gitignore`.
- **Estado:** Observación — este hallazgo es preexistente del slice BE-005 y no específico de BE-006. Se registra para continuidad.

### Minor

**MIN-006-001: Sesión de base de datos no cerrada en `get_current_db`**

- **Archivo:** `backend/app/api/v1/routers/services.py`, `veterinarians.py`, `internal_users.py`
- **Descripción:** La función `get_current_db()` llama `next(_get_db())` directamente sin garantizar el cierre de la sesión. Si ocurre una excepción durante el procesamiento de la solicitud, la conexión puede no liberarse correctamente al pool.
- **Impacto:** Bajo — posible pérdida de conexiones en escenarios de error.
- **Recomendación:** Usar `contextlib.contextmanager` o un FastAPI `yield` dependency para garantizar `session.close()` en el bloque `finally`.

**MIN-006-002: Sesión de DB no gestionada en endpoint de asignación**

- **Archivo:** `backend/app/api/v1/routers/veterinarians.py` (línea ~250, `assign_service_to_veterinarian`)
- **Descripción:** Se crea `VeterinarianRepositoryImpl(next(get_current_db()))` manualmente dentro del handler. Esta sesión adicional no tiene garantía de cierre y se abre sin pasar por el dependency injection estándar.
- **Impacto:** Bajo — posible fuga de conexión en escenarios de error.
- **Recomendación:** Inyectar el repositorio como dependencia FastAPI o usar `try/finally` para cerrar la sesión.

**MIN-006-003: Body parameter tipado como `dict` en endpoints de asignación**

- **Archivo:** `backend/app/api/v1/routers/veterinarians.py`, `internal_users.py`
- **Descripción:** Los endpoints `assign_service_to_veterinarian` y `assign_branch_to_internal_user` usan `body: dict` en lugar de un schema Pydantic dedicado. FastAPI no valida automáticamente los campos del cuerpo; la validación se hace manualmente con `body.get()`.
- **Impacto:** Bajo — falta validación automática de tipos y constraints. El campo `service_id`/`branch_id` podría recibir valores no enteros sin ser capturado por Pydantic.
- **Recomendación:** Crear schemas `ServiceAssignmentSchema` y `BranchAssignmentSchema` con campos tipados (`service_id: int`, `branch_id: int`).

**MIN-006-004: `InternalUserCreateSchema` acepta `db` como parámetro de constructor**

- **Archivo:** `backend/app/application/use_cases/internal_user_use_cases.py`
- **Descripción:** `CreateInternalUserUseCase.__init__` acepta `db: Optional[Session] = None`. El router lo inyecta manualmente con `get_current_db()`. Esta dependencia de infraestructura en el caso de uso viola el principio de clean architecture (los use cases no deberían conocer Session).
- **Impacto:** Bajo — acoplamiento innecesario entre capa de aplicación e infraestructura.
- **Recomendación:** Mover la verificación `check_user_exists` al repositorio o a un gateway de autenticación, eliminando la dependencia directa de `Session`.

## Evidencia de revisión

### 1. Autenticación — Todos los endpoints requieren Bearer token

Todos los endpoints de los tres routers incluyen `current_user: dict = Depends(get_current_access_user)`, que depende de `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`. Sin token válido, FastAPI retorna 401 automáticamente.

```
services.py:    current_user: dict = Depends(get_current_access_user) — en POST, GET, PUT, PATCH (6 endpoints)
veterinarians.py: current_user: dict = Depends(get_current_access_user) — en POST, GET, PUT, PATCH, POST assign, DELETE (8 endpoints)
internal_users.py: current_user: dict = Depends(get_current_access_user) — en POST, GET, PUT, PATCH, POST assign, DELETE (8 endpoints)
```

### 2. Autorización por rol — Escrita requiere admin/manager

Todos los endpoints de escritura (POST create, PUT update, PATCH deactivate) verifican el rol:

```python
role = current_user.get("role", "user")
if role not in ("admin", "manager"):
    raise HTTPException(status_code=403, detail="Permiso denegado...")
```

Los endpoints GET (lectura) no verifican rol explícitamente pero dependen del aislamiento tenant para prevenir acceso cruzado.

### 3. Aislamiento tenant / IDOR protection

Todos los endpoints extraen `clinic_id` del usuario autenticado:

```python
clinic_id = _get_clinic_id_from_user(current_user)
```

Y lo pasan a los use cases que filtran por `clinic_id` en las consultas SQL. Los GET con ID verifican ownership post-recuperación:

```python
if service.clinic_id != clinic_id:
    raise HTTPException(status_code=403, detail="No tiene acceso a este servicio.")
```

Los endpoints de asignación validan que ambos extremos (recurso origen y destino) pertenezcan al mismo `clinic_id`.

### 4. Validación de input con Pydantic

- **Service:** `name` (1-200 chars), `price` (>0), `duration_minutes` (>0), `description` (max 2000)
- **Veterinarian:** `nombre_completo`, `licencia_profesional`, `especialidad` requeridos; `email` validado como EmailStr; `telefono` (max 30)
- **InternalUser:** `user_id` (>=1), `nombre` (1-200), `rol` (1-50), `branch_ids` (list[int])

Los use cases realizan validación adicional de reglas de negocio (unicidad de nombre/licencia, campos requeridos).

### 5. Datos sensibles en respuestas/logs

- **Schemas de lectura:** No contienen campos de contraseña, token, ni secretos.
  - `ServiceReadSchema`: id, clinic_id, name, description, price, duration_minutes, is_active
  - `VeterinarianReadSchema`: id, clinic_id, nombre_completo, licencia_profesional, especialidad, telefono, email, is_active (datos profesionales públicos)
  - `InternalUserReadSchema`: id, user_id, clinic_id, nombre, rol, branch_ids, is_active
- **Logging:** No se encontró ninguna llamada a `logging` o `logger` en los routers revisados.

### 6. Tokens JWT

- **Access token:** Expira en 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`), tipo `"access"`.
- **Refresh token:** Expira en 7 días, tipo `"refresh"`.
- **Reset token:** Expira en 1 hora, tipo `"reset"`.
- **Algoritmo:** HS256 (symmetric).
- **Verificación:** `verify_access_token` valida el campo `type` para prevenir confusión de tokens.

### 7. Password hashing

Se usa `CryptContext(schemes=["bcrypt"], deprecated="auto")` — bcrypt es adecuado para hashing de contraseñas.

### 8. Paginación y límites

Todos los listados incluyen paginación:
- `page: int = Query(1, ge=1)`
- `size: int = Query(20, ge=1, le=100)` — límite máximo de 100 items.

### 9. Manejo de errores

Consistente en todos los routers:
- 401 sin token válido
- 403 sin permiso o tenant mismatch
- 404 recurso no encontrado
- 409 conflicto (duplicado)
- 422 campo obligatorio faltante
- Mensajes genéricos en español sin stack traces ni detalles internos

## Decision final

- **Decision:** `APPROVED` con observaciones

La implementación de slice BE-006 cumple con los controles de seguridad requeridos:

1. Todos los endpoints están protegidos con autenticación Bearer JWT.
2. Las operaciones de escritura requieren rol admin/manager (403 para otros roles).
3. El aislamiento tenant (`clinic_id`) se aplica en todas las consultas y se verifica ownership en GET por ID.
4. Los endpoints de asignación validan que ambos extremos pertenezcan a la misma clínica.
5. La validación de input es robusta con Pydantic + reglas de negocio en use cases.
6. No hay exposición de datos sensibles en respuestas o logs.
7. Los tokens JWT tienen expiración adecuada y verificación de tipo.
8. El password hashing usa bcrypt.
9. La paginación tiene límite máximo de 100 items.
10. El manejo de errores es consistente y no filtra información interna.

Las observaciones registradas (MJR-006-001, MIN-006-001 a MIN-006-004) son mejoras recomendadas pero no bloquean la aprobación porque:
- MJR-006-001 es un hallazgo preexistente del slice BE-005.
- Las observaciones menores no representan vulnerabilidades explotables directamente en el contexto de este slice.

## Hallazgos previos de slices (continuidad)

| ID | Slice | Severidad | Estado | Descripción |
|---|---|---|---|---|
| MJR-005-001 | BE-005 | Major | OPEN | Clave secreta hardcoded en `settings.py` — afecta todos los slices posteriores incluyendo BE-006 |

## Politica UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.

---

**Fecha de revision:** 2026-08-09
**Revisor:** InVet Security Reviewer (GitHub Copilot agent)
**Siguiente paso recomendado:** Functional review para BE-006
**Motivo:** La revision de seguridad ha sido completada con decision APPROVED. Seguir el flujo de gates definido en `docs/opencode/13_agents_architecture_and_gate_flow.md`.
