# 21. Branching, release promotion, and quality gates

Date: 2025-11-21
Status: Accepted

## Context
◊
We need a simple, reliable way to run multiple tracks of development:

* **Feature/Dev** for fast iteration.
* **Staging** for testing release candidates in a prod-like environment.
* **Prod** as the stable version deployed for customers.

To keep quality high without slowing iteration, we establish **explicit promotion gates** between these branches and define how multi-branch features advance without breaking `dev`.

We’ll start with a minimal, enforceable process and iterate.

## Decision

Adopt a **three-stream** branching model with **explicit promotion** and quality gates.

### Branches

* Long-lived: `dev`, `staging`, `prod`
* Short-lived: `feature/*`, `bugfix/*`, `hotfix/*`

### Promotion flow

```
feature/*  →  dev  →  staging  →  prod
         (merge)  (merge)  (merge)
```


* `dev` = integration of day-to-day work.
* `staging` = release candidate tested in a prod-like environment.
* `prod` = version deployed (or ready to deploy) for customers.

Code must flow and transition in this way. It is not possible to go from feature straight to staging for example

---

## Quality gates

### 1) Feature → Dev (integration-ready, with tests)

**Must have (ALL):**
All previous tests pass, additionally
* **Unit tests** for new/changed domain logic and **service functions** are created and pass on the dev machine
* **Contract/adapter tests** for any new adapter (port compliance + error translation) are created and pass on the dev machine.
* **DTO Mapper tests* for new or changed DTOs are created and pass on the dev machine.
* For each **new service function**,tests are created and pass on the dev machine
* **Docs updated** where applicable:
  * ADR created if the change impacts architecture decisions.

### 2) Dev → Staging (release candidate)

**Must have (ALL):**

* For any **major feature / new use case**, add at least one new backend E2E test.
* If new features/use cases are implemented, performance tests must be written in locust
* **Docs updated** where applicable:
  * ADR created if the change impacts architecture decisions.

### 3) Staging → Prod (release)

**Must have (ALL):**
* Code review from a person outside the core dev team responsible for the current changes
* Only fast-forward/merge from **`staging`** (no direct commits to `prod`).
* Deployed to a **staging environment** with **same or lower specs** than prod.
* **Performance/sanity checks** are passed in the staging environment. (utilizing makefile)
* **Human testing window** completed on staging


## Consequences

Placeholder