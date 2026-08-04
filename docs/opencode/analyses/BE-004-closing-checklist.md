# BE-004 — Checklist de cierre de correcciones

**Slice**: BE-004 (perfil público de clínica/sucursal)  
**Vertical**: BE-004 / FE-004 / QA-004  
**Revisiones consultadas**: 
- `BE-004-review.md` (general — BLOCKED/REJECTED)
- `BE-004-clean-architecture-review.md` (APPROVED)
- `BE-004-security-review.md` (REJECTED — 3 findings no resueltos + QA findings pending)
- `QA-004-findings.md` (RESUELTO — inconsistencia con revision general)
- `BE-004-corrections.md` (correcciones previas aplicadas, solicitud revalidacion)
- `validate_slice_plan.py --stage findings` (FAIL 7 errores de estructura documental)

---

## Hallazgos que pueden cerrarse en esta revision (solo documentales/procesales)

| # | Hallazgo | Origen | Severidad | Estado cierre | Cierre aplicado |
|---|----------|---------|-----------|--------------|-----------------|
| **D1** | Plan tareas no actualizado — T02/T03 sin task file | BE-004-plan.md, analisis manual | Medio | ✅ CERRADO DOCUMENTALMENTE | Generado `BE-004-findings-analysis.md` que documenta estado real de implementacion (codigo presente, tests existentes) y explica el gap documental vs realidad. |
| **D2** | Tareas marcadas pending con evidencia "pending" pero codigo testeable existe | BE-004-T01.md, QA findings | Medio | ✅ CERRADO DOCUMENTALMENTE | Analisis documenta que los 3 archivos de test (use cases + API HTTP + security) tienen assertions reales y son verificables. Solo falta escribir evidencia en el task file. |
| **D3** | Inconsistencia entre documentos — "RESUELTO" vs "BLOCKED" | QA findings vs review general | Bajo-Medio | ✅ CERRADO DOCUMENTALMENTE | Se documenta que `QA-004-findings.md` declara RESUELTO tras revalidacion exitosa (9 passed); el bloque de revisiones previas era historicamente correcto pero fue superado por las correcciones. |
| **D4** | Validador documental FAIL por estructura faltante | validate_slice_plan.py stage=findings | Alto (proceso) | ❌ PENDIENTE — requiere actualizacion del plan | El plan necesita secciones: contrato implementacion frontend, checklist tecnico, contratos API por accion, formularios/validacion, y criterios de aceptacion en formato esperado. |

---

## Hallazgos que NO pueden cerrarse sin otra ejecucion (productivos)

| # | Hallazgo | Origen | Severidad | Estado | Bloqueo |
|---|----------|---------|-----------|--------|---------|
| **H1** | JWT auth guard verifica solo presencia, no decodifica token real | Review general C2; security H? (auth) | Critical (debt post-slice) | OPEN (debt) | Requiere integro con auth-provider en implementacion real |
| **H2** | Refresh token sin rotacion | Security review H1 | CRITICAL (debt) | OPEN (debt) | Cambios de auth-use-case + DB migration para invalidar old refresh token |
| **H3** | Sin configuracion CORS | Security review H2 | MAJOR (debt) | OPEN (debt) | Agregar CORSMiddleware a main.py y router |
| **H4** | Secret key por defecto hardcodeada ("secret-key-for-dev") | Security review H3 | MAJOR (debt) | OPEN (debt) | Fail-open guard en startup de app |
| **H5** | Endpoint public expone clinic_id como ID entero enumerables | Security review H4 | minor | OPEN (opcion — justificacion requerida) | Cambio a UUIDs o documentar decision explicita |
| **G1** | Frontend 100% sin pruebas unitarias ni integration tests | Este analisis | CRITICO | OPEN (nuevo gap) | Requiere setup de testing + minimo 2 tests cliente API + 1 test componente principal |

---

## Correcciones previas ya cerradas (no requieren accion en esta revision)

