# Flujo agentico InVet en VS Code

## Objetivo

VS Code puede ejecutar el mismo slice que OpenCode sin crear subagentes. El modelo seleccionado conserva la ejecucion durante cada fase; los perfiles especializados delimitan responsabilidades cuando el usuario inicia una fase manualmente, pero el orquestador no los convoca como otros modelos.

Las reglas automaticas y compactas viven en `.github/copilot-instructions.md`. Este documento explica el flujo y no debe cargarse antes de cada tarea.

## Configuracion local recomendada

- Contexto de Ollama: 65,536 tokens.
- Presupuesto operativo por fase: detener y guardar checkpoint cerca de 48,000 tokens.
- Solicitudes maximas de VS Code: 50 mediante `.vscode/settings.json`.
- Tiempo maximo por fase: 30 minutos.
- Inactividad sin herramienta o progreso: 3 minutos.
- Acciones equivalentes: cancelar al tercer intento; despues del primer fallo se exige nueva evidencia.

El limite de salida definido en OpenCode no gobierna necesariamente el proveedor nativo Ollama de VS Code. El control efectivo aqui es mantener pequeño el contexto de entrada y cerrar cada tarea atomica con checkpoint.

## Un solo modelo, varias responsabilidades

Los agentes especializados de `.github/agents/` son perfiles seleccionables, no una autorizacion para delegar. Ninguno declara la herramienta `agent`, listas `agents` ni handoffs.

El catalogo canonico es `docs/opencode/agent_registry.json`. Cada `.github/prompts/*.prompt.md` declara el perfil visible que corresponde al mismo comando OpenCode. La equivalencia de permisos es semantica: GitHub expone `read/search/edit/execute`, mientras las instrucciones del perfil, el manifiesto de capa y los gates restringen que puede editar; OpenCode expresa parte de esas restricciones directamente en su frontmatter.

| Perfil | Responsabilidad |
|---|---|
| InVet Orchestrator | Ejecutar el flujo completo en el modelo actual |
| InVet Product Planner | Plan, US, UIA, APIA y cinco manifiestos |
| InVet Backend Implementer | Codigo y pruebas backend |
| InVet Frontend Implementer | Producto y pruebas frontend |
| InVet UI Automation Implementer | Automatizacion de navegador |
| InVet API Automation Implementer | Automatizacion HTTP/API |
| InVet QA Validator | Decision QA con evidencia, sin reparar producto |
| InVet Slice Reviewer | Revision funcional |
| InVet Clean Architecture Reviewer | Limites de arquitectura |
| InVet Security Reviewer | Riesgos de seguridad |
| InVet Check Runner | UI checks y checks formales |
| InVet Docs Updater | Cierre documental |
| InVet Findings Implementer | Correcciones y revalidacion pendiente |
| InVet Final Reviewer | Decision final obligatoria |

Los antiguos perfiles genericos Planner, Implementer, QA Reviewer y Findings Resolver se retiraron porque duplicaban funciones y habilitaban handoffs.

## Propiedad de los manifiestos

`plan-task.prompt.md` con InVet Product Planner es el unico flujo que decide alcance. Crea o repara:

- `docs/opencode/plans/BE-00X-plan.md`
- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`
- `docs/opencode/manifests/BE-00X-{backend,frontend,qa,ui-automation,api-automation}.md`

Despues de validar el plan ejecuta:

```text
python backend/scripts/manage_slice_task.py manifest BE-00X --layer all
python backend/scripts/manage_slice_task.py verify BE-00X --layer all
```

Los implementadores leen solamente el manifiesto de su capa. QA y gates de cierre verifican los cinco y abren despues solo la evidencia relevante. El plan completo se consulta si un hash falla o hay una contradiccion concreta.

## Flujo completo

`execute-slice.prompt.md` acepta BE, FE o QA y normaliza el indice. El mismo modelo ejecuta:

```text
plan-task.prompt.md BE-00X
implement-backend-task.prompt.md BE-00X
implement-frontend-task.prompt.md BE-00X
implement-ui-automation-task.prompt.md BE-00X
implement-api-automation-task.prompt.md BE-00X
qa-task.prompt.md QA-00X
review-slice.prompt.md BE-00X
clean-architecture-review.prompt.md BE-00X
security-review.prompt.md BE-00X
run-ui-checks.prompt.md BE-00X
run-checks.prompt.md BE-00X
update-docs.prompt.md BE-00X
final-gate.prompt.md BE-00X
```

El comando backend ejecuta internamente sus validadores, incluida la persistencia segura cuando aplica; el usuario no tiene que invocar el script. El final gate es obligatorio. El flujo se detiene ante el primer `REJECTED`, `BLOCKED`, finding bloqueante, manifiesto stale, archivo fuera de allowlist o invariante de router perdida.

En el flujo completo el perfil activo es siempre `InVet Orchestrator`, que ejecuta directamente cada contrato sin handoff. En una ejecucion manual se selecciona el perfil indicado por el prompt: por ejemplo, `implement-backend-task.prompt.md BE-014` se ejecuta con `InVet Backend Implementer`. La tabla, el diagrama y las plantillas de prompt copiables para cada etapa de ambas rutas viven en `13_agents_architecture_and_gate_flow.md`, bajo `Prompts recomendados por etapa`.

Verifica que los 14 perfiles, 15 prompts, mapeos y copias distribuibles sigan alineados con:

```text
python backend/scripts/validate_agent_catalog.py
```

## Checkpoint por tarea

Cada implementador trabaja una tarea atomica:

```text
python backend/scripts/manage_slice_task.py start BE-00X --task BE-00X-TNN
python backend/scripts/manage_slice_task.py state --task BE-00X-TNN --set editing
python backend/scripts/manage_slice_task.py state --task BE-00X-TNN --set testing
python backend/scripts/manage_slice_task.py finish --task BE-00X-TNN --result pass --evidence "comando: resultado"
```

El checkpoint registra tarea, estado, resultado, evidencia y archivos cambiados. `failed` o `blocked` nunca quedan como tarea completada. Al reanudar BE-009, el agente inspecciona el checkpoint y no repite tareas completas.

Las eliminaciones requieren una justificacion explicita con `--allow-deletions`. El cierre tambien bloquea archivos fuera de `Entregables` y cualquier `include_router(...)` previo que desaparezca.

## Estado observable y cancelacion

El agente informa solamente cambios de estado: `leyendo`, `editando`, `ejecutando pruebas`, `esperando permiso` y `generacion cancelada`.

Al cancelar por presupuesto, inactividad o repeticion:

1. Termina de forma segura la operacion local en curso.
2. Guarda checkpoint de la tarea si hay evidencia valida.
3. No marca el gate como aprobado.
4. Devuelve el prompt o comando exacto para reanudar.

## Continuidad de gates

- QA aprobada sin findings bloqueantes pasa a revision funcional.
- Un finding `OPEN` o `IN_PROGRESS` vuelve a `implement-findings.prompt.md`.
- Un finding corregido queda `READY_FOR_REVALIDATION` y vuelve a QA.
- Revision funcional aprobada pasa a arquitectura, no vuelve a QA.
- Correcciones posteriores repiten QA, UI checks y los reviews afectados.
- Docs aprobada pasa siempre a final gate.

Cada respuesta termina con estado, siguiente paso exacto y motivo conforme a `.github/copilot-instructions.md`.
