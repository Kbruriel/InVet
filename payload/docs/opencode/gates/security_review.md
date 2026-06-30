# Gate — Security Review

## Objetivo

Cerrar el gate `security_review` antes de avanzar al siguiente slice.

## Entrada

- Cambios actuales del slice.
- Tareas BE/FE/QA correspondientes.
- Evidencia de implementación o QA.

## Salida requerida

- Estado: Aprobado/Rechazado.
- Hallazgos por severidad.
- Acciones requeridas.
- Riesgos aceptados si aplica.

## Bloqueantes comunes

- Alcance fuera del MVP.
- Datos privados expuestos.
- Falta de permisos backend.
- IDOR/BOLA posible.
- Routers con lógica de negocio.
- ORM expuesto.
- Tests críticos faltantes.
- Build/lint/typecheck fallando sin justificación.
