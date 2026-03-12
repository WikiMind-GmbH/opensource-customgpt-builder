# =============================================================================
# Makefile conventions (READ ME)
#
# - This Makefile is the primary developer interface: prefer `make <target>` over
#   long docker/pytest/ruff commands.
#
# - Document targets inline using `##` on the *same line*:
#     up: ## Start dev stack (detached)
#
# - Group targets using section headers that start with `## ` (note the space):
#     ## ----------------------DEV STACK----------------------
#
# - The `help` target parses these conventions:
#   - Lines matching `<target>: ... ## <description>` are listed as commands.
#   - Lines starting with `## ` are printed as bold section headings.
#
# - Tip: keep target names verb-first and consistent:
#   - `test-*` for pytest suites, `locust-*` for load tests, `clean-*` for resets.
# =============================================================================

PROJECT_NAME = opensource-customgpt-builder
PG_VOLUME = $(PROJECT_NAME)_pgdata
FRONTEND_VOLUME = $(PROJECT_NAME)_frontend_node_modules

COMPOSE_DEV = docker compose -p $(PROJECT_NAME) -f docker-compose.dev.yaml
COMPOSE_PROD = docker compose -p $(PROJECT_NAME) -f docker-compose.prod.yaml
COMPOSE_LOCUST_LOCAL := docker compose -f backend/tests/tests_perf_locust/docker-compose.locust-perf-local.yaml
COMPOSE_LOCUST_STAGING := docker compose -f backend/tests/tests_perf_locust/docker-compose.locust-perf-staging.yaml
PYTEST_FLAGS := -q -s --maxfail=1 -m 'not performance'
PYTEST_FLAGS_PERFORMANCE := -q -s --maxfail=1 -m performance



.PHONY: generate-client-ts-frontend test test-unit test-integration test-unit-exec test-integration-exec test-clean up down restart logs ps rebuild clean-restart-db

## ----------------------DOCKER----------------------

up: ## Start dev stack (fast). Use after pulling latest or normal day-to-day work.
	$(COMPOSE_DEV) up -d

up-build: ## Start dev stack + rebuild if Dockerfile/requirements changed (cached rebuild).
	$(COMPOSE_DEV) up -d --build

define rebuild
	$1 build --no-cache
	$1 up -d
endef

up-rebuild: ## in dev: Clean rebuild (no cache) + start. Use if build cache seems stale or deps won't update.
	$(call(rebuild, $(COMPOSE_DEV)))

up-rebuild-prod: ## in prod: Clean rebuild (no cache) + start. Use if build cache seems stale or deps won't update.
	$(call(rebuild, $(COMPOSE_PROD)))

down: ## Stop stack and remove containers/network. Volumes remain unless explicitly removed.
	$(COMPOSE_DEV) down

down-prod:

restart: ## Recreate containers (no rebuild). Use after .env/compose changes or to reset a weird runtime state.
	$(COMPOSE_DEV) down
	$(COMPOSE_DEV) up -d

restart-build: ## Recreate containers + rebuild if needed. Use after Dockerfile/requirements changes + you want a clean restart.
	$(COMPOSE_DEV) down
	$(COMPOSE_DEV) up -d --build

restart-rebuild: ## Recreate containers + clean rebuild. Use for "it still uses old deps" or suspected cache issues.
	$(COMPOSE_DEV) down
	$(COMPOSE_DEV) build --no-cache
	$(COMPOSE_DEV) up -d

logs: ## Follow logs for the whole dev stack (ctrl+c to stop following).
	$(COMPOSE_DEV) logs -f

ps: ## Show container status for the dev stack.
	$(COMPOSE_DEV) ps


define clean_restart_frontend
	$1 stop frontend
	$1 rm -f frontend
	-docker volume rm $2
	$1 build --no-cache frontend
	$1 up -d frontend
endef

clean-restart-frontend: ## clean restart frontend in dev
	$(call clean_restart_frontend,$(COMPOSE_DEV),$(FRONTEND_VOLUME))

clean-restart-frontend-prod: ## clean restart frontend in prod
	$(call clean_restart_frontend,$(COMPOSE_PROD),$(FRONTEND_VOLUME))


define clean_restart_db
	$1 stop postgres
	$1 rm -f postgres
	docker volume rm $(PG_VOLUME) || true
	$1 build --no-cache postgres
	$1 up -d postgres
endef

