# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/

# Establecer variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]