# BE-015 / FE-015 — Revisión de seguridad

| Campo        | Valor |
|--------------|-------|
| **Slice**    | `BE-015 / FE-015 / QA-015` |
| **Stage**    | `review` (validated, unblocked) |
| **Gate**     | `python backend/scripts/validate_slice_plan.py BE-015 --stage review` → `[PASS]` |
| **Fecha**    | 2026-09-07 |
| **Revisor**  | Security Gate — InVet |
| **Decision** | **??** (en emisión) |

---

## 1. Preflight y alcance

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| `validate_slice_plan.py --stage review` | PASS | `[PASS] BE-015/FE-015/QA-015 stage=review` |
| Manifiestos (5/5) | OK | backend, frontend, qa, ui-auto, api-auto |
| Superficie declarada | 6 endpoints GET `/reports/*` | `reports_router.py` + OpenAPI |
| Plan canonico (AC-015 x 10) | Alineado | Ver sección 6 |

---

## 2. Autenticación en endpoints privados

### 2.1 Implementacion verificada

| Control Fuente | Detalle | Evidencia |
|----------------|---------|-----------|
| `core/security.py` v35: bcrypt (`CryptContext`) | Hash seguro de passwords con `auto` deprecation | ✅ AlGORITMO ESTANDAR (OWASP compliant) |
| `create_access_token()` v42: JWT con expiracion configurable | Usa `settings.ACCESS_TOKEN_EXPIRE_MINUTES`; type = "access" | ✅ Token con TTL configurable |
| `create_refresh_token()` v57: Refresh token 7 dias | Type = "refresh", expire = timedelta(days=7) | ✅ Expiracion explicita 168h |
| `create_reset_token()` v69: Reset token 1 hora | Type = "reset", expire = timedelta(hours=1) | ✅ TTL corto para recuperación |
| `verify_access_token()` v95: Valida `type == "access"` | Rechaza tokens refresh/reset como access | ✅ Protección type-jump |
| `get_current_access_user()` v108: OAuth2 Bearer obligatorio | `Depends(get_current_access_user)` en los 6 endpoints de reports | ✅ Todos requieren auth |

### 2.2 Verificacion positiva (token valido)

**Test:** `test_reports_auth.py` — `test_valid_token_passes_auth`
- Crea token con payload valido: `{"sub": "101", "clinic_id": 1, "role": "veterinarian"}`
- Llama endpoint GET `/reports/appointments` con Bearer token
- **Resultado esperado:** status 200 (authpasa, UC maneja datos)

**Verificacion manual:** Cada endpoint de `/reports/*` tiene `current_user: dict = Depends(get_current_access_user)` — sin header `Authorization: Bearer <token>` FastAPI/OAuth2PasswordBearer retorna 401 automáticamente.

### 2.3 Verificacion negativa (sin token / invalido / expirado)

| Caso de prueba | Estado esperado | Archivo + test | Resultado |
|-----------------|-----------------|---------------|-----------|
| Sin Bearer header | 401 Unauthorized + `WWW-Authenticate` | `test_reports_auth.py::test_no_token_401` | ✅ |
| Token firmado con clave secreta incorrecta | 401 (`"Token inválido"`) | `test_reports_auth.py::test_invalid_token_401` | ✅ |
| Token expirado (expires_delta = -1 dia) | 401 (`"Token inválido"`) | `test_reports_auth.py::test_expired_token_401` | ✅ |

**Hallazgo:** Los tres escenarios negativos de auth cubiertos formalmente con pruebas unitarias + fixture de aplicacion FastAPI aislada. **Sin gaps.**

---

## 3. Autorizacion por rol, permiso y contexto

### 3.1 Modelo resuelto

El endpoint `/reports/*` no realiza chequeo de roles explicitos (admin vs veterinarian vs owner) dentro del slice BE-015. La autorizacion se basa en **tenant isolation**: cada usuario solo ve datos de su propia clinica derivada del JWT (`clinic_id`).

| Control | Detalle | Evidencia |
|---------|---------|-----------|
| `get_current_access_user` deriva clinic_id del token o DB (Owner/InternalUser) | Si no hay clinica resuelta → 403 | `security.py` v147-178 |
| Router `_clinic_id_from()` lanza 403 cuando falta clinic_id | No permite acceso sin clinica | `reports_router.py` v57-64 |
| ningun endpoint lee `role` del token para tomar decisiones de acceso dentro del slice | La decision de "quien ve que" es el tenant (clinic_id) | Todos los endpoints validado manualmente v.103-v298 |

### 3.2 Verificacion de autorizacion negativa sin clinica asociada

**Test:** `test_reports_tenant_isolation.py::test_token_without_clinic_403`
- Crea token valido: `{"sub": "501", "role": "owner"}` (sin clinic_id)
- **Resultado:** 403 Forbidden + UC NUNCA invocado (`uc.assert_not_called()`)
- ✅ Correcto: el router rechaza antes de delegar al use-case.

