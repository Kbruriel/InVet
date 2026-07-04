# 00 — Manifiesto de instalación OpenCode InVet

## Objetivo

Instalar una capa operativa para que OpenCode ejecute el MVP de InVet mediante comandos secuenciales y agentes especializados.

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

## Principio de ejecución

Cada índice representa un slice vertical:

```text
BE-00X + FE-00X + QA-00X = un resultado funcional verificable
```

No se debe avanzar al siguiente índice hasta cerrar arquitectura, seguridad, checks y documentación.
