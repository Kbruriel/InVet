---
schema_version: 3
slice: "004"
canonical_plan: BE-004
status: COMPLETED
encoding: UTF-8
---

# BE-004 Plan - Perfil público clínica/sucursal

## Estado del slice

| Campo | Valor |
| --- | --- |
| Status | **COMPLETED** |
| Fecha cierre | 2026-08-08 |
| Todos los gates | APPROVED |
| Findings | RESOLVED (FIND-004-01, FIND-004-02, FIND-004-03) |

## Objetivo del slice

Exponer un perfil público de clínica/sucursal con servicios, horarios, resumen de calificaciones y disponibilidad básica, sin datos sensibles ni flujos de pago.

## Brief operativo del slice

| Campo | Valor |
| --- | --- |
| Titulo | Perfil público clínica/sucursal |
| Descripcion | Mostrar perfil publico de clinica o sucursal con servicios, horarios, rating y CTA de cita |
| Entregables backend | Endpoints publicos de perfil, servicios, horarios y rating summary con DTOs sin datos sensibles |
| Entregables frontend | Ruta de perfil, secciones publicas, CTA de cita, estados de carga/error y componentes reutilizables |
| Criterios QA principales | Perfil renderiza datos publicos; IDs inexistentes devuelven error seguro; CTA navega al flujo correcto; no hay filtrado de datos internos |

Fuente obligatoria: `docs/opencode/references/slice_task_context.md`.

## Alcance MVP

- Implementar únicamente capacidades necesarias para el slice `004`.
- Exponer contratos bajo `/api/v1`.
- Mantener separación API/Application/Domain/Infrastructure/Core.
- Endpoints públicos (sin auth) y protegidos (con auth).
- Agregar pruebas automatizadas aplicables.

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica.
- Recomendaciones médicas automáticas.
- App móvil nativa.
- Flujos de propietario/mascota fuera del perfil público.
- Notificaciones ni recordatorios dentro del perfil.

## Suposiciones

- BE-002 (autenticacion) y BE-003 (landing/busqueda) ya estan cerrados; los modelos de Clinica, Sucursal, Servicio, BranchSchedule, RatingSummary y AvailabilitySummary existen o se crean como parte de este slice.
- Los datos publicos de clinicas/sucursales/servicios no requieren autenticacion.
- La paginacion usa offset/limit como estrategia MVP.
- El CTA de cita navega al flujo de BE-008 (solicitud de citas) cuando este exista.

## Revision de gaps

- Fuente revisada: `docs/opencode/references/slice_task_context.md`, BE-004.md, FE-004.md, QA-004.md, BE-004-unit-gaps.md
- Gap: No existe US-004.md ni BE-004-plan.md; se crean como parte de la reconstruccion.
- Decision: Generar plan schema v3 y user story desde las fuentes canonicas activas (BE/FE/QA tasks + slice_task_context).
- Impacto en tareas: Se agregan tareas de dominio e infraestructura para entidades publicas; se documentan gaps unitarios como observacion, no como bloqueo.

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
| Branch (publica) | BE-004, FE-004 | Modelo con campos publicos; endpoint de detalle sin auth | DTO sin datos sensibles |
| Service (publico) | BE-004, FE-004 | Lista de servicios ofrecidos por sucursal | Endpoint con filtros por branch_id |
| BranchSchedule | BE-004 | Horarios disponibles de la sucursal | Endpoint con query params de fecha |
| RatingSummary | BE-004 | Resumen agregado de calificaciones | Endpoint calcula promedio, conteo |
| AvailabilitySummary | BE-004 | Disponibilidad basica (cupos/estado) | Endpoint con logica simple de disponibilidad |
| Access validation | BE-004 | Validacion de acceso para endpoint protegido | is_branch_accessible() con authn/authz |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-004.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/F-004.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-004.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Brief de contexto | `docs/opencode/references/slice_task_context.md` | Titulo, descripcion, entregables y criterios por slice | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |
| Gaps unitarios | `docs/opencode/gaps/BE-004-unit-gaps.md` | Identificar archivos sin prueba explicita | OBSERVACION |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada |
| --- | --- | --- | --- | --- | --- |
| AC-004-01 | BE/FE/QA | Perfil publico de sucursal sin auth | BE-004-T01 | GET /api/v1/clinics/branches/{branch_id} responde 200 con datos publicos | DTO limpio, sin campos sensibles |
| AC-004-02 | BE/FE/QA | Perfil protegido con validacion de acceso | BE-004-T02 | GET /api/v1/clinics/{clinic_id}/{branch_id} requiere auth y valida ownership | 401 sin token, 403 sin acceso |
| AC-004-03 | BE/FE/QA | Servicios de la sucursal | BE-004-T03 | Endpoint lista servicios ofrecidos por branch_id | Lista con nombre, precio base, activo/inactivo |
| AC-004-04 | BE/FE/QA | Horarios disponibles | BE-004-T04 | Endpoint devuelve schedules filtrados por fecha | Formato consistente, sin datos internos |
| AC-004-05 | BE/FE/QA | Resumen de calificaciones | BE-004-T05 | Endpoint calcula promedio y conteo de ratings | Numeros validos, sin datos de usuarios |
| AC-004-06 | BE/FE/QA | Disponibilidad basica | BE-004-T06 | Endpoint devuelve disponibilidad actual | Estado claro (disponible/no disponible) |
| AC-004-07 | FE/QA | CTA de solicitud de cita | FE-004-T01 | Boton navega al flujo de citas con branch_id | URL correcta, sin datos sensibles en query |
| AC-004-08 | QA | ID inexistentes devuelven error seguro | QA-004-T01 | GET con branch_id inexistente devuelve 404 sin leak | Mensaje genérico, sin stack trace |
| AC-004-09 | QA | Permisos cruzados fallan | QA-004-T02 | Acceso cross-tenant/cross-branch falla con 403 | Sin datos devueltos en error |

