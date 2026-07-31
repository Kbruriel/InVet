# 00 - Manifiesto de instalacion OpenCode InVet

## Objetivo

Instalar una capa operativa para que OpenCode ejecute el MVP de InVet mediante comandos secuenciales y agentes especializados.

## Nota sobre skills

Este paquete instala agentes OpenCode, no skills Codex individuales.

Si Codex muestra:

```text
Skill "invet-backend-implementer" not found. Available skills: customize-opencode
```

usa el comando slash:

```text
/implement-backend-task BE-00X
```

`customize-opencode` es la skill para personalizar esta configuracion. Los agentes `invet-*` viven en `.opencode/agents` y se invocan desde `.opencode/commands`.

## Archivos instalados

```text
.opencode/agents/*.md
.opencode/commands/*.md
docs/opencode/**/*.md
```

## Comandos instalados

```text
/plan-task
/implement-backend-task
/implement-frontend-task
/qa-task
/review-slice
/implement-findings
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## Agentes instalados

```text
invet-orchestrator
invet-product-planner
invet-backend-implementer
invet-frontend-implementer
invet-qa-validator
invet-slice-reviewer
invet-findings-implementer
invet-clean-architecture-reviewer
invet-security-reviewer
invet-check-runner
invet-docs-updater
```

## Principio de ejecucion

Cada indice representa un slice vertical:

```text
BE-00X + FE-00X + QA-00X = un resultado funcional verificable
```

No se debe avanzar al siguiente indice hasta cerrar arquitectura, seguridad, checks y documentacion.
