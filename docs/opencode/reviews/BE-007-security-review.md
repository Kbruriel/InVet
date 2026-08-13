---
artifact: review
encoding: UTF-8
---

# Revisión de seguridad — BE-007 (Propietarios y mascotas)

## Resumen

- Slice: BE-007
- Alcance revisado: Backend (primario), Frontend (clientes API y hooks revisados), QA (evidencia previa revisada)
- Preflight: `python backend/scripts/validate_slice_plan.py BE-007 --stage review` → PASS (2026-08-12)
- Branch / commit de evidencia: branch `BE-003`, commit `3114ba86` (tests y QA artifacts añadidos)

## Objetivo

Evaluar controles de autenticación, autorización, IDOR/BOLA, manejo de secretos, validación de entrada y exposición de datos para el slice BE-007.

## Checklist (resumen)

- Autenticación en endpoints privados: ✅ (token JWT vía `get_current_access_user`)
- Autorización por rol/contexto: ✅ (validaciones en routers y `_validate_pet_ownership`)
- Prevención IDOR/BOLA: ✅ (tests de IDOR existen y pasan), pero mirar mapping de Owner→user_id (ver hallazgo mayor)
- Validación de input: ✅ (Pydantic schemas en `owner_pets_schemas.py`)
- Rate limiting: ❌ (No implementado en este slice)
- Manejo de secretos: ❌ (default `SECRET_KEY` en código fuente)
- Logs sin datos sensibles: ✅ (no logging de tokens/PII detectado en artefactos inspeccionados)

## Hallazgos por severidad

### Major

- S1 — Default `SECRET_KEY` en configuración de aplicación
  - Archivo: `backend/app/core/config/settings.py`
  - Descripción: El valor `SECRET_KEY` tiene un valor por defecto (`"secret-key-for-dev"`) embebido en el código. Esto permite que entornos sin configuración de variables de entorno usen una llave conocida, lo que facilita la falsificación o reusado de tokens JWT en entornos expuestos.
  - Riesgo: Alta — permite forjar o reutilizar tokens si no se sobrescribe en entornos de despliegue; rotación y gestión de claves no estan garantizadas.
  - Corrección requerida: Eliminar valores secretos por defecto en el repo; exigir la presencia de `SECRET_KEY` en tiempo de arranque o fallar con mensaje claro; documentar uso de secret manager y CI para inyectar secretos.

- S2 — Mapeo inconsistente de Owner ↔ user_id (uso de `clinic_id`)
  - Archivo: `backend/app/infrastructure/database/repositories/owner_repository_impl.py` (métodos `_to_domain`, `_from_domain_create`, `create_owner`, `get_owner_by_user_id`)
  - Descripción: El repositorio persiste/lee la relación usuario→propietario usando la columna `clinic_id` del modelo `Owner` (que a su vez es FK a `clinics.id`). La implementacion asigna `clinic_id=owner.user_id` y consulta por `clinic_id == user_id`. Esto es semánticamente confuso y puede causar corrupción de relaciones, filtrado inadecuado y errores de ownership/IDOR si la tabla `clinics` existe y usa los mismos ids.
  - Riesgo: Alta — mapeo incorrecto puede llevar a permisos mal aplicados y exposición involuntaria de datos entre dominios (propietarios, clinicas, usuarios). Aunque las pruebas actuales pasan (posiblemente por fixtures que soportan este mapeo), la inconsistencia es una vulnerabilidad lógica que debe corregirse.
  - Corrección requerida: Definir un campo claro `user_id` en la tabla `owners` (o documentar explícitamente por qué `clinic_id` se reutiliza) y migrar datos; actualizar repositorio para usar `user_id`; revisar y actualizar tests y fixtures. Evitar reutilizar campos con meaning distinto.

### Minor

- S3 — Falta de rate limiting en endpoints sensibles
  - Archivo(s): (no hay implementación de rate limiting encontrada)
  - Descripción: No hay controles de rate limit para endpoints de auth, creación de recursos o búsqueda pública.
  - Recomendación: Añadir rate limiting a endpoints de login y operaciones sensibles (p. ej. via una capa de middleware o API gateway). No bloqueante para cierre del slice, pero recomendable.

- S4 — Interfaces de repositorio declaradas `async` vs implementaciones síncronas
  - Archivo(s): `backend/app/domain/repositories/owner_repository.py` vs `.../owner_repository_impl.py`
  - Descripción: Desacople de firmar métodos como asíncronos en la interfaz y síncronos en la implementación; no es directamente explotable pero complica migraciones a IO asíncrono y puede inducir errores por confusión.

- S5 — Tokens refresh rotativos no verificados
  - Archivo(s): `backend/app/core/security.py` contiene creación de `create_refresh_token` pero no mecanismo de rotación observable en este slice. Recomendación: revisar estrategia de refresh tokens y rotación/blacklisting en la capa auth central.

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

- A1 (critica): Eliminar `SECRET_KEY` por defecto y asegurar que la aplicación falla en arranque si no existe una variable de entorno `SECRET_KEY`.
  - Comando recomendado: `/implement-findings BE-007 --focus secret-key`
  - Justificación: Evitar que entornos sin configuración utilicen una clave conocida en el repo.

- A2 (critica): Corregir el mapeo Owner↔user_id y migrar esquema si corresponde.
  - Comando recomendado: `/implement-findings BE-007 --focus owner-repo-mapping`
  - Justificación: Evitar exposicion involuntaria o confusión de ownership que puede producir IDOR/BOLA lógicos.

- A3 (recomendado): Añadir tests unitarios que cubran los mapeos `_to_domain` y `_from_domain_*` en `owner_repository_impl.py` y `pet_repository_impl.py`.
  - Comando recomendado: `/implement-findings BE-007 --focus repo-unit-tests`

- A4 (recomendado): Documentar y/o implementar rate limiting para endpoints de `auth` y operaciones sensibles.
  - Comando recomendado: `/implement-findings BE-007 --focus rate-limiting`

## Decision final

- Decision: `REJECTED`

Estado de ejecucion: REJECTED
Siguiente paso recomendado: /implement-findings BE-007
Motivo: Se detectaron hallazgos de seguridad de severidad alta (clave secreta por defecto en el repo y mapeo inconsistente `clinic_id`→`user_id`) que requieren corrección antes de avanzar a gates posteriores.

Comando recomendado para resolver hallazgos: /implement-findings BE-007
Motivo: Corregir la gestión de secretos en configuración y alinear el modelo de persistencia para evitar riesgos de ownership/IDOR.