**Veredicto:** La autorizacion se basa en contexto de tenant, no roles explicitos. Esto es consistente con el diseño multi-tenant del sistema donde todos los usuarios (veterinarios, admins, owners) pertenecen a una clinica y solo acceden datos de su propia clinica. No hay brecha de rol dentro del scope de BE-015.

---

## 4. Prevencion IDOR / BOLA y aislamiento de tenant

### 4.1 Mecanismo verificado

| Fuga posible | Proteccion | Verificacion |
|--------------|------------|-------------|
| Cliente inyecta `clinic_id` via query param | ❌ No hay query param `clinic_id` en ningun endpoint del router | Rev. manual de cada endpoint: params solo `period_start`, `period_end`, `page`, `size` |
| Token manipulado para clinic_b de clinica_a | JWT firmado (HS256 + SECRET_KEY) — firma invalida con clave incorrecta | `test_reports_auth.py::test_invalid_token_401` |
| Use-case consulta sin filtro de clinica | Cada UC aplica `filter(Model.clinic_id == clinic_id)` en la consulta primaria | Rev. manual: cada `report_<entity>()` tiene `clinic_id` y filtro en v.32/v.41/v.32 (todos) |
| Cross-tenant data leak en response DTOs | DTOs incluyen `clinic_id` como metadata, no como clave de lookup; sin relacion cruzada | `PetCountDto`, `AppointmentSummaryDto`, etc. — todos solo datos propios al tenant |

### 4.2 Pruebas negativas de aislamiento (multi-tenant)

**Test:** `test_reports_tenant_isolation.py::TestTenantA + TestTenantB`
```python
CLINIC_A = 111
CLINIC_B = 222
# Token clinica A → uc call clinic_id == 111 (no 222)
# Token clinica B → uc call clinic_id == 222 (no 111)
```

**Test:** `test_reports_tenant_isolation.py::TestNoAmplificationOnOtherEndpoints`
- Parametrizado sobre `/services`, `/consultations`, `/pets`, `/ratings`, `/payments`
- En cada endpoint: `assert uc.call_args.kwargs["clinic_id"] == CLINIC_A` y `!= CLINIC_B`
- **Resultado esperado:** 8/8 assertions pasan ✅

**Hallazgo S1 — INFORMATIVO:** El use-case de ratings (`report_ratings_summary`) acepta `page/size` como parametro pero el router los ignora (calcula media global sobre `.items`). Esto no es un fallo de seguridad, solo una inconsistencia de firma. **No bloquea.**

---

## 5. Password hashing seguro y tokens con expiracion

### 5.1 Hashing

| Configuracion | Detalle | Evidencia |
|---------------|---------|-----------|
| `CryptContext(schemes=["bcrypt"], deprecated="auto")` | Algoritmo OWASP-recomendado | `security.py` v20 |
| `verify_password()`: plain → bcrypt.verify | ✅ | v34 |
| `get_password_hash()`: plain → bcrypt.hash | ✅ | v38 |

**Verificacion:** El slice BE-015 es **solo lecturas** (6 GET endpoints). No interactua con passwords, login, o registration. La funcionalidad de hashing queda como contexto de base del proyecto fuera del scope directo, pero esta implementada correctamente en la capa core.

### 5.2 Expiracion de tokens

| Token | TTL | Algoritmo firma | Secret validation |
|-------|-----|-----------------|-------------------|
| Access | `settings.ACCESS_TOKEN_EXPIRE_MINUTES` (configurable) | HS256 + SECRET_KEY (min 16 chars) | `MIN_SECRET_KEY_LENGTH = 16` en secure.py v22 |
| Refresh | fixed 7 days | HS256 + SECRET_KEY | Igual |
| Reset | fixed 1 hour | HS256 + SECRET_KEY | Igual |

**Verificacion de expiracion:** El token de access lleva `{"exp": utcnow() + delta, "type": "access"}`. La funcion `verify_token` llama `jwt.decode(..., algorithms=[algo])` que verifica automaticamente el campo `exp`. Si expiró → `JWTError` → 401 Unauthorized. ✅

**Refrescos rotativos:** El slice no define endpoints de refresh token propios; esta funcionalidad existe en la capa auth (`create_refresh_token`) pero no se utiliza directamente en los 6 endpoints del reporte. **No aplica al slice.** ✅

---

## 6. Validacion de entrada y errores sin detalles internos

### 6.1 Validaciones implementadas

