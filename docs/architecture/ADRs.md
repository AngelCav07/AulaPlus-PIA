# Architecture Decision Records (ADRs) — AulaPlus

Este documento formaliza las decisiones clave de arquitectura de software adoptadas para el sistema AulaPlus, justificando su alineación con los requerimientos de negocio, mantenibilidad, principios SOLID y restricciones técnicas.

---

## ADR 01: Selección de Arquitectura en Capas Concéntricas y Domain-Driven Design (DDD)

* **Estado:** Aceptado
* **Fecha:** Noviembre 2026
* **Decisores:** Equipo de Arquitectura de Software

### Contexto
AulaPlus requiere modelar reglas de negocio estrictas: anticipación mínima de 48 horas en reservas, umbral de grabación del 70% para liberar pagos, límite diario de 5 sesiones por tutor y una máquina de estados para el ciclo de vida de cada sesión. Un acoplamiento estrecho entre los controladores HTTP y la base de datos dificultaría las pruebas unitarias y violaría la separación de responsabilidades.

### Decisión
Adoptar una arquitectura limpia dividida estrictamente en cuatro capas desacopladas:
1. **Domain (`src/domain/`):** Entidades puras (`Sesion`), Value Objects (`Liquidacion`, `Grabacion`), especificaciones compuestas y excepciones de negocio sin dependencias externas.
2. **Application (`src/application/`):** Servicios de aplicación (`LiquidacionService`) y puertos de infraestructura definidos mediante protocolos/interfaces.
3. **Infrastructure (`src/infrastructure/`):** Implementaciones concretas de persistencia relacional con SQLAlchemy/SQLite y adaptadores externos simulados (`MockPagoGateway`).
4. **API (`src/api/`):** Controladores REST con FastAPI, validación de esquemas con Pydantic y documentación OpenAPI.

### Alternativas Evaluadas
* **Arquitectura Monolítica Transaccional (Smart UI / Active Record):** Menor tiempo de desarrollo inicial, pero mezcla reglas de negocio con SQL, imposibilitando pruebas unitarias aisladas sin base de datos activa.
* **Microservicios distribuidos:** Complejidad operativa innecesaria para el alcance y volumen actual del sistema.

### Consecuencias
* **Positivas:** El dominio es 100% testeable en memoria; se cumple el principio de inversión de dependencias (DIP); alta legibilidad y mantenibilidad.
* **Negativas:** Mayor número de archivos y necesidad de mapear entidades de dominio a modelos ORM.

---

## ADR 02: Implementación del Patrón Specification para Reglas de Negocio

* **Estado:** Aceptado
* **Fecha:** Noviembre 2026
* **Decisores:** Equipo de Arquitectura de Software

### Contexto
El sistema cuenta con múltiples reglas de validación que pueden combinarse o evaluarse de manera independiente según el caso de uso (por ejemplo: anticipación suficiente AND tutor con disponibilidad horaria AND tutor sin sobrecupo diario). Escribir condicionales anidados (`if-else`) en los controladores o servicios generaría código frágil y violaría el principio Open/Closed (OCP).

### Decisión
Implementar el patrón **Specification** mediante una clase base abstracta `Specification` que sobrecarga operadores lógicos (`&`, `|`, `~`), permitiendo componer reglas de negocio de forma declarativa:
* `AnticipacionMinimaSpec`
* `LimiteDiarioTutorSpec`
* `GrabacionAprobadaSpec`

### Alternativas Evaluadas
* **Validación inline con condicionales en el servicio:** Conduce a duplicación de lógica en diferentes casos de uso.
* **Validaciones exclusivas en esquemas de entrada (Pydantic):** Pydantic solo valida tipos de datos y formato, no tiene acceso al contexto temporal dinámico ni a reglas de dominio compuestas.

### Consecuencias
* **Positivas:** Cumplimiento estricto de SRP y OCP; cada regla se prueba unitariamente de forma aislada; combinatoria flexible y reutilizable.
* **Negativas:** Introduce pequeñas clases adicionales en el módulo de dominio.

---

## ADR 03: Motor de Persistencia Relacional Ligero (SQLite + SQLAlchemy ORM)

* **Estado:** Aceptado
* **Fecha:** Noviembre 2026
* **Decisores:** Equipo de Arquitectura de Software

### Contexto
Se requiere persistencia transaccional (con soporte de `commit` y `rollback`) para registrar sesiones y liquidaciones, garantizando que el entorno sea completamente reproducible tanto en desarrollo local, en ejecución dentro de contenedores Docker y en pipelines automatizados de CI/CD sin depender de servidores de bases de datos pesados externos.

### Decisión
Utilizar **SQLAlchemy** como ORM junto con el motor relacional **SQLite**. En pruebas unitarias automatizadas (`tests/test_repository.py`) se emplea SQLite en memoria (`sqlite:///:memory:`) para aislamiento total y velocidad milimétrica, mientras que en ejecución local/Docker se utiliza persistencia en archivo `aulaplus.db`.

### Alternativas Evaluadas
* **PostgreSQL / MySQL en contenedor:** Mayor capacidad de concurrencia en producción, pero añade sobrecarga de configuración de red y tiempos de espera en los pipelines de GitHub Actions.
* **Persistencia plana en JSON/CSV:** No ofrece garantías ACID ni soporte nativo de transaccionalidad (`commit`/`rollback`).

### Consecuencias
* **Positivas:** Cero configuración de servicios externos; ejecución instantánea del pipeline de CI/CD; desacoplamiento garantizado gracias al patrón Repository.
* **Negativas:** SQLite no está diseñado para alta concurrencia masiva en producción distribuida (fácilmente migrable a PostgreSQL modificando únicamente la variable de entorno `DATABASE_URL`).

---

## ADR 04: Framework Web FastAPI y Contratos OpenAPI

* **Estado:** Aceptado
* **Fecha:** Noviembre 2026
* **Decisores:** Equipo de Arquitectura de Software

### Contexto
La rúbrica del proyecto exige una API REST documentada con especificación OpenAPI/Swagger interactiva y respuestas HTTP semánticamente correctas (`201 Created`, `400 Bad Request`, `404 Not Found`, `409 Conflict`).

### Decisión
Implementar los endpoints en **FastAPI** montado sobre el servidor ASGI **Uvicorn**, aprovechando:
* Tipado estático con validación en tiempo de ejecución.
* Generación automática del esquema Swagger UI en `/docs` y OpenAPI en `/openapi.json`.
* Manejadores globales de excepciones de dominio para mapear errores de negocio a códigos de estado HTTP estándar.

### Alternativas Evaluadas
* **Flask:** Requiere librerías adicionales para documentación OpenAPI y validación de esquemas.
* **Django REST Framework:** Demasiado acoplado a su propio ORM y estructura de proyectos, dificultando la separación pura de capas DDD.

### Consecuencias
* **Positivas:** Desempeño asíncrono óptimo, documentación viva sin esfuerzo manual adicional y validación de DTOs transparente.
* **Negativas:** Requiere Python 3.10 o superior para aprovechar la sintaxis moderna de tipos.