# Format of bootstrap.py

Date: 2025-08-04

## Status

OPEN    

## Context

(As later detailed in adr 16:) We are using hexagonal architecture principles, utilizing Ports and Adapters.  [Fastapis `Depends`](https://fastapi.tiangolo.com/tutorial/dependencies/).

Our backend app uitilizes the dependencies inversion techinique:   
Wherever we use Ports and Adapters, the service layer and its functions are only aware of the Port definitions - in our case `Protocol`s - and completely unaware and independent of the adapters implementing the Ports.    
The actual adapters/dependencies are injected into our service layer by the http layer. This is done by passing them as (Dependency) parameters to our service functions which utilizes them.

We can see this fact by looking at our **service layer function declarations**:
```.py
def continue_conversation(
    user_message: str,
    conv_id: str,
    conv_uow: ConversationUOW, # <- This is a port
    cgpt_retreiver: CustomGPTInstructionsRetreiver, # <- This is a port
    llm_adapter: LlmPort, # <- This is a port
    use_rag: bool = False,
) -> str:
```

`ConversationUOW`, `CustomGPTInstructionsRetreiver` and `LlmPort` are all service layer owned Ports / Protocols, not adapters / implementations:
```.py
class ConversationUOW(Protocol): # <- We use Protocols instead of abstract classes for Ports due to being more pythonic
    #make sure that one session per unit of work
    def __enter__(self)->Self: ...
    def __exit__(self, exc_type, exc, tb)-> None: ... # <- the `...` is in the actual code!
    def commit(self): ...
    def rollback(self): ...
    @property
    def conversation_repo(self)-> ConversationRepository: ...

class CustomGPTInstructionsRetreiver(Protocol):
    
    def get_cgpt_sys_prompt(self, cgpt_id: str, ) -> list[MessageDTORetreiver]: ...



class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages_excluding_sys_prompt: list[MessageDTOllm],
        cgpt_systemprompt: list[MessageDTOllm],
    ) -> str: ...
```

Thus, the http layer - our fastapi endpoints, need to inject those dependencies.   

However, in the same way we want our service layer to be modular and independent from any specific adapter implementations, we do not want to bake in (and set up) adapters into our http layer.    
We do want the http layer to work with the Ports defined in our service layer (dependency inversion - outer layers depend on inner one).    

Now there are two tasks that must be fulfilled by other modules:    
Initializing and setting up the dependencies (like starting the db mappers and creating adapter factories or singletons that can be used as fastapi dependencies). 

We also want this to be configurable, such that we can easily adjust things like the db url.
This could be done by setting default parameter values, looking up values from an env, or (the better version of reading straight from an env) utilizing the `pydantic_settings` library to create a settings.py.

Additionally, we need to connect this module with our http layer in some way.

We also want to have typing hints for the dependencies and the ability to use type checkers/linters.
Therefore, just using a dictionary export from a bootstrap function does not work.

## Decision
We want a solution which covers the important aspects and whose shortcomings can be fixed by changes that do not require a deeper refactor of the whole strucutre, but only the change of specific regions of code. This follows from our goal of establishing a foundation that can be used for future projects.   

We create three modules:
`bootstrap.py` whose bootstrap function creates a dependencies object containing all dependencies and which sets everything up (mappers/db schema creation)
`deps.py` which calls the bootstrap function of the above module utilizing the env values as parameters.
We import the dependencies Container object created in deps.py in all routers and utilize the dependencies.

Thus, we will not use `pydantic_settings` in a settings.py module for now, but work with os.getenv directly to populate the bootstrap parameters in deps.py.


The bootstrap function in bootstrap.py
``` bootstrap.py
def bootstrap(
    *,
    db_url_chat: str,
    db_url_cgpt: str,
    model_name: str,
    create_schema: bool = False,
) -> DependenciesContainer:
```


To benefit from intellisense and linter support, our bootstrap function returns a (typed) object that contains all the dependencies.
```bootstrap.py
@dataclass(frozen=True)
class DependenciesContainer:
    # Return **port types** (or ports’ concrete implementations if ports are Protocols)
    conversation_uow_factory: Factory[ConversationUOW]
    cgpt_uow_factory: Factory[CgptUOW]
    cgpt_retreiver_adapter_factory: Factory[CustomGPTInstructionsRetreiver]
    llm_adapter_factory: Factory[LlmPort]
    cgpt_queries_adapter_factory: Factory[CgptQueries]
    chat_queries_adapter_factory: Factory[ChatQueries]
    conversation_adapter_factory: Factory[ConversationPort]
```

The bootstrap function does all the necessary initialization and creates adapters or adapter factories.
``` bootstrap.py
def bootstrap(
    *,
    db_url_chat: str,
    db_url_cgpt: str,
    model_name: str,
    create_schema: bool = False,
) -> DependenciesContainer:
    chat_start_mappers()
    engine_chat = _make_engine(db_url_chat, chat_prepare_engine)
    sessionMaker_Chat: sessionmaker[Session] = _make_sessionmaker(engine_chat)
    if create_schema:
        chat_metadata.create_all(engine_chat)
    register_last_message_at_events(sessionMaker_Chat)

    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(sessionMaker_Chat)

    # Stateless LLM adapter can be a singleton or a factory; both fine.
    _llm_adapter = OpenaiAdapter(model_name=model_name)

    ...

    def conversation_adapter_factory() -> ConversationPort:
        return ConversationAdapter(conv_uow_factory=conversation_uow_factory)

    return DependenciesContainer(
        conversation_uow_factory=conversation_uow_factory,
        cgpt_uow_factory=cgpt_uow_factory,
        cgpt_retreiver_adapter_factory=cgpt_instructions_adapter_factory,
        llm_adapter_factory=llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_queries_adapter_factory,
        chat_queries_adapter_factory=chat_queries_adapter_factory,
        conversation_adapter_factory=conversation_adapter_factory,
    )
```
(If a dependency can be a singleton or if it must be a factory is discussed in another ADR.)

The connecting piece with our http layer is the `deps.py` module.   
In `deps.py`, we create a `DependenciesContainer` object by calling the `bootstrap` function utilizing the variables defined in `.env`    



```deps.py
from src.bootstrap import bootstrap, DependenciesContainer

deps: DependenciesContainer = bootstrap(
    db_url_chat=require_env("DB_URL_CHAT"),
    db_url_cgpt=require_env("DB_URL_CGPT"),
    model_name=require_env("MODEL_NAME"),
    create_schema=require_env("CREATE_SCHEMA").lower() == "true"  # dev/test only
)
```

Now we can import into all routers this `deps` object from the `deps.py` module. Due to the fact that no matter how often we import a module, the module code will only be executed once per runtime, we have no problem with mappers running more than once, which would be a problem.

```chat_commands.py
from src.interface.http.deps import deps

deps: DependenciesContainer = deps

@chat_commands_router.post(
    "/send-user-message",
    response_model=AssistantMessage,
    operation_id="sendUserMessage",
)
async def send_user_message(
    request: UserMessageRequest,
    conv_uow: ConversationUOW = Depends(deps.conversation_uow_factory),
    llm_adapter: LlmPort = Depends(deps.llm_adapter_factory),
    cgpt_retreiver: CustomGPTInstructionsRetreiver = Depends( 
        deps.cgpt_retreiver_adapter_factory # <-----
    ),
) -> AssistantMessage:
```
### Influences of ths decision on Testing
When testing the app and its endpoints directly -e.g. in an e2e test, we create a pytest fixture that returns a fastapi Testclient. In the testclient, we can override the dependencies adapters with fake adapters.

To assure that we do not miss any dependency overrides in the test-app fixture, we pass it a DependenciesContainer object (which itself is a fixture)
```
@pytest.fixture()
def test_client(test_deps:DependenciesContainer): #<--
    from src.interface.http.deps import deps
    from src.interface.http.app import app
    app.dependency_overrides[deps.conversation_uow_factory] = test_deps.conversation_uow_factory
    ...
    test_app: TestClient = TestClient(app)
    return test_app
```

With this exact setup, the bootstrap function is run when creating a Testclient. Discussion on this in consequences

When testing the service layer, we can simply pass any adapter (factory) implementing the Port of a service layer function parameter. We do not need to use the ones defined in deps.py.

Testing 'architecture' specifics are out of scope and discussed in another adr.
## Consequences

With this change, we decouple the wiring from the http layer and make it easy to change dependencies without touching the http layer, further modularizing our app according to ddd and hexagonal principles. 


Running unit tests for service level and below is straight forward, the bootstrap funcion is not run and  we set up mappers and fake adapters in conftest.py. 
As usual, we need to be paying attention to call the mappers only once by putting the mapper fixture at the top level.

If we want to test the endpoints directly for e2e use case tests or individually, we have the side effect of the bootstrap function running due to how we handle imports. We can however, override the dependencies.



Utilizing a settings.py module is an improvement that should be done in the future.   

The exact setup is something I created based on the cosmic python book, but adopted to fit a non message-bus architecture and with keeping typing in mind. However, this means that it is not a 1:1 adaption and has not proven itself, making it less safe.

I have not confimed, but chatgpt criticises:
Current setup is safe with uvicorn (dev + prod) without preload.
If we ever switch to gunicorn with --preload, or any preload/forking server, we must:
Move bootstrap() to FastAPI lifespan (per-process, after fork), or
Rebuild/dispose engines in a post_fork hook.
Consider making mapper/event registration idempotent to be resilient under alternative runners or tests.

I explored utilizing the app state once without good results, but maybe not the exact suggestions [here](https://chatgpt.com/s/t_6930be86bb308191a3e0d009705ec459) 
[Other food for thought](https://chatgpt.com/s/t_6930c2e2c1c88191b4471fb227a37dc1)