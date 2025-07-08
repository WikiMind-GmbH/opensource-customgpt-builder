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