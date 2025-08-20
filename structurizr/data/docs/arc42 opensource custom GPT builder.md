## Introduction and Goals
This document describes the Opensource CustomGPT Builder Software system. It can be used to create your own CustomGPTs outside of the OpenAI Software System. 
The goal of this system is to have a baseline product onto which we can build more customized solutions for clients. The aim is to have a product that has a use case for as many clients as possible. We hope that this makes for broader adaption and more follow-up costumized solutions then we get without having a more basic product.
The goal this system achives for the users is the following:
They want to use the capabilities of CustomGPTs without directly giving their data to OpenAI while still getting a very simimalar user experience.
(Requirements describe what the system should do. Goals describe how the system will help the organization)

This specific project also has as goal for the team to learn&utilize design and architecture patterns as well as follow SWA documentation best practices.
### Requirements Overview

1. The UI must display a history of previous chats. Previous chats can be viewed, continued and deleted
2. The user must be able to create, modify and delete CustomGPTs
3. Document upload for OpenDocument Format files and PDFs is possible
4. The information inside these documents is processed and CustomGPT will use and reference it in conversations
5. The user can see all the data that is used by a CustomGPT, including the documents uploaded.

### Quality Goals

#### Usability
- The UI must be similar to ChatGPT to enable fast adaption of new users.
The Feedback give to user input must be clear such that users know why a certain operation, like uploading unsupported document types, did not succeed.
#### Performance
*Latency*
- A user interaction must trigger a UX response in 500ms. The answer of the backend, when serving assistant messages, can be slow, though other responses shall not exceed 1s response time. Uploading documents shall lead to a fast response initial response once the documents are saved to the backend. Afterwards, the Preprocessing shall take no longer than 10 minutes before the user can use the CustomGPT
*Throughput*
- The system is not designed for high throughput, so 2 concurrent preprocessing tasks can be made in parallel with the expected latency.
#### Security
- Basic Auth and https will suffice for this POC
#### Reliability
*Concurrent Users*
- The system expects 5 concurrent users max as of now
*Data volume*
- The uploaded files are expected to not exceed 20MB and the storage for documents is expected to grow less then 10GB per year
*Load*
- The system should handle 4 preprocessing requests in parallel. the other tasks are less computationally heavy are expected to take more concurrent requests

#### Transferability
- The software system should be designed in such a way that enabling the usage of other LLM Apis is not too much work
### Stakeholders
#### Product Owner
Product owner must have a overview of the SWA to check if all features are implemented, which features can be implemented more easily and check the architecture decisions
#### Management
Management wants a quick overview of the SWA capabilities
#### Dev team
The dev team needs a place to document and reference architecture and architecture decisions

## Constraints

- The project must be completely dockarized and use or expand the current full-stack-template of wikimind.
- The code must be completely open-source

## Context and Scope
The following diagram shows 
![](embed:SystemContex)
### User
Utilizes LLM. Wants to utilize CustomGPTs without depending on Openai and having full transparency
### OpenAI Api
The Api OpenAI provides to create assistant responses from passed conversations. Tool usage is possible as well. It's CustomGPT functionality will not be used.

## Solution Strategy
### Handling RAG file upload and availability status without strong coupling 
We want to be able to upload files, directly get a feedback if those files have been uploaded, and then later receive a async http push message / websocketmessage if the processing has finished and the embeddings can be used in the chat.   
Additionally, we want to be able to have a restapi where we can directly query the curernt status and availability.

To fulfill both these features as well as still keeping our services decoupled, we went for the following solution:   
The Rag service provides an api for retreiving the status
## Buildig Block view
![](embed:SystemContex)
![](embed:ContainerView)
### ChatService
The chat service has the following apis:
```
createConversation(CustomGptId:int | None, usermessage: str, useRag:bool)
continueConversation(conversationid::int | None , usermessage: str, useRag:bool)
```
If a CustomGPTid is given, the CustomGPTservice api is called to retreive Infos about the customgpt. If the customGPTservice is not reachable, the request will be processed without the customGPT, but the answer will include this information.
Same for the RAG Service. This is due to decoupling and keeping the service running even if the other services are down.

The Rag service will return relevant chunks, but will not process them. How we tune&enrich our prompt with the retreived chunks is decided by the chatservice, not in the rag service, to keep responsibilities clear.

### RAGService
The RagService will use WebsocketMessages (/async messages)to inform other services when uploaded documents have been processed. (The initial sync Data uoload api will retrurn a success msg as soon as the files have been uploaded and will then use the WSMessage to nitify when everything has been processed)

For simplicity, documents will be identified by the following: `customgpt_id: int | None, document_name` if `customgpt_id` is None, the document is available for all chats, not just a specific customgpt.



### CustomGPTService
Database schema sketch: 
`id:int, name:str, description:str, rag_files_availability: json_str`
Where `rag_files_availability` is a dictionary where the keys are the names of the documents and the values are either `uploaded` or `processed`

Decouopling&eventual consistency: The customGPTService will have a 
## Runtime View

## Deployment View
## Architectural decisions
See [ADRs](http://localhost:8080/workspace/decisions/Opensource%20CustomGPT%20builder) 
## Quality Requirements
## Risks & Technical Debt
### Internal network traffic -> safety and logging

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
