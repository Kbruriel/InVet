# 09 — Decisiones de alcance y diseño incorporadas

## Decisiones funcionales

- El MVP valida búsqueda, perfil, citas, consulta, recetas, recordatorios, pagos operativos, ratings, soporte, reportes y administración inicial.
- La única funcionalidad comercial del MVP es el registro operativo de pagos de servicios.
- El pago operativo no tiene efectos fiscales.
- La pasarela de pago de Stage 2 aplica solo a suscripciones de clínicas, no al checkout de servicios MVP.

## Decisiones frontend

- El HTML de referencia se interpreta como resultado visual, no como fuente técnica.
- La implementación debe ser Next.js + TypeScript + Tailwind local.
- La landing debe reemplazar marca y textos provisionales por InVet y español consistente.
- El buscador público debe navegar a `/buscar` con query params.

## Decisiones backend

- Clean Architecture es obligatoria.
- API REST versionada bajo `/api/v1`.
- Permisos y pertenencia se validan siempre en backend.
- No se exponen modelos ORM.
