# 01 — Runbook de comandos secuenciales

## Secuencia obligatoria

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

## Reglas

1. `plan-task` siempre recibe un ID backend `BE-00X`.
2. `implement-backend-task` implementa el contrato y reglas del slice.
3. `implement-frontend-task` recibe el ID frontend equivalente `FE-00X`.
4. `qa-task` recibe el ID QA equivalente `QA-00X`.
5. Las revisiones globales se ejecutan después de QA.
6. `run-checks` debe ejecutarse antes de `update-docs`.
7. `update-docs` cierra el slice.

## Ejemplo: búsqueda pública

```text
/plan-task BE-003
/implement-backend-task BE-003
/implement-frontend-task FE-003
/qa-task QA-003
/clean-architecture-review
/security-review
/run-checks
/update-docs
```

## Resultado esperado por slice

- Código backend implementado o explícitamente no requerido.
- Código frontend implementado o explícitamente no requerido.
- QA ejecutado con evidencia.
- Revisión arquitectura aprobada.
- Revisión seguridad aprobada.
- Checks verdes o fallos documentados.
- Documentación actualizada.
