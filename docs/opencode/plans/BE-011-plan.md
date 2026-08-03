---
schema_version: 2
slice: "011"
canonical_plan: BE-011
status: DONE
---

# BE-011 Plan - Registro operativo de pagos de servicios

## Objetivo del slice

Registrar pagos de servicios sin efectos fiscales, con metodos de pago, cambio, cancelacion y trazabilidad operativa.

## Alcance MVP

- Registro basico de transacciones de servicios.
- Calculo de totales y cambio.
- Cancelacion de transacciones en estados permitidos.
- Endpoints bajo `/api/v1`.
- Arquitectura backend por capas y frontend operativo.

## Fuera de alcance

- Facturacion electronica o timbrado fiscal.
- Venta de productos fisicos.
- Checkout en linea o pasarela de pago externa.
- Integraciones contables avanzadas.

## Revision de gaps

- El plan previo ya describia el negocio, pero no seguia el esquema V2.
- Se agregan frontend, QA y definicion de cierre para trazabilidad completa.
- La capa operativa no debe mezclar datos fiscales ni modelos ajenos al slice.

## Entidades y reglas de negocio

- **PaymentRecord**: registro de pago por servicio.
- **ServiceTransactionDetail**: detalle de los servicios incluidos.
- **PaymentMethod**: metodo de pago empleado.
- Solo se registran servicios y no productos fisicos.
- La cancelacion solo aplica en estados permitidos.
- No se guardan efectos fiscales en este slice.

## Endpoints esperados

- `POST /api/v1/payments`
- `GET /api/v1/payments/{id}`
- `PUT /api/v1/payments/{id}/cancel`
- `GET /api/v1/services/transactions`

## Contrato de implementacion frontend

### Rutas y acceso

- `GET /pagos`
- `GET /pagos/nuevo`
- `GET /pagos/[id]`
- Rutas protegidas para usuarios internos autorizados.

### Flujos y estados UX

- Formulario de registro de pago.
- Listado con filtros basicos.
- Detalle de transaccion y recibo no fiscal.
- Estados loading, error, empty y success.

### Contratos API por accion

- Registrar usa `POST /api/v1/payments`.
- Consultar detalle usa `GET /api/v1/payments/{id}`.
- Cancelar usa `PUT /api/v1/payments/{id}/cancel`.
- Listar transacciones usa `GET /api/v1/services/transactions`.

### Formularios y validacion

- Monto, metodo y detalle obligatorios.
- Cambio calculado solo cuando corresponda.
- Errores claros si la transaccion no puede cancelarse.

### Arquitectura de componentes

- Feature de pagos en `frontend/src/features/payments`.
- Recibo no fiscal reutilizable.
- Cliente API compartido en `frontend/src/shared/api`.

### Responsive y accesibilidad

- Formularios y detalle adaptables a mobile.
- Estados y totales legibles en pantallas pequenas.
- Confirmacion clara antes de cancelar.

### Estrategia de pruebas frontend

- Pruebas de formulario, detalle y estados.
- Smoke de navegacion protegida y regresion.

## Pruebas QA

- Happy path: registro exitoso de pago con cambio.
- Negative path: formulario invalido o cancelacion prohibida.
- Permisos: usuarios sin rol no pueden registrar.
- IDOR/BOLA: no se exponen pagos ajenos.

## Riesgos de seguridad/IDOR/BOLA

- Acceso a transacciones de otros usuarios o sucursales.
- Errores que revelen datos fiscales no previstos.
- Cancelaciones inconsistentes por falta de control de estado.

## Checklist tecnico

- [x] Contrato backend de pagos y detalle definido.
- [x] Reglas de cancelacion y ownership documentadas.
- [x] Frontend operativo de pagos descrito.
- [x] QA del slice trazable.

## Checklist de tareas

### Backend

- [x] BE-011-T01 - Normalizar el registro operativo de pagos
  Capa: backend
  Objetivo: Exponer pagos, detalle y cancelacion sin componentes fiscales.
  Depende de: Ninguna
  Entregables: routers, schemas, use cases y pruebas.
  Criterios de aceptacion: Se registran pagos operativos, el cambio se calcula y la cancelacion respeta estados.
  Validacion: python -m pytest app/tests/test_payments_api.py -q
  Evidencia: Backend del slice 011 validado
  Paralelismo[P]: No

- [x] BE-011-T02 - Reforzar control de estado y ownership
  Capa: backend
  Objetivo: Evitar accesos cruzados y cancelaciones invalidas.
  Depende de: BE-011-T01
  Entregables: validaciones de dominio y tests de seguridad.
  Criterios de aceptacion: Los pagos ajenos no se exponen y la cancelacion solo funciona en estados permitidos.
  Validacion: python -m pytest app/tests/test_payments_rules.py -q
  Evidencia: Reglas operativas y seguridad cubiertas
  Paralelismo[P]: No

### Frontend

- [x] FE-011-T01 - Construir UI de pagos operativos
  Capa: frontend
  Objetivo: Permitir registrar y consultar pagos desde la interfaz.
  Depende de: BE-011-T01
  Entregables: paginas, formularios, detalle y recibo no fiscal.
  Criterios de aceptacion: La UI muestra estados y consume la API real sin enlaces rotos.
  Validacion: npm test -- --run
  Evidencia: UI del slice 011 con regresion estable
  Paralelismo[P]: Si

### QA

- [x] QA-011-T01 - Verificar pagos operativos y seguridad
  Capa: qa
  Objetivo: Confirmar happy path, negative path y control de acceso.
  Depende de: BE-011-T01, BE-011-T02, FE-011-T01
  Entregables: reporte QA y evidencia funcional.
  Criterios de aceptacion: El flujo de pago funciona y los accesos no autorizados fallan de forma segura.
  Validacion: python backend/scripts/validate_slice_plan.py BE-011 --stage plan
  Evidencia: Plan V2 validado para el slice 011
  Paralelismo[P]: No

## Definition of Done

- [x] El registro operativo de pagos quedo descrito en V2.
- [x] Frontend y QA del slice 011 quedaron trazables.
- [x] El plan pasa validacion de esquema.
