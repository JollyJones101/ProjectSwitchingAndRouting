# Smart Sensor Gateway - Technische Documentatie

**Project:** Containergebaseerd sensor monitoringsysteem  
**Auteur:** Jamie Jones | **Datum:** 2024

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
- `portainer-network`: portainer, portainer_init

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
buttons button1=true,button2=false
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

sleep 30  # Wacht tot services starten
make status
```

### Stap 3: Verificatie
```bash
# Logs controleren
docker-compose logs -f

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
  - PORTAINER_USER=admin       # Admin username
  - PORTAINER_PASS=password    # Admin password
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

**Aanbevolen settings:**
```javascript
module.exports = {
    httpRequestTimeout: 120000,
    
    // Editor bescherming
    adminAuth: {
        type: "credentials",
        users: [{
            username: "admin",
            password: "hash_of_password",
            permissions: "*"
        }]
    },
    
    // File persistentie
    userDir: "/data/",
    
    // Logging level
    logging: {
        console: {
            level: "info"
        }
    }
}
```

### InfluxDB Data Retention Policy

```bash
# Retention policies instellen via CLI
influx bucket create \
    --name sensordata \
    --org mineorg \
    --retention 30d          # 30 dagen retention
```

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

#### Flux Query Voorbeeld
```flux
from(bucket: "sensordata")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "joystick")
  |> filter(fn: (r) => r._field == "x")
  |> mean()
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

### Health Checks

#### Mosquitto Health
```bash
docker exec switchingandrouting-mosquitto-1 \
    mosquitto_sub -h localhost -t sensor/+
```

#### Node-RED Health
```bash
curl http://localhost:1880/flows
# Return: flow config JSON
```

#### InfluxDB Health
```bash
curl -i http://localhost:8086/health
# Return: HTTP 200 OK + health JSON
```

#### Sensor Simulator Health
```bash
docker logs switchingandrouting-sensor_sim-1 | tail -20
# Check for: "Published joystick", "Published buttons"
```

### Performance Monitoring

#### CPU/Memory per Service
```bash
docker stats --no-stream
```

**Expected:**
- mosquitto: <5% CPU, <100 MB RAM
- nodered: <10% CPU, <200 MB RAM
- influxdb: <20% CPU, <500 MB RAM
- sensor_sim: <1% CPU, <50 MB RAM
- portainer: <5% CPU, <150 MB RAM

#### Data Throughput
- **Joystick:** 1 msg/sec (typ. 50 bytes)
- **Buttons:** 1 msg/sec (typ. 40 bytes)
- **Total MQTT:** ~90 bytes/sec = ~7.8 MB/dag
- **InfluxDB write:** ~2-3 req/sec

### Common Issues & Diagnostics

**Container fails to start:**
```bash
docker-compose logs <service-name>
docker inspect <container-id>
```

**MQTT connection refused:**
```bash
docker exec mosquitto netstat -tulpn
# Check port 1883 active
```

**InfluxDB init failed:**
```bash
docker logs influxdb_init
# Check: token, org name, bucket name
```

**Node-RED flows not saved:**
```bash
ls -la docker/nodered/
# Check: flows.json, flows_cred.json exist
docker exec nodered ls /data/
```

---

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

### Deployment Scenarios

#### Scenario 1: Eerste Keer Deploy

```bash
cd /path/to/project

# 1. Setup environment
cat > .env << EOF
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=secure123
INFLUXDB_ORG=mineorg
INFLUXDB_BUCKET=sensordata
INFLUXDB_TOKEN=secret_token_123
PORTAINER_USER=admin
PORTAINER_PASS=portainer_pass
EOF

# 2. Deploy
make deploy

# 3. Wacht ~30 sec voor alle services
sleep 30

# 4. Verificatie
make status

# 5. Import dashboard
./scripts/import_influx_dashboard.sh

# 6. Access http://localhost:9000
```

#### Scenario 2: Code Update in sensor_sim

```bash
# 1. Update code
vim sensor-sim/sensor_sim.py

# 2. Rebuild & redeploy
make deploy

# 3. Monitor output
make logs
```

#### Scenario 3: Quick Service Restart

```bash
# Only restart without rebuild (faster)
make restart

# Verify
make status
```

#### Scenario 4: Clean Reset

```bash
# Waarschuwing: verwijdert alle volumes!
make clean

# Redeploy everything
make deploy
```

### Automatisatie in Production

**Gebruiken met systemd timer (Linux VM):**

```ini
# /etc/systemd/system/sensor-stack-deploy.service
[Unit]
Description=Sensor Stack Deployment
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/sensor-stack
ExecStart=/usr/bin/make deploy

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/sensor-stack-deploy.timer
[Unit]
Description=Daily Sensor Stack Deployment

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable:**
```bash
systemctl daemon-reload
systemctl enable sensor-stack-deploy.timer
systemctl start sensor-stack-deploy.timer
```

