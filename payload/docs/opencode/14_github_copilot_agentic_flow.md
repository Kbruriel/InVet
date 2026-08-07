# Flujo agentico InVet para GitHub Copilot

## Estado del documento

| Campo | Valor |
|---|---|
| Estado | Vigente |
| Objetivo | Adaptar el flujo agentico OpenCode a GitHub Copilot |
| Instrucciones Copilot | `.github/copilot-instructions.md` |
| Custom agents VS Code | `.github/agents/*.agent.md` |
| Prompt files | `.github/prompts/*.prompt.md` |
| Plan canonico | `docs/opencode/plans/BE-00X-plan.md` |
| Motor de gates | `backend/scripts/validate_slice_plan.py` |

Este documento traduce el flujo agentico de InVet a una forma compatible con GitHub Copilot. GitHub Copilot no ejecuta los slash commands de OpenCode como `/plan-task` o `/qa-task`; en Copilot se trabaja con instrucciones del repositorio, prompts reutilizables y artefactos Markdown versionables.

La fuente funcional sigue siendo `docs/opencode/13_agents_architecture_and_gate_flow.md`. Esta version solo cambia la forma de invocar el flujo.

Nota de compatibilidad: `.github/copilot-instructions.md` es la instruccion principal del repositorio. Para que VS Code muestre agentes en el selector, deben existir archivos de agente en `.github/agents/*.agent.md`. Los prompt files `*.prompt.md` siguen siendo utiles como prompts reutilizables; si el IDE no los expone, copia el contenido del prompt correspondiente en Copilot Chat y conserva las mismas reglas de gates y evidencia.

## Estructura Copilot

| Archivo | Funcion |
|---|---|
| `.github/copilot-instructions.md` | Instrucciones permanentes para Copilot dentro del repositorio |
| `.github/agents/invet-orchestrator.agent.md` | Agente visible en VS Code para conducir el flujo completo |
| `.github/agents/invet-planner.agent.md` | Agente visible en VS Code para planificar o reparar slices |
| `.github/agents/invet-implementer.agent.md` | Agente visible en VS Code para implementar una capa |
| `.github/agents/invet-qa-reviewer.agent.md` | Agente visible en VS Code para QA, reviews y cierre |
| `.github/agents/invet-findings-resolver.agent.md` | Agente visible en VS Code para corregir findings |
| `.github/prompts/invet-plan-slice.prompt.md` | Prompt para crear o reparar el plan canonico del slice |
| `.github/prompts/invet-execute-slice.prompt.md` | Prompt para ejecutar el flujo completo gate por gate |
| `.github/prompts/invet-implement-slice.prompt.md` | Prompt para implementar backend, frontend, UI automation o API automation |
| `.github/prompts/invet-qa-review-close.prompt.md` | Prompt para QA, reviews, checks, docs y final gate |
| `.github/prompts/invet-resolve-findings.prompt.md` | Prompt para corregir hallazgos y preparar revalidacion |

## Cobertura migrada

La migracion Copilot debe conservar paridad con OpenCode. La cobertura vigente es:

| Area OpenCode | Cantidad OpenCode | Migracion Copilot | Estado |
|---|---:|---|---|
| Comandos slash | 15 | 15 prompt files equivalentes en `.github/prompts/<command>.prompt.md` | Completo |
| Agentes especializados | 16 | 16 custom agents espejo en `.github/agents/invet-*.agent.md` | Completo |
| Agentes de conveniencia Copilot | No aplica | 4 agentes agregados para flujo resumido | Complementario |
| Templates Markdown | 8 | Reutilizados desde `docs/opencode/templates/*.md` por prompts y agentes | Completo |
| Referencias operativas | 9 | Reutilizadas desde `docs/opencode/references/*.md` por prompts y agentes | Completo |
| Validador determinista | 1 | Reutilizado como `backend/scripts/validate_slice_plan.py` | Completo |
| Payload distribuible | `.opencode`, `docs/opencode`, scripts | `.github`, prompts, agents y docs sincronizados en `payload/` | Completo |

La migracion no duplica el contenido completo de cada comando dentro de Copilot. Cada agente y prompt Copilot lee el contrato OpenCode original que le corresponde y lo ejecuta con herramientas de VS Code/Copilot. Esto evita que existan dos fuentes normativas divergentes.

## Mapeo OpenCode a Copilot

