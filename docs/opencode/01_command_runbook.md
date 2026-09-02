# 01 - Runbook de comandos secuenciales

## Secuencia obligatoria

La forma recomendada es:

```text
/execute-slice BE-001
```

La secuencia manual equivalente es:

```text
/plan-task BE-001
/implement-backend-task BE-001
/implement-frontend-task BE-001
/implement-ui-automation-task BE-001
/implement-api-automation-task BE-001
/qa-task QA-001
/review-slice BE-00X
/clean-architecture-review BE-001
/security-review BE-001
/run-ui-checks BE-001
/run-checks BE-001
/update-docs BE-001
/final-gate BE-001
```

## Runtime y rutas canónicas

- Para levantar el stack completo del repositorio usa:

  ```text
  docker compose up -d --build --force-recreate db backend frontend
  ```

- Frontend base: `http://localhost:3000`
- Backend base: `http://localhost:8000`
- API base: `/api/v1`
- UI pública de clínicas: `http://localhost:3000/clinicas`
- La UI pública de clínicas se implementa en `frontend/src/app/clinicas/page.tsx` y el detalle en `frontend/src/app/clinicas/[clinicId]/page.tsx`.
- UI de citas del propietario: `http://localhost:3000/portal/owner/appointments`
- UI de alta de cita: `http://localhost:3000/portal/owner/appointments/new`
- UI de agenda clínica: `http://localhost:3000/clinic/appointments`
- API pública de clínicas: `http://localhost:8000/api/v1/clinicas`
- API de citas: `http://localhost:8000/api/v1/appointments`
- Los endpoints de BE-008 se implementan en `backend/app/api/v1/routers/appointment_router.py` y sus schemas canónicos viven en `backend/app/api/v1/schemas/appointment_schemas.py`.
- Las regresiones UI y Playwright deben validar sobre `http://localhost:3000`; no deben apuntar al backend directo para simular navegación de navegador.

## Comandos canónicos por contexto

| Comando | Cuándo usarlo | Qué debe quedar claro en la evidencia |
|---|---|---|
| `docker compose up -d --build --force-recreate db backend frontend` | Cargar el entorno completo antes de implementación, QA o regresión | Que el stack quedó arriba con `db`, `backend` y `frontend` saludables |
| `docker compose up -d db` | Solo cuando se necesita persistencia o pruebas con PostgreSQL | Que la DB quedó disponible para el backend o para una corrida puntual |
| `docker compose run --rm backend pytest ...` | Pruebas backend que requieren el contenedor y la base de datos | Que la suite corrió dentro del runtime correcto |
| `/run-ui-checks BE-00X` | Regresión UI contra `db`, `backend` y `frontend` de Docker Compose | Que la UI se validó sobre el puerto publicado de `frontend` con `PLAYWRIGHT_START_FRONTEND=false` |
| `/run-checks BE-00X` | Checks técnicos y reejecución API contra Docker | Que `npm run test:api` apuntó al backend publicado por Docker y dejó trazabilidad |
| `/qa-task QA-00X` | Validación QA formal del slice | Que QA valida el flujo extremo a extremo con URLs y endpoints canónicos |

- Para FE-008, la ruta canónica de validación UI es `http://localhost:3000`.
- Para BE-008, la ruta canónica de API es `http://localhost:8000/api/v1` y el router vive en `backend/app/api/v1/routers/appointment_router.py`.
- Para QA-008, la evidencia debe nombrar explícitamente `http://localhost:3000`, `http://localhost:8000` y las rutas `/api/v1/clinicas` y `/api/v1/appointments`.
- UI/API automation no admite fallback host. Si Docker no esta disponible, el comando responsable termina `BLOCKED` y se reanuda con el mismo comando cuando el entorno se recupere.

## Reglas

0. En Windows PowerShell 5.1 no encadenes comandos con `&&`: configura el
   directorio de trabajo `C:\InVet` directamente en la herramienta y ejecuta
   cada comando por separado. Para fail-fast usa
   `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`. Esta regla aplica a todos
   los agentes y especialmente a los gates de review.

