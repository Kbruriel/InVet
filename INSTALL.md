# Instalacion del paquete OpenCode para InVet

## 1. Descomprimir

```powershell
Expand-Archive .\invet_opencode_agents_install_package.zip -DestinationPath .\invet_opencode_agents_install_package -Force
cd .\invet_opencode_agents_install_package
```

## 2. Instalar en el repositorio

```powershell
.\install-invet-opencode-agents.ps1 -Root "C:\ruta\al\repo-invet" -Force
```

## 3. Revisar archivos instalados

```powershell
Get-ChildItem "C:\ruta\al\repo-invet\.opencode\agents"
Get-ChildItem "C:\ruta\al\repo-invet\.opencode\commands"
Get-ChildItem "C:\ruta\al\repo-invet\docs\opencode"
```

## 4. Ejecutar el primer slice

Antes de lanzar `/run-checks`, confirma que el entorno de Python del backend tenga instaladas las dependencias de `backend/requirements.txt`.
Si no estan presentes `pytest`, `ruff`, `black` o `mypy`, instala primero el backend en ese entorno y vuelve a ejecutar los checks.
Para preparar el entorno QA automaticamente, ejecuta `python backend/scripts/prepare_qa_env.py --install-deps` desde la raiz del repo.
Ese bootstrap crea `backend/.env.qa` con `sqlite:///./qa-test.db`, valida una base utilizable y deja listas las variables locales para pruebas.
Si prefieres correrlos fuera de OpenCode, usa `.\run-checks.ps1` o `.\run-checks.cmd` desde la raiz del repo.

```text
/plan-task BE-001
/implement-backend-task BE-001
/implement-frontend-task FE-001
/qa-task QA-001
/review-slice BE-001
/implement-findings BE-001
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## Nota sobre skills

No invoques `invet-backend-implementer` como skill. Ese nombre corresponde a un agente OpenCode en `.opencode/agents`.

Si ves:

```text
Skill "invet-backend-implementer" not found. Available skills: customize-opencode
```

usa:

```text
/implement-backend-task BE-001
```

`customize-opencode` es la skill usada para personalizar la configuracion OpenCode; el flujo InVet se ejecuta con comandos slash.

## 5. Confirmar cierre

Antes de iniciar `BE-002`, deben estar verdes:

- Clean Architecture review.
- Security review.
- Checks backend/frontend.
- QA del slice.
- Documentacion actualizada.
