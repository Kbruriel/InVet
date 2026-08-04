---
schema_version: 3
slice: "XXX"
canonical_plan: BE-XXX
status: PLANNED
encoding: UTF-8
---

# BE-XXX Plan - Titulo del slice

## Objetivo del slice

Un resultado funcional vertical, demostrable y acotado.

## Alcance MVP

## Fuera de alcance

## Suposiciones

Registrar solo supuestos no bloqueantes. Si el supuesto cambia contrato publico, seguridad, persistencia o aceptacion QA, detener la planificacion y preguntar.

## Revision de gaps

- Fuente revisada:
- Gap:
- Decision:
- Impacto en tareas:

## Entidades y reglas de negocio

| Entidad o regla | Fuente | Responsabilidad del slice | Validacion |
| --- | --- | --- | --- |
|  |  |  |  |

## Fuentes y artefactos de contexto

| Artefacto | Ruta | Uso por agentes | Estado |
| --- | --- | --- | --- |
| Matriz BE/FE/QA | `docs/opencode/02_be_fe_qa_task_matrix.md` | Alcance vertical y correspondencia de IDs | REQUIRED |
| Tarea backend | `docs/opencode/tasks/backend/BE-XXX.md` | Reglas, entidades, persistencia y API | REQUIRED |
| Tarea frontend | `docs/opencode/tasks/frontend/FE-XXX.md` | Rutas, UI, estados y contrato de cliente | REQUIRED |
| Tarea QA | `docs/opencode/tasks/qa/QA-XXX.md` | Criterios de aceptacion y riesgos | REQUIRED |
| Referencia arquitectura | `docs/opencode/references/backend_clean_architecture.md` | Limites backend | REQUIRED si hay backend |
| Referencia visual | `docs/opencode/references/frontend_visual_alignment.md` | UI y accesibilidad | REQUIRED si hay frontend |
| Referencia checks | `docs/opencode/references/run_checks_matrix.md` | Checks esperados | REQUIRED |

## Matriz de trazabilidad

| ID | Fuente | Historia o criterio | Tarea planificada | Validacion | Evidencia esperada |
| --- | --- | --- | --- | --- | --- |
| AC-XXX-01 | BE/FE/QA/matriz |  | BE-XXX-T01 |  |  |

Regla: ningun criterio funcional, contrato API, riesgo de seguridad o estado UX puede quedar sin tarea y validacion asociada.

## Endpoints esperados

| Accion | Metodo | Ruta `/api/v1` | Auth | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Contrato de implementacion frontend

### Rutas y acceso

### Flujos y estados UX

Debe cubrir `loading`, `submitting`, `error`, `empty` y `success` cuando apliquen.

### Contratos API por accion

| Accion UI | Endpoint | Metodo | Request | Response | Errores | Auth |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

### Formularios y validacion

### Arquitectura de componentes

### Responsive y accesibilidad

### Estrategia de pruebas frontend

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
| `docs/opencode/qa/QA-XXX-results.md` | QA | Orchestrator, reviews, docs | Siempre durante `/qa-task` |
| `docs/opencode/qa/QA-XXX-findings.md` | QA | Implementadores, QA | Si hay `FAIL`, `BLOCKED` o gaps unitarios |
| `docs/opencode/reviews/BE-XXX-review.md` | Slice reviewer | Findings, checks | Siempre durante `/review-slice` |
| `docs/opencode/reviews/BE-XXX-clean-architecture-review.md` | Clean architecture reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/reviews/BE-XXX-security-review.md` | Security reviewer | Findings, checks | Siempre durante el gate |
| `docs/opencode/checks/BE-XXX-checks.md` | Check runner | Docs | Siempre durante `/run-checks BE-XXX` |
| `docs/opencode/slices/BE-XXX-evidence.md` | Orchestrator o docs | Equipo | Al cierre del slice |

## Pruebas QA

| Criterio | Riesgo | Nivel | Suite o archivo esperado | Decision esperada |
| --- | --- | --- | --- | --- |
|  |  | unit/integration/contract/security/regression/frontend |  | PASS |

## Riesgos de seguridad/IDOR/BOLA

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

Reglas:
- Cada tarea tiene una sola responsabilidad verificable.
- Cada tarea apunta a una sola capa y a un tipo de trabajo.
- Si mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, dividir en tareas `TNN` consecutivas.
- `Responsabilidad unica` debe ser `Si`.
- `Objetivo` debe ser corto, sin objetivos compuestos.
- `Contexto necesario` debe listar archivos o decisiones que el implementador debe leer.
- `Contratos usados` debe mapear la tarea con endpoints, criterios, referencias o reportes.
- `Resultado esperado` debe describir el outcome observable que otro agente puede validar.

### Backend

- [ ] BE-XXX-T01 - Titulo corto
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-XXX-01
  Objetivo: Definir contrato backend verificable.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: `docs/opencode/tasks/backend/BE-XXX.md`; matriz del slice
  Contratos usados: endpoint o regla asociada
  Entregables: Rutas concretas de archivos, endpoint o migracion.
  Criterios de aceptacion: Condiciones observables separadas por punto.
  Validacion: Comando o inspeccion reproducible.
  Resultado esperado: Contrato disponible para implementacion y QA.
  Evidencia: pending
  Paralelismo[P]: No

### Frontend

- [ ] FE-XXX-T01 - Titulo corto
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-XXX-01
  Objetivo: Implementar cliente API tipado.
  Responsabilidad unica: Si
  Depende de: BE-XXX-T01
  Contexto necesario: `docs/opencode/tasks/frontend/FE-XXX.md`; contrato frontend del plan
  Contratos usados: endpoint o accion UI asociada
  Entregables: Rutas, componentes, formularios o cliente API concretos.
  Criterios de aceptacion: Condiciones observables separadas por punto.
  Validacion: Comando de prueba, typecheck o build.
  Resultado esperado: UI o cliente verificable por QA.
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] QA-XXX-T01 - Titulo corto
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-XXX-01
  Objetivo: Validar criterio principal.
  Responsabilidad unica: Si
  Depende de: BE-XXX-T01, FE-XXX-T01
  Contexto necesario: plan canonico; tareas BE/FE/QA; reportes existentes
  Contratos usados: matriz de trazabilidad; contrato Docker y pruebas
  Entregables: Suites y reporte QA esperado.
  Criterios de aceptacion: Estados PASS requeridos y evidencia esperada.
  Validacion: Comandos y reportes machine-readable.
  Resultado esperado: Decision QA trazable.
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
