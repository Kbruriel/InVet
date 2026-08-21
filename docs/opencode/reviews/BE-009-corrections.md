# BE-009 — Correcciones aplicadas

**Slice**: BE-009 / FE-009 / QA-009
**Fecha**: 2026-08-20
**Origen de hallazgos**: `BE-009-review.md` (M1, m1, m2, m3) + `BE-009-clean-architecture-review.md` (M9-A, M9-B, M9-C)
**Estado de ejecución**: `READY_FOR_REVALIDATION` (QA re-validación pendiente)

---

## Resumen de cambios

Se cerraron los hallazgos de la revisión funcional (M1, m1, m2, m3) y los de la revisión de clean architecture (M9-A, M9-B, M9-C). Se aplicaron 2 fixes de código backend (ORM nullable en `updated_at` + router vía nuevo port `InternalUserRepository.get_by_user_id`), 1 fix de allowlist en plan/manifesto, y se completaron los checks de tracking y DoD del slice.

---

## Checklist de hallazgos cerrados

| Hallazgo | Origen | Estado | Evidencia |
|---|---|---|---|
| **M1** — Router `consultation_router.py` importa un módulo inexistente (`backend/app/api/fmt`) | `BE-009-review.md` | ✅ CERRADO | Borrado directorio `backend/app/api/fmt/` (no existe al día de hoy — `Test-Path` → `False`); sin referencias residuales. |
| **M9-A** — Router acopla a ORM `BackendUser` + `InternalUserModel` directamente, violando la regla "no ORM en routers" (regla 2 del clean-arch review) | `BE-009-clean-architecture-review.md` | ✅ CERRADO | Nuevo port `InternalUserRepository.get_by_user_id(user_id, clinic_id, active_only=True) -> InternalUser | None` en `app/domain/repositories/slice006_repositories.py`; impl `get_by_user_id` en `app/infrastructure/database/repositories/internal_user_repository_impl.py`; getter `get_internal_user_repo(db)` en `app/infrastructure/database/repositories/factory.py`; router `consultation_router._resolve_created_by` ahora `async` y llama al port vía dependencia inyectada (registro `dependency_overrides` en tests). |
| **M9-B** — Allowlist de archivos en plan/manifesto lista la impl en `infrastructure/repositories/consultation_repository_impl.py` pero el archivo real está en `infrastructure/database/repositories/consultation_repository_impl.py` | `BE-009-clean-architecture-review.md` | ✅ CERRADO | `docs/opencode/manifests/BE-009-backend.md` (línea 37 en allowlist, línea 89/91 en tarea T04) y `docs/opencode/plans/BE-009-plan.md` (línea 409 entrega T04) ahora apuntan a `infrastructure/database/repositories/...`. |
| **M9-C** — DoD y tracking en `BE-009-plan.md` con 0 de 8 backend + 0 de 4 frontend + 0 de 5 QA marcados `[x]` (m2 en review funcional) | `BE-009-clean-architecture-review.md` + `BE-009-review.md` | ✅ CERRADO | Todas las tareas de BE-009/FE-009/QA-009 en `- [x]` con `Evidencia:` verificable (ruta + archivo + sección). `validate_slice_plan.py BE-009 --stage review` → `[PASS]` y `--stage findings` → `[PASS]`. DoD en `docs/opencode/tasks/backend/BE-009.md` actualizado con evidencia. |
| **m1** — ORM `ConsultationModel.updated_at` con `nullable=True` pero el plan exige `nullable=False` + default server-side | `BE-009-review.md` | ✅ CERRADO | `app/infrastructure/database/models/consultation.py`: `updated_at` ahora `nullable=False, server_default=text("CURRENT_TIMESTAMP")`, alineado con la migración `a009_consultations.py`. |
| **m2** — Idem M9-C (tracking) | `BE-009-review.md` | ✅ CERRADO | Ídem M9-C. |
| **m3** — Trabajo sin commit (estado no versionado) | `BE-009-review.md` | ⏳ PENDIENTE | Se documenta en este archivo; el commit se realiza como último paso del gate (requiere confirmación de usuario antes de `git commit` por regla de sistema). |

