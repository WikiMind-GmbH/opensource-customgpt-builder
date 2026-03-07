# Seperating internal and external endpoints via nginx

Date: 2025-08-04

## Status

Superceded by [16. Modulith](0016-modulith.md)

## Context
For every Service with a rest api, we want some endpoints to only be accessible to other services in the docker network and not to the outside. This is due to the fact that these endpoints are part of system internal logic and are expected to only be called with specific data in specific circumstances by other services. 

## Decision
The simplest solution is to a fastapi router with a prefix that is not forwarded by our reverse proxy.
```
public = APIRouter(prefix="/api")
internal = APIRouter(prefix="/internal")
```

```
# Public API only
    location /api/ {
        proxy_pass http://fastapi:8000;
        include proxy_params.conf;
    }

    # Just in case someone guesses the path: deny
    location /internal/ { return 403; }
    location / { return 404; }
```


## Consequences

Fastapi config must be changed to where it sees and can read the prefix that nginx gave it.

Extra care is taken when writing endpoints that are meant for system internal consumption only! The nginx config must not contain a reverse proxy to those endpoints.   
Endpoints only meant for internal consumption must use the `internal` route prefix.   
If endpoints are for external as well as internal consumption: Use a non-internal prefix.

In the future: extra authentication must be added for safety.