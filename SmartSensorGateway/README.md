# Smart Sensor Gateway

This project is a clean, from-scratch implementation of a local edge gateway for sensor data.

## Components
- MQTT broker: Mosquitto
- Data processing: Node-RED
- Time-series database: InfluxDB 2.x
- Sensor simulator: Python script
- Container management: Portainer

## Stack
- MQTT broker receives sensor updates on `sensors/joy` and `sensors/btn`
- Node-RED validates and routes the messages
- InfluxDB stores the cleaned readings
- Portainer exposes the Docker environment

## Quick start
1. Go to the project folder.
2. Verify the `.env` file.
3. Run:

```bash
docker compose --env-file .env up -d --build
```

4. Open the following endpoints (see `.env` for current port mappings):
   - Node-RED: http://localhost:1880
   - Portainer: http://localhost:9000
   - InfluxDB: http://localhost:8086
   - Mosquitto MQTT: localhost:1883
   - Mosquitto WebSocket: http://localhost:9001

## Useful commands
```bash
docker compose logs -f
make up
make down
make rebuild
```

## Default credentials
- InfluxDB user: `edgeadmin`
- InfluxDB password: `EdgeSensor!2026`
- Portainer user: `edgeadmin`
- Portainer password: `EdgePortainer!2026`

## Notes
The project is intentionally kept simple and production-friendly so it can be used as a starting point for a bigger edge stack.
