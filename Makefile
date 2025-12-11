# Makefile for UniMarket (updated to use local image for migrations)
# Usage (examples):
#   make dev
#   make prod
#   make migrate
#   make migrate-local    # run alembic locally (requires venv)
#   make build
#   make down-prod
#   make logs

SHELL := /bin/bash

COMPOSE_PROD ?= docker-compose.prod.yml
COMPOSE_DEV ?= docker-compose.dev.yml
ENV_PROD ?= .env.production
ENV_DEV ?= .env.development

# Image names (local)
IMAGE_PROD ?= unimarket:latest
IMAGE_DEV ?= unimarket-dev:latest

# network name used in docker-compose.prod.yml (should match your compose file)
COMPOSE_NETWORK ?= unimarket_net

.PHONY: help build prod down-prod migrate migrate-local migrate-prod-db dev down-dev logs test lint

help:
	@echo "UniMarket Makefile - quick targets"
	@echo "  make build         - build production Docker image ($(IMAGE_PROD))"
	@echo "  make prod          - build image and start production compose (uses $(COMPOSE_PROD))"
	@echo "  make migrate       - build image, start DB (prod compose), run alembic in a temporary container from local image"
	@echo "  make migrate-local - run alembic upgrade head locally (requires venv & alembic installed)"
	@echo "  make down-prod     - stop production compose"
	@echo "  make dev           - start development compose (hot reload)"
	@echo "  make logs          - follow dev compose web logs"
	@echo

# ----------------------------
# Build & Prod
# ----------------------------
build: ## Build production image locally
	@echo "[make] Building production image: $(IMAGE_PROD)"
	docker build -t $(IMAGE_PROD) .

prod: build ## Start production compose (builds image and runs docker-compose.prod.yml)
	@echo "[make] Starting production compose (file: $(COMPOSE_PROD))"
	# make sure DB is up (depends_on in compose will handle full stack)
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_PROD) up -d --build

down-prod: ## Stop production compose
	@echo "[make] Stopping production compose"
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_PROD) down -v

# ----------------------------
# Migrations (use local image)
# ----------------------------
# Strategy:
# 1) Build local image unimarket:latest (if needed)
# 2) Start DB service so network & DB exist
# 3) Run temporary container from local image that executes alembic upgrade head
# 4) Remove temporary container
migrate: build ## Build image, start DB and run migrations using local image
	@echo "[make] Running migrations using local image: $(IMAGE_PROD)"
	# 1) ensure DB service is up (we only start DB to create network & DB)
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_PROD) up -d db

	# 2) Wait a little for DB to become ready (basic)
	@echo "[make] Waiting for DB to become available (sleep 3s)..."
	sleep 3

	# 3) Run migrations inside a temporary container from local image.
	#    It will reuse the compose network so DB is reachable by service name (db).
	docker run --rm \
	  --network $(COMPOSE_NETWORK) \
	  --env-file $(ENV_PROD) \
	  $(IMAGE_PROD) \
	  /bin/sh -c "alembic upgrade head"

	@echo "[make] Migrations finished."

migrate-local: ## Run alembic upgrade head locally (requires venv & alembic installed)
	@echo "[make] Running alembic locally"
	python -m alembic upgrade head

# ----------------------------
# Development helpers
# ----------------------------
dev:
	@echo "[make] Starting dev compose (hot-reload, bind mount)"
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_DEV) up -d --build

down-dev:
	@echo "[make] Stopping dev compose"
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_DEV) down -v

logs:
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_DEV) logs -f web

# ----------------------------
# Quality & Tests
# ----------------------------
test:
	pytest -q

lint:
	black --check .
	isort --check-only .
	flake8 .
	mypy .

fmt:
	black .

# ----------------------------
# Utilities
# ----------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
