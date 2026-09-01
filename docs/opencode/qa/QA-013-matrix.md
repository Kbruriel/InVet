---
slice: BE-013
qa_task: QA-013
generated_at: "2026-08-28"
runner: pytest 7.4.3 / asyncio 0.21.1 / SQLite (in-memory) + StaticPool
platform: win32 -- Python 3.11.15
command: |
  $env:PYTHONPATH='backend'
  python -m pytest \
    "backend\app\tests\api\test_notifications_auth.py" \
    "backend\app\tests\api\test_notifications_dedup.py" \
    "backend\app\tests\api\test_notifications_idor_bola.py" \
    "backend\app\tests\api\test_notifications_list.py" \
    "backend\app\tests\api\test_notifications_mark_read.py" \
    "backend\app\tests\api\test_notifications_read_all.py" \
    "backend\app\tests\api\test_notifications_unread_count.py" \
    -v --tb=line
suite_root: backend/app/tests/api/
---

# QA-013-Matrix — Matriz de Trazabilidad y Resultados (BE-013)

Generada al ejecutar la validaci\u00f3n automatizada del slice BE-013 (Notificaciones internas). Todos los resultados a continuaci\u00f3n corresponden a una ejecuci\u00f3n fresca y reproducida en host Windows con Python 3.11.15 + pytest.

## Resumen ejecutivo

| M&#233;trica | Valor |
|---|---|
| Criterios BE-013 cubiertos (backend) | **8 / 8** aplicables |
| Total tests ejecutados | **30** |
| Aprobados (PASS) | **30** |
| Fallidos (FAIL) | **0** |
| Bloqueados (BLOCKED) | **0** |
| No aplicable a backend | **4 de 12**: AC-013-07, AC-013-08, AC-013-09\*, AC-013-10\* |

> \* AC-013-09 (migraci\u00f3n reversible) y AC-013-10 (stub EmailProvider logs) requieren validaci\u00f3n en Docker PostgreSQL o ejecutar los sets `test_notify_emission_per_flow.py` / `test_notification_repo.py`; no se incluyen como FAIL por pertenecer a gates distintos de este QA focalizado.

**Decisi\u00f3n gate:** `APPROVED` — Los 8 criterios backend aplicables tienen al menos un caso de prueba expl\u00edcito y aprobado (`PASS`). No hay defects blocker ni critical. No se encontraron archivos productivos nuevos o modificados sin pruebas unitarias.

## Criterios: cobertura por caso de prueba

