# Plan BE-011 — Registro operativo de pagos de servicios

## Objetivo del slice

Registrar pago/venta de servicio sin efectos fiscales, métodos, efectivo/cambio, cancelación.

## Alcance MVP

Implementar capacidad para registrar operaciones de pago por servicios, incluyendo:

- Registro básico de transacciones
- Cálculo de totales y posibles cambios
- Cancelación parcial o total de transacción
- Uso exclusivo de endpoints bajo `/api/v1`
- Implementación en arquitectura backend dividida por capas (API/Application/Domain/Infrastructure)

## Fuera de alcance

- Productos, marketplace, carrito, checkout, pasarela de pago de servicios, facturación electrónica y timbrado fiscal
- Automatizaciones avanzadas o analítica avanzada salvo que este slice sea de hardening y solo como preparación documental
- App móvil nativa
- Checkout en línea
- Pasarela de pago de servicios
- Productos, marketplace, carrito, inventario o facturación

## Entidades y reglas de negocio

### Entidades

1. `PaymentRecord`: Registro de pago por servicio.
2. `ServiceTransactionDetail`: Detalle de transacción de servicio (relación uno a muchos con PaymentRecord).
3. `PaymentMethod`: Método de pago (método como efectivo, tarjeta, etc.)

### Reglas de negocio

1. Solo se permite registrar servicios y no productos físicos.
2. Las transacciones pueden cancelarse si se encuentran en estado pendiente.
3. El sistema no gestiona efectos fiscales.
4. La entrada se limita a datos básicos: monto, método, fecha, detalle de servicios consumidos.
5. No se permite el registro de pagos parciales o desgloses de los métodos.

## Endpoints esperados

- `POST /api/v1/payments` - Registrar nuevo pago
- `GET /api/v1/payments/{id}` - Consultar un pago específico
- `PUT /api/v1/payments/{id}/cancel` - Cancelar un pago (solo en estado pendiente)
- `GET /api/v1/services/transactions` - Listar transacciones de servicios

## Componentes frontend esperados

- Formulario de registro de pago operativo
- Listado de pagos registrados con filtros básicos
- Detalle de una transacción de pago
- Componente de recibo no fiscal para impresión o descarga
- Estados UX: loading, empty, error, success

## Pruebas QA

1. Happy path: registro exitoso de pago, validación del total y cambio calculado
2. Negative path: formulario incompleto o inválido, envío con datos incorrectos
3. Permisos por rol
4. Ownership/tenant/branch cuando aplique (si se implementa)
5. IDOR/BOLA
6. Estados HTTP (200, 400, 401, 403, 409, 422, 500)
7. Estados UI: loading, error, empty, success
8. Responsive design
9. Regresión del flujo principal

## Riesgos de seguridad/IDOR/BOLA

- Posible acceso no autorizado a transacciones de otros usuarios si no se implementan validaciones de ownership.
- Filtrado incorrecto de datos si se usan IDs de entidades externos sin validación previa.
- Posibles errores en manejo de cambios, cancelación o cálculo de totales.

## Definition of Done

- [ ] Código backend implementado
- [ ] Migraciones aplicadas o justificadas como no requeridas
- [ ] Tests backend agregados/actualizados
- [ ] Permisos y ownership validados
- [ ] OpenAPI consistente
- [ ] Sin alcance fuera del MVP

## Checklist de tareas

### Tarea Backend

1. **Objetivo:** Crear modelo de dominio para `PaymentRecord` y `ServiceTransactionDetail`
   - **Criterios de aceptacion:** Entidades existen con campos mínimos necesarios, siguen estándares de nomenclatura, se definen relaciones
   - **Paralelismo[P]:** No

2. **Objetivo:** Definir casos de uso para registro operativo de pagos y cancelación
   - **Criterios de aceptacion:** Casos de uso definidos en capa aplicación, incluyen cálculo de totales y control de cancelación, sin dependencias a sistemas externos de pago
   - **Paralelismo[P]:** No

3. **Objetivo:** Crear interfaces para repositorios `PaymentRecordRepository` y `ServiceTransactionDetailRepository`
   - **Criterios de aceptacion:** Interfaces existen, contienen métodos CRUD estándar, métodos de búsqueda personalizados si aplica
   - **Paralelismo[P]:** No

4. **Objetivo:** Implementar repositorios SQLAlchemy para `PaymentRecord` y `ServiceTransactionDetail`
   - **Criterios de aceptacion:** Repositorios implementados en capa infraestructura, usan SQLAlchemy ORM, cumplen con interfaz definida
   - **Paralelismo[P]:** No

