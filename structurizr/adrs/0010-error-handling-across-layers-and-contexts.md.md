# ADR-XXX: Error Handling Pattern (Ports Own Errors, Global HTTP Translation)

**Status:** Open
**Date:** 2025-10-03

## Context

We need a simple, consistent approach to error handling across multiple bounded contexts and layers.

## Decision

1. **Error classes per context & layer combo**

   * Each bounded context defines its own **domain error classes** (business-focused).
   * Each **port** (e.g., repository/gateway interface) defines its own **port error classes** for that context.

2. **Ports define errors; adapters only raise those**

   * Adapters must translate vendor/ORM exceptions into the **port-defined** errors and **never** leak vendor exceptions.
   * Include a single catch-all mapping for anything not explicitly handled:

   ```python
   # inside the adapter
   from sqlalchemy.exc import IntegrityError, OperationalError, StaleDataError

   class RepoError(Exception): ...
   class UniqueViolation(RepoError): ...
   class ConcurrencyConflict(RepoError): ...
   class RepoUnavailable(RepoError): ...

   def _map_sa(e: Exception) -> RepoError:
       if isinstance(e, IntegrityError):   return UniqueViolation(str(e))
       if isinstance(e, StaleDataError):   return ConcurrencyConflict(str(e))
       if isinstance(e, OperationalError): return RepoUnavailable(str(e))
       return RepoError(str(e))  # catch-all
   ```

Adapter can use an explicit translator:
```
from sqlalchemy.exc import IntegrityError, OperationalError, StaleDataError
from .ports import RepoError, UniqueViolation, ConcurrencyConflict, RepoUnavailable

def _map_sa(e: Exception) -> RepoError:
   if isinstance(e, IntegrityError):   return UniqueViolation(str(e))
   if isinstance(e, StaleDataError):   return ConcurrencyConflict(str(e))
   if isinstance(e, OperationalError): return RepoUnavailable(str(e))
   return RepoError(str(e))  # catch-all
```

3. **Service/Application layer**

   * We will **not** manually translate domain or port errors in the service layer.
   * Services allow **domain** and **port** errors to bubble up unchanged to keep the application layer simpler.

4. **HTTP layer (FastAPI)**

   * FastAPI **exception handlers** must handle and translate **all** domain and application/port errors to `HTTPException` responses.
   * Centralize this translation with global handlers; better: an explicit translator function that handlers call
```
one handler catching all exception types, then calling the translator function to return the correct translation.
Need one global catch-all again, here: take care not to overwrite important errors that fastapi would throw for validation for example. So maybe just return all errors not explicitly translated as-is
```
   * If using an explicit translator, it maps known domain/port/app errors to HTTP status codes; unknowns become 500.


## Consequences

* **Pros:** Clear boundaries; no vendor leaks; minimal service-layer boilerplate; one place for HTTP mapping; predictable failure semantics.
* **Cons:** HTTP layer must know the set of domain/port/app error types to translate.

## Status & Next Steps

* **Status:** Open
* **Next:**

  1. Define domain error modules per context.
  2. Define port error classes per port per context.
  3. Update adapters to map vendor exceptions using the catch-all `_map_sa` pattern.
  4. Add FastAPI global exception handlers (or a single translator + thin handlers) to cover all domain and port/app errors.

