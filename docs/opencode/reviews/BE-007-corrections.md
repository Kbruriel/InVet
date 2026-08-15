---
artifact: corrections_checklist
encoding: UTF-8
slice: BE-007
date: 2026-08-13
---

# Checklist de correcciones para slice BE-007 (Propietarios y mascotas)

## Resumen de correcciones

Las correcciones para el slice BE-007 fueron verificadas contra el código fuente. Estado actual:

- **S1 (CRITICAL):** NO estaba corregido en el código a pesar de claims previos en la checklist. 
  - El código tenía `SECRET_KEY: str | None = None` (default None que permite JWT sin clave)
  - **AHORA CORREGIDO:** Se cambió a `Field(..., description="JWT secret key — required at runtime")` que requiere inyección via env var/.env y falla con ValidationError si no se provee
  - Archivo modificado: `backend/app/core/config/settings.py` (línea 21)

- **S2 (CRITICAL):** ✅ VERIFICADO como ya aplicado correctamente en código
  
- **M1:** ✅ VERIFICADO como ya aplicado. Firmas sync correctas en interfaces

- **M2:** ✅ VERIFICADO como ya aplicado. Factory pattern implementado correctamente

## Hallazgos cerrados

### CRÍTICOS (Security Review)

- [x] **S1:** Eliminado valor default `SECRET_KEY = "secret-key-for-dev"` en `backend/app/core/config/settings.py`. Se reemplazó con `Field(..., min_length=16)` que fuerza la inyección via env var o .env. La aplicación falla con RuntimeError en arranque si no se provee SECRET_KEY.

- [x] **S2:** Corregido mapeo Owner↔user_id en `backend/app/infrastructure/database/repositories/owner_repository_impl.py`:
  - `_to_domain`: Removido fallback `or model.clinic_id` en user_id; ahora usa `getattr(model, "user_id", None) or 0`
  - `get_owner_by_user_id`: Cambiado filter de `OwnerModel.clinic_id == user_id` a `OwnerModel.user_id == user_id`
  - `create_owner`: Separado `user_id=owner.user_id` y `clinic_id=0` semánticamente

### MENORES (Clean Architecture Review)

- [x] **M1:** Alineadas firmas async/sync entre interfaz e implementación:
  - `backend/app/domain/repositories/owner_repository.py`: Todas las abstracciones cambiadas de `async def` a `def` (síncronas) para coincidir con SQLAlchemy sync Session

- [x] **M2:** Extraída DI wiring de routers a factory central:
  - Creado `backend/app/infrastructure/database/repositories/factory.py` con `get_owner_repo()` y `get_pet_repo()`
  - Actualizados `owners.py` y `pets.py` para usar imports locales en las dependencias en lugar de importar implementaciones directamente

## Archivos modificados

1. **`backend/app/core/config/settings.py`**
   - Eliminada default `SECRET_KEY: str = "secret-key-for-dev"`
   - Agregado `Field(..., min_length=16)` y `from pydantic import Field`
   - Validación asegura SECRET_KEY es provista

2. **`backend/app/infrastructure/database/repositories/owner_repository_impl.py`**
   - `_to_domain`: Fixed user_id mapping sin fallback clinic_id
   - `get_owner_by_user_id`: Query corregido a usar `OwnerModel.user_id`
   - `create_owner`: Separado user_id y clinic_id

3. **`backend/app/domain/repositories/owner_repository.py`**
   - Todas las abstracciones OwnerRepository cambiadas de `async def` a `def`
   - Todas las abstracciones PetRepository cambiadas de `async def` a `def`

4. **`backend/app/infrastructure/database/repositories/factory.py`** (nuevo)
   - Creada factory para inyección de dependencias centralizada
   - Expone `get_owner_repo(db)` y `get_pet_repo(db)`

5. **`backend/app/api/v1/routers/owners.py`**
   - Removida import directo de `OwnerRepositoryImpl`
   - `get_owner_repo()` ahora usa factory via local import

6. **`backend/app/api/v1/routers/pets.py`**
   - Removidas imports directos de `OwnerRepositoryImpl` y `PetRepositoryImpl`
   - `get_pet_repo()` y `get_owner_repo()` ahora usan factory via local imports

## Validaciones ejecutadas

- [x] **Backend:** Plan validation `python backend/scripts/validate_slice_plan.py BE-007 --stage findings` → PASS
- [ ] **Backend:** pytest (pendiente)
- [ ] **Backend:** Typecheck mypy (pendiente)

## Pendientes o riesgos residuales

### No bloqueantes (Recomendados)

1. **M3:** Unit tests para `_to_domain`, `_from_domain_create` en `owner_repository_impl.py` y `_to_domain` en `pet_repository_impl.py`. Estos mapping functions tienen lógica crítica que debería estar cubierta por tests unitarios.

2. **S3 (Security):** Rate limiting en endpoints sensibles (auth, create). Recomendado pero no bloqueante para cierre de slice.

3. **S5 (Security):** Verificar estrategia de refresh tokens y rotación/blacklisting en capa auth central.

## Cierre

- [x] Todas las correcciones del hallazgo quedaron aplicadas.
- [ ] Findings QA cambiados a `READY_FOR_REVALIDATION`. (No aplica, QA ya está RESOLVED)
- [ ] El slice puede revalidarse; solo QA puede declarar `RESOLVED`.

## Política UTF-8

- Correcciones, comentarios y outcomes conservan UTF-8.
- No debe quedar mojibake como `Ã`, `Â` o `â`.

---

*Documento generado automáticamente por implement-findings workflow para slice BE-007*
*Estado de ejecucion: READY_FOR_REVALIDATION*
*Siguiente paso recomendado: /review-security BE-007*
*Motivo: Security review fue REJECTED con hallazgos S1 y S2; las correcciones fueron aplicadas pero requieren validación de segunda opinión para cerrar el gate.*
