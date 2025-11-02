# ADR-XXX: Error Handling Pattern (Ports Own Errors, Global HTTP Translation)

**Status:** Open
**Date:** 2025-10-03

## Context

We need a simple, consistent approach to error handling across multiple bounded contexts and layers.

See:
https://chatgpt.com/s/t_68fa00d64ad48191802c77e5deccb544

For more details on how catch-all exceptions can be applied, and possible pitfalls,  see https://chatgpt.com/s/t_68fa149487a48191a5d18869845aba8b
https://chatgpt.com/s/t_68faad13da78819190b985d0e0c62b4b


Absolutely—here’s a single, coherent guide that merges both threads: **where to define exceptions across layers** and **how to handle/reraise them safely (including a per-port catch-all).**

#### Exception ownership by layer

#### 1) Domain (Core)

**What:** Business-rule & invariant errors.
**Why:** They express domain semantics and are independent of infrastructure.
**Examples:** `InvalidPrompt`, `QuotaExceeded`, `OperationNotAllowed`.
**How used:** Raised by domain logic or services; handled in services or mapped to HTTP at the boundary.

#### 2) Per-Port (Contract) — your key stability point

**What:** The *declared failure modes* of a port (the interface your app calls).
**Why:** Adapters may change tech, but callers rely on stable, domain-ish semantics.
**Examples:** `CgptNotFoundError`, `RetrieverUnavailable`, `RetrieverError` (base).
**How used:** **Adapters translate infra/library errors → these exceptions**. Callers see only port exceptions (and domain exceptions), never raw infra ones.

#### 3) Service / Use-case layer (optional, be frugal)

**When to create service exceptions:** Only if the service adds **new semantics** that don’t belong to a single port (e.g., orchestration/compensation failure, cross-port normalization).
**Otherwise:** Use **domain + port exceptions directly**; catch/handle or let them bubble to HTTP.

#### 4) Adapters / Infrastructure

**What:** Implementation details stay here.
**Rule:** Never leak infra exceptions upward. **Map to port exceptions** (specific first, then a *port-scoped* catch-all). Keep try-blocks tight.

#### 5) HTTP Boundary

**What:** Central exception handlers that map domain/port exceptions → HTTP (Problem Details).
**Rule:** Keep HTTP knowledge here; the core remains transport-agnostic.

---

#### Handling & re-raising: rules that keep you safe

* **Define exceptions per port** as part of the port interface; adapters raise only those.
* **Raise instances, not classes:** `raise CgptNotFoundError("cgpt_id=...")`.
* **Preserve tracebacks:** `raise ... from e` for observability.
* **Catch only when you add value:** translation, add context, adjust retryability, ensure cleanup.
* **Keep try-scopes tight** so you don’t mask unrelated bugs.
* **No blanket `except Exception`** *except* for a **final, port-scoped catch-all** that wraps to a generic port error and re-raises (with chaining).
* **Don’t catch control-flow exceptions:** `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`, `asyncio.CancelledError`.
* **Expected absence vs exception:** if “not found” is common/acceptable, return `model | None`. If it violates an invariant for the operation, raise `NotFound`.
* **Log once at the boundary** (HTTP/middleware). Inside adapters/services, prefer adding context and re-raising—avoid duplicate logs.

---

### Minimal shapes (concise patterns)

#### Port contract (exceptions + protocol)

```python
# ports/cgpt_retriever.py
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class CGPTRetrieverError(RuntimeError): ...
class CgptNotFoundError(CGPTRetrieverError): ...
class CGPTRetrieverUnavailable(CGPTRetrieverError): ...
class RetrieverUnexpectedError(CGPTRetrieverError): ...  # final catch-all type

class RoleDTO(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"

@dataclass(frozen=True)
class MessageDTO:
    role: RoleDTO
    text_content: str

class CustomGPTInstructionsRetriever(Protocol):
    def get_cgpt_sys_prompt(self, cgpt_id: str) -> list[MessageDTO]: ...
```

#### Adapter (specific mappings → final port-scoped catch-all)

