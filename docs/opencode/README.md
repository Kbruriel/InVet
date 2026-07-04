# InVet — OpenCode secuencial

Esta carpeta contiene la documentación operativa para ejecutar InVet por slices verticales usando comandos OpenCode.

## Flujo obligatorio por slice

```text
/plan-task BE-00X
/implement-backend-task BE-00X
/implement-frontend-task FE-00X
/qa-task QA-00X
/review-slice BE-00X
/implement-findings BE-00X
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## Índice

- `00_installation_manifest.md`: qué instaló el paquete.
- `01_command_runbook.md`: cómo ejecutar comandos.
- `02_be_fe_qa_task_matrix.md`: matriz BE/FE/QA.
- `03_task_prompt_contracts.md`: contrato de prompts por comando.
- `04_agent_contracts.md`: responsabilidades de agentes.
- `05_done_gates_by_command.md`: gates de cierre.
- `11_chatgpt_project_context.md`: contexto consolidado para usar el proyecto en ChatGPT.
- `templates`: plantillas Markdown para resultados, hallazgos y correcciones.
- `tasks/backend`: tareas backend.
- `tasks/frontend`: tareas frontend.
- `tasks/qa`: tareas QA.
- `references`: reglas de alcance, diseño, arquitectura y seguridad.
