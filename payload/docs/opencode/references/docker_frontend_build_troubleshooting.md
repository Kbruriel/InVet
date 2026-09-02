# Diagnóstico de builds frontend con Docker

## Objetivo

Esta guía define cómo reproducir, clasificar, corregir y documentar un fallo de build del servicio `frontend`. La regla principal es simple: un error no se declara *preexistente* o *ajeno al slice* sin evidencia reproducible.

## Fuente de verdad

Para un cierre que exige Docker, la comprobación canónica es una construcción limpia:

```powershell
docker compose build --no-cache frontend
```

Una ejecución local ayuda a aislar el problema, pero no sustituye este gate. La imagen limpia evita que artefactos generados en el host, como `.next`, oculten o inventen resultados.

## Flujo obligatorio

1. Validar el contrato del slice y leer su manifiesto frontend.
2. Registrar el estado inicial con `git status --short` y `git diff --name-only`.
3. Reproducir el fallo con `docker compose build --no-cache frontend` y conservar el primer error bloqueante completo.
4. Aislarlo desde `frontend/` con:

   ```powershell
   npm run lint
   npm run typecheck
   npm test -- --runInBand <pruebas-del-slice>
   ```

5. Comparar cada ruta reportada con los `Entregables` de la tarea y el diff inicial.
6. Verificar el contrato real del backend —schemas, router, casos de uso y respuestas— antes de cambiar tipos o llamadas del cliente.
7. Corregir código productivo y pruebas. No se acepta silenciar reglas, borrar funcionalidad requerida ni convertir pruebas en placeholders para conseguir un build verde.
8. Repetir, en este orden: lint, typecheck, pruebas enfocadas y build Docker sin caché.
9. Si el slice requiere integración en ejecución, levantar el stack y comprobar salud después del build.

## Cómo clasificar los hallazgos

| Resultado | Clasificación | Acción |
|---|---|---|
| `error` en un archivo entregable del slice | Bloqueante relacionado | Corregir antes de cerrar la tarea. |
| `error` fuera del slice, reproducible también en la línea base | Bloqueante heredado | Documentar comparación, propietario y comando exacto; no afirmar que el build del slice pasó. |
| `warning` con proceso en código `0` | No bloqueante | Registrar por separado. Solo bloquea si la política usa, por ejemplo, `--max-warnings=0`. |
| Error local dentro de `.next` que desaparece en el build limpio | Caché generada del host | Limpiar el directorio generado y repetir la validación local. |
| Error que aparece en el build limpio | Error de fuente o configuración | Corregirlo aunque una ejecución incremental local hubiera pasado. |

Que un archivo existiera antes no demuestra que su error sea ajeno. Para sostener esa conclusión deben existir una reproducción de línea base o historial verificable, la ruta exacta y la diferencia entre el resultado anterior y el actual.

## Caché local `.next`

Si `npm run typecheck` solo reporta rutas bajo `.next/types` que ya no existen en `src/app`, valida que la ruta resuelta sea exactamente `<repo>\frontend\.next`, elimina únicamente ese artefacto generado y repite:

```powershell
Resolve-Path -LiteralPath .next
Remove-Item -LiteralPath .next -Recurse -Force
npm run typecheck
```

No se elimina código fuente ni se usa este procedimiento para ocultar un error que también aparece en la construcción limpia.

## Evidencia mínima de cierre

```text
Fallo reproducido:
- Comando:
- Código de salida:
- Primer error bloqueante:

Clasificación:
- Rutas relacionadas con el slice:
- Errores heredados demostrados:
- Advertencias no bloqueantes:

Corrección:
- Causa raíz:
- Archivos modificados:
- Contrato backend verificado:

Validación final:
- lint:
- typecheck:
- pruebas enfocadas:
- docker compose build --no-cache frontend:
- salud del stack, si aplica:
```

## Caso de referencia: BE-014

La afirmación inicial indicaba que el fallo Docker era ajeno a BE-014. La reproducción limpia mostró lo contrario: los errores que detenían `next build` estaban en componentes productivos de soporte; otras rutas solo emitían advertencias no bloqueantes.

Las causas fueron contratos frontend desalineados con la API —estados en inglés, IDs con tipos incorrectos, respuestas ya parseadas tratadas como `Response` y ausencia de `PATCH`—, estado y paginación incompletos, y pruebas con placeholders o mocks incompatibles.

La solución alineó el cliente y la UI con los schemas y transiciones reales del backend, conservó el filtro de estado requerido y reemplazó los placeholders por pruebas funcionales. La evidencia final fue:

- `npm run lint`: código `0`; quedaron siete advertencias fuera de BE-014.
- 7 suites enfocadas de soporte: 23 pruebas aprobadas.
- `docker compose build --no-cache frontend`: código `0`; compilación, comprobación de tipos y generación de 28 rutas completadas.
- El typecheck local aislado leyó inicialmente una referencia obsoleta bajo `.next/types/app/notifications`; el builder limpio no la reprodujo y `npm run build` regeneró `.next`, tras lo cual `npm run typecheck` terminó con código `0`. Se clasificó como caché local y no como fallo de fuente.
- `docker compose up -d --build --force-recreate db backend frontend`: código `0`; base de datos, backend y frontend quedaron `healthy`.
- `GET http://localhost:8000/health` y `GET http://localhost:3000/support`: ambas comprobaciones respondieron `200`.
