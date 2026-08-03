# Política de actualización documental

Después de cada slice, actualizar documentación si cambió:

- Contratos API.
- Entidades.
- Reglas de negocio.
- Permisos.
- Variables de entorno.
- Migraciones.
- Componentes frontend.
- Estados UX.
- Casos QA.
- Riesgos y pendientes.

## Archivos sugeridos por cambio

- `docs/opencode/02_be_fe_qa_task_matrix.md` si cambia el estado de slice.
- `docs/opencode/tasks/**` si se ajusta alcance.
- `docs/api/**` si cambian endpoints.
- `docs/frontend/**` si cambian rutas/componentes.
- `docs/security/**` si cambian permisos o controles.

## Prohibido

- Mover alcance fuera del MVP hacia MVP sin decisión explícita.
- Documentar checkout, marketplace, productos o facturación como MVP.
