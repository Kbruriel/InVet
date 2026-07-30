---
description: Ejecuta QA funcional y tecnico para una tarea QA InVet con evidencia reproducible y gates objetivos.
agent: invet-qa-validator
---

Valida la tarea QA indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de aceptacion/alcance o se requiere una accion destructiva.
1. Normaliza el argumento a `QA-00X` e identifica `BE-00X` y `FE-00X`.
2. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
3. Antes de declarar bloqueo por infraestructura:
   - valida dependencias del backend;
   - ejecuta `python backend/scripts/prepare_qa_env.py --install-deps` desde la raiz o `python scripts/prepare_qa_env.py --install-deps` desde `backend/` si faltan dependencias, `.env.qa` o una base utilizable;
   - usa `python -m pip install -e .[dev]` o `backend/requirements.txt` como fallback de instalacion cuando haga falta;
   - prefiere `DATABASE_URL=sqlite:///./qa-test.db` o los fixtures SQLite en memoria cuando el slice no requiera un servicio externo real.
4. Usa los `Objetivo` y `Criterios de aceptacion` de cada tarea del plan para derivar una matriz de trazabilidad por criterio:
   - criterio
   - riesgo
   - caso de prueba
   - nivel de prueba
   - suite o archivo
   - comando ejecutado
   - resultado
   - evidencia
   - estado (`PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`)
5. Si ya existe `docs/opencode/qa/QA-00X-results.md`, auditalo antes de reutilizarlo:
   - invalida conclusiones historicas si el plan actual, `git diff`, `git status` o el filesystem muestran que el slice cambio desde esa corrida;
   - no conserves `NOT_APPLICABLE` para frontend cuando existe `frontend/package.json`, el plan marca tareas FE como `- [x]` o `run-checks` ya ejecuta scripts frontend;
   - reescribe la evidencia stale para que el resultado final refleje solo la corrida actual.
6. Revisa `git status`, `git diff` y los archivos afectados para definir regresion por impacto antes de ejecutar suites costosas.
7. Verifica que las tareas backend/frontend marcadas como `- [x]` tengan evidencia suficiente contra sus criterios de aceptacion; no des por cubierto un criterio solo porque existe una prueba parecida.
8. Disena o ajusta pruebas automatizadas necesarias para cubrir criterios de aceptacion no cubiertos, priorizando unitarias, integracion, contrato, seguridad, frontend y modelos/datos segun el cambio.
9. Ejecuta las pruebas relevantes y, cuando el tooling lo permita, genera reportes machine-readable (`JUnit XML`, JSON, cobertura XML/LCOV).
10. Valida que las pruebas realmente fueron descubiertas y ejecutadas; registra codigo de salida, recolectadas, ejecutadas, pass/fail/error/skip/xfail/xpass, duracion, timestamp y archivo de reporte. Rechaza evidencia vacia, vieja o inconsistente.
11. Emite una decision final objetiva:
   - `APPROVED` solo si todos los criterios aplicables estan en `PASS`, la regresion relevante pasa y no hay defects `blocker` o `critical`.
   - `REJECTED` si existe un `FAIL` relevante, una regresion nueva, una vulnerabilidad o exposicion de datos.
   - `BLOCKED` si el entorno o la evidencia del runner no permiten una decision confiable.
12. Marca como completadas en `docs/opencode/plans/BE-00X-plan.md` solo las tareas QA o de validacion cuyo criterio asociado este en `PASS`, con evidencia enlazada, pruebas ejecutadas y sin blocker asociado.
13. Documenta trazabilidad por tarea, comandos, resultados esperados vs obtenidos, coverage, baseline, defects y decision final en `docs/opencode/qa/QA-00X-results.md` usando `docs/opencode/templates/qa_results_template.md`.
14. Solo si la auto-recuperacion del entorno falla o si la suite depende de un servicio externo no mockeable, crea `docs/opencode/qa/QA-00X-findings.md` siguiendo `docs/opencode/templates/qa_findings_template.md` para que luego lo consuma `/implement-findings`.
