# Structurizr lite as http (no s!) root app

Date: 2025-08-04

## Status

ACCEPTED    

## Context
Structurizr does not work behind a reverse-proxy as stated on their webpage.
>>Structurizr Lite is designed to work as the root application (i.e. via a context path of /) **and will not work if deployed to a different path or used behind a reverse-proxy** with a rewrite rule. The UI is shared between Structurizr Lite, the on-premises installation, and the cloud service so we have no plans to change this.

We do use a reverse proxy for everything else. Will not be able to use it here.
## Decision
Frontend and backend behind nginx with https. We do not listen for port 8080 in nginx. This way, we can diretly reach structurizr-lite on http://localhost:8080

We use structurizr only in the dev environment for now.
## Consequences

Port 8080 is reserved and used for the structurizr-lite with no ssl in the dev environment.