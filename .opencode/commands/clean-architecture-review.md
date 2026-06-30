---
description: Revisa cumplimiento de Clean Architecture backend y modularidad frontend.
agent: invet-clean-architecture-reviewer
---

Ejecuta revisión de arquitectura limpia sobre los cambios actuales.

Instrucciones:
1. Revisa `git diff` y archivos modificados.
2. Valida backend por capas: API, application, domain, infrastructure, core, tests.
3. Valida que los routers no tengan lógica de negocio.
4. Valida que dominio no dependa de FastAPI/SQLAlchemy/proveedores.
5. Valida que ORM no se exponga.
6. Valida frontend por rutas, features, shared UI y cliente API centralizado.
7. Entrega Aprobado/Rechazado con hallazgos por severidad.
