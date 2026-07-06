# Backend Architecture Overview (Onboarding)

This document explains **how our architecture is reflected in the folder structure** and how to navigate the codebase day-to-day.

> **Source of truth:** Architecture rules and decisions live in ADRs (Structurizr).  
> If this document conflicts with ADRs, ADRs win.

## Where the rules live (most central ADRs)
- Modulith Architecture: [structurizr/adrs/0016-modulith.md](structurizr/adrs/0016-modulith.md)
- Quality gates [structurizr/adrs/0022-branching-release-promotion-and-quality-gates.md](structurizr/adrs/0022-branching-release-promotion-and-quality-gates.md)
- Boundary DTO rule: [structurizr/adrs/0026-dtos-at-boundaries-contract-data-must-be-independent-from-internal-models.md](structurizr/adrs/0026-dtos-at-boundaries-contract-data-must-be-independent-from-internal-models.md)


Testing is documented in: [structurizr/adrs/0020-testing-the-backend.md](structurizr/adrs/0020-testing-the-backend.md) and test folder structure in [backend/tests/README.md](backend/tests/README.md)

---

## Architecture encoded in the folder structure

We organize the backend in two dimensions:

1) **Horizontal separation:** bounded contexts (DDD-style)  
2) **Vertical separation:** layers inside each context (hexagonal / ports-and-adapters style)

### High-level layout


src/
├─ contexts/ # bounded contexts (horizontal separation)
│ ├─ chat/
│ ├─ customgpt/
│ └─ knowledge/
│
├─ interface/http/ # delivery mechanism (FastAPI)
└─ bootstrap.py # composition root: wiring ports ↔ adapters


---

## 1) Bounded contexts: `src/contexts/<context>/`

Each folder under `src/contexts/` is a bounded context with its own responsibilities, models, and implementation details.


src/contexts/
├─ chat/
├─ customgpt/
└─ knowledge/


Inside each context we use a consistent structure:


src/contexts/<context>/
├─ domain/ # pure domain model + domain rules
├─ application/ # use cases (orchestration) + ports (contracts)
└─ infrastructure/ # adapters (implementations), db, external clients


This is the practical implementation of “ports and adapters”:
- **Domain/Application define rules and contracts**
- **Infrastructure implements details**
- Dependencies point inward (infrastructure depends on application/domain, not vice versa)

---

## 2) Domain layer: `domain/` (pure core)

What belongs here:
- domain models (entities/value objects)
- domain functions (business rules)

What does *not* belong here:
- database sessions / ORM
- HTTP requests/responses
- calling other contexts
- calling external services/APIs

**Rule of thumb:** domain code only operates on in-memory objects and expresses business rules.  
Any “getting data from somewhere” is done in the application layer via ports.

---

## 3) Application layer: `application/` (use cases + ports)

The application layer implements use cases by orchestrating:
- fetching/storing through ports (db, other contexts, external APIs)
- calling domain logic
- committing via UoW (if applicable)

Typical structure:


src/contexts/chat/application/
├─ ports/ # contracts this context depends on
└─ service_functions.py # use cases / orchestration


### Ports (`application/ports/`)
Ports define *what the application layer needs*, not how it is implemented.

A good mental model:
- If a use case needs data or capabilities from “outside”, it must enter via a **port**.
- Ports are contracts: they are stable, test-friendly, and implementation-agnostic.

**Important boundary rule:** data passed through ports must follow the DTO boundary rules (see [ADR 0026](structurizr/adrs/0026-dtos-at-boundaries-contract-data-must-be-independent-from-internal-models.md)).

---

## 4) Infrastructure layer: `infrastructure/` (adapters)

Infrastructure contains implementations of ports (adapters), such as:
- database repositories and UoW implementations
- external API clients (e.g., LLM provider adapters)
- implementations of ports defined by other contexts

Typical structure:


src/contexts/chat/infrastructure/
├─ db/ # ORM mappings, repo/uow implementations, db plumbing
└─ adapters/ # external API adapters, cross-context adapters, etc.


Infrastructure is allowed to depend on libraries and framework details.  
It must translate those details into the port’s contract types.

---

## 5) Interface layer: `src/interface/http/`

The HTTP layer is our delivery mechanism (FastAPI):
- defines endpoints and request/response schemas
- calls application-layer use cases
- translates errors into HTTP responses

It should not contain business rules.  
If logic feels like “use case logic”, it belongs in the application layer.

---

## 6) Bootstrapping / composition: `bootstrap.py`

Ports and adapters are connected at the composition root:
- create adapter instances (db session factories, http clients, etc.)
- wire them into dependency containers / factories
- expose them as **port types** to the interface layer

Goal:
- HTTP layer depends on “what” (ports), not “how” (concrete adapters)

---

## How to navigate changes

### “I want to add a new feature / endpoint”
- Add/modify endpoint in `src/interface/http/`
- Implement the use case in `src/contexts/<context_a>/application/service_functions.py`
- Put business rules in `src/contexts/<context_a>/domain/`
- Add (/modify) port in `src/contexts/<contex_at>/infrastructure/`
- Add (/modify) adapter in `src/contexts/<context_a_or_other>/infrastructure/`
- Wire the adapter in `src/bootstrap.py` and `src/interface/http/composition.py` if needed

### “I want to change a business rule”
- Usually in `src/contexts/<context>/domain/`
- Possibly adjust orchestration in `src/contexts/<context>/application/service_functions.py`
- Try to keep infrastructure unchanged unless the rule requires new persistence/integration behavior

### “I need to integrate an external system”
- Define/extend a port in `src/contexts/<context>/application/ports/`
- Implement adapter in `src/contexts/<context>/infrastructure/adapters/`
- Wire the adapter in `src/bootstrap.py` and `src/interface/http/composition.py`

---

## Dataclass conventions (project rules)

We use @dataclass to model simple data structures, especially when:
- the object is primarily “data + invariants”
- value-based equality is useful for testing and reasoning

### `@dataclass(frozen=True)` for value objects / DTO-like structures
Use `frozen=True` when instances should be immutable after creation:
- makes behavior easier to reason about
- avoids accidental mutation bugs
- improves testability (values are stable)

### Mutable dataclasses (or regular classes) for entities
If the object represents an entity with identity and lifecycle (state changes over time), immutability may be the wrong fit.
Use a mutable structure only where mutation is a real domain need and is controlled by domain rules.

> Note: the exact “entity vs value object” line is domain-specific. Default to immutability unless you have a good reason not to.