### GitHub Actions CI/CD (Advanced)

```yaml
# .github/workflows/deploy.yml
name: Deploy Sensor Stack

on:
  push:
    branches: [main]
    paths:
      - 'sensor-sim/**'
      - 'docker-compose.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SSH Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/sensor-stack
            git pull origin main
            make deploy
```

---

## Troubleshooting

### Container Won't Start

**Symptom:** Container exits immediately

```bash
# Diagnose
docker-compose logs <service>

# Mogelijke oorzaken:
# 1. Port already in use
sudo lsof -i :1883
# Fix: Kill process of change port in docker-compose.yml

# 2. Missing .env file
cat .env  # Should show variables

# 3. Insufficient resources
docker stats  # Check free RAM/CPU
free -h
```

### MQTT Connectivity Issues

**Symptom:** Node-RED cannot connect to Mosquitto

```bash
# Verify mosquitto is running
docker ps | grep mosquitto

# Test MQTT connection
docker exec nodered mosquitto_sub -h mosquitto -t sensor/+

# Check network
docker network ls | grep sensor-network
docker network inspect sensor-network

# Fix: Ensure mosquitto in sensor-network
docker-compose down
docker-compose up -d
```

### InfluxDB Authentication Failed

**Symptom:** "Unauthorized" error in Node-RED logs

```bash
# Verify token in environment
echo $INFLUXDB_TOKEN
grep INFLUXDB_TOKEN .env

# Regenerate token if needed
docker exec influxdb influx auth list

# Update Node-RED format functions with correct token
# Restart services
make restart
```

### High CPU/Memory Usage

**Symptom:** System slow, containers using >30% CPU

```bash
# Monitor per container
docker stats --no-stream

# Common causes:
# 1. Too many MQTT messages → rate limit in sensor_sim
# 2. InfluxDB disk full → cleanup old buckets
# 3. Node-RED memory leak → restart
#    docker-compose restart nodered

# Check disk space
df -h /var/lib/docker

# Cleanup old logs
docker system prune
```

### Data Not Appearing in Dashboard

**Symptom:** Dashboard shows "No data"

**Debugging flow:**
```bash
# 1. Check sensor_sim output
docker logs -f sensor_sim | head -20

# 2. Check Mosquitto receiving messages
docker exec mosquitto mosquitto_sub -h localhost -t sensor/+

# 3. Check Node-RED debug panel
# Open http://localhost:1880 → Debug messages

# 4. Check InfluxDB data
curl -H "Authorization: Token supersecrettoken" \
  http://localhost:8086/api/v2/query \
  -d "query=from(bucket:\"sensordata\")|>range(start:-1h)"

# 5. If no data: check Node-RED flows are running
docker logs -f nodered | grep -i "error\|payload"
```

### Dashboard Import Failed

```bash
# Rerun import script with debug
bash -x ./scripts/import_influx_dashboard.sh

# Manual import
curl -X POST http://localhost:8086/api/v2/dashboards \
  -H "Authorization: Token supersecrettoken" \
  -H "Content-Type: application/json" \
  --data-binary @docker/influxdb/sensor_dashboard.yaml
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

### Network/Firewall Issues (VM Deployment)

```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 1883/tcp
sudo ufw allow 1880/tcp
sudo ufw allow 8086/tcp
sudo ufw allow 9000/tcp

# Check Docker network subnet
docker network inspect sensor-network | grep Subnet

# Test connectivity from host to container
ping 172.17.0.2  # Mosquitto
curl http://172.17.0.3:1880/flows  # Node-RED
```

---

## Beveiligingsopmerkingen

### Huidige Status: Development Environment

⚠️ Dit project is geconfigureerd voor **ontwikkelings- en testomgevingen**. Het volgende is NIET productie-gereed:

| Aspect | Current | Issue | Aanbeveling |
|--------|---------|-------|-------------|
| **MQTT Auth** | None | Elke client kan connecteren | Implementeer username/password auth |
| **TLS/SSL** | Disabled | Man-in-the-middle risk | Enable TLS op poort 8883 |
| **API Auth** | Basic Token | Token in code/logs | Use OAuth2 / API keys in vault |
| **Node-RED** | Unprotected | Direct flow access | Enable adminAuth in settings.js |
| **Portainer** | Dev credentials | Weak auth | Use strong passwords, 2FA |
| **Network** | All public | Port exposed | Firewall only to trusted IPs |
| **Secrets** | In .env file | Git leak risk | Use Docker secrets / Hashicorp Vault |
| **Logging** | No audit log | No security tracking | Implement centralized logging |

### Productie Hardening Checklist

#### 1. MQTT Security
```ini
# mosquitto.conf
allow_anonymous false
password_file /mosquitto/config/passwd