5. **Objetivo:** Crear schemas Pydantic para entrada/salida de pagos
   - **Criterios de aceptacion:** Schemas validados, siguen convenciones, cubren campos necesarios para transacciones, no exponen información interna
   - **Paralelismo[P]:** No

6. **Objetivo:** Crear routers FastAPI para `/api/v1/payments`
   - **Criterios de aceptacion:** Routers existen, usan schemas Pydantic, cumplen con arquitectura (no implementan lógica de negocio), expuestos bajo `/api/v1`
   - **Paralelismo[P]:** No

7. **Objetivo:** Implementar migraciones Alembic para `PaymentRecord` y `ServiceTransactionDetail`
   - **Criterios de aceptacion:** Migraciones creadas, incluyen estructuras necesarias para entidades definidas, se pueden ejecutar sin errores
   - **Paralelismo[P]:** No

8. **Objetivo:** Agregar pruebas Pytest/HTTPX específicas por casos de uso
   - **Criterios de aceptacion:** Tests cubren happy path, negative path y validaciones de permisos, no filtran información interna
   - **Paralelismo[P]:** No

### Tarea Frontend

1. **Objetivo:** Definir rutas para listado y registro de pagos operativos en `src/app`
   - **Criterios de aceptacion:** Rutas están definidas en Next.js, siguen convenciones estándar, incluye rutas para `/payments/new` y `/payments/:id`
   - **Paralelismo[P]:** No

2. **Objetivo:** Crear feature `payment-operation` en `src/features`
   - **Criterios de aceptacion:** Feature contiene componentes principales necesarios (formulario, listado y detalle), implementa estado de loading/error/empty/success
   - **Paralelismo[P]:** No

3. **Objetivo:** Crear formularios con validación para registro de pago operativo
   - **Criterios de aceptacion:** Formulario tiene validaciones, campos requeridos están definidos, muestra errores claros, no se permite envío si hay datos inválidos
   - **Paralelismo[P]:** No

4. **Objetivo:** Integrar cliente API para consumo de `BE-011`
   - **Criterios de aceptacion:** Cliente centralizado en `src/shared/api`, consume endpoints definidos, maneja errores HTTP 400/401/403/404/409/422/500
   - **Paralelismo[P]:** No

5. **Objetivo:** Manejar estados visuales en componentes de transacciones
   - **Criterios de aceptacion:** Componentes manejan loading, error, empty y success, no se muestran acciones que contradigan permisos conocidos, sin links `#`
   - **Paralelismo[P]:** No

6. **Objetivo:** Validar responsive en componentes de UI
   - **Criterios de aceptacion:** Componentes son compatibles con desktop y mobile, usan Tailwind correctamente, no hay uso de CDN de Tailwind
   - **Paralelismo[P]:** No

### Tarea QA

1. **Objetivo:** Validar happy path: registro exitoso de pago y cálculo de totales/cambio
   - **Criterios de aceptacion:** Transacción se guarda, campos calculados son correctos, no hay filtrado de información interna
   - **Paralelismo[P]:** No

2. **Objetivo:** Validar negative path: formularios inválidos o datos incorrectos
   - **Criterios de aceptacion:** Sistema responde con errores claros sin revelar detalles internos, errores se muestran en UI correctamente
   - **Paralelismo[P]:** No

3. **Objetivo:** Validar permisos por rol en endpoints de transacciones
   - **Criterios de aceptacion:** Acceso con rol correcto permite operación, rol incorrecto recibe 403 o similar, se validan casos de usuario autenticado/sin permiso
   - **Paralelismo[P]:** No

4. **Objetivo:** Validar IDOR/BOLA en endpoints de transacciones
   - **Criterios de aceptacion:** Solicitud con ID ajeno a un usuario recibe error 404 o 403, datos sensibles no se exponen en UI o APIs sin permiso
   - **Paralelismo[P]:** No

5. **Objetivo:** Validar estados HTTP de endpoints
   - **Criterios de aceptacion:** Todos los endpoints responden con código apropiado (200, 400, 401, 403, 409, 422, 500), no hay respuestas inconsistentes
   - **Paralelismo[P]:** No

6. **Objetivo:** Validar estados UI del flujo principal
   - **Criterios de aceptacion:** UI muestra correctamente loading/error/empty/success, no se permite navegar si es inválido según permisos
   - **Paralelismo[P]:** No

7. **Objetivo:** Validar regresión del flujo principal
   - **Criterios de aceptacion:** Flujos anteriores (BE-010 o anteriores) siguen funcionando correctamente después de implementar BE-011
   - **Paralelismo[P]:** No
