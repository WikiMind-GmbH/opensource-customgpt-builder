# Backend (FastAPI)

This backend is Docker-first and designed around:
- strong testing
- strict typing (Pylance/Pyright)
- stric linting and formatting compliance utilizing ruff
- architecture rules captured in ADRs (ports/adapters, modulith boundaries, DTO/mappers, etc.)

> This README describes **how to work** with this backend.
> The guidelines on writing and commiting code + the **why** (trade-offs & rationale) are documented in ADRs. Please read them.

>For an onboarding overview of the architecture, check out 
[backend architecture overview onboarding](backend_architecture_overview_onboarding.md)

---
## Prerequisites for local dev
- All prerequisites detailed in the root folder README
- To enable Intellisense usage in vscode, install pip libraries of `requirements.txt` and `requirements-dev.txt` via pip. Creating a [virtual environment](https://code.visualstudio.com/docs/python/python-tutorial#_create-a-virtual-environment) is recommended.

## Run

From repo root: 

```sh
make up
```

Backend runs as part of the dev compose stack. Logs:
 
```sh
make logs
```

API documentation (Swagger UI):

* [https://localhost:api/docs](https://localhost/api/docs)

ADRS

* [http://localhost:8080/workspace/decisions/Opensource%20CustomGPT%20builder](http://localhost:8080/workspace/decisions/Opensource%20CustomGPT%20builder)

SWA

* [http://localhost:8080/](http://localhost:8080/)

---

## Type checking & linting (required)

### VSCode config is part of the contract

This repo commits `.vscode/settings.json` and expects developers to use it.

* Python typechecking uses **Pylance/Pyright**.
* Do not relax strictness casually. If you need an exception, follow the documented typing guideline rationale in ADRs.

### Ruff
On saving, ruff runs the formatter and fixes all automatically fixable lint violations.

To run ruffmanually:
```sh
make ruff-fix-save
```

---

## Testing philosophy

We rely heavily on tests. If you change behavior, you are expected to update or add tests. Also, run the tests periodically to make sure that nothing broke.

### Test groups & commands

#### **All functional tests (excluding performance-marked tests):**
Run omponent (service/unit/contract/integration) and e2e tests utilizing a Fastapi test client with
```sh
make tests
make test-use-cases
```
Test external api adapters only when having changed them to save money
```sh
make test-external-api-adapters
```

#### Run only a subset of the tests selected by `make tests`:

**Unit tests only:**

```sh
make test-unit
```

**Integration tests only:**

```sh
make test-integration
```

**Contract tests only:**

```sh
make test-contracts
```

### Performance tests
For simplicity, we mostly rely on locust performance tests for now. You can run them against your local dev environment via
```sh
make locust-local
```
and against the staging env via

```sh
make locust-staging
```

A html page with the results is created and accesible in `backend/tests/tests_perf_locust/result`. Drag it into the browser to view it.

Pytest performance tests are explicitly marked and run seperately. To run them, use the following target:

```sh
make test-perf
```

> Keep performance tests stable, deterministic, and scoped to measurable goals.

---

## Architecture rules (quick pointers)

This backend follows architecture rules documented as ADRs and in Structurizr Lite:

* modulith structure and boundaries
* ports & adapters
* cross-context communication via DTOs and mapping (no domain model leakage)
* error handling conventions, factories vs singletons, etc.

Start here:

* Structurizr docs: `structurizr/README.md`
* ADRs: see the `adrs/` folder (rendered in Structurizr Lite) -view them, after `make up` on http://localhost:8080