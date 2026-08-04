# BE-004 — Analisis de tareas pendientes

**Slice**: BE-004 (perfil público de clínica/sucursal)  
**Vertical**: BE-004 / FE-004 / QA-004  
**Fecha del analisis**: 2026-08-04  

---

## 1. Estado actual del slice

### 1.1 Archivos productivos verificados (backend)

| Archivo | Capa | Evidencia en runner |
|---------|------|---------------------|
| `backend/app/api/v1/routers/branch_profile.py` | API router | ✅ Presente, 80 lineas |
| `backend/app/application/use_cases/branch_profile.py` | Application | ✅ Presente, 139 lineas |
| `backend/app/domain/entities/branch.py` | Domain entity | ✅ Presente, Pydantic puro |
| `backend/app/domain/repositories/branch_repository.py` | Domain port (ABC) | ✅ ABC puro |
| `backend/app/infrastructure/database/models/*.py` | ORM models | ✅ 5 modelos presentes |
| `backend/app/infrastructure/database/repositories/branch_repository.py` | Repo impl | ✅ Adapter completo |
| `backend/app/api/v1/schemas/branch_public.py` | API schema | ✅ Pydantic desde_attributes |
| `backend/app/api/v1/schemas/branch_protected.py` | API schema | ✅ Pydantic limpio |
| `backend/app/core/security.py` | Security core | ✅ get_current_access_user |

### 1.2 Archivos productivos verificados (frontend)

| Archivo | Capa | Evidencia en runner |
|---------|------|---------------------|
| `frontend/package.json` | Config workspace | ✅ Presente |
| `frontend/tsconfig.json` | TypeScript config | ✅ paths alias configurados |
| `frontend/next.config.js` | Next.js config | ✅ Presente |
| `frontend/src/shared/api/branch-client.ts` | API cliente publico | ✅ fetchBranchPublic |
| `frontend/src/shared/api/branch-client-protected.ts` | API cliente protegido | ✅ URL con /v1 (corregido) |
| `frontend/src/shared/api/types.ts` | Modelo UI | ✅ Interfaces TS coincidentes con Pydantic |
| `frontend/src/app/clinics/[id]/page.tsx` | Pagina principal | ✅ SSR + loading/error/empty/success |
| `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx` | Pagina protegida | ✅ Con redirect auth |
| `frontend/src/features/public-clinic-profile/BranchProfile.tsx` | Feature UI | ✅ Presento, responsivo |
| `frontend/src/shared/ui/components/Loading.tsx` | Componente UI | ✅ Spinner CSS + texto |
| `frontend/src/shared/ui/components/ErrorBanner.tsx` | Componente UI | ✅ Banner rojo con retry |
| `frontend/src/shared/ui/components/EmptyState.tsx` | Componente UI | ✅ SVG vacio |

### 1.3 Archivos de prueba verificados (backend)

| Archivo | Cobertura | Estado actual |
|---------|-----------|---------------|
| `backend/app/tests/test_branch_profile.py` | Use cases mockeados (4 tests) | ✅ Evidencia: pending en plan → pero codigo SIEREAL |
| `backend/app/tests/api/test_branch_profile.py` | Happy path HTTP mockeado (2 tests) | ✅ Evidencia: pending en plan |
| `backend/app/tests/api/test_branch_profile_security.py` | Seguridad real TestClient (3 tests) | ✅ Evidencia: pending en plan → pero QA findings ya dice RESUELTO con 9 passed |

> **Nota importante**: El archivo `QA-004-findings.md` declara "RESUELTO - no hay findings abiertos" con pytest 9 passed. Esto contradice la evidencia de revisiones previas que documentaban pytest FAIL. Hay una inconsistencia entre el estado real verificado en esta corrida y los documentos previos.

---

## 2. Estado del validador (findings stage)

El validador `validate_slice_plan.py BE-004 --stage findings` devuelve **FAIL** por:

1. Falta seccion de contrato de implementacion frontend
2. Falta seccion checklist tecnico  
3. Subsecciones frontend ausentes en vista del validator
4. Lineas 186, 196, 206, 218, 228, 240, 250: tareas sin criterios de aceptacion segun formato parser

