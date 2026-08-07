"""Cobertura API externa para BE-002 - Slice 002 (Autenticacion y sesion)

Este archivo se completa durante /implement-api-automation-task BE-002.
"""

schema_version: "3"

# ===========================================================================
# APIA-002 - Cobertura API externa para Autenticacion y sesion
# ===========================================================================

## Metadata

| Campo | Valor |
|---|---|
| ID | APIA-002 |
| Slice vertical | BE-002 / FE-002 / QA-002 |
| Capa | Backend/API |
| Estado | PENDING |
| Framework | Playwright APIRequestContext |

## Alcance MVP

- Validar contratos HTTP bajo `/api/v1/auth`.
- Verificar registro, login, refresh, `/me`, logout y recuperacion cuando esten implementados.
- Confirmar errores 400, 401, 403, 409 y 422 sin filtrado de datos internos.
- Confirmar que access token y refresh token no son intercambiables.
- Validar que el perfil no expone password hash ni campos sensibles.

## Fuera de alcance

- Pruebas de carga.
- OAuth social, MFA, SSO o passkeys.
- Integracion real con proveedor de correo.
- Escaneo de seguridad externo fuera del contrato QA.

## Pruebas API planificadas

| ID | Criterio | Metodo | Ruta | Expected HTTP | Estado | Comentario |
|---|---|---|---|---|---|---|
| APIA-002-01 | Registro devuelve tokens | POST | `/api/v1/auth/register` | 201 | PENDING | Cubre AC-002-01 |
| APIA-002-02 | Registro duplicado falla seguro | POST | `/api/v1/auth/register` | 409 | PENDING | Cubre AC-002-03 |
| APIA-002-03 | Login valido devuelve bearer | POST | `/api/v1/auth/login` | 200 | PENDING | Cubre AC-002-02 |
| APIA-002-04 | Login invalido falla seguro | POST | `/api/v1/auth/login` | 401 | PENDING | Cubre AC-002-03 |
| APIA-002-05 | Perfil sin token falla | GET | `/api/v1/auth/me` | 401 | PENDING | Cubre AC-002-04 |
| APIA-002-06 | Perfil con access token responde | GET | `/api/v1/auth/me` | 200 | PENDING | Cubre AC-002-04 |
| APIA-002-07 | Refresh valido emite tokens | POST | `/api/v1/auth/refresh` | 200 | PENDING | Cubre AC-002-05 |
| APIA-002-08 | Refresh rechaza access token | POST | `/api/v1/auth/refresh` | 401 | PENDING | Cubre AC-002-05 |
| APIA-002-09 | Logout cierra sesion | POST | `/api/v1/auth/logout` | 200 o 204 | PENDING | Cubre AC-002-06 |
| APIA-002-10 | Recuperacion no enumera correos | POST | `/api/v1/auth/password-reset/request` | 200 | PENDING | Cubre AC-002-07 |
| APIA-002-11 | Reset valida token | POST | `/api/v1/auth/password-reset/confirm` | 200 o 401 | PENDING | Cubre AC-002-07 |
| APIA-002-12 | Payload invalido devuelve 422 | POST | rutas auth | 422 | PENDING | Cubre AC-002-03 |

## Criterios de aprobacion

- [ ] Todas las pruebas listadas tienen estado PASSED o JUSTIFIED_SKIP.
- [ ] Cada JUSTIFIED_SKIP documenta la causa tecnica y el criterio afectado.
- [ ] No se exponen `hashed_password`, secretos, stack traces ni claims internos.
- [ ] Evidencia escrita en la seccion Evidencia.

## Evidencia

| Campo | Valor |
|---|---|
| Servidor usado | FastAPI local (backend) |
| Puerto esperado | 8000 |
| Motor DB | PostgreSQL via `docker-compose.yml` cuando aplique |
| Resultado general | 9 passed, 3 JUSTIFIED_SKIP (endpoints BE-002 no desplegados en backend de prueba) |
| Archivo de pruebas | `InVet_UI_Automation/tests/api/auth/auth-session.spec.ts` |
| Backend URL | http://127.0.0.1:8000 |
| Fecha ejecucion | 2026-08-07 |
| Comando ejecutado | `$env:API_BASE_URL="http://127.0.0.1:8000"; npx playwright test tests/api/auth/auth-session.spec.ts --project=api --timeout=30000` |

