# Service function always expect UOW, even as adapters from other contexts

Date: 2025-08-04

## Status

ACCEPTED    

## Context

Context A utilizes an adapter of Context B.    
Context B's adapter simply calls a service function and returns its value.   
We want this service function to work i) when called by the http layer and ii) if called by an adapter.  


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