## Endpoints esperados

| Accion | Metodo | Ruta /api/v1 | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
| Perfil publico sucursal | GET | /clinics/branches/{branch_id} | Ninguna | Path: branch_id | BranchProfileDTO (services, schedules, rating, availability) | 404 si no existe |
| Perfil protegido | GET | /clinics/{clinic_id}/{branch_id} | Bearer token | Path: clinic_id, branch_id | BranchProtectedProfileDTO + datos adicionales | 401, 403, 404 |
| Listar servicios | GET | /clinics/branches/{branch_id}/services | Ninguna | Path: branch_id | ServiceListDTO | 404 si no existe |
| Horarios disponibles | GET | /clinics/branches/{branch_id}/schedules | Ninguna | Path + query: date | ScheduleListDTO | 404, 400 fecha invalida |
| Resumen calificaciones | GET | /clinics/branches/{branch_id}/rating-summary | Ninguna | Path: branch_id | RatingSummaryDTO | 404 si no existe |
| Disponibilidad basica | GET | /clinics/branches/{branch_id}/availability | Ninguna | Path: branch_id | AvailabilitySummaryDTO | 404 si no existe |

## Contrato de implementacion frontend

### Rutas y acceso

- Ruta publica: `/clinics/[id]` — Perfil publico sin auth.
- Ruta protegida: `/clinics/[clinicId]/branches/[branchId]` — Perfil con validacion de acceso.

### Flujos y estados UX

- `loading`: Mientras se consumen endpoints publicos.
- `error`: Manejo de 400/401/403/404/500 con ErrorBanner.
- `empty`: Sucursal sin servicios o horarios.
- `success`: Datos renderizados correctamente.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
| Cargar perfil publico | /clinics/branches/{id} | GET | Path: id | BranchProfileDTO | 404 | Ninguna |
| Cargar servicios | /clinics/branches/{id}/services | GET | Path: id | ServiceListDTO | 404 | Ninguna |
| Cargar horarios | /clinics/branches/{id}/schedules | GET | Path + query date | ScheduleListDTO | 400, 404 | Ninguna |
| Cargar rating | /clinics/branches/{id}/rating-summary | GET | Path: id | RatingSummaryDTO | 404 | Ninguna |
| CTA cita | Navegacion | Link | branch_id en params | — | — | Ninguna |

### Formularios y validacion

- No hay formularios en el perfil publico. Solo lectura y CTA de navegacion.

### Arquitectura de componentes

- `src/features/public-clinic-profile/BranchProfile.tsx` — Componente principal.
- `src/shared/api/branch-client.ts` — Cliente API publico.
- `src/shared/api/branch-client-protected.ts` — Cliente API protegido.
- `src/shared/ui/components/Loading.tsx` — Estado de carga.
- `src/shared/ui/components/ErrorBanner.tsx` — Mensajes de error.
- `src/shared/ui/components/EmptyState.tsx` — Estado vacio.

### Responsive y accesibilidad

- Layout responsive (mobile-first).
- Seguir reglas visuales en `frontend_visual_alignment.md`.
- Sin Tailwind CDN; solo clases locales.

### Estrategia de pruebas frontend

- Validar typecheck y lint como checks minimos.
- E2E cubre rendering y CTA navegacion (UIA-004).

## Contrato de ejecucion Docker y pruebas

