FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar paquetes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y las pruebas
COPY src/ ./src/
COPY tests/ ./tests/

EXPOSE 8000

# Comando por defecto para correr la API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]