# Infrastructure Overview

The project is designed to run fully containerized.

All main runtime components are started through Docker Compose, so local development and deployment-like environments use the same basic infrastructure shape.

## Main Components

The stack consists of:

```text
backend
frontend
postgres
nginx
structurizr-lite
````

## Backend

The backend runs in its own container.

It is built from the backend Dockerfile and receives configuration through environment variables from the `.env` file.

In development, the backend source code is mounted into the container, so code changes can be picked up without rebuilding the image every time.

The backend exposes a health check based on the generated OpenAPI endpoint.

## Frontend

The frontend also runs in its own container.

It is built separately from the backend and uses a mounted source directory for development.

`node_modules` are stored in a Docker volume so the container dependency state is separated from the host filesystem.

## Database

PostgreSQL runs as its own container.

Database state is stored in a Docker volume, so it can survive container restarts.

In development, the database port is exposed only on localhost.

## Nginx

Nginx is the main HTTPS entry point.

It sits in front of the frontend and backend and routes incoming traffic to the appropriate service.

TLS certificates are mounted into the nginx container.

## Structurizr Lite

Structurizr Lite runs as a separate development-only architecture documentation service.

It is exposed directly on port `8080`.

This is intentional because Structurizr Lite expects to run as a root application and does not work well behind a rewritten reverse-proxy path.

## Networks and Volumes

Docker networks are used to connect containers internally.

A separate shared network exists for Locust/performance testing integration.

Docker volumes are used for persistent or container-owned data such as:

```text
PostgreSQL data
frontend node_modules
generated or mounted runtime data
```

## High-Level Mental Model

```text
Browser
  -> nginx over HTTPS
  -> frontend / backend containers
  -> backend talks to postgres
```

Development architecture tools and performance tooling run alongside the main stack but remain separate from the application core.