| Flujo OpenCode | Equivalente Copilot |
|---|---|
| `/execute-slice FE-00X` | `execute-slice.prompt.md` con agente `InVet Orchestrator` |
| `/plan-task BE|FE|QA-00X` | `plan-task.prompt.md` con agente `InVet Product Planner` |
| `/implement-backend-task BE-00X` | `implement-backend-task.prompt.md` con agente `InVet Backend Implementer` |
| `/implement-frontend-task FE-00X` | `implement-frontend-task.prompt.md` con agente `InVet Frontend Implementer` |
| `/implement-ui-automation-task FE-00X` | `implement-ui-automation-task.prompt.md` con agente `InVet UI Automation Implementer` |
| `/implement-api-automation-task BE-00X` | `implement-api-automation-task.prompt.md` con agente `InVet API Automation Implementer` |
| `/qa-task QA-00X` | `qa-task.prompt.md` con agente `InVet QA Validator` |
| `/review-slice FE-00X` | `review-slice.prompt.md` con agente `InVet Slice Reviewer` |
| `/clean-architecture-review FE-00X` | `clean-architecture-review.prompt.md` con agente `InVet Clean Architecture Reviewer` |
| `/security-review FE-00X` | `security-review.prompt.md` con agente `InVet Security Reviewer` |
| `/implement-findings FE-00X` | `implement-findings.prompt.md` con agente `InVet Findings Implementer` |
| `/run-ui-checks FE-00X` | `run-ui-checks.prompt.md` con agente `InVet Check Runner` |
| `/run-checks FE-00X` | `run-checks.prompt.md` con agente `InVet Check Runner` |
| `/update-docs FE-00X` | `update-docs.prompt.md` con agente `InVet Docs Updater` |
| `/final-gate FE-00X` | `final-gate.prompt.md` con agente `InVet Final Reviewer` |

## Agentes visibles en VS Code

VS Code detecta agentes personalizados de workspace desde `.github/agents`. En este repositorio se crean estos agentes:

| Agente VS Code | Uso principal |
|---|---|
| `InVet Orchestrator` | Ejecutar el flujo completo gate por gate |
| `InVet Planner` | Crear o reparar el plan canonico schema v3 |
| `InVet Implementer` | Implementar backend, frontend, UI automation o API automation |
| `InVet QA Reviewer` | Ejecutar QA, reviews, UI checks, checks, docs y final gate |
| `InVet Findings Resolver` | Resolver findings y preparar revalidacion |

Tambien existen agentes espejo de paridad para cada agente OpenCode:

```text
InVet Orchestrator
InVet Product Planner
InVet Backend Implementer
InVet Frontend Implementer
InVet UI Automation Implementer
InVet API Automation Implementer
InVet QA Validator
InVet Slice Reviewer
InVet Clean Architecture Reviewer
InVet Security Reviewer
InVet Findings Implementer
InVet Check Runner
InVet Docs Updater
InVet Final Reviewer
InVet Command Executor
InVet Command Executor Fallback
```

Si no aparecen en VS Code, abre la raiz del repo `C:\InVet`, recarga la ventana, ejecuta `/agents` en Chat o abre `Chat: Open Customizations`. Si abriste una subcarpeta, activa `chat.useCustomizationsInParentRepositories` para que VS Code descubra customizations del repositorio padre.

## Flujo completo en Copilot

Para pedir a Copilot que ejecute un slice completo:

```text
Usa .github/prompts/invet-execute-slice.prompt.md
Slice ID: FE-001
Ejecuta el flujo gate por gate y detenlo ante el primer gate fallido.
```

La secuencia completa que Copilot debe seguir es:

```text
Plan Slice for FE-001
Implement Slice Layer: backend for BE-001
python backend/scripts/validate_slice_plan.py BE-001 --stage secure-persistence
Implement Slice Layer: frontend for FE-001
Implement Slice Layer: ui-automation for FE-001
Implement Slice Layer: api-automation for BE-001
QA, Review, And Close Gates: qa for QA-001
QA, Review, And Close Gates: functional-review for FE-001
QA, Review, And Close Gates: clean-architecture-review for FE-001
QA, Review, And Close Gates: security-review for FE-001
QA, Review, And Close Gates: ui-checks for FE-001
QA, Review, And Close Gates: checks for FE-001
QA, Review, And Close Gates: docs for FE-001
QA, Review, And Close Gates: final-gate for FE-001
```

`final-gate` es opcional. Si no se solicita segunda opinion de release, el cierre normal termina en `Gate: docs` despues de checks aprobados.

## Flujo manual recomendado

Cuando se trabaje paso a paso en Copilot, usar los prompts en este orden:

