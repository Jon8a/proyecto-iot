# Imagen base de Python
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del sensor
COPY sensor_simulator.py .

# Comando para ejecutar
CMD ["python", "sensor_simulator.py"]