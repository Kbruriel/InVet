# Gate - Run Checks

## Objetivo

Cerrar el gate `run_checks` antes de avanzar al siguiente slice.

## Entrada

- Cambios actuales del slice.
- Tareas BE/FE/QA correspondientes.
- Evidencia de implementacion o QA.
- Matriz vigente en `docs/opencode/references/run_checks_matrix.md`.

## Salida requerida

- Estado: Aprobado/Rechazado.
- Tabla de checks ejecutados con comando, directorio y resultado.
- Checks omitidos con motivo verificable.
- Hallazgos por severidad si queda algun fallo.
- Acciones requeridas o riesgos aceptados si aplica.

## Criterios de aprobacion

- Todos los checks configurados pasan.
- Los checks no configurados quedan marcados como `skipped` con motivo.
- No hay fallos de test, formato, lint o tipos sin justificar.
- Si se ejecuta en modo correccion, todos los cambios aplicados quedan resumidos y los checks afectados se rerunean.

## Bloqueantes comunes

- Alcance fuera del MVP.
- Datos privados expuestos.
- Falta de permisos backend.
- IDOR/BOLA posible.
- Routers con logica de negocio.
- ORM expuesto.
- Tests criticos faltantes.
- Build/lint/typecheck fallando sin justificacion.
- Configuracion de checks rota o inconsistente.

## Estrategia actual del repo

- Backend: ejecutar desde `backend/` con `python -m pytest app/tests -q`, `python -m ruff check .`, `python -m black --check .` y `python -m mypy app`.
- Frontend: ejecutar lint, typecheck, test y build cuando `frontend/package.json` exista y el script este definido; skipped solo cuando no existe `frontend/package.json` o falta un script especifico.
- DevOps: `git status` es read-only y obligatorio para decidir el cierre. Docker Compose esta autorizado por el contrato del agente cuando existe configuracion, Docker esta disponible, no hubo fallos previos y hay cambios relevantes; skipped solo si no aplica por configuracion, herramienta ausente, fallos previos o ausencia de cambios relevantes.