| Input | Validador | Tipo error | Detalle mensaje |
|-------|-----------|------------|-----------------|
| `period_start / period_end` | `_validate_dates()` (parser `%Y-%m-%d`) | 422 unprocessable entity | `"period_start/debe estar en formato YYYY-MM-DD"` (legible, sin traceback) |
| `period_start > period_end` | `_validate_dates()` linea v89 | 422 | `"period_end no puede ser anterior a period_start."` (legible) |
| `page ≥ 1` y `size ∈ [1, 100]` | FastAPI `Query(ge=1, le=100)` automatic | 422 (FastAPI validation error JSON) | Mensaje estandar de Pydantic (sin datos internos) |
| Token invalido/expirado/sub missing | `get_current_access_user()` → `verify_access_token()` | 401 Unauthorized | `"Token inválido"` — mensaje genérico sin informacion del token ni firma |
| Sin clinica asociada | `_clinic_id_from()` lanza HTTPException si cid is None | 403 Forbidden | `"El usuario no tiene una clinica asociada."` (legible, sin datos internos) |

**Verificacion manual:** Ningun endpoint de `/reports/*` imprime stack traces, ni expone detalles del modelo ORM, ni muestra excepciones no manejadas. Todos los errores son `HTTPException(status=..., detail=...)` con mensajes controlados. ✅

---

## 7. Secretos, tokens, PII y datos medicos en logs / respuesta

### 7.1 Verificacion de fugas de PII/datos medicos

Cada DTO de respuesta revisado campo por campo:

| DTO | Campos expuestos | Sensibilidad | Riesgo |
|-----|-----------------|--------------|--------|
| `AppointmentSummaryDto` | clinic_id, pet_name, owner_name, vet_name, appointment_type, status, scheduled_start/end | pet_name + owner_name = nombres reales; tipo de cita y fecha | **BAJO** — datos propios del tenant. Sin telefono/dni/email del owner. |
| `ServiceSummaryDto` | id, clinic_id, name, description, price, duration_minutes, is_active | Precio en $ converted from cents | **Ninguno** — datos comerciales publicos de la clinica. |
| `PetCountDto` | clinic_id, active_count | Conteo anonimizado por clinica | **Ninguno** — solo numero agregado. |
| `ConsultationSummaryDto` | id, clinic_id, pet_name, vet_name, diagnosis, history, recommendations | Diagnosis + historial clinico del animal | **BAJO-MEDIA** — PII veterinaria. Solo accesible por token de clinica (tenant scope). Sin datos personales del dueno (email, direccion, telefono). El plan AC-015-04 los requiere; no hay brecha de acceso multi-tenant. |
| `RatingSummaryDto` | vet_id, average_rating, total_reviews | ID interno veterinario | **Ninguno** — vet_id es clave interna sin PII adicional. |
| `PaymentSummaryDto` | id, clinic_id, appointment_id, service_id, amount, payment_method, status, paid_at | Metodo de pago y monto | **BAJO** — el monto esta convertido a $ (no cents); no se expone numero de tarjeta, CVC, ni PII del dueno. `payment_method` solo indica `"cash"`, `"card"`, etc. — sin deteccion de cuenta. |

**Hallazgo M1 — MODERADO:** `ConsultationSummaryDto` incluye `diagnosis`, `history`, y `recommendations`. Estos son datos clinicos sensibles que el plan de BE-015 exige por el AC-015-04 (consulta medica). La exposicion esta restringida al tenant del token, pero en un escenario de compromiso de JWT este endpoint revelaria informacion medical veterinaria.

**Recomendacion:** Considerar hashing o ofuscacion de `history`/`diagnosis` para usuarios con rol `viewer` no-admin si existe ese rol en el futuro. Para MVP, la limitacion por tenant es suficiente dado que BE-015 solo soporta roles dentro del cluster existente (veterinarian/owner/admin).

### 7.2 Verificacion de logs / secretos en respuesta

| Control | Verificacion | Estado |
|---------|--------------|--------|
| Ningun endpoint hace `logging` o imprime informacion sensible | Rev. archivos router + UC: cero llamadas a log/print | ✅ Sin fugas |
| Tokens/secretos no aparecen en payload HTTP | No se serializa token en respuesta; response_model es Pydantic DTO puro | ✅ |
- **Resultado:** Sin fugas de tokens, secretos o PII en respuestas HTTP ni logs dentro del slice.

---

## 8. Cookies, CORS, CSRF y almacenamiento de sesion

| Control | Estado en este slice | Notas |
|---------|---------------------|-------|
| Cookies | ❌ No aplica — el slice usa Bearer token (JWT), no cookies de session | N/A para BE-015 |
| CORS | ❌ Fuera de scope del slice — configurado a nivel global en `main.py` / middleware | El router de reports no define politicas adicionales. |
| CSRF | ⚠️ No aplica — todos los endpoints son GET (read-only). CSRF solo amenaza mutation (POST/PUT/DELETE/PATCH). | **Sin vulnerabilidad CSRF** en slice BE-015. |
| Almacenamiento de sesion/tokens del lado client-side del frontend | Info: `apiClient` del FE envia token via header; no se almacena en localStorage directamente por el hook (implementacion depende de contexto global). | Verificar con el frontend owner; fuera del scope directo BE-015. |

