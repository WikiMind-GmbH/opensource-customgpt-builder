# opensource-customgpt-builder

Docker-first development setup for a full-stack app (FastAPI backend + React frontend) with supporting services (Postgres, Nginx, Structurizr Lite).

> This README is intentionally **operational**: how to run, test, lint, and troubleshoot.

> It does not cover Architecture and decisions (incl. guidelines). They live in **Structurizr Lite + ADRs**. You can read the adrs in [structurizr/adrs](structurizr/adrs) or on http://localhost:8080 after starting the project. For more on SWA see [structurizr/README.md](structurizr/README.md)

> Here is an onboarding overview of the architecture: [backend architecture overview onboarding](backend/backend_architecture_overview_onboarding.md)


---

## Prerequisites
Here are all the prerequisites you need to run the project.
### Set up environment

The project uses a single `.env` file for environment variables. Copy the `.env.example`, paste it in the same folder, rename the copy to `.env` and fill in all values that are not defaults.

### Install Docker
* [Docker](https://www.docker.com/get-started) + [Docker Compose](https://docs.docker.com/compose/)

### Install/ use Make
* `make` is preinstalled on macOS

#### Install make on Windows

Use **Git Bash** (not PowerShell/cmd). Then install make via Chocolatey:

```sh
choco install make
```

### Set up HTTPS for local development

Local HTTPS uses **mkcert**. See [nginx/README.md](nginx/README.md) for how to set it up.

### Use VSCode & Ruff

This repo ships `.vscode/settings.json` + `.vscode/launch.json`    
as well as `pyproject.toml`

* Use them (don’t fight them) — they contain **type checker configuration** and **debug presets**    
as well as **ruff configuration** and **pytest configuration**
* Python type checking is expected via **Pylance/Pyright** (see backend README for details).
* Linting and formatting is expected via **Ruff** (see backend README for details).

---

## Quickstart (Development)

All commands are expected to run **from the repo root**.

If you fulfill all the prerequisites listed above, you can start the project with:

```sh
make up
```

Then open:

* Frontend: [https://localhost](https://localhost)
* Backend API docs (Swagger): [https://localhost/api/docs](https://localhost/api/docs)
* Structurizr Lite: [http://localhost:8080](http://localhost:8080)





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

### Info on docker container

```sh
make logs
make ps
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