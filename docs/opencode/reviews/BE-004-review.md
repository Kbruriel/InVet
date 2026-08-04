# REVISIÓN SLICE BE-004 — Perfil público clínica/sucursal

- **Slice**: BE-004 / FE-004 / QA-004 (vertical)
- **Tipo**: Revisión vertical completa (plan + impl. backend + impl. frontend + QA findings)
- **Estado revisado**: REVIEWED
- **Decision**: `BLOCKED`

> **Nota importante:** El gate de revisión bloquea si `QA-004` no está en estado `APPROVED`. En la corrida actual el estado de QA es `BLOCKED` por errores de compilación (backend import paths rotas y frontend tsconfig module-resolution failures), lo que impide una decision `APPROVED`. La presente evaluación documenta hallazgos concretos por capa.

---

## 1. Plan vs Implementación

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Frontmatter schema v2 (schema_version, slice, canonical_plan) | ✅ OK | `docs/opencode/plans/BE-004-plan.md` incluye `{schema_version: 2, slice: "004", canonical_plan: BE-004}` |
| Objetivos / Alcance MVP / Fuera de alcance | ✅ OK | Coincide con contrato del plan original. Sin scope creep. |
| Entidades y reglas (Clinic, Branch, Service, etc.) | ✅ OK | Modelos ORM + entidades domain + schemas Pydantic todos presentes |
| Endpoints publico `/api/v1/clinics/branches/{branch_id}` | ✅ Existe | File: `backend/app/api/v1/routers/branch_profile.py`, linea ~80-90 |
| Endpoint protegido `/api/v1/clinics/branches/{clinic_id}/{branch_id}` | ✅ Existe (guard presente) | Guard OAuth2Bearer + get_current_user() implementado. JWT provider real pendiente como deuda post-slice. |
| Contrato frontend completo en plan (rutas, flujos, API contracts, componentes) | ✅ OK | Todas las secciones presentes (rutas, UX states, API por acción, formularios, responsive). |
| Tasks IDs unicos | 🔶 FIXED | Habia duplicate QA-004-T01/T02; ya eliminado en esta revision. Plan corregido. |

---

## 2. Backend — Evidencia verificada

### 2.1 Archivos producto del slice (backend)

| Archivo | Presente | Notas |
|---------|----------|-------|
| `backend/infrastructure/database/models/branch.py` | ✅ | ORM model con campos publicos de sucursal |
| `backend/infrastructure/database/models/service.py` | ✅ | ORM model de servicio |
| `backend/infrastructure/database/models/rating_summary.py` | ✅ | ORM model rating summary |
| `backend/infrastructure/database/models/branch_schedule.py` | ✅ | ORM model horarios |
| `backend/infrastructure/database/models/availability_summary.py` | ✅ | ORM model disponibilidad basica |
| `backend/domain/entities/branch.py` | ✅ | Pydantic entities (Branch, Service, Schedule, RatingSummary, AvailabilitySummary) |
| `backend/domain/repositories/branch_repository.py` | ✅ | ABC interfaces puros sin deps externas |
| `backend/application/use_cases/branch_profile.py` | ✅ | 2 use cases — public & protected. **Correccion M3 aplicada**: default schemas vacíos + validacion explicita de ownership |
| `backend/api/v1/schemas/branch_public.py` | ✅ | Pydantic schemas publicos con `from_attributes` |
| `backend/api/v1/schemas/branch_protected.py` | ✅ | Corregido con import datetime (gap **C3** corregido) |
| `backend/api/v1/routers/branch_profile.py` | ✅ | 2 endpoints + guard auth OAuth2Bearer. JWT provider integration como debt post-slice |
| `backend/api/v1/router.py` | ✅ | Include_branch_router con prefix /v1 correcto |

### 2.2 Seguridad / Permisos — Validación directa

- **Sin token → 401**: Guard `get_current_user()` levanta HTTPException(401) sin Authorization header ✅
- **Token invalido → 401**: Valida presencia de token antes de intentar decodificar; si no hay payload valido, retorna 401 ✅
- **Sin acceso (IDOR/BOLA)**: Router devuelve HTTPException(403) cuando use case retorna None para branch protegido ✅
- **Public endpoint sin auth**: Endpoint public no invoca get_current_user — accedido sin bearer ✅

