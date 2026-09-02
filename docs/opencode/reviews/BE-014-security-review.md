---
encoding: UTF-8
artifact: review_security
slice: BE-014
aliases: [FE-014]
type: security-review
date: 2026-09-02
decision: APPROVED
---

# Revisión de seguridad para slice BE-014 — Soporte básico (tickets)

## Normalización y agente ejecutor

El índice vertical es `BE-014`. Este gate valida controles de seguridad, autorizacion y resistencia a ataques comunes del deliverable del ticket soporte.

## Alcance de la revision

| Control | Capa | Fuente de evidencia |
|---|---|---|
| AuthN requerida en todos los endpoints | Router FastAPI | `backend/app/api/v1/routers/support_ticket_router.py` + AC-014-07 |
| AuthZ / aislamiento by tenant | Router + repo | IDOR/BOLA test suite (AC-014-04, C11) |
| Validations entradas / inyeccion SQL | Pydantic schemas + ORM params | `support_ticket_schemas.py` + ORM parametrizado |
| Status enum guardado sin escape | Use-case state machine | `support_ticket_use_cases.py` `_TRANSITIONS` |
| Categories seed idempotente | Migration Alembic | `a014_support.py` — `WHERE NOT EXISTS` |
| Logging / audit de eventos | No implementado (fuera alcance) | Fuera de scope AC-014 |

## Hallazgos por severidad

| # | Severidad | Descripcion | Impacto | Estado |
|---|-----------|-------------|---------|--------|
| S1 | Low — El campo `status` del modelo tiene `nullable=True` aunque la migracion fija `server_default "iniciado"`. SQLAlchemy enmascara el NULL con el default, pero una bypass directa al ORM podria generar inconsistencias. | Bajo — el use-case siempre setea status explicito y el router valida via Pydantic enum. | Aceptado como riesgo menor. |
| S2 | Low — No existe auditoria/log de cambios de estado. La maquina de estados `_TRANSITIONS` protege las transiciones pero no deja rastro. | Bajo — fuera del alcance AC-014 (Stage 2 para audit trail). | Aceptado, documentado en fuera de alcance. |
| S3 | Info — La validacion de longitud de `description` (<= 2000) se realiza en el use-case y los schemas Pydantic, duplicando la guard. | Sin riesgo — redundancia benigna que endurece la capa HTTP. | Cierre sin accion. |

## Verificacion IDOR / BOLA

- El repo aplica `where(OwnerTicket.owner_id == user.id)` (u `InternalUser` con `clinic_id`) en todas las querys de listado y detalle.
- PRUEBA `test_support_ticket_api.py::test_get_ticket_other_owner_returns_404` verifica que un ticket ajen o no es expuesto ni por contenido ni por enumeracion (respuesta 404, no 403 — previene confirmacion de existencia).
- **Resultado: PASS**

## Verificacion de transiciones seguras

- El dict `_TRANSITIONS` en `support_ticket_use_cases.py` controla los permisos de cambio de estado. Solo administradores (`internal_user`) pueden iniciar transiciones.
- Owner solo puede read y crear; no tiene capacidad de modificar el ticket ajen o su propio status una vez creado (salvo como admin).
- **Resultado: PASS**

## Decision final

No hay hallazgos bloqueantes ni CRITICAL/MAJOR. Los riesgos menores (S1, S2) son aceptados como fuera de alcance del MVP y se dejan para Stage 2 cuando la arquitectura de logging/audit este madura.

- **Decision:** APPROVED

- Decision: APPROVED

## Proximo paso recomendado

Continuar por `/run-ui-checks BE-014` → `/final-gate BE-014`.
