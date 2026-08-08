# Hallazgos de revisión Clean Architecture - BE-004

## Resumen

- Slice: BE-004 (Perfil público clínica/sucursal)
- Tipo de review: Clean Architecture
- Estado: `APPROVED`
- Decision: `APPROVED`

## Alcance revisado

- Backend:
  - Domain entities: `branch.py` (Branch, Service, BranchSchedule, RatingSummary, AvailabilitySummary)
  - Repository interfaces: `branch_repository.py` (5 abstract repos)
  - Use cases: `branch_profile.py`, `public_branches.py`, `public_services.py`
  - Application DTOs: `dtos/public_branch_dtos.py`, `dtos/public_service_dtos.py`
  - Infrastructure ORM models: `infrastructure/database/models/branch.py`, `service.py`, `branch_schedule.py`, `rating_summary.py`, `availability_summary.py`
  - Repository implementations: `infrastructure/database/repositories/branch_repository.py` (5 concrete impls)
  - API schemas: `branch_public.py`, `branch_protected.py`, `public_branch.py`, `public_service.py`
  - Routers: `branch_profile.py`, `public_branches.py`

- Frontend: No revisado en este gate (corresponde a functional review).
- QA: QA-004 reportado como APPROVED por el usuario.

## Hallazgos por severidad

### Blocker

Ninguno.

### Critical

Ninguno.

**C1 — Application layer importa schemas del API layer**: ~~RESUELTO~~ ✅
- Los DTOs fueron movidos a `app/application/dtos/` en una corrección previa.
- Ambos use cases (`public_branches.py`, `public_services.py`) importan desde `app.application.dtos`.
- No hay violaciones de dependencias Application → API en el código BE-004.

### Major

Ninguno.

**M1 — Router return type annotations**: ~~RESUELTO~~ ✅
- `get_branch_public_profile`: retorno `-> BranchPublicProfile` ✅
- `get_branch_protected_profile`: retorno `-> BranchProtectedProfile` ✅

**M2 — Routers importan implementaciones concretas**: ~~RESUELTO~~ ✅
- Dependency functions usan anotaciones de tipo ABC + import local dentro de la función.
- Router no conoce nombres concretos en nivel de módulo.

### Minor

**D1 — Entidades de dominio contienen campos de colección para datos relacionados**

Archivo: `backend/app/domain/entities/branch.py`

Descripción: La entidad `Branch` contiene campos `services`, `schedules`, `rating_summary`, `availability_summary` que representan datos relacionados. Esto es aceptable para el MVP pero podría ser un problema en dominios más complejos donde la entidad debería solo contener su propio estado.

Impacto: Bajo — aceptado para MVP.

**D2 — Router prefix `/sucursales` no coincide con patrón del plan**

Archivo: `backend/app/api/v1/routers/public_branches.py` (línea 10): `APIRouter(prefix="/sucursales", ...)`

Descripción: El plan especifica rutas bajo `/api/v1/clinics/branches/*`. El router de listados usa `/sucursales` como prefijo, lo que podría causar problemas de integración con el frontend.

Impacto: Bajo — no es una violación de Clean Architecture. Es un tema de contrato API que corresponde al gate de functional review o QA.

**D3 — Sin gestión explícita de transacciones**

No se encontraron contextos de transacción explícitos (`db.begin()`, `db.commit()`, etc.) en los use cases o repositorios. Para operaciones de solo lectura (GET) esto es aceptable.

Impacto: Bajo — aceptado para MVP dado que todos los endpoints BE-004 son de solo lectura.

## Grafo de dependencias verificado

```
API Layer (routers)
    ↓ depends on
Application Layer (use cases + application DTOs)
    ↓ depends on
Domain Layer (entities + repository interfaces)

Infrastructure Layer (ORM models + repo implementations)
    ↓ depends on
Domain Layer (implements interfaces, maps to entities)
```

## Dependencias correctas verificadas

| Capa | Verificación | Resultado |
|------|-------------|-----------|
| Domain → Frameworks | Sin imports de FastAPI, SQLAlchemy en domain | ✅ PASS |
| Domain → Pydantic | Solo pydantic.BaseModel y stdlib | ✅ PASS |
| Repository interfaces | ABC puro, sin dependencias externas | ✅ PASS |
| Use cases → Domain | Solo importa `app.domain.repositories.*` y `app.domain.entities.*` | ✅ PASS |
| Use cases → Application DTOs | Importa desde `app.application.dtos` (no desde API) | ✅ PASS |
| Infrastructure → Domain | Implementa interfaces de dominio, mapea ORM→entities | ✅ PASS |
| Infrastructure → SQLAlchemy | ORM models usan SQLAlchemy correctamente | ✅ PASS |
| API → Use cases | Routers llaman use cases via DI | ✅ PASS |
| API → Schemas | Pydantic schemas para validación/respuesta | ✅ PASS |
| Circular deps | No se detectaron ciclos en el código BE-004 | ✅ PASS |

