# Structurizr lite as http (no s!) root app

Date: 2025-08-04

## Status

ACCEPTED    

## Context

>>No, Structurizr Lite is designed to work as the root application (i.e. via a context path of /) and will not work if deployed to a different path or used behind a reverse-proxy with a rewrite rule. The UI is shared between Structurizr Lite, the on-premises installation, and the cloud service so we have no plans to change this.

## Decision
Our software system utilizes https, so we can set up nginx such that we only proxy `https://domain` and use `http://domain` for structurizr alone.



## Consequences

It is now less clear how the routing works, because we have port 443 with ssl displaying our software system and backend docs via nginx and port 8080 without ssl displaying our swa documentation.   

Nginx in dev only routes urls going to port 443 to the containers where needed and no other port.

Port 8080 is reserved and used for the structurizr-lite with no ssl.