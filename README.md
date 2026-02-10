# 🌡️ Simulador de Sensores IoT con Docker

## 👥 Equipo
- [Tu nombre]

## 📖 Descripción
Sistema de captura de datos IoT que simula un sensor ambiental enviando mediciones en tiempo real a una base de datos InfluxDB, con visualización mediante Grafana.

## 🏗️ Arquitectura

### Componentes:
1. **Sensor Simulator (Python):** Genera datos cada 5 segundos
2. **InfluxDB:** Base de datos de series temporales
3. **Grafana:** Dashboard de visualización en tiempo real

### Diagrama de flujo:
Sensor → InfluxDB → Grafana


## 🚀 Instrucciones de Uso

### Requisitos previos:
- Docker
- Docker Compose

### Ejecución:
```bash
# Arrancar todos los servicios
docker compose up --build

# Acceder a Grafana
http://localhost:3000
Usuario: admin / Contraseña: admin

# Acceder a InfluxDB
http://localhost:8086
Usuario: admin / Contraseña: admin123456
```

### Parar el sistema:
```bash
docker compose down
```

## 📊 Datos Simulados
- **Temperatura:** 18-30°C
- **Humedad:** 40-80%
- **Presión:** 1010-1016 hPa
- **Frecuencia:** Cada 5 segundos

## 💡 Mejoras Posibles
- [ ] Añadir múltiples sensores con diferentes IDs
- [ ] Implementar alertas cuando temperatura > 28°C
- [ ] Usar protocolo MQTT en lugar de HTTP directo
- [ ] Añadir persistencia de configuración de Grafana
- [ ] Dockerizar el dashboard de Grafana (JSON)
- [ ] Añadir API REST para consultar datos

## 🐛 Problemas Encontrados
- **Delay inicial:** El sensor necesita esperar 10s a que InfluxDB esté listo
  - **Solución:** Añadido `time.sleep(10)` y `depends_on` en compose
- **Token hardcodeado:** El token está en el código
  - **Solución propuesta:** Usar Docker secrets en producción

## 🔄 Alternativas Consideradas
- **TimescaleDB** en lugar de InfluxDB (PostgreSQL con extensión temporal)
- **Prometheus** para métricas (pero es más para monitoreo de sistemas)
- **Mosquitto (MQTT)** para comunicación más realista IoT
- **Node-RED** para flujo visual de datos

## 📚 Referencias
- [Documentación InfluxDB](https://docs.influxdata.com/)
- [Documentación Grafana](https://grafana.com/docs/)
- [Docker Compose](https://docs.docker.com/compose/)