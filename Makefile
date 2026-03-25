# Variables
export TAG ?= latest
COMPOSE ?= docker-compose

.PHONY: help build start stop cleanup logs restart status dev

help:
	@echo "======================================================================"
	@echo "               Server Management Makefile                 "
	@echo "======================================================================"
	@echo "Usage: make [target] [TAG=tag_name]"
	@echo ""
	@echo "Targets:"
	@echo "  dev         Start development environment with hot-reload"
	@echo "  build       Build docker images (uses TAG, default is 'latest')"
	@echo "  start       Start all services in detached mode"
	@echo "  stop        Stop all services"
	@echo "  cleanup     Stop and remove containers, networks, volumes, and images"
	@echo "  restart     Restart all services"
	@echo "  logs        Follow log output for all services"
	@echo "  status      Show the status of all services"
	@echo "======================================================================"

dev:
	@echo "Starting development environment with hot-reload..."
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

build:
	@echo "Building images with tag: $${TAG}"
	$(COMPOSE) build

start:
	@echo "Starting services..."
	$(COMPOSE) up -d

stop:
	@echo "Stopping services..."
	$(COMPOSE) stop

cleanup:
	@echo "Cleaning up containers, networks, volumes, and images..."
	$(COMPOSE) down -v --rmi all

restart: stop start

logs:
	$(COMPOSE) logs -f

status:
	$(COMPOSE) ps
