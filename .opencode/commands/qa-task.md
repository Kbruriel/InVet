---
description: Ejecuta QA funcional y tecnico para una tarea QA InVet con evidencia reproducible y gates objetivos.
agent: invet-qa-validator
---

Valida la tarea QA indicada por `$ARGUMENTS`.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, hay una decision critica de aceptacion/alcance o se requiere una accion destructiva.
0.1. Modo compatibilidad: ejecuta los pasos de forma secuencial. No uses llamadas paralelas para leer archivos ni una herramienta llamada `python`; cuando necesites Python, usalo como comando de terminal, por ejemplo `python backend/scripts/validate_slice_plan.py ...`.
1. Normaliza el argumento a `QA-00X` e identifica `BE-00X` y `FE-00X`.
2. Ejecuta `python backend/scripts/validate_slice_plan.py QA-00X --stage qa`.
   - Si falla, no intentes validar criterios ambiguos; documenta `BLOCKED` por contrato de plan, marca cualquier `docs/opencode/qa/QA-00X-results.md` previo como baseline stale y crea o actualiza `docs/opencode/qa/QA-00X-findings.md` con evidencia concreta del preflight.
   - Si el archivo roto es `docs/opencode/plans/BE-00X-plan.md`, solicita `/plan-task BE-00X` como correccion canonica del slice.
   - Si faltan dependencias o el entorno no levanta, intenta recuperarlo antes de bloquearte: instala dependencias y usa Docker cuando el slice dependa de PostgreSQL o del runtime del repo.
   - La UI de validacion corre sobre `http://localhost:3000`.
   - La API del slice corre sobre `http://localhost:8000/api/v1`.
3. Lee:
   - `docs/opencode/plans/BE-00X-plan.md`
   - `docs/opencode/tasks/qa/QA-00X.md`
   - `docs/opencode/tasks/backend/BE-00X.md`
   - `docs/opencode/tasks/frontend/FE-00X.md`
   - `docs/opencode/references/slice_task_context.md`
4. Antes de declarar bloqueo por infraestructura:
   - valida dependencias del backend;
   - ejecuta `python backend/scripts/prepare_qa_env.py --install-deps` desde la raiz o `python scripts/prepare_qa_env.py --install-deps` desde `backend/` si faltan dependencias, `.env.qa` o una base utilizable;
   - usa `python -m pip install -e .[dev]` o `backend/requirements.txt` como fallback de instalacion cuando haga falta;
   - prefiere `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/invet` y ejecutar las pruebas dentro del contenedor de backend cuando el slice requiera base de datos;
   - levanta PostgreSQL con `docker compose up -d db` antes de la suite cuando la validacion dependa de persistencia;
   - ejecuta la suite de backend con `docker compose run --rm backend pytest app/tests/ -q` o una ruta puntual equivalente, nunca como sustituto en el host si el slice requiere Docker;
   - si el backend ya esta vivo y la suite necesita el mismo contenedor, `docker compose exec backend ...` es valido;
   - si `backend/app/tests/conftest.py` reinicia o elimina tablas, no ejecutes una suite destructiva contra la misma base usada por el stack levantado sin aislar antes una base o schema de pruebas;
    - trata el contenedor de `frontend` como runtime por defecto: no asumas que sirve para pruebas sin un flujo de testing explicito.
    - usa los contenedores de backend cuando la suite requiera PostgreSQL en Docker.
   - antes de bloquear o aprobar, confirma que todos los contenedores Docker aplicables fueron actualizados o recreados y quedaron saludables; si no aplican cambios relevantes, registra el skip con causa exacta.
5. Usa los `Objetivo` y `Criterios de aceptacion` de cada tarea del plan para derivar una matriz de trazabilidad por criterio:
   - historia o criterio
   - responsabilidad unica
   - contexto necesario
   - contratos usados
   - resultado esperado
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
17. Crea `docs/opencode/qa/QA-00X-findings.md` con `- Estado global: OPEN` cuando existan findings; `/implement-findings` lo mueve a `READY_FOR_REVALIDATION` y solo una nueva corrida QA puede marcarlo `RESOLVED`.
    - Si la revalidacion confirma que todos los findings quedaron corregidos o aceptados formalmente, actualiza el estado global a `RESOLVED` o `ACCEPTED_RISK`.
    - Si queda cualquier finding `OPEN`, `IN_PROGRESS` o `READY_FOR_REVALIDATION`, el estado global debe seguir bloqueante.
18. No declares el slice listo mientras QA no sea `APPROVED` o existan findings no resueltos.
19. Escribe resultados, findings y outcomes en UTF-8. Rechaza evidencia nueva con mojibake como `Ãƒ`, `Ã‚` o `Ã¢`.
20. Cierra siempre con `Estado de ejecucion: APPROVED|REJECTED|BLOCKED` antes de `Siguiente paso recomendado`.
21. `READY_FOR_REVALIDATION` no es un estado de cierre de QA; pertenece al lifecycle de findings.
22. Si los findings siguen `READY_FOR_REVALIDATION`, refleja el bloqueo real y deriva al flujo de correcciones; no ordenes un auto-rerun de QA como unico desbloqueo.

Hook de cierre:
- Si QA termina en `APPROVED`, Docker Compose esta disponible y el usuario no pidiÃ³ omitirlo, primero validar si existen cambios pendientes que afecten `backend`, `frontend`, `docker-compose.yml`, `Dockerfile*`, `backend/requirements.txt`, `backend/pyproject.toml`, `frontend/package.json` o lockfiles.
- Si Docker Compose se ejecuta, confirmar que los contenedores aplicables quedaron actualizados o recreados antes de reportar el cierre.
- Si no existen cambios pendientes que requieran actualizar contenedores, registrar el skip con la causa exacta y no ejecutar el restart.
- Si existen cambios pendientes, ejecutar `docker compose up -d --build --force-recreate db backend frontend`.
- Si Docker Compose no esta disponible o QA no fue aprobado, registrar el skip con la causa exacta.
Cierre obligatorio:
- Al cerrar, reporta siempre Siguiente paso recomendado con el comando exacto segun el estado final del gate.
- Solo recomienda `/review-slice BE-00X` cuando `docs/opencode/qa/QA-00X-results.md` termine con `Decision: APPROVED` y `QA-00X-findings.md` no exista o tenga estado global `RESOLVED`/`ACCEPTED_RISK`.
- Si QA queda `REJECTED` o hay findings `OPEN`/`IN_PROGRESS`/`READY_FOR_REVALIDATION`, recomienda `/implement-findings BE-00X`; no recomiendes review ni un rerun auto-referencial de QA.
- Si el bloqueo es de contrato de plan o artefacto faltante, recomienda `/plan-task BE-00X`.
- Si hubo findings, agrega Comando recomendado para resolver hallazgos con el comando exacto que sigue en el flujo.
- Si hubo bloqueo, agrega Comando recomendado para desbloquear el gate con el comando exacto que destraba la ejecucion.
- Usa la tabla de continuidad definida en docs/opencode/13_agents_architecture_and_gate_flow.md para decidir la recomendacion correcta y explicar el motivo.