1. `plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, informa la normalizacion y conserva el mismo indice vertical.
2. `plan-task` genera un unico `docs/opencode/plans/BE-00X-plan.md` schema v3 con contrato frontend, trazabilidad, Docker, UTF-8 y tareas atomicas.
   Nunca implementa codigo de backend ni frontend.
   Ademas crea o actualiza `US-00X`, `UIA-00X` y `APIA-00X`, renderiza los cinco manifiestos y verifica sus hashes. Ningun otro agente decide su alcance.
3. Cada comando mutable ejecuta `backend/scripts/validate_slice_plan.py` antes de editar.
4. Backend y frontend implementan sus pruebas unitarias y registran evidencia por tarea.
5. `implement-ui-automation-task` acepta cualquier prefijo del mismo slice, consume el manifiesto UIA verificado, implementa E2E en `InVet_UI_Automation/tests/e2e` y ejecuta contra el stack Docker con el frontend local de Playwright desactivado.
6. `implement-api-automation-task` acepta cualquier prefijo del mismo slice, consume el manifiesto APIA verificado, implementa pruebas HTTP en `InVet_UI_Automation/tests/api` y ejecuta contra el backend Docker.
7. `qa-task` recibe el ID QA equivalente `QA-00X`, valida usando objetivos y criterios del plan, y marca tareas QA o de validacion completadas.
8. `qa-task` documenta evidencia, rechaza gaps unitarios y no repara pruebas unitarias de producto.
9. Si una corrida necesita PostgreSQL, el flujo canonico es levantar `docker compose up -d db` y ejecutar la suite dentro del contenedor de backend con `docker compose run --rm backend pytest ...`; la ejecucion en host solo es fallback documentado cuando Docker no esta disponible. Antes de cerrar QA o checks, confirmar que los contenedores Docker aplicables fueron actualizados o recreados cuando correspondia.
10. `review-slice` acepta `BE-00X` o `FE-00X` y siempre deja `docs/opencode/reviews/BE-00X-review.md` con decision.
11. `clean-architecture-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-clean-architecture-review.md`.
12. `security-review BE-00X` siempre deja `docs/opencode/reviews/BE-00X-security-review.md`.
13. `run-ui-checks BE-00X|FE-00X|QA-00X` ejecuta `npm run test:e2e` y `npm run test:regression` contra los servicios Docker; `/run-checks` reejecuta `npm run test:api` contra el mismo stack.
14. `implement-findings` acepta `BE-00X` o `FE-00X`, toma el reporte de hallazgos, el archivo de bloqueo de QA o los archivos de review del slice y cierra correcciones sobre el mismo slice vertical.
15. `/implement-findings` deja findings QA en `READY_FOR_REVALIDATION`; QA es el unico que puede declarar `RESOLVED`.
16. Las revisiones reciben un ID explicito y siempre escriben decision `APPROVED|REJECTED`.
17. `run-checks BE-00X` deja evidencia Markdown antes de `update-docs BE-00X`.
18. `final-gate BE-00X` es obligatorio, usa el modelo seleccionado y deja el reporte final de release.
19. Si una tarea se posterga o se transfiere desde otro slice, registrar el carryover en `docs/opencode/carryovers/BE-00X-carryovers.md`, reflejar la misma evidencia en el plan origen y el destino, y validar el registro antes de aprobar `qa`, `review`, `checks` o `docs`.

## Ejemplo: busqueda publica

```text
/plan-task BE-003
/implement-backend-task BE-003
/implement-frontend-task BE-003
/implement-ui-automation-task BE-003
/implement-api-automation-task BE-003
/qa-task QA-003
/review-slice BE-003
/implement-findings BE-003
/qa-task QA-003
/clean-architecture-review BE-003
/security-review BE-003
/run-ui-checks BE-003
/run-checks BE-003
/update-docs BE-003
/final-gate BE-003
```

## Resultado esperado por slice

- Plan de implementacion generado en `docs/opencode/plans/BE-00X-plan.md`.
- Historias `US-00X` y coberturas `UIA-00X` / `APIA-00X` actualizadas.
- Codigo backend implementado o explicitamente no requerido.
- Codigo frontend implementado o explicitamente no requerido.
- Checklist del plan actualizado con tareas completadas verificadas.
- QA ejecutado con evidencia trazada por tarea.
- Hallazgos revisados o cerrados si aplicaba.
- Revision arquitectura aprobada.
- Revision seguridad aprobada.
- Checks verdes o fallos documentados.
- Documentacion actualizada.
- Gate final de release aprobado cuando se active.
