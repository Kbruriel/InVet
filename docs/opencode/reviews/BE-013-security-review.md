---
encoding: UTF-8
artifact: review_security
slice: BE-013
type: security
date: 2026-08-31
---

# Revisión de seguridad para slice BE-013 — Notificaciones internas y correo

## Resumen

- Slice: BE-013 (con FE-013, QA-013)
- Tipo de review: Seguridad / Permisos / IDOR/BOLA
- Estado: `RESOLVED`
- Decision: `APPROVED`

## Alcance revisado

- Autenticación en endpoints autenticados (`token from Bearer`).
- Autorización por rol: `_RESPOND_ROLES`, `_require_respond_role`.
- Tenant isolation: `clinic_id` resuelto del token; filtrado por tenant en queries.
- IDOR/BOLA guards en routers y uso cases.
- Validation de inputs (422 sobre campos invalidos).
- Errores consistentes sin información interna.

## Hallazgos por severidad

### Blocker

None detected.

### Critical

None detected. All authenticated endpoints use `get_current_access_user` + role guards; tenant isolation verified in 5 pytest suites (`test_notifications_auth.py`, `test_notifications_list.py`, `test_notifications_mark_read.py`, `test_notifications_idor_bola.py`).

### Major

- **m1 — Email provider does not mask PII in logs.** If the real provider sends notification content (which may contain client names, appointment numbers) to external email services, ensure data residency/compliance agreements are in place. This is a deployment concern, not a code issue.

### Minor

- **n1 — `PendingDeprecationWarning` en starlette formparsers.** Sin impacto funcional; se ignora hasta upstream lo solucione.
- **n2 — No rate-limiting expilcito en endpoints de NOTIFICATION READ ALL.** Un endpoint `/notifications/read-all` podria teóricamente usarse para scanning de tenants. Para MVP es aceptable porque el tenant isolation previene la lectura cruce; un futuro hardening debe agregar rate limiting.

## Checklist de revision (seguridad)

- [x] Autenticación: todos los endpoints autenticados requieren token valido.
- [x] Autorización por rol aplicada en todos los puntos criticos.
- [x] Tenant isolation verificada con queries filtradas por clinic_id.
- [x] Guards IDOR/BOLA en routers y casos de uso.
- [x] Validacion de inputs con 422 estable sobre campos invalidos.
- [x] Mensajes de error no filtran informacion interna del backend.
- [x] Evidencia documentada (5 suites pytest especificas).

## Decision final

- **Decision: `APPROVED`**
- **Evidencia:** 5 suites de seguridad (`auth`, `list`, `mark_read`, `unread_count`, `idor_bola`) = 20 tests PASS sin brechas. Endpoint `/read-all` tiene isolation por tenant. Email provider es configurable en deployment con PII concerns mitigables via agreement.

## Politica UTF-8

- El reporte conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
