# 10 — Migración desde paquete secuencial anterior

El paquete anterior contenía únicamente:

```text
update-invet-opencode-sequential-plan.ps1
docs/opencode/00_sequential_execution_manifest.md
docs/opencode/01_command_runbook.md
docs/opencode/02_be_fe_qa_task_matrix.md
docs/opencode/03_task_prompt_contracts.md
docs/opencode/04_done_gates_by_command.md
docs/opencode/README.md
```

Este paquete lo reemplaza por una instalación completa que añade:

- Agentes OpenCode en `.opencode/agents`.
- Comandos slash en `.opencode/commands`.
- Tareas individuales BE/FE/QA.
- Referencias de diseño, seguridad, arquitectura y checks.
- Instalador PowerShell con backup opcional.

## Comando recomendado tras instalar

```text
/plan-task BE-001
```
