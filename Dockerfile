FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente completo
COPY . .

# Variables de entorno
ENV PORT=8000
ENV HOST=0.0.0.0
EXPOSE 8000

# Iniciar servidor FastAPI y frontend
CMD ["uvicorn", "core_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