clean-restart-db: ## clean restart the db in dev, helpful if init has changed while we do not use migrations
	$(call clean_restart_db, $(COMPOSE_DEV))

clean-restart-db: ## clean restart the db in prod, helpful if init has changed while we do not use migrations
	$(call clean_restart_db, $(COMPOSE_PROD))

## ----------------------PYTEST FUNCTIONAL MAIN TESTS----------------------

test-external-api-adapters: ## Testing adapters that utilize external apis- might cost money, thus its outside the tests/test folder
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/test_external_api_adapters"

test-use-cases: ## run the light e2e tests (directly using the Fastapi TestApp)
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) -s tests/test_rest_api_use_cases"

tests: ## run all the remaining functional tests not covered by test-use-cases or test-external-api-adapters
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/tests"

test-show-setup: ## same as tests target, but with additional infos printed
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) --setup-show -s tests/tests"
## ----------------------PYTEST FUNCTIONAL subset of `test-show-setup`-----
test-unit: ## Run only unit tests
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/tests/unit"
test-contracts: ## Run only contract tests
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/tests/contracts"
test-integration: ## Run only integration tests
	$(COMPOSE_DEV) up -d postgres
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS) tests/tests/integration"



# ## (Optional) Run tests in an already-running backend container
# test-unit-exec:
# 	$(COMPOSE_DEV) exec backend pytest $(PYTEST_FLAGS) tests/tests/unit

# test-integration-exec:
# 	$(COMPOSE_DEV) exec backend pytest $(PYTEST_FLAGS) tests/tests/integration


test-clean: ## Clean up any stopped test containers
	$(COMPOSE_DEV) rm -f
## ------------------------------------------------------------------------


## ----------------------PYTEST PERFORMANCE----------------------

test-use-cases-perf: ## run all pytest-performance tests in the test_rest_api_use_cases folder
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) -s tests/test_rest_api_use_cases"

test-integration-perf: ## run all pytest-performance tests in the integratioin folder
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) tests/tests/integration"

test-perf: # combines the targets `test-use-cases-perf` `test-integration-perf`
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) tests/tests"
	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE) -s tests/test_rest_api_use_cases"
# 	$(COMPOSE_DEV) run --rm backend sh -c "pytest $(PYTEST_FLAGS_PERFORMANCE)" tests
# #replace the automatically generated base/url of the backend api 
# #with the one defined as environment variable (if not already done)
# fix-openapi-base:
# 	docker-compose -f docker-compose.dev.yaml exec frontend \
# 	sh -c 'grep -q "import.meta.env.VITE_APP_DOMAIN" src/client/core/OpenAPI.ts || sed -i '\''s|BASE: .*|BASE: import.meta.env.VITE_APP_DOMAIN + "/api",|'\'' src/client/core/OpenAPI.ts'
# NOT YET WORKING

## ----------------------LOCUST PERFORMANCE----------------------
locust-staging: ## run locust against the staging environment, save results html
	$(COMPOSE_LOCUST_STAGING) run --rm locust sh -c "locust -f locustfile.py --html 'results/locust_results_$$(date +%Y%m%d_%H%M%S).html'"
locust-local: ## run locust against the local environment, save results html
	$(COMPOSE_DEV) up -d
	$(COMPOSE_LOCUST_LOCAL) up -d locust
	$(COMPOSE_LOCUST_LOCAL) exec locust sh -c "locust -f locustfile.py --html 'results/locust_results_$$(date +%Y%m%d_%H%M%S).html'"
locust-local-debugging: ## run locust for debugging - no results html is generated
	$(COMPOSE_DEV) up -d
	$(COMPOSE_LOCUST_LOCAL) up -d locust
	$(COMPOSE_LOCUST_LOCAL) exec locust sh -c "locust -f locustfile.py"

## ----------------------LINTING, TYPECHECKING AND CO----------------------
ruff: ## run ruff, incl. formatting
	ruff check backend
	ruff format backend
ruff-fix-save: ## run ruff, incl. formatting and auto-apply fixes where save
	ruff check backend --fix
	ruff format backend


## ----------------------GENERATING FRONTEND CLIENT----------------------
generate-client-ts-frontend: ## creates the typescript client based on the openaipi provided by the backend
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



## ----------------------OTHER----------------------
help: ## Show available make targets
	@echo ""
	@echo "Available targets:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} \
		/^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2} \
		/^## / {printf "\n\033[1m%s\033[0m\n", substr($$0, 4)}' $(MAKEFILE_LIST)
	@echo ""