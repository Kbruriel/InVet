# Guia para desarrolladores: uso de agentes en InVet

## Objetivo

Esta guia explica como pedir y ejecutar una tarea usando los agentes de InVet, desde el plan inicial hasta el final review.

El formato base de trabajo es por slice:

- `BE-00X`: tarea de backend.
- `FE-00X`: tarea de frontend.
- `QA-00X`: tarea de validacion.

Cada slice debe tener un alcance claro, criterios de aceptacion, comandos de cierre y evidencia.

## Como pedir una tarea

La forma recomendada de pedir trabajo a los agentes es indicar:

- Codigo del slice.
- Objetivo.
- Alcance.
- Criterios de aceptacion.
- Restricciones importantes.
- Resultado esperado.

Ejemplo para backend:

```text
Implementa BE-004: gestion de clinicas.

Objetivo:
Crear endpoints para listar clinicas y consultar detalle por ID.

Alcance:
- GET /api/v1/clinics
- GET /api/v1/clinics/{id}
- Soporte de paginacion y filtro por ciudad.
- Respuestas 404 cuando no exista la clinica.

Criterios de aceptacion:
- Tests de API en verde.
- Contrato compatible con FE-004.
- Sin exponer datos sensibles.
```

Ejemplo para frontend:

```text
Implementa FE-004: buscador publico de clinicas.

Objetivo:
Crear una pantalla publica para buscar clinicas y abrir detalle.

Alcance:
- Ruta /search.
- Ruta /clinics/[id].
- Estados loading, error y empty.
- Consumo real de /api/v1/clinics.

Criterios de aceptacion:
- UI responsive.
- Cliente API centralizado.
- No usar mocks si el backend ya existe.
```

Ejemplo para QA:

```text
Ejecuta QA-004 para BE-004 y FE-004.

Objetivo:
Validar el flujo publico de busqueda de clinicas.

Alcance:
- Happy path.
- Negative path.
- Empty state.
- Permisos si aplica.
- Regresion minima.

Entregable:
Documento de findings con estado APPROVED o BLOCKED.
```

## Flujo completo de una tarea

Una tarea completa normalmente pasa por estas etapas:

1. **Plan**
2. **Implementacion BE**
3. **Implementacion FE**
4. **QA**
5. **Correccion de findings**
6. **Run checks**
7. **Final review**

### 1. Plan

El plan convierte una necesidad de producto en slices concretos.

Entrada esperada:

- Descripcion funcional.
- Prioridad.
- Dependencias entre BE, FE y QA.

Salida esperada:

- Lista de slices, por ejemplo `BE-004`, `FE-004`, `QA-004`.
- Contratos esperados.
- Gates requeridos.

Prompt recomendado:

```text
Genera el plan para implementar el flujo de busqueda publica de clinicas.
Divide el trabajo en BE-004, FE-004 y QA-004.
Incluye alcance, criterios de aceptacion, riesgos y gates de cierre.
```

### 2. Implementacion BE-00X

Usa el agente BE cuando la tarea modifica API, dominio, persistencia, autenticacion, permisos o reglas de negocio.

Prompt recomendado:

```text
Implementa BE-004 segun el plan.
Respeta Clean Architecture.
Actualiza routers, use cases, repositorios y tests necesarios.
Ejecuta los gates de backend antes de cerrar.
```

Funcionamiento del agente BE:

- Lee el plan y el contrato.
- Ubica las capas afectadas.
- Implementa endpoint, caso de uso y persistencia.
- Agrega o ajusta tests.
- Ejecuta validaciones tecnicas.

Comandos que debe ejecutar o dejar listos:

```powershell
python -m ruff check app
python -m mypy app
python -m pytest app/tests -q
```

Si aplica persistencia segura:

```powershell
python backend/scripts/validate_slice_plan.py BE-00X --stage secure-persistence
```

Entregables:

- Codigo backend implementado.
- Tests backend actualizados.
- Evidencia de comandos.
- Notas de riesgos o decisiones.

### 3. Implementacion FE-00X

Usa el agente FE cuando la tarea modifica pantallas, componentes, rutas, estados visuales o consumo de API.

Prompt recomendado:

```text
Implementa FE-004 segun el contrato de BE-004.
Crea las rutas, componentes y cliente API necesarios.
Incluye estados loading, error y empty.
Valida responsive y ejecuta el gate de frontend.
```

Funcionamiento del agente FE:

- Lee el contrato backend.
- Define rutas y componentes.
- Conecta el cliente API.
- Maneja estados de UI.
- Ejecuta build o gate de frontend.

Comandos que debe ejecutar o dejar listos:

```powershell
npm run gate
npm run build
```

Para validar integracion:

```powershell
docker compose up -d --build --force-recreate db backend frontend
```

Entregables:

- Pantallas implementadas.
- Componentes reutilizables.
- Cliente API actualizado.
- Evidencia visual o tecnica.
- Build/gate de frontend en verde.

