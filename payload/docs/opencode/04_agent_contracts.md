# 04 - Agent Contracts

## Contrato comun

- `US-00X`, `BE-00X`, `FE-00X`, `QA-00X`, `UIA-00X` y `APIA-00X` representan un unico slice vertical.
- El plan canonico es `docs/opencode/plans/BE-00X-plan.md`.
- Los agentes intercambian estado mediante Markdown versionado, no memoria implicita.
- Cada comando mutable ejecuta `backend/scripts/validate_slice_plan.py`.
- Los planes nuevos usan `schema_version: 3` y declaran `encoding: UTF-8`.
- Todas las redacciones, comentarios, evidencias y outcomes operativos se escriben en UTF-8.
- Las tareas mecanicas de ejecucion pueden delegarse a `invet-command-executor` para conservar el razonamiento en el agente de dominio.
- Una tarea completada requiere criterios verificados y `Evidencia` reproducible.
- Un gate fallido detiene el flujo; no se convierte en `skipped`.
- Cada tarea debe tener responsabilidad unica, tipo declarado, contexto necesario, contratos usados y resultado esperado.
- Los agentes de implementacion deben rechazar tareas compuestas en lugar de reinterpretarlas.
- Cada agente debe cerrar con `Estado de ejecucion`, `Siguiente paso recomendado` y, cuando aplique, `Comando recomendado para resolver hallazgos` o `Comando recomendado para desbloquear el gate`.
- El `Estado de ejecucion` debe usar el vocabulario permitido por la familia del agente y no mezclarlo con el estado de findings.
- Los agentes no deben afirmar que un comando es "el unico" que desbloquea el slice; deben declarar el estado actual, el bloqueo real y el siguiente gate verificable.
- El frontend de validacion corre por defecto en `http://localhost:3000` y el backend en `http://localhost:8000` con API bajo `/api/v1`.
- Las rutas y archivos canónicos del producto deben quedar explicitados en los artefactos de cada slice: `backend/app/api/v1/routers/*.py`, `backend/app/api/v1/schemas/*.py`, `frontend/src/app/**`, `frontend/src/features/**` y `src/shared/api`.
- La UI pública de clínicas vive en `frontend/src/app/clinicas/page.tsx` y responde en `http://localhost:3000/clinicas`.
- Para BE-008, el router canónico es `backend/app/api/v1/routers/appointment_router.py` y la UI canónica vive en `frontend/src/app/portal/owner/appointments`, `frontend/src/app/portal/owner/appointments/new` y `frontend/src/app/clinic/appointments`.

## Gobernanza de carryovers

- Cuando una tarea se posterga por una razon justificada, el agente responsable debe registrar el carryover en `docs/opencode/carryovers/BE-00X-carryovers.md`.
- Usa `docs/opencode/templates/carryovers_registry_template.md` como base del registro para no improvisar columnas ni estados.
- Si una tarea proviene de otro slice, el cierre debe quedar reflejado tanto en el plan destino como en el plan origen con la misma evidencia o con una referencia explicita al cierre.
- Un carryover no se considera resuelto si el plan origen, el plan destino y el registro no coinciden.
- QA, reviewers, docs y final gate deben bloquear slices con carryovers abiertos, desalineados o sin evidencia reproducible.
- `backend/scripts/validate_slice_plan.py --stage qa|review|checks|docs` aplica esa regla de forma deterministica.
- Los stages de trabajo `plan`, `backend`, `frontend`, `qa` y `findings` permiten tareas abiertas segun la etapa. Los stages de cierre `review`, `checks` y `docs` bloquean cualquier tarea aplicable en `- [ ]`.
- Una tarea abierta solo queda exenta del cierre si declara `Estado: CANCELLED` y evidencia verificable; texto informal, `pending`, `N/A`, `OPEN` o `TRANSFERRED` no justifican el cierre.

## Responsabilidades

