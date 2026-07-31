# 12 - Troubleshooting: skills vs agentes OpenCode

## Error

```text
Skill "invet-backend-implementer" not found. Available skills: customize-opencode
```

## Causa

`invet-backend-implementer` no es una skill de Codex. Es un agente OpenCode instalado en:

```text
.opencode/agents/invet-backend-implementer.md
```

Los agentes OpenCode se ejecutan mediante comandos slash definidos en:

```text
.opencode/commands/*.md
```

La skill disponible `customize-opencode` sirve para crear, instalar o modificar la configuracion OpenCode. No reemplaza a los comandos slash del flujo InVet.

## Uso correcto

Para ejecutar backend usa el comando slash:

```text
/implement-backend-task BE-00X
```

No uses:

```text
Skill invet-backend-implementer
```

## Mapeo rapido

| Objetivo | Uso correcto | Agente usado internamente |
|---|---|---|
| Planificar slice | `/plan-task BE-00X` | `invet-product-planner` |
| Implementar backend | `/implement-backend-task BE-00X` | `invet-backend-implementer` |
| Implementar frontend | `/implement-frontend-task FE-00X` | `invet-frontend-implementer` |
| Ejecutar QA | `/qa-task QA-00X` | `invet-qa-validator` |
| Revisar slice | `/review-slice BE-00X` | `invet-slice-reviewer` |
| Implementar hallazgos | `/implement-findings BE-00X` | `invet-findings-implementer` |

## Verificacion

Confirma que existan estos archivos:

```powershell
Get-ChildItem .opencode/agents
Get-ChildItem .opencode/commands
```

Si los archivos existen pero OpenCode no reconoce los comandos, reinicia la sesion de OpenCode para recargar `.opencode`.
