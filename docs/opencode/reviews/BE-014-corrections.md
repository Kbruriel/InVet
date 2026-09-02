# Resolución del build Docker frontend de BE-014

## Resultado

El build limpio del servicio `frontend` quedó aprobado. La hipótesis inicial —que el fallo era preexistente y ajeno a BE-014— no se sostuvo al reproducirlo: los errores bloqueantes estaban en entregables productivos y pruebas del propio slice. Otros archivos sí emitían advertencias heredadas, pero no detenían la compilación.

## Diagnóstico reproducible

Se ejecutaron las validaciones locales y la construcción canónica:

```powershell
Set-Location frontend
npm run lint
npm run typecheck
npm test -- --runInBand src/shared/api/support.test.ts src/features/support/ui/ticket-form.test.tsx src/features/support/ui/ticket-list.test.tsx src/features/support/ui/ticket-list-filtered.test.tsx src/app/support/page.test.tsx 'src/app/support/[ticketId]/ticket-status-updater.test.tsx' 'src/app/support/[ticketId]/page.test.tsx'
Set-Location ..
docker compose build --no-cache frontend
```

La primera construcción limpia falló en archivos de soporte por errores de TypeScript y lint. Las advertencias encontradas en appointments, clínicas, perfil público y notifications no fueron el bloqueo: el proceso llegó a código `0` al corregir BE-014 aun conservándolas.

## Causa raíz

- El cliente frontend no representaba el contrato real del backend: usaba estados en inglés, IDs incompatibles y trataba valores ya parseados como si fueran objetos `Response`.
- El cliente HTTP no ofrecía `PATCH`, mientras el endpoint de transición exige `{ "new_status": ... }`.
- Listado, filtro, detalle y actualización de estado tenían tipos y estado React incompletos.
- Varias pruebas eran placeholders, contenían imports sin uso o mocks que ya no coincidían con la API.

## Corrección aplicada

- Se añadió soporte tipado para `PATCH` en el cliente central.
- `supportApi` quedó alineado con los schemas, estados, IDs, paginación, categorías y transición reales del backend.
- Se corrigieron formulario, listado, filtro por estado, detalle, badge y actualizador de estado sin retirar funcionalidad del alcance.
- Se reemplazaron placeholders por siete suites funcionales que cubren cliente API, formulario, listas, página principal, detalle y transiciones.

## Evidencia final

| Gate | Resultado |
|---|---|
| `npm run lint` | Aprobado, código `0`; siete advertencias ajenas a BE-014. |
| `npm run typecheck` | Aprobado, código `0`, después de regenerar `.next` con el build local. |
| Pruebas enfocadas | 7 suites y 23 pruebas aprobadas. |
| `docker compose build --no-cache frontend` | Aprobado, código `0`. |
| Compilación Next.js dentro de Docker | Tipos y lint aprobados; 28 rutas generadas, incluidas `/support` y `/support/[ticketId]`. |
| `docker compose up -d --build --force-recreate db backend frontend` | Aprobado, código `0`; los tres servicios quedaron `healthy`. |
| Comprobaciones HTTP | `GET http://localhost:8000/health` y `GET http://localhost:3000/support` respondieron `200`. |

El `npm run typecheck` aislado en el host reportó inicialmente una referencia obsoleta bajo `.next/types/app/notifications/page.ts`. Esa ruta generada no apareció en el builder limpio; `npm run build` regeneró `.next` y el typecheck posterior terminó con código `0`. Se clasificó como caché local, no como fallo de fuente. La limpieza segura y la política general quedaron documentadas en `docs/opencode/references/docker_frontend_build_troubleshooting.md`.

## Advertencias residuales

Las siete advertencias heredadas no bloquean el build actual, pero deben tratarse como deuda separada. No deben usarse para afirmar que un error bloqueante del slice es ajeno ni cerrarse silenciosamente dentro de BE-014.

## Regla para próximos agentes

Antes de declarar que un fallo es preexistente, el agente debe demostrarlo con línea base o historial reproducible y separar claramente errores, advertencias y caché generada. Si `docker compose build --no-cache frontend` nombra un entregable del slice como error, el slice no está listo para cierre.