```text
invet-plan-slice.prompt.md
invet-implement-slice.prompt.md        Layer: backend
secure-persistence validator
invet-implement-slice.prompt.md        Layer: frontend
invet-implement-slice.prompt.md        Layer: ui-automation
invet-implement-slice.prompt.md        Layer: api-automation
invet-qa-review-close.prompt.md        Gate: qa
invet-qa-review-close.prompt.md        Gate: functional-review
invet-qa-review-close.prompt.md        Gate: clean-architecture-review
invet-qa-review-close.prompt.md        Gate: security-review
invet-qa-review-close.prompt.md        Gate: ui-checks
invet-qa-review-close.prompt.md        Gate: checks
invet-qa-review-close.prompt.md        Gate: docs
invet-qa-review-close.prompt.md        Gate: final-gate
```

## Hallazgos y revalidacion

Si Copilot encuentra findings en QA, reviews, UI checks o checks, debe detener el avance normal.

Primero se usa:

```text
invet-resolve-findings.prompt.md
Slice ID: FE-001
```

Despues de corregir, el primer gate de revalidacion siempre es QA:

```text
invet-qa-review-close.prompt.md
Gate: qa
Slice ID: QA-001
```

Luego se repiten los gates afectados:

```text
Gate: functional-review
Gate: clean-architecture-review
Gate: security-review
Gate: ui-checks
Gate: checks
```

Un finding en `READY_FOR_REVALIDATION` todavia bloquea. Copilot no debe marcarlo como `RESOLVED` durante implementacion; solo QA o el reviewer responsable puede cerrarlo con evidencia.

Los archivos `docs/opencode/qa/QA-00X-findings.md` deben incluir un estado global:

```text
- Estado global: OPEN|IN_PROGRESS|READY_FOR_REVALIDATION|RESOLVED|ACCEPTED_RISK
```

Copilot solo puede recomendar el gate de review funcional despues de QA si `docs/opencode/qa/QA-00X-results.md` declara `Decision: APPROVED` y el archivo de findings no existe o tiene estado global `RESOLVED`/`ACCEPTED_RISK`.

Si QA queda `REJECTED`, `BLOCKED` o con findings `OPEN`/`IN_PROGRESS`, el siguiente paso recomendado es `invet-resolve-findings.prompt.md` o `implement-findings.prompt.md` con el `BE-00X` equivalente. Si los findings estan `READY_FOR_REVALIDATION`, ese estado pertenece al flujo de correcciones y la revalidacion QA se recomienda desde el resolver, no como auto-rerun del cierre de QA.

Cuando el gate `functional-review` si se ejecuta y queda `APPROVED`, el siguiente paso recomendado es `clean-architecture-review.prompt.md` o `invet-qa-review-close.prompt.md` con `Gate: clean-architecture-review`, no volver a QA. Solo se recomienda QA desde functional review si el preflight impidio revisar porque QA no estaba aprobado o necesitaba revalidacion.

## Siguiente paso recomendado

Cada prompt Copilot debe terminar con:

```text
Siguiente paso recomendado: <prompt o comando exacto>
Motivo: <razon del siguiente gate>
```

Si hay hallazgos:

```text
Comando recomendado para resolver hallazgos: invet-resolve-findings.prompt.md con Slice ID FE-00X
Motivo: Los findings bloquean el avance hasta revalidacion.
```

Si hay bloqueo:

```text
Comando recomendado para desbloquear el gate: <prompt o comando exacto>
Motivo: <artefacto, evidencia o validacion faltante>
```

## Reglas de compatibilidad Copilot

- No depender de memoria conversacional. Cada prompt debe leer los artefactos Markdown relevantes.
- No tratar los slash commands como ejecutables dentro de Copilot.
- Usar los prompt files como equivalentes operativos.
- Mantener la evidencia en archivos versionables.
- Ejecutar comandos de terminal solo cuando sean necesarios para validar.
- No avanzar si falta el plan canonico o si `validate_slice_plan.py` falla.
- No cerrar el slice solo porque Copilot termino una tarea de codigo.
- Mantener `payload/` sincronizado cuando se cambie documentacion o contratos distribuibles.

## Fuentes de contexto

Esta adaptacion se apoya en la documentacion oficial de GitHub Copilot para:

- Instrucciones de repositorio en `.github/copilot-instructions.md`.
- Instrucciones por ruta en `.github/instructions/**/*.instructions.md` cuando se necesiten.
- Prompt files reutilizables `*.prompt.md`.

En InVet, la version inicial usa instrucciones de repositorio y prompt files. Las instrucciones por ruta pueden agregarse despues si hace falta separar reglas para `backend/`, `frontend/` o `InVet_UI_Automation/`.