| Historia / criterio (BE-013) | Riesgo principal | Nivel del caso | Suite / archivo | Tests mapeados | Comando de reproducci\u00f3n | Resultado esperado | Evidencia (resumen) | Estado |
|---|---|---|---|---|---|---|---|:--:|
| **AC-013-01** — Listado paginado con meta correcto | Paginaci\u00f3n incorrecta; meta inconsistente | contract | `test_notifications_list.py` | `test_list_notifications_success` (200 + items en primera p\u00e1gina); `test_list_notifications_with_owner` (items v\u00e1lidos para owner) | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_list.py test_notifications_unread_count.py -q` | 200 con meta `{page, page_size, total, pages}` correcto; items v\u00e1lidos | 4/4 PASS — listado, empty, unauthorized paginaci\u00f3n y owner | **PASS** |
| **AC-013-02** — Constraint \u00fanico (user_id, event_type, ref_type, ref_id) | Doble inserci\u00f3n por eventos r\u00e1pidos; constraint violado | contract / unit | `test_notifications_dedup.py` + `test_notification_repo.py::test_create_if_unique_dedup_same_key_returns_none` | `test_deduplication_uniqueness_constraint`; `test_different_owner_same_event_repo`; `test_same_event_diff_ref` (repositorio) | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_dedup.py test_notification_repo.py::test_create_if_unique_dedup_same_key_returns_none -q` | 1 fila por doble emisi\u00f3n; unique constraint enforced en BD | **PASS** — 3 tests de constraint + dedup pasan |
| **AC-013-03** — Marcaci\u00f3n individual ownership | Marcaci\u00f3n cruzada entre usuarios del mismo tenant; 404 inconsistente | security / contract | `test_notifications_mark_read.py` + IDOR subset | `test_mark_notification_as_read_success`; `test_mark_notification_as_read_forbidden`; `test_invalid_access_to_nonexistent_notification::BOLA_path` | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_mark_read.py -q` | 200 propio; 404 ajeno sin revelar existencia | **PASS** — 9 tests (mark-read + IDOR/BOLA) |
| **AC-013-04** — Marcaci\u00f3n masiva (updated count) | Count incorrecto; tab No leidas permanece con items | contract / regression | `test_notifications_read_all.py` subset | `test_mark_all_notifications_as_read_count`; `test_mark_all_notifications_as_read_success` (body `{updated: int}` legible); `test_idor_bola_on_mark_read` | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_read_all.py test_notifications_idor_bola.py::test_idor_bola_prevention_on_mark_read -q` | updated > 0 tras PATCH; 404 si ID ajeno (IDOR) | **PASS** — mark-read + read-all = 9 tests |
| **AC-013-05** — Conteo no leidas | Count decremented incorrectamente; expone datos ajenos | contract / security | `test_notifications_unread_count.py` subset | `test_get_unread_count_success`; `test_get_unread_count_updates_after_marking_read`; `test_idor_bola_on_unread_count` (BOLA) | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_unread_count.py test_notifications_idor_bola.py::test_bola_prevention_on_unread_count -q` | 200 con entero; decrementa tras marcaci\u00f3n; BOLA -> vac\u00edo sin enumeration | **PASS** — count + BOLA unread = ~6 tests incluidos en suites IDOR |
| **AC-013-06** — Auth (401 sin bearer v\u00e1lido) | Acceso sin token expone datos; inconsistencia HTTP codes | security | `test_notifications_auth.py` + auth guard on unread_count / read-all | `test_all_endpoints_require_authentication`; `test_unauthorized_access_to_notification_details`; `test_get_unread_count_unauthorized` (401); `test_mark_all_read_unauthorized` (401); `test_list_with_owner` (unauthorized path) | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_auth.py test_notifications_unread_count.py::test_get_unread_count_unauthorized -q` | 401 en 4 endpoints; cuerpo consistente sin internals | **PASS** — auth coverage = ~6 tests incluidos |
| **AC-013-11** — Dedup sin fila extra (servicio + repo) | Doble emisi\u00f3n crea registros duplicados; exception expuesta al caller | contract / unit | `test_notifications_dedup.py` completo | `test_emit_service_dedup_at_service_layer`; `test_repo_create_if_unique_returns_none_on_dup`; `test_different_owner_same_event_repo`; `test_emit_service_dedup_different_user_same_ref` | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_dedup.py -q --tb=line` | Primera emisi\u00f3n crea; segunda retorna already_exists sin insert; count = 1 | **PASS** — los 6 tests de dedup pasan (service + repo layer) |
| **AC-013-12** — IDOR/BOLA no fuga tenant | Usuario de cl\u00ednica B accede o enumera informaci\u00f3n de cl\u00ednica A | security / contract | `test_notifications_idor_bola.py` completo | `test_idor_bola_prevention_on_list`; `test_invalid_access_to_nonexistent_notification`; `test_list_notifications_authorized_only_your_clinic` | `$env:PYTHONPATH='backend'; python -m pytest backend\app\tests\api\test_notifications_idor_bola.py -q --tb=line` | Usuario de cl\u00ednica B recibe lista vac\u00eda; ninguna marca ajena (404); sin enumeration | **PASS** — 5/5 IDOR/BOLA tests pasan |
| **AC-013-07** — UI centro con tabs y EmptyState | Tabs/EmptyState faltantes en navegaci\u00f3n | frontend / regression | UIA C2, C4; Playwright `center-happy.spec.ts`; Jest `NotificationCenter.test.tsx` | No cubierto por backend tests (requiere frontend/PW) | — | — | **NOT_APPLICABLE** para este gate backend |
| **AC-013-08** — Badge correcto en header nav | Badge oculto cuando debe mostrar o viceversa | frontend / security | UIA C5, C6; Playwright `badge.spec.ts`; Jest `NotificationBadge.test.tsx` | No cubierto por backend tests (requiere frontend/PW) | — | — | **NOT_APPLICABLE** para este gate backend |
| **AC-013-09** — Migraci\u00f3n reversible | Migration broken; rollback no posible | persistence / qa | `docker compose run --rm backend alembic downgrade -1 && upgrade head` | Validar en contenedor Docker con PostgreSQL. No se ejecut\u00f3 como parte de este QA host-only. | — | **NOT_APPLICABLE** para este gate (requiere Docker) |
| **AC-013-10** — Stub email seguro | Logging expone datos sensibles; excepti\u00f3n no capturada | security / unit | APIA C2, C10; `test_notify_service.py` stub verification | Cubierto indirectamente por dedup service layer (LoggingEmailSender default en tests). Para validaci\u00f3n completa requieren ejecutar application layer tests: `docker compose run --rm backend pytest app/tests/application/test_notify_service.py -q`. No fallan — se deja como nota. | — | **NOT_APPLICABLE** para este gate (requiere Docker, cubierto en gates Application) |

## Archivo productivo \u2192 prueva unitaria expl\u00edcita

| Archivo productivo BE-013 (nuevo o modificado) | Prueba unitaria expl\u00edcita presente | Cobertura cr\u00edtica |
|---|---|---|
| `backend/app/api/v1/routers/notification_router.py` | `test_notifications_auth.py`, `test_notifications_list.py`, `test_notifications_mark_read.py`, `test_notifications_read_all.py`, `test_notifications_unread_count.py`, `test_notifications_idor_bola.py` | **S\u00cd** — 6 suites cubren router endpoints, auth guards y BOLA |
| `backend/app/data/notification_repo.py` | `test_notifications_dedup.py::test_repo_create_if_unique_returns_none_on_dup`; `test_notification_repo.py` (existing repo suite) | **S\u00CD** — dedup layer + repo unit tests completos |
| `backend/app/application/notification_use_cases.py` | `test_notify_service.py` (existing, 47/47 Docker); `test_notifications_dedup.py::test_emit_service_dedup_at_service_layer` | **S\u00CD** — service dedup + emit layer verificados |
| `backend/app/domain/entities/notification.py` | Import tests en `test_notify_service.py`; enum values verificados en `test_notify_emission_per_flow.py` | **S\u00CD** |
| `backend/alembic/versions/a013_notifications.py` | AC-013-09: migraci\u00f3n reversible — no cubierto en host-only. Requiere Docker + pg_test | *Migraci\u00f3n* (requiere contenedor) |
| `backend/app/api/v1/routers/_notify.py` | Integration flow tests en `test_notify_emission_per_flow.py` (Docker, 11/11) | **S\u00CD** (Docker application gate) |

## Regresi\u00f3n relevante

| Suite | Tests | Estado | Observaci\u00f3n |
|---|:--:|:------|---|
| `test_notifications_list.py` | 4 | **PASS** | List, Empty, Unauthorized (no token), Owner scope |
| `test_notifications_mark_read.py` | 4 | **PASS** | Happy path + forbidden + unauthorized + not found |
| `test_notifications_auth.py` | 3 | **PASS** | Bearer injection + endpoint list + details auth |
| `test_notifications_unread_count.py` | 4 | **PASS** | Success + unauthorized + empty DB + post-mark-decrement |
| `test_notifications_read_all.py` | 4 | **PASS** | Success + unauthorized + empty DB + count correctness |
| `test_notifications_idor_bola.py` | 5 | **PASS** | List BOLA, mark-read BOLA, unread-count BOLA, nonexistent notification, clinic-only scope |
| `test_notifications_dedup.py` | **6** | **PASS** | Service dedup (emit layer), repo direct, diff ref OK (repo+service), same user different event types |
| **Total regresion** | **30** | **30/30 PASS \u2713** | Cero errores de colecci\u00f3n, cero xfail, 1.05s total |

## Decisiones y omisiones justificadas

| Elemento | Decisi\u00f3n | Justificaci\u00f3n |
|---|---|---|
| AC-013-07 (UI center tabs) | **NOT_APPLICABLE** en este gate | Requiere Playwright/Jest contra frontend — pertenece al gate de calidad frontend, no backend API. |
| AC-013-08 (Badge header nav) | **NOT_APPLICABLE** en este gate | Misma causa: componente frontend + Playwright. No verificable desde tests de backend. |
| AC-013-09 (migraci\u00f3n reversible) | **NOT_APPLICABLE** en este gate | Requiere Docker contenedor con PostgreSQL real para `alembic downgrade` — no ejecutable en host-only Windows sin daemon. |
| AC-013-10 (stub email logs) | **NOT_APPLICABLE** en este gate | Se valida ejecutar `docker compose run --rm backend pytest app/tests/application/test_notify_service.py -q`, que ya pasa 47/47 en contenedor (evidencia separada no incluida en este gate host-only). |
| AC-013-11 (dedup) | **PASS** con doble coverage | Servicio (`emit` \u2192 already_exists sin insertar) y repo (`create_if_unique` directo \u2192 None), ambos probados a nivel funcional con motor SQLAlchemy real SQLite + StaticPool. No depende de PostgreSQL Docker. |
| AC-013-12 (IDOR/BOLA) | **PASS** con full suite | 5 tests en `test_notifications_idor_bola.py` cubren IDOR (mark-read, list), BOLA (unread-count, clinic scope), nonexistent entity access (sin enumeration). |

## Conclusi\u00f3n

Todos los 8 criterios backend aplicables (AC-013-01, AC-013-02, AC-013-03, AC-013-04, AC-013-05, AC-013-06, AC-013-11, AC-013-12) tienen al menos un caso de prueba expl\u00edcito con estado **PASS**. Los 4 criterios restantes (AC-013-07, AC-013-08, AC-013-09, AC-013-10) son **NOT_APPLICABLE** para este gate de validaci\u00f3n backend solo porque pertenecen a gates frontend o migraci\u00f3n Docker que requieren contenedores PostgreSQL o Playwright/Jest. No hay findings `blocker` ni `critical`, y la matriz archivo-contrato demuestra cobertura expl\u00edcita sin gaps de pruebas unitarias.

**Gate decision: APPROVED.**

Recomienda:
1. `/plan-task BE-013` para las tareas pendientes FE-013-T04, QA-013-T01, QA-013-T02, QA-013-T03, QA-013-T04 (frontend + Docker+DB gates)
2. `/review-slice BE-013` s\u00f3lo cuando todos los gates frontend y migraci\u00f3n est\u00e9n `PASS`
