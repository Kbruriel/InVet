# BE-002 — Autenticación y sesión

## Objetivo

Registro, login, logout, recuperación, refresh rotativo, roles iniciales y `/me`.

## Alcance MVP

- Implementar únicamente capacidades necesarias para el slice `002`.
- Exponer contratos bajo `/api/v1`.
- Mantener separación API/Application/Domain/Infrastructure/Core.
- Agregar pruebas automatizadas aplicables.

## Actividades Backend

1. Revisar entidades y reglas existentes.
2. Crear o ajustar entidades/value objects de dominio.
3. Crear casos de uso en application.
4. Crear interfaces de repositorio/ports.
5. Implementar repositorios SQLAlchemy en infrastructure.
6. Crear schemas Pydantic separados por contexto.
7. Crear/ajustar routers FastAPI.
8. Crear migraciones Alembic si aplica.
9. Agregar pruebas Pytest/HTTPX.
10. Validar permisos, ownership e IDOR/BOLA cuando aplique.

## Criterios de aceptación

- El contrato requerido por `FE-002` existe o queda documentado como mock temporal aprobado.
- Los routers no contienen lógica de negocio.
- No se exponen modelos ORM.
- Las respuestas son paginadas cuando hay listados.
- Los errores son consistentes y no filtran información interna.
- Las pruebas cubren al menos happy path y un negative path.

## Definition of Done

- [x] Código backend implementado.
- [x] Migraciones aplicadas o justificadas como no requeridas.
- [x] Tests backend agregados/actualizados.
- [x] Permisos y ownership validados.
- [x] OpenAPI consistente.
- [x] Sin alcance fuera del MVP.

## Tareas Frontend

### FE-002 — Autenticación y sesión

#### Objetivo

Pantallas de login, registro, recuperación, sesión, guards y manejo 401/403.

#### Actividades Frontend

1. Revisar contrato de `BE-002`.
2. Definir rutas en `src/app`.
3. Crear feature en `src/features`.
4. Crear componentes reutilizables si aplica.
5. Crear formularios con validación.
6. Integrar cliente API.
7. Manejar errores HTTP 400/401/403/404/409/422/500.
8. Agregar estados visuales.
9. Validar responsive.
10. Agregar pruebas si el repo tiene framework configurado.

#### Criterios de aceptación

- La UI consume el contrato del slice o mock documentado.
- No hay Tailwind CDN.
- No hay links `#` en flujos implementados.
- No se muestran acciones que contradigan permisos conocidos.
- No se loggean datos sensibles.
- La interfaz es usable en desktop y mobile.

#### Definition of Done

- [x] Rutas implementadas.
- [x] Componentes implementados.
- [x] Estados UX implementados.
- [x] Validaciones implementadas.
- [x] Consumo API centralizado.
- [x] Manejo de errores HTTP 400/401/403/404/409/422/500 implementado.
- [x] Sin alcance fuera del MVP.

## Referencias

- Tokens y reglas visuales en `docs/opencode/references/frontend_visual_alignment.md`.