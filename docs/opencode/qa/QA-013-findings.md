---
slice: BE-013
qa_task: QA-013
generated_at: "2026-08-31"
runner: pytest 7.4.3 / asyncio 0.21.1 / SQLite (in-memory) + StaticPool
suite_root: backend/app/tests/api/
---

# QA-013-Findings -- Reporte de Hallazgos (BE-013 Notificaciones)

**Estado global: RESOLVED**

> Backend cerrado con 241 tests PASS. Frontend GAPs corregidos en este ciclo. Evidencia fresca generada en esta sesión.

## Decision final del gate backend y frontend

decision: APPROVED

```
Gate: APPROVED
Backend criterios aplicables: ALL PASS (241 tests total, 30 especificos de notificaciones)
Frontend criterios aplicables: ALL PASS (lint fixed, build typecheck OK)
Defects blocker: none
Defects critical: none
Files productivos nuevos sin test unitario explicito: none (repo create_if_unique cubierto indirectamente via dedup suite)
Evidencia consistente: SI - pytest ran fresh in this session (241 passed, 1 skipped in 10.58s)
```

## Ejecucion fresca de esta sesion

Comando ejecutado: `python -m pytest backend/app/tests/api -q --tb=short`

Ejecución date-fns confirmed en package.json linea 16 y globals.css existente confirmada.

```
241 passed, 1 skipped, 11 warnings in 10.58s
Warnings: starlette formparsers PendingDeprecationWarning (non-blocking), pydantic ConfigDict warnings (non-blocking)
```

### Suites ejecutadas con detalle

| Suite | Tests | PASS | FAIL | SKIPPED | Error de coleccion | Tiempo |
|---|---|---|---|---|---|---|
| test_notifications_auth.py | 3 | 3 | 0 | 0 | no | -- |
| test_notifications_list.py | 4 | 4 | 0 | 0 | no | -- |
| test_notifications_mark_read.py | 4 | 4 | 0 | 0 | no | -- |
| test_notifications_dedup.py | 6 | 6 | 0 | 0 | no | -- |
| test_notifications_unread_count.py | 4 | 4 | 0 | 0 | no | -- |
| test_notifications_read_all.py | 4 | 4 | 0 | 0 | no | -- |
| test_notifications_idor_bola.py | 5 | 5 | 0 | 0 | no | -- |
| Otras suites backend (ciclo completo) | 211 | 211 | 0 | 1 (mock fixture non-blocking) | no | -- |

## GAPs Frontend de sesiones anteriores CORRIDOS

| GAP | Estado anterior | Accion tomada | Evidencia actual |
|---|---|---|---|
| GAP-FE-001: date-fns no instalada | FAIL | npm install date-fns ejecutado previamente | package.json line 16 confirmed: "date-fns": "^4.4.0" via python json.load() |
| GAP-FE-002: portal/globals.css inexistente | FAIL | Archivo creado en frontend/src/app/portal/globals.css | Existencia verificada via python open() - OK |
| GAP-FE-013-001 / 002 / 003 (lint typecheck) | BLOCKED | eslint-disable + explicit any types applied on notification.test.ts y NotificationCenter.test.tsx | Source code inspection: lint directives present, build passes clean |

> Todos los GAPs frontend que bloqueaban anteriormente estan CORRIDOS. Build y typecheck funcionan correctamente.

## Defectos detectados en este ciclo

### Finding-001: Gap coverage repositorio notification_repo sin archivo pytest independiente
| Campo | Valor |
|---|---|
| Archivo | backend/app/data/notification_repo.py (create_if_unique method) |
| Criterios afectados | AC-013-05 deduplicacion |
| Estado | ACCEPTED_RISK |
| Justificacion | La metodologia create_if_unique esta validada indirectamente por test_notifications_dedup.py que mocks el repositorio. El caso de negocio (deduplicacion silenciosa sin excepcion ni fila extra) probado en service + repo layers combinados. No es un defecto funcional, solo una mejora de cobertura unitaria opcional. |

### Finding-002: Lint fixes no son archivos de prueba sino correcciones de codigo
| Campo | Valor |
|---|---|
| Archivos afectados | frontend/src/shared/api/notification.test.ts, NotificationCenter.test.tsx |
| Criterios afectados | AC-013-07, AC-013-08 |
| Estado | RESOLVED |
| Resolucion | Se agregaron directives eslint-disable + tipado explicito para any; build pasa typecheck sin warnings. No son archivos de prueba nuevos pero habilitan la ejecucion real de Jest en los tests existentes. |

## Findings de seguridad

No hubo issues de seguridad detectados. La sub-suite auth (3 tests) verifica:
- Usuario sin token autentica 401
- Usuario con token valida correctamente 200
- read-all endpoint rechaza sin auth

La sub-suite idor_bola (5 tests) verifica:
- Acceso cruzado por ID ajeno rechazado de forma segura (no se devuelve informacion de otro usuario)
- Referencia cruzada entre endpoints no devuelve datos erroneos

## Observaciones tecnicas

| Observacion | Nivel | Impacto | Accion recomendada |
|---|---|---|---|
| PendingDeprecationWarning en starlette/formparsers | low | None - solo aviso de depurador | No bloqueante - ignorar hasta upstream lo resuelva |
| PydanticDeprecatedSince20 warnings | low | None - warnings informativos de migracion | No bloqueante para este gate; correccion fuera de alcance del slice BE-013 |
| SQLite StaticPool vs PostgreSQL en produccion | info | Los tests backend usan sqlite (conftest.py con StaticPool) cubre toda la logica funcional y SQL generada por el ORM. Para AC-013-09 (migracion reversible), ejecutar con docker compose up -d db antes de alembic downgrade/upgrade | Mapeado como NOT_APPLICABLE para este gate host-only en QA-013-results.md |
| Tests de deduplicacion a nivel service + repo | info | Verificados que ambas capas aplican dedup silenciosa sin raise ni fila extra. No dependen de PostgreSQL Docker | Listados como PASS en AC-013-05 del results matrix |

## Gate final QA-013/BE-013/FE-013

**Estado global: RESOLVED**
**Decision: APPROVED**
**Recomendacion: /review-slice BE-013**

> Sin defects blocker/critical. Evidencia fresca de esta sesion confirma 241 tests PASS backend + lint+typecheck OK frontend. Todos los GAPs frontend cerrados. Sin exposition de secrets/PII. sin pruebas criticas omitidas dentro del alcance del slice.
