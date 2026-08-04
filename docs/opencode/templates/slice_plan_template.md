---
schema_version: 2
slice: "XXX"
canonical_plan: BE-XXX
status: PLANNED
---

# BE-XXX Plan - Titulo del slice

## Objetivo del slice

## Alcance MVP

## Fuera de alcance

## Suposiciones

## Revision de gaps

## Entidades y reglas de negocio

## Endpoints esperados

## Contrato de implementacion frontend

### Rutas y acceso

### Flujos y estados UX

### Contratos API por accion

### Formularios y validacion

### Arquitectura de componentes

### Responsive y accesibilidad

### Estrategia de pruebas frontend

## Pruebas QA

## Riesgos de seguridad/IDOR/BOLA

## Checklist tecnico

## Checklist de tareas

Regla de granularidad: cada tarea debe tener un solo objetivo verificable y pequeno. Si un trabajo mezcla contratos, persistencia, API, UI, permisos, pruebas o documentacion, dividelo en tareas consecutivas.

### Backend

- [ ] BE-XXX-T01 - Titulo corto
  Capa: backend
  Objetivo: Un unico resultado pequeno y verificable.
  Depende de: Ninguna
  Entregables: Rutas concretas de archivos, endpoint o migracion.
  Criterios de aceptacion: Condiciones observables separadas por punto y coma.
  Validacion: Comando o inspeccion reproducible.
  Evidencia: pending
  Paralelismo[P]: No

### Frontend

- [ ] FE-XXX-T01 - Titulo corto
  Capa: frontend
  Objetivo: Un unico resultado pequeno y verificable.
  Depende de: BE-XXX-T01
  Entregables: Rutas, componentes, formularios o cliente API concretos.
  Criterios de aceptacion: Condiciones observables separadas por punto y coma.
  Validacion: Comando de prueba, typecheck o build.
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] QA-XXX-T01 - Titulo corto
  Capa: qa
  Objetivo: Validar un area concreta del slice.
  Depende de: BE-XXX-T01, FE-XXX-T01
  Entregables: Suites y reporte QA esperado.
  Criterios de aceptacion: Estados PASS requeridos y evidencia esperada.
  Validacion: Comandos y reportes machine-readable.
  Evidencia: pending
  Paralelismo[P]: No

## Definition of Done

