---
description: Ejecuta QA funcional y tecnico para una tarea QA InVet con evidencia reproducible y gates objetivos.
agent: invet-qa-validator
---

Valida la tarea QA indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de aceptacion/alcance o se requiere una accion destructiva.
1. Normaliza el argumento a `QA-00X` e identifica `BE-00X` y `FE-00X`.
2. Ejecuta `python backend/scripts/validate_slice_plan.py QA-00X --stage qa`.
   - Si falla, no intentes validar criterios ambiguos; documenta `BLOCKED` por contrato de plan y solicita `/plan-task QA-00X`.
3. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
4. Antes de declarar bloqueo por infraestructura:
   - valida dependencias del backend;
   - ejecuta `python backend/scripts/prepare_qa_env.py --install-deps` desde la raiz o `python scripts/prepare_qa_env.py --install-deps` desde `backend/` si faltan dependencias, `.env.qa` o una base utilizable;
   - usa `python -m pip install -e .[dev]` o `backend/requirements.txt` como fallback de instalacion cuando haga falta;
   - prefiere `DATABASE_URL=sqlite:///./qa-test.db` o los fixtures SQLite en memoria cuando el slice no requiera un servicio externo real.
5. Usa los `Objetivo` y `Criterios de aceptacion` de cada tarea del plan para derivar una matriz de trazabilidad por criterio:
   - criterio
   - riesgo
   - caso de prueba
   - nivel de prueba
   - suite o archivo
   - comando ejecutado
   - resultado
   - evidencia
   - estado (`PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`)
6. Si ya existe `docs/opencode/qa/QA-00X-results.md`, auditalo antes de reutilizarlo:
   - invalida conclusiones historicas si el plan actual, `git diff`, `git status` o el filesystem muestran que el slice cambio desde esa corrida;
   - no conserves `NOT_APPLICABLE` para frontend cuando existe `frontend/package.json`, el plan marca tareas FE como `- [x]` o `run-checks` ya ejecuta scripts frontend;
   - reescribe la evidencia stale para que el resultado final refleje solo la corrida actual.
7. Revisa `git status`, `git diff` y los archivos afectados para definir regresion por impacto.
8. Inventaria archivos productivos y mapealos contra pruebas unitarias explicitas.
9. Si un archivo queda sin prueba unitaria, marca el criterio en `FAIL`, crea un finding `OPEN`, emite `REJECTED` y deriva la correccion al implementador o `/implement-findings`; QA no implementa esa prueba.
10. Verifica que las tareas `- [x]` tengan `Evidencia` suficiente.
11. Disena o ajusta pruebas QA de aceptacion, integracion, contrato, seguridad, regresion y modelos/datos; no uses QA para reparar cobertura unitaria de producto.
12. Ejecuta las pruebas relevantes y genera reportes machine-readable cuando sea posible.
13. Valida descubrimiento y ejecucion real y rechaza evidencia stale o vacia.
14. Emite una decision final objetiva:
   - `APPROVED` solo si todos los criterios aplicables estan en `PASS`, la regresion relevante pasa y no hay defects `blocker` o `critical`.
   - `REJECTED` si existe un `FAIL` relevante, una regresion nueva, una vulnerabilidad, exposicion de datos o gaps de pruebas unitarias en archivos productivos del slice.
   - `BLOCKED` si el entorno o la evidencia del runner no permiten una decision confiable.
15. Marca tareas QA `- [x]` solo con estado `PASS` y sustituye `Evidencia: pending`.
16. Documenta trazabilidad, reportes, defects, gate unitario y decision final.
17. Crea `docs/opencode/qa/QA-00X-findings.md` con estado `OPEN`; `/implement-findings` lo mueve a `READY_FOR_REVALIDATION` y solo una nueva corrida QA puede marcarlo `RESOLVED`.
18. No declares el slice listo mientras QA no sea `APPROVED` o existan findings no resueltos.
