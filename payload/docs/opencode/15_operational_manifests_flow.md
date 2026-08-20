# Flujo coherente con manifiestos operativos

## Propiedad de los artefactos

`/plan-task BE-00X` es el unico comando que decide el alcance del slice. El agente `invet-product-planner` crea o actualiza:

- `docs/opencode/plans/BE-00X-plan.md`.
- `docs/opencode/tasks/user-stories/US-00X.md`.
- `docs/opencode/tasks/ui-automation/UIA-00X.md`.
- `docs/opencode/tasks/api-automation/APIA-00X.md`.
- Los cinco manifiestos `BE-00X-{backend,frontend,qa,ui-automation,api-automation}.md`.

`backend/scripts/manage_slice_task.py` no interpreta producto ni inventa alcance. Solo renderiza el contexto compacto y guarda los hashes SHA-256 del plan y del sidecar de capa.

El cierre de planeacion exige:

```text
python backend/scripts/validate_slice_plan.py BE-00X --stage plan
python backend/scripts/manage_slice_task.py manifest BE-00X --layer all
python backend/scripts/manage_slice_task.py verify BE-00X --layer all
```

Si falta `UIA-00X` o `APIA-00X`, o cambia una fuente despues de generar el manifiesto, `verify` bloquea el flujo y devuelve la responsabilidad a `/plan-task BE-00X`.

## Responsabilidad por fase

| Fase | Contexto compacto | Responsabilidad que conserva |
|---|---|---|
| Backend | Manifiesto backend | Implementar solo tareas BE y pruebas backend |
| Frontend | Manifiesto frontend | Implementar solo tareas FE y pruebas frontend |
| UI automation | Manifiesto UIA | Implementar Playwright E2E contra `db/backend/frontend` de Docker, actualizar `UIA-00X` y guardar checkpoint de fase `UIA-00X` |
| API automation | Manifiesto APIA | Implementar pruebas HTTP contra el backend Docker, actualizar `APIA-00X` y guardar checkpoint de fase `APIA-00X` |
| QA | Los cinco manifiestos | Validar handoffs y emitir la decision QA; no reparar producto |
| Reviews | Los cinco manifiestos | Delimitar alcance; decidir desde diff, QA y evidencia real |
| UI checks y checks | Manifiestos afectados | Ejecutar suites reales y producir evidencia reproducible |
| Documentacion | Los cinco manifiestos y reportes | Reconciliar cierre sin cambiar producto |
| Final gate | Los cinco manifiestos y todos los reportes | Aprobar o bloquear el release con el modelo seleccionado |

Los manifiestos no sustituyen al plan, checkpoints, resultados QA, reportes de review, diff ni salida de pruebas. Sirven para reducir contexto y prevenir cambios fuera de alcance.

Los manifiestos UIA y APIA declaran Docker como entorno obligatorio. Docker ausente deja la fase `BLOCKED`; no autoriza evidencia equivalente desde procesos host. La UI usa `PLAYWRIGHT_START_FRONTEND=false` para evitar que Playwright sustituya el contenedor `frontend` por un servidor local.

## Ejecucion completa

`/execute-slice` puede recibir BE, FE o QA. Para la secuencia manual se usa BE como entrada uniforme, excepto el comando QA:

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
/run-ui-checks BE-00X
/run-checks BE-00X
/update-docs BE-00X
/final-gate BE-00X
```

`/execute-slice BE-00X` ejecuta la misma cadena, se detiene en el primer gate fallido y reanuda desde ese punto. Si aparecen findings, el flujo inserta `/implement-findings BE-00X` y repite QA y los gates afectados antes de continuar.

Las validaciones deterministas pertenecen al comando responsable. En particular, `/implement-backend-task` ejecuta internamente la validacion de persistencia cuando aplica; el flujo publico no expone scripts Python como fases independientes.

## Regla de coherencia

Los comandos que aceptan aliases normalizan el indice compartido `00X`, pero no intercambian responsabilidades. Aceptar `BE-00X` en el comando frontend solo normaliza la entrada a `FE-00X`; no autoriza al frontend a modificar backend. QA conserva `QA-00X`, y review rechaza `QA-00X` para evitar una reinterpretacion silenciosa. La allowlist de `Entregables`, los checkpoints y el validador mantienen esa separacion.
