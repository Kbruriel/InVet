# InVet — Paquete instalable OpenCode secuencial

Este paquete instala **agentes OpenCode**, **comandos slash** y **documentación Markdown** para ejecutar el MVP de InVet con flujo secuencial por slice:

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

## Qué instala

```text
.opencode/
  agents/
  commands/
docs/opencode/
  tasks/backend/BE-001..BE-017.md
  tasks/frontend/FE-001..FE-017.md
  tasks/qa/QA-001..QA-017.md
  gates/
  references/
  templates/
```

## Instalación rápida

Desde la carpeta descomprimida del paquete:

```powershell
.\install-invet-opencode-agents.ps1 -Root "C:\ruta\al\repo-invet" -Force
```

Desde la raíz del repo, si copiaste el paquete ahí:

```powershell
.\install-invet-opencode-agents.ps1 -Force
```

Validar sin escribir:

```powershell
.\install-invet-opencode-agents.ps1 -Root "C:\ruta\al\repo-invet" -DryRun
```

## Reglas principales

- Cada slice debe usar el mismo índice para backend, frontend y QA: `BE-00X`, `FE-00X`, `QA-00X`.
- Backend define contrato y reglas primero.
- Frontend consume el contrato del mismo slice.
- QA valida backend + frontend + permisos + regresión.
- Las revisiones de arquitectura, seguridad, checks y documentación son obligatorias antes de pasar al siguiente slice.
- El MVP no incluye productos, marketplace, carrito, checkout en línea, pasarela de pago de servicios, facturación electrónica ni timbrado fiscal.

## Primer comando recomendado

```text
/plan-task BE-001
```
