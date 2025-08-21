## Risks & Technical Debt

### Central Logging service
A central logging service must be used in the future.
All services will send their logs to this service with a timestamp, logging level *as well as an operationID/requestID*. In this way, we can trace the logs of one operation across multiple services, even if there were multiple parallel requests. (I.e. multiple users in parallel upload documents (on multiple instances). One experiences an error. We can't just from timestamp or instance see which logs of the different services belong to this one request if wew do not have a request or operationID for tracing)

### Internal network traffic -> safety and logging
See: the following chatgpt snippet

### Document uploading

As of now, the C4 model only shows how to upload one document.  
This must be changed to allow multiple document uploads (?) -> parallelization easily done.  


#### Why direct service→service HTTP is OK

* **Fewer hops/latency:** you’re not hair-pinning through Nginx.
* **Simplicity:** no extra Nginx routes/ACLs to maintain for internal traffic.
* **Docker DNS works out of the box:** each container can call others by service name, e.g. `http://usersvc:8000/internal/...`.

#### When you might *not* want to bypass Nginx

* You need **authn/authz, mTLS, rate limiting, request shaping, or WAF** on *internal* calls.
* You want **single place for access logs/metrics** (observability).
* You run **multiple replicas** of a target service and want **load balancing** without adding a client-side LB.

(If those matter later, you can still keep Option 1 for public traffic and add a second, **internal-only** Nginx listener/port just for east–west traffic.)

---

#### Minimal, robust setup for direct internal calls

#### 1) FastAPI route grouping + internal guard (defense-in-depth)

Even if `/internal/*` isn’t proxied publicly, protect it in-app.

```python
# fastapi_app.py
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status

app = FastAPI()
public = APIRouter(prefix="/api")
internal = APIRouter(prefix="/internal")

def require_internal(request: Request):
    # simplest: shared secret header set by callers inside the network
    if request.headers.get("x-internal-token") != "supersecret":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@public.get("/health")
def health(): return {"ok": True}

@internal.post("/reindex")
def reindex(_=Depends(require_internal)):
    return {"started": True}

app.include_router(public)
app.include_router(internal)
```

> If you prefer stronger auth, swap the header for **JWT** verification or **mTLS** (terminate TLS in the app).

#### 2) Nginx: expose only public paths

```nginx
server {
  listen 443 ssl;
  server_name your.public.host;

  # Public API only
  location /api/ {
    proxy_pass http://fastapi:8000;
    include proxy_params.conf;
  }

  # Belt-and-suspenders: block internal paths at the edge
  location /internal/ { return 403; }
  location / { return 404; }
}
```

#### 3) Docker networking basics

* In `docker-compose.yml`, **don’t publish** the FastAPI port to the host; only `expose` it.
* Other services call it via service DNS (e.g., `fastapi:8000`).

```yaml
services:
  api:
    build: .
    expose: ["8000"]
    networks: [appnet]
  nginx:
    image: nginx:alpine
    ports: ["443:443"]    # only public
    depends_on: [api]
    networks: [appnet]

networks:
  appnet: { driver: bridge }
```

### 4) Client code for internal calls (timeouts + retries)

Use `httpx` and be strict about timeouts/retries to avoid cascading failures.

```python
import httpx
import asyncio
from typing import Callable

INTERNAL_HEADERS = {"x-internal-token": "supersecret"}

def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(connect=1.0, read=1.5, write=1.0, pool=5.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        headers=INTERNAL_HEADERS,
    )

async def call_internal(client: httpx.AsyncClient, url: str, json: dict):
    # simple bounded retry with jitter
    for attempt in range(3):
        try:
            r = await client.post(url, json=json)
            r.raise_for_status()
            return r.json()
        except (httpx.ConnectError, httpx.ReadTimeout):
            await asyncio.sleep(0.05 * (attempt + 1))
    raise RuntimeError(f"internal call failed: {url}")
```

Add **circuit breakers** (e.g., `aiobreaker`) if the downstream can flap.

---

#### Trade-offs and tips

* **Load balancing / scaling:** direct calls hit one container. If you scale a target service to N replicas, Docker’s DNS gives round-robin IPs, but it’s not a full LB. If you need smarter balancing, either:

  * run an **internal Nginx/Envoy** (not exposed to host) and point clients to `http://nginx-internal:PORT`, or
  * use a **service mesh** (Envoy sidecars, linkerd) later.
* **Observability:** add request IDs (`X-Request-Id`) and propagate them across services; log internal vs public separately.
* **Zero trust mindset:** network boundaries are not security. Keep the app-level guard, and prefer JWT/mTLS if risk increases.
* **Fail-closed at the edge:** the Nginx “deny `/internal`” block prevents accidental exposure by config drift.

---

#### Bottom line

Your plan (Option 1 + direct internal HTTP) is **perfectly reasonable** for a single Docker network setup. Keep internal routes unproxied publicly, add a lightweight app-level check, and be disciplined about client timeouts/retries. If you later need richer auth, load balancing, or centralized observability for east–west traffic, you can introduce an **internal** Nginx/Envoy without changing public behavior.
