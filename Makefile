

PROJECT_NAME = opensource-customgpt-builder
PG_VOLUME = $(PROJECT_NAME)_pgdata
FRONTEND_VOLUME = $(PROJECT_NAME)_frontend_node_modules

COMPOSE_DEV = docker compose -p $(PROJECT_NAME) -f docker-compose.dev.yaml
COMPOSE_LOCUST := docker compose -f backend/tests_perf_locust/docker-compose.locust-perf.yaml
PYTEST_FLAGS := -q -s --maxfail=1 -m 'not performance'
PYTEST_FLAGS_PERFORMANCE := -q -s --maxfail=1 -m performance



.PHONY: generate-client-prod test test-unit test-integration test-unit-exec test-integration-exec test-clean up down restart logs ps rebuild clean-restart-db

## ----------------------DEV STACK----------------------

up:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE_DEV) down

restart:
	$(COMPOSE_DEV) down
	$(COMPOSE_DEV) up -d

logs:
	$(COMPOSE_DEV) logs -f

ps:
	$(COMPOSE_DEV) ps

rebuild:
	$(COMPOSE_DEV) build --no-cache

clean-restart-frontend:
	$(COMPOSE_DEV) stop frontend
	$(COMPOSE_DEV) rm -f frontend
	docker volume rm $(FRONTEND_VOLUME) || true
	$(COMPOSE_DEV) build --no-cache frontend
	$(COMPOSE_DEV) up -d frontend

clean-restart-db:
	$(COMPOSE_DEV) stop postgres
	$(COMPOSE_DEV) rm -f postgres
	docker volume rm $(PG_VOLUME) || true
	$(COMPOSE_DEV) build --no-cache postgres
	$(COMPOSE_DEV) up -d postgres

## ----------------------PYTEST FUNCTIONAL----------------------
tests:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests"

test-show-setup:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) --setup-show -s tests"

test-use-cases:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) -s test_rest_api_use_cases"

## Run only unit tests
test-unit:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/unit"

## Run only external api tests -might cost money
test-external-api-adapters:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) test_external_api_adapters"


test-contracts:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/contracts"

## Run only integration tests
test-integration:
	$(COMPOSE_DEV) up -d postgres
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/integration"

## (Optional) Run tests in an already-running backend container
test-unit-exec:
	$(COMPOSE_DEV) exec backend pytest $(PYTEST_FLAGS) tests/unit

test-integration-exec:
	$(COMPOSE_DEV) exec backend pytest $(PYTEST_FLAGS) tests/integration

## Clean up any stopped test containers
test-clean:
	$(COMPOSE_DEV) rm -f


## ----------------------PYTEST PERFORMANCE----------------------

test-use-cases-perf:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) -s test_rest_api_use_cases"

test-integration-perf:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) tests/integration"

test-perf:
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) tests"
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) -s test_rest_api_use_cases"
# 	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE)" tests
# #replace the automatically generated base/url of the backend api 
# #with the one defined as environment variable (if not already done)
# fix-openapi-base:
# 	docker-compose -f docker-compose.dev.yaml exec frontend \
# 	sh -c 'grep -q "import.meta.env.VITE_APP_DOMAIN" src/client/core/OpenAPI.ts || sed -i '\''s|BASE: .*|BASE: import.meta.env.VITE_APP_DOMAIN + "/api",|'\'' src/client/core/OpenAPI.ts'
# NOT YET WORKING

## ----------------------LOCUST PERFORMANCE----------------------
locust:
	$(COMPOSE_LOCUST) run --rm locust sh -c "locust -f locustfile.py --html 'results/locust_results_$$(date +%Y%m%d_%H%M%S).html'"


## ----------------------LINTING, TYPECHECKING AND CO----------------------
ruff:
	ruff check backend
	ruff format backend
ruff-fix-save:
	ruff check backend --fix
	ruff format backend



# Waits until the backend container is marked as healthy, then runs codegen
generate-client-prod:
	@echo "🔄 Starting containers..."
	docker-compose -f docker-compose.dev.yaml up -d

	@echo "⏳ Waiting for backend to be marked healthy..."
	until [ "$$(docker inspect --format='{{.State.Health.Status}}' backend)" = "healthy" ]; do \
		echo "⏳ Backend not healthy yet..."; \
		sleep 2; \
	done

	@echo "⚙️  Backend is healthy. Generating client..."
	docker-compose -f docker-compose.dev.yaml exec frontend \
	npx openapi-typescript-codegen \
	--input http://backend:5173/openapi.json \
	--output src/client \
	--client axios

	@echo "✅ Client generated successfully"