| # | Descripcion | Estado | Evidencia |
|---|-------------|--------|-----------|
| B1-prev | Endpoint protegido sin auth → agregado OAuth2Bearer guard | CERRADO | `security.py` get_current_access_user con HTTPException(401) |
| C1-prev | FE-004 frontend incompleto | CERRADO | 13 archivos creados (package.json, tsconfig, next.config, 2 páginas, branch-client, types, 3 UI components, BranchProfile) |
| C2-prev | Tests de seguridad sin cobertura real | CERRADO | `test_branch_profile_security.py` con 3 assertions HTTP reales |
| C3-prev | datetime no importado en schema protegido | CERRADO | Import agregado a branch_protected.py |
| M3-prev | Use case sin validacion ownership explicita | CERRADO | is_branch_accessible() + branch.clinic_id != clinic_id check |

---

## Archivados generados en esta revision

| Archivo | Descripcion |
|---------|-------------|
| `docs/opencode/analyses/BE-004-findings-analysis.md` | Analisis completo del estado real de tareas, evidencia y gaps por capa |
| `docs/opencode/gaps/BE-004-unit-gaps.md` | Gaps unitarios por archivo productivo — clasificados por severidad para priorizar pruebas faltantes |

---

## Checklist verificacion final

### Backend
- [x] Codigo implementado: router, use cases, schemas, entities, ports, orm models, repo adapters → 7 archivos verificados presentes
- [x] Arquitectonic check (Clean Architecture): APPROVED por revisor anterior
- [x] Tests existents: 3 suites con 9+ tests totales (use case mocks + API HTTP + security TestClient)
- [ ] Prueba explicita de entity models → GAP (DB1)
- [ ] Prueba explicita de repo adapter ORM → GAP (DB4)

### Frontend  
- [x] Rutas implementadas: 2 paginas Page + componente feature
- [x] Client API centralizado: branch-client.ts + branch-client-protected.ts con URLs `/api/v1/...`
- [x] Tipos TypeScript: coincidentes con Pydantic schemas backend
- [x] Estados UX: loading/error/empty/success/submitting cubiertos en UI code
- [x] CTA: `<a href="/booking?branch=...">` — no es `#` link dead
- [ ] Tests unitarios frontend → GAP CRITICO (FB1-FB8)

### QA  
- [x] QA findings revisados → estado RESUELTO
- [x] Inconsistencia documental documentada
- [ ] Validacion documental del plan → FAIL por estructura plan.md
- [ ] `/qa-task QA-004` como siguiente paso de cierre (solicitado en BE-004-corrections.md)

---

## Riesgos residuales

| # | Descripcion | Prioridad | Mitigacion recomendada |
|---|-------------|-----------|---------------------|
| **R1** | JWT guard acepta任意 Bearer token sin verificar signature/expiry | Alta (debt post-slice) | Bloquear merge si auth-provider no se integra en slice siguiente |
| **R2** | 100% del frontend sin tests — regresiiones invisibles | Alta | Implementar minimo 2 tests de cliente API + 1 test rendering de BranchProfile |
| **R3** | Plans.tasks pendientes marcan implementacion como "pending" → confusion con equipo/bot automation | Media | Actualizar BE-004-T01.md, crear BE-004-T02.md y T03.md con evidencia real |
| **R4** | Plan markdown FAIL en validator — bloquea automated gating | Media | Agregar secciones faltantes al plan O deshabilitar checks documentales estrictos para plans legacy |
| **R5** | Inconsistencia entre QA findings (RESUELTO) y review general (BLOCKED) | Baja | Sincronizar estado en BE-004-corrections.md o actualizar todas las MDs al estado actual |

---

## Cierre de esta revision del agente implementador

- [x] Se revisaron los hallazgos de revisiones previas (general, clean arch, security)
- [x] Se revisaron los hallazgos de QA findings  
- [x] Se consolido el estado real codigo vs documentos
- [x] Se genero analisis de tareas pendientes clasificado por capa
- [x] Se genero archivo de gaps unitarios explicitos (`docs/opencode/gaps/BE-004-unit-gaps.md`)
- [x] Lista de hallazgos cerrados documentalmente (D1-D3) y pendientes de cierre por otra ejecucion (H1-H5, G1)

### No se modifico:
- Codigo productivo (backend o frontend) — los gaps identificados requieren implementacion real de tests o integro de servicios de auth/CORS, lo cual excede el alcance de analisis/documentacion de hallazgos.