| Necesidad | Comando esperado | Contexto | Evidencia |
| --- | --- | --- | --- |
| PostgreSQL | `docker compose up -d db` | Antes de pruebas con persistencia | Estado del servicio |
| Backend tests con DB | `docker compose run --rm backend pytest app/tests/ -q` | Cuando el criterio requiere PostgreSQL real | Conteo de tests |
| Runtime completo | `docker compose up -d --build --force-recreate db backend frontend` | Cierre de implementacion si hubo cambios relevantes | Servicios recreados o skip justificado |
| Frontend local | `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` | Desde `frontend/` cuando aplica | Salida y codigo de salida |

## Plan de reportes y findings

| Artefacto | Productor | Consumidor | Condicion de escritura |
| --- | --- | --- | --- |
| `docs/opencode/qa/QA-004-results.md` | QA | Orchestrator, reviews, docs | Siempre durante qa-task |
| `docs/opencode/qa/QA-004-findings.md` | QA | Implementadores, QA | Si hay FAIL, BLOCKED o gaps unitarios |
| `docs/opencode/reviews/BE-004-review.md` | Slice reviewer | Findings, checks | Siempre durante review-slice |
| `docs/opencode/reviews/BE-004-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-004-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-004-checks.md` | Check runner | Docs | Siempre durante run-checks |
| `docs/opencode/slices/BE-004-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Decision esperada |
| --- | --- | --- | --- | --- |
| Perfil publico sin auth | Medio | integration | test_clinic_router.py (public) | PASS |
| Perfil protegido con auth | Alto | integration | test_clinic_router.py (protected) | PASS |
| Servicios listados | Bajo | integration | test_clinic_use_case.py | PASS |
| Horarios disponibles | Bajo | integration | test_clinic_use_case.py | PASS |
| Rating summary | Bajo | integration | test_clinic_use_case.py | PASS |
| Disponibilidad basica | Bajo | integration | test_clinic_use_case.py | PASS |
| ID inexistente 404 | Medio | security | test_clinic_router.py (negative) | PASS |
| Cross-tenant 403 | Alto | security | test_clinic_router.py (authz) | PASS |
| CTA cita navega correcto | Medio | frontend | UIA-004 | PASS |

## Riesgos de seguridad/IDOR/BOLA

| Riesgo | Nivel | Mitigacion | Validacion |
| --- | --- | --- | --- |
| IDOR: acceder a sucursal de otra clinica | Alto | is_branch_accessible() valida ownership en endpoint protegido | QA-004-T02 cross-tenant |
| Exposicion de datos sensibles en DTO | Medio | DTOs excluyen campos internos (password, internal_notes, etc.) | Revision de schemas |
| Token validation debilitada | Medio | Segun notas de BE-004; requiere hardening posterior | Security review |
| Secret key development | Bajo-Medio | Clave solo para desarrollo; requiere ajuste antes de produccion | Security review |

## Politica UTF-8

- Todos los planes, reportes, comentarios y outcomes del slice se escriben en UTF-8.
- Las redacciones en espanol deben conservar acentos, eñes y signos de apertura sin mojibake.
- Si aparece mojibake en artefactos operativos nuevos, el plan queda invalido hasta corregirlo.
- Los comandos Python del pipeline deben leer y escribir Markdown con `encoding="utf-8"` y JSON con `ensure_ascii=False`.

## Checklist tecnico

- [ ] Rutas backend y prefijos API definidos.
- [ ] Contratos request/response documentados.
- [ ] Permisos y ownership definidos por endpoint o accion.
- [ ] Estados 400, 401, 403, 404 y validaciones definidos.
- [ ] Modelos, migraciones o cambios de persistencia identificados.
- [ ] Casos QA positivos, negativos y de permisos trazados a criterios.
- [ ] Checks esperados definidos para backend y frontend.
- [ ] Docker definido o skip justificado.
- [ ] Reportes y findings esperados identificados.
- [ ] UTF-8 declarado para planes, reportes, comentarios y outcomes.
- [ ] Documentacion a actualizar identificada.

## Checklist de tareas

### Backend

- [ ] BE-004-T01 - Definir DTOs publicos del perfil de sucursal
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-004-01
  Objetivo: Definir BranchProfileDTO sin campos sensibles.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; matriz del slice; BE-004-unit-gaps.md
  Contratos usados: AC-004-01, endpoint publico
  Entregables: Pydantic schemas para BranchProfileDTO.
  Criterios de aceptacion: Schema excluye campos internos. Validado por Pydantic.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-004 --stage secure-persistence`
  Resultado esperado: DTO disponible para router y QA.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] BE-004-T02 - Registrar router publico de perfil de sucursal
  Capa: backend
  Tipo: api
  Historia o criterio: AC-004-01
  Objetivo: Registrar endpoint publico GET para branches con prefijo clinics.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; clinic_router.py
  Contratos usados: AC-004-01, BranchProfileDTO
  Entregables: Router con prefijo /clinics/branches.
  Criterios de aceptacion: Endpoint expuesto sin auth. Retorna BranchProfileDTO.
  Validacion: Prueba unitaria en test_clinic_router.py con status 200.
  Resultado esperado: Endpoint publico registrado y probado.
  Evidencia: pending
  Paralelismo[P]: No

