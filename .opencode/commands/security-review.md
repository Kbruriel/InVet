---
description: Revisa seguridad OWASP y documenta hallazgos que puedan consumirse con /implement-findings.
agent: invet-security-reviewer
---

Revisa los cambios actuales con foco en seguridad.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, se requiere auditoria externa o hay una decision critica de riesgo/alcance.
1. Identifica el BE-00X afectado a partir del contexto, los archivos modificados o la rama actual.
2. Revisa `git diff` y archivos modificados.
3. Valida autenticacion y autorizacion en endpoints privados.
4. Valida controles por rol, permiso y contexto.
5. Prueba o razona escenarios IDOR/BOLA.
6. Valida aislamiento por clinica, sucursal, empresa y propietario.
7. Valida manejo de tokens, cookies y logs.
8. Verifica que endpoints publicos no expongan datos internos.
9. Si existen correcciones, crea `docs/opencode/reviews/BE-00X-security-review.md` con base en `docs/opencode/templates/review_findings_template.md`.
10. Si no hay hallazgos, reporta estado Aprobado.
11. No implementes codigo en este comando.
