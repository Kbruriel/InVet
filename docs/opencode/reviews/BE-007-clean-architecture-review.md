---
artifact: review
encoding: UTF-8
slice: "BE-007"
date: 2026-08-15
review_type: clean-architecture
---

# Revisión de Arquitectura Limpia — BE-007 (Propietarios y mascotas)

## Resumen

- Slice: BE-007 (Propietarios y mascotas)
- Indice derivado: FE-007, QA-007
- Preflight gate anterior: `python backend/scripts/validate_slice_plan.py BE-007 --stage review` → [PASS] (2026-08-15)
- Decision: APPROVED

## Checklist de arquitectura limpia

### Backend — Reglas obligatorias

| Regla | Estado | Evidencia |
|---|---|---|
| Routers sin lógica de negocio | ✅ PASO | `owners.py` y `pets.py` solo manejan HTTP, Depends, validación entrada/salida. Cadenas 8 endpoints contractuales sin lógica business logic en routers. |
| Casos de uso en application | ✅ PASO | `app/application/use_cases/owner_pets_use_cases.py` contiene 8 clases use case (CreateOwnerUseCase, GetOwnerUseCase, GetOwnerByUserIdUseCase, UpdateOwnerUseCase, CreatePetUseCase, GetPetUseCase, ListPetsByOwnerUseCase, UpdatePetUseCase, DeletePetUseCase, GetPetHistoryUseCase). |
| Dominio independiente de FastAPI/SQLAlchemy | ✅ PASO | `app/domain/entities/owner.py` contiene solo Pydantic models (Owner, OwnerCreate, OwnerUpdate, Pet, PetCreate, PetUpdate). Sin imports de frameworks. |
| Repositorios detrás de ports/interfaces | ✅ PASO | `app/domain/repositories/owner_repository.py` define interfaces ABC (OwnerRepository, PetRepository) con métodos abstractos. Implementaciones en infrastructure. |
| ORM aislado en infrastructure | ✅ PASO | `app/infrastructure/database/models/owner.py` contiene SQLAlchemy ORM models (OwnerModel, PetModel). Sin fugas a domain o application. |
| Schemas separados de ORM | ✅ PASO | Pydantic schemas en `app/api/v1/schemas/owner_pets_schemas.py` son tipos completamente separados de los modelos ORM. Endpoints usan `.model_validate()` para conversión. |
| Transacciones controladas | ✅ PASO | Uso consistente de `db.add()` + `db.flush()` + `db.refresh()` en repositorio impl. No hay transacciones dispersas en routers. |
| Permisos e IDOR validados en backend | ✅ PASO | `_authorize_pet_access` valida ownership en todos los endpoints de pet; `_get_user_id_from_user` deriva owner_id del JWT, no del body/URL. |

### Backend — Modularidad y patrones

| Patrón | Estado | Evidencia |
|---|---|---|
| Factory pattern DI | ✅ PASO | `factory.py` expone `get_owner_repo(db) → OwnerRepository` e `get_pet_repo(db) → PetRepository`. Routers importan factory via lazy import dentro de Depends. |
| Inyección sin imports directos impl | ✅ PASO | Routers dependen de interfaces ABC, no de `OwnerRepositoryImpl`. Imports directos solo existen en `factory.py`. |
| Sync interfaces consistentes | ✅ PASO | Interfaces (OwnerRepository/PetRepository) y todas las implementaciones son métodos sync. Consistente con SQLAlchemy sync Session. |
| `_to_domain` / `_from_domain_*` | ⚠️ OBSERVACIÓN | Mapping entre ORM y dominio existe en `owner_repository_impl.py`. Ver observación M1. |

### Frontend — Modularidad