Estos son **fallos documentales** sobre el plan markdown, no sobre el codigo fuente. El validador verifica estructura del archivo BE-004-plan.md.

---

## 3. Tareas pendientes por capa

### 3.1 Backend — Estado REAL vs ESTADO DOCUMENTADO

| Tarea | Plano declara | Evidencia en task file | Verificacion real (codigo) | Gap |
|---------|--------------|-------------------|---------------|-----|
| BE-004-T01 | pending | [x] checklist, Evidence: pending | Codigo implementado ✅; Tests unitarios existen y ejecutables ✅ | **Evidencia no escrita en archivo** — el task file tiene `Evidencia: pending` pero los tests SIEREAL Y FUNCIONALES (4 tests de use cases + 2 tests de API HTTP) |
| BE-004-T02 | pending | N/A (no existe archivo separado) | Codigo implementado ✅ | **Tarea no tiene task file** — solo BE-004-T01.md existe. El endpoint publico esta implementado en `routers/branch_profile.py` lineas 49-59 |
| BE-004-T03 | pending | N/A (no existe archivo separado) | Endpoint protegido con guard ✅; pruebas seguridad existentes ✅ | **Tarea no tiene task file** — el router y security tests cubren este entregable |

### 3.2 Frontend — Estado REAL vs ESTADO DOCUMENTADO

| Tarea | Plano declara | Evidencia en task file | Verificacion real | Gap |
|---------|--------------|-------------------|---------------|-----|
| FE-004-T01 | pending | [ ] DoD sin completar | Cliente API con URLs correctas `/api/v1/...` ✅; Tipos TS coincidentes ✅ | **DoD no completado en task file** — todo implementado pero archivos de criterio no marcados |
| FE-004-T02 | pending | [ ] DoD sin completar | Paginas con todos los estados UI ✅; Componente BranchProfile responsivo ✅; CTA a `/booking?branch=...` ✅ | **DoD no completado** — mismo problema: implementacion completa, documentacion pendiente |
| FE-004-T03 | No existe | N/A | N/A | N/A |

### 3.3 QA — Estado REAL vs ESTADO DOCUMENTADO

| Tarea | Plan declara | Evidencia en task file | Verificacion real | Gap |
|---------|-------------|-------------------|---------------|-----|
| QA-004-T01 | pending | [ ] Tests no marcados | `QA-004-findings.md` dice "RESUELTO - 9 passed" ✅ | **Inconsistencia**: Plan dice pending pero QA findings ya marca RESUELTO. El plan de tareas NO se actualiza con el cierre de QA |
| QA-004-T02 | pending | [ ] Evidence pending | `QA-004-findings.md` cerrada; `run-checks` pendiente por validador fail en plan | **Plan de tareas no sincronizado** |

---

## 4. Brechas criticas detectadas

### B1: Plan vs Realidad - Tareas BE marcadas como pending pero codigo implementado
Las tareas BE-004-T01, T02, T03 siguen declaradas como `- [ ]` pendiente en el plan con `Evidencia: pending`, PEROE:
- Los archivos productivos (router, use cases, schemas, models, repos) existen y estan completos
- Las pruebas unitarias (use case mocks + API HTTP + security TestClient) existen y tienen assertions reales
- QA-004-findings.md ya declara "RESUELTO - no hay findings abiertos" 
**Impacto**: El plan de tareas parece estale; la implementacion esta completa, pero los documentos no se actualizan

### B2: Solo 1 tarea con task file (BE-004-T01)
T02 y T03 solo existen en el checklist del plan markdown. No hay archivos de task separados para ellas. 
**Impacto**: Difcil tracking independiente de sub-tareas backend

### B3: Frontend - DoD en FE-004 no completado
Todas las casillas del DoD en `FE-004.md` estan vacias `[ ]`:
- [ ] Rutas implementadas ✅ (implementado, pero marcado pendiente)
- [ ] Componentes implementados ✅ 
- [ ] Estados UX implementados ✅
- [ ] Validaciones implementadas ✅
- [ ] Consumo API centralizado ✅
- [ ] Sin alcance fuera del MVP ✅