listener 8883
protocol mqtt
cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
```

#### 2. InfluxDB Access Control
```bash
# Create limited-permission tokens
influx auth create \
  --description "Node-RED write token" \
  --org mineorg \
  --write-bucket sensordata
```

#### 3. Network Isolation
```yaml
# docker-compose.yml
networks:
  sensor-network:
    driver: bridge
    # Restrict to internal only
    driver_opts:
      com.docker.network.bridge.name: br_sensor
```

#### 4. Data Encryption
- Volume encryption: LUKS on Linux
- In-transit: TLS/SSL on all connections
- At-rest: Database encryption (InfluxDB Enterprise)

#### 5. Access Logging
```bash
# Enable audit logs in InfluxDB
docker exec influxdb \
  influx config create -n audit \
    -t INFLUXDB_TOKEN \
    -o mineorg \
    -u http://localhost:8086
```

#### 6. Regular Backups
```bash
#!/bin/bash
# Backup InfluxDB data
docker exec influxdb \
  influx backup /backups/influxdb-$(date +%Y%m%d)

# Backup volumes
tar -czf backups/volumes-$(date +%Y%m%d).tar.gz \
  docker/influxdb docker/nodered
```

### Vulnerability Scanning

```bash
# Scan Docker images for CVEs
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image sensor_sim:latest

# Update images regularly
docker pull nodered/node-red:latest
docker pull influxdb:2.7
docker pull eclipse-mosquitto:2.0
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

### B. Flux Query Voorbeelden

```flux
# Query 1: Last 24h joystick X values
from(bucket: "sensordata")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "joystick")
  |> filter(fn: (r) => r._field == "x")

# Query 2: 1-hour moving average
from(bucket: "sensordata")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "joystick")
  |> filter(fn: (r) => r._field == "y")
  |> window(every: 1h)
  |> mean()

# Query 3: Button events (where value changed)
from(bucket: "sensordata")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "buttons")
  |> difference()
  |> filter(fn: (r) => r._value != 0)
```

### C. Environment Variables Reference

```bash
# .env template
# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883
TOPIC_JOYSTICK=sensor/joystick
TOPIC_BUTTONS=sensor/buttons

# InfluxDB v2
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password
INFLUXDB_ORG=mineorg
INFLUXDB_BUCKET=sensordata
INFLUXDB_TOKEN=your_secure_token_123456
DOCKER_INFLUXDB_INIT_MODE=setup

# Portainer
PORTAINER_USER=admin
PORTAINER_PASS=your_portainer_password
```

### D. Network Debugging Commands

```bash
# List all networks
docker network ls

# Inspect sensor-network
docker network inspect sensor-network

# Test DNS from container
docker exec nodered nslookup mosquitto

# Test port connectivity
docker exec nodered nc -zv mosquitto 1883

# View network traffic
docker exec mosquitto netstat -tulpn
```

### E. Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect portainer_data

# Backup volume
docker run -v portainer_data:/data \
  -v /tmp:/backup \
  alpine tar -czf /backup/portainer_data.tar.gz /data

# Restore volume
docker run -v portainer_data:/data \
  -v /tmp:/backup \
  alpine tar -xzf /backup/portainer_data.tar.gz -C /
```

### F. Performance Tuning

#### Mosquitto
```ini
max_connections -1           # Unlimited connections
max_queued_messages 1000     # Per-client queue size
```

#### InfluxDB
```bash
# Increase cache/memory
docker-compose.yml:
  influxdb:
    environment:
      - INFLUXDB_CACHE_MAX_MEMORY_BYTES=536870912  # 512MB
```

#### Node-RED
```javascript
// settings.js
module.exports = {
    functionGlobalContext: {},
    functionExternalModules: true,  // Enable npm modules
    httpRequestTimeout: 120000,      // 2 minutes timeout
}
```

---

## Versiebeheer

| Versie | Datum | Wijzigingen |
|--------|-------|-------------|
| 1.0 | 2024-05-10 | Initiële documentatie |
| - | - | - |

---

## Contact & Support

- **Projectleider:** Jamie Jones
- **Deployment Host:** Proxmox VM (Ubuntu 24.04.4)
- **Documentatie:** Dit bestand

---

**Einde van Technische Documentatie**
