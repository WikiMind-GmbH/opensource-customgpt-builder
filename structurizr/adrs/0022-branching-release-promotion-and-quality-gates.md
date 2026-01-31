# 21. Branching, release promotion, and quality gates

Date: 2025-11-21
Status: OPEN

## Context

We have two contrasting goals:   
1. **Stability**: We want to make sure that the app that we deploy in prod to our customer stays reliable - in functionality and in performance.      
2. **Constant change**: We need to change the code to add new features or adapt existing, adding new components, or changing existing ones. We want new versions of our software to deploy to our clients.

Therefore, we need to find a way to reach both opposing goals.

To achive this, we want to have a branching and environment strategy where code changes mature from a freshly created to well tested and evaluated as stable version.

## Alternatives considered

There are multiple things that we consider to include in our process. It is now a decision on how to combine them. 

### Tools to check code-style-quality
- Linters
- Typecheckers

### Tests
- Functional tests
- Performance tests

### Promotion strategy
We need a promotion strategy which has the following goal: Taking code from fresh feature to prod ready, tested code.   
This is now a combination of the environments and branches.
We could work with different branches that correspond to one maturity level and environment or create naming conventions for branches and using statuses or tags to mark maturity.

### Quality gates for promotion strategy
For code to be promoted to the next branch (staging -> prod) or status (release branch is promoted from `in testing` to `production tested`), we want to define quality gates - e.g. a code review, unit or performance tests to be written and passed, linters and typecheckers not throwing any errors, or similar things.

### Using CI/CD or not
We could use github actions for ci cd tasks, or just define a process and do the testing and building manually.

### How to integrate performance tests
- Due to experience with them, we want to stay with pytest benchmark and locust for now. 
However, it is unclear how we want to utilize pytest-benchmark. Only for components, also for full user-stories on a local machine, on critical components or only when e2e tests have already failed us.  
With locust, the question is: a) do we want to use it outside the staging env for local smoke tests 2) Do we want to define p95 goals that must be met?



## Decision
To keep things simple, matching environments, maturity level and branch name, we choose this first iteration approach:

We have the following branches
- **Feature/bugfix** branches for fast iteration.
- one **dev** branch for continous integration of new feature or bugfix branches
- one **Staging** branch for testing release candidates in a prod-like environment.
- one **Prod** branch as the stable version deployed for customers.

To keep quality high without slowing iteration, we establish **explicit promotion gates** between these branches and define how multi-branch features advance without breaking `dev`.

We’ll start with a minimal, enforceable process and iterate.

Adopt a **three-stream** branching model with **explicit promotion** and quality gates.

### Branches

- Long-lived: `dev`, `staging`, `prod`
- Short-lived: `feature/*`, `bugfix/*`, `hotfix/*`

Our prod branch will be our stable branch, acting as the main or master branch. 
Because we want to also use ci to build and deploy directly when pushing to this branch, we name it prod:
Code that is pushed there is ready for prod and will also be deployed to prod once pushed. It is our default branch.

### Promotion flow

```
feature/*  →  dev  →  staging  →  prod
         (merge)  (merge)  (merge)
```

- `dev` = integration of day-to-day work.
- `staging` = release candidate tested in a prod-like environment.
- `prod` = version deployed (or ready to deploy) for customers.

Code must flow and transition in this way. It is not possible to go from feature straight to staging for example

---

## Quality gates

### 1) Feature → Dev (integration-ready, with tests)

**Must have (ALL):**
#### Tests
All previous tests pass, additionally
- **Unit tests** for (new or) changed domain logic and **service functions** (are created and) pass on the dev machine
- **Contract/adapter tests** for any new adapter (port compliance + error translation) are created and pass on the dev machine.
- **DTO Mapper tests** for new or changed DTOs are created and pass on the dev machine.
- For each **new service function**,tests are created and pass on the dev machine

#### Documentation
- **Docs updated** where applicable:
  - ADR created if the change impacts architecture decisions.
  - Decision was made on whether addtional documentation should be added(e.g. for new technology)
  - If positive: Documentation was made

#### Linting & Typechecking
The reference are the typechecking and linting configurations shared in the repository.

With those configurations:
- All linter checks must have passed
- The type checker shows no problemss


### 2) Dev → Staging (release candidate)

**Must have (ALL):**

- For any **major feature / new use case**, add 1) at least one new backend E2E test. 2) One locust test
- If new features/use cases are implemented, performance tests must be written in locust
- **Docs updated** where applicable:
  - ADR created if the change impacts architecture decisions.


### 3) Staging → Prod (release)

**Must have (ALL):**

- Code review from a person outside the core dev team responsible for the current changes
- Only fast-forward/merge from **`staging`** (no direct commits to `prod`).
- Deployed to a **staging environment** with **same or lower specs** than prod.
- **Performance/sanity checks** are passed in the staging environment. (utilizing makefile)
- **Human testing window** completed on staging


## Performance tests OPEN
I need more experience to be able to judge if a specific process is a good idea. 

What i do know: 
1. we need to run locust with all user stories against staging and if we see an outlier where performance is inexcusable bad, it must be changed
2. To narrow the problem down, pytest-benchmark can be used

What is yet to be decided:
- (How) do we want to use performance regression tests with pytest-benchmark for critical components
- Is it feasible to run locust against a local instance such that we can have a smoke test and utilize it as an early warning sign, before we deploy to staging
- Do we want to use explicit tresholds, or decide on an individual basis
- 



## Consequences

Placeholder
