# InVet - OpenCode secuencial

Esta carpeta contiene la documentacion operativa para ejecutar InVet por slices verticales usando comandos OpenCode.

## Skills vs agentes OpenCode

Los `invet-*` son agentes OpenCode, no skills Codex. Se ejecutan mediante comandos slash.

Ejemplo correcto:

```text
/implement-backend-task BE-00X
```

Si aparece `Skill "invet-backend-implementer" not found`, revisa `12_troubleshooting_skills_vs_agents.md`.

## Flujo obligatorio por slice

Flujo recomendado:

```text
/execute-slice BE-00X
```

Flujo manual equivalente:

```text
/plan-task BE-00X
/implement-backend-task BE-00X
/implement-frontend-task FE-00X
/qa-task QA-00X
/review-slice BE-00X
/clean-architecture-review BE-00X
/security-review BE-00X
/implement-findings BE-00X  # solo si hay hallazgos
/qa-task QA-00X             # repetir despues de correcciones
/run-checks BE-00X
/update-docs BE-00X
```

Notas:
- `/plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, normaliza el mismo indice y nunca implementa codigo.
- Todos los IDs producen un unico plan canonico `docs/opencode/plans/BE-00X-plan.md`.
- Los planes nuevos usan schema v3 y se validan con `backend/scripts/validate_slice_plan.py`.
- Los planes schema v2 son legacy: deben regenerarse con `/plan-task` antes de implementarse.
- Los artefactos operativos se escriben en UTF-8.
- Para implementar frontend usa `/implement-frontend-task FE-00X`.
- Para ejecutar QA usa `/qa-task QA-00X`.
- Para revisar un slice puedes usar `/review-slice BE-00X` o `/review-slice FE-00X`.
- Para cerrar hallazgos puedes usar `/implement-findings BE-00X` o `/implement-findings FE-00X`.

Los archivos de hallazgos esperados son:
- `docs/opencode/reviews/BE-00X-review.md`
- `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
- `docs/opencode/reviews/BE-00X-security-review.md`
- `docs/opencode/reviews/BE-00X-corrections.md`

## Indice

- `00_installation_manifest.md`: que instalo el paquete.
- `01_command_runbook.md`: como ejecutar comandos.
- `02_be_fe_qa_task_matrix.md`: matriz BE/FE/QA.
- `03_task_prompt_contracts.md`: contrato de prompts por comando.
- `04_agent_contracts.md`: responsabilidades de agentes.
- `05_done_gates_by_command.md`: gates de cierre.
- `11_chatgpt_project_context.md`: contexto consolidado para usar el proyecto en ChatGPT.
- `12_troubleshooting_skills_vs_agents.md`: solucion al error de confundir skills Codex con agentes OpenCode.
- `templates`: plantillas Markdown para resultados, hallazgos y correcciones.
- `templates/slice_plan_template.md`: contrato obligatorio de planes schema v3.
- `references/spec_kit_reference_improvements.md`: adaptacion de aprendizajes de `github/spec-kit` al flujo agentico InVet.
- `tasks/backend`: tareas backend.
- `tasks/frontend`: tareas frontend.
- `tasks/qa`: tareas QA.
- `references`: reglas de alcance, diseno, arquitectura y seguridad.
