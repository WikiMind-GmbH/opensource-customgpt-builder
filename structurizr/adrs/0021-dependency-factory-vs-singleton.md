# 24. Dependency factories vs. singletons

# Status
Accepted

## Context

We use Hexagonal Architecture (ports & adapters) and per-request **Unit of Work (UoW)** to manage DB sessions/transactions.
Some adapters are **request-scoped** (e.g., UoW), while others can be **process-scoped** (e.g., LLM client) if safe.

Creating all dependencies as factories (per request) is always safe but can be wasteful (e.g., repeatedly constructing heavyweight SDK clients). Using singletons reduces overhead but introduces concurrency concerns if adapters hold mutable or request-specific state.

### Forces / Constraints

* **Correctness & isolation:** UoW/DB `Session` must be per request.
* **Simplicity:** Prefer decisions that are easy to apply consistently.
* **Performance:** Avoid unnecessary construction of heavy clients.
* **Safety:** Avoid subtle concurrency bugs in multi-threaded workers.

## Decision

Adopt a **conservative default**:

1. **Must be a factory (per request)** if an adapter:

   * Holds **request / UoW / transaction** state (e.g., SQLAlchemy `Session`, UoW).
   * Keeps **mutable state** that isn’t explicitly concurrency-safe.
   * Needs **per-user/tenant credentials** on the instance.
   * Uses an SDK that is **not thread-safe**.

2. **May be a singleton (per process)** if an adapter:

   * Is **stateless / immutable**, **or**
   * Only holds **thread-safe shared resources** (e.g., HTTP client connection pool, SDK documented as thread-safe), **and**
   * Stores **no per-request state** on the instance.

3. **Bias to factories.** We will default to factories unless we are **confident** a singleton is safe. We will **avoid adding concurrency control** (locks, etc.) in adapters for now; if that becomes necessary, we will revisit.

### Rationale

* Factories guarantee isolation and avoid shared mutable state across requests.
* Singletons reduce overhead for heavy clients but require proof of thread safety and no per-request state.
* A strict rule (“singletons only if immutable/stateless”) is easy to apply and error-resistant; we can relax it later case-by-case.

### Considered Options

* **Factories everywhere:** Safest, simplest; potentially wasteful for heavy clients.
* **Singletons wherever possible:** Best performance; high risk without strict review and thread-safety guarantees.
* **Hybrid (chosen):** Default to factories; allow singletons for immutable/stateless or documented thread-safe adapters.

## Consequences

**Positive**

* Clear, low-cognitive-load rule for new dependencies.
* Minimizes concurrency bugs from shared mutable state.
* Keeps UoW semantics correct (new `Session` per request).

**Negative / Trade-offs**

* May incur extra object creation overhead (e.g., recreating external SDK clients) until we explicitly allow singletons.
* Developers must occasionally recognize when performance warrants an exception and document it.

### Risks & Mitigations

* **Risk:** Overhead from factories for heavy clients.
  **Mitigation:** Promote specific adapters to singletons when proven safe (documented thread safety, no per-request state).

* **Risk:** Subtle shared-state bugs if a non-immutable adapter is mistakenly made singleton.
  **Mitigation:** Code review checklist item (“lifetime: factory vs singleton?”) and ADR reference.

### Examples / Rules of Thumb

* **Always factory:** UoW, Repositories that wrap a `Session`, anything that holds request context.
* **Singleton OK:** LLM/OpenAI client configured once; shared HTTP client with connection pooling; read-only config providers.

### Future Work

* Add a **lifetime annotation** to dependency factories (e.g., `@lifetime("request")` vs `@lifetime("process")`) to make intent explicit.
* Provide a **bench + profiling** guide to justify promoting specific adapters to singletons.
* If/when needed, introduce **concurrency control** inside specific adapters to enable safe singleton usage.
* Document thread-safety guarantees for any SDKs we rely on.