### 4. QA-00X

Usa el agente QA cuando BE y FE ya tienen una version candidata para validacion.

Prompt recomendado:

```text
Ejecuta QA-004 sobre BE-004 y FE-004.
Valida happy path, negative path, permisos si aplica, empty state y regresion minima.
Documenta findings y emite APPROVED o BLOCKED.
```

Funcionamiento del agente QA:

- Lee plan, BE y FE implementados.
- Ejecuta pruebas funcionales.
- Ejecuta pruebas tecnicas cuando aplique.
- Documenta evidencia.
- Decide si el slice pasa o queda bloqueado.

Comandos que puede ejecutar:

```powershell
python -m pytest app/tests -q
powershell scripts/compile-gate.ps1
docker compose up -d --build --force-recreate db backend frontend
```

Entregables:

- Documento `docs/opencode/qa/QA-00X-findings.md`.
- Estado `APPROVED` o `BLOCKED`.
- Lista de evidencia.
- Riesgos residuales.

### 5. Correccion de findings

Usa el agente de hallazgos cuando QA deja el slice en `BLOCKED` o cuando hay cambios obligatorios despues de review.

Prompt recomendado:

```text
Implementa los findings de QA-004.
Corrige solo los puntos bloqueantes.
Reejecuta los gates que fallaron y actualiza la evidencia.
```

Funcionamiento:

- Lee findings.
- Identifica responsable: BE, FE o ambos.
- Corrige la causa raiz.
- Repite el gate afectado.

Entregables:

- Fix aplicado.
- Evidencia nueva.
- Findings resueltos o reabiertos con causa clara.

### 6. Run checks

Antes de pedir final review, ejecuta el gate general.

Comando recomendado:

```powershell
powershell scripts/compile-gate.ps1
```

Este gate ejecuta:

- Gate de frontend.
- Lint backend.
- Typecheck backend.
- Tests backend.

Si el proyecto requiere validar la pila completa:

```powershell
docker compose up -d --build --force-recreate db backend frontend
```

### 7. Final review

El final review confirma que el slice esta listo para cerrar.

Prompt recomendado:

```text
Haz final review de BE-004, FE-004 y QA-004.
Confirma criterios de aceptacion, gates ejecutados, riesgos residuales y estado final.
Si todo pasa, marca APPROVED. Si no, deja BLOCKED con findings accionables.
```

El final review debe revisar:

- Que el alcance planeado fue cubierto.
- Que los contratos BE/FE coinciden.
- Que QA documento evidencia.
- Que los gates pasaron.
- Que no quedan riesgos bloqueantes.

Entregable:

- Documento en `docs/opencode/reviews/`.
- Estado final `APPROVED` o `BLOCKED`.
- Resumen de cambios.
- Riesgos residuales.
- Siguiente paso recomendado.

## Formato recomendado para cada slice

Usa este formato para que cualquier desarrollador pueda delegar bien una tarea:

```text
Codigo:
BE-00X / FE-00X / QA-00X

Titulo:
Nombre corto de la tarea.

Objetivo:
Que debe lograr el slice.

Alcance:
Que entra en la tarea.

Fuera de alcance:
Que no debe tocarse.

Criterios de aceptacion:
Condiciones para aprobar.

Dependencias:
Slices, endpoints, pantallas o datos requeridos.

Gates:
Comandos que deben pasar.

Entregables:
Archivos, tests, findings o review esperados.
```

## Ejemplo end-to-end

Solicitud inicial:

```text
Necesitamos busqueda publica de clinicas con detalle.
Genera plan y ejecuta BE-004, FE-004 y QA-004 hasta final review.
```

Plan esperado:

- `BE-004`: endpoints de clinicas.
- `FE-004`: buscador, listado y detalle.
- `QA-004`: validacion end-to-end.

Ejecucion:

1. Orquestador genera plan.
2. BE implementa API.
3. FE consume API y muestra UI.
4. QA valida funcionalidad.
5. Hallazgos corrigen bloqueos.
6. Run checks confirma estabilidad.
7. Final review emite estado final.

Resultado aprobado:

- `docs/opencode/reviews/BE-004-final-review.md`
- `docs/opencode/qa/QA-004-findings.md`
- Gates en verde.
- Estado `APPROVED`.

Resultado bloqueado:

- Findings accionables.
- Estado `BLOCKED`.
- Correccion asignada a BE, FE o ambos.
- Nueva ronda de QA despues del fix.

## Reglas de oro

- No cierres FE si BE no tiene contrato estable.
- No cierres QA si falta evidencia.
- No cierres final review si algun gate fallo.
- No mezcles cambios no relacionados dentro del mismo slice.
- Usa `BE-00X`, `FE-00X` y `QA-00X` para mantener trazabilidad.
- Todo `BLOCKED` debe incluir findings accionables.
- Todo `APPROVED` debe incluir evidencia.