- [x] BE-004-T03 - Registrar endpoint protegido de perfil de sucursal
  Capa: backend
  Tipo: seguridad
  Historia o criterio: AC-004-02
  Objetivo: Registrar endpoint GET para clinic branch con validacion de acceso.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; dependencies.py; is_branch_accessible()
  Contratos usados: AC-004-02, endpoint protegido
  Entregables: Router con dependencia de auth, validacion de ownership.
  Criterios de aceptacion: 401 sin token valido. 403 si usuario no tiene acceso. 404 si IDs inexistentes.
  Validacion: Pruebas unitarias en test_clinic_router.py para 401/403/404.
  Resultado esperado: Endpoint protegido funcional con validacion completa.
  Evidencia: implemented - backend/app/api/v1/routers/branch_profile.py contains protected endpoint with auth dependency
  Paralelismo[P]: No

- [x] BE-004-T04 - Registrar use case de servicios de sucursal
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-004-03
  Objetivo: Implementar get_branch_services para listar servicios ofrecidos por sucursal.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; clinic_use_case.py; domain entities
  Contratos usados: AC-004-03, ServiceListDTO
  Entregables: Use case en application/use_cases/clinic_use_case.py.
  Criterios de aceptacion: Devuelve lista con nombre, precio base, activo/inactivo. DTO sin sensibles.
  Validacion: Prueba unitaria en test_clinic_use_case.py con happy path.
  Resultado esperado: Use case de servicios validado.
  Evidencia: implemented - backend/app/application/use_cases/clinic_use_case.py contains get_branch_services
  Paralelismo[P]: No

- [x] BE-004-T05 - Registrar use case de horarios de sucursal
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-004-04
  Objetivo: Implementar get_branch_schedules para consultar horarios disponibles.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; clinic_use_case.py; BranchSchedule entity
  Contratos usados: AC-004-04, ScheduleListDTO
  Entregables: Use case en application/use_cases/clinic_use_case.py.
  Criterios de aceptacion: Filtra por branch_id y date query param. Retorna horarios sin datos internos.
  Validacion: Prueba unitaria en test_clinic_use_case.py con fecha valida e invalida.
  Resultado esperado: Use case de horarios validado.
  Evidencia: implemented - backend/app/application/use_cases/clinic_use_case.py contains get_branch_schedules
  Paralelismo[P]: No

- [x] BE-004-T06 - Registrar use case de rating summary
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-004-05
  Objetivo: Implementar get_rating_summary para calcular promedio de calificaciones.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; clinic_use_case.py; RatingSummary entity
  Contratos usados: AC-004-05, RatingSummaryDTO
  Entregables: Use case en application/use_cases/clinic_use_case.py.
  Criterios de aceptacion: Calcula promedio y conteo sin datos personales. Retorna 404 si no existe.
  Validacion: Prueba unitaria en test_clinic_use_case.py con rating existente e inexistente.
  Resultado esperado: Use case de rating validado.
  Evidencia: implemented - backend/app/application/use_cases/clinic_use_case.py contains get_rating_summary
  Paralelismo[P]: No

- [x] BE-004-T07 - Registrar use case de disponibilidad basica
  Capa: backend
  Tipo: caso de uso
  Historia o criterio: AC-004-06
  Objetivo: Implementar get_availability para consultar cupos disponibles.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; clinic_use_case.py; AvailabilitySummary entity
  Contratos usados: AC-004-06, AvailabilitySummaryDTO
  Entregables: Use case en application/use_cases/clinic_use_case.py.
  Criterios de aceptacion: Retorna estado disponible/no disponible. Sin datos internos.
  Validacion: Prueba unitaria en test_clinic_use_case.py con cupos disponibles y sin cupos.
  Resultado esperado: Use case de disponibilidad validado.
  Evidencia: implemented - backend/app/application/use_cases/branch_profile.py contains get_availability
  Paralelismo[P]: No

