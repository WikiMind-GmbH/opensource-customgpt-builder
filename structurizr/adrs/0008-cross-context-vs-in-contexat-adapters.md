# Cross context vs in context adapters

Date: 2025-08-04

## Status

OPEN

Superceded by [19. Different type of Port Adapter combos](0019-different-type-of-port-adapter-combos.md)

## Context

We have different sources of adapters: cross context adapters when it is absolutely necessary to have communication between different contexts.  
And in-context adapters, e.g. for calling an external api, where, similar to our db implementation being hidden behind the repo port, we do not want to have the implementation details in our core layer.

As such, they differ completely in their nature: The cross context adapter providing core/domain level functionality, while the in-context adapter explicitly does not, it provides explicitly non core/domain level functionality.

Due to that, they must be strucured completely differnt. -The logic in the cross context adapter must be minimal -it is merely an interface like our http layer. As such, we want to reroute the function call to a service layer function which provides this core layer functionality/logic.  
For the in-context adapter however, this would directly contradict its purpose: guranteeing that its implementation and logic is decoupled from the service/domain layer.

For the cross-context adapter:
Context A utilizes an adapter of Context B.  
Context B's adapter simply calls a service function and returns its value.  
We want this service function to work i) when called by the http layer and ii) if called by an adapter.

! However, we now have another problem: The provider context now depends on the consumer context (via the Port). This breaks the dependency inversion principle and does not necessarily scale well.
Ignore Option B but else: https://chatgpt.com/s/t_690aa6070224819195b006b5f66dbdc3

## Decision

The adapter function does not enter the passed UoW(or other dependency), it passes a uow directly to the service layer function.

See the following chatgpt snippet for how this ensures consistency

```
# HTTP controller → service (Context B)
# DI provides an unopened handle
def get_b_uow() -> KnowledgeUoW: return make_b_uow()

# controller
def route(uow: KnowledgeUoW = Depends(get_b_uow)):
    return b_service.fetch(uow=uow, topic=...)

# application service (owns the boundary)
def fetch(*, uow: KnowledgeUoW, topic: str) -> ResultDTO:
    with uow:
        data = uow.queries.find(topic)
        # optionally uow.commit() if writing
        return map_to_dto(data)

# Cross-context adapter (Context A → B)
class RetrievalForChatAdapter(RetrievalPort):
    def __init__(self, b_uow_factory: Callable[[], KnowledgeUoW]):
        self._mk = b_uow_factory

    def fetch_docs_for_chat(self, topic: str) -> RetrievedDocs:
        uow = self._mk()                             # create handle
        docs = b_service.fetch(uow=uow, topic=topic) # service owns the boundary
        return map_to_chat_dto(docs)
```

## Consequences

Adapter is initialized with a uow factory. In the adapter function: create uow from uow factory, pass uow to service function.

Details are not yet determined (init adapter with uow factory or uow directly)
