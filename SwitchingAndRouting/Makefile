# =============================================================================
#  CI/CD Makefile — Sensor Monitoring Stack
#  Gebruik: make <target>
# =============================================================================

COMPOSE         = docker compose
PROJECT_NAME    = switchingandrouting
SENSOR_SIM_IMG  = sensor_sim:latest

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# help — toon alle beschikbare commando's
# -----------------------------------------------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "  Sensor Monitoring Stack — beschikbare commando's"
	@echo "  ================================================="
	@echo ""
	@echo "  make build       Bouw gewijzigde images opnieuw"
	@echo "  make up          Start de volledige stack op"
	@echo "  make down        Stop en verwijder alle containers"
	@echo "  make deploy      Volledige CI/CD cyclus: build → down → up"
	@echo "  make restart     Herstart de stack zonder rebuild"
	@echo "  make logs        Toon live logs van alle services"
	@echo "  make status      Toon de status van alle containers"
	@echo "  make clean       Stop stack en verwijder volumes (reset)"
	@echo "  make prune       Verwijder ongebruikte Docker resources"
	@echo ""

# -----------------------------------------------------------------------------
# build — bouw alleen de custom images (sensor_sim)
# -----------------------------------------------------------------------------
.PHONY: build
build:
	@echo "[1/1] Building custom images..."
	$(COMPOSE) build --no-cache sensor_sim
	@echo "Build complete."

# -----------------------------------------------------------------------------
# up — start de volledige stack in de achtergrond
# -----------------------------------------------------------------------------
.PHONY: up
up:
	@echo "Starting stack..."
	$(COMPOSE) up -d
	@echo "Stack is running. Portainer: http://localhost:9000"

# -----------------------------------------------------------------------------
# down — stop en verwijder containers (volumes blijven bewaard)
# -----------------------------------------------------------------------------
.PHONY: down
down:
	@echo "Stopping stack..."
	$(COMPOSE) down
	@echo "Stack stopped."

# -----------------------------------------------------------------------------
# deploy — volledige CI/CD cyclus
#   1. Bouw nieuwe images
#   2. Stop oude containers
#   3. Start nieuwe stack op
# -----------------------------------------------------------------------------
.PHONY: deploy
deploy:
	@echo "========================================"
	@echo "  Starting deployment..."
	@echo "========================================"
	@echo ""
	@echo "[1/3] Building updated images..."
	$(COMPOSE) build --no-cache sensor_sim
	@echo ""
	@echo "[2/3] Stopping old containers..."
	$(COMPOSE) down
	@echo ""
	@echo "[3/3] Starting new stack..."
	$(COMPOSE) up -d
	@echo ""
	@echo "========================================"
	@echo "  Deployment complete!"
	@echo "  Portainer : http://localhost:9000"
	@echo "  Node-RED  : http://localhost:1880"
	@echo "  InfluxDB  : http://localhost:8086"
	@echo "========================================"

# -----------------------------------------------------------------------------
# restart — herstart stack zonder rebuild (sneller dan deploy)
# -----------------------------------------------------------------------------
.PHONY: restart
restart:
	@echo "Restarting stack..."
	$(COMPOSE) down
	$(COMPOSE) up -d
	@echo "Stack restarted."

# -----------------------------------------------------------------------------
# logs — volg live logs (Ctrl+C om te stoppen)
# -----------------------------------------------------------------------------
.PHONY: logs
logs:
	$(COMPOSE) logs -f

# -----------------------------------------------------------------------------
# status — toon de huidige containerstatus
# -----------------------------------------------------------------------------
.PHONY: status
status:
	$(COMPOSE) ps

# -----------------------------------------------------------------------------
# clean — volledige reset inclusief volumes (portainer account wordt gewist!)
# -----------------------------------------------------------------------------
.PHONY: clean
clean:
	@echo "WARNING: This will delete all volumes including Portainer data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(COMPOSE) down -v
	@echo "Stack and volumes removed."

# -----------------------------------------------------------------------------
# prune — ruim ongebruikte Docker images/netwerken op
# -----------------------------------------------------------------------------
.PHONY: prune
prune:
	@echo "Pruning unused Docker resources..."
	docker image prune -f
	docker network prune -f
	@echo "Prune complete."
