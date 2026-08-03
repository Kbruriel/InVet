---
description: Ejecuta checks backend/frontend disponibles, corrige fallos si se solicita y resume resultados.
agent: invet-check-runner
---

Ejecuta los checks tecnicos disponibles del repositorio y reporta pass/fail/skipped.

Estrategia:
0. Si `$ARGUMENTS` contiene `BE-00X`, `FE-00X` o `QA-00X`, normaliza el slice y ejecuta `python backend/scripts/validate_slice_plan.py BE-00X --stage checks`.
   - Si falla, reporta el gate y no declares checks finales del slice.
   - Sin argumento puedes ejecutar diagnostico tecnico, pero no cerrar un slice.
1. Antes de correr nada, verifica que el interprete Python seleccionado tenga instaladas las dependencias de backend declaradas en `backend/requirements.txt`.
   - Si faltan `pytest`, `ruff`, `black` o `mypy`, reporta el bloqueo con la causa exacta y la instruccion de instalacion.
   - Prioriza un entorno local ya preparado, como `backend/.venv` o `.venv`, si existe.
2. Ejecuta de forma autonoma los checks configurados. Pregunta al usuario solo si falta informacion bloqueante, se requiere Docker/servicios externos o una decision critica.
3. Detectar estructura del repo y herramientas configuradas antes de ejecutar.
4. Backend:
   - Entrar a `backend/` si existe.
   - Ejecutar `python -W ignore::PendingDeprecationWarning -m pytest app/tests -q`.
   - Ejecutar `python -m ruff check .`.
   - Ejecutar `python -m black --check .`.
   - Ejecutar `python -m mypy app` si `mypy.ini` o configuracion equivalente existe.
5. Frontend:
   - Ejecutar checks solo si existe `frontend/package.json`.
   - Usar el gestor detectado por lockfile: pnpm, npm o yarn.
   - Ejecutar lint, typecheck, test y build solo si el script existe.
6. DevOps:
   - Docker Compose es opcional y solo se ejecuta con entorno/configuracion disponible y permiso explicito.
   - Si todos los checks aplicables pasan, primero validar si `git status` muestra cambios pendientes relevantes para `backend`, `frontend`, `docker-compose.yml`, `Dockerfile*` o lockfiles/manifiestos de dependencias.
   - Si no hay cambios pendientes relevantes, registrar el skip y no reiniciar contenedores.
   - Si hay cambios pendientes relevantes, cerrar con el hook `docker compose up -d --build --force-recreate db backend frontend`.
7. Reportar comandos ejecutados, resultado, skips justificados y warnings relevantes.
8. Cuando recibas un ID de slice, crea `docs/opencode/checks/BE-00X-checks.md` usando `docs/opencode/templates/checks_results_template.md`.
   - Usa `Decision: APPROVED` solo si todos los checks aplicables pasan y cada skip es realmente no aplicable.
   - Usa `Decision: REJECTED` si cualquier check aplicable falla o queda bloqueado.

Modo correccion:
- Por defecto, `/run-checks` solo reporta resultados.
- Si el usuario pide explicitamente corregir/solucionar/fix errors, se pueden modificar archivos para reparar fallos de configuracion, formato, lint, tipos o tests.
- Despues de cualquier cambio, rerunear los checks afectados y dejar evidencia del resultado final.
- Cuando la corrida termine sin fallos, ejecutar el hook de Docker Compose de cierre antes de reportar la decision final.
