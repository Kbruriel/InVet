---
description: Revisa Clean Architecture y documenta hallazgos que puedan consumirse con /implement-findings.
agent: invet-clean-architecture-reviewer
---

Revisa los cambios actuales con foco en Clean Architecture.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante o hay una decision critica de alcance arquitectonico.
1. Identifica el BE-00X afectado a partir del contexto, los archivos modificados o la rama actual.
2. Revisa `git diff` y archivos modificados.
3. Valida backend por capas: API, application, domain, infrastructure, core y tests.
4. Valida que los routers no tengan logica de negocio.
5. Valida que dominio no dependa de FastAPI, SQLAlchemy ni proveedores.
6. Valida que ORM no se exponga.
7. Valida frontend por rutas, features, shared UI y cliente API centralizado.
8. Si existen correcciones, crea `docs/opencode/reviews/BE-00X-clean-architecture-review.md` con base en `docs/opencode/templates/review_findings_template.md`.
9. Si no hay hallazgos, reporta estado Aprobado.
10. No implementes codigo en este comando.