| Agente | Responsabilidad | Gate o salida |
| --- | --- | --- |
| `invet-orchestrator` | Ejecuta el slice completo y evita saltar etapas | Bloquea ante plan invalido, QA no aprobado, findings abiertos, reviews o checks rechazados |
| `invet-product-planner` | Acepta IDs BE/FE/QA, crea el plan vertical schema v3 y actualiza `US/UIA/APIA` | `BE-00X-plan.md` validado y sidecars actualizados |
| `invet-backend-implementer` | Implementa tareas `Capa: backend` y sus pruebas unitarias | Criterios, validacion y evidencia por tarea |
| `invet-frontend-implementer` | Implementa el contrato frontend y sus pruebas unitarias/de componente | Criterios, validacion y evidencia por tarea |
| `invet-ui-automation-implementer` | Implementa E2E, formularios, navegacion, redirects y estados UI con Playwright | `UIA-00X.md` con cobertura y evidencia |
| `invet-api-automation-implementer` | Implementa validacion HTTP externa con Playwright `APIRequestContext` | `APIA-00X.md` con cobertura y evidencia |
| `invet-qa-validator` | Valida aceptacion, integracion, contrato, seguridad y regresion | `QA-00X-results.md` y decision `APPROVED|REJECTED|BLOCKED` |
| `invet-slice-reviewer` | Revisa el slice vertical completo | `BE-00X-review.md` con decision |
| `invet-clean-architecture-reviewer` | Revisa capas backend y modularidad frontend | `BE-00X-clean-architecture-review.md` con decision |
| `invet-security-reviewer` | Revisa autenticacion, autorizacion, IDOR/BOLA y datos | `BE-00X-security-review.md` con decision |
| `invet-findings-implementer` | Corrige findings y pruebas unitarias faltantes en la capa responsable | Correcciones y estado `READY_FOR_REVALIDATION` |
| `invet-command-executor` | Ejecuta comandos, tests, lint, lectura de logs y reintentos mecanicos con el modelo seleccionado por el usuario | Salida cruda y evidencia reproducible |
| `invet-command-executor-fallback` | Respaldo mecanico para comandos y verificaciones que requieran reintentos | Salida cruda y evidencia reproducible |
| `invet-final-reviewer` | Gate final de release con revision de alta capacidad | `BE-00X-final-review.md` con decision |
| `invet-check-runner` | Ejecuta UI checks, tests, lint, format, types y build; valida si hay cambios pendientes antes del cierre Docker | `BE-00X-checks.md` con decision |
| `invet-docs-updater` | Documenta el cierre despues de aprobar gates | Changelog, contratos y estado final |

## Estados de ejecucion por familia

| Familia | Estado de ejecucion permitido | Cuando usarlo |
| --- | --- | --- |
| Implementadores | `COMPLETED` o `BLOCKED` | Trabajo terminado o imposibilidad real de avanzar |
| Planner | `PLANNED` o `BLOCKED` | Plan generado o bloqueado por contrato/evidencia |
| QA y reviewers | `APPROVED`, `REJECTED` o `BLOCKED` | Gate aprobado, rechazado o impedido por evidencia/entorno; `READY_FOR_REVALIDATION` no es un estado de gate |
| Findings implementer | `READY_FOR_REVALIDATION`, `COMPLETED` o `BLOCKED` | Correccion preparada para revalidacion, terminada o bloqueada |
| Check runner / docs / final reviewer | `APPROVED`, `REJECTED`, `COMPLETED` o `BLOCKED` | Gate aprobado/rechazado o cierre documental completado |

## Ownership de pruebas

| Tipo | Responsable |
| --- | --- |
| Unitarias backend | `invet-backend-implementer` |
| Unitarias/componentes frontend | `invet-frontend-implementer` |
| E2E y regresion UI | `invet-ui-automation-implementer` |
| Contratos HTTP externos | `invet-api-automation-implementer` |
| Unitarias faltantes reportadas | Agente de capa o `invet-findings-implementer` |
| Aceptacion, integracion, contrato, seguridad y regresion | `invet-qa-validator` |
| Certificacion final | `invet-qa-validator` |