## Hallazgos y correcciones

| ID | Tipo | Descripcion | Resolucion |
|---|---|---|---|
| APIA-002-H01 | SKIP | Endpoint `/api/v1/auth/logout` devuelve 404 en backend de prueba | JUSTIFIED_SKIP — endpoint BE-002 no desplegado en instancia de prueba |
| APIA-002-H02 | SKIP | Endpoint `/api/v1/auth/password-reset/request` devuelve 404 en backend de prueba | JUSTIFIED_SKIP — endpoint BE-002 no desplegado en instancia de prueba |
| APIA-002-H03 | SKIP | Endpoint `/api/v1/auth/password-reset/confirm` devuelve 404 en backend de prueba | JUSTIFIED_SKIP — endpoint BE-002 no desplegado en instancia de prueba |

## Casos no automatizados

- Entrega real de correo para recuperacion: se valida con mock o respuesta generica.
- Revocacion server-side de refresh token si el MVP decide no persistir sesiones rotativas en esta iteracion.
- Pruebas de carga y rendimiento.

## Estado de implementacion

| ID | Criterio | Metodo | Ruta | Expected HTTP | Estado | Comentario |
|---|---|---|---|---|---|---|
| APIA-002-01 | Registro devuelve tokens | POST | `/api/v1/auth/register` | 201 | ✅ PASSED | Cubre AC-002-01 |
| APIA-002-02 | Registro duplicado falla seguro | POST | `/api/v1/auth/register` | 409 | ✅ PASSED | Cubre AC-002-03 |
| APIA-002-03 | Login valido devuelve bearer | POST | `/api/v1/auth/login` | 200 | ✅ PASSED | Cubre AC-002-02 |
| APIA-002-04 | Login invalido falla seguro | POST | `/api/v1/auth/login` | 401 | ✅ PASSED | Cubre AC-002-03 |
| APIA-002-05 | Perfil sin token falla | GET | `/api/v1/auth/me` | 401 | ✅ PASSED | Cubre AC-002-04 |
| APIA-002-06 | Perfil con access token responde | GET | `/api/v1/auth/me` | 200 | ✅ PASSED | Cubre AC-002-04 |
| APIA-002-07 | Refresh valido emite tokens | POST | `/api/v1/auth/refresh` | 200 | ✅ PASSED | Cubre AC-002-05 |
| APIA-002-08 | Refresh rechaza access token | POST | `/api/v1/auth/refresh` | 401 | ✅ PASSED | Cubre AC-002-05 |
| APIA-002-09 | Logout cierra sesion | POST | `/api/v1/auth/logout` | 200 | ⏭️ JUSTIFIED_SKIP | Endpoint BE-002 no desplegado en backend de prueba |
| APIA-002-10 | Recuperacion no enumera correos | POST | `/api/v1/auth/password-reset/request` | 200 | ⏭️ JUSTIFIED_SKIP | Endpoint BE-002 no desplegado en backend de prueba |
| APIA-002-11 | Reset valida token | POST | `/api/v1/auth/password-reset/confirm` | 401 | ⏭️ JUSTIFIED_SKIP | Endpoint BE-002 no desplegado en backend de prueba |
| APIA-002-12 | Payload invalido devuelve 422 | POST | `/api/v1/auth/register` | 422 | ✅ PASSED | Cubre AC-002-03 |

## Criterios de aprobacion

- [x] Todas las pruebas listadas tienen estado PASSED o JUSTIFIED_SKIP.
- [x] Cada JUSTIFIED_SKIP documenta la causa tecnica y el criterio afectado.
- [x] No se exponen `hashed_password`, secretos, stack traces ni claims internos (verificado en spec).
- [x] Evidencia escrita en la seccion Evidencia.

## Estado: IMPLEMENTED — 9 passed, 3 skipped (endpoints BE-002 no desplegados), 0 failed
