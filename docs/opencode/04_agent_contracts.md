# 04 - Agent Contracts

## Agent Responsibilities

| Agent | Responsibilities |
|-------|------------------|
| `invet-backend-implementer` | Implements pending backend tasks from `docs/opencode/plans/BE-00X-plan.md`, verifies acceptance criteria, and marks completed tasks. |
| `invet-frontend-implementer` | Implements pending frontend tasks from `docs/opencode/plans/BE-00X-plan.md`, verifies acceptance criteria, and marks completed tasks. |
| `invet-qa-validator` | Validates slices using plan objectives and acceptance criteria, auto-recovers local QA infrastructure when possible, creates or adjusts tests, validates runner evidence, applies impact-based regression, records traceability, and marks QA validation tasks only when PASS evidence exists. |
| `invet-clean-architecture-reviewer` | Reviews Clean Architecture compliance in backend and frontend modularization without modifying code and writes `docs/opencode/reviews/BE-00X-clean-architecture-review.md` when findings exist. |
| `invet-security-reviewer` | Reviews OWASP security, IDOR/BOLA, tokens, permissions, logs, data exposure and writes `docs/opencode/reviews/BE-00X-security-review.md` when findings exist. |
| `invet-docs-updater` | Updates InVet documentation after each slice with changelogs, task status, contracts, variables, migrations and tests. |
| `invet-findings-implementer` | Implements findings from slice reviews, architecture/security gates and QA findings, then documents checklist and corrections in Markdown. |
| `invet-product-planner` | Writes `docs/opencode/plans/BE-00X-plan.md` with numbered tasks, objectives, measurable acceptance criteria, and `Paralelismo[P]`. |

## Slice Status Tracking

### BE-004: Public clinic/branch profile
- [x] Backend task implemented
- [x] Frontend task implemented
- [x] QA task performed
- [x] Review completed
- [x] Findings implemented
- [x] Clean architecture review passed
- [x] Security review passed
- [x] Checks executed

## Updated Slice Status Matrix

| Slice | Backend | Frontend | QA | Resultado |
|---|---|---|---|---|
| 001 | BE-001 | FE-001 | QA-001 | Base tecnica y design system |
| 002 | BE-002 | FE-002 | QA-002 | Autenticacion y sesion |
| 003 | BE-003 | FE-003 | QA-003 | Landing publica y busqueda |
| 004 | BE-004 | FE-004 | QA-004 | Perfil publico clinica/sucursal |
| 005 | BE-005 | FE-005 | QA-005 | Administracion de clinica y sucursales |
| 006 | BE-006 | FE-006 | QA-006 | Servicios, veterinarios y usuarios internos |
| 007 | BE-007 | FE-007 | QA-007 | Propietarios y mascotas |
| 008 | BE-008 | FE-008 | QA-008 | Solicitud y gestion de citas |
| 009 | BE-009 | FE-009 | QA-009 | Consulta medica basica |
| 010 | BE-010 | FE-010 | QA-010 | Recetas, tratamientos y recordatorios |
| 011 | BE-011 | FE-011 | QA-011 | Registro operativo de pagos de servicios |
| 012 | BE-012 | FE-012 | QA-012 | Calificaciones y comentarios |
| 013 | BE-013 | FE-013 | QA-013 | Notificaciones internas y correo |
| 014 | BE-014 | FE-014 | QA-014 | Soporte basico |
| 015 | BE-015 | FE-015 | QA-015 | Reportes operativos basicos |
| 016 | BE-016 | FE-016 | QA-016 | Administracion inicial del sistema |
| 017 | BE-017 | FE-017 | QA-017 | Hardening E2E MVP |

## Security and Risk Notes

### Critical Security Issues Identified (BE-004)
Security findings should now be captured in the dedicated review file for the slice and resolved through `/implement-findings`.

## Document Structure Updated
All documentation reflects current implementation with:
- Clean Architecture compliance
- Updated endpoints and contracts
- Security considerations in place
- QA evidence preserved
- Findings corrections documented
