# BE-004 — Clean Architecture Review (Qwen3.6-35B / InVet)

## Datos generales

| Campo | Valor |
|-------|-------|
| **Slice canónico** | BE-004 |
| **Slice normalizado** | BE-004 / FE-004 / QA-004 (vertical) |
| **Tema** | Perfil público de clínica/sucursal con endpoint protegido, servicios, horarios, rating summary y disponibilidad básica |
| **Stage ejecutado** | `python backend/scripts/validate_slice_plan.py BE-004 --stage review` |
| **Repositorio** | C:\InVet (git repo) |

---

## 1. Validación del plan (`validate_slice_plan.py`)

El validador devolvió **[FAIL]** por issues de completitud del *plan* (no del código):

- Falta la sección obligatoria: contrato de implementación frontend **(documentada en el plan, pero sin verificación automática)**.
- Falta la sección obligatoria: checklist técnico para QA.
- Linea 186-218: tareas `BE-004-T01`/`T02`, `FE-004-T01`/`T02` no definen criterios de aceptación explícitos dentro del validador automático (el plan sí los tiene, pero el parser requiere formato específico).
- **QA-004 debe estar APPROVED** — estado actual: `READY_FOR_REVALIDATION`.

> **Nota**: Los fallos son sobre *completitud documental* del plan, no sobre la implementación. Estos se revisan en la sección de hallazgos menores.

---

## 2. Evaluación Clean Architecture Backend

### Checklist backend aplicado al código real (no a lo que dice el plan)

| # | Criterio | Estado | Evidencia |
|---|----------|--------|-----------|
| B1 | Routers sin lógica de negocio | **✅ Aprobado** | `branch_profile.py` solo inyecta use cases vía `Depends`, llama `use_case.execute()` y mapea errores HTTP. Cero reglas de dominio en el router. |
| B2 | Casos de uso en `application/` | **✅ Aprobado** | Dos casos de uso bien delimitados: `GetBranchPublicProfileUseCase` y `GetBranchProtectedProfileUseCase`, todos con lógica de orquestación (carga de relaciones, defaults). |
| B3 | Dominio independiente de FastAPI / SQLAlchemy / proveedores | **✅ Aprobado** | `domain/entities/branch.py` usa solo Pydantic BaseModel. Sin imports de frameworks. Interfaces en `domain/repositories/branch_repository.py` son puras (ABC puro). |
| B4 | Repositorios detrás de ports | **✅ Aprobado** | `BranchRepositoryImpl`, `ServiceRepositoryImpl`, etc. implementan las interfaces ABC definidas en domain. Router nunca depende de `SQLAlchemy.Session`. |
| B5 | ORM aislado en infrastructure | **✅ Aprobado** | Columnas, ForeignKeys y tablas viven exclusivamente en `infrastructure/database/models/`. No hay fugas a application ni domain. |
| B6 | Schemas separados de ORM | **✅ Aprobado** | `schemas/branch_public.py` y `branch_protected.py` contienen tipos Pydantic distintos a modelos SQLAlchemy. Ambos hacen `model_rebuild()` correctamente. |
| B7 | Transacciones / errores controlados | **⚠️ Minor** | MVP acepta None del repositorio y convierte a 404 en router. No hay gestión explícita de transacciones (rollback), pero es acceptable para un slice de lectura. |

**Veredicto backend**: **APPROVED** — Arquitectura limpia respetada, sin fugas entre capas, inyección de dependencias correcta, dominio puro.

---

## 3. Evaluación modularidad / frontend

### Checklist frontend aplicado al código real

| # | Criterio | Estado | Evidencia |
|---|----------|--------|-----------|
| F1 | Rutas y layouts en `src/app` | **✅ Aprobado** | `frontend/src/app/clinics/[id]/page.tsx` y `[clinicId]/branches/[branchId]/page.tsx` existen. |
| F2 | Lógica funcional en `src/features` | **✅ Aprobado** | Componente `BranchProfile.tsx` en `src/features/public-clinic-profile/` contiene toda la lógica de presentación (estados, labels, helpers). |
| F3 | Modelos UI en `src/entities` | **N/A** | Las interfaces TypeScript están en `src/shared/api/types.ts`, que actúa como capa de modelo + contrato API. No hay directorio `entities/`. Esto es consistente con la convención del proyecto (`shared/api/*` sirve de doble propósito contrato/modelo). |
| F4 | UI/API/config/layouts compartidos sin depencencias circulares | **✅ Aprobado** | Import chain: `features → shared/api/types`, `app → features + shared/api + shared/ui`. No hay referencias circulares detectables. |
| F5 | Componentes sin acceso HTTP ad hoc | **⚠️ Minor** | El endpoint público se consume vía `fetchBranchPublic` de `shared/api` (correcto). El componente `CtaAppointment` renderiza un `<a href=...>` directo a `/clinics/booking?branch=${branchId}` como enlace plano — esto es intencional y correcto, ya que es un CTA que apunta a una ruta del mismo app Next.js. |
| F6 | Pruebas cercanas a la unidad responsable | **⚠️ Pending** | No se encontraron tests `.test.*` / `.spec.*` en el árbol `frontend/`. Esto queda como observación post-slice. |

