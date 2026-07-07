# Matriz de checks

Esta matriz define que debe ejecutar `/run-checks` y cuando un check debe
marcarse como `skipped`.

## Backend

Directorio de ejecucion: `backend/`.

Checks obligatorios cuando existe el backend:

```bash
python -m pytest app/tests -q
python -m ruff check .
python -m black --check .
python -m mypy app
```

Reglas:
- Usar `python -m ...` para asegurar que se ejecuten las herramientas del ambiente activo.
- `pytest` es obligatorio si existe `backend/app/tests`.
- `ruff` es obligatorio si existe `ruff.toml` o configuracion equivalente.
- `black --check` es obligatorio si Black esta instalado/configurado.
- `mypy app` es obligatorio si existe `mypy.ini` o configuracion equivalente.
- Si una herramienta no esta instalada, reportar `fail` salvo que no exista configuracion del check.

## Frontend

Directorio de ejecucion: `frontend/`.

Reglas:
- Si `frontend/package.json` no existe, marcar todos los checks frontend como `skipped`.
- Detectar gestor por lockfile en este orden: `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`.
- Ejecutar solo scripts existentes en `package.json`.
- Si un script no existe, marcar ese script como `skipped` con motivo.

Scripts esperados cuando existen:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Alternativas segun gestor:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

```bash
yarn lint
yarn typecheck
yarn test
yarn build
```

## DevOps

Docker Compose es opcional.

```bash
docker compose config
docker compose build
```

Reglas:
- Ejecutar solo si existe archivo compose y el usuario lo permite.
- Si no existe configuracion o no hay permiso, marcar como `skipped`.

## Modo correccion

`/run-checks` opera en modo reporte por defecto.

Si el usuario pide explicitamente corregir, solucionar o "fix errors":
- Puede modificar archivos de configuracion, formato, lint, tipos o tests.
- Debe rerunear los checks afectados.
- Debe reportar cambios aplicados y evidencia final.