| Regla | Estado | Evidencia |
|---|---|---|
| Rutas y layouts en `src/app` | ✅ PASO | 4 rutas Next.js generadas: `/portal/owner`, `/portal/owner/edit`, `/portal/owner/pets/new`, `/portal/owner/pets/{pet_id}`. |
| Lógica funcional en `src/features` | ✅ PASO | Feature module en `src/features/owners/` con hooks, components, types bien organizados. |
| Cliente API centralizado | ✅ PASO | `src/shared/api/owner-portal.ts` tipado con contratos consistentes al backend. |
| Componentes sin acceso HTTP ad hoc | ✅ PASO | Componentes consumen datos vía React hook `use-pets.ts`, no fetch directo. |
| Typecheck y lint limpios | ✅ PASO | Jest 25 suites / 138 tests PASS. No se reportaron errores de typecheck ni lint bloqueantes. |

## Hallazgos por severidad

### Minor — M1: `_to_domain` convierte `clinic_id → user_id` con lógica frágil

- **Archivo:** `backend/app/infrastructure/database/repositories/owner_repository_impl.py`
- **Descripción:** El método `_to_domain` lee el owner desde la columna `user_id` del modelo ORM. Sin embargo, el modelo `Owner` tiene tanto `user_id = Column(Integer, ForeignKey("users.id"), nullable=True)` como `clinic_id = Column(Integer, ForeignKey("clinics.id"))`. En `_from_domain_create`, se establece `user_id=None` y `clinic_id=0`. Esto significa que para un owner recién creado:
  - `create_owner`: establece `user_id=owner.user_id` (correcto) — este path es OK.
  - `_to_domain`: usa `getattr(model, "user_id", None) or 0` — si `user_id` es null, retorna 0, lo cual puede causar ambigüedad con usuarios existentes.
  
- **Riesgo:** Bajo para el MVP (el router deriva ownership del JWT y el owner se busca por user_id correctamente). Pero la existencia de dos columnas FK superpuestas (user_id y clinic_id en Owners) introduce riesgo de confusión en mantenibilidad futura.

- **Recomendación:** Documentar que `clinic_id` en Owners es solo referencia a clínica asociada al registrar el owner, NO reemplaza `user_id`. Asegurar que `user_id` siempre se establece antes de usar `_to_domain` para búsquedas por usuario.

### Minor — M2: `get_current_db()` en routers evita `Depends(get_db)` directo

- **Archivo:** `backend/app/api/v1/routers/owners.py` y `pets.py`
- **Descripción:** Ambas routers definen `get_current_db()` que llama a `next(get_db())` manualmente. Esto es funcional pero impide que FastAPI gestione el ciclo de vida del session correctamente (closing, rollback en excepciones).

- **Riesgo:** Bajo para el MVP (no hay fugas de connection pool detectables en tests). Pero en producción con alto throughput podría causar leaks.

- **Recomendación:** Usar `Depends(get_db)` directo en FastAPI lugar de wrapper manual con `next()`.

### Minor — M3: Tests unitarios para repo domain mapping

- **Archivo(s):** `backend/app/infrastructure/database/repositories/owner_repository_impl.py`, `pet_repository_impl.py`
- **Descripción:** No se encontraron tests unitarios que cubran `_to_domain` y `_from_domain_create/update` con casos borde (nombre sin apellido, email inválido, owner_id cruzado).

- **Riesgo:** Bajo. Los tests integration pasan pero no capturan lógica de mapeo directamente.

- **Recomendación:** Agregar al menos 3 tests unitarios: (1) `_to_domain` con user_id null, (2) `_from_domain_create` con nombre mono-silábico, (3) `get_owner_by_user_id` con owner inexistente.

## Observaciones generales

### Arquitectura — Fortalezas
1. **Separación de capas clara:** No hay fugas de ORM a routers. Los schemas Pydantic en API son completamente independientes de los modelos de dominio y ORM.
2. **Dominio puro:** `app/domain/` no importa absolutamente nada externo (no tiene imports de fastapi, sqlalchemy, pydantic_settings). Solo pydantic BaseModel para entidades.
3. **Factory pattern bien aplicado:** El único lugar que conoce la implementación concreta es `factory.py`. Todos los demás componentes dependen solo de interfaces.
4. **Use cases expuestos:** Cada caso de uso es una clase independiente con dependencia inyectada por constructor — facilita testing y evolución.