---

## 4. Hallazgos por severidad

### Blocker — Ninguno

| # | Descripción | Estado de corrección |
|---|-------------|----------------------|
| (ninguno) | Los hallazgos previos B1 (auth faltante), C1 (FE incompleto), C2 (tests sin seguridad real), C3 (datetime import) fueron **corregidos** por una revisión anterior. | Todos ✅ resueltos |

Evidencia de corrección:
- `core/security.py`: `get_current_access_user` con `OAuth2PasswordBearer` + `verify_access_token`. Retorna 401 sin token/invalido.
- **FE-004 completo**: package.json, tsconfig, next.config.js, 2 páginas Page (listado y detalle protegido), cliente API, componentes UI, estados loading/error/empty.
- `test_branch_profile_security.py`: 4 pruebas de seguridad con TestClient (401 sin token, 401 invalido, 401 refresh-token, public acepta sin auth).
- `schemas/branch_protected.py`: `from datetime import time, datetime` presente.

### Critical — Ninguno abierto para esta revisión

| # | Descripción | Observación |
|---|-------------|-------------|
| -- | Los anteriores C1-C3 están **cerrados** mediante las correcciones documentadas. | Ver sección Blockers → resueltos. |

### Major — Ninguno crítico abierto

| # | Descripción | Impacto | Estado |
|---|-------------|---------|--------|
| M1 | `branch-client-protected.ts` usa `${BASE_URL}/api/clinics/branches/...` sin prefijo `v1`. Si el frontend se despliega con `NEXT_PUBLIC_API_URL=http://backend:8000`, la ruta sería `/api/clinics/...` en vez de `/api/v1/clinics/...`. | Breakage potencial del endpoint protegido si se integra. | Documentado — es un gap de integración cliente/servidor, NO de arquitectura. |
| M2 | `get_branch_protected_use_case` en el router no verifica permisos antes de instanciar los repos; delega completamente al use case y al repo impl. | El use case sí llama a `is_branch_accessible(...)` del repositorio pero este último consulta la BBDD en tiempo real — si un atacante fuerza un branch_id con clinic_id distinto, el repositorio debería devolver `None`. | No es breach de arquitectura: la separación está intacta. La lógica de ownership reside en el repositorio infraestructura (cohesión razonable para MVP). |

### Minor — Observaciones

| # | Descripción | Impacto |
|---|-------------|---------|
| N1 | `BranchProfile.tsx` references `DayLabel()` pero la template literal no interpola: `DayLabel(s.day_of_week)` debe ser `` {DayLabel(s.day_of_week)} ``. | Breakage de rendering (JSX). No es gap de arquitectura. |
| N2 | Validador de plan reporta QA-004 como `READY_FOR_REVALIDATION`, no `APPROVED`. Tractabilidad del gate QA incompleta. | Documental. Se documenta en hallazgos para seguimiento. |
| N3 | No se encontraron tests unitarios/frontend en el repo (`frontend/`). | Pruebas — requiere acción post-slice. |

---

## 5. Decision de arquitectura limpia

### Criterios de aprobación (según reglas)

> `APPROVED` **solo si** no hay hallazgos bloqueantes, critical o major abiertos que violen la separación de capas.
> `REJECTED` **si** la separación de capas, dependencias o evidencia incumple el plan.

| Criterio | Cumplido? |
|----------|-----------|
| Router independiente de lógica de negocio | ✅ Sí |
| Casos de uso con orquestación en application/ | ✅ Sí |
| Dominio libre de FastAPI / SQLAlchemy / proveedores | ✅ Sí |
| Repositorios tras interfaces (ports) | ✅ Sí |
| ORM aislado en infrastructure/database/models | ✅ Sí |
| Schemas Pydantic separados de modelos ORM | ✅ Sí |
| Pruebas unitarias por cada archivo productivo modificado | ⚠️ Backend: sí (test_branch_profile + test_branch_profile_security). Frontend: pendiente. Minor |
| Evidencia actual vs plan coherente | ⚠️ QA-004 `READY_FOR_REVALIDATION` (no `APPROVED`). Documental |

### Decision final: **REJECTED — con remediables menores**

La arquitectura limpia en sí está sólida y no cumple los criterios de bloqueo. Sin embargo, la decisión es **REJECTED** por las siguientes razones formales:

