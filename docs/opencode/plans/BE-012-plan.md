# BE-012 — Calificaciones y comentarios

## Tareas Backend

1. [ ] Crear entidades y value objects de dominio para rating/coment.
   - Objetivo: Definir entidades Rating, RatingResponse y ClinicAverage en el domain layer.
   - Criterios de aceptacion: 
     - Se crea archivo `domain/models/rating.py`.
     - Se definen correctamente las clases con atributos esperados.
     - No hay dependencias externas no permitidas.
   - Paralelismo[P]: No

2. [ ] Crear casos de uso para crear/update respuesta rating.
   - Objetivo: Implementar casos de uso del domaine para calificaciones y respuestas.
   - Criterios de aceptacion:
     - Se crea archivo `application/use_cases/rating_create.py`.
     - Se crean clases de caso de uso que manejan operaciones con base de datos.
     - Se asegura que los datos de entrada son validados (pydantic).
   - Paralelismo[P]: No

3. [ ] Implementar interfaces de repositorio/ports.
   - Objetivo: Crear interfaces para persistencia y acceso a datos de rating.
   - Criterios de aceptacion:
     - Interfaces `RatingRepository` y `RatingResponseRepository` definidas.
     - Se usa patrón de puerto para abstracción de DB.
     - No se implementa lógica de negocio en las interfaces.
   - Paralelismo[P]: No

4. [ ] Implementar repositorios SQLAlchemy.
   - Objetivo: Crear implementaciones de persistencia para entidades de rating.
   - Criterios de aceptacion:
     - Clases concretas que implementan las interfaces.
     - Uso adecuado de ORM SQLAlchemy.
     - Se definen correctamente migraciones.
   - Paralelismo[P]: No

5. [ ] Crear schemas Pydantic (validaciones en capa de entrada).
   - Objetivo: Validar estructuras para solicitudes y respuestas de API.
   - Criterios de aceptacion:
     - Archivos `schemas/rating_request.py` y `schemas/rating_response.py`.
     - Se validan campos obligatorios, tipos y rangos.
   - Paralelismo[P]: No

6. [ ] Implementar routers FastAPI con endpoints.
   - Objetivo: Crear endpoint para calificar citas y responder comentarios.
   - Criterios de aceptacion:
     - Rutas definidas en `api/v1/ratings.py`.
     - Se implementan funciones de controlador que invocan casos de uso.
     - Endpoints responden con códigos HTTP adecuados.
   - Paralelismo[P]: No

7. [ ] Generar/migrar base de datos si aplica.
   - Objetivo: Aplicar migraciones para nuevas tablas de ratings.
   - Criterios de aceptacion:
     - Se generan archivos de migración Alembic.
     - Migración es idempotente.
     - Tablas se crean correctamente y con claves foreanas adecuadas.
   - Paralelismo[P]: No

8. [ ] Implementar pruebas con pytest/httpx.
   - Objetivo: Cubrir casos de uso con pruebas automatizadas.
   - Criterios de aceptacion:
     - Tests para casos happy path y error.
     - Se usan mocks para dependencias externas.
     - Cobertura > 80%.
   - Paralelismo[P]: No

9. [ ] Validar permisos, ownership e IDOR/BOLA.
   - Objetivo: Asegurar que solo usuarios autorizados puedan acceder a datos.
   - Criterios de aceptacion:
     - Implementación de validación de ownership (por cita / clínica).
     - Se validan privilegios en cada endpoint.
     - Se evita acceso cruzado entre usuarios.
   - Paralelismo[P]: No

## Tareas Frontend

1. [ ] Definir rutas y componentes de calificación.
   - Objetivo: Crear estructura de vistas para calificacion y promedio clínico.
   - Criterios de aceptacion:
     - Nueva carpeta `/src/features/rating` con componentes base.
     - Rutas definidas en `src/app`.
     - Componentes reutilizables para estrellas, comentarios, etc.
   - Paralelismo[P]: Si

