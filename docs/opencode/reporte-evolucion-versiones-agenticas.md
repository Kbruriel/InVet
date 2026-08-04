# Reporte de evolucion de versiones agenticas InVet

## Metadata

| Campo | Valor |
|---|---|
| Fecha | 2026-08-04 |
| Estado | Vigente |
| Version actual | Schema v3 |
| Alcance | Agentes OpenCode, comandos, templates, validador, gates y artefactos Markdown |
| Referencias | `docs/opencode/13_agents_architecture_and_gate_flow.md`; `docs/opencode/references/spec_kit_reference_improvements.md`; `backend/scripts/validate_slice_plan.py` |

## Resumen ejecutivo

El sistema agentico de InVet evoluciono desde una ejecucion secuencial por comandos hacia un flujo mas contractual, verificable y tolerante a gaps. La version actual, schema v3, incorpora aprendizajes de `github/spec-kit` sin reemplazar la estructura propia de InVet: mantiene un plan canonico por slice, pero agrega contexto explicito, trazabilidad, tareas atomicas, contrato Docker/pruebas, reportes esperados y politica UTF-8.

El cambio principal es que el plan deja de ser solo una lista de trabajo y pasa a ser un artefacto ejecutable para agentes independientes.

## Linea de evolucion

| Version | Enfoque | Capacidades | Limitaciones detectadas |
|---|---|---|---|
| v0 - Operacion manual | Ejecucion por criterio del agente o del usuario | Permitio avanzar slices iniciales y documentar hallazgos | Dependia demasiado de memoria conversacional y revisiones manuales |
| v1 - Flujo secuencial | Comandos BE, FE, QA y checks separados | Introdujo responsabilidad por rol y cierre por gates | Las tareas aun podian mezclar capas o entregables independientes |
| v2 - Plan canonico | `BE-00X-plan.md` como fuente de verdad por slice | Normalizo BE/FE/QA, evidencias, dependencias y preflights | Faltaban trazabilidad fina, contexto minimo, reportes esperados y politica de encoding |
| v2.1 - Gates reforzados | Persistencia segura, QA anterior, Docker y findings | Mejoro bloqueo por QA, seguridad, IDOR/BOLA y contenedores | Docker y reportes estaban documentados de forma parcial dentro de cada comando |
| v3 - Spec-driven agentico | Plan con contexto, trazabilidad, tareas atomicas, Docker, reportes y UTF-8 | Reduce gaps entre planner, implementadores, QA y docs | Los planes v2 existentes pasan a ser legacy y deben regenerarse antes de implementar |

## Motivacion del cambio v3

El analisis de `github/spec-kit` mostro patrones utiles para InVet:

- Separar especificacion, plan, tareas, analisis e implementacion.
- Tratar la documentacion como artefacto ejecutable.
- Hacer que cada tarea sea independiente, verificable y trazable.
- Detectar ambiguedades antes de implementar.
- Mantener templates como contrato de trabajo, no como documentacion decorativa.

InVet adopto esos principios en su propio modelo BE/FE/QA, sin copiar la estructura completa `specs/[feature]/`.

## Cambios aplicados en schema v3

### 1. Plan canonico mas explicito

El template `docs/opencode/templates/slice_plan_template.md` ahora exige:

- `schema_version: 3`.
- `encoding: UTF-8`.
- `Fuentes y artefactos de contexto`.
- `Matriz de trazabilidad`.
- `Contrato de ejecucion Docker y pruebas`.
- `Plan de reportes y findings`.
- `Politica UTF-8`.
- `Definition of Done` alineada a QA, reviews, checks, Docker y documentacion.

### 2. Tareas mas pequenas y con responsabilidad unica

Cada tarea debe declarar:

- `Capa`.
- `Tipo`.
- `Historia o criterio`.
- `Objetivo`.
- `Responsabilidad unica`.
- `Depende de`.
- `Contexto necesario`.
- `Contratos usados`.
- `Entregables`.
- `Criterios de aceptacion`.
- `Validacion`.
- `Resultado esperado`.
- `Evidencia`.
- `Paralelismo[P]`.

El objetivo es que un agente de implementacion pueda interpretar la tarea sin pedir contexto adicional y sin inventar alcance.

### 3. Rechazo de tareas compuestas

El validador y los contratos ahora bloquean tareas que mezclen responsabilidades como:

- Persistencia y endpoint.
- Caso de uso y router.
- UI y cliente API.
- Implementacion y pruebas.
- Seguridad y funcionalidad general.
- Docker y pruebas de producto.
- Documentacion y codigo.

Si una tarea mezcla varios resultados, debe dividirse antes de implementar.

### 4. Contrato Docker y pruebas

Los planes schema v3 deben indicar cuando una validacion corre:

- En host local.
- Dentro del contenedor `backend`.
- Contra PostgreSQL en `db`.
- Con runtime completo `db backend frontend`.

Esto evita que QA considere equivalente una corrida local cuando el criterio exige PostgreSQL o runtime en contenedor.

