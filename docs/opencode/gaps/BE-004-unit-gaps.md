# BE-004 — Gaps de cobertura de pruebas unitarias

**Slice**: BE-004 (perfil público de clínica/sucursal)  
**Fecha**: 2026-08-04  
**Proposito**: Identificar archivos producto del slice que NO tienen prueba unitaria explicita.  

---

## Metodoologia

Para cada archivo productivo identificado en el plan y las revisiones, se verifico:
1. Si existe un archivo `.test.ts`, `.spec.ts` o `test_*.py` con assertion directa sobre su comportamiento public.
2. Si la cubierta es solo indirecta (mockeo via otros archivos), se marca como GAP de cobertura explicita pero no GAP funcional.

---

## 1. Backend — Archivos sin prueba unitaria explicita

### Gap BE004-DB1 — Domain entity: `backend/app/domain/entities/branch.py`
- **Tipo**: Entity Pydantic (7 modelos)
- **Sin test explicito**: ✅ SINO
- **Verificacion directa**: No existe `test_branch_entity*.py`. Los entities solo se crean en fixtures de use-cases tests.
- **Impacto**: Medio — los schemas Pydantic no se validan contra reglas de serializacion (construccion, defaults, forward references). La integracion con schemas API es implicita.
- **Riesgo**: Si `RatingSummary`, `AvailabilitySummary` o `Service` tienen logica en `model_validate` o validators, esta queda sin cobertura directa.

### Gap BE004-DB2 — Domain port (ABC): `backend/app/domain/repositories/branch_repository.py`
- **Tipo**: 5 interfaces ABC
- **Sin test explicito**: ✅ SINO
- **Verificacion**: Solo se mockean en tests de use-cases. Las firmas ABC no son verificadas por un test que instancie todas las clases concretas.
- **Impacto**: Menor — los ABCs son puros Python sin logica; el riesgo es solo que la abstraccion cambie y el adapter se desalinee silenciosamente.
- **Riesgo medio/bajo**.

### Gap BE004-DB3 — Infrastructure ORM models: `backend/app/infrastructure/database/models/*.py` (5 archivos)
| Modelo | Tabla sin test explicito |
|--------|--------------------------|
| `branch.py` | branches |
| `service.py` | services |
| `branch_schedule.py` | branch_schedules |
| `rating_summary.py` | rating_summaries |
| `availability_summary.py` | availability_summaries |
- **Sin test explicito**: ✅ SINO (ninguno)
- **Impacto**: Menor — estos son modelos declarativos de SQLAlchemy, validados indirectamente por el adapter. No tienen logica compleja.
- **Riesgo bajo**.

### Gap BE004-DB4 — Repository impl: `backend/app/infrastructure/database/repositories/branch_repository.py`
- **Tipo**: 5 clases repo adapter (BranchRepoImpl, ServiceRepoImpl, etc.)
- **Sin test explicito de adaptador como unidad**: ⚠️ Parcial
- **Verificacion**: Se mockean completamente en todos los tests. Las querys SQL y el mapeo ORM→entity NO se verifican con una DB real o al menos un session simulado.
- **Impacto**: Medio — si la estructura de columnas cambia, las queries podrian fallar silenciosamente sin test directo del adapter.
- **Riesgo medio**.

### Gap BE004-DB5 — Schema protegido: `backend/app/api/v1/schemas/branch_protected.py`
- **Tipo**: Pydantic response model (BranchProtectedProfile)
- **Sin assertion explicita de schema**: ⚠️ Parcial  
- **Verificacion**: Los tests de endpoint retornan BranchProtectedProfile pero las assertions solo verifican status_code. No se hace `assert schema.model_validate(obj).field == expected`.
- **Impacto**: Bajo-Medio.

**Resumen backend**: 5 gaps. Los mas significativos son **DB1** (entities sin test directo) y **DB4** (adapter orm sin prueba directa sobre session simulada o fixture DB).

---

## 2. Frontend — Archivos sin prueba unitaria explicita

### Gap FE004-FB1 — Cliente API publico: `frontend/src/shared/api/branch-client.ts`
- **Sin test explicito**: ✅ SINO (no existe `.test.ts` ni `.spec.ts`)
- **Verificacion directa**: El archivo tiene 11 lineas, funcion `fetchBranchPublic` con error handling basico. Nada se prueba.
- **Impacto**: Alto — la capa de comunicacion client→server SIN test es el primer punto de fallo si cambia el endpoint, response format o manejo de errores.

### Gap FE004-FB2 — Cliente API protegido: `frontend/src/shared/api/branch-client-protected.ts`
- **Sin test explicito**: ✅ SINO
- **Impacto**: Alto — maneja Authorization bearer, fallback a localStorage, y error handling mas complejo. Sin ninguna prueba.

### Gap FE004-FB3 — Paginas de ruta: `frontend/src/app/clinics/[id]/page.tsx`
- **Sin test explicito**: ✅ SINO  
- **Impacto**: Medio — es una pagina Page (SSR) con loading/error/empty/success. Se verificaria via testing de componentes o E2E.

### Gap FE004-FB4 — Pagina protegida: `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx`
- **Sin test explicito**: ✅ SINO
- **Impacto**: Medio — logica de redirect a login si 401. Se verificaria via testing de componentes.

### Gap FE004-FB5 — Feature: `frontend/src/features/public-clinic-profile/BranchProfile.tsx`
- **Sin test explicito**: ✅ SINO
- **Impacto**: Alto — componente principal que combina datos de services, schedules, rating summary. Sin prueba de rendering ni de interaccion.

