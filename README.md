# AulaPlus — Sistema de Gestión y Liquidación de Tutorías Académicas

[![CI AulaPlus - Build, Test & Coverage](https://github.com/TU_USUARIO/TU_REPOSITORIO/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/TU_REPOSITORIO/actions/workflows/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)
![Architecture](https://img.shields.io/badge/architecture-DDD%20%2F%20Layered-orange)
![License](https://img.shields.io/badge/license-MIT-green)

Solución de software desarrollada para el **Producto Integrador de Aprendizaje (PIA)** de la unidad de aprendizaje **Componentes de Lógica de Negocio** (FIME - UANL).

---

## Descripción del Proyecto
**AulaPlus** es una plataforma de intermediación de tutorías personalizadas (1 a 1) que automatiza las reglas de negocio críticas del servicio:
* **Anticipación de reserva:** Mínimo estricto de 48 horas previo a la sesión.
* **Control de carga:** Límite máximo de 5 sesiones diarias por tutor[cite: 13, 15].
* **Auditoría de evidencias:** Validación de duración en grabaciones con umbral mínimo del 70% (63 de 90 minutos)[cite: 9].
* **Liquidación inmutable:** Desglose financiero automático de $200.00 MXN ($160.00 al tutor y $40.00 de comisión para la plataforma)[cite: 9].

---

## Arquitectura del Software
El sistema sigue los principios de **Domain-Driven Design (DDD)** y **Arquitectura Limpia en Capas Concéntricas**, desacoplando la lógica de negocio de frameworks y bases de datos[cite: 2, 3]:

```text
AulaPlus-PIA/
├── docs/
│   ├── BRD.md                   # Requerimientos, glosario, 16 User Stories (Gherkin) y matriz
│   ├── architecture/
│   │   └── ADRs.md              # Registros de decisiones arquitectónicas (ADR 01 a 04)
│   └── api/
│       └── openapi.json         # Especificación OpenAPI / Swagger exportada
├── src/
│   ├── domain/                  # Entidades (Sesion), Value Objects, Specs y Excepciones
│   ├── application/             # Casos de uso (LiquidacionService) y puertos
│   ├── infrastructure/          # Repositorio SQLite (SQLAlchemy) y gateways simulados
│   └── api/                     # Endpoints FastAPI, routers y esquemas Pydantic
├── tests/                       # Suite de pruebas unitarias y de integración (18 tests)
├── .github/workflows/
│   └── ci.yml                   # Pipeline de integración continua (CI/CD)
├── Dockerfile                   # Empaquetado de la aplicación
├── docker-compose.yml           # Orquestación de API y contenedor de pruebas
├── .env.example                 # Variables de entorno modelo (12-Factor App)
└── requirements.txt             # Dependencias del proyecto
```

---

## Requisitos Previos
- Python 3.12+ instalado.
- Git configurado.
- Docker & Docker Compose para ejecución contenerizada (Opcional).

---

## Instalación y Ejecución Local
1. Clonar el repositorio y configurar el entorno

git clone [https://github.com/AngelCav07/AulaPlus-PIA](https://github.com/AngelCav07/AulaPlus-PIA)
cd AulaPlus-PIA

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar entorno virtual (Linux/macOS)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

2. Iniciar el servidor de desarrollo

uvicorn src.api.main:app --reload

- API REST disponible en: http://127.0.0.1:8000
- Swagger UI interactivo en: http://127.0.0.1:8000/docs
- Especificación OpenAPI (JSON): http://127.0.0.1:8000/openapi.json

## Ejecución de Pruebas y Cobertura
La solución cuenta con 18 pruebas automatizadas que validan la máquina de estados, el patrón Specification, transacciones ACID (commit/rollback) e integración de endpoints REST:

pytest --cov=src --cov-report=term-missing --cov-fail-under=80

Resultados de Cobertura Obtenidos:
Cobertura Total: 88% (superando el umbral obligatorio >= 80).
Módulos auditados: src/domain/, src/application/, src/infrastructure/ y src/api/.

## Ejecución con Docker Compose
Para levantar la solución de forma reproducible y aislada:

# Construir y levantar API y contenedor de pruebas
docker compose up --build

## Integración Continua (CI/CD)
El proyecto cuenta con un flujo automatizado en GitHub Actions (.github/workflows/ci.yml) que se dispara en cada push o pull request hacia la rama principal:
1.Checkout del código fuente.
2.Configuración de entorno Python aislado.   
3.Instalación de dependencias limpias.   
4.Ejecución de la suite con validación estricta de cobertura mínima del 80% (--cov-fail-under=80)[cite: 1].

## Integrantes del Equipo (Equipo 8)
Esther Garza Cano — Matrícula: 2143077   
Luis Angel David Cavazos Reyes — Matrícula: 2142838   
Emilio Garza Arizpe — Matrícula: 2143702   



Facultad de Ingeniería Mecánica y Eléctrica (FIME) — UANL