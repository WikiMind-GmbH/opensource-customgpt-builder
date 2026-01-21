# 16. Modulith

Date: 2025-11-19

## Status

Accepted

Supercedes [Microservices Architecture](0003-Microservices-architecture-test)
Supercedes [Seperating internal and external endpoints via nginx](0005-Seperating-internal-and-external-endpoints-via-nginx)

## Created by
Albert Sandritter
## Decision Maker
Albert Sandritter

## Context

This project establishes a first iteration of a software architecture and development template, including:

* Architectural style and layering
* Separation of business logic and technical concerns
* Testability and long-term maintainability
* Clear module boundaries and contracts
* A structure that allows future evolution (features, team size, deployment topology)

A central decision is the choice of architectural style that enables:

* Business-aligned modularization
* Strong decoupling between domain logic and infrastructure
* Explicit, stable interfaces between components
* A clear path towards future distribution (e.g. microservices) without starting with premature operational complexity

---

## Alternatives Considered

### 1. Unstructured Monolith

A single codebase without explicit module boundaries, contracts, or dependency rules.

* **Pros:** Fast to start, low initial overhead.
* **Cons:** Strong coupling, poor testability, unclear ownership, difficult evolution, high long-term maintenance cost.

### 2. Microservices

Independent deployable services, typically combined with DDD and hexagonal architecture.

* **Pros:** Independent scaling, deployment, and technology choices.
* **Cons:** High operational overhead (network, orchestration, observability, distributed failure modes), unjustified for the current team and system size.

### 3. Modulith with DDD and Hexagonal Architecture (Chosen)

A single deployable system structured as a set of strongly isolated modules with explicit contracts and dependency rules.

* Uses DDD for domain modeling and bounded contexts.
* Uses hexagonal architecture (ports & adapters) for dependency inversion.
* Preserves clear boundaries while avoiding premature distributed-system complexity.

---

## Decision

We implement the system as a **modulith** (modular monolith) structured using:

* **Domain-Driven Design (DDD)** for:

  * Business-aligned decomposition
  * Bounded contexts and ubiquitous language
  * Separation of application logic and domain model
* **Hexagonal Architecture (Ports & Adapters)** for:

  * Dependency inversion
  * Isolation of technical concerns
  * Stable, explicit contracts between components
* **Command / Query Separation (CQRS-lite)** for:

  * Clear separation of write use cases and read models

The system is deployed as a single unit but internally structured as independently evolvable bounded contexts.

---

### Architectural Structure

#### Subdomains and Bounded Contexts

* A **subdomain** is a business capability.
* A **bounded context** is a boundary within which a domain model and language are consistent.

In this first iteration:

> Each subdomain is implemented as exactly one bounded context.

Code is structured accordingly:

```
src/contexts/<context_name>/
    domain/          # domain model, business rules
    application/     # use cases, orchestration, ports
    infrastructure/  # technical adapters, cross-context adapters (first iteration)
```

Each bounded context contains:

* **Domain layer:** entities, value objects, domain services
  (aggregate boundaries and domain events may be introduced later as the model evolves)
* **Application layer:** use cases (application services), orchestration, ports
* **Infrastructure layer:** adapters for persistence, external systems, LLMs, vector stores, etc., including adapters currently consumed by other contexts

This one-to-one mapping between subdomains and bounded contexts may evolve as the domain grows.

---

### Ports, Adapters, and Ownership

#### Current State (First Iteration)

* Ports are defined by the **consuming context**.
* Adapters implementing these ports may live in the **providing context’s infrastructure**.
* Cross-context communication uses:

  * Explicit ports
  * DTOs
  * Mapping at the boundary

This enforces dependency inversion and prevents direct model sharing.

#### Target State (Planned Evolution)

We plan to evolve toward a stricter bounded-context integration model:

* **Provider-owned APIs/ports**
  Each context defines what it offers in its own language and DTOs.
* **Consumer-owned ports**
  Each consuming context defines what it needs.
* **Anti-Corruption Layer (ACL) adapters** in the consumer context:

  * Call provider APIs
  * Translate provider DTOs into consumer DTOs
  * Prevent model and language leakage

This supports:

* Multiple consumers with different needs
* Independent evolution of provider and consumer models
* Clean bounded-context autonomy
* Easier extraction into microservices later

The current “provider implements consumer port” approach is accepted as a transitional state.

---

### Command / Query Separation

A lightweight CQRS style is applied:

#### Commands / Use Cases

* Implemented in application services.
* Operate on domain models via UoW and repositories.
* Enforce business rules through domain methods.
* Transaction semantics are controlled by the application layer.

#### Queries

* Implemented via dedicated query adapters.
* Return DTO projections, not domain entities.
* Are optimized independently from write paths.

---

### Rationale

* **DDD** provides:

  * Business-aligned decomposition
  * Explicit domain models and ownership
  * Clear bounded contexts
* **Hexagonal Architecture** provides:

  * Dependency inversion
  * Isolation of infrastructure
  * Stable ports and adapters
* **Modulith packaging** provides:

  * Low operational overhead
  * Fast local development and testing
  * A clear evolutionary path toward microservices
* **Explicit contracts (ports + DTOs)**:

  * Enable testability and clarity
  * Mimic microservice boundary strictness without network cost
* **CQRS separation**:

  * Avoids read/write model coupling
  * Improves maintainability and performance tuning

---

## Consequences

### Benefits

* Clear bounded-context isolation within a single deployable.
* Strong separation of domain, application, and infrastructure concerns.
* High testability at all levels (domain, use case, adapter, integration, performance).
* Stable contracts enabling future service extraction.
* Explicit command/query separation.

### Limitations and Technical Debt

#### 1. Deployment and Scaling

* All contexts are deployed together.
* Independent scaling and release are not yet possible.

#### 2. Port Ownership and Cross-Context Integration

* Some adapters currently live in provider contexts and implement consumer-owned ports.
* Planned evolution: provider APIs + consumer-side ACL adapters.

#### 3. Boundary Enforcement

* Context isolation is currently enforced by structure and convention, not yet by tooling (import rules, static boundary checks).

#### 4. Domain Invariants and Validation

Currently, many business rules and invariants are enforced at the system boundary via Pydantic DTO validation. This means part of the domain’s correctness logic resides in the transport layer instead of the domain model.

This is accepted for the first iteration but considered architectural debt because:

* The domain is not yet the single source of truth for invariants.
* Internal code paths could bypass business rules.
* Validation logic risks duplication and drift.

**Target approach:**

* **Domain layer**

  * Enforce all true business invariants in constructors and state-changing methods.
  * Raise explicit domain validation errors (e.g. `DomainValidationError(field, message)`).

* **DTO layer**

  * Keep validation minimal and defensive (type, presence, basic shape).

* **Application / Interface layer**

  * Translate domain validation errors at the boundary (e.g. FastAPI exception handlers) into appropriate HTTP responses (e.g. 422 with field-level error information).

This makes the domain model the authoritative source of business correctness while preserving good API error reporting.

#### 5. Aggregate Modeling

Aggregate boundaries are not yet explicitly modeled. As domain complexity grows, aggregates and their invariants will be introduced to define transactional consistency boundaries more formally.