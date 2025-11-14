

COMPOSE := docker compose -f docker-compose.dev.yaml
PYTEST_FLAGS := -q -s --maxfail=1  

.PHONY: generate-client-prod test test-unit test-integration test-unit-exec test-integration-exec test-clean

## Run ALL tests (unit + integration)
test:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests"

test-show-setup:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) --setup-show -s tests"

test-use-cases:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) -s test_rest_api_use_cases"

## Run only unit tests
test-unit:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/unit"

## Run only external api tests -might cost money
test-external-api-adapters:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) test_external_api_adapters"


test-contracts:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/contracts"

## Run only integration tests
test-integration:
	$(COMPOSE) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/integration"

## (Optional) Run tests in an already-running backend container
test-unit-exec:
	$(COMPOSE) exec backend pytest $(PYTEST_FLAGS) tests/unit

test-integration-exec:
	$(COMPOSE) exec backend pytest $(PYTEST_FLAGS) tests/integration

## Clean up any stopped test containers
test-clean:
	$(COMPOSE) rm -f



# #replace the automatically generated base/url of the backend api 
# #with the one defined as environment variable (if not already done)
# fix-openapi-base:
# 	docker-compose -f docker-compose.dev.yaml exec frontend \
# 	sh -c 'grep -q "import.meta.env.VITE_APP_DOMAIN" src/client/core/OpenAPI.ts || sed -i '\''s|BASE: .*|BASE: import.meta.env.VITE_APP_DOMAIN + "/api",|'\'' src/client/core/OpenAPI.ts'
# NOT YET WORKING


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

