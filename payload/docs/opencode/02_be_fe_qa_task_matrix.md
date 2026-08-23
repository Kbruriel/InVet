# 02 - Matriz US/BE/FE/QA/UIA/APIA por slice

| Slice | User stories | Backend | Frontend | QA | UI Automation | API Automation | Resultado | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001 | US-001 | BE-001 | FE-001 | QA-001 | UIA-001 | APIA-001 | Base tecnica y design system | CLOSED |
| 002 | US-002 | BE-002 | FE-002 | QA-002 | UIA-002 | APIA-002 | Autenticacion y sesion |
| 003 | US-003 | BE-003 | FE-003 | QA-003 | UIA-003 | APIA-003 | Landing publica y busqueda |
| 004 | US-004 | BE-004 | FE-004 | QA-004 | UIA-004 | APIA-004 | Perfil publico clinica/sucursal |
| 005 | US-005 | BE-005 | FE-005 | QA-005 | UIA-005 | APIA-005 | Administracion de clinica y sucursales |
| 006 | US-006 | BE-006 | FE-006 | QA-006 | UIA-006 | APIA-006 | Servicios, veterinarios y usuarios internos |
| 007 | US-007 | BE-007 | FE-007 | QA-007 | UIA-007 | APIA-007 | Propietarios y mascotas | IMPLEMENTED |
| 008 | US-008 | BE-008 | FE-008 | QA-008 | UIA-008 | APIA-008 | Solicitud y gestion de citas | APPROVED |
| 009 | US-009 | BE-009 | FE-009 | QA-009 | UIA-009 | APIA-009 | Consulta medica basica | APPROVED |
| 010 | US-010 | BE-010 | FE-010 | QA-010 | UIA-010 | APIA-010 | Recetas, tratamientos y recordatorios |
| 011 | US-011 | BE-011 | FE-011 | QA-011 | UIA-011 | APIA-011 | Registro operativo de pagos de servicios |
| 012 | US-012 | BE-012 | FE-012 | QA-012 | UIA-012 | APIA-012 | Calificaciones y comentarios |
| 013 | US-013 | BE-013 | FE-013 | QA-013 | UIA-013 | APIA-013 | Notificaciones internas y correo |
| 014 | US-014 | BE-014 | FE-014 | QA-014 | UIA-014 | APIA-014 | Soporte basico |
| 015 | US-015 | BE-015 | FE-015 | QA-015 | UIA-015 | APIA-015 | Reportes operativos basicos |
| 016 | US-016 | BE-016 | FE-016 | QA-016 | UIA-016 | APIA-016 | Administracion inicial del sistema |
| 017 | US-017 | BE-017 | FE-017 | QA-017 | UIA-017 | APIA-017 | Hardening E2E MVP |

## Regla de equivalencia

```text
US-00X -> BE-00X -> FE-00X -> QA-00X -> UIA-00X -> APIA-00X
```

El planner no debe mezclar indices salvo que documente una dependencia explicita.
Cada criterio `CA-NN` debe quedar cubierto por UI automation, API automation o una justificacion manual.

## Gobernanza de carryovers

- Si una tarea pasa de un slice a otro, la fila del slice solo puede considerarse cerrada cuando `docs/opencode/carryovers/BE-00X-carryovers.md`, el plan origen y el plan destino muestran la misma evidencia o una referencia explicita al cierre.
- `OPEN` o `TRANSFERRED` en el registro de carryovers sigue bloqueando QA, reviews, checks y docs.
- Si la matriz muestra trabajo heredado, el planner debe actualizar tambien la trazabilidad del slice original antes de marcarlo como cerrado.
