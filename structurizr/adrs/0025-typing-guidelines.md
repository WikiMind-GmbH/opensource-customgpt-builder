# typing guidelines

Not having the type checker throw errors is a great sign. However, it does not mean that everything was done cleanly and that the types chosen guarantee best readability.

## Accepted
OPEN 

## Created by

Albert Sandritter

## Decision Maker

Albert Sandritter



## Scope

Backend typechecking with pyright / vscode pylance. Always in the context of the currently selected settings.json.



## Context

Not having the type checker throw errors is a great sign. However, it does not mean that everything was done cleanly and that the types chosen guarantee best readability.



## Alternatives Considered

Multiple Aspects where we need to make a decision:

### 1. When to choose more general or specific types



## Decision
### 1. Prefer Precise Types Over General Types if meaningful

Always prefer the most specific, semantically meaningful type available instead of widening to a more generic one (e.g. `Callable`, `Any`, or overly abstract aliases).

Concrete library types carry more information, improve readability, and allow the type checker to enforce stronger guarantees.

**Example**

```python
T = TypeVar("T")
Factory = Callable[[], T]

# Too generic
def build_session(factory: Factory[Session]) -> Session:
    return factory()

# Prefer the concrete type
def build_session(factory: sessionmaker[Session]) -> Session:
    return factory()
```

Although `sessionmaker[Session]` is callable and compatible with `Callable[[], Session]`, it conveys stronger intent and preserves SQLAlchemy-specific typing information.

**Rule of thumb:**
If a richer or domain-specific type exists, use it instead of a structurally compatible but more general type.





## Consequences

Describe the impact of this decision, including:

* Benefits introduced
* Trade-offs accepted
* New limitations or constraints
* Risks and how they may be mitigated
* Follow-up work required (if any)

Be explicit about what becomes easier and what becomes harder as a result.
