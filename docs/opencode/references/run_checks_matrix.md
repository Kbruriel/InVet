# Matriz de checks

## Backend

```bash
pytest
ruff check .
black --check .
mypy app
```

Alternativas:

```bash
python -m pytest
python -m ruff check .
python -m black --check .
python -m mypy app
```

## Frontend

Con npm:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

Con pnpm:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## DevOps

```bash
docker compose config
docker compose build
```

Solo ejecutar Docker si el entorno está preparado.
