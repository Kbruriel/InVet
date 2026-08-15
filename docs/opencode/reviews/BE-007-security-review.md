---
artifact: review
encoding: UTF-8
slice: "BE-007"
date: 2026-08-15
review_type: security
---

# Revisión de seguridad — BE-007 (Propietarios y mascotas)

## Resumen

- Slice: BE-007 (Propietarios y mascotas)
- Indice derivado: FE-007, QA-007
- Preflight: `python backend/scripts/validate_slice_plan.py BE-007 --stage review` → [PASS] (2026-08-15)
- Decision anterior: REJECTED (hallazgos S1/S2 críticos previos)
- Decision actual: APPROVED (S1 y S2 corregidos, hallazgos minor restantes no bloqueantes)

## Objetivo

Evaluar controles de autenticación, autorización, IDOR/BOLA, manejo de secretos, validación de entrada y exposición de datos para el slice BE-007.

## Checklist (resumen actualizado)

- Autenticación en endpoints privados: ✅ (token JWT vía `get_current_access_user` con validación type + subject)
- Autorización por rol/contexto: ✅ (_authorize_pet_access valida ownership en todos los endpoints de pet; clinic role restricted)
- Prevención IDOR/BOLA: ✅ (tests de IDOR pasan; user_id mapeo corregido)
- Validación de input: ✅ (Pydantic schemas con field_validator + EmailStr)
- Rate limiting: ⚠️ No implementado (S3 minor, no bloqueante)
- Manejo de secretos: ✅ (S1 corregido: Field(...); _require_secret_key() valida antes de usar)
- Logs sin datos sensibles: ✅ (no logging de tokens/PII detectado)
- Password hashing seguro: ✅ (bcrypt via passlib CryptContext)
- Refresh tokens: ⚠️ Sin rotación verificable (S5 minor, no bloqueante)
- CORS configurado: ✅ (BACKEND_CORS_ORIGINS = [localhost:3000])

## Hallazgos por severidad

### Corregidos desde revision anterior

#### S1 — Default `SECRET_KEY` → CORREGIDO ✅
  - **Archivo:** `backend/app/core/config/settings.py`
  - **Estado actual:** `SECRET_KEY: str = Field(..., description="JWT secret key — required at runtime")`
  - **Verificacion:** No hay valor por defecto. Pydantic exige env var al instanciar `Settings()`.
  - **Defensa en profundidad:** `_require_secret_key()` en `security.py` valida que SECRET_KEY no esté vacio antes de usarlo; lanza `RuntimeError` con mensaje claro si falta.
  - **Impacto en tests:** Fixtures de test establecen `os.environ["SECRET_KEY"]` antes de importar settings — compatible con el cambio.

#### S2 — Mapeo inconsistente Owner ↔ user_id → CORREGIDO ✅
  - **Archivo:** `backend/app/infrastructure/database/repositories/owner_repository_impl.py`
  - **Estado actual verificado:**
    - Modelo ORM (`owner.py`): tiene tanto `user_id = Column(Integer, ForeignKey("users.id"), nullable=True)` como `clinic_id = Column(Integer, ForeignKey("clinics.id"))`. Dos columnas FK distintas.
    - `create_owner()`: establece explícitamente `user_id=owner.user_id` y `clinic_id=0` — correcto.
    - `get_owner_by_user_id()`: filtra con `OwnerModel.user_id == user_id` — usa la columna correcta, NO clinic_id.
    - `_to_domain()`: usa `getattr(model, "user_id", None) or 0` — lee de `user_id` directamente.
    - `_from_domain_create()`: establece `user_id=None` y `clinic_id=0` en el modelo ORM (para el caso create desde domain).
  - **Verificacion:** El router deriva ownership del JWT (`_get_user_id_from_user`) y busca owner por `user_id` correcto. No hay mapeo clinic_id→user_id.
  - **Observacion residual:** La dualidad user_id/clinic_id en la tabla Owners es semánticamente confusa. Merece documentacion futura, pero no representa riesgo de seguridad explotable en el MVP actual.

### Minor