QA no repara y certifica el mismo gap unitario. Debe emitir `REJECTED`, dejar un finding y revalidar despues de la correccion.

`READY_FOR_REVALIDATION` pertenece al lifecycle de findings, no al cierre del gate de QA ni de los reviewers. Si un agente de QA o review reporta `Estado de ejecucion`, debe usar solo `APPROVED`, `REJECTED` o `BLOCKED`.

Todos los agentes operativos pueden usar `docker compose` cuando el slice requiera PostgreSQL, backend runtime o frontend runtime en contenedor. La referencia normal es `db` + `backend` para pruebas con persistencia y `frontend` para validacion de UI cuando aplique.

Cuando la validacion requiera PostgreSQL u otro servicio del compose del repo, `invet-qa-validator` ejecuta la suite dentro del contenedor de backend y usa `docker compose` como contexto de prueba. Antes de reiniciar contenedores al cierre, valida si existen cambios pendientes que realmente ameriten rebuild/restart; si no los hay, registra el skip y no fuerza Docker. Si Docker aplica, QA tambien debe confirmar que todos los contenedores relevantes fueron actualizados o recreados y que su estado quedo saludable. El contenedor de `frontend` se considera runtime por defecto y no debe asumirse apto para tests salvo que el flujo lo prepare de forma explicita.

## Contrato de tarea schema v3

Cada tarea del plan debe incluir:

- `Capa`
- `Tipo`
- `Historia o criterio`
- `Objetivo`
- `Responsabilidad unica`
- `Depende de`
- `Contexto necesario`
- `Contratos usados`
- `Entregables`
- `Criterios de aceptacion`
- `Validacion`
- `Resultado esperado`
- `Evidencia`
- `Paralelismo[P]`

`Responsabilidad unica` debe ser `Si`. El objetivo debe ser pequeno y no compuesto. Si un agente detecta que una tarea mezcla contrato, persistencia, API, UI, seguridad, pruebas, Docker o documentacion, debe devolverla al planner para division antes de implementar.

## Politica UTF-8

- Markdown operativo, comentarios de codigo escritos por agentes, reportes, findings y outcomes deben conservar UTF-8.
- Los scripts Python del pipeline deben usar `encoding="utf-8"` para leer/escribir texto.
- JSON generado por herramientas propias debe usar `ensure_ascii=False`.
- Texto nuevo con mojibake probable (`Ã`, `Â`, `â`) invalida el artefacto hasta corregirse.

## Lifecycle de findings QA

```text
OPEN
  -> IN_PROGRESS
  -> READY_FOR_REVALIDATION
  -> RESOLVED
```

- `/implement-findings` puede llegar hasta `READY_FOR_REVALIDATION`.
- Solo `/qa-task` puede declarar `RESOLVED`.
- `ACCEPTED_RISK` requiere una decision explicita y evidencia.
- `OPEN`, `IN_PROGRESS` y `READY_FOR_REVALIDATION` bloquean el siguiente slice.

## Fuente de verdad y distribucion

- `.opencode`, `docs/opencode` y `backend/scripts` son los archivos operativos del repositorio.
- `payload` es el espejo distribuible usado por `install-invet-opencode-agents.ps1`.
- Las pruebas contractuales deben impedir divergencias en agentes, comandos, templates y validadores.
- `invet-command-executor` es el ejecutor primario y hereda el modelo seleccionado por el usuario.
- `invet-command-executor-fallback` se mantiene como respaldo operativo, pero no fija un modelo por defecto.
- `invet-final-reviewer` es el gate final de release y se usa despues de QA, reviews, checks y docs cuando se desea una segunda opinion de alta capacidad.
