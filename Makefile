.DEFAULT_GOAL := help

COMPOSE := docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn
PYTHON ?= .venv3145/bin/python

.PHONY: help up up-d local-python openapi-status urls swagger redoc json \
	down restart ps docker-logs api-logs db-logs docker-config migrate \
	test test-basic test-extra test-compose test-local test-local-basic \
	test-local-extra ruff ruff-fix ruff-format-check ruff-format-fix mypy global-check

help: ## Show available Make targets
	awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up-d: ## Backward-compatible alias for docker-up-d
	@$(MAKE) docker-up-d

docker-up-d: ## Start "To-Do Tasks" service via Docker Compose in detached mode (RECOMMENDED)
	$(COMPOSE) up --build -d
	@echo 'API endpoints (all urls):'
	@printf '%s\n' http://127.0.0.1:8000
	@printf '\n'
	@echo 'API documentation:'
	@printf '%s\n' http://127.0.0.1:8000/docs
	@printf '%s\n' http://127.0.0.1:8000/redoc
	@printf '%s\n' http://127.0.0.1:8000/openapi.json

docker-up: ## Start "To-Do Tasks" service via Docker Compose in the foreground
	$(COMPOSE) up --build

up: ## Backward-compatible alias for docker-up
	@$(MAKE) docker-up

local-python: ## Start "To-Do Tasks" service via local Python
	bash -lc 'load_env_file() { while IFS= read -r line || [ -n "$$line" ]; do case "$$line" in ""|\#*) continue ;; *=*) key=$${line%%=*}; value=$${line#*=}; printf -v "$$key" "%s" "$$value"; export "$$key" ;; esac; done < "$$1"; } && load_env_file ./docker_compose/.env.postgres && load_env_file ./docker_compose/.env.api_uvicorn && $(COMPOSE) up -d db && until $(COMPOSE) exec -T db pg_isready -h 127.0.0.1 -p "$${POSTGRES_PORT:-15433}" -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"; do sleep 1; done && $(PYTHON) -m alembic -c alembic/alembic.ini upgrade head && exec $(PYTHON) -m uvicorn main:app --host "$${API_HOST:-0.0.0.0}" --port "$${API_PORT:-8000}"'

openapi-status: ## Check the live OpenAPI endpoint from inside the API container
	$(COMPOSE) exec -T api python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/openapi.json').status)"

urls: ## Open the API base URL in the browser after the service is running
	@printf '\n'
	@echo 'API endpoints (all urls):'
	@printf '%s\n' http://127.0.0.1:8000

swagger: ## Open Swagger UI in the browser after the service is running
	@printf '\n'
	@echo 'API Swagger documentation:'
	@printf '%s\n' http://127.0.0.1:8000/docs

redoc: ## Open Swagger UI in the browser after the service is running
	@printf '\n'
	@echo 'API Redoc documentation:'
	@printf '%s\n' http://127.0.0.1:8000/redoc

json: ## Open openapi.json in the browser after the service is running
	@printf '\n'
	@echo 'API OpenAPI JSON:'
	@printf '%s\n' http://127.0.0.1:8000/openapi.json

down: ## Stop the Docker stack and remove containers
	$(COMPOSE) down

restart: ## Recreate the Docker stack in detached mode
	$(COMPOSE) down
	$(COMPOSE) up --build -d
	@echo 'API endpoints (all urls):'
	@printf '%s\n' http://127.0.0.1:8000
	@printf '\n'
	@echo 'API documentation:'
	@printf '%s\n' http://127.0.0.1:8000/docs
	@printf '%s\n' http://127.0.0.1:8000/redoc
	@printf '%s\n' http://127.0.0.1:8000/openapi.json

ps: ## Show Docker Compose service status
	$(COMPOSE) ps

docker-logs: ## Show all Docker Compose logs
	$(COMPOSE) logs -f

api-logs: ## Show API container logs
	$(COMPOSE) logs -f api

db-logs: ## Show PostgreSQL container logs
	$(COMPOSE) logs -f db

docker-config: ## Validate the rendered Docker Compose configuration
	$(COMPOSE) config
	@printf '\n'
	@echo 'Docker-Compose configuration [OK]'

migrate: ## Apply Alembic migrations from the host environment
	alembic -c alembic/alembic.ini upgrade head
	@printf '\n'
	@echo 'Alembic migration [OK]'

test: ## Run the full (BASIC + EXTRA) test suite inside the API container
	$(COMPOSE) exec -T api python -m pytest -q -vv

test-basic: ## Run the compact smoke tests (BASIC) inside the API container
	$(COMPOSE) exec -T api python -m pytest -q -vv _tests_basic

test-extra: ## Run the extended test suite (EXTRA) inside the API container
	$(COMPOSE) exec -T api python -m pytest -q -vv _tests_extra

test-compose: ## Run the Docker and Compose contract tests locally
	$(PYTHON) -m pytest -q -vv _tests_extra/docker_compose/test_compose_contract.py

test-local: ## Run the full local test suite (BASIC + EXTRA) with the configured Python interpreter
	$(PYTHON) -m pytest -q -vv

test-local-basic: ## Run the local compact smoke tests (BASIC) with the configured Python interpreter
	$(PYTHON) -m pytest -q -vv _tests_basic

test-local-extra: ## Run the local compact smoke tests (BASIC) with the configured Python interpreter
	$(PYTHON) -m pytest -q -vv _tests_extra

ruff: ## Run Ruff lint checks
	$(PYTHON) -m ruff check . --output-format=full

ruff-fix: ## Run Ruff lint checks with autofix enabled
	$(PYTHON) -m ruff check . --fix

ruff-format-check: ## Check formatting without changing files with Ruff
	$(PYTHON) -m ruff format . --check

ruff-format-fix: ## Format the codebase with Ruff
	$(PYTHON) -m ruff format .

mypy: ## Run static type checks with Mypy
	$(PYTHON) -m mypy .

global-check: ## Run the main local quality gate (ALL TESTS + RUFF + MYPY)
	$(PYTHON) -m pytest -q
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy .
