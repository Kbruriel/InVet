# Analisis comparativo: Manual Brain Framework e InVet

## 1. Alcance y criterio de analisis

Este informe compara el contenido de `MANUAL_DE_USUARIO.md` con el sistema agentico que existe en InVet.

La comparacion distingue dos niveles de evidencia:

- **Brain documentado**: capacidades declaradas en el manual. No se recibio el repositorio ni se ejecuto su CLI, por lo que no se consideran verificadas.
- **InVet comprobado**: contratos, agentes, comandos, planes, validadores, manifiestos y gates presentes en el repositorio `C:\InVet`.

Las instrucciones operativas incluidas dentro del manual se analizaron como contenido del documento, no como instrucciones para modificar o ejecutar InVet.

## 2. Conclusion ejecutiva

Brain e InVet resuelven problemas complementarios:

- **Brain es mas fuerte como modelo de gobierno del producto**: descubrimiento, stakeholders, requisitos, cambios, decisiones de arquitectura, evidencias, riesgos y trazabilidad global.
- **InVet es mas fuerte como sistema de ejecucion y cierre verificable**: slices verticales, tareas atomicas por capa, responsabilidades especializadas, automatizacion UI/API, revisiones independientes, manifiestos firmados, checkpoints y gates de cierre.

La mejor evolucion no es reemplazar el flujo de InVet por el de Brain. Es incorporar una capa de gobierno inspirada en Brain por encima del flujo existente:

```text
Requisito + decision + riesgo
            |
            v
Slice InVet y plan canonico
            |
            v
BE + FE + UIA + APIA + QA + revisiones + checks
            |
            v
Indice consolidado de evidencias y trazabilidad
```

## 3. Mejoras que InVet puede aportar al manual de Brain

### 3.1 Sustituir el flujo conceptual por un contrato operativo completo

El manual presenta cuatro agentes generales —Analyst, Architect, Engineer y Tester—. InVet demuestra que una ejecucion real se vuelve mas controlable al separar funciones y evitar que un mismo agente implemente, juzgue y cierre su propio trabajo.

El manual deberia documentar al menos estas familias de responsabilidad:

- planificacion del producto;
- implementacion backend y frontend;
- automatizacion UI y API;
- QA con autoridad de rechazo;
- revision funcional;
- revision de arquitectura limpia;
- revision de seguridad;
- implementacion de hallazgos;
- ejecucion de checks;
- actualizacion documental;
- gate final.

InVet ya materializa esta separacion en 14 agentes y en un flujo obligatorio de 13 etapas. Brain podria mantener nombres genericos, pero deberia definir una matriz de propiedad, entradas, salidas y prohibiciones por rol.

### 3.2 Introducir planes atomicos y no reinterpretables

InVet aporta controles que el manual no especifica con suficiente precision:

- una tarea pertenece a una sola capa y a un solo tipo de trabajo;
- cada tarea declara dependencia, entregable, validacion y evidencia;
- el plan marca paralelismo de forma explicita;
- los ejecutores no pueden reinterpretar el alcance;
- existe un unico plan canonico por slice;
- un validador determinista revisa el contrato antes de ejecutar cada etapa.

Brain deberia incorporar un esquema equivalente para sus planes de cambio. La lista de archivos propuesta por un agente no deberia ser solamente texto libre: tendria que ser una lista permitida de entregables, validada antes y despues de implementar.

### 3.3 Hacer reanudable y verificable la ejecucion

El manual explica estados del cambio, pero no detalla suficientemente como recuperar una ejecucion interrumpida o detectar que una entrada fue alterada.

InVet puede aportar:

- checkpoints por capa y tarea;
- manifiestos operativos derivados del plan;
- hashes SHA-256 para detectar artefactos obsoletos;
- snapshots de archivos;
- verificacion previa a continuar;
- rechazo de manifiestos desactualizados;
- distincion entre propietario semantico del plan y generador mecanico de vistas.

Esto convierte la reanudacion en un procedimiento verificable, no en una suposicion basada en memoria conversacional.

### 3.4 Ampliar el concepto de prueba

En Brain, Tester concentra gran parte de la validacion. InVet aporta una defensa por capas:

1. pruebas y validaciones de la implementacion;
2. automatizacion de interfaz;
3. automatizacion de API;
4. QA funcional;
5. revision integral del slice;
6. revision de arquitectura;
7. revision de seguridad;
8. checks tecnicos y visuales;
9. gate final.

El manual deberia diferenciar estos tipos de evidencia y declarar cual de ellos puede rechazar un cambio. Tambien debe prohibir que QA corrija directamente el producto: los hallazgos regresan a un implementador y luego se revalidan.

### 3.5 Formalizar bloqueos, omisiones y correcciones

InVet ofrece reglas operativas utiles para Brain:

- `BLOCKED` cuando el entorno o una dependencia impide una prueba real;
- `SKIPPED` solo cuando la actividad es demostrablemente no aplicable;
- prohibicion de presentar un entorno roto como exito o como prueba omitida;
- ciclo explicito de hallazgo, correccion y nueva validacion;
- Docker obligatorio cuando el slice depende de PostgreSQL o del runtime integrado;
- intento de autorrecuperacion antes de declarar bloqueo.

Brain deberia incluir estas semanticas en su maquina de estados y en los ejemplos de salida del CLI.

### 3.6 Gobernar trabajo transferido entre cambios

InVet valida los `carryovers` en tres lugares: plan de origen, plan de destino y registro central. Un pendiente abierto o solamente transferido bloquea el cierre.

Brain puede adoptar esta gobernanza para evitar que un cambio llegue a `completed` dejando trabajo implicito en notas o conversaciones.

### 3.7 Añadir un gate sobre el incremento anterior

InVet impide comenzar un nuevo slice sobre una base cuyo QA anterior no esta cerrado. Brain deberia aplicar el mismo principio a cambios encadenados y declarar las excepciones permitidas.

### 3.8 Corregir y reforzar la calidad editorial del manual

Mejoras concretas al archivo:

- eliminar enlaces locales `file:///c:/Users/Daniels/...` y usar rutas relativas o enlaces publicos;
- reparar la numeracion repetida y sincronizar el indice con todas las secciones;
- separar capacidades **implementadas**, **experimentales** y **planeadas**;
- evitar afirmaciones absolutas como trazabilidad de “cada linea” si no se explica el mecanismo que la demuestra;
- acompañar cifras de rendimiento, como “microsegundos”, con benchmark, plataforma y version;
- añadir una matriz de compatibilidad por sistema operativo, proveedor de IA y runtime local;
- documentar recuperacion tras interrupciones, concurrencia, conflictos, rollback y artefactos obsoletos;
- incluir ejemplos reales de salidas exitosas, rechazadas, bloqueadas y reanudadas;
- añadir un diagrama unico del ciclo completo y una tabla de entradas/salidas por agente;
- indicar la version del manual, version del CLI y fecha de compatibilidad.

## 4. Ideas del manual que InVet deberia adoptar

### 4.1 Grafo formal de trazabilidad

InVet posee trazabilidad operativa, pero esta distribuida entre historias, planes, tareas, QA, revisiones y checks. Conviene crear un indice generado que conecte cuatro conceptos sin duplicar las fuentes actuales:

| Concepto Brain | Equivalente o destino en InVet | Accion recomendada |
|---|---|---|
| `REQ-*` | `US-*` y criterios `CA-*` | Conservarlos como fuente canonica del requisito |
| `CHG-*` | Slice vertical del mismo indice | Crear una vista de cambio que enlace todas sus capas |
| `ADR-*` | Decisiones hoy dispersas en planes y referencias | Crear ADR versionados para decisiones significativas |
| `EVD-*` | QA, reviews, checks, checkpoints y hashes | Crear un indice generado de evidencia, sin copiar resultados |

El valor principal seria responder automaticamente: que requisito origino un archivo, que decision lo condiciona y que evidencia demuestra su cumplimiento.

### 4.2 Etiquetas de certeza: confirmado e inferido

Durante planeacion, adopcion de codigo existente y revisiones, InVet deberia diferenciar:

- `confirmed`: respaldado por codigo, configuracion, prueba o decision aprobada;
- `inferred`: deducido por el agente y pendiente de confirmacion.

Esta regla reduce el riesgo de convertir una suposicion del modelo en requisito o arquitectura oficial.

### 4.3 Riesgo cuantificado y autonomia proporcional

Los planes de InVet ya registran riesgos, pero no existe una politica general visible que determine cuanta autonomia puede ejercer el agente.

Se recomienda añadir un puntaje reproducible basado en factores como:

- seguridad y autorizacion;
- datos personales o sensibles;
- migraciones y perdida de datos;
- impacto financiero;
- superficie del cambio;
- reversibilidad;
- dependencias externas.

Politica inicial propuesta:

| Nivel | Ejecucion permitida |
|---|---|
| Bajo | Automatica con checks y evidencia |
| Medio | Automatica con revision independiente obligatoria |
| Alto | Requiere aprobacion humana antes de implementar o desplegar |
| Critico | Aprobacion humana obligatoria en plan, ejecucion y cierre |

Los umbrales deben calibrarse con datos reales de InVet; no conviene copiar sin validacion la formula del manual.

### 4.4 Constitucion ejecutable del proyecto

InVet tiene reglas fuertes en documentos y validadores. Puede consolidarlas en una constitucion legible por maquina con invariantes como:

- Clean Architecture obligatoria;
- autorizacion resuelta en backend;
- no exponer modelos de persistencia como contrato API;
- API bajo `/api/v1`;
- una sola responsabilidad por tarea;
- QA no implementa correcciones;
- evidencia obligatoria para cerrar;
- prohibicion de omitir gates aplicables.

El validador existente puede evaluar primero reglas estructurales; las reglas semanticas permanecerian bajo revisores especializados.

### 4.5 Descubrimiento de proyecto y memoria de dominio

InVet deberia incorporar los cinco pilares del descubrimiento de Brain:

- stakeholders y autoridad de aprobacion;
- identidad y convenciones de nombres;
- stack y restricciones;
- alcance del MVP;
- glosario de dominio.

Para InVet, el glosario es especialmente valioso: inventario, lotes, movimientos, unidades, almacenes, usuarios y permisos deben tener definiciones canonicas compartidas por producto, codigo y pruebas.

### 4.6 Registro explicito de ADR

Las decisiones arquitectonicas importantes no deberian quedar unicamente en el plan del slice o en documentos generales. Un `ADR-*` debe registrar contexto, opciones, decision, consecuencias y slices afectados.

### 4.7 Modo de adopcion de sistemas legacy

Brain propone descubrir componentes y reconstruir trazabilidad en proyectos existentes. InVet puede crear un flujo de adopcion que:

1. inventarie modulos, rutas, persistencia, integraciones y pruebas;
2. marque cada hallazgo como confirmado o inferido;
3. genere candidatos de historias, ADR y riesgos;
4. solicite aprobacion antes de convertirlos en fuentes canonicas;
5. produzca el primer plan compatible con schema vigente.

### 4.8 Interoperabilidad entre asistentes

InVet ya mantiene contratos para OpenCode y GitHub Copilot. Puede avanzar hacia una fuente neutral que genere adaptadores para distintos asistentes, evitando mantener manualmente instrucciones duplicadas y divergentes.

### 4.9 Comando unificado de diagnostico y verificacion

Conviene envolver los validadores y checks actuales en una interfaz unica, conceptualmente equivalente a:

```text
invet doctor            # dependencias, Docker, configuracion y artefactos
invet status BE-012     # etapa, pendientes, bloqueos y checkpoints
invet verify BE-012     # contrato, trazabilidad, evidencias y gates
invet ci BE-012         # salida estable para integracion continua
```

No es necesario reemplazar los scripts actuales: esta interfaz seria una fachada estable y facil de automatizar.

### 4.10 Integracion continua real del flujo agentico

El repositorio incluye contratos para GitHub Copilot, pero no se encontro un workflow de CI que ejecute el cierre agentico. Debe añadirse una verificacion no interactiva que compruebe al menos:

- schema y dependencias del plan;
- manifiestos y hashes;
- pruebas backend y frontend;
- lint, formato, tipos y build;
- estado de QA, revisiones y carryovers;
- consistencia del indice de evidencias.

## 5. Priorizacion recomendada para InVet

### P0 — Control y confianza

1. Añadir etiquetas `confirmed/inferred` a planes y revisiones.
2. Definir politica de riesgo y aprobacion humana.
3. Generar el indice `REQ/CHG/ADR/EVD` sobre los artefactos actuales.
4. Crear `invet verify` y ejecutarlo en CI.

### P1 — Gobierno del conocimiento

5. Crear ADR formales.
6. Añadir stakeholders y responsables de aprobacion.
7. Crear glosario de dominio.
8. Consolidar invariantes en una constitucion ejecutable.

### P2 — Portabilidad y adopcion

9. Implementar descubrimiento/adopcion de repositorios legacy.
10. Generar adaptadores para varios asistentes desde contratos neutrales.
11. Añadir panel o comando de estado global del proyecto.

## 6. Cambios que no conviene copiar literalmente

- No reducir los 14 roles actuales de InVet a cuatro agentes generales.
- No reemplazar los IDs `US/BE/FE/QA/UIA/APIA`; son utiles para ejecucion. El grafo nuevo debe indexarlos.
- No duplicar evidencias dentro de nuevos archivos `EVD`; se deben enlazar y verificar por hash.
- No adoptar una formula de riesgo fija sin calibrarla con incidentes, cambios y falsos positivos reales.
- No hacer que un grafo YAML se convierta en una segunda fuente manual de verdad.
- No declarar independencia de proveedor hasta que los contratos se hayan probado en cada adaptador.

## 7. Resultado esperado de la combinacion

La union de ambos enfoques daria a InVet tres propiedades simultaneas:

1. **Gobierno**: saber por que existe cada cambio, quien lo aprueba y que riesgo tiene.
2. **Ejecucion**: repartir el trabajo en tareas atomicas, reanudables y con propiedad clara.
3. **Demostracion**: probar el cumplimiento mediante evidencias enlazadas, revisiones independientes y gates deterministas.

En sintesis: Brain puede aportar a InVet la memoria estructurada del **por que**; InVet puede aportar al manual de Brain la disciplina operativa del **como se ejecuta, se rechaza, se corrige y se cierra**.

## 8. Evidencia de InVet consultada

Las conclusiones sobre InVet se apoyan principalmente en:

- `.opencode/agents/`: contratos de los 14 agentes especializados;
- `.opencode/commands/`: comandos que orquestan las etapas del slice;
- `docs/opencode/README.md`: secuencia operativa obligatoria;
- `docs/opencode/03_task_prompt_contracts.md`: contratos de entrada y salida;
- `docs/opencode/04_agent_contracts.md`: propiedad y limites de cada agente;
- `docs/opencode/05_done_gates_by_command.md`: condiciones de cierre;
- `docs/opencode/09_scope_and_design_decisions.md`: alcance e invariantes tecnicos;
- `docs/opencode/13_agents_architecture_and_gate_flow.md`: continuidad, checkpoints y gates;
- `docs/opencode/15_operational_manifests_flow.md`: manifiestos, hashes y propiedad semantica;
- `backend/scripts/validate_slice_plan.py`: validacion determinista del plan;
- `backend/scripts/manage_slice_task.py`: generacion y verificacion de manifiestos;
- `.github/agents/` y `.github/prompts/`: adaptacion actual para GitHub Copilot.

No se encontro un archivo de workflow bajo `.github/workflows/`; por eso la integracion continua del flujo agentico figura como recomendacion y no como capacidad presente.