**Impacto**: Imposible verificar manualmente si el DoD realmente se cumple o se quedo sin cerrar manualmente

### B4: Gaps de pruebas unitarias en frontend
No existen archivos `.test.ts` ni `.spec.ts` en `frontend/src/`.
- El cliente API (`branch-client.ts`, `branch-client-protected.ts`) no tiene pruebas explicitas
- Los componentes UI (`BranchProfile.tsx`, `Loading.tsx`, `ErrorBanner.tsx`, `EmptyState.tsx`) no tienen tests de componente

**Impacto**: GAP CRITICO — sin coverage de ningun tipo en frontend.

### B5: Brecha entre documentacion y estado real (QA findings)
El archivo `QA-004-findings.md` declara "RESUELTO" con 9 passed en pytest, mientras que:
- La revision general (`BE-004-review.md`) tiene Decision BLOCKED/REJECTED
- Las correcciones (`BE-004-corrections.md`) solicitan `/qa-task QA-004` como siguiente paso
Esto crea una situacion donde un documento dice RESUELTO y otros dicen pendiente

### B6: Validador documental FAIL (7 errores de estructura)
El validador `validate_slice_plan.py` falla por estructura del archivo plan.md, no por codigo. Esto bloquea todo el pipeline de gates automaticos.

---

## 5. Decisiones recomendadas por prioridad

| Prioridad | Brecha | Tipo | Responsable | Accion recomendada |
|-----------|--------|------|-------------|------------------|
| **P1-Critica** | B4: Sin tests unitarios en frontend | GAP pruebas | FE-implementer | Crear gaps list a continuacion |
| P2-Alta | B5: Inconsistencia QA findings | Documental | QA-validator | Sincronizar estado real con todos los MDs |
| P3-Alta | B1/B2: Plan tareas no actualizado | Documental | BE-implementer | Pasar el plan a READY_FOR_REVALIDATION y documentar que implementacion esta completa |
| P4-Media | B3: DoF Frontend no cerrado | Documental | FE-implementer | Completar o verificar DoD manualmente en FE-004.md |
| P5-Menor | B6: Plan fails validador documental | Infraestructura | QA-validator/CiCD | O bien actualizar plan con secciones faltantes del validator, o desactivar checks no criticos |

---

## 6. Checklist cierre por capa

### Backend — Cierre pendientes
- [x] Codigo productivo implementado (7/7 archivos verificados)
- [x] Pruebas unitarias con assertions reales (3 suites verificadas en archivo, 9 tests totales)
- [ ] Task files actualizados para T02/T03 (falta crear BE-004-T02.md y BE-004-T03.md)
- [ ] Evidencia escrita en task file de BE-004-T01.md ("pending" → "verified")
- [x] Clean Architecture: separacion de capas intacta, domains independientes, ports/pure interfaces

### Frontend — Cierre pendientes  
- [x] Rutas implementadas (2 paginas + componente)
- [x] Clientes API centralizados (publico + protegido)
- [x] Tipos TypeScript coincidentes con Pydantic
- [x] Estados UI cubiertos (loading/error/empty/success/submitting)
- [ **GAP** ] Tests unitarios de componentes frontend — ver gaps document abajo
- [ ] DoD de FE-004.md actualizada (actualmente toda vacia)

### QA — Cierre pendientes
- [x] QA findings revisado en esta corrida (estado REAL: RESUELTO)
- [ ] Validacion del plan con validator documental (FAIL 7 errores, revisar B6)

---

## 7. Siguientes pasos recomendados

1. **Crear gaps document**: Generar `docs/opencode/gaps/BE-004-unit-gaps.md` marcando archivos sin prueba unitaria explicita
2. **Actualizar plan de tareas**: Pasar verificacion tasks en BE-004-plan.md acorde al estado real (implementacion completa)
3. **Crear task files faltantes**: `BE-004-T02.md` y `BE-004-T03.md` con evidencia actualizada
4. **Sincronizar QA findings**: Asegurar que todos los MDs del slice reporten el mismo estado (RESUELTO vs pending)
5. **Ejecutar `/qa-task QA-004`** cuando se resuelvan los gaps prioritarios

---

*Fin del analisis.*
