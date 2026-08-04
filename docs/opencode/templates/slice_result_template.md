---
encoding: UTF-8
artifact: slice_result
---

# Resultado de slice XX

## Comandos ejecutados

```text
/execute-slice BE-XXX
```

O flujo manual:

```text
/plan-task BE-XXX
/implement-backend-task BE-XXX
/implement-frontend-task FE-XXX
/qa-task QA-XXX
/review-slice BE-XXX
/clean-architecture-review BE-XXX
/security-review BE-XXX
/implement-findings BE-XXX
/qa-task QA-XXX
/run-checks BE-XXX
/update-docs BE-XXX
```

## Resumen

## Backend

## Frontend

## QA

## Seguridad

## Arquitectura

## Checks

## Documentación actualizada

## Pendientes

## Decisión de avance

- Plan gate: `PASS|FAIL`
- QA: `APPROVED|REJECTED|BLOCKED`
- Slice review: `APPROVED|REJECTED`
- Architecture review: `APPROVED|REJECTED`
- Security review: `APPROVED|REJECTED`
- Checks: `APPROVED|REJECTED`
- [ ] Puede avanzar al siguiente slice.
- [ ] No puede avanzar por blockers.

## Política UTF-8

- Redacciones, comentarios y outcomes conservan UTF-8.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