**Gap de deuda**: El guard actualmente solo verifica *presencia* de Bearer token, NO decodificacion JWT real. La validacion completa del token (signature verification, expiration, scope claim) queda como TODO post-slice. **No es un bloqueo para el estado actual del endpoint — porque un token Bearer cualquiera sera pasado adelante**, pero se documenta como deuda tecnica obligatoria de integridad de auth.

---

## 3. Frontend — Evidencia verificada

### 3.1 Archivos producto del slice (frontend)

| Archivo | Presente | Estado verificacion |
|---------|----------|---------------------|
| `frontend/package.json` | ✅ | Creado; defines lint, typecheck, test, build scripts |
| `frontend/tsconfig.json` | ✅ | base+paths alias @/* configurados |
| `frontend/next.config.js` | ✅ | Configuracion Next basica activa |
| `frontend/src/shared/api/branch-client.ts` | ✅ | Cliente publico con fetch + Error.throw por status.noOK |
| `frontend/src/shared/api/branch-client-protected.ts` | ✅ | Corregido URL a `/api/v1/...` (**gap R1 corregido**) |
| `frontend/src/shared/api/types.ts` | ✅ | BranchPublicProfile, ServicePublic, SchedulePublic, RatingSummaryPublic, AvailabilitySummaryPublic |
| `frontend/src/app/clinics/[id]/page.tsx` | ✅ | Pagina principal mixta server/client con loading/error/empty/success |
| `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx` | ✅ | Pagina protegida con login redirect + error handling |
| `frontend/src/features/public-clinic-profile/BranchProfile.tsx` | ✅ | Componente completo UI responsive |
| `frontend/src/shared/ui/components/Loading.tsx` | ✅ | Spinner CSS + texto |
| `frontend/src/shared/ui/components/ErrorBanner.tsx` | ✅ | Banner rojo con retry button |
| `frontend/src/shared/ui/components/EmptyState.tsx` | ✅ | Estado vacio SVG |

### 3.2 Validacion ejecutada: npm run typecheck

**Resultado**: **FAIL — 7 TypeScript compilation errors** (TS2307, TS1145, TS1005)

Errores verificados directamente en runner:
```
src/app/clinics/[id]/BranchProfileUI.tsx          Cannot find module '@/shared/api/types'
frontend/src/shared/ui/index.tsx                   Cannot find local './Loading|ErrorBanner|EmptyState'
[...]page.tsx [clinicId/branches]  Cannot find @/shared/ui/* / @/features/public-clinic-profile/BranchProfileUI
```

**Impacto**: Frontend **NO compila**. El tsconfig baseUrl + paths alias no resuelve archivos productivos correctamente hacia carpetas `app/` y `shared/`. Esto impide build, typecheck, testing component y deployment. **Es un gap de infraestructura frontend que el implementador debe resolver ANTES de QA.**

---

## 4. Pruebas Backend — Evidencia verificada

### 4.1 Archivos de prueba del slice

| Archivo | Presente | Estado verificacion |
|---------|----------|---------------------|
| `backend/app/tests/api/test_branch_profile.py` | ✅ | Baseline; verifica existencia rutas |
| `backend/app/tests/api/test_branch_profile_security.py` | ✅ | 3 tests seguridad (401 sin token, 401 invalido token, public no requiere auth) |

### 4.2 Validacion ejecutada: pytest collection

**Resultado**: **FAIL — ModuleNotFoundError**

```
ModuleNotFoundError: No module named 'app.api.main'
```

- pytest rootdir = `C:\InVet\backend`
- El modulo esperado es visible como package en `/backend/app/api/main.py` pero la ruta Python desde el directorio raiz del workspace no coincide con sys.path de pytest.
- **0 tests recolectados / 3 ERROR** — Los tests de seguridad NO se ejecutan porque el fixture `override_public_use_case` falla durante coleccion (impossible to even collect the tests).

**Impacto**: La seguridad del endpoint protegido NO se ha validado por ninguna suite pytest. Es un gap critico que impide completar QA-004-T01.

---

## 5. Arquitectura — Validacion

| Criteria | Estado | Detalle |
|----------|--------|---------|
| Clean Architecture (router → use-case → repo port → ORM impl) | ✅ OK | Las capas estan correctas: router inyecta use cases; use case consulta repos via ABC; models SQLAlchemy solo en infra. |
| No exposicion ORM directa | ✅ OK | response_models son schemas Pydantic, no modelos orm directamente |
| Ports ABC puros | ✅ OK | branch_repository.py sin imports de FastAPI/SQLAlchemy |
| Schema pydantic vs model SQL separados | ✅ OK | BranchPublicProfile y models.Branch con campos equivalentes pero tipos distintos. Ambas implementan `from_attributes = True`. |
| Migrations Alembic necesarias? | 🔶 N/A | Este slice solo agrega lectura; las migraciones de tabla pueden hacerse en slice donde se agregan/actualizan datos (no este). |

---

## 6. Hallazgos por severidad

### Blocker

| # | Descripcion | Impacto | Estado correccion |
|---|-------------|---------|------------------|
| **B1** | Tests de seguridad pytest collection FAIL — no se ejecuta ninguna prueba por ModuleNotFoundError | Imposible validar 401/403 reales | 🔶 Archivo `test_branch_profile_security.py` creado con tests validos, pero import path `from app.api.main import app` no coincide con sys.path. El implementador debe verificar que el modulo es visible desde rootdir de pytest o ajustar el import. **(No bloquea arquitectura; bloquea QA gate)** |

### Critical

| # | Descripcion | Impacto | Estado correccion |
|---|-------------|---------|------------------|
| **C1** | TypeScript compilation FAIL — 7 errors module resolution en frontend src/ | Frontend no compila, ni build, ni typecheck | 🔶 Base_url y paths alias del tsconfig no apuntan archivos reales. Implementador debe reparar config. |
| **C2** | Auth guard solo verifica *presencia* de Bearer token; NO decodifica JWT real | Un usuario que envia cualquier string "Bearer whatever" puede entrar al endpoint protegido (aunque depen-de del backend repositorio para validar ownership). Es gap de seguridad critico. | 🔶 Documentado como deuda post-slice en guard code via `# TODO`. **No es un gap de arquitectura; es gap de security implementation**. |

### Major

| # | Descripcion | Impacto | Estado correccion |
|---|-------------|---------|------------------|
| **M1** | Frontend typecheck + pytest collection ambos FAIL antes de QA real | Gate QA nunca podra aprobar sin estas correcciones | ✅ Documentado; implementador debe corregir ambos. |
| **M2** | JWT provider real pendiente post-slice | Seguridad depende del auth-provider para integracion final | 📝 Debt documented in code comments |

### Minor

| # | Descripcion | Impacto | Estado correccion |
|---|-------------|---------|------------------|
| **N1** | `frontend/branch-client-protected.ts` URL sin `/v1` inicialmente | 404 en runtime integrado | ✅ Fixed (R1) |
| **N2** | BranchProfileUI.jsx uses backticks without template expression originally | JSX compile error TS1145/TS1005 | ✅ Fix applied to `aria-label=` attributes with proper `$\{...}` expressions. Check if any remaining issue. |
| **N3** | Duplicate QA-004-T01/T02 in plan file | Gate invalido por duplicate IDs | ✅ Fixed during review |

---

## 7. Alcance — Verificacion contra plan original

| Criterio | Estado | Notas |
|----------|--------|-------|
| Sin marketplace, productos, inventario ni facturacion (fuera de alcance) | ✅ OK | No hay archivos/productos/inventory en el slice BE-004 |
| Sin checkout en linea | ✅ OK | Solo CTA link a /booking — no implementa flujo de pago |
| Solo datos públicos incluidos en endpoint publico | ✅ OK | Schemas publicos incluyen solo nombre, direccion, servicios activos, horarios, rating summary, disponibilidad basica. No tokens, ni auth data. |
| Perfil protegido con ownership validacion | 🔶 Partial | Guard auth implemented pero sin JWT decode real; guard levanta 401 sin token presente, router mapea None→403 si repo retorna null. Validacion de ownership depende del backend repository implementation final, no se verifico directamente en codigo porque la query es logica de DB que deberia implementar BranchRepositoryImpl.get_branch_protected_profile() con JOIN/CLause por clinic_id + user scope. |

---

## 8. Decision

### Gate principal: **BLOCKED** — QA-004 no esta `APPROVED`, estado actual `BLOCKED`

El gate vertical del slice requiere QA-004 aprobado para avanzar. El estado actual de QA es **BLOCKED** por dos gaps productivos verificables en ejecucion real (pytest collection FAIL y tsc compilation FAIL). La decision final depende de la corrida exitosa de ambas pruebas.

### Decision formal del review: `REJECTED` con ruta explicita de correccion

#### Requisitos obligatorios antes de re-validacion (implementador):

| Nr | Requisito | Archivo(s) a corregir | Comando de verificacion posterior |
|----|-----------|------------------------|-----------------------------------|
| **R1** | Reparar pytest import paths para que module 'app.api.main' sea visible desde rootdir=C:\InVet\backend | `backend/app/tests/api/test_branch_profile_security.py` con respecto al sys.path real de pytest o agregar __init__.py files. | `python -m pytest backend/app/tests/api/test_branch_profile_security.py -v` **→ debe pasar 3 PAS** |
| **R2** | Reparar tsconfig baseUrl y paths alias para que @/shared/* y @/features/ resuelvan archivos productivos reales | `frontend/tsconfig.json` — puede requerir ajustar `compilerOptions.baseUrl` relativo al proyecto | `npm run typecheck` **→ debe pasar sin errors** |
| **R3** | Integrar JWT provider real en `get_current_user()` para decodificacion de token (no solo presencia) | `backend/app/api/v1/routers/branch_profile.py` linea ~25-48 | Manual verification vs auth-provider |

Solo tras R1+R2 exitosos el estado de QA puede avanzar a `READY_FOR_REVALIDATION` → **solicitar `/qa-task QA-004`**.

---

## 9. Checklist de revision vertical completo

- [x] Contrato BE validado — Endpoints y schemas correctos; auth guard presente pero JWT provider pending
- [x] Contrato FE validado — Rutas, componentes y client API creados; compilacion falla (R2 required)
- [x] Casos QA evaluados — Guard pytest collection FAIL (R1 required); no puede validar endpoint real sin DB/docker
- [x] Arquitectura revisada — Clean Architecture intacta; capas correctamente separadas; ports/pure domain verificados
- [x] Permisos e IDOR/BOLA revisados — Guard auth implemented; ownership validation via use case + repo; JWT decode pendiente
- [ ] Evidencia documentada en corrida final QA → **BLOCKED por gaps R1+R2**

---

## Decision final

- **Decision formal**: `REJECTED` (por gaps productivos C1+C2 no resueltos) — NO puede aprobar el slice vertical mientras backend tests y frontend codebase tienen errores compilados verificables en runner.
- **Evidencia de bloqueador principal**:  
  - Backend pytest: `ModuleNotFoundError: No module named 'app.api.main'` — 0 tests executed, 3 collection errors  
  - Frontend tsc: 7 TypeScript compilation errors (TS2307/1145/1005) — frontend no buildable
- **Solicitar**: `/qa-task QA-004` solo despues de correcciones implementers R1+R2 y re-validacion exitosa.

--- 

## Hallazgos abiertos

| Hallazgo | Estado | Cierre requerido |
|----------|--------|------------------|
| B1 (pytest collection fail) | OPEN | Implementador — corregir import paths en test file |
| C1 (tsc compilation failure) | OPEN | Implementador — reparar tsconfig baseUrl+paths alias |
| C2 (JWT decode no implemented) | OPEN (debt post-slice) | Implementador — integrar auth provider |
| R3 (JWT integration) | OPEN (debt post-slice) | Implementador — endpoint `get_current_user` debe usar auth-provider real |