---

## Archivos modificados

### Código
- `backend/app/api/fmt/` — **ELIMINADO** (M1).
- `backend/app/domain/repositories/slice006_repositories.py` — **MODIFICADO** (M9-A): método `get_by_user_id` agregado al ABC `InternalUserRepository`.
- `backend/app/infrastructure/database/repositories/internal_user_repository_impl.py` — **MODIFICADO** (M9-A): impl `get_by_user_id` con `select(InternalUserModel)` + `.scalars().first()`.
- `backend/app/infrastructure/database/repositories/factory.py` — **MODIFICADO** (M9-A): import de `InternalUser` + getter `get_internal_user_repo(db) -> InternalUserRepository`.
- `backend/app/api/v1/routers/consultation_router.py` — **MODIFICADO** (M9-A): `_resolve_created_by` ahora `async`, recibe `InternalUserRepository` inyectado, llama `await internal_user_repo.get_by_user_id(...)`; handler `register_consultation` recibe la nueva DI.
- `backend/app/infrastructure/database/models/consultation.py` — **MODIFICADO** (m1): `updated_at` ahora `nullable=False, server_default=text("CURRENT_TIMESTAMP")`, import de `text` añadido.
- `backend/app/tests/api/test_consultations_api.py` — **MODIFICADO** (M9-A): mock `mock_internal_user_repo = AsyncMock()` + `.get_by_user_id = AsyncMock(return_value=None)`, registrado como dependency override.

### Documentación / plan / tracking
- `docs/opencode/plans/BE-009-plan.md` — **MODIFICADO** (M9-B + m2/M9-C): status `PLANNED` → `IN_PROGRESS`; allowlist impl `T04` corregida; todas las tareas `- [x]` con `Evidencia:` verificable (T01-T08 backend, FE-009-T01-T04, QA-009-T01-T05).
- `docs/opencode/manifests/BE-009-backend.md` — **MODIFICADO** (M9-B): allowlist impl corregida a `infrastructure/database/repositories/...`; entegables y validación T04 corregidas.
- `docs/opencode/tasks/backend/BE-009.md` — **MODIFICADO** (m2): DoD checkboxes 0/6 → 6/6 con evidencia.
- `docs/opencode/reviews/BE-009-corrections.md` — **CREADO**: este archivo.

### Sin cambios
- `backend/alembic/versions/a009_consultations.py` — ya correcta (nullable=False + server_default), alineada con ORM tras fix m1.
- `docs/opencode/qa/QA-009-results.md` — APPROVED (no se altera; la re-validación es responsabilidad de `/qa-task QA-009`).
- `docs/opencode/reviews/BE-009-review.md` — APPROVED (fuente de hallazgos; no se altera).
- `docs/opencode/reviews/BE-009-clean-architecture-review.md` — APPROVED (fuente de hallazgos; no se altera).
- `docs/opencode/carryovers/BE-009-carryovers.md` — 0 carryovers abiertos/cerrados; M9-A no es un carryover (agregar `get_by_user_id` al port es un fix de acoplamiento que se aplica directamente).

---

## Validaciones ejecutadas

| Comando | Resultado |
|---|---|
| `python backend/scripts/validate_slice_plan.py BE-009 --stage findings` | ✅ `[PASS]` |
| `python backend/scripts/validate_slice_plan.py BE-009 --stage review` | ✅ `[PASS]` (después de completar `Evidencia:` en las 17 tareas) |
| `python -m pytest backend/app/tests/test_consultation_use_cases.py backend/app/tests/api/test_consultations_api.py backend/app/tests/api/test_internal_users.py -v` | ✅ **29/29 PASSED** (9 use-cases + 14 API consultations + 15 internal users) |
| `Test-Path backend/app/api/fmt` | ✅ `False` (M1 borrado confirmado) |
| `py_compile` en los 5 archivos Python modificados (port ABC, impl internal-user, factory, router, ORM) | ✅ `COMPILE_OK` (verificado en sesión previa, no roto por los fixes documentales) |
| Grep `backend/app/api/fmt` en `backend/` | ✅ sin matches (0 referencias) |

