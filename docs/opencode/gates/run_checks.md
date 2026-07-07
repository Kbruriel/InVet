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
- Frontend: skipped cuando `frontend/package.json` no existe.
- DevOps: skipped si Docker Compose no esta configurado o no hay permiso explicito.
