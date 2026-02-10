import time
import random
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# ============================================
# CONFIGURACIÓN
# ============================================
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'mi_empresa')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'sensores')

# Esperar a que InfluxDB esté listo
print("⏳ Esperando a que InfluxDB esté listo...")
time.sleep(10)

# ============================================
# CONEXIÓN A INFLUXDB
# ============================================
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    print("✅ Conexión exitosa con InfluxDB")
except Exception as e:
    print(f"❌ Error conectando con InfluxDB: {e}")
    exit(1)

# ============================================
# SIMULACIÓN DE SENSORES
# ============================================
print("🌡️  ===================================")
print("🌡️  SIMULADOR DE SENSORES IoT INICIADO")
print("🌡️  ===================================")
print()

# Contador de mediciones
contador = 0

# Valores base para simular variaciones realistas
temp_base = 22.0
humedad_base = 60.0
presion_base = 1013.25

while True:
    try:
        # Simular variaciones pequeñas (como sensores reales)
        temp_variacion = random.uniform(-0.5, 0.5)
        humedad_variacion = random.uniform(-2, 2)
        presion_variacion = random.uniform(-1, 1)
        
        temperatura = round(temp_base + temp_variacion, 2)
        humedad = round(humedad_base + humedad_variacion, 2)
        presion = round(presion_base + presion_variacion, 2)
        
        # Actualizar valores base lentamente (tendencia)
        temp_base += random.uniform(-0.1, 0.1)
        humedad_base += random.uniform(-0.3, 0.3)
        
        # Mantener en rangos realistas
        temp_base = max(18, min(30, temp_base))
        humedad_base = max(40, min(80, humedad_base))
        
        # Crear punto de datos para InfluxDB
        point = Point("mediciones") \
            .tag("sensor_id", "SENSOR_001") \
            .tag("ubicacion", "Planta_Principal") \
            .tag("tipo", "ambiental") \
            .field("temperatura", temperatura) \
            .field("humedad", humedad) \
            .field("presion", presion) \
            .time(datetime.utcnow())
        
        # Enviar a InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        
        # Incrementar contador
        contador += 1
        
        # Mostrar en consola
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"📊 [{timestamp}] Medición #{contador}")
        print(f"   🌡️  Temperatura: {temperatura}°C")
        print(f"   💧 Humedad: {humedad}%")
        print(f"   🔽 Presión: {presion} hPa")
        print(f"   ✅ Enviado a InfluxDB")
        print()
        
        # Esperar 5 segundos antes de la siguiente medición
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(5)

# Cerrar conexión
client.close()
print("👋 Simulador finalizado")