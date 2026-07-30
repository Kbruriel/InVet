---
description: Ejecuta checks backend/frontend disponibles, corrige fallos si se solicita y resume resultados.
agent: invet-check-runner
---

Ejecuta los checks tecnicos disponibles del repositorio y reporta pass/fail/skipped.

Estrategia:
0. Antes de correr nada, verifica que el interprete Python seleccionado tenga instaladas las dependencias de backend declaradas en `backend/requirements.txt`.
   - Si faltan `pytest`, `ruff`, `black` o `mypy`, reporta el bloqueo con la causa exacta y la instruccion de instalacion.
   - Prioriza un entorno local ya preparado, como `backend/.venv` o `.venv`, si existe.
1. Ejecuta de forma autonoma los checks configurados. Pregunta al usuario solo si falta informacion bloqueante, se requiere Docker/servicios externos o una decision critica.
2. Detectar estructura del repo y herramientas configuradas antes de ejecutar.
3. Backend:
   - Entrar a `backend/` si existe.
   - Ejecutar `python -W ignore::PendingDeprecationWarning -m pytest app/tests -q`.
   - Ejecutar `python -m ruff check .`.
   - Ejecutar `python -m black --check .`.
   - Ejecutar `python -m mypy app` si `mypy.ini` o configuracion equivalente existe.
4. Frontend:
   - Ejecutar checks solo si existe `frontend/package.json`.
   - Usar el gestor detectado por lockfile: pnpm, npm o yarn.
   - Ejecutar lint, typecheck, test y build solo si el script existe.
5. DevOps:
   - Docker Compose es opcional y solo se ejecuta con entorno/configuracion disponible y permiso explicito.
6. Reportar comandos ejecutados, resultado, skips justificados y warnings relevantes.

Modo correccion:
- Por defecto, `/run-checks` solo reporta resultados.
- Si el usuario pide explicitamente corregir/solucionar/fix errors, se pueden modificar archivos para reparar fallos de configuracion, formato, lint, tipos o tests.
- Despues de cualquier cambio, rerunear los checks afectados y dejar evidencia del resultado final.
