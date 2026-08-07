# InVet UI Automation

Proyecto independiente de automatizacion para InVet.

## Alcance

- UI automation con Playwright para flujos E2E.
- API automation con `APIRequestContext`.
- Trazabilidad por historia de usuario, criterio, caso automatizado y evidencia.
- Separacion operativa entre UIA y APIA.

## Estructura

```text
InVet_UI_Automation/
  .opencode/
  docs/
  tests/
  playwright.config.ts
  package.json
  tsconfig.json
  .env.example
```

## Requisitos

- Node.js 20+
- Un frontend de InVet accesible en `FRONTEND_BASE_URL`
- Un backend de InVet accesible en `API_BASE_URL`

## Instalacion

```bash
npm install
npx playwright install
```

## Configuracion

1. Copia `.env.example` a `.env`.
2. Ajusta `FRONTEND_BASE_URL` y `API_BASE_URL`.
3. Si la ruta de login UI aun no existe, deja `LOGIN_UI_ENABLED=false`.
4. Si quieres validar login real, configura `LOGIN_EMAIL` y `LOGIN_PASSWORD`.

## Ejecucion

```bash
npm run typecheck
npm run test:e2e
npm run test:regression
npm run test:api
npm run check
```

## Estado inicial

- El spec de UI de login queda listo, pero se omite cuando `LOGIN_UI_ENABLED=false`.
- El spec de API de login queda listo y se ejecuta cuando `LOGIN_API_ENABLED=true`.
- Los specs anotan `US` y `CA` para trazabilidad.
- Los specs de UI adjuntan `Feature`, `Scenario`, `Given`, `When` y `Then` en formato Gherkin dentro de `testInfo` y del reporte de Playwright.
