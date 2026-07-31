---
description: Revisa seguridad OWASP, permisos, IDOR/BOLA y exposición de datos.
agent: invet-security-reviewer
---

Ejecuta revisión de seguridad sobre los cambios actuales.

Instrucciones:
0. Ejecuta de forma autonoma. Pregunta al usuario solo si falta informacion bloqueante, se requiere auditoria externa o hay una decision critica de riesgo/alcance.
1. Revisa autenticación/autorización en endpoints privados.
2. Valida controles por rol, permiso y contexto.
3. Prueba o razona escenarios IDOR/BOLA.
4. Valida aislamiento por clínica, sucursal, empresa y propietario.
5. Valida manejo de tokens, cookies y logs.
6. Verifica que endpoints públicos no expongan datos internos.
7. Entrega Aprobado/Rechazado con riesgos bloqueantes.
