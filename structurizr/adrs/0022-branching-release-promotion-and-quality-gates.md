# 21. Branching, release promotion, and quality gates

Date: 2025-11-21  
Status: OPEN

This ADR documents a first-iteration process and is expected to be revised
after practical experience has been gained.

## Context

We have two contrasting goals:

1. **Stability**:
   The application deployed to production must remain reliable in both
   functionality and performance.

2. **Constant change**:
   We need to continuously evolve the codebase by adding new features,
   adapting existing behavior, and introducing or modifying components.

To reconcile these opposing goals, we need a branching and environment
strategy in which code changes mature from freshly created work to
well-tested, production-ready versions.


## Alternatives considered
Instead of comparing "alternative-packages", we list different sub-topics. Each sub topic must be considered if we want to include it in our solution and for each sub topic we might have to decide between explicit alternatives or how we implement it.

### Tools to check code-style quality

* Linters
* Type checkers

### Tests

* Functional tests
* Performance tests

### Promotion strategy markers

We need a promotion strategy that moves code from new feature work to
production-ready code.

This can be marked by:

* branches that correspond to maturity levels and environments, or
* naming conventions, tags, or statuses that indicate maturity.

### Quality gates

For promotion to the next maturity level (e.g. `staging → prod`), we want
explicit quality gates such as:

* code reviews
* tests to be written and passed
* linting and type checking
* performance validation

### CI/CD usage

We considered whether to rely on CI/CD tooling or to start with a
well-defined, mostly manual process.

### Performance testing approach

We plan to use:

* **pytest-benchmark** for local performance measurements
* **Locust** for request-level and concurrency testing

At this stage, it is intentionally left open:

* how extensively pytest-benchmark should be used
* whether it should focus on components or higher-level flows
* whether explicit performance thresholds should be defined

---

## Decision

To keep the process simple and enforceable in a first iteration, we align
**branch names, maturity levels, and deployment environments**.

### Branches

* Long-lived: `dev`, `staging`, `prod`
* Short-lived: `feature/*`, `bugfix/*`, `hotfix/*`

The `prod` branch is the stable, production-truth branch and acts as the
repository’s default branch (equivalent to `main` in other setups).

Code pushed to `prod` is considered production-ready and is deployed to
the production environment.

Code pushed to `staging` is deployed to the staging environment for testing. 

---

### Promotion flow

```
feature/* → dev → staging → prod
       (merge) (merge) (merge)
```

* `dev`: continuous integration of feature and bugfix work
* `staging`: release candidate tested in a prod-like environment
* `prod`: version deployed to customers

**Code must progress through these steps in order. Direct promotion
(e.g. feature → staging) is not allowed.**

The staging environment always deploys the `staging` branch, and the
production environment always deploys the `prod` branch.

---

## Quality gates

### 1) Feature → Dev (integration-ready)

**Must have (ALL):**

#### Tests

* All existing unit tests pass locally.
* For new or changed domain logic and service functions unit tests exist and pass.
* Each new service function has corresponding tests.
* Contract/adapter tests exist and pass for new adapters.
* DTO mapper tests exist and pass for new or changed DTOs.
* Typescript client from openapi.json is generated via the make target (`generate-client-ts-frontend`)

#### Documentation

* An ADR is created if architectural decisions are impacted - **check also if old adrs are to be superseded or impacted**
* Documentation is updated where applicable.
* A conscious decision is made whether additional documentation is required.

#### Linting & type checking
Always using the config files committed to the repo:
* All configured linter checks pass.
* The type checker reports no errors.

---

### 2) Dev → Staging (release candidate)

**Must have (ALL):**

* For any major new feature or new use case:

  * functional: at least one backend E2E test is added
  * performance: at least one Locust test is written
* Documentation is updated where applicable.



---

### 3) Staging → Prod (release)

**Must have (ALL):**

* Code is deployed to a staging environment with equal or lower specs than prod.
* Locust tests have been executed **against the staging environment**.
* Results of these tests must be evaluated, even if no explicit performance thresholds are defined yet.

* Code review by a developer not responsible for the changes.
* Performance and sanity checks pass on staging (using Makefile-driven tooling).
* A human testing window on staging is completed.

---

## Performance tests (OPEN)

More experience is needed to finalize a strict performance-testing policy.

What is currently understood:

1. **Locust runs against the staging environment are the authoritative
   performance signal.**
   All user stories must be exercised via Locust on staging. If results show
   unacceptable performance, promotion must stop and the issue must be addressed.
   We fix one parameter only for now: `users = 20` - the rest is still open.

2. **pytest-benchmark may be used diagnostically**, not as a primary gate.
   When high-level Locust results indicate unexpected latency or behavior,
   pytest-benchmark can be used to narrow the problem down to individual
   components or functions.

3. Locust may optionally be run against local deployments as a smoke test
   and early warning signal, but these results are non-authoritative.

Open questions to be revisited:

* How and when to introduce performance regression checks with pytest-benchmark
* How explicit performance thresholds should be defined for locust.

---

## Consequences

* Establishes a **clear and predictable promotion path** from feature
  development to production by aligning branch names, environments, and
  maturity levels.
* Keeps the initial process **simple and enforceable**, avoiding premature
  complexity such as release branches or strict performance SLAs.
* Ensures **baseline quality** through mandatory testing, linting, and type
  checking before code reaches staging or production.
* Introduces **performance awareness early** by mandating Locust tests for
  new user stories, even before explicit performance policies exist.
* Encourages a **top-down performance investigation strategy**:
  start with end-to-end behavior and introduce component benchmarks only
  when needed.

### Accepted technical debt and limitations

* Performance testing policy is intentionally incomplete:

  * no formal thresholds are defined
  * results are evaluated manually
* pytest-benchmark usage is not standardized:

  * benchmarks may vary in scope and coverage
  * no enforced regression baselines exist
* Local performance results vary by machine and are used only as relative signals.
* The process relies on **manual execution** of tests and checks due to the
  absence of CI/CD.
* Accumulation of unfinished features in `dev` may require future mitigation
  (e.g. feature flags or release branches).
* This ADR is expected to evolve once real performance data and operational
  experience are available.
