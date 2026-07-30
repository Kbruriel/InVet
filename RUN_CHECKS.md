# Run Checks

Quick ways to run the standard checks:

```powershell
.\run-checks.ps1
```

```cmd
.\run-checks.cmd
```

What it does:
- Runs backend `pytest`, `ruff`, `black`, and `mypy`.
- Skips frontend checks if `frontend/package.json` is missing.
- Skips Docker Compose checks by design.

If you want the OpenCode command version instead, use:

```text
/run-checks
```
