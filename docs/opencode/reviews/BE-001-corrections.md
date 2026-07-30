# Checklist de correcciones para slice BE-001

## Resumen de correcciones

Se alineo la documentacion fuente del slice `001` con el estado real ya aprobado en el plan y en `QA-001-results`. El ajuste cierra el drift entre tareas fuente, evidencia QA y checklist del slice.

## Hallazgos cerrados

- [x] Se actualizo `docs/opencode/tasks/backend/BE-001.md` para reflejar backend completado y validado.
- [x] Se actualizo `docs/opencode/tasks/qa/QA-001.md` para reflejar QA completado y documentado.
- [x] Se sincronizaron los equivalentes en `payload/`.
- [x] Se actualizo el contrato de `/implement-findings` para aceptar `FE-00X` y trabajar el mismo slice vertical.

## Archivos modificados

- `docs/opencode/tasks/backend/BE-001.md`
- `payload/docs/opencode/tasks/backend/BE-001.md`
- `docs/opencode/tasks/qa/QA-001.md`
- `payload/docs/opencode/tasks/qa/QA-001.md`
- `.opencode/commands/implement-findings.md`
- `payload/.opencode/commands/implement-findings.md`
- `.opencode/agents/invet-findings-implementer.md`
- `payload/.opencode/agents/invet-findings-implementer.md`
- `docs/opencode/01_command_runbook.md`
- `payload/docs/opencode/01_command_runbook.md`
- `docs/opencode/03_task_prompt_contracts.md`
- `payload/docs/opencode/03_task_prompt_contracts.md`
- `docs/opencode/README.md`
- `payload/docs/opencode/README.md`
- `docs/opencode/11_chatgpt_project_context.md`
- `payload/docs/opencode/11_chatgpt_project_context.md`
- `docs/opencode/12_troubleshooting_skills_vs_agents.md`
- `payload/docs/opencode/12_troubleshooting_skills_vs_agents.md`

## Validaciones ejecutadas

- [x] Backend
- [x] Frontend
- [x] QA
- [x] Checks

## Documentacion actualizada

- Estado del slice `001` consistente entre tareas fuente, plan, resultados QA y correcciones.
- Uso operativo de `/implement-findings FE-00X` documentado junto a la variante `BE-00X`.

## Pendientes o riesgos residuales

- Ninguno para el hallazgo corregido.

## Cierre

- [x] Todas las correcciones del hallazgo quedaron aplicadas.
- [x] El slice puede revalidarse o avanzar.
