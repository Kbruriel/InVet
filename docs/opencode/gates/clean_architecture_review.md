# Gate — Clean Architecture Review

## Objetivo

Cerrar el gate `clean_architecture_review` antes de avanzar al siguiente slice.

## Entrada

- Cambios actuales del slice.
- Tareas BE/FE/QA correspondientes.
- Evidencia de implementación o QA.

## Salida requerida

- Estado: Aprobado/Rechazado.
- Hallazgos por severidad.
- Acciones requeridas.
- Riesgos aceptados si aplica.

## Preflight reproducible y compatibilidad PowerShell

El agente `invet-clean-architecture-reviewer` debe normalizar `FE-00X` al
plan `BE-00X` y trabajar con `C:\InVet` como directorio de ejecución. Windows
PowerShell 5.1 no admite `&&`; por eso cada comando se ejecuta en una
invocación separada. Para secuencias fail-fast se usa
`if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`.

Antes de emitir decisión, documenta evidencia de:

1. `validate_slice_plan.py` en `plan` y `backend` (o la etapa equivalente del
   slice).
2. Los cinco manifiestos y sus allowlists mediante `manage_slice_task.py verify`.
3. Registro del modelo en `models/__init__.py` y correspondencia ORM/Alembic
   (tablas, columnas, claves foráneas, índices, unicidad y defaults).
4. `upgrade`, `downgrade`, seed idempotente y reversión de la migración.
5. Pruebas dirigidas del backend/frontend y `git diff --check`.
6. Diff final trazado a cada criterio AC del plan canónico; no se debe asumir
   que existe un archivo de requisitos separado.

Comandos de referencia:

```powershell
python backend/scripts/validate_slice_plan.py FE-00X --stage plan
python backend/scripts/validate_slice_plan.py FE-00X --stage backend
python backend/scripts/manage_slice_task.py verify FE-00X --layer all
python -m pytest backend/tests/api/test_*migration*.py -q
git diff --check
```

Si Docker es necesario, usa comandos separados y recuerda que el contenedor
`backend` trabaja en `/app`: las rutas de prueba son `tests/...`, no
`backend/tests/...`. Después de cambiar pruebas o código, reconstruye la imagen
antes de ejecutarla para evitar evidencia de una imagen obsoleta:

```powershell
docker compose up -d db
docker compose build backend
docker compose run --rm backend pytest tests/api/test_support_ticket_migration.py -q
```

No uses `&&` en PowerShell 5.1. Un error de ruta como
`/backend/alembic/...` indica que la prueba depende de una raíz absoluta; debe
resolver `BACKEND_DIR` desde `Path(__file__)` para funcionar en host y Docker.

## Bloqueantes comunes

- Alcance fuera del MVP.
- Datos privados expuestos.
- Falta de permisos backend.
- IDOR/BOLA posible.
- Routers con lógica de negocio.
- ORM expuesto.
- Tests críticos faltantes.
- Build/lint/typecheck fallando sin justificación.