2. [ ] Crear formulario de rating por cita.
   - Objetivo: Implementar UI para calificación tras finalización de cita.
   - Criterios de aceptacion:
     - Formulario con entrada de estrellas y comentario.
     - Validaciones aplicadas a los campos.
     - Se usa el cliente API centralizado.
   - Paralelismo[P]: Si

3. [ ] Mostrar campo de respuesta clínica para usuarios autorizados.
   - Objetivo: Permitir a veterinarios responder comentarios.
   - Criterios de aceptacion:
     - Componente condicional para respuestas clínicas.
     - Validación por rol antes de permitir entrada.
   - Paralelismo[P]: Si

4. [ ] Consumir API centralizada.
   - Objetivo: Integrar datos desde backend.
   - Criterios de aceptacion:
     - Uso del cliente API común en `src/shared/api`.
     - Manejo adecuado de errores HTTP y estados UI.
   - Paralelismo[P]: Si

5. [ ] Manejar estados de UI/UX.
   - Objetivo: Mostrar estados de carga, éxito y error durante el flujo.
   - Criterios de aceptacion:
     - Loading state visible al enviar calificación.
     - Error message claro si falla.
     - Success feedback tras envío exitoso.
   - Paralelismo[P]: Si

6. [ ] Validar formularios.
   - Objetivo: Garantizar que los datos sean válidos antes de enviarlos.
   - Criterios de aceptacion:
     - Inputs validados en tiempo real.
     - Indicaciones visuales para campos invalidos.
     - Mensajes de error adecuados.
   - Paralelismo[P]: Si

7. [ ] Implementar responsive.
   - Objetivo: Asegurar que la UI funcione en dispositivos móviles y desktop.
   - Criterios de aceptacion:
     - Diseño adapta a tamaño de pantalla.
     - Elementos de formulario son accesibles desde móvil.
   - Paralelismo[P]: Si

## Tareas QA

1. [ ] Validar happy path.
   - Objetivo: Verificar que el flujo principal funcione correctamente para todos los tipos de usuarios.
   - Criterios de aceptacion:
     - Propietario califica cita, se guarda y muestra en promedio.
     - Veterinario responde comentario, se refleja.
   - Paralelismo[P]: No

2. [ ] Testear paths negativos.
   - Objetivo: Validar comportamiento ante errores.
   - Criterios de aceptacion:
     - Intento de calificar sin autenticación devuelve HTTP 401.
     - Intento de responder comentario desde rol errado devuelve 403.
   - Paralelismo[P]: No

3. [ ] Verificar permisos por rol.
   - Objetivo: Confirmar que solo se permiten operaciones según tipo de usuario.
   - Criterios de aceptacion:
     - Roles definidos correctamente.
     - Acciones prohibidas devuelven códigos correctos.
   - Paralelismo[P]: No

4. [ ] Validar IDOR/BOLA.
   - Objetivo: Prevenir accesos cruzados no autorizados.
   - Criterios de aceptacion:
     - Intento de acceder a citas/calentamientos de otro propietario falla.
     - No se filtran datos sensibles en respuestas.
   - Paralelismo[P]: No

5. [ ] Revisión de estados REST.
   - Objetivo: Confirmar compatibilidad de códigos y estructura HTTP.
   - Criterios de aceptacion:
     - Endpoints devuelven códigos HTTP correctos.
     - Estructuras de datos siguen convenciones.
   - Paralelismo[P]: No

6. [ ] Verificar estados UI.
   - Objetivo: Asegurar que la interfaz maneje correctamente todos los casos.
   - Criterios de aceptacion:
     - Mostrar loading durante requests.
     - Mostrar error si falla una operación.
     - Mostrar éxito tras operación completada.
   - Paralelismo[P]: No

7. [ ] Testing regressión del flujo principal.
   - Objetivo: Verificar que nuevo código no rompa funcionalidades anteriores.
   - Criterios de aceptacion:
     - Ejecución exitosa de test suite existente relacionada con citas.
     - Ningún cambio en comportamiento esperado.
   - Paralelismo[P]: No