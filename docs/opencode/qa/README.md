# QA Command Runbook

Este archivo es la referencia canonica para ejecutar QA en InVet.
Su objetivo es evitar confusiones entre el ID del slice, el comando de QA y
los artefactos que deben revisarse antes de validar un cambio.

## Comando canonico

- Comando principal: `/qa-task QA-00X`
- El ID de QA siempre usa el mismo indice que el slice backend/frontend:
  - `BE-007` -> `QA-007`
  - `FE-007` -> `QA-007`
- No uses `/review-slice QA-00X`; para ese caso existe `/qa-task QA-00X`.

## Archivos que QA debe leer

1. `docs/opencode/plans/BE-00X-plan.md`
2. `docs/opencode/tasks/qa/QA-00X.md`
3. `docs/opencode/tasks/backend/BE-00X.md`
4. `docs/opencode/tasks/frontend/FE-00X.md`
5. `docs/opencode/references/slice_task_context.md`

## Secuencia recomendada

1. Validar el plan antes de evaluar el slice:

   ```text
   python backend/scripts/validate_slice_plan.py QA-00X --stage qa
   ```

2. Intentar recuperacion automatica del entorno si faltan dependencias o
   configuracion:

   ```text
   python backend/scripts/prepare_qa_env.py --install-deps
   ```

3. Si el slice usa base de datos, levantar PostgreSQL:

   ```text
   docker compose up -d db
   ```

4. Ejecutar la suite relevante de backend dentro del contenedor cuando el
   slice dependa de PostgreSQL:

   ```text
   docker compose run --rm backend pytest app/tests/ -q
   ```

5. Ejecutar la validacion frontend o los checks necesarios segun el alcance
   del slice.

6. Registrar evidencia en:
   - `docs/opencode/qa/QA-00X-results.md`
   - `docs/opencode/qa/QA-00X-findings.md` cuando existan hallazgos abiertos

## Decision y siguiente paso

- `APPROVED` -> siguiente paso: `/review-slice BE-00X`
- `REJECTED` -> siguiente paso: `/implement-findings BE-00X`
- `BLOCKED` -> siguiente paso:
  - `/plan-task BE-00X` si falta contrato, artefacto o el plan esta roto
  - recuperar dependencias y repetir QA si el bloqueo es de entorno

## Reglas rapidas

- `QA-00X` es el ID de validacion.
- `BE-00X` es el ID del plan canonico.
- `FE-00X` comparte el mismo indice vertical.
- QA no corrige pruebas unitarias de producto.
- QA no debe aprobar si hay findings abiertos o evidencia stale.

## Referencias

- `docs/opencode/01_command_runbook.md`
- `docs/opencode/03_task_prompt_contracts.md`
- `docs/opencode/05_done_gates_by_command.md`
- `docs/opencode/13_agents_architecture_and_gate_flow.md`
