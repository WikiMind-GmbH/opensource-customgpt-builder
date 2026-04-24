# 26. DTOs at boundaries: contract data must be independent from internal models

Date: 2026-03-10

Boundary contracts must use DTOs that belong to the contract (not to either side’s internal models), and mapping between DTOs and internal models must happen outside the port module.

## Status

Accepted

Supercedes [Utilizing DTOs in cross-context ports](0014-utilizing-dtos-and-mappers-in-cross-context-ports.md)

## Created by

Albert Sandritter


## Decision Maker

Albert Sandritter



## Scope

Applies to **all boundaries** in this repository, including:
- cross-bounded-context calls inside the modulith
- calls across layers/modules within a context EXCEPT DOMAIN MODEL ORM REPOSITORY
- any Port/Adapter integration, regardless of whether it is “consumer→provider” or “provider→consumer”

Does **not** prescribe concrete DTO field schemas. It defines **rules and responsibilities**, not payload shapes.

Does **not** define runtime error-handling behavior (logging, retries, HTTP mapping, etc.).

## Context

We want clear separation and long-term maintainability. A common failure mode is structural coupling caused by passing internal models across boundaries:

- Internal domain models change for internal reasons; coupling contracts to them creates ripple effects.
- Internal models often contain more data and invariants than a boundary should expose.
- Exposing internal models leaks details and reduces autonomy of the owning part.
- “Renaming leakage” (DTOs that are structurally identical to another side’s model) creates the same coupling under a different name.

This problem is independent of direction and topology:
- whether the boundary is between bounded contexts or layers/modules
- whether the integration is in-process (modulith) or remote
- whether one side is considered “consumer” or “provider”

We need a stable, explicit boundary contract that protects internal models from each other and keeps responsibilities clear.

## Alternatives Considered

1) **Use internal domain models directly in boundary contracts**
- Advantages:
  - Less mapping code up front
  - Fast initial development
- Disadvantages:
  - High coupling; internal refactors become cross-cutting changes
  - Leaks internals and increases blast radius of domain evolution
  - Encourages “God models” traveling across the system
- Not chosen because it undermines bounded context autonomy and maintainability.

2) **Use provider domain models as the shared contract**
- Advantages:
  - Provider remains “source of truth”
  - Less duplication than mapping on both sides
- Disadvantages:
  - Still binds consumers to provider internals
  - Prevents consumer from evolving independently
  - Breaks when multiple consumers need different shapes/semantics
- Not chosen because a contract must be stable and externalized, not an internal domain surface.

3) **Use consumer domain models as the shared contract**
- Advantages:
  - Fits consumer use cases directly
  - Less mapping inside consumer
- Disadvantages:
  - Forces provider to model the consumer’s concepts (reverse dependency)
  - Creates implicit coupling and semantic confusion at the boundary
- Not chosen because providers must not depend on consumer domain language.

4) **Use contract-owned DTOs + explicit mapping except between domain model and orm repo(chosen)**
- Advantages:
  - Stable contracts with minimal coupling
  - Internal refactors stay local
  - Clear separation of responsibilities
- Disadvantages:
  - Requires mapping code and discipline
  - Requires explicit evolution/versioning of DTOs

## Decision

1) **All boundary data is expressed via contract-owned DTOs except between domain model and orm repo**
- Data crossing a boundary must use DTOs that belong to the **contract**, not internal models.
- DTOs must not be:
  - internal domain entities
  - persistence/ORM models
  - structurally identical “renamed” versions of another side’s internal model

2) **Port module contents are contractual**
Where a boundary is represented as a Port module, that module contains:
- the Port interface (Protocol) describing operations (including property functions where necessary)
- the DTOs used by the contract (inputs/outputs)
- the contract-level error types exposed to callers

3) **Mappers live outside the Port module**
- Mapping between DTOs and internal models happens outside the Port module.
- Each side maps contract DTOs into its own internal representations.
- The Port module must not import internal domain or infrastructure.

4) **Dependencies do not leak into the contract**
- Port functions must not require internal dependencies (e.g., UoW/DB/session/client objects) as parameters.
- Adapters may receive such dependencies via construction/DI as implementation details.

## Consequences

Benefits:
- Clear, stable boundary contracts with reduced coupling.
- Internal refactors (domain/persistence/external libraries) are less likely to ripple across the system.
- Contracts become easier to test and reason about.
- Port modules become predictable and reviewable: Protocol + DTOs + contract errors.

Trade-offs / costs:
- Additional mapping code and maintenance overhead.
- DTO evolution must be handled intentionally (compatibility considerations).

Constraints introduced:
- “No internal models across boundaries” is now an explicit rule.
- “No dependency objects in port signatures” is now an explicit rule.

Risks and mitigations:
- Risk: DTOs drift into “renamed internal models”.
  - Mitigation: code reviews check DTO semantics; DTO names must reflect boundary concepts, not internal model names.
- Risk: mapping becomes scattered or duplicated.
  - Mitigation: keep mappers close to the owning internal model (per context/layer) and treat them as first-class code.
