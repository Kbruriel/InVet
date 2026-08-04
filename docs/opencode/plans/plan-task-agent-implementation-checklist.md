---
schema_version: 2
slice: "000"
canonical_plan: BE-000
status: COMPLETED
---

# BE-000 Plan - Actualizacion del agente invet-product-planner

## Objetivo del slice

Actualizar el contrato operativo de `/plan-task` y del agente `invet-product-planner` para producir planes verticales compatibles con schema v2, con tareas atomicas, criterios medibles, paralelismo explicito y validacion determinista.

Este archivo conserva el checklist historico recuperado como plan auxiliar de mantenimiento. No representa un slice funcional de producto, pero usa la estructura schema v2 para que pueda auditarse con las mismas reglas documentales.

## Alcance MVP

- Actualizar el contrato del comando `/plan-task`.
- Actualizar las responsabilidades del agente `invet-product-planner`.
- Definir reglas de paralelismo para tareas generadas.
- Exigir criterios de aceptacion medibles.
- Actualizar documentacion operativa relacionada.
- Sincronizar el payload distribuible.
- Validar que el formato generado cumple la estructura solicitada.
- Documentar el cierre de la actualizacion.

## Fuera de alcance

- Implementar codigo fuente de producto.
- Ejecutar un slice funcional BE/FE/QA real.
- Eliminar o renombrar archivos historicos recuperados.
- Cambiar el motor de validacion fuera del contrato de planes.

## Suposiciones

- `/plan-task` debe aceptar IDs `BE-00X`, `FE-00X` y `QA-00X`, normalizando siempre al plan canonico `BE-00X-plan.md`.
- Los planes generados deben incluir tareas backend, frontend y QA trazables.
- La evidencia de esta actualizacion vive en agentes, comandos, documentacion y payload.

## Revision de gaps

- El checklist original recuperado no tenia frontmatter schema v2.
- El checklist original no usaba IDs de tarea `BE|FE|QA-000-TNN`.
- El checklist original no tenia todas las secciones obligatorias de un plan canonico.
- Este documento fue normalizado para conservar la informacion sin eliminarlo.

## Entidades y reglas de negocio

- `SlicePlan`: plan Markdown versionable con frontmatter schema v2.
- `TaskId`: identificador atomico con formato `BE|FE|QA-000-TNN`.
- `PlanContract`: reglas que debe cumplir `/plan-task`.
- `AgentContract`: responsabilidades del agente `invet-product-planner`.
- `PayloadMirror`: copia distribuible que debe mantenerse sincronizada.

Reglas:

- Cada tarea debe tener un unico objetivo verificable.
- Cada tarea debe declarar `Paralelismo[P]: Si` o `Paralelismo[P]: No`.
- Las tareas completadas deben incluir evidencia verificable.
- La documentacion activa y el payload no deben contradecirse.

## Endpoints esperados

No aplica a producto. Para compatibilidad schema v2, los contratos operativos equivalentes son:

- Comando slash `/plan-task`.
- Agente `.opencode/agents/invet-product-planner.md`.
- Validador `backend/scripts/validate_slice_plan.py`.
- Plantilla `docs/opencode/templates/slice_plan_template.md`.

## Contrato de implementacion frontend

### Rutas y acceso

No aplica a UI de producto. El acceso operativo se realiza mediante el comando slash `/plan-task BE|FE|QA-00X`.

### Flujos y estados UX

El flujo esperado para el desarrollador es:

- Ejecutar `/plan-task FE-00X`, `/plan-task BE-00X` o `/plan-task QA-00X`.
- Recibir un plan canonico `docs/opencode/plans/BE-00X-plan.md`.
- Confirmar que el plan contiene tareas BE, FE y QA con dependencias y evidencia.
- Corregir o regenerar el plan si el validador reporta errores.

### Contratos API por accion

No aplica a HTTP. Las acciones operativas son:

- `plan-task`: genera el plan canonico.
- `validate_slice_plan.py --stage plan`: valida schema, secciones, tareas y dependencias.

### Formularios y validacion

No aplica a formularios de producto. La validacion documental exige frontmatter schema v2, secciones obligatorias, subtitulos frontend y tareas con campos completos.

### Arquitectura de componentes

No aplica a componentes UI. Los componentes operativos son comando, agente, plantilla, validador, documentacion y payload.

### Responsive y accesibilidad

No aplica a UI. Para uso documental, el plan debe permanecer legible en Markdown plano y facil de revisar por cualquier desarrollador.

### Estrategia de pruebas frontend

No aplica a pruebas frontend de producto. La validacion equivalente es comprobar que el contrato frontend requerido por schema v2 queda representado en cada plan generado.

## Pruebas QA

- Ejecutar validacion de schema v2 sobre los planes `BE-00X-plan.md`.
- Revisar que cada tarea completada tenga evidencia no pendiente.
- Confirmar que el payload contiene los contratos equivalentes.
- Verificar que no hay contradicciones entre comando, agente, plantilla y documentacion.

## Riesgos de seguridad/IDOR/BOLA

- Riesgo: aceptar planes incompletos que omitan ownership, permisos o controles IDOR/BOLA.
- Mitigacion: exigir seccion de riesgos de seguridad/IDOR/BOLA y gate de persistencia segura.
- Riesgo: que QA avance por existencia de archivos sin decision aprobada.
- Mitigacion: usar `validate_slice_plan.py` como motor determinista de gates.

## Checklist tecnico

- El comando `/plan-task` exige salida schema v2.
- El agente `invet-product-planner` produce tareas atomicas.
- La plantilla de plan contiene secciones obligatorias.
- El validador rechaza planes legacy.
- El payload distribuible refleja el contrato activo.

## Checklist de tareas

### Backend