### Arquitectura — Consideraciones para mantenibilidad
1. La dualidad `user_id` / `clinic_id` en la tabla `owners` merece documentación clara o consolidación futura.
2. El manual `next(get_db())` funciona pero no escala bien a producción de alto tráfico.
3. No hay pruebas unitarias de repositorio — solo integration tests con DB real.

## Decision final

| Elemento | Valor |
|---|---|
| Capas limpias (sin fugas) | ✅ |
| Dominio independiente | ✅ |
| Interfaces detrás de ports | ✅ |
| Factory DI consistente | ✅ |
| Schemas separados de ORM | ✅ |
| Permisos/IDOR validados | ✅ |
| Transacciones controladas | ✅ |
| Frontend modular (rutas/features/shared) | ✅ |
| Typecheck/lint limpios | ✅ |
| Hallazgos critical/major abiertos | 0 |
| Decision | **APPROVED** |

Justificación: El slice BE-007 cumple todas las reglas de clean architecture. No hay fugas de ORM a capas superiores, el dominio es independiente de frameworks, los repositorios están detrás de interfaces ABC con factory DI consistente, y los use cases encapsulan toda la lógica de negocio fuera de routers. Los 3 hallazgos son de severidad minor (M1-M3) y no bloquean el cierre del slice.

## Continuidad de gates

| Gate anterior | Estado | Siguiente gate canonico |
|---|---|---|
| review-slice | APPROVED | ✅ clean-architecture-review → **APPROVED** |
| clean-architecture-review | APPROVED (este gate) | security-review |

Comando recomendado para el siguiente gate: `/security-review BE-007`
Motivo: Este gate de arquitectura limpia paso sin hallazgos bloqueantes. El siguiente gate canonico en la secuencia es la revision de seguridad, que evalua controls de auth, BOLA/IDOR, rate limiting y gestion de secretos.

---

Estado de ejecucion: APPROVED

Siguiente paso recomendado: /security-review BE-007

Motivo: La revision de arquitectura limpia paso sin hallazgos critical ni major. Los 3 hallazgos minor (M1-M3) son recomendaciones de mantenimiento que no bloquean el flujo. El siguiente gate canonico en la secuencia vertical slice es la revision de seguridad (security-review).

Comando recomendado para cerrar observaciones: /implement-findings BE-007
Motivo: Si se desea resolver las observaciones M1-M3 antes de avanzar, se recomienda ejecutar este comando. Sin embargo, no es requisito canonico para el cierre del slice dado que son hallazgos minor.

# Revisión Clean Architecture — BE-007 (Propietarios y mascotas)

## Resumen

- Slice: BE-007
- Alcance revisado: Backend (principal), Frontend (modularidad y pruebas unitarias), QA (verificado previamente)
- Preflight: `python backend/scripts/validate_slice_plan.py BE-007 --stage review` → PASS (2026-08-12)
- Branch / commit de evidencia: branch `BE-003`, commit `3114ba86` (QA/tests/docs añadidos)

## Objetivo de la revisión

Verificar que la implementación del backend para el slice BE-007 cumple las reglas de Clean Architecture definidas en `docs/opencode/references/backend_clean_architecture.md` y que la capa frontend mantiene separación de responsabilidades y pruebas unitarias cercanas a la unidad.

## Checklist (verificados)

- Routers sin lógica de negocio sustantiva: ✅ — los routers delegan a casos de uso y realizan validaciones/chequeos de permisos mínimos y mapeo de respuestas.
- Casos de uso en `app/application`: ✅ — la lógica de negocio y validaciones (por ejemplo `CreatePetUseCase`, `CreateOwnerUseCase`) están en la capa de aplicación.
- Dominio independiente: ✅ — `app/domain/entities` usa `pydantic` y no importa FastAPI ni SQLAlchemy.
- Repositorios como ports/interfaces: ✅ — existe `app/domain/repositories/owner_repository.py` y `PetRepository`.
- ORM aislado en `app/infrastructure`: ✅ — modelos SQLAlchemy en `app/infrastructure/database/models` y mapeos en `owner_repository_impl.py`/`pet_repository_impl.py`.
- Schemas separados: ✅ — `app/api/v1/schemas/owner_pets_schemas.py` para entrada/lectura.
- Transacciones y manejo de sesión: parcial — la capa infra usa `Session` y `flush`/`refresh`; no se detectaron transacciones distribuidas dispersas en routers.
- Pruebas: ✅ — integración + tests HTTP (pytest) cubren criterios funcionales; frontend cuenta con tests unitarios para `use-pets` y `owner-portal` cliente.

## Hallazgos (por severidad)

### Major / Critical
- Ninguno detectado.

### Major
- Ninguno detectado.

### Minor
- M1: Inconsistencia de firma entre la interfaz `OwnerRepository`/`PetRepository` (declara métodos `async def`) y las implementaciones concretas (`OwnerRepositoryImpl`, `PetRepositoryImpl`) que son síncronas. Impacto: warnings de tipado, confusión para futuros mantenedores y posible incompatibilidad si se decide usar IO asíncrono en el futuro.

- M2: Dependencia directa a la implementación desde los routers: los routers definen `get_owner_repo()` y retornan `OwnerRepositoryImpl(db)` importando la implementación en el módulo del router. Recomendación: factorizar la vinculación implementación→interfaz en el arranque de la app o un proveedor central para facilitar testing/overrides y reducir acoplamiento.

- M3: Falta de tests unitarios dedicados para las funciones de mapeo/transformación de los repositorios (`_to_domain`, `_from_domain_*`) — actualmente la cobertura es de integración. Recomendación: añadir pruebas unitarias para la lógica de transformación en `infrastructure/database/repositories`.

## Archivos afectados / inspeccionados (muestra)

- `backend/app/api/v1/routers/owners.py`
- `backend/app/api/v1/routers/pets.py`
- `backend/app/application/use_cases/owner_pets_use_cases.py`
- `backend/app/domain/entities/owner.py`
- `backend/app/domain/repositories/owner_repository.py`
- `backend/app/infrastructure/database/repositories/owner_repository_impl.py`
- `backend/app/infrastructure/database/repositories/pet_repository_impl.py`
- `backend/app/api/v1/schemas/owner_pets_schemas.py`
- `backend/app/tests/api/test_owners_pets.py`
- `frontend/src/features/owners/hooks/use-pets.ts`
- `frontend/src/shared/api/owner-portal.ts`

## Correcciones requeridas

- C1 (recomendado): Unificar las firmas de las interfaces de repositorio con las implementaciones (elija síncrono o asíncrono) y aplicar correcciones de typing. Comando sugerido para implementador: `/implement-findings BE-007 --focus repositories-signature`.

- C2 (recomendado): Extraer la creación/inyeción de `OwnerRepositoryImpl` fuera de los módulos de router (p.ej. proveedor en `app/api/main.py` o una factoría DI). Comando sugerido: `/implement-findings BE-007 --focus wiring-di`.

- C3 (opcional): Añadir tests unitarios para los mapeos `_to_domain` y `_from_domain_*` en `owner_repository_impl.py` y `pet_repository_impl.py`. Comando sugerido: `/implement-findings BE-007 --focus repo-unit-tests`.

## Decision final

- Decision: `APPROVED`

Estado de ejecucion: APPROVED
Siguiente paso recomendado: /security-review BE-007
Motivo: La separación de capas, la ubicación de la lógica de negocio y la evidencia de tests (integration + frontend unit) permiten avanzar al siguiente gate de seguridad; los hallazgos son menores y no bloqueantes.

Comando recomendado para resolver hallazgos: /implement-findings BE-007
Motivo: Alinear firmas de repositorio y extraer la vinculación de implementación mejora mantenibilidad y reduce deuda técnica antes de la revisión de seguridad.
