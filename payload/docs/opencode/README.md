# InVet - OpenCode secuencial

Esta carpeta contiene la documentacion operativa para ejecutar InVet por slices verticales usando comandos OpenCode.

Consulta `15_operational_manifests_flow.md` para la propiedad, verificacion y cadena completa de manifiestos operativos.

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
/implement-frontend-task BE-00X
/implement-ui-automation-task BE-00X
/implement-api-automation-task BE-00X
/qa-task QA-00X
/review-slice BE-00X
/clean-architecture-review BE-00X
/security-review BE-00X
/implement-findings BE-00X  # solo si hay hallazgos
/qa-task QA-00X             # repetir despues de correcciones
/run-ui-checks BE-00X
/run-checks BE-00X
/update-docs BE-00X
/final-gate BE-00X
```

Notas:
- `/plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, normaliza el mismo indice y nunca implementa codigo.
- Todos los IDs producen un unico plan canonico `docs/opencode/plans/BE-00X-plan.md`.
- El planner tambien debe crear o actualizar `US-00X`, `UIA-00X` y `APIA-00X`.
- Los planes nuevos usan schema v3 y se validan con `backend/scripts/validate_slice_plan.py`.
- Los planes schema v2 son legacy: deben regenerarse con `/plan-task` antes de implementarse.
- `/plan-task` y `/qa-task` validan primero el contrato vigente y tratan artefactos desactualizados o entornos rotos como insumos de reparacion, no como estado final.
- `/qa-task` intenta autorecuperar dependencias y contexto Docker antes de bloquearse.
- Los agentes de UI y API automation validan el plan con stage `qa` y usan Docker cuando el slice depende de PostgreSQL o del runtime del repo.
- Cuando Docker aplica al cierre, todos los contenedores relevantes deben quedar actualizados o recreados y saludables antes de reportar cierre.
- Los stages de cierre `review`, `checks` y `docs` no aceptan tareas aplicables abiertas; solo `Estado: CANCELLED` con evidencia verificable puede quedar exento.
- Los artefactos operativos se escriben en UTF-8.
- Implementadores, automatizaciones y gates tecnicos aceptan aliases BE/FE/QA del mismo indice; la cadena usa BE como entrada uniforme y QA conserva `/qa-task QA-00X`.
- `/plan-task` crea plan, `US/UIA/APIA` y los cinco manifiestos; los demas agentes solo regeneran y verifican esas vistas derivadas.
- En VS Code, `.vscode/settings.json` limita cada ejecucion a 50 solicitudes y `.github/copilot-instructions.md` exige un solo modelo, checkpoints y corte cerca de 48,000 tokens de contexto.
- `/final-gate` es obligatorio despues de actualizar documentacion.
- Para implementar frontend usa `/implement-frontend-task BE-00X`.
- `/implement-backend-task` ejecuta internamente las validaciones tecnicas de backend y persistencia que correspondan; no se agrega un script Python como fase del flujo del usuario.
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
- `02_be_fe_qa_task_matrix.md`: matriz US/BE/FE/QA/UIA/APIA.
- `03_task_prompt_contracts.md`: contrato de prompts por comando.
- `04_agent_contracts.md`: responsabilidades de agentes.
- `05_done_gates_by_command.md`: gates de cierre.
- `11_chatgpt_project_context.md`: contexto consolidado para usar el proyecto en ChatGPT.
- `12_troubleshooting_skills_vs_agents.md`: solucion al error de confundir skills Codex con agentes OpenCode.
- `13_agents_architecture_and_gate_flow.md`: arquitectura agentica y continuidad de gates.
- `14_github_copilot_agentic_flow.md`: version del flujo compatible con GitHub Copilot.
- `templates`: plantillas Markdown para resultados, hallazgos y correcciones.
- `templates/slice_plan_template.md`: contrato obligatorio de planes schema v3.
- `templates/carryovers_registry_template.md`: plantilla para registrar tareas postergadas o transferidas.
- `templates/missing_artifact_generation_template.md`: solicitud reusable para regenerar artefactos canonicos faltantes.
- `references/spec_kit_reference_improvements.md`: adaptacion de aprendizajes de `github/spec-kit` al flujo agentico InVet.
- `references/carryovers_governance.md`: reglas para tareas postergadas y cierres cruzados entre slices.
- `references/slice_task_context.md`: brief por slice con titulo, descripcion, entregables BE/FE y foco de aceptacion QA.
- `references/missing_artifact_generation.md`: procedimiento para migrar backups legacy de `payload/` a artefactos canonicos validos.
- `tasks/backend`: tareas backend.
- `tasks/frontend`: tareas frontend.
- `tasks/qa`: tareas QA.
- `tasks/user-stories`: historias de usuario y criterios `CA-NN`.
- `tasks/ui-automation`: tareas UI automation.
- `tasks/api-automation`: tareas API automation.
- `references`: reglas de alcance, diseno, arquitectura y seguridad.
