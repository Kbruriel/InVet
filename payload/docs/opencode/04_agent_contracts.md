# 04 - Contratos de agentes

## invet-product-planner

Genera `docs/opencode/plans/BE-00X-plan.md` con checklist numerado, objetivos, criterios de aceptacion medibles y `Paralelismo[P]`. No escribe codigo fuente.

## invet-backend-implementer

Implementa tareas backend pendientes del plan, verifica criterios de aceptacion y marca como completadas solo las tareas verificadas.

## invet-frontend-implementer

Implementa tareas frontend pendientes del plan, respeta contratos API y sistema visual, verifica criterios de aceptacion y marca como completadas solo las tareas verificadas.

## invet-qa-validator

Valida calidad funcional usando objetivos y criterios de aceptacion del plan, auto-recupera infraestructura QA local cuando es posible, crea o ajusta pruebas cuando hace falta, valida evidencia del runner, aplica regresion por impacto, documenta trazabilidad y marca tareas QA solo cuando existe evidencia PASS.

## invet-slice-reviewer

Revisa plan e implementacion de BE/FE/QA y documenta hallazgos en Markdown.

## invet-findings-implementer

Implementa hallazgos de review o QA, genera checklist de correcciones y documenta el cierre.

## invet-clean-architecture-reviewer

Revisa separacion de capas backend y modularidad frontend. No modifica codigo.

## invet-security-reviewer

Revisa OWASP, IDOR/BOLA, tokens, permisos, logs y exposicion de datos. No modifica codigo.

## invet-check-runner

Ejecuta checks disponibles sin modificar archivos.

## invet-docs-updater

Actualiza documentacion Markdown y estado del slice.

## invet-orchestrator

Agente primario opcional para coordinar el flujo completo y evitar saltar gates.
