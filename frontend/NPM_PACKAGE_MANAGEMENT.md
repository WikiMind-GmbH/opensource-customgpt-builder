# Managing frontend npm packages

This project manages frontend dependencies from the repository root through
Docker and Make. The lockfile is committed, and Docker images install from it
with `npm ci`.

## The dependency state

Frontend dependency state exists in four places:

| Location | Meaning |
| --- | --- |
| `frontend/package.json` | The direct dependencies and version ranges the project permits |
| `frontend/package-lock.json` | The exact resolved versions, including transitive dependencies |
| Docker `frontend_node_modules` volume | The packages used by the running development container |
| Frontend Docker image | The package snapshot installed by `npm ci` when the image was built |

`package.json` is the version policy. `package-lock.json` is the reproducible
snapshot selected under that policy.

For example:

```json
"axios": "^1.8.4"
```

permits compatible Axios 1.x releases. The lockfile can still select exactly
`1.16.0`. Running `npm ci` installs that locked version. Running `npm update`
may select a newer permitted 1.x version and rewrite the lockfile.

An exact declaration permits only one version:

```json
"@hey-api/openapi-ts": "0.99.0"
```

`npm update` cannot move this dependency to `0.100.0`. Upgrade it explicitly
after reviewing its migration notes.

## Command reference

Run these commands from the repository root.

| Task | Command |
| --- | --- |
| Show current, compatible, and latest versions | `make check-frontend-deps` |
| Update within current `package.json` ranges | `make update-frontend-deps` |
| Add or explicitly upgrade a runtime package | `make add-frontend-dep PACKAGE=date-fns@4` |
| Add an exactly pinned runtime package | `make add-frontend-dep-exact PACKAGE=date-fns@4.1.0` |
| Add or explicitly upgrade a development package | `make add-frontend-dev-dep PACKAGE=vitest@3` |
| Add an exactly pinned development package | `make add-frontend-dev-dep-exact PACKAGE=@hey-api/openapi-ts@0.99.0` |
| Check known vulnerabilities | `make audit-frontend-deps` |
| Type-check and build | `make verify-frontend` |
| Rebuild the image and replace the modules volume | `make clean-restart-frontend` |

The add targets update `package.json`, `package-lock.json`, and the running
container's `node_modules` volume.

## Inspecting updates

Run:

```sh
make check-frontend-deps
```

The underlying `npm outdated` output uses these columns:

| Column | Meaning |
| --- | --- |
| `Current` | Version installed in the running container |
| `Wanted` | Newest version permitted by `package.json` |
| `Latest` | Newest version published by the package |

If `Current` differs from `Wanted`, a compatible update is available.

If `Wanted` differs from `Latest`, the latest release is outside the current
range or the dependency is pinned exactly. That update must be considered and
installed explicitly.

## Adding a runtime dependency

Without a requested version:

```sh
make add-frontend-dep PACKAGE=date-fns
```

npm normally installs the package's current `latest` version and writes a caret
range to `package.json`:

```json
"date-fns": "^4.1.0"
```

The lockfile records the exact selected version, download location, integrity
hash, and full transitive dependency tree.

To select a major version deliberately:

```sh
make add-frontend-dep PACKAGE=date-fns@4
```

To pin one exact version:

```sh
make add-frontend-dep-exact PACKAGE=date-fns@4.1.0
```

## Adding a development dependency

Development-only tools belong in `devDependencies`:

```sh
make add-frontend-dev-dep PACKAGE=vitest
```

Pin tools that can materially change generated output or build behavior:

```sh
make add-frontend-dev-dep-exact PACKAGE=@hey-api/openapi-ts@0.99.0
```

## Applying compatible updates

Run:

```sh
make update-frontend-deps
```

This runs `npm update` inside the frontend container. It updates the running
`node_modules` volume and rewrites `package-lock.json` with newer versions that
still satisfy `package.json`.

Examples:

| Declaration | Compatible update behavior |
| --- | --- |
| `"axios": "^1.8.4"` | May update to a newer 1.x release, but not 2.x |
| `"react": "~19.1.0"` | May update patch releases within 19.1.x |
| `"tool": "0.99.0"` | Remains at exactly 0.99.0 |

