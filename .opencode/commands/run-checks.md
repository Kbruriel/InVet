---
description: Ejecuta checks backend/frontend disponibles y resume resultados.
agent: invet-check-runner
---

Ejecuta los checks técnicos disponibles del repositorio.

Orden sugerido:
1. Detectar estructura del repo.
2. Backend:
   - `pytest` o `python -m pytest`.
   - `ruff check .`.
   - `black --check .`.
   - `mypy` o `pyright` si está configurado.
3. Frontend:
   - `npm run lint` / `pnpm lint`.
   - `npm run typecheck` / `pnpm typecheck`.
   - `npm run test` / `pnpm test`.
   - `npm run build` / `pnpm build`.
4. Reportar pass/fail/skipped.
5. No modificar archivos.
