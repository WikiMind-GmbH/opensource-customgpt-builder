

## Docker env mechanisms — complete comparison table

| Mechanism                | Phase           | Where defined                  | Visible to app?     | Affects build (`RUN`)? | Persists in image? | Typical use                |
| ------------------------ | --------------- | ------------------------------ | ------------------- | ---------------------- | ------------------ | -------------------------- |
| `ARG`                    | build           | Dockerfile / `build.args`      | ❌ (unless exported) | ✅                      | ❌                  | Parameterize image build   |
| `ENV` (Dockerfile)       | build + runtime | Dockerfile                     | ✅                   | ✅                      | ✅                  | Defaults baked into image  |
| `environment:` (compose) | runtime         | `docker-compose.yml`           | ✅                   | ❌                      | ❌                  | Runtime config per service |
| `env_file:` (compose)    | runtime         | `docker-compose.yml` → file(s) | ✅                   | ❌                      | ❌                  | Runtime config from file   |


You’re welcome 🙂
Here’s the same table again, **now including `env_file:`**, with the distinctions made explicit.

---

## Docker env mechanisms — complete comparison table

| Mechanism                | Phase           | Where defined                  | Visible to app?     | Affects build (`RUN`)? | Persists in image? | Typical use                |
| ------------------------ | --------------- | ------------------------------ | ------------------- | ---------------------- | ------------------ | -------------------------- |
| `ARG`                    | build           | Dockerfile / `build.args`      | ❌ (unless exported) | ✅                      | ❌                  | Parameterize image build   |
| `ENV` (Dockerfile)       | build + runtime | Dockerfile                     | ✅                   | ✅                      | ✅                  | Defaults baked into image  |
| `environment:` (compose) | runtime         | `docker-compose.yml`           | ✅                   | ❌                      | ❌                  | Runtime config per service |
| `env_file:` (compose)    | runtime         | `docker-compose.yml` → file(s) | ✅                   | ❌                      | ❌                  | Runtime config from file   |


## Precedence (runtime env resolution)

At container runtime, roughly:

1. `environment:` in compose
2. `env_file:` in compose (later files override earlier)
3. Dockerfile `ENV`
4. Base image defaults

(Exact precedence between 1 and 2 is documented as `environment:` overriding `env_file:` when both define the same key.)

---

## Mental model summary (one glance)

* **Build-time only** → `ARG`
* **Baked default** → Dockerfile `ENV`
* **Runtime config (inline)** → compose `environment:`
* **Runtime config (file-based)** → compose `env_file:`