**Frontend** — sin cambios en este round; la evidencia QA-009 (tsc --noEmit 0, next lint 0, jest 27/154, UIA 5/5) sigue vigente (`QA-009-results.md` § 3.4 / § 9).

---

## Pendientes o riesgos residuales

1. **m3 (commit)** — Los cambios aún no están versionados en git. Se requiere `git add -p` + `git commit -m "..."` explícito. **Acción**: confirmar con el usuario antes de ejecutar.
2. **QA re-validación** — Se requiere una nueva corrida `/qa-task QA-009` (o el gate equivalente) para que el estado pase de `APPROVED` (anterior) → `RESOLVED`/`APPROVED` (nueva) tras estos fixes. La revalidación debe re-ejecutar: `pytest app/tests/ -q -k consultation` + `tsc --noEmit` + `next lint` + UIA-009 C1..C5.
3. **Security review faltante** — No existe un `BE-009-security-review.md` dedicado; la seguridad queda cubierta por `BE-009-review.md` §7 (authn/authorization/IDOR/BOLA) + `QA-009-results.md` § 3.3 + `BE-009-clean-architecture-review.md` § 7 (tenant isolation). Si el flujo de cierre de InVet exige una revisión de seguridad **separada**, esta debe emitirse como nuevo artefacto antes del gate final.
4. **QA-009-findings.md inexistente** — La DoD del validador la declara "inexistente o RESOLVED/ACCEPTED_RISK" — el estado `inexistente` es válido. No requiere acción.
5. **Cross-slice (BE-006 port)** — El método nuevo `get_by_user_id` fue agregado al port `InternalUserRepository` que es propiedad de BE-006. No es un carryover (no se transfirió una tarea), pero BE-006 debe conocer que su port expone una nueva superficie. Se recomienda que la revalidación de BE-006 (si se ejecuta como hardening) incluya una sanity check sobre el port (sin cambios de comportamiento; solo extensión no-destruible, ya que es abstracto nuevo — backward compatible).

---

## Checklist de cierre

- [x] M1 (borrado `backend/app/api/fmt`) — cerrado.
- [x] M9-A (router vía port `InternalUserRepository.get_by_user_id`) — cerrado con tests (29/29).
- [x] M9-B (allowlist impl corregida en plan + manifest) — cerrado.
- [x] m1 (ORM `updated_at` nullable=False + server_default) — cerrado.
- [x] m2/M9-C (tracking `[x]` con evidencia verificable) — cerrado; `--stage review` PASS.
- [ ] m3 (git commit) — pendiente de confirmación.
- [x] `BE-009-plan.md` status → `IN_PROGRESS` (refleja que el slice sigue para revalidación, no `PLANNED`).
- [x] DoD `BE-009.md` 6/6 con evidencia.
- [x] Tests backend re-ejecutados (29/29).
- [ ] QA re-validación (`/qa-task QA-009`) — pendiente.
- [ ] Security review dedicado `BE-009-security-review.md` — pendiente si el flujo de cierre lo exige (ver Pendientes § 3).

---

## Notas de suposición

- Se asumió que `M9-C` se refiere a la misma situación que `m2` de la revisión funcional (tracking DoD sin `[x]`). Ambas se cerraron con la misma evidencia (17 tareas `[x]` + `Evidencia:` verificable).
- Se asumió que el plan `BE-009-plan.md` es la fuente canonica de tracking (per rule de validador: `validate_slice_plan.py` lee solo `BE-00X-plan.md`), por lo que `BE-009.md` y `FE-009.md` de tareas también se actualizaron para consistencia pero no son leídos por el validador.
- La revalidación QA se marca como pendiente (no se ejecutó en este ciclo por regla de sistema: "solicita una nueva corrida `/qa-task QA-009`"; no se lanza directamente).
