# InVet - Paquete instalable OpenCode secuencial

Este paquete instala agentes OpenCode, comandos slash y documentacion Markdown para ejecutar el MVP de InVet con flujo secuencial por slice:

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

## Importante: skills vs agentes

Los archivos `invet-*-implementer` son agentes OpenCode, no skills Codex.

Si aparece este error:

```text
Skill "invet-backend-implementer" not found. Available skills: customize-opencode
```

usa el comando slash correspondiente:

```text
/implement-backend-task BE-001
```

La skill `customize-opencode` sirve para instalar o modificar la configuracion OpenCode. Los agentes se invocan indirectamente desde los comandos en `.opencode/commands`.

## Que instala

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

## Instalacion rapida

Desde la carpeta descomprimida del paquete:

```powershell
.\install-invet-opencode-agents.ps1 -Root "C:\ruta\al\repo-invet" -Force
```

Desde la raiz del repo, si copiaste el paquete ahi:

```powershell
.\install-invet-opencode-agents.ps1 -Force
```

Validar sin escribir:

```powershell
.\install-invet-opencode-agents.ps1 -Root "C:\ruta\al\repo-invet" -DryRun
```

## Reglas principales

- Cada slice debe usar el mismo indice para backend, frontend y QA: `BE-00X`, `FE-00X`, `QA-00X`.
- Backend define contrato y reglas primero.
- Frontend consume el contrato del mismo slice.
- QA valida backend, frontend, permisos y regresion.
- Las revisiones de arquitectura, seguridad, checks y documentacion son obligatorias antes de pasar al siguiente slice.
- El MVP no incluye productos, marketplace, carrito, checkout en linea, pasarela de pago de servicios, facturacion electronica ni timbrado fiscal.

## Primer comando recomendado

```text
/plan-task BE-001
```
