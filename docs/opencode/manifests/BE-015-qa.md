---
manifest_version: 1
slice: "015"
layer: qa
generated_at: 2026-09-07T23:29:16+00:00
source_plan: docs/opencode/plans/BE-015-plan.md
source_plan_sha256: 2e65b3a8c877e97da8639d617e56613f701fa37ee145127a0da81ace38c52823
source_task: docs/opencode/tasks/qa/QA-015.md
source_task_sha256: 2a3977e504aedb7feaf9126d752214c798fa475ba0e67654cc0d2cbac498bd70
---

# BE-015 - manifiesto compacto qa

## Uso

- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.
- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.
- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.
- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.
- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.

## Fuente de capa

- Estado: DISPONIBLE
- Archivo: `docs/opencode/tasks/qa/QA-015.md`

## Archivos permitidos

- `backend/app/tests/**`
- `docs/opencode/checkpoints/BE-015-qa.json`
- `docs/opencode/manifests/BE-015-qa.md`
- `docs/opencode/plans/BE-015-plan.md`
- `docs/opencode/qa/**`
- `docs/opencode/qa/QA-015-findings.md`
- `docs/opencode/qa/QA-015-results.md`

## Tareas

### QA-015-T01 - COMPLETADA
- Tipo: qa
- Criterio: AC-015-01, AC-015-03, AC-015-04
- Objetivo: Verificar que los totales soncorrectos con datos de prueba controlados.
- Depende de: BE-015-T08 (endpoint disponible)
- Contexto: plan canonico; datos seed slices previos 008 a 012; contract Docker para backend PostgreSQL.
- Contratos: matriz de trazabilidad; contratos endpoints.
- Entregables: reporte QA resultados de ejecucion en `docs/opencode/qa/QA-015-results.md`.
- Aceptacion: Cada tipo de reporte devuelve al menos un dato conocido con valor correcto. Totales coinciden con conteo manual sobre fixtures.
- Validacion: `python -m pytest backend/app/tests/integration/test_reports_integration.py -q --timeout=60`; complementario manual si aplica.
- Resultado: Decision QA APPROVED o bloqueante documentada.

### QA-015-T02 - COMPLETADA
- Tipo: qa
- Criterio: AC-015-02, AC-015-03
- Objetivo: Comprobar que page page_size se respetan en listados extensos.
- Depende de: BE-015-T08
- Contexto: plan canonico; fixtures con multiples registros por tipo reporte mas de page_size items.
- Contratos: contrato paginacion del plan.
- Entregables: reporte QA resultados en `docs/opencode/qa/QA-015-results.md`.
- Aceptacion: Numero de elementos por pagina <= page_size. Pagina N devuelve datos distintos consistentes con total coherente a Total dividido por page_size.
- Validacion: Ejecutar endpoints iterando paginas desde Docker backend y comparar conteos.
- Resultado: Decision QA APPROVED o bloqueante documentada.

### QA-015-T03 - COMPLETADA
- Tipo: qa
- Criterio: AC-015-09, AC-015-10, AC-015-11
- Objetivo: Confirmar que sin token retorna 401 en endpoints de reportes.
- Depende de: BE-015-T08
- Contexto: plan canonico; multi-tenant fixtures con dos o mas clinicas distintas.
- Contratos: contract auth y risk IDOR/BOLA del plan.
- Entregables: reporte QA negative path BOLA en `docs/opencode/qa/QA-015-findings.md`.
- Aceptacion: Sin token retorna 401 en todos los endpoints de reportes. Tipo invalido genera 422 con mensaje claro. Usuario Clinica A no ve datos de Clinica B en respuesta alguna.
- Validacion: Ejecutar contratos desde docker backend (pytest parametrizado mas multi-tenant fixtures). Complementar manual si aplica para verificacion visual.
- Resultado: Decision QA APPROVED o bloqueante documentada.

## Brief de capa

## Objetivo
Validar datos agregados, permisos y paginación.
## Dependencias
- Backend relacionado: `BE-015`.
- Frontend relacionado: `FE-015`.
## Alcance de validación
- Happy path.
- Negative path.
- Permisos por rol.
- Ownership/tenant/branch cuando aplique.
- IDOR/BOLA.
- Estados HTTP.
- Estados UI.
- Responsive.
- Regresión del flujo principal.
## Casos mínimos
1. Usuario autorizado ejecuta flujo correctamente.
2. Usuario no autenticado recibe 401 cuando aplica.
## Controles de cierre

- Ningun archivo fuera de la allowlist cambio durante la tarea.
- No se eliminaron archivos ni lineas existentes sin justificacion explicita.
- Los registros `include_router(...)` existentes permanecen presentes.
- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.
- El plan canonico se actualizo solo despues de verificar la tarea.