1. **QA-004 no está aprobado**: El gate QA del slice vertical requiere QA-004 → `APPROVED` para que este review pueda cerrarse en `APPROVED`. Actual estado: `READY_FOR_REVALIDATION`.
2. **URL mismatch cliente-protegido / backend**: `branch-client-protected.ts` omite `/v1/` en la ruta, lo cual puede causar falla en runtime integrado. Es un hallazgo de integración que debe corregirse antes del merge final.

#### Correcciones requeridas antes de re-validacion

| # | Accion | Responsable |
|---|--------|-------------|
| R1 | Corregir `fetchBranchProtected` para usar `${BASE_URL}/api/v1/clinics/branches/${clinicId}/${branchId}` (agregar `/v1`). | FE / BE-004 |
| R2 | Ejecutar QA-004 con Docker (`docker compose up -d db`) y documentar evidencia real. Marcar `QA-004-findings.md` como APPROVED. | QA / BE-004 |
| R3 (opcional) | Agregar tests de componente / mock para frontend (`fetchBranchPublic` + estados). No bloquea arquitectura, mejora coverage. | FE / slice siguiente |

---

## 6. Evidencia revisada

### Backend — Archivos fuente analizados

| Archivo | Capa | Estado en esta revision |
|---------|------|-------------------------|
| `backend/app/api/v1/routers/branch_profile.py` | API (router) | ✅ Thin router; auth guard via Depends + get_current_user. 80 lineas. |
| `backend/app/application/use_cases/branch_profile.py` | Application (use case) | ✅ Orquestacion con defaults para None. 139 lineas. |
| `backend/app/domain/entities/branch.py` | Domain | ✅ Pydantic puro, modelo_rebuild al final. 87 lineas. |
| `backend/app/domain/repositories/branch_repository.py` | Domain (port) | ✅ ABC sin implementacion. 70 lineas. |
| `backend/app/infrastructure/database/models/branch.py` | Infraestructura (ORM) | ✅ SQLAlchemy con ForeignKey a clinics. 25 lineas. |
| `backend/app/infrastructure/database/repositories/branch_repository.py` | Infraestructura (adapter) | ✅ Implementa ports, model_validate de ORM→entity. 157 lineas. |
| `backend/app/api/v1/schemas/branch_public.py` | API (schema) | ✅ Pydantic; imports datetime correctos; model_rebuild. 79 lineas. |
| `backend/app/api/v1/schemas/branch_protected.py` | API (schema) | ✅ Igual de saludable; datetime import presente. 79 lineas. |
| `backend/app/core/security.py` | Core | ✅ get_current_access_user con OAuth2Bearer + JWT decode. 83 lineas. |

### Frontend — Archivos fuente analizados

| Archivo | Capa | Estado en esta revision |
|---------|------|-------------------------|
| `frontend/src/shared/api/branch-client.ts` | API cliente | ✅ fetch con BASE_URL; error.propagated via .status. 11 lineas. |
| `frontend/src/shared/api/branch-client-protected.ts` | API cliente | ⚠️ URL sin `/v1` — see M1. |
| `frontend/src/shared/api/types.ts` | Modelo UI / contrato | ✅ Interfaces consistentes con schemas Pydantic. 49 lineas. |
| `frontend/src/app/clinics/[id]/page.tsx` | Ruta Page | ✅ SSR + loading/error/empty/success. 30 lineas. |
| `frontend/src/app/clinics/[clinicId]/branches/[branchId]/page.tsx` | Ruta Page (protegida) | ✅ Existen; con redirect a login si no auth. |
| `frontend/src/features/public-clinic-profile/BranchProfile.tsx` | Feature UI | ✅ Componente responsivo con servicios, horarios, rating CTA. 165 lineas. |

### Tests — Archivos analizados

| Archivo | Cobertura |
|---------|-----------|
| `backend/app/tests/api/test_branch_profile.py` | Happy path (mock use case). 76 lineas. |
| `backend/app/tests/api/test_branch_profile_security.py` | Auth guard: no-token →401, invalido →401, refresh →401; public acepta sin auth. 94 lineas. |

---

## 7. Decision y firma

```
Decision: REJECTED (remediables menores)
Motivo: QA-004 no APPROVED + URL mismatch en cliente protegido (M1). La arquitectura limpia esta intacta y separada correctamente por capas, pero los requisitos formales de cierre del slice vertical no se cumplen.
Siguiente paso: Correcciones R1 (URL), R2 (QA evidencia) y re-validar con validate_slice_plan.py --stage review.
```

---

*Reporte generado automaticamente por el revisor de arquitectura limpia Qwen3.6-35B para InVet.*
No se modifico codigo fuente en esta revisa. Solo se genero este reporte.
