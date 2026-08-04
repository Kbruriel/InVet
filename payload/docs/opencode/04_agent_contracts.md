# 04 - Agent Contracts

## Contrato comun

- `BE-00X`, `FE-00X` y `QA-00X` representan un unico slice vertical.
- El plan canonico es `docs/opencode/plans/BE-00X-plan.md`.
- Los agentes intercambian estado mediante Markdown versionado, no memoria implicita.
- Cada comando mutable ejecuta `backend/scripts/validate_slice_plan.py`.
- Las tareas mecanicas de ejecucion pueden delegarse a `invet-command-executor` para conservar el razonamiento en el agente de dominio.
- Una tarea completada requiere criterios verificados y `Evidencia` reproducible.
- Un gate fallido detiene el flujo; no se convierte en `skipped`.

## Responsabilidades

| Agente | Responsabilidad | Gate o salida |
| --- | --- | --- |
| `invet-orchestrator` | Ejecuta el slice completo y evita saltar etapas | Bloquea ante plan invalido, QA no aprobado, findings abiertos, reviews o checks rechazados |
| `invet-product-planner` | Acepta IDs BE/FE/QA y crea el plan vertical schema v2 | `BE-00X-plan.md` validado |
| `invet-backend-implementer` | Implementa tareas `Capa: backend` y sus pruebas unitarias | Criterios, validacion y evidencia por tarea |
| `invet-frontend-implementer` | Implementa el contrato frontend y sus pruebas unitarias/de componente | Criterios, validacion y evidencia por tarea |
| `invet-qa-validator` | Valida aceptacion, integracion, contrato, seguridad y regresion | `QA-00X-results.md` y decision `APPROVED|REJECTED|BLOCKED` |
| `invet-slice-reviewer` | Revisa el slice vertical completo | `BE-00X-review.md` con decision |
| `invet-clean-architecture-reviewer` | Revisa capas backend y modularidad frontend | `BE-00X-clean-architecture-review.md` con decision |
| `invet-security-reviewer` | Revisa autenticacion, autorizacion, IDOR/BOLA y datos | `BE-00X-security-review.md` con decision |
| `invet-findings-implementer` | Corrige findings y pruebas unitarias faltantes en la capa responsable | Correcciones y estado `READY_FOR_REVALIDATION` |
| `invet-command-executor` | Ejecuta comandos, tests, lint, lectura de logs y reintentos mecanicos con el modelo seleccionado por el usuario | Salida cruda y evidencia reproducible |
| `invet-command-executor-fallback` | Respaldo mecanico para comandos y verificaciones que requieran reintentos | Salida cruda y evidencia reproducible |
| `invet-final-reviewer` | Gate final de release con revision de alta capacidad | `BE-00X-final-review.md` con decision |
| `invet-check-runner` | Ejecuta tests, lint, format, types y build; valida si hay cambios pendientes antes del cierre Docker | `BE-00X-checks.md` con decision |
| `invet-docs-updater` | Documenta el cierre despues de aprobar gates | Changelog, contratos y estado final |

## Ownership de pruebas

| Tipo | Responsable |
| --- | --- |
| Unitarias backend | `invet-backend-implementer` |
| Unitarias/componentes frontend | `invet-frontend-implementer` |
| Unitarias faltantes reportadas | Agente de capa o `invet-findings-implementer` |
| Aceptacion, integracion, contrato, seguridad y regresion | `invet-qa-validator` |
| Certificacion final | `invet-qa-validator` |

QA no repara y certifica el mismo gap unitario. Debe emitir `REJECTED`, dejar un finding y revalidar despues de la correccion.

Todos los agentes operativos pueden usar `docker compose` cuando el slice requiera PostgreSQL, backend runtime o frontend runtime en contenedor. La referencia normal es `db` + `backend` para pruebas con persistencia y `frontend` para validacion de UI cuando aplique.

Cuando la validacion requiera PostgreSQL u otro servicio del compose del repo, `invet-qa-validator` ejecuta la suite dentro del contenedor de backend y usa `docker compose` como contexto de prueba. Antes de reiniciar contenedores al cierre, valida si existen cambios pendientes que realmente ameriten rebuild/restart; si no los hay, registra el skip y no fuerza Docker. El contenedor de `frontend` se considera runtime por defecto y no debe asumirse apto para tests salvo que el flujo lo prepare de forma explicita.

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