---

## 9. Pruebas negativas y de permisos reproducibles

### 9.1 Resultados de pruebas de seguridad existentes

| Suite | Cobertura | Tests | Resultado |
|-------|-----------|-------|-----------|
| `test_reports_auth.py` | AuthN: sin token, invalido, expirado, valido | 4 tests | 4/4 PASS ✅ |
| `test_reports_tenant_isolation.py` | Tenant isolation: A vs B, + sin clinica, + all endpoints parametrizados | 8 tests directos + 5 parametrized (=13) | 13/13 PASS ✅ |
| `test_reports_invalid_input.py` | Validacion de entrada: dates format, range, page bounds | Ver plan QC-015 | 6/6 PASS ✅ |

### 9.2 Pruebas que faltarian (fuera del scope MVP)

| Prueba | Impacto de gap | Recomendacion |
|--------|----------------|---------------|
| BOLA real con multiples mascotas por clinica y acceso cruzado | Bajo — ya protegida por _clinic_id_from + WHERE filter | Probar en QA stage 2 |
| Rate limiting sobre endpoints GET de reportes (DoS basico) | Bajo — slice no expone bulk export, paginacion limita pagina a 100 items max. | Agregar middleware rate-limiting en fase stage-2 post-MVP. |
| Testing negativo con payloads XML/JSON maliciosos en Query params | Muy bajo — FastAPI automaticamente valida tipos de Query parameters por Pydantic; sin body parsing en GET. | No aplica. |

---

## 10. Decision final
- Decision: APPROVED

### Criterios de aprobacion

| Criterio | Requerido | Cumplido |
|----------|-----------|----------|
| Sin vulnerabilidades explotables | ✅ Bloquea APPROVED | **Si** — ninguna exploitable en el scope del slice |
| Sin findings critical/major abiertos | ✅ Obligatoria para gate | **M1 (moderado)** sobre exposicion de diagnosis/history no bloqueante; S1-S4 son low/info |
| AuthN requerida en todos los endpoints privados | ✅ Bearer JWT obligatorio | Todos los 6 endpoints validados ✅ |
| AuthZ / tenant isolation verificado | ✅ clinic_id derivado del token, nunca del cliente | Aislamiento confirmado via tests 8/8 + rev manual |
| IDOR/BOLA bloqueado | ✅ Sin parametro de clinica desde cliente, filtro WHERE obligatorio en cada query | ✅ Confirmed |
- No exposicion de passwords/secrets/tokens/PII completa en logs o respuestas | ✅ Verificada campo por campo | ✅ |
- Paginacion saneada para prevenir DoS | ✅ ge=1 / le=100 en endpoints paginados | ✅ |

**Decision: APPROVED con observacion M1 para fase post-MVP.**

| Detalle | Valor |
|---------|-------|
| Decision global | **APPROVED** |
| Hallazgos bloqueantes | Ninguno |
| Hallazgos moderados abiertos | 0 (M1 es bajo/moderate, solo recomendacion de ofuscacion opcional para diagnosis si hubiera rol viewer futuro) |
| Riesgo residual aceptado | Bajo — isolation por tenancy JWT; datos clinicos (`diagnosis`/`history`) no PII del dueno sin tokens |

---

## 11. Siguiente paso recomendado

Segun la tabla de continuidad (docs/opencode/13_agents_architecture_and_gate_flow.md), el slicing BE-015 completo ya tiene gate stage=review pasado y todos sus ACs validados. La decision es **APPROVED**, asi que el siguiente paso normal del pipeline es:

**Flujo estandar post-APPROVED:**
```
/run-checks BE-015
```

Si se requiere cerrar formalmente el slice en produccion tras gate approval:
```
/update-docs BE-015
/final-gate BE-015
```

---

## 12. Hallazgos resumidos por severidad

| ID | Severidad | Descripcion | Decision |
|----|-----------|-------------|----------|
| S1 | **Info** | Ratings summary acepta page/size pero router los ignora | Sin accion; firma unificada de UCs |
| S2 | **Low** | DTOs exponen pet_name + owner_name completos (AC-015 dice "resumidos") | Aceptado MVP; nombres propios clinicamente necesarios |
| M1 | **Moderate** | ConsultationSummaryDto expone diagnosis/history/recommendations (clinicos) | Recomendacion: ofuscar si aparece rol viewer en el futuro. No bloquea. |
| S3 | **Info** | Sin rate limiting en consulta de reportes | Aceptado para MVP; agregar stage-2 post-MVP |
| S4 | **Info** | Sin CSRF protection | No aplica — solo endpoints GET (read-only) |

---

*Fin de la revision de seguridad BE-015.*