If all direct dependencies are exact, `npm update` may have little or no direct
dependency work to do. This restriction comes from `package.json`, not from the
exact versions recorded in the lockfile.

After updating:

```sh
make audit-frontend-deps
make verify-frontend
```

Review and commit the lockfile changes. Recreate the Docker installation before
finishing the update:

```sh
make clean-restart-frontend
```

## Upgrading to a new major version

A caret range does not cross a major version boundary. For example,
`"some-package": "^1.8.4"` cannot be updated to 2.x by `npm update`.

Use this workflow:

1. Run `make check-frontend-deps`.
2. Read the package's release notes and migration guide.
3. Install the new major explicitly.
4. Update application code for breaking changes.
5. Audit, type-check, and build.
6. Rebuild the frontend image and modules volume.
7. Commit `package.json` and `package-lock.json` together.

For a runtime dependency:

```sh
make add-frontend-dep PACKAGE=some-package@2
make audit-frontend-deps
make verify-frontend
make clean-restart-frontend
```

For an exactly pinned development tool:

```sh
make add-frontend-dev-dep-exact PACKAGE=some-tool@2.0.0
make verify-frontend
make clean-restart-frontend
```

If the package generates source code, regenerate that output after upgrading.
For the OpenAPI client generator:

```sh
make generate-client-ts-frontend
make verify-frontend
```

## `npm install` and `npm ci`

These commands serve different purposes.

`npm install` is a dependency-management command. It can add packages,
reconcile `package.json` with the lockfile, update `node_modules`, and rewrite
the lockfile when necessary.

`npm ci` is a reproduction command. It:

- Requires `package.json` and `package-lock.json` to agree.
- Installs exactly the locked dependency tree.
- Starts from a clean `node_modules` directory.
- Does not update either package file.

The Dockerfiles use `npm ci` so two builds from the same commit install the same
dependencies. Dependency changes are made deliberately with the Make targets,
not during image construction.

## The Docker modules volume

Development Compose mounts a named volume at `/app/node_modules`. This keeps
container packages separate from host packages, but the volume can outlive an
image rebuild and become stale.

`make update-frontend-deps` and the add targets update the running volume
immediately. The Docker image remains unchanged until it is rebuilt.

Use:

```sh
make clean-restart-frontend
```

after committing a dependency change, after pulling dependency changes from
another branch, or whenever the image, lockfile, and volume appear to disagree.
This target removes the old frontend container and modules volume, rebuilds the
image with `npm ci`, and starts a fresh frontend container.

## Optional host installation for VS Code

The application runs in Docker. If the host editor needs a local `node_modules`
directory for IntelliSense, install the exact lockfile locally:

```sh
cd frontend
npm ci
```

The host installation is separate from the Docker named volume and is ignored
by Git. Do not use the host installation as proof that the container is current.

## Security updates

Inspect vulnerabilities with:

```sh
make audit-frontend-deps
```

If npm reports a compatible fix, run `npm audit fix` explicitly in the running
container, then verify the result:

```sh
docker compose -p opensource-customgpt-builder \
  -f docker-compose.dev.yaml \
  exec frontend npm audit fix

make verify-frontend
make clean-restart-frontend
```

Do not use `npm audit fix --force` as routine maintenance. It may cross major
version boundaries and introduce breaking changes.

## Do not routinely delete the lockfile

Deleting `package-lock.json` discards the complete tested dependency snapshot
and asks npm to resolve every allowed dependency again. This can change many
unrelated transitive packages at once.

Regenerate the lockfile only when it is genuinely corrupt, when migrating npm
or package managers, or when intentionally rebuilding the entire dependency
tree. Treat that as a broad dependency migration and review the resulting diff.

## Commit checklist

Before committing a dependency change:

1. Confirm the intended direct dependency change in `frontend/package.json`.
2. Review the `frontend/package-lock.json` diff for unexpected large changes.
3. Run `make audit-frontend-deps`.
4. Run `make verify-frontend`.
5. Regenerate generated code when its generator changed.
6. Run `make clean-restart-frontend` for a clean Docker verification.
7. Commit `package.json` and `package-lock.json` together when both changed.
