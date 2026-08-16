COMPOSE = docker compose

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make up       Start the stack"
	@echo "  make down     Stop the stack"
	@echo "  make rebuild  Rebuild images and start the stack"
	@echo "  make logs     Follow logs"
	@echo "  make status   Show running containers"

.PHONY: up
down:
	$(COMPOSE) down

.PHONY: up
up:
	$(COMPOSE) up -d

.PHONY: rebuild
rebuild:
	$(COMPOSE) up -d --build

.PHONY: logs
logs:
	$(COMPOSE) logs -f

.PHONY: status
status:
	$(COMPOSE) ps
