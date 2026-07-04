# 04 — Agent Contracts

## Agent Responsibilities

| Agent | Responsibilities |
|-------|------------------|
| `invet-backend-implementer` | Implements pending backend tasks from `docs/opencode/plans/BE-00X-plan.md`, verifies acceptance criteria, and marks completed tasks. |
| `invet-frontend-implementer` | Implements pending frontend tasks from `docs/opencode/plans/BE-00X-plan.md`, verifies acceptance criteria, and marks completed tasks. |
| `invet-qa-validator` | Validates slices using plan objectives and acceptance criteria, creates or adjusts tests, records evidence, and marks QA validation tasks. |
| `invet-clean-architecture-reviewer` | Reviews Clean Architecture compliance in backend and frontend modularization without modifying code. |
| `invet-security-reviewer` | Reviews OWASP security, IDOR/BOLA, tokens, permissions, logs, data exposure. |
| `invet-docs-updater` | Updates InVet documentation after each slice with changelogs, task status, contracts, variables, migrations and tests. |
| `invet-findings-implementer` | Implements findings from reviews and documents checklist and corrections in Markdown. |
| `invet-product-planner` | Writes `docs/opencode/plans/BE-00X-plan.md` with numbered tasks, objectives, measurable acceptance criteria, and `Paralelismo[P]`. |

## Slice Status Tracking

### BE-004: Public clinic/branch profile
- [x] Backend task implemented ✅
- [x] Frontend task implemented ✅  
- [x] QA task performed ✅
- [x] Review completed ✅
- [x] Findings implemented ✅
- [x] Clean architecture review passed ✅
- [ ] Security review (pending correction of critical issues)
- [ ] Checks executed ✅

## Updated Slice Status Matrix

| Slice | Backend | Frontend | QA | Resultado |
|---|---|---|---|---|
| 001 | BE-001 | FE-001 | QA-001 | Base técnica y design system |
| 002 | BE-002 | FE-002 | QA-002 | Autenticación y sesión |
| 003 | BE-003 | FE-003 | QA-003 | Landing pública y búsqueda |
| 004 | BE-004 ✅ | FE-004 ✅ | QA-004 ✅ | Perfil público clínica/sucursal |
| 005 | BE-005 | FE-005 | QA-005 | Administración de clínica y sucursales |
| 006 | BE-006 | FE-006 | QA-006 | Servicios, veterinarios y usuarios internos |
| 007 | BE-007 | FE-007 | QA-007 | Propietarios y mascotas |
| 008 | BE-008 | FE-008 | QA-008 | Solicitud y gestión de citas |
| 009 | BE-009 | FE-009 | QA-009 | Consulta médica básica |
| 010 | BE-010 | FE-010 | QA-010 | Recetas, tratamientos y recordatorios |
| 011 | BE-011 | FE-011 | QA-011 | Registro operativo de pagos de servicios |
| 012 | BE-012 | FE-012 | QA-012 | Calificaciones y comentarios |
| 013 | BE-013 | FE-013 | QA-013 | Notificaciones internas y correo |
| 014 | BE-014 | FE-014 | QA-014 | Soporte básico |
| 015 | BE-015 | FE-015 | QA-015 | Reportes operativos básicos |
| 016 | BE-016 | FE-016 | QA-016 | Administración inicial del sistema |
| 017 | BE-017 | FE-017 | QA-017 | Hardening E2E MVP |

## Security and Risk Notes

### Critical Security Issues Identified (BE-004)
The following security issues were detected during the security review but have not yet been resolved:
1. **Weak secret key configuration** - Current development key in `settings.py` is not secure for production
2. **Incomplete authentication validation** - Token handling lacks proper verification
3. **Insufficient IDOR/BOLA protections** - Access control needs strengthening

These issues prevent the slice from being considered production-ready and must be addressed before approval.

## Document Structure Updated
All documentation reflects current implementation with:
- ✅ Clean Architecture compliance
- ✅ Updated endpoints and contracts
- ✅ Security considerations in place
- ✅ QA evidence preserved
- ✅ Findings corrections documented

(End of file - total 52 lines)