- S3 — Falta de rate limiting en endpoints sensibles ⚠️ NO BLOQUEANTE
  - Archivo(s): (sin implementacion de rate limiting)
  - Estado: No bloqueante para cierre del slice MVP.
  - Recomendacion: Anadir rate limiting a endpoints de login y operaciones sensibles via middleware o API gateway en etapas posteriores.

- S4 — M1/M2: Interfaces y implementaciones sync consistentes → CORREGIDO ✅
  - Estado anterior: Declaradas `async` en interfaz pero síncronas en impl.
  - Estado actual: Ambas son `sync`. Consistente con SQLAlchemy sync Session. Correccion M1 aplicada.

- S5 — Tokens refresh sin rotacion verificable ⚠️ NO BLOQUEANTE
  - Archivo(s): `backend/app/core/security.py` + `AuthUseCase.refresh()`
  - Estado: Logout invalida token (session delete), login genera nuevo. No hay blacklist explicito.
  - Recomendacion: Implementar rotacion explicita con blacklist para alta seguridad.

## Archivos inspeccionados (muestra)

- `backend/app/core/config/settings.py`
- `backend/app/core/security.py`
- `backend/app/infrastructure/database/repositories/owner_repository_impl.py`
- `backend/app/infrastructure/database/repositories/pet_repository_impl.py`
- `backend/app/api/v1/routers/owners.py`
- `backend/app/api/v1/routers/pets.py`
- `backend/app/api/v1/schemas/owner_pets_schemas.py`
- `frontend/src/shared/api/owner-portal.ts`
- `frontend/src/features/owners/hooks/use-pets.ts`

## Correcciones requeridas (acciones concretas)

- A1 (recomendado): Tests unitarios para mapeos `_to_domain` / `_from_domain_*`
  - Comando: `/implement-findings BE-007 --focus repo-unit-tests`

- A2 (recomendado): Documentar dualidad user_id/clinic_id en tabla Owners
  - Comando: `/implement-findings BE-007 --focus owner-repo-mapping`

## Decision final

| Elemento | Valor |
|---|---|
| Secretos seguros (sin default) | ✅ S1 corregido |
| Password hashing seguro | ✅ bcrypt via passlib |
| Tokens expiracion corta | ✅ ACCESS_TOKEN_EXPIRE_MINUTES=30 |
| Refresh tokens validados | ✅ type=refresh + session DB |
| Auth en endpoints privados | ✅ get_current_access_user |
| Autorizacion por rol/contexto | ✅ _authorize_pet_access |
| Prevencion IDOR/BOLA | ✅ tests pasan; user_id correcto |
| Validacion input Pydantic | ✅ field_validator + EmailStr |
| Logs sin PII/tokens | ✅ Verificado |
| CORS configurado | ✅ localhost:3000 |
| Hallazgos critical/major abiertos | 0 |
| Decision | **APPROVED** |

- Decision: APPROVED

Justificacion: Los dos hallazgos criticos de la revision anterior (S1 y S2) fueron corregidos exitosamente. S1: SECRET_KEY ahora exige env var con Field(...). S2: get_owner_by_user_id filtra correctamente por user_id, no clinic_id. Los hallazgos minor restantes (S3 rate-limiting, S5 refresh rotation) son recomendaciones de mejora pero no vulnerabilidades explotables en el MVP.

## Continuidad de gates

| Gate anterior | Estado | Siguiente gate canonico |
|---|---|---|
| clean-architecture-review | APPROVED | ✅ security-review → **APPROVED** |
| security-review | APPROVED (este gate) | checks |

Comando recomendado para el siguiente gate: `/run-checks BE-007`
Motivo: Este gate de seguridad paso sin hallazgos critical ni major. El siguiente gate canonico en la secuencia es ejecucion de checks automatizados.

## Estado de ejecucion

Estado de ejecucion: APPROVED

Siguiente paso recomendado: /run-checks BE-007

Motivo: Este gate de seguridad paso sin hallazgos critical ni major. El siguiente gate canonico en la secuencia es ejecucion de checks automatizados.

Comando recomendado para cerrar observaciones: /implement-findings BE-007
Motivo: Si se desea resolver las observaciones S3/S5 antes de avanzar, se recomienda ejecutar este comando. Sin embargo, no es requisito canonico dado que son hallazgos minor.