- [x] BE-000-T01 - Actualizar contrato del comando plan-task
  Capa: backend
  Objetivo: Exigir que `/plan-task` produzca planes schema v2 con tareas atomicas y paralelismo explicito.
  Depende de: Ninguna
  Entregables: `.opencode/commands/plan-task.md`; `payload/.opencode/commands/plan-task.md`.
  Criterios de aceptacion: El comando mantiene la regla de no implementar codigo; el resultado esperado incluye tareas numeradas, criterios de aceptacion y `Paralelismo[P]`.
  Validacion: Revisar el contrato del comando y buscar las reglas schema v2 documentadas.
  Evidencia: Contrato recuperado en `.opencode/commands/plan-task.md` y payload restaurado.
  Paralelismo[P]: No

- [x] BE-000-T02 - Actualizar responsabilidades del agente product planner
  Capa: backend
  Objetivo: Asegurar que `invet-product-planner` genere tareas atomicas y separadas por capa.
  Depende de: BE-000-T01
  Entregables: `.opencode/agents/invet-product-planner.md`; `payload/.opencode/agents/invet-product-planner.md`.
  Criterios de aceptacion: El agente conserva separacion MVP, etapas y fuera de alcance; ninguna responsabilidad combina backend, frontend y QA en una misma tarea.
  Validacion: Revisar el agente activo y su espejo en payload.
  Evidencia: Agente recuperado en `.opencode/agents/invet-product-planner.md` y payload restaurado.
  Paralelismo[P]: No

- [x] BE-000-T03 - Mantener validador determinista de planes
  Capa: backend
  Objetivo: Validar estructura, dependencias, evidencia y gates mediante `validate_slice_plan.py`.
  Depende de: BE-000-T01
  Entregables: `backend/scripts/validate_slice_plan.py`; `payload/backend/scripts/validate_slice_plan.py`.
  Criterios de aceptacion: El validador exige `schema_version: 2`; rechaza secciones faltantes, capas invalidas y dependencias inexistentes.
  Validacion: Ejecutar validacion de schema sobre planes recuperados.
  Evidencia: Los planes `BE-001`, `BE-002`, `BE-003`, `BE-005`, `BE-006`, `BE-007`, `BE-008`, `BE-009`, `BE-010`, `BE-011` y `BE-012` pasan `validate_plan_text`.
  Paralelismo[P]: No

### Frontend

- [x] FE-000-T01 - Definir contrato frontend obligatorio en planes
  Capa: frontend
  Objetivo: Garantizar que cada plan generado describa rutas, UX, contratos API, formularios, componentes, responsive, accesibilidad y pruebas frontend.
  Depende de: BE-000-T01
  Entregables: `docs/opencode/templates/slice_plan_template.md`; `docs/opencode/13_agents_architecture_and_gate_flow.md`.
  Criterios de aceptacion: La plantilla contiene las siete subsecciones frontend requeridas; el reporte de arquitectura documenta el contrato frontend schema v2.
  Validacion: Comparar la plantilla con las subsecciones requeridas por `validate_slice_plan.py`.
  Evidencia: Template recuperado y reporte de arquitectura actualizado.
  Paralelismo[P]: Si

- [x] FE-000-T02 - Documentar experiencia de uso del plan-task
  Capa: frontend
  Objetivo: Explicar el flujo que sigue un desarrollador al solicitar un plan con identificadores BE, FE o QA.
  Depende de: FE-000-T01
  Entregables: `docs/opencode/03_task_prompt_contracts.md`; `docs/opencode/11_chatgpt_project_context.md`; `docs/opencode/guia-uso-agentes-desarrolladores.md`.
  Criterios de aceptacion: La documentacion explica como especificar `FE-00X`, `BE-00X` o `QA-00X`; el resultado apunta al plan canonico BE del mismo indice.
  Validacion: Revisar referencias a `/plan-task` y normalizacion de IDs.
  Evidencia: Documentacion operativa recuperada y guia de uso para desarrolladores creada.
  Paralelismo[P]: Si

### QA

- [x] QA-000-T01 - Validar planes recuperados contra schema v2
  Capa: qa
  Objetivo: Confirmar que los planes canonicos recuperados cumplen el contrato estructural schema v2.
  Depende de: BE-000-T03, FE-000-T01
  Entregables: Resultado de validacion de planes en la revision actual.
  Criterios de aceptacion: Todos los archivos `BE-*-plan.md` pasan `validate_plan_text`; los fallos por QA anterior se clasifican como gates de avance, no errores de schema.
  Validacion: Ejecutar validacion enfocada en metadata, secciones, tareas, dependencias y campos requeridos.
  Evidencia: Validacion local reporto PASS para los 11 planes canonicos recuperados.
  Paralelismo[P]: No

- [x] QA-000-T02 - Documentar cierre de la actualizacion del planner
  Capa: qa
  Objetivo: Conservar evidencia auditable de que el checklist historico fue normalizado sin eliminar archivos.
  Depende de: QA-000-T01
  Entregables: `docs/opencode/plans/plan-task-agent-implementation-checklist.md`.
  Criterios de aceptacion: El archivo incluye frontmatter schema v2; conserva el contexto original; declara que es plan auxiliar historico y no slice funcional de producto.
  Validacion: Validar este documento con `validate_plan_text` usando el slice auxiliar `BE-000`.
  Evidencia: Documento actualizado a schema v2 auxiliar.
  Paralelismo[P]: No

## Definition of Done

- Los planes canonicos recuperados cumplen schema v2.
- El checklist historico recuperado queda normalizado como plan auxiliar schema v2.
- No se eliminan ni renombran archivos.
- No se modifican archivos fuera de `docs/opencode/plans`.
- Cualquier bloqueo de avance por QA anterior se mantiene como gate operativo independiente del schema documental.