### 5. Reportes y findings como contrato previo

El plan ahora declara que artefactos deben producirse, quien los escribe y quien los consume:

- `docs/opencode/qa/QA-00X-results.md`.
- `docs/opencode/qa/QA-00X-findings.md`.
- `docs/opencode/reviews/BE-00X-review.md`.
- `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
- `docs/opencode/reviews/BE-00X-security-review.md`.
- `docs/opencode/checks/BE-00X-checks.md`.
- `docs/opencode/slices/BE-00X-evidence.md`.

Esto reduce gaps entre implementacion, QA, revisiones y documentacion final.

### 6. Politica UTF-8

Se introdujo UTF-8 como regla explicita para:

- Planes.
- Reportes.
- Findings.
- Reviews.
- Checks.
- Correcciones.
- Comentarios y outcomes escritos por agentes.

El validador detecta mojibake probable en planes nuevos y los scripts Python propios deben leer/escribir texto con `encoding="utf-8"` y emitir JSON con `ensure_ascii=False`.

## Archivos actualizados

| Area | Archivos |
|---|---|
| Validador | `backend/scripts/validate_slice_plan.py`; `payload/backend/scripts/validate_slice_plan.py` |
| Planner | `.opencode/commands/plan-task.md`; `.opencode/agents/invet-product-planner.md` |
| Implementadores | `.opencode/commands/implement-backend-task.md`; `.opencode/commands/implement-frontend-task.md`; `.opencode/agents/invet-backend-implementer.md`; `.opencode/agents/invet-frontend-implementer.md` |
| QA | `.opencode/commands/qa-task.md`; `.opencode/agents/invet-qa-validator.md` |
| Contratos | `docs/opencode/03_task_prompt_contracts.md`; `docs/opencode/04_agent_contracts.md`; `docs/opencode/05_done_gates_by_command.md` |
| Arquitectura | `docs/opencode/13_agents_architecture_and_gate_flow.md` |
| Templates | `docs/opencode/templates/*.md` |
| Referencia | `docs/opencode/references/spec_kit_reference_improvements.md` |
| Tests | `backend/app/tests/test_agentic_plan_schema_v3.py` |
| Payload | `payload/.opencode/**`; `payload/docs/opencode/**`; `payload/backend/scripts/validate_slice_plan.py` |

## Impacto esperado por agente

| Agente | Antes | Ahora |
|---|---|---|
| `invet-product-planner` | Generaba plan y tareas atomicas schema v2 | Genera plan schema v3 con contexto, trazabilidad, Docker, reportes, UTF-8 y tareas de responsabilidad unica |
| `invet-backend-implementer` | Implementaba por objetivo, entregables y criterios | Tambien consume tipo, criterio, contexto, contratos y resultado esperado; rechaza tareas compuestas |
| `invet-frontend-implementer` | Implementaba contrato frontend y pruebas | Tambien valida responsabilidad unica, contrato API/UI, resultado esperado y UTF-8 |
| `invet-qa-validator` | Validaba criterios, regresion y unit gaps | Tambien valida trazabilidad schema v3, contrato Docker, reportes esperados y evidencia UTF-8 |
| `invet-orchestrator` | Ordenaba flujo y gates | Opera sobre planes mas estrictos y bloquea antes si hay gaps de plan |

## Validaciones agregadas

Se agrego `backend/app/tests/test_agentic_plan_schema_v3.py` para comprobar:

- Que un plan schema v3 minimo con tareas atomicas pasa.
- Que un objetivo compuesto falla.
- Que mojibake probable falla.
- Que validador, template y referencia Spec Kit estan sincronizados con `payload`.

Validaciones ejecutadas:

```text
python -m ruff check backend\scripts\validate_slice_plan.py payload\backend\scripts\validate_slice_plan.py backend\app\tests\test_agentic_plan_schema_v3.py
python -m pytest backend\app\tests\test_agentic_plan_schema_v3.py backend\app\tests\test_secure_persistence_contracts.py backend\app\tests\test_docker_compose_closure_hooks.py -q
git diff --check
```

Resultado observado:

- Ruff: PASS.
- Pytest focalizado: 7 passed.
- Diff check: sin errores de whitespace.

## Riesgos y consideraciones

- Los planes schema v2 existentes son evidencia historica y deben tratarse como legacy para nueva implementacion.
- El siguiente `/plan-task` debe regenerar el plan al formato schema v3 antes de que BE, FE o QA implementen.
- El payload debe mantenerse sincronizado para que una reinstalacion no revierta los contratos.
- La deteccion de mojibake opera como guardrail documental; si un artefacto nuevo falla, debe corregirse el encoding antes de continuar.

## Decision

La version agentica vigente queda definida como schema v3. A partir de esta version, el cierre de un slice requiere planes con trazabilidad completa, tareas pequenas, responsabilidad unica, contexto suficiente para agentes independientes, contrato Docker/pruebas, reportes previstos y UTF-8 conservado.
