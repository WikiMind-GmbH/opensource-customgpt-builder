# Frontend (React)

The frontend consumes the backend via a generated TypeScript client derived from FastAPI’s OpenAPI spec.

---

## Run

From repo root:

```sh
make up
```

For debugging with vscode, use the `React debugger` launch configuration from the debugger drop down menu.

---
## Prerequisites for local dev
- All prerequisites detailed in the root folder README
- to enable Intellisense usage in vscode, install the node libraries locally by typing into console `npm i`. (Requires [this](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm))

## Installing / updating npm dependencies

### Important: `node_modules` is a named volume

The dev compose uses a named volume for `node_modules`. This is needed to decouple to node_modules installed in the container from those on our local machnine.
But it can also cause stale dependency state after changing `package.json`.

If you changed dependencies and things look wrong, or dependencies are outdated, do:

```sh
make clean-restart-frontend
```

### Installing new npm libraries
The npm libraries present in package.json will automatically be installed by the dockerfile.

If you want to add new ones, you can connect to the docker container and then run `npm i ${some_package}` from there. This will update the package.json and still keep everything docker first. 

To do this:

Make sure that the container is up and running.

Then, open a shell inside the running frontend container:

```sh
docker-compose -f docker-compose.dev.yaml exec frontend /bin/sh
```

This gives you access to the container environment where you can safely run npm commands (e.g. `npm install some-package`).

---

## Generated API client (required workflow)

When backend endpoints change, regenerate the client:

```sh
make generate-client-ts-frontend
```

This:

1. starts the dev stack (if needed)
2. waits until the backend container is healthy
3. generates the TypeScript client from the OpenAPI spec

### Base URL

The generated client must point to the correct backend base path.

As of now, we need to manually set the baseurl of the backend in the automatically generated frontend client.

In `frontend/src/client/core/OpenAPI.ts` set the `BASE`:
```py
export const OpenAPI: OpenAPIConfig = {
    BASE: 'http://localhost/api', #<-- set this value (use the value of env.BASE_URL + '/api')
    VERSION: '0.1.0',
    WITH_CREDENTIALS: false,
    CREDENTIALS: 'include',
    TOKEN: undefined,
    USERNAME: undefined,
    PASSWORD: undefined,
    HEADERS: undefined,
    ENCODE_PATH: undefined,
};
```

---

## Calling backend endpoints

Generated services live under:

* `src/client/services/*`
* Types live under:

  * `src/client/models/*`

Use the generated types in the UI code to keep request/response shapes aligned with the backend.