### Gap FE004-FB6 — Componente UI: `frontend/src/shared/ui/components/Loading.tsx`
- **Sin test explicito**: ✅ SINO
- **Impacto Bajo-Medio** — componente puramente presentacional, pero se verifica renderizado CSS.

### Gap FE004-FB7 — Componente UI: `frontend/src/shared/ui/components/ErrorBanner.tsx`
- **Sin test explicito**: ✅ SINO
- **Impacto**: Medio — contiene logica de botoner y estado visual. Se verificaria con testing de componentes.

### Gap FE004-FB8 — Componente UI: `frontend/src/shared/ui/components/EmptyState.tsx`
- **Sin test explicito**: ✅ SINO  
- **Impacto**: Bajo-Medio — SVG puramente presentacional.

**Resumen frontend**: 8 gaps (FB1-FB8). Todos los archivos de producto frontend carecen de pruebas explicitas porque:
1. No existe `.test.ts` ni `.spec.ts` en todo el repo `frontend/src/`.
2. El package.json probablemente no tiene `@testing-library/react` o framework de testing configurado.

---

## 3. Resumen consolidated by layer

| Capa | Archivos producto | Archivos con test explicito | GAP sin test | Mas significativo |
|------|------------------|--------------------------|-------------|-------------------|
| **Backend - Domain** | 7 entities | 0 | 7 (1 gap) | DB1: Entities |
| **Backend - Port** | 5 ABC | 0 | 5 (1 gap) | DB2: ABC ports |
| **Backend - Infra ORM** | 5 models | 0 | 5 (1 gap) | DB3: Models |
| **Backend - Repo impl** | 1 file | 0 | 1 (1 gap) | DB4: Repository impl |
| **Backend - Schema protected** | 1 file | 0 | 1 (1 gap) | DB5: Protected schema |
| **Frontend - API client** | 2 files | 0 | 2 (BOTH GAP!) | FB1, FB2: Both clients |
| **Frontend - Pages/Routes** | 2 files | 0 | 2 (BOTH GAP) | FB3, FB4 |
| **Frontend - Feature UI** | 1 file | 0 | 1 (GAP!) | FB5: BranchProfile |
| **Frontend - UI Components** | 3 files | 0 | 3 | FB6-FB8 |

### Total de gaps por capa
- **Backend total**: 5 gaps (DB1-DB5) — impacto medio
- **Frontend total**: 8 gaps (FB1-FB8) — impacto alto (todo el frontend sin test alguno)

---

## 4. Clasificacion por severidad del gap de pruebas

| Nr | Gap | Capa | Severidad | Justificacion |
|----|-----|------|-----------|---------------|
| **G1** | FE004-FB1 + FE004-FB2 | Frontend client API | CRITICO | 100% del frontend sin test. Los dos clientes API no verificados en absoluto. |
| **G2** | BE004-DB3 + BE004-DB5 | Backend ORM/Schema | MEDIO | Models y schemas sin prueba explicita pero verificables via endpoint. |
| **G3** | FE004-FB5 | Frontend componente principal | ALTO | BranchProfile es el unico componente de feature, maneja estado de datos complejo. |
| **G4** | BE004-DB1 + BE004-DB4 | Backend entity/repo impl | MEDIO | Entities y adapters ORM sin prueba directa sobre sus contras/mappings. |
| **G5** | FE004-FB3 + FE004-FB4 | Frontend pages | BAJO-MEDIO | Paginas SSR se verificarian via E2E; unit tests de pagina son menos utiles. |

---

## 5. Decision por gap

### G1 (Frontend sin test alguno) — Bloqueo para merge en produccion
**Estado**: GAP CRITICO abierto  
**Accion recomendada**: Agregar `@testing-library/react` y jest/vitest al package.json del frontend. Implementar minimo 2 tests:
- Uno que verifica `fetchBranchPublic` (mocked fetch) retorna BranchPublicProfile correcto
- Uno que renderiza `BranchProfile` con datos mock para verificar UI rendering

### G2 (Backend ORM models sin test) — Gap aceptable para MVP
**Estado**: GAP medio  
**Accion recomendada**: Para el MVP se acepta. En slice siguiente, crear fixture de DB o usar SQLite in-memory para tests del ORM layer.

### G3-F5 — Prioridad media/baja
**Estado**: GAPs documentados  
**Accion recomendada**: Integrar en plan de la siguiente iteracion.

---

## 6. Archivos productivos que SI tienen prueba unitaria explicita

| Archivo | Suite de test | Verificado en runner |
|---------|--------------|---------------------|
| `application/use_cases/branch_profile.py` | `test_branch_profile.py` (4 tests directos) | ✅ Cada public method tiene assertion directa |
| `api/v1/routers/branch_profile.py` (public endpoint) | `test_branch_profile.py` + `test_branch_profile_security.py` | ✅ Mocked use-case + TestClient HTTP assertions |
| `core/security.py` (get_current_access_user) | `test_branch_profile_security.py` | ✅ 3 tests con headers reales via TestClient |

> Nota importante: Los tests de use-cases son de **unidad con mocks** (no integration real), pero tienen assertion explicita sobre las funcionalidades. Son validos para cubrir gap "por cada archivo productivo modificado" en la regla de clean architecture review.

---

*Fin del documento de gaps.* 