```python
# adapters/cgpt_retriever_adapter.py
import asyncio
from src.contexts.chat.ports.cgpt_retriever import (
    CustomGPTInstructionsRetriever,
    MessageDTO, CgptNotFoundError, CGPTRetrieverUnavailable, RetrieverUnexpectedError
)
from src.contexts.chat.domain.models import CustomGPT
from src.contexts.chat.domain.uow import CgptUOW, CGPTNonExistentError
from src.shared.types import Factory

def cgpt_infos_to_sysprompt(*, cgpt_name: str, cgpt_instructions: str) -> list[MessageDTO]:
    ...

class CustomGPTInstructionsRetrieverAdapter(CustomGPTInstructionsRetriever):
    def __init__(self, cgpt_uow_factory: Factory[CgptUOW]):
        self._cgpt_uow_factory = cgpt_uow_factory

    def get_cgpt_sys_prompt(self, cgpt_id: str) -> list[MessageDTO]:
        try:
            with self._cgpt_uow_factory() as uow:
                try:
                    cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
                except CGPTNonExistentError as e:
                    raise CgptNotFoundError(f"cgpt_id={cgpt_id}") from e

                return cgpt_infos_to_sysprompt(
                    cgpt_name=cgpt.name,
                    cgpt_instructions=cgpt.instructions,
                )

        # Map known transient/operational issues first
        except (ConnectionError, TimeoutError) as e:
            raise CGPTRetrieverUnavailable(f"cgpt_id={cgpt_id}") from e

        # Preserve control-flow exceptions
        except (KeyboardInterrupt, SystemExit, GeneratorExit, asyncio.CancelledError):
            raise

        # Final, port-scoped catch-all: wrap & chain (never swallow)
        except Exception as e:
            raise RetrieverUnexpectedError(f"unexpected failure; cgpt_id={cgpt_id}") from e
```

#### Service layer (use domain/port exceptions; add service errors only for new semantics)

```python
def build_system_prompt(retriever: CustomGPTInstructionsRetriever, cgpt_id: str) -> list[MessageDTO]:
    try:
        return retriever.get_cgpt_sys_prompt(cgpt_id)
    except CgptNotFoundError:
        # Either handle (e.g., default prompt) or bubble unchanged
        raise
    # Add service-level exceptions only if this function introduces
    # a new, higher-level failure not captured by the port/domain types.
```

#### HTTP boundary (Problem Details mapping)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.contexts.chat.ports.cgpt_retriever import (
    CgptNotFoundError, CGPTRetrieverUnavailable, RetrieverUnexpectedError
)

app = FastAPI()

def problem(status: int, type_: str, title: str, detail: str | None = None):
    return JSONResponse(
        status_code=status,
        content={"type": type_, "title": title, "status": status, "detail": detail},
        headers={"Cache-Control": "no-store"},
    )

@app.exception_handler(CgptNotFoundError)
def _not_found(_: Request, exc: CgptNotFoundError):
    return problem(404, "urn:problem:cgpt-not-found", "Custom GPT not found", str(exc))

@app.exception_handler(CGPTRetrieverUnavailable)
def _unavailable(_: Request, exc: CGPTRetrieverUnavailable):
    return problem(503, "urn:problem:retriever-unavailable", "Retriever unavailable", str(exc))

@app.exception_handler(RetrieverUnexpectedError)
def _unexpected(_: Request, exc: RetrieverUnexpectedError):
    return problem(500, "urn:problem:unexpected", "Unexpected error", "An unexpected error occurred.")
```

---

### Should you have a blanket per-port catch-all?

**Yes**, at the adapter boundary—**one per port**—implemented as the *final* `except Exception as e` that **wraps into a generic port error** and **re-raises with chaining**.
This ensures no unknown infra errors leak outside the adapter while preserving debuggability.

---

### Quick checklist

* **Domain exceptions:** business rules; raised/handled in core/services.
* **Per-port exceptions:** part of the port contract; adapters only raise these.
* **Service exceptions:** only when you invent new cross-port semantics; otherwise reuse domain/port.
* **Adapters:** map known errors specifically; add a **port-scoped catch-all**; no swallowing; tight try-scopes; chain with `from e`.
* **HTTP:** central Problem Details mapping; log at the boundary.

If you want, paste another port’s methods + typical failures and I’ll suggest the minimal exception set and its adapter mapping table.


## Decision
OLD:

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


