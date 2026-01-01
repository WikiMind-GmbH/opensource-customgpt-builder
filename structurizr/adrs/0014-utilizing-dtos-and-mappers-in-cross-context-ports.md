# Utilizing DTOs in cross-context ports
Date: 2025-08-04

## Status

OPEN    

## Context
Our contexts each have their own domain models and we want to make sure that the contexts are decoupled from each other.   
If we now have cross context communication via Ports of Context `A` and Adapter implementing this Port in context `B`, we must pay close attention to how we define this interface to not create coupling.   
A)
We might be tempted to use domain models of `A` in the Port. But that binds the Port to the domain model and that is not advisable because 1) we don't want to have to modify the port(&adapters) every time we change something in the domain model 2) the domain model might contain way more information than we need for our interface 3) We don't want to leak internals of a context to the outside.

Therefore, DTOs and a mapper translating those is a solid and widely used choice.
B)
Additionally, we have the problems of the following kind:       
The adapter of Context B might need to access its db and therefore needs it uow.   
We don't want to have the uow of `B` as a parameter of the Port function of `A`or anything that couples the contexts.   
Therefore we will have the uow and similar dependencies as properties of the adapter (not defined in the port.) and then wire them up in the bootstrap.   
In this way, we have no coupling


## Decision

We will define DTOs in the Port and utilize those in the Ports functions to pass data.
The context owning the Port with its DTOs will then define a mapper function to translate the DTOs to domain objects.   
If we change the domain model or DTO, we will only have to adjust this mapper function and nothing more

Additionally, 






We will define per Cross context Port<>Adapter in the Port DTOs and a mapper function like this:

Port:
```.py
class DefaultCGPTRetreiverError(RuntimeError):
    "The adapter threw an error"
class CgptNotFoundError(DefaultCGPTRetreiverError):
    "CGPT does not exist"
class RoleDTO(StrEnum):
    user = "user"
    assistant = "assistant"
    system = 'system'

@dataclass(frozen= True)
class MessageDTO:
    role: RoleDTO
    text_content: str

class CustomGPTInstructionsRetreiver(Protocol):
    
    def get_cgpt_sys_prompt(self, cgpt_id: str, ) -> list[MessageDTO]: ...
```
Adapters init with the uow:

```.py
class CustomGPTInstructionsRetreiverAdapter(CustomGPTInstructionsRetreiver):
    def __init__(self, cgpt_uow_factory: Factory[CgptUOW]):
        self._cgpt_uow_factory: Factory[CgptUOW] = cgpt_uow_factory

    def get_cgpt_sys_prompt(
        self, cgpt_id: str
    ) -> list[
        MessageDTO
    ]:  # ToDo: add exception GPTDoesNotExist and add management here
        
        try:
            with self._cgpt_uow_factory() as uow:
                try:
                    cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
                except CGPTNonExistentError:
                    raise CgptNotFoundError
                
                messages_of_sysprompt: list[MessageDTO] = cgpt_infos_to_sysprompt(
                    cgpt_name=cgpt.name, cgpt_instructions=cgpt.instructions
                )
                return messages_of_sysprompt
        except Exception:
            raise DefaultCGPTRetreiverError
```

Wire everything up in the bootstrap
```bootstrap.py
@dataclass(frozen=True)
class DependenciesContainer:
    # Return **port types** (or ports’ concrete implementations if ports are Protocols)
    conversation_uow_factory: Factory[ConversationUOW]
    cgpt_uow_factory: Factory[CgptUOW]
    cgpt_instructions_adapter_factory: Factory[CustomGPTInstructionsRetreiver]
```

```.py
def bootstrap( ... ):
    def cgpt_instructions_adapter_factory() -> CustomGPTInstructionsRetreiver:
        # Adapter owns its own context’s UoW factory
        return CustomGPTInstructionsRetreiverAdapter(cgpt_uow_factory)

    return DependenciesContainer(
        ...
        cgpt_instructions_adapter_factory=cgpt_instructions_adapter_factory,
        ...
    )
```

## Consequences

