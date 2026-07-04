# Plan de implementacion - agente invet-product-planner

## Contexto analizado

El comando `/plan-task` usa el agente `invet-product-planner`. El agente ya define el alcance funcional del slice, conserva limites MVP y evita escribir codigo fuente, pero el contrato actual no exige que el resultado se entregue como checklist numerado con paralelismo y criterios medibles por tarea.

## Checklist de implementacion

- [ ] 1. Objetivo: Actualizar el contrato del comando `/plan-task` para exigir un checklist numerado como salida del plan.
  Criterios de aceptacion: `.opencode/commands/plan-task.md` indica explicitamente que el resultado debe incluir tareas numeradas; cada tarea contiene objetivo, criterios de aceptacion y `Paralelismo[P]`; el comando mantiene la regla de no implementar codigo.
  Paralelismo[P]: No

- [ ] 2. Objetivo: Actualizar las responsabilidades del agente `invet-product-planner` para producir tareas atomicas.
  Criterios de aceptacion: `.opencode/agents/invet-product-planner.md` indica que cada tarea debe tener un unico objetivo; ninguna responsabilidad combina backend, frontend y QA en una misma tarea; el agente conserva la separacion MVP, Stage 1, Stage 2 y fuera de alcance.
  Paralelismo[P]: No

- [ ] 3. Objetivo: Definir reglas de paralelismo para las tareas generadas por `/plan-task`.
  Criterios de aceptacion: El contrato documenta que `Paralelismo[P]: Si` solo aplica cuando la tarea no depende de entregables previos; `Paralelismo[P]: No` aplica cuando la tarea requiere decisiones, contratos o resultados anteriores; todas las tareas generadas incluyen exactamente una marca de paralelismo.
  Paralelismo[P]: Si

- [ ] 4. Objetivo: Definir criterios de aceptacion medibles para cada tarea generada por `/plan-task`.
  Criterios de aceptacion: El contrato exige criterios verificables mediante archivos, endpoints, pruebas, comandos ejecutados o documentos generados; no se aceptan criterios ambiguos como "funciona correctamente" sin una medicion observable; cada tarea contiene al menos dos criterios de aceptacion.
  Paralelismo[P]: Si

- [ ] 5. Objetivo: Actualizar la documentacion operativa del contrato `/plan-task`.
  Criterios de aceptacion: `docs/opencode/03_task_prompt_contracts.md` describe el nuevo formato checklist; `docs/opencode/05_done_gates_by_command.md` incluye un gate que valida numeracion, objetivo unico, criterios medibles y paralelismo; `docs/opencode/11_chatgpt_project_context.md` resume la nueva salida esperada.
  Paralelismo[P]: No

- [ ] 6. Objetivo: Sincronizar el espejo `payload` con los cambios del comando, agente y documentacion.
  Criterios de aceptacion: Los archivos equivalentes bajo `payload/.opencode` y `payload/docs/opencode` contienen las mismas reglas de salida; una busqueda por `Paralelismo[P]` encuentra referencias en la documentacion principal y en el espejo; no existen contradicciones entre ambos arboles.
  Paralelismo[P]: No

- [ ] 7. Objetivo: Validar que el formato del plan generado cumpla la estructura solicitada.
  Criterios de aceptacion: Existe al menos un archivo Markdown de ejemplo o resultado que usa el formato `- [ ] Numero de tarea`; cada entrada incluye las lineas `Objetivo`, `Criterios de aceptacion` y `Paralelismo[P]`; el archivo puede revisarse con busqueda textual sin pasos manuales adicionales.
  Paralelismo[P]: Si

- [ ] 8. Objetivo: Documentar el cierre de la actualizacion del agente.
  Criterios de aceptacion: El resumen de cierre enumera archivos modificados; indica que no se implemento codigo fuente de producto; registra cualquier pendiente o limitacion si no se pudo validar el agente en ejecucion real.
  Paralelismo[P]: No