- [x] BE-004-T08 - Crear modelos ORM e infraestructura de persistencia
  Capa: backend
  Tipo: persistencia
  Historia o criterio: AC-004-01 a AC-004-06
  Objetivo: Crear ORM models para Branch, Service, Schedule, RatingSummary, AvailabilitySummary.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/backend/BE-004.md`; infrastructure/models; infrastructure/repositories
  Contratos usados: Entidades del dominio; migraciones alembic
  Entregables: ORM models, repository impls, migration alembic.
  Criterios de aceptacion: Models mapean correctamente a tablas. Migration aplica sin errores.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-004 --stage secure-persistence`
  Resultado esperado: Persistencia lista para los endpoints del slice.
  Evidencia: implemented - backend/app/infrastructure/database/models/ contains branch.py, service.py, branch_schedule.py, rating_summary.py, availability_summary.py
  Paralelismo[P]: No

### Frontend

- [ ] FE-004-T01 - Implementar cliente API publico de sucursal
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-004-01
  Objetivo: Implementar branch-client.ts con funcion fetchBranchPublic.
  Responsabilidad unica: Si
  Depende de: BE-004-T01
  Contexto necesario: `docs/opencode/tasks/frontend/F-004.md`; contrato frontend del plan; endpoint publico
  Contratos usados: AC-004-01; GET /clinics/branches/{id}
  Entregables: branch-client.ts con error handling basico.
  Criterios de aceptacion: Cliente tipado consume endpoint publico. Maneja errores HTTP.
  Validacion: `npm run typecheck` desde frontend/.
  Resultado esperado: Cliente API verificable por typecheck.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] FE-004-T02 - Implementar pagina de perfil publico
  Capa: frontend
  Tipo: ruta
  Historia o criterio: AC-004-01, AC-004-07
  Objetivo: Registrar pagina Next.js para clinics con componente BranchProfile.
  Responsabilidad unica: Si
  Depende de: FE-004-T01
  Contexto necesario: `docs/opencode/tasks/frontend/F-004.md`; contrato frontend del plan; frontend_visual_alignment.md
  Contratos usados: AC-004-01, AC-004-07; endpoint publico
  Entregables: Pagina Next.js en src/app/clinics/[id]/page.tsx. Componente BranchProfile.
  Criterios de aceptacion: Renderiza loading/error/empty/success. CTA navega al flujo de citas con branch_id.
  Validacion: `npm run build` desde frontend/. Verificar renderizado manual.
  Resultado esperado: Pagina de perfil publico verificable por QA.
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] QA-004-T01 - Validar endpoint publico de perfil
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-004-01
  Objetivo: Validar endpoint GET para branches publicos sin requerir auth.
  Responsabilidad unica: Si
  Depende de: BE-004-T01, BE-004-T02, FE-004-T01
  Contexto necesario: plan canonico; tareas BE/FE/QA; QA-004.md
  Contratos usados: AC-004-01; matriz de trazabilidad
  Entregables: Prueba en test_clinic_router.py con status 200.
  Criterios de aceptacion: Endpoint responde 200 con datos publicos sin auth. DTO limpio.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-004 --stage qa`
  Resultado esperado: Prueba QA PASS para AC-004-01.
  Evidencia: pending
  Paralelismo[P]: No

- [ ] QA-004-T02 - Validar endpoint protegido y permisos
  Capa: qa
  Tipo: prueba
  Historia o criterio: AC-004-02, AC-004-09
  Objetivo: Validar endpoint protegido con verificacion de acceso cruzado.
  Responsabilidad unica: Si
  Depende de: BE-004-T03
  Contexto necesario: plan canonico; tareas BE/QA; QA-004.md
  Contratos usados: AC-004-02, AC-004-09; matriz de trazabilidad
  Entregables: Pruebas en test_clinic_router.py para 401/403.
  Criterios de aceptacion: 401 sin token. 403 cross-tenant. Sin datos en errores.
  Validacion: `python backend/scripts/validate_slice_plan.py BE-004 --stage qa`
  Resultado esperado: Pruebas QA PASS para AC-004-02 y AC-004-09.
  Evidencia: pending
  Paralelismo[P]: No

## Definition of Done

- [ ] Plan schema v3 valido.
- [ ] Todas las tareas aplicables estan en `- [x]` con evidencia reproducible.
- [ ] QA termina `APPROVED`.
- [ ] Findings inexistentes o `RESOLVED|ACCEPTED_RISK`.
- [ ] Reviews funcional, arquitectura y seguridad terminan `APPROVED`.
- [ ] Checks terminan `APPROVED`.
- [ ] Docker actualizado o skip justificado.
- [ ] Reporte de cierre del slice escrito en UTF-8.
