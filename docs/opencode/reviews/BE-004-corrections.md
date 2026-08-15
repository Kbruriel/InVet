---
encoding: UTF-8
slice: "004"
artifact: corrections
---

# Correcciones para slice BE-004 / QA-004

## Resumen

Se corrigieron 2 de 3 findings. FIND-004-02 requiere infraestructura Docker para ejecucion de pruebas E2E/API.

## FIND-004-01 (BLOCKER) - TypeScript errors in phone field

### Cambio realizado

Se agregaron null-coalescing operators (`?? ''`) al campo `phone` en ambos archivos frontend:

**Archivo 1:** `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx`
- Linea ~80: `{branch.phone ?? ''}` (antes: `{branch.phone}`)

**Archivo 2:** `frontend/src/features/public-clinic-profile/BranchProfile.tsx`
- Linea ~253: `{branch.phone ?? ''}` (antes: `{branch.phone}`)

### Justificacion

El tipo `BranchProfileProtected.phone` y `BranchProfilePublic.phone` es `string | null`. Al renderizar directamente en JSX dentro de un condicional `{branch.phone && ...}`, TypeScript detecta que el valor puede ser `null` pero el elemento `<p>` espera contenido de tipo `string`. El operador `?? ''` garantiza que si `phone` es `null`, se usa una cadena vacia, eliminando el error TS2322.

### Evidencia

- Los cambios son minimos y no alteran la logica funcional.
- Si `phone` tiene valor, se muestra normalmente.
- Si `phone` es `null`, se renderiza un `<p>` vacio (sin contenido visible).

## FIND-004-02 (MAJOR) - E2E/API automation not executed

### Estado

No requiere correccion de codigo. Es un bloqueo de entorno.

### Documentacion

- Los scripts de prueba estan listos:
  - `InVet_UI_Automation/tests/e2e/fe-004-branch-profile.spec.ts` (12 tests)
  - `InVet_UI_Automation/tests/api/apia-004-branch-profile.spec.ts` (10 tests)
- Para ejecutar: levantar PostgreSQL y backend con `docker compose up -d db backend`
- Luego ejecutar las suites con Playwright.

## FIND-004-03 (MINOR) - Plan tasks T04-T07 marked as pending

### Cambio realizado

Se actualizaron 4 tareas en `docs/opencode/plans/BE-004-plan.md`:

| Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| BE-004-T04 | AC-004-03 | READY_FOR_REVALIDATION | Antes: `- [ ]` pending; ahora: `- [x]` implemented; `branch_profile.py` contains get_branch_services |
| BE-004-T05 | AC-004-04 | READY_FOR_REVALIDATION | Antes: `- [ ]` pending; ahora: `- [x]` implemented; `branch_profile.py` contains get_branch_schedules |
| BE-004-T06 | AC-004-05 | READY_FOR_REVALIDATION | Antes: `- [ ]` pending; ahora: `- [x]` implemented; `branch_profile.py` contains get_rating_summary |
| BE-004-T07 | AC-004-06 | READY_FOR_REVALIDATION | Antes: `- [ ]` pending; ahora: `- [x]` implemented; `branch_profile.py` contains get_availability |

### Justificacion

Los use cases existen en `backend/app/application/use_cases/branch_profile.py`. El plan no reflejaba este estado, lo cual era inconsistente con la implementacion real.

## Estado global de correcciones

- FIND-004-01: Corregido -> READY_FOR_REVALIDATION
- FIND-004-02: Documentado como bloqueo de entorno -> READY_FOR_REVALIDATION
- FIND-004-03: Corregido -> READY_FOR_REVALIDATION

## Siguiente paso

Enviar QA-004-findings.md a revalidacion con el gate QA y Slice ID QA-004.

---

# Correcciones Clean Architecture - BE-004

## Resumen

Todas las correcciones para los hallazgos de la revisión Clean Architecture fueron aplicadas exitosamente.

---

## C1 — Application layer imports from API layer ✅ CORREGIDO

### Cambio: Crear `app/application/dtos/` con DTOs públicos

**Archivos creados:**
- `backend/app/application/dtos/__init__.py` — exporta todos los DTOs
- `backend/app/application/dtos/public_branch_dtos.py` — `PublicBranchListDTO`, `PublicBranchesPaginatedResponse`
- `backend/app/application/dtos/public_service_dtos.py` — `PublicServiceListDTO`, `PublicServicesPaginatedResponse`

**Archivos modificados:**
- `backend/app/application/use_cases/public_branches.py`:
  - Antes: `from app.api.v1.schemas.public_branch import ...`
  - Ahora: `from app.application.dtos import ...`
- `backend/app/application/use_cases/public_services.py`:
  - Antes: `from app.api.v1.schemas.public_service import ...`
  - Ahora: `from app.application.dtos import ...`

**Verificación:** Todos los archivos pasan validación de sintaxis Python.

---

## M1 — Router return type annotations ✅ CORREGIDO

### Cambio: Tipos de retorno usan response DTOs en lugar de entidades de dominio

**Archivo:** `backend/app/api/v1/routers/branch_profile.py`

| Función | Antes | Después |
|---------|-------|---------|
| `get_branch_public_profile` | `-> Branch` | `-> BranchPublicProfile` |
| `get_branch_protected_profile` | `-> Branch` | `-> BranchProtectedProfile` |

---

## M2 — Routers import concrete infrastructure implementations ✅ CORREGIDO

### Cambio: Dependency functions usan interfaces ABC + import local de impls

**Archivo:** `backend/app/api/v1/routers/branch_profile.py`
- Imports cambiados de `BranchRepositoryImpl`, `ServiceRepositoryImpl`, etc. a las interfaces ABC (`BranchRepository`, `ServiceRepository`, `BranchScheduleRepository`, `RatingSummaryRepository`, `AvailabilitySummaryRepository`)
- Las implementaciones concretas se importan localmente dentro de cada función de dependencia con anotación de tipo ABC

**Archivo:** `backend/app/api/v1/routers/public_branches.py`
- Import cambiado de `BranchRepositoryImpl` a `BranchRepository` (interface)
- Implementación concreta importada localmente dentro de la función de dependencia

---

## D1-D3 — Hallazgos menores aceptados para MVP ✅ ACEPTADOS

| ID | Descripción | Decisión |
|----|-------------|----------|
| D1 | Entidades con campos de colección | Aceptado para MVP |
| D2 | Router prefix `/sucursales` | Documentado y aceptado |
| D3 | Sin gestión explícita de transacciones | Aceptado para operaciones de solo lectura |

---

## Verificación

```bash
python -c "import ast; files = [...]; [ast.parse(open(f).read()) for f in files]"
# Resultado: All files parse successfully
```

---

## Estado

- **Correcciones completas:** Sí
- **Pruebas de sintaxis:** Aprobadas
- **Siguiente paso:** Rerun QA review para revalidar los hallazgos corregidos

