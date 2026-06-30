# Instalación del paquete OpenCode para InVet

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
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## 5. Confirmar cierre

Antes de iniciar `BE-002`, deben estar verdes:

- Clean Architecture review.
- Security review.
- Checks backend/frontend.
- QA del slice.
- Documentación actualizada.
