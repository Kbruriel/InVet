# Security checklist InVet

## OWASP requerido

- Autenticación en endpoints privados.
- Autorización por rol, permiso y contexto.
- Prevención IDOR/BOLA.
- Aislamiento por clínica, sucursal, empresa y propietario.
- Password hashing Argon2id o bcrypt.
- Access tokens de corta duración.
- Refresh tokens rotativos y seguros.
- Validación con Pydantic.
- Paginación y límites de tamaño.
- Rate limiting en auth, búsqueda pública y endpoints sensibles.
- Logs sin datos sensibles.
- Auditoría de acciones críticas.
- Escaneo de dependencias y secretos en CI/CD.

## Frontend

- No almacenar secretos en código.
- No loggear tokens, payloads médicos ni datos personales.
- Manejar 401/403 sin filtrar información.
- No confiar en permisos visuales como autorización real.
- Sanitizar contenido mostrado cuando provenga de usuarios.

## Backend

- Validar ownership en cada acceso por ID.
- No exponer IDs internos innecesarios en endpoints públicos.
- No filtrar stack traces.
- No exponer modelos ORM.
- Aplicar rate limit y paginación.
