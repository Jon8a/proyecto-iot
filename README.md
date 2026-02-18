# 🌡️ Simulador de Sensores IoT con Docker

> Sistema de captura de datos IoT que simula un sensor ambiental enviando mediciones en tiempo real a una base de datos InfluxDB, con visualización mediante Grafana.

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=flat&logo=influxdb&logoColor=white)](https://www.influxdata.com/)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)](https://grafana.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

---

## 👥 Miembros del Equipo

- **Jon Ochoa** 
- **Oier Martinez** 


---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Explicación de los Pasos Seguidos](#-explicación-de-los-pasos-seguidos)
- [Instrucciones de Uso](#-instrucciones-de-uso)
- [Datos Simulados](#-datos-simulados)
- [Problemas / Retos Encontrados](#-problemas--retos-encontrados)
- [Posibles Vías de Mejora](#-posibles-vías-de-mejora)
- [Alternativas Posibles](#-alternativas-posibles)
- [Referencias](#-referencias)

---

## 📖 Descripción

Este proyecto implementa un sistema completo de captura y visualización de datos IoT utilizando Docker Compose. Simula un sensor ambiental que genera mediciones de temperatura, humedad y presión atmosférica cada 5 segundos, almacenándolas en una base de datos especializada en series temporales y visualizándolas en tiempo real mediante un dashboard profesional.

**Objetivo del reto:** Montar en Docker Compose una tecnología que permita enviar datos simulados a otro contenedor que se encargue de almacenarlos y comprobar que se han guardado apropiadamente.

---

## 🏗️ Arquitectura

El sistema está compuesto por **3 contenedores Docker** que se comunican entre sí mediante una red virtual privada:

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│   Sensor Python     │         │      InfluxDB       │         │      Grafana        │
│                     │         │   (Base de Datos)   │         │    (Dashboard)      │
│  - Genera datos     │         │                     │         │                     │
│  - Cada 5 segundos  │ HTTP    │  - Almacena datos   │ HTTP    │  - Visualiza datos  │
│  - HTTP POST        ├────────>│  - Series temporales│<────────┤  - Tiempo real      │
│                     │         │  - Volumen          │         │  - Auto-refresh     │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
         ↓                                ↓                               ↓
         └────────────────────────────────┴───────────────────────────────┘
                          Red Docker: iot_network (bridge)
```

### Componentes:

1. **Sensor Simulator (Python 3.12)**
   - Genera datos simulados realistas
   - Utiliza librería `influxdb-client`
   - Envía mediciones cada 5 segundos
   - Implementa reconexión automática

2. **InfluxDB 2.7**
   - Base de datos de series temporales
   - Optimizada para datos IoT
   - Almacenamiento persistente mediante volúmenes
   - API REST para lectura/escritura

3. **Grafana (latest)**
   - Dashboard de visualización profesional
   - Configuración automática via Provisioning
   - Gráficas en tiempo real
   - Auto-refresh cada 5 segundos

---

## 📝 Explicación de los Pasos Seguidos

### Paso 1: Preparación del Entorno

**1.1. Verificar instalación de Docker**
```bash
docker --version
docker compose version
```

**1.2. Crear estructura del proyecto**
```bash
mkdir proyecto-iot-docker
cd proyecto-iot-docker
mkdir -p sensor grafana/dashboards grafana/provisioning/dashboards grafana/provisioning/datasources
```

**1.3. Inicializar repositorio Git**
```bash
git init
git remote add origin https://github.com/Jon8a/proyecto-iot
```

---

### Paso 2: Configuración de Docker Compose

Creamos `docker-compose.yml` que define los 3 servicios:

```yaml
version: '3.8'

services:
  # ===================================
  # Base de Datos InfluxDB
  # ===================================
  influxdb:
    image: influxdb:2.7
    container_name: influxdb_iot
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=admin123456
      - DOCKER_INFLUXDB_INIT_ORG=mi_empresa
      - DOCKER_INFLUXDB_INIT_BUCKET=sensores
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=mi-token-super-secreto-12345
    volumes:
      - influxdb_data:/var/lib/influxdb2
    networks:
      - iot_network

  # ===================================
  # Simulador de Sensor
  # ===================================
  sensor:
    build: ./sensor
    container_name: sensor_simulator
    depends_on:
      - influxdb
    environment:
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=mi-token-super-secreto-12345
      - INFLUXDB_ORG=mi_empresa
      - INFLUXDB_BUCKET=sensores
    networks:
      - iot_network
    restart: unless-stopped

  # ===================================
  # Dashboard Grafana
  # ===================================
  grafana:
    image: grafana/grafana:latest
    container_name: grafana_iot
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - influxdb
    networks:
      - iot_network

# ===================================
# Volúmenes para persistencia
# ===================================
volumes:
  influxdb_data:
  grafana_data:

# ===================================
# Red privada para comunicación
# ===================================
networks:
  iot_network:
    driver: bridge
```

**Decisiones de diseño importantes:**
- **Volúmenes nombrados** para persistencia de datos entre reinicios
- **Red bridge personalizada** para aislamiento y DNS interno
- **depends_on** para control de orden de arranque
- **restart: unless-stopped** para recuperación automática del sensor
- **Variables de entorno** para configuración flexible

---

### Paso 3: Implementación del Simulador de Sensor

**3.1. Crear `sensor/Dockerfile`**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sensor_simulator.py .

CMD ["python", "sensor_simulator.py"]
```

**3.2. Crear `sensor/requirements.txt`**
```
influxdb-client==1.38.0
```

**3.3. Crear `sensor/sensor_simulator.py`**

Implementa:
- Generación de datos realistas con variaciones aleatorias
- Conexión a InfluxDB con retry automático
- Espera inicial de 10 segundos para que InfluxDB esté listo
- Logging detallado de cada medición
- Manejo de errores con reintentos

**Características del simulador:**
- Temperatura base: 22°C con variaciones de ±0.5°C
- Humedad base: 60% con variaciones de ±2%
- Presión base: 1013.25 hPa con variaciones de ±1 hPa
- Deriva lenta de valores para simular cambios ambientales reales
- Tags: sensor_id, ubicación, tipo de sensor

---

### Paso 4: Configuración de Grafana Provisioning

**4.1. Crear `grafana/provisioning/datasources/influxdb.yml`**

Define la conexión a InfluxDB con **UID fijo** para evitar problemas de referencia:

```yaml
apiVersion: 1

datasources:
  - name: InfluxDB
    type: influxdb
    access: proxy
    uid: influxdb-iot  # UID fijo - crucial para persistencia
    url: http://influxdb:8086
    jsonData:
      version: Flux
      organization: mi_empresa
      defaultBucket: sensores
      tlsSkipVerify: true
    secureJsonData:
      token: mi-token-super-secreto-12345
    isDefault: true
    editable: false
```

**4.2. Crear `grafana/provisioning/dashboards/dashboard.yml`**
```yaml
apiVersion: 1

providers:
  - name: 'IoT Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

**4.3. Exportar dashboard creado manualmente**

Después de configurar los paneles en Grafana:
1. Dashboard → Share → Export → Save to file
2. Guardar como `grafana/dashboards/iot-dashboard.json`

**Queries Flux utilizadas:**

```flux
// Temperatura
from(bucket: "sensores")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mediciones")
  |> filter(fn: (r) => r["_field"] == "temperatura")
  |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)

// Humedad
from(bucket: "sensores")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mediciones")
  |> filter(fn: (r) => r["_field"] == "humedad")
  |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)

// Presión
from(bucket: "sensores")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mediciones")
  |> filter(fn: (r) => r["_field"] == "presion")
  |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
```

---

### Paso 5: Testing y Validación

**5.1. Construcción y arranque**
```bash
docker compose up --build
```

**5.2. Verificación de logs**
```bash
# Ver logs de todos los contenedores
docker compose logs -f

# Ver logs solo del sensor
docker logs sensor_simulator -f

# Ver logs de InfluxDB
docker logs influxdb_iot -f
```

**5.3. Verificación de datos en InfluxDB**
- Acceder a `http://localhost:8086`
- Login: `admin` / `admin123456`
- Data Explorer → verificar datos en bucket `sensores`

**5.4. Verificación de visualización en Grafana**
- Acceder a `http://localhost:3000`
- Login: `admin` / `admin`
- Dashboard "IoT Industrial" debe aparecer automáticamente
- Verificar actualización automática cada 5 segundos

---



## 🚀 Instrucciones de Uso

### Requisitos Previos

- Docker Engine 20.10 o superior
- Docker Compose v2.0 o superior
- 2GB de RAM disponible
- Puertos 8086 y 3000 libres

### Instalación y Ejecución

**1. Clonar el repositorio**
```bash
git clone https://github.com/Jon8a/proyecto-iot
cd proyecto-iot-docker
```

**2. Arrancar todos los servicios**
```bash
docker compose up --build
```

Este comando:
- Construye la imagen del sensor
- Descarga las imágenes de InfluxDB y Grafana
- Crea la red `iot_network`
- Crea los volúmenes para persistencia
- Arranca los 3 contenedores
- Muestra logs en tiempo real

**3. Acceder a los servicios**

| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| InfluxDB | http://localhost:8086 | admin | admin123456 |
| Grafana | http://localhost:3000 | admin | admin |

**Al entrar en el Dashboard de Grafana, refrescar cada panel para que carguen los datos**

**4. Verificar funcionamiento**

En la terminal verás logs como:
```
sensor_simulator | 📊 [14:30:05] Medición #1
sensor_simulator |    🌡️  Temperatura: 22.3°C
sensor_simulator |    💧 Humedad: 61.2%
sensor_simulator |    🔽 Presión: 1013.8 hPa
sensor_simulator |    ✅ Enviado a InfluxDB
```

El dashboard de Grafana mostrará las gráficas actualizándose automáticamente.



---

## 📊 Datos Simulados

El sensor genera datos realistas cada **5 segundos**:

| Métrica | Rango | Unidad | Variación |
|---------|-------|--------|-----------|
| 🌡️ Temperatura | 18-30 | °C | ±0.5°C por lectura |
| 💧 Humedad | 40-80 | % | ±2% por lectura |
| 🔽 Presión | 1010-1016 | hPa | ±1 hPa por lectura |

**Características de la simulación:**
- Variaciones aleatorias suaves que simulan cambios ambientales reales
- Deriva lenta de valores base para simular cambios de tendencia
- Valores mantenidos dentro de rangos realistas
- Tags: `sensor_id=SENSOR_001`, `ubicacion=Planta_Principal`, `tipo=ambiental`

**Estructura de datos en InfluxDB:**
```
Measurement: mediciones
Tags:
  - sensor_id: SENSOR_001
  - ubicacion: Planta_Principal
  - tipo: ambiental
Fields:
  - temperatura (float)
  - humedad (float)
  - presion (float)
Timestamp: UTC
```

---

## 🐛 Problemas / Retos Encontrados

### 1. ❌ Sensor arranca antes que InfluxDB esté listo

**Síntoma:**
```
Connection refused (Connection refused) at http://influxdb:8086
```

**Causa:** Docker `depends_on` solo espera a que el contenedor arranque, no a que el servicio interno esté listo para aceptar conexiones.

**Solución implementada:**
```python
# Esperar a que InfluxDB esté listo
print("⏳ Esperando a que InfluxDB esté listo...")
time.sleep(10)

# Implementar reintentos en conexión
try:
    client = InfluxDBClient(...)
except Exception as e:
    print(f"❌ Error conectando: {e}")
    time.sleep(5)  # Reintentar
```

**Alternativas evaluadas:**
- Healthchecks en docker-compose (más complejo, no necesario para este caso)
- Script de espera externo como `wait-for-it.sh` (dependencia adicional)

---

### 2. ❌ Error "unauthorized access" en Grafana

**Síntoma:**
```
InfluxDB returned error: unauthorized access
```

**Causa:** Query language configurado en InfluxQL en lugar de Flux, o token incorrecto.

**Solución:**
1. En Grafana → Data Sources → InfluxDB
2. Cambiar "Query Language" de `InfluxQL` a `Flux`
3. Verificar que el token coincide exactamente con el de docker-compose.yml
4. Organization: `mi_empresa` (exactamente como está definido)
5. Bucket: `sensores`

**Lección aprendida:** InfluxDB 2.x usa Flux por defecto, InfluxQL es legacy.


---

### 3. ❌ Datos no persisten al reiniciar contenedores

**Síntoma:** Después de `docker compose down`, al volver a arrancar el dashboard está vacío.

**Causa:** 
1. No configurar volúmenes en docker-compose.yml
2. Usar `docker compose down -v` que borra volúmenes

**Solución:**
```yaml
# docker-compose.yml
influxdb:
  volumes:
    - influxdb_data:/var/lib/influxdb2  # ← CRÍTICO

volumes:
  influxdb_data:  # ← Declarar volumen
```

**Comandos correctos:**
- ✅ `docker compose down` - Conserva datos
- ❌ `docker compose down -v` - BORRA datos

---

### 4. ❌ Solo muestra datos nuevos, no históricos

**Síntoma:** Dashboard siempre empieza desde cero, no muestra datos antiguos.

**Causa:** Volumen no montado correctamente o query con rango fijo corto.

**Solución:**
1. Verificar que el volumen está montado:
```bash
docker volume inspect proyecto-iot-docker_influxdb_data
```

2. Usar rango dinámico en queries:
```flux
|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
```
En lugar de:
```flux
|> range(start: -1h)  # ← Rango fijo
```

3. En Grafana, cambiar el selector de tiempo (arriba derecha) a "Last 6 hours" o "Last 24 hours"

---

### 5. ❌ Dashboard no se guarda automáticamente

**Síntoma:** Configuración de Grafana se pierde al recrear el contenedor.

**Solución: Dashboard Provisioning**
1. Exportar dashboard: Dashboard → Share → Export → Save to file
2. Guardar en `grafana/dashboards/iot-dashboard.json`
3. Configurar provisioning en `grafana/provisioning/dashboards/dashboard.yml`
4. Montar volúmenes en docker-compose.yml:
```yaml
grafana:
  volumes:
    - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
    - ./grafana/provisioning:/etc/grafana/provisioning:ro
```

**Resultado:** Dashboard aparece automáticamente al iniciar Grafana.

---

## 🚀 Posibles Vías de Mejora

### 1. 🔢 Múltiples Sensores

**Implementación:**
```yaml
# docker-compose.yml
sensor_001:
  build: ./sensor
  environment:
    - SENSOR_ID=SENSOR_001
    - UBICACION=Planta_Norte

sensor_002:
  build: ./sensor
  environment:
    - SENSOR_ID=SENSOR_002
    - UBICACION=Planta_Sur
```

**Beneficios:**
- Simular escenario real de múltiples dispositivos
- Probar escalabilidad del sistema
- Comparar lecturas entre ubicaciones

---

### 2. 🚨 Sistema de Alertas

**Implementación con Grafana Alerting:**
```yaml
# En el dashboard JSON
alerts:
  - name: "Temperatura Alta"
    condition: temperatura > 28°C
    notification: email/slack/webhook
```

**Casos de uso:**
- Temperatura crítica > 28°C
- Humedad anormal < 30% o > 90%
- Sensor sin datos por más de 1 minuto

---

### 3. 📡 Protocolo MQTT

**Arquitectura mejorada:**
```
Sensor → Mosquitto (MQTT Broker) → Telegraf → InfluxDB → Grafana
```

**Ventajas:**
- Protocolo estándar en IoT real
- Menor overhead que HTTP
- Pub/Sub permite múltiples consumidores
- QoS configurable

**Implementación:**
```yaml
mosquitto:
  image: eclipse-mosquitto:2
  ports:
    - "1883:1883"

telegraf:
  image: telegraf:latest
  volumes:
    - ./telegraf.conf:/etc/telegraf/telegraf.conf
```

---

### 4. 🔐 Seguridad Mejorada

**Docker Secrets:**
```yaml
secrets:
  influx_token:
    file: ./secrets/influx_token.txt

influxdb:
  secrets:
    - influx_token
```

**TLS/SSL:**
- Certificados para HTTPS en Grafana
- Conexiones encriptadas entre servicios

**Variables de entorno sensibles:**
```bash
# .env (no subir a Git)
INFLUXDB_TOKEN=...
GRAFANA_PASSWORD=...
```

---

### 5. 🤖 Machine Learning para Anomalías

**Implementación con Python:**
```python
# detector_anomalias.py
from sklearn.ensemble import IsolationForest

model = IsolationForest()
model.fit(datos_historicos)
anomalias = model.predict(datos_nuevos)
```

**Contenedor adicional:**
```yaml
ml_detector:
  build: ./ml
  depends_on:
    - influxdb
```

**Casos de uso:**
- Detectar fallos de sensor
- Predecir mantenimiento
- Identificar patrones anormales

---

### 6. 📱 API REST

**Implementación con FastAPI:**
```python
# api/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/sensors")
def get_sensors():
    # Consultar InfluxDB
    return {"sensors": [...]}

@app.get("/measurements/latest")
def get_latest():
    return {"temperatura": 24.5, ...}
```

**Endpoints útiles:**
- `GET /sensors` - Lista de sensores
- `GET /measurements/latest` - Última medición
- `GET /measurements/history` - Histórico con filtros
- `POST /sensors/configure` - Configuración

---

### 7. ☁️ Despliegue en Cloud

**AWS:**
```
ECS (Fargate) + RDS para InfluxDB + CloudWatch
```

**Azure:**
```
Container Instances + Managed InfluxDB + Application Insights
```

**Ventajas:**
- Escalabilidad automática
- Alta disponibilidad
- Backups automáticos
- Monitoreo integrado

---

### 8. 🔄 CI/CD Pipeline

**GitHub Actions:**
```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  test:
    - run: docker compose up -d
    - run: pytest tests/
  deploy:
    - run: docker compose push
```

**Automatización:**
- Tests automáticos en cada commit
- Build y push de imágenes
- Despliegue automático a producción

---

### 9. 📊 Dashboard Mobile

**Grafana Mobile App:**
- Notificaciones push
- Visualización en móvil
- Alertas en tiempo real

**Alternativa: PWA personalizada**
```javascript
// React + Chart.js
fetch('http://api:8000/measurements/latest')
  .then(data => renderChart(data))
```

---

### 10. 💾 Backup Automatizado

**Script de backup:**
```bash
#!/bin/bash
# backup.sh
docker exec influxdb_iot influx backup /backup
docker cp influxdb_iot:/backup ./backups/$(date +%Y%m%d)
```

**Cron job:**
```cron
0 2 * * * /home/user/proyecto/backup.sh
```

---

## 🔄 Alternativas Posibles

### Base de Datos

| Alternativa | Ventajas | Desventajas | Cuándo usar |
|-------------|----------|-------------|-------------|
| **TimescaleDB** | PostgreSQL con extensiones temporales, SQL familiar | Más pesado que InfluxDB | Cuando necesitas SQL complejo |
| **Prometheus** | Excelente para métricas, integración con Kubernetes | Diseñado para métricas, no logs | Monitoreo de infraestructura |
| **MongoDB** | Flexible, esquema dinámico | No optimizado para series temporales | Datos heterogéneos |
| **PostgreSQL + TimescaleDB** | Ecosistema PostgreSQL completo | Mayor complejidad | Aplicaciones enterprise |

**Decisión tomada:** InfluxDB por su especialización en IoT y series temporales.

---

### Visualización

| Alternativa | Ventajas | Desventajas | Cuándo usar |
|-------------|----------|-------------|-------------|
| **Kibana** | Potente para logs, integración con Elasticsearch | Curva de aprendizaje alta | Stack ELK completo |
| **Chronograf** | Integración nativa con InfluxDB | Menos flexible que Grafana | Solo InfluxDB |
| **Metabase** | Fácil de usar, SQL-friendly | No diseñado para tiempo real | BI y analytics |
| **Custom React Dashboard** | Control total | Desarrollo desde cero | Requisitos muy específicos |

**Decisión tomada:** Grafana por su versatilidad y comunidad.

---

### Comunicación

| Alternativa | Ventajas | Desventajas | Cuándo usar |
|-------------|----------|-------------|-------------|
| **HTTP REST** | Simple, universal | Overhead alto | Pocos sensores (<10) |
| **MQTT** | Ligero, pub/sub, QoS | Broker adicional | Muchos sensores, conectividad variable |
| **gRPC** | Rápido, tipado, streaming | Complejidad adicional | Microservicios de alto rendimiento |
| **WebSockets** | Bidireccional, tiempo real | Mantener conexiones | Interacción bidireccional constante |
| **Apache Kafka** | Escalable, persistencia | Infraestructura compleja | Miles de sensores, procesamiento de streams |

**Decisión tomada:** HTTP REST por simplicidad. MQTT sería la mejora natural para escalar.

---

### Orquestación

| Alternativa | Ventajas | Desventajas | Cuándo usar |
|-------------|----------|-------------|-------------|
| **Docker Compose** | Simple, local, fácil desarrollo | No escala en producción | Desarrollo, testing, demos |
| **Kubernetes** | Escalabilidad, alta disponibilidad | Complejidad alta | Producción enterprise |
| **Docker Swarm** | Más simple que K8s | Menos features | Producción pequeña-mediana |
| **Nomad** | Flexible, no solo containers | Menos documentación | Infraestructura mixta |

**Decisión tomada:** Docker Compose adecuado para el alcance del proyecto.

---

### Lenguaje del Simulador

| Alternativa | Ventajas | Desventajas | Cuándo usar |
|-------------|----------|-------------|-------------|
| **Python** | Fácil, librerías IoT abundantes | Más lento | Desarrollo rápido, prototipado |
| **Go** | Rápido, bajo consumo, concurrencia | Curva de aprendizaje | Producción, muchos sensores |
| **Node.js** | Async nativo, npm rico | Menos usado en IoT | Integración con ecosistema JS |
| **Rust** | Máximo rendimiento, seguridad | Complejidad alta | Embedded, crítico en recursos |

**Decisión tomada:** Python por productividad y claridad educativa.

---

## 📂 Estructura del Proyecto

```
proyecto-iot-docker/
│
├── docker-compose.yml          # Orquestación de servicios
├── .gitignore                  # Archivos excluidos de Git
├── README.md                   # Este archivo
│
├── sensor/                     # Simulador de sensor
│   ├── Dockerfile              # Imagen del sensor
│   ├── sensor_simulator.py     # Código Python del simulador
│   └── requirements.txt        # Dependencias Python
│
└── grafana/                    # Configuración de Grafana
    ├── dashboards/
    │   └── iot-dashboard.json  # Dashboard exportado
    └── provisioning/
        ├── dashboards/
        │   └── dashboard.yml   # Config de carga de dashboards
        └── datasources/
            └── influxdb.yml    # Config de datasource InfluxDB
```

---


## 📚 Referencias

### Documentación Oficial

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [InfluxDB 2.x Documentation](https://docs.influxdata.com/influxdb/v2.7/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Flux Query Language](https://docs.influxdata.com/flux/v0.x/)

### Tutoriales Útiles

- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [InfluxDB Python Client](https://github.com/influxdata/influxdb-client-python)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)

### Recursos Adicionales

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Time Series Databases Comparison](https://db-engines.com/en/ranking/time+series+dbms)
- [IoT Protocols Overview](https://www.eclipse.org/community/eclipse_newsletter/2014/february/article2.php)

---
