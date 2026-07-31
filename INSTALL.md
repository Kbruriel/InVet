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
