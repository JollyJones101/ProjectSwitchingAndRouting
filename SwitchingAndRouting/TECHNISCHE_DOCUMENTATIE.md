# Smart Sensor Gateway - Technische Documentatie

**Project:** Containergebaseerd sensor monitoringsysteem  
**Auteur:** Jamie Jones | **Datum:** 2026

## Inhoudsopgave
1. [Overzicht](#overzicht) | 2. [Architectuur](#architectuur) | 3. [Componenten](#componenten) | 4. [Installatie](#installatie) | 5. [Configuratie](#configuratie) | 6. [Monitoring](#monitoring) | 7. [Deployment](#deployment) | 8. [Troubleshooting](#troubleshooting)

---

## Overzicht

Edge-gateway systeem dat sensordata verzamelt via **MQTT** → verwerkt met **Node-RED** → opslaat in **InfluxDB** → visualiseert via dashboards. Alles draait in Docker containers, beheerd via **Portainer**.

| Onderdeel | Technologie | Versie |
|-----------|-------------|--------|
| Container runtime | Docker | 24.x |
| Orchestratie | Docker Compose | 2.x |
| Message Broker | Mosquitto | 2.0 |
| Data Processing | Node-RED | latest |
| Time-series DB | InfluxDB | 2.7 |
| Container Mgmt | Portainer | CE |
| Sensor Sim | Python | 3.x |

---

## Architectuur

```
Sensors → MQTT (Mosquitto) → Node-RED (validation/format) → InfluxDB → Dashboard
                                        ↓
                                  Portainer (monitoring)
```

**Data Flow:**
- Sensor Simulator publiceert joystick (x,y) & buttons (bool) naar MQTT
- Node-RED abonneert op topics, valideert ranges, converteert naar Line Protocol
- HTTP POST naar InfluxDB
- InfluxDB opslaat in bucket `sensordata`
- Dashboard query's via Flux language

**Networks:**
- `sensor-network`: mosquitto, nodered, influxdb, sensor_sim
- `portainer-network`: portainer

---

## Componenten

### 1. Mosquitto MQTT Broker

- **Port:** 1883 (MQTT), 9001 (WebSocket)
- **Config:** `docker/mosquitto.conf` - anonymous access, persistence
- **Topics:** `sensor/joystick` (x,y floats), `sensor/buttons` (booleans)

### 2. Sensor Simulator (Python)

- **Image:** Dockerfile in `sensor-sim/`
- **Publiceert:** Joystick & button data elk seconde
- **Env vars:** `MQTT_BROKER`, `MQTT_PORT`

### 3. Node-RED Data Processing

**Port:** 1880 | **Flows:**
- MQTT Input → Validation Functions → Format for InfluxDB → HTTP POST

**Validation:**
- Joystick: range check (-1 tot 1), round naar 2 decimals
- Buttons: type coercion (bool/number/string → boolean)

**Format:** Converteert naar InfluxDB Line Protocol
```
joystick x=0.45,y=-0.78
buttons button1=0,button2=1
```

### 4. InfluxDB v2.7

- **Port:** 8086
- **Org:** mineorg | **Bucket:** sensordata | **Token:** supersecrettoken
- **Retention:** 30 days
- **Data:** Joystick (x,y) & Buttons (b1,b2) measurements

### 5. Portainer CE

- **Port:** 9000 (HTTP), 9443 (HTTPS)
- **Auto-init:** Admin account via `portainer_init` service
- **Doel:** Container monitoring & management UI

### 6. Dashboards

InfluxDB UI + pre-configured YAML dashboards via `scripts/import_influx_dashboard.sh`

---

## Installatie

### Stap 1: Setup
```bash
cd SwitchingAndRouting

# .env bestand aanmaken
cat > .env << EOF
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=secure123
INFLUXDB_ORG=mineorg
INFLUXDB_BUCKET=sensordata
INFLUXDB_TOKEN=supersecrettoken
PORTAINER_USER=admin
PORTAINER_PASS=portainer_pass
EOF
```

### Stap 2: Deploy
```bash
make deploy
# Of: docker-compose up -d

make status
```

### Stap 3: Verificatie
```bash
# Logs controleren
docker-compose logs -f
docker-compose ps
# Data importeren
./scripts/import_influx_dashboard.sh

# Access:
# Node-RED: http://localhost:1880
# InfluxDB: http://localhost:8086
# Portainer: http://localhost:9000
```

---

## Configuratie

### Environment Variabelen (.env)

#### InfluxDB (`docker-compose.yml`)

```yaml
environment:
  - DOCKER_INFLUXDB_INIT_MODE=setup          # Eenmalige setup
  - DOCKER_INFLUXDB_INIT_USERNAME=admin      # Web UI user
  - DOCKER_INFLUXDB_INIT_PASSWORD=...        # Web UI pass
  - DOCKER_INFLUXDB_INIT_ORG=mineorg         # Org name
  - DOCKER_INFLUXDB_INIT_BUCKET=sensordata   # Data bucket
  - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=...     # API token
```

#### Sensor Simulator (`docker-compose.yml`)

```yaml
environment:
  - MQTT_BROKER=mosquitto      # Broker hostname
  - MQTT_PORT=1883             # MQTT port
```

#### Portainer Init

```yaml
environment:
  - PORTAINER_USER=       # Admin username
  - PORTAINER_PASS=    # Admin password
```

### Mosquitto Configuratie (`docker/mosquitto.conf`)

```ini
# MQTT listener configuratie
listener 1883              # Standard MQTT port
protocol mqtt

# Toegangscontrole (dev environment)
allow_anonymous true       # Geen auth vereist

# Persistentie (message durability)
persistence true
persistence_location /mosquitto/data/

# Logging
log_dest stdout           # Logs naar container output
```

**Productie-Aanbevelingen:**
```ini
# Enable authentication
allow_anonymous false
password_file /mosquitto/config/passwd

# Enable TLS/SSL
listener 8883
protocol mqtt
cafile /mosquitto/config/certs/ca.crt
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key

# Rate limiting
max_connections -1        # Onbeperkt
message_size_limit 0

# Logging detail
log_dest file /var/log/mosquitto/mosquitto.log
log_timestamp true
log_type all
```

### Node-RED Configuration (`docker/nodered/settings.js`)

- Flow & credentials persisteren naar volume
- Gebruik credentials.json voor gevoelige data (encrypted)
- Theme & UI customisatie
---

## Werking & Monitoring

### Web Interfaces Overzicht

| Interface | URL | Doel | Login |
|-----------|-----|------|-------|
| Node-RED | http://localhost:1880 | Flow editor | None (dev) |
| InfluxDB UI | http://localhost:8086 | Query builder, dashboards | admin / pass |
| Portainer | http://localhost:9000 | Container management | admin / pass |
| MQTT Web UI | http://localhost:9001 | MQTT test client | None |

### Node-RED Flow Monitoring

#### Flow anschouwen
1. Open http://localhost:1880
2. Tab "Flow 1" tonen
3. Nodes zichtbaar:
   - **mqtt_in_joystick** - Joystick input
   - **mqtt_in_buttons** - Button input
   - **f1, f1b** - Validation functions
   - **fmtj, fmtb** - Format functions
   - **httpr_j, httpr_b** - HTTP output nodes

#### Debug View
- **Right panel:** Debug messages van `debug_joystick` / `debug_buttons` nodes
- **Console logs:** Validation results, errors
- **Flow status:** Groene bolletje = connected

### InfluxDB Monitoring

#### Data Verifiëren
```bash
# In InfluxDB UI:
1. Data Explorer → sensordata bucket
2. Measurement: joystick, buttons
3. Selecteer Fields: x, y, button1, button2
4. Time range: Last 1h
5. Visualize
```

### Portainer Container Monitoring

#### Status Checken
1. http://localhost:9000 openen
2. Home → Containers
3. Zien:
   - Container status (Running/Exited)
   - CPU/Memory usage
   - Logs in real-time
   - Start/Stop/Restart controls

#### Logs bekijken
```bash
# Via CLI
docker-compose logs -f sensor_sim
docker-compose logs -f nodered
docker-compose logs -f influxdb
```

## CI/CD & Deployment

### Makefile Commando's

**Locatie:** Makefile in project root

#### Build Commands

```bash
# Build custom images (sensor_sim)
make build

# Output:
# [1/1] Building custom images...
# Building image sensor_sim:latest
# Build complete.
```

#### Deployment Commands

```bash
# Full CI/CD cycle: build → down → up
make deploy

# Output:
# ========================================
#   Starting deployment...
# ========================================
# [1/3] Building updated images...
# [2/3] Stopping old containers...
# [3/3] Starting new stack...
# ========================================
#   Deployment complete!
#   Portainer : http://localhost:9000
#   Node-RED  : http://localhost:1880
#   InfluxDB  : http://localhost:8086
# ========================================
```

#### Operational Commands

```bash
# Start stack (without rebuild)
make up

# Stop stack (volumes blijven)
make down

# Restart (sneller dan deploy)
make restart

# View live logs
make logs

# Check container status
make status

# Full reset (delete volumes) - REQUIRES CONFIRMATION
make clean

# Remove unused Docker resources
make prune
```

### Port Already in Use

```bash
# Find process using port
lsof -i :1883  # MQTT
lsof -i :1880  # Node-RED
lsof -i :8086  # InfluxDB
lsof -i :9000  # Portainer

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
# Then redeploy
make deploy
```


---

## Appendix

### A. Docker Compose Service Dependency Graph

```
portainer_init
    ↓ depends_on
portainer

nodered
    ↑ depends_on
    ├─ mosquitto
    ├─ influxdb
    ↓

mosquitto
    ↑ depends_on
sensor_sim

influxdb
    ← used by nodered
    ← used by influxdb_init

influxdb_init
    ↓ depends_on
influxdb
```

---

## Contact & Support

- **Projectleider:** Jamie Jones
- **Deployment Host:** Proxmox VM (Ubuntu 24.04.4)
- **Documentatie:** hier

---