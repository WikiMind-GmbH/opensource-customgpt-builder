# opensource-customgpt-builder

Docker-first development setup for a full-stack app (FastAPI backend + React frontend) with supporting services (Postgres, Nginx, Structurizr Lite).

> This README is intentionally **operational**: how to run, test, lint, and troubleshoot.
> Architecture and decisions (incl. guidelines) live in **Structurizr Lite + ADRs**.


---

## Prerequisites

* Docker + Docker Compose
* `make`

### Windows note

Use **Git Bash** (not PowerShell/cmd). Then install make via Chocolatey:

```sh
choco install make
```

### HTTPS for local development

Local HTTPS uses **mkcert**. See `nginx/README.md`.

### VSCode & Ruff

This repo ships `.vscode/settings.json` + `.vscode/launch.json`    
as well as `pyproject.toml`

* Use them (don’t fight them) — they contain **type checker configuration** and **debug presets**    
as well as **ruff configuration** and **pytest configuration**
* Python type checking is expected via **Pylance/Pyright** (see backend README for details).
* Linting and formatting is expected via **Ruff** (see backend README for details).

---

## Quickstart (Development)

All commands are expected to run **from the repo root**.

```sh
make up
````

Then open:

* Frontend: [https://localhost](https://localhost)
* Backend API docs (Swagger): [https://localhost/api/docs](https://localhost/api/docs)
* Structurizr Lite: [http://localhost:8080](http://localhost:8080)

Useful commands:

```sh
make logs
make down
make ps
```



## Daily workflow
Run `make help` to see:
- **all available targets**.
- **more information on each target**

### Start / stop

```sh
make up
make down
make restart
```

### Generate the frontend API client (after backend endpoint changes)

```sh
make generate-client-prod
```

### Lint + format (backend)

```sh
make ruff
make ruff-fix-save
```

### Tests (functional, non-performance)

```sh
make tests
make test-use-cases
make test-external-api-adapters
```

### Performance tests

```sh
make test-perf
make locust-local
make locust-staging
```



---

## Architecture & quality rules (must-read)

* **Architecture docs + ADRs** are best viewed via Structurizr Lite → see `structurizr/README.md`.
* Backend architecture follows a modulith with ports/adapters; cross-context data must use DTOs/mappers (see ADRs).
* Quality gates (linting/typechecking/testing) are part of the engineering contract.

---

## Troubleshooting

### Frontend dependencies seem stale / weird after changing `package.json`

The frontend uses a named volume for `node_modules`. Sometimes old dependencies remain.

```sh
make clean-restart-frontend
```

### Reset Postgres data

```sh
make clean-restart-db
```