## Hallazgos pre-existentes (fuera de alcance BE-004)

Los siguientes violations existen en el repositorio pero fueron introducidos por otros slices:

| # | Origen | Destino | Severidad | Slice origen |
|---|--------|---------|-----------|-------------|
| P1 | `application/use_cases/clinic_search.py` | `api/v1/schemas/clinic_search.py` | Critical | BE-003 |
| P2 | `application/use_cases/public_clinics.py` | `api/v1/schemas/public_clinic.py` | Critical | BE-003 |
| P3 | `domain/repositories/session_repository.py` | `infrastructure/database/models/session.py` | Critical | BE-002 |

Estos hallazgos están documentados pero **no son responsabilidad de BE-004**.

## Checklist de revisión

- [x] Contrato BE validado.
- [x] Arquitectura revisada.
- [x] Pruebas unitarias por archivo productivo modificado — `test_branch_profile.py`, `test_branch_profile_security.py`, `api/test_branch_profile.py` existen.
- [x] Permisos e IDOR/BOLA revisados — `is_branch_accessible()` implementado correctamente con validación de ownership.
- [x] Schemas separados de ORM — Pydantic schemas independientes de modelos SQLAlchemy.
- [x] Dominio independiente de frameworks — Sin imports de FastAPI/SQLAlchemy en domain.
- [x] Repository pattern — Interfaces en domain, implementaciones en infrastructure.
- [x] Routers sin lógica de negocio — Solo HTTP handling y DI.
- [x] Validación script — `validate_slice_plan.py BE-004 --stage review` PASS

## Decision final

- **Decision: `APPROVED`**
- **Evidencia:**

1. **C1 — Application → API dependency**: ✅ RESUELTO (DTOs movidos a `app/application/dtos/`)
2. **M1 — Router return type annotations**: ✅ RESUELTO (schemas correctos)
3. **M2 — Routers importan implementaciones concretas**: ✅ RESUELTO (ABC + local imports)
4. **D1-D3 — Hallazgos menores**: ✅ ACEPTADOS PARA MVP
5. **Validación script**: ✅ PASS (`validate_slice_plan.py BE-004 --stage review`)
6. **Tests**: ✅ Existen pruebas unitarias para use cases y API endpoints
7. **Grafo de dependencias**: ✅ Sin violaciones en el código BE-004

## Cierre del gate

Estado de ejecucion: APPROVED
Siguiente paso recomendado: `/security-review BE-004`
Motivo: La arquitectura Clean Architecture está aprobada sin hallazgos bloqueantes. El siguiente gate en el flujo es la revisión de seguridad para validar IDOR/BOLA, sanitización de inputs y protección de datos sensibles.


La arquitectura de BE-004 cumple con los principios de Clean Architecture:
- Dependencias fluyen correctamente hacia adentro (API → Application → Domain)
- Application layer es independiente de la capa API
- Repository pattern implementado correctamente con interfaces ABC
- Separación clara entre DTOs de aplicación y schemas de respuesta

## Estado global: READY_FOR_REVALIDATION

### Hallazgos corregidos

**C1 — Application layer importa schemas del API layer** ✅ CORREGIDO
- DTOs movidos a `app/application/dtos/` (nuevo directorio)
- `public_branches.py` actualizado: `from app.application.dtos import ...`
- `public_services.py` actualizado: `from app.application.dtos import ...`
- `__init__.py` exporta todos los DTOs públicos

**M1 — Router return type annotations usan entidades de dominio** ✅ CORREGIDO
- `get_branch_public_profile`: retorno cambiado de `-> Branch` a `-> BranchPublicProfile`
- `get_branch_protected_profile`: retorno cambiado de `-> Branch` a `-> BranchProtectedProfile`

**M2 — Routers importan implementaciones concretas de infraestructura** ✅ CORREGIDO
- `branch_profile.py`: imports cambiados a interfaces ABC (`BranchRepository`, `ServiceRepository`, etc.)
- Dependency functions usan anotaciones de tipo ABC + import local de impls concretos
- `public_branches.py`: igual patrón aplicado con `BranchRepository` interface

**D1-D3 — Hallazgos menores** ✅ ACEPTADOS PARA MVP
- D1: Entidades con campos de colección — aceptado para MVP
- D2: Router prefix `/sucursales` — documentado y aceptado
- D3: Sin gestión explícita de transacciones — aceptado para operaciones de solo lectura

## Siguiente paso recomendado

Rerun QA review para revalidar los hallazgos corregidos.
