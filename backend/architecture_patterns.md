# Motivation: Unmaintainable architecture: ball of mud

When software is rushed to deliver quick results and grows without attention to how new functionality is added, components end up tightly coupled, responsibilities blur, and the codebase becomes hard to change. This kind of system is commonly called a “ball of mud.” In a ball of mud, components are tightly coupled, not cohesive, and each carries multiple responsibilities—making the system hard to read, understand, and develop for.
If we instead follow clean code and architecture patterns, we can avoid that.
Let’s compare a ball of mud with a cleaner architecture to evaluate whether the extra structure is worth it.

## Ease of change

### Ball of mud
- Changes in one component lead to a cascading effect.
- Seemingly unrelated but coupled components must be changed.
- Due to unclear boundaries and architecture, the affected components might be unexpected.

### Clean architecture
- Cohesive components with a single responsibility depend on other components **only via Ports** (stable interfaces defined by the consumer/inner layer).
- If we change something, we always know if and what else we need to change.I.e. If we change our data layer, we must only assure that its Adapter still works.

## Readability

### Ball of mud
- Unmaintainable code: unclear responsibilities and coupling force you to understand far more than the component you want to change/debug.

### Clean architecture
- Cohesive components with a single responsibility communicate through Ports and use **their own layer-specific data types**.
- To understand a component, you need only the component itself and the Ports it defines/depends on.
- The whole picture and how the single components work toghether is easier to understand due to clearly defined context boundaries and interfaces

## Testability
### Ball of mud
Hard to write tests for due to thight coupling.
### Clean Architecture
Unit tests are easy to write as we can just inject fake adapters. No need to worry about coupling.

---

### Notes on terms

- **Cohesion:** how closely related the responsibilities inside a single component are. High cohesion means a component does one focused thing well. It is closely related to the single responsibility principle
- **Coupling:** the degree to which a component depends on others. Lower coupling is better.
- **Service layer**: other names are orchestration layer and application layer
- **Ports & Adapter**: A Port is a contract on how a component has to be structured. An Adapter is an implementation of such a port. Functions will have Ports as Parameters and we will pass them an Adapter. Will be explained later in this document.





## Solution: Clean code and Architecture patterns
With this motivation in mind, we want to follow clean architecture patterns. In this first iteration, I decided to closely follow the [Cosmic Python books](https://www.cosmicpython.com/) chapters 1-6, 13 and adapt them slightly in places I see improvements.

As the book follows Domain-Driven Design (DDD), the patterns presented are often influenced by this. But the ideas of structuring the code into high vs low level modules and further seperating the code into sub modules, and defining how these modules 'talk'/interface with each other e.g. by utilizing the Port-Adapter pattern, helping with the decoupling of different components, is clean design regardless of DDD (and also the basis for Microservices).

So I first want to detail how Ports and adapters work, what DDD is and then go into more detail on the implemented architecture patterns.

# Background
## Ports & Adapters
We want to find a solution for the following problem:   
How can a component define its interface with another component? We want the consumer component (i.e. the component that utilizes functionality of the other one) to be the owner of the contract. We want the contract to be in the 'language' of the owner and not be concerned with implementation details for clear decoupling.   
In this way, the consumer component is easily understood without knowing anything about the other components.   

This is achived in the following way:    
The consumer component defines Ports utilizing Pythons Protocol, e.g.
```
class ConversationRepository(Protocol):
    def get(self, conv_id:str)-> Conversation: ...
    def list_all_overviews_ordered_by_latest_msg(self,)-> Sequence[ConversationOverview]: ...
    def create_conversation(self)-> Conversation: ...
    def add_message(self, msg: Message): ...
    def delete(self, conversation: Conversation): ...
```

And then another component implements this port as an adapter:    
backend/src/contexts/chat/infrastructure/db/conv_repo_implmementations.py
```
class SQAlchemyConversartionRepository(ConversationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session
    def get(self, conv_id:str)-> Conversation:
        conv = self._session.get(Conversation, conv_id)
        if conv == None: raise ConversationNonExistentError(conv_id)
        return conv
    def list_all_overviews_ordered_by_latest_msg(self,)-> Sequence[ConversationOverview]:
        stmt = ( 
            select(Conversation.id, Conversation.title)
            .order_by(conversations.c.last_message_at.desc().nullslast())
        )
        rows = self._session.execute(stmt).all()
        return [ConversationOverview(id=id, title=title) for id, title in rows] 
    def create_conversation(self)-> Conversation:
        uuid = str(uuid4())
        conv = Conversation(id = uuid)
        self._session.add(conv)
        return conv
    def add_message(self, msg: Message):
        self._session.add(msg)
    def delete(self, conversation: Conversation):
        self._session.delete(conversation)
```
This adapter is part of the data layer which contains other modules that make this adapter work.


## Domain driven design
[Most unclear to Albert]
Domain-Driven Design (DDD) is concerned with the following things:
1. Having at the heart of the software system a model of the buisness domain whose language (buisness-) domain experts will understand and agree with.
2. Structuring the rest of the code around this domain model and clear decoupling of modules created by subdomains and an architecture consisting of 1) TOP: http layer 2)CORE/MIDDLE: domain layer + service layer 3) LOWER: data layer
3. Keeping these modules 'pure' -> not leaking data types of different modules leak into each other. This is done by using Ports & Adapters.
#### What is a domain model
At the heart of DDD is looking at a software-system as something that models a buisness domain. The domain model and the domain functions that we will create in our software system should be understandable by, and in the language of, a domain expert who has no software development experience.   

Cosmic Python quote:
>The domain model is the mental map that business owners have of their businesses. All business people have these mental maps—they’re how humans think about complex processes.

>You can tell when they’re navigating these maps because they use business speak. Jargon arises naturally among people who are collaborating on complex systems.

Martin Fowler quotes: 
> Domain-Driven Design is an approach to software development that centers the development on programming a domain model that has a rich understanding of the processes and rules of a domain.

>At the heart of this was the idea that to develop software for a complex domain, we need to build Ubiquitous Language that embeds domain terminology into the software systems that we build

As our current project is closely related to swe, the border between technical implementation details and domain is more fuzzy to me, but I would argue the following:
We have the following contexts:
A context regarding chats, one for customGPTs and one for the RAG System.
Lets look at chat context   
A Conversation might be composed of messages, a system prompt(itself a list of messages), an id and so on.

The buisness domain model will include the process of initializing a Conversation with a System Prompt, throwing an error if I want to add a message to the conversation if no system Prompt has been implemented and so on.   
The important thing:    
How to interface with the openai api, the expected json structure of the openai API are not part of the domain model.    
Our message might be a dataclass with two properties: Role and text, nothing more.

The service/orchestration layer will be in charge of utilizing the openAI Api Adapter and the adapter (/UoW) for the database to provide this functionality.

Constructing the System prompt however is a domain function(/service).    
However, it will construct the system Prompt in the language of the domain model.   
It will be the task of our openaillm adapter to translate this domain model system prompt to the json format that the openaiAPI expects.    

Viewed from this angle, the domain model will always abstract away technical details to enable clearer reasoning about the behaviour of our system.    
A nice case view of how abstraction from technical details helps us to write better and way easier to test code is found in [chapter three of cosmic python](https://www.cosmicpython.com/book/chapter_03_abstractions.html)

# Our architecture patterns
At the basis of everything is clear seperation of concerns. The seperation is done vertically, along the different layers, and horizontally by seperating the domain into sub-domains/bounded contexts.  
## "Horizontal" seperation: Bounded context
Bounded contexts with Ports& adapters for communication between them
(1)Cohesion, (2)single responsibility
(1)One task should be isolated to one component
(2)-One context should have one single task that it is responsible for, not more
ToDo: better word for task -sub domain? sure: bounded context, but that needs explanation itself.




## "Vertical" seperation: Three layers & dependency injection
TOP: http layer
MIDDLE/CORE: (service & domain) layer
LOWER: data layer

MIDDLE layer (service & domain):
does not know anything about the data types of the other layers or how their adapters implement the functions defined in the service layer ports.   
Domain layer:    
The domain model functions and models are completely closed off, not utilizing any Ports/Adapters. However, there are many use cases where we want to feed data into our domain model(s) functions. That is the job of the service/orchestration layer functions. They utiilize the injected adapters of its Ports to get data from the database or other contexts and calls the domain functions with the retreived data.    
Service layer:
- Service layer is called orchestration layer, because it fulfills use cases by orchestrating adapter function calls, retreiving domain models from the database via the UoW, calling domain functions and commiting changes to the db.
- service layer fulfills uses cases by providing service functions to the http layer, with atomic types and Ports as Parameters. 
- Actual adapers are injected via a bootstrap module that is called in the http layer.

TOP: http layer
Endpoints are defined here and the dependencies are wired up in the deps.py as well.

## Details -how our code really is set up
Lets look at how the code is structured.
### Overview
```
src/
├─ contexts/
│  ├─ chat/
│  │  ├─ application/
│  │  │  ├─ ports/
│  │  │  │  ├─ conversation_repo.py
│  │  │  │  ├─ customgpt_instructions_retreiver.py
│  │  │  │  ├─ llm_client.py
│  │  │  │  └─ uow.py
│  │  │  └─ service_functions.py
│  │  ├─ domain/
│  │  │  ├─ models.py
│  │  │  └─ domain_functions.py
│  │  └─ infrastructure/
│  │     ├─ adapters/
│  │     │  └─ openai_llm.py
│  │     └─ db/
│  │        ├─ events.py
│  │        ├─ orm.py
│  │        ├─ uow_implementations.py
│  │        └─ conv_repo_implmementations.py
│  ├─ customgpt/
│  └─ knowledge/
│
├─ interface/
│  └─ http/
│     ├─ app.py
│     ├─ deps.py
│     └─ routes/
│
├─ bootstrap.py
└─ tests/
```

Let's first look at the `contexts` folder
```
src/
├─ contexts/
```  
We have divided our buisness domain into multiple bounded contexts: 
```
├─ contexts/
│  ├─ chat/
│  ├─ customgpt/
│  └─ knowledge/
```
The application, domain and data layer are at home here. Each context has its own domain-, application/service- and data-layer.

How each context is structured can be seen in the example of the chat context.    
```
│  ├─ chat/
│  │  ├─ application/
│  │  │  ├─ ports/
│  │  │  │  ├─ conversation_repo.py
│  │  │  │  ├─ customgpt_instructions_retreiver.py
│  │  │  │  ├─ llm_client.py
│  │  │  │  └─ uow.py
│  │  │  └─ service_functions.py
│  │  ├─ domain/
│  │  │  ├─ models.py
│  │  │  └─ domain_functions.py
│  │  └─ infrastructure/
│  │     ├─ adapters/
│  │     │  └─ openai_llm.py
│  │     └─ db/
│  │        ├─ events.py
│  │        ├─ orm.py
│  │        ├─ uow_implementations.py
│  │        └─ conv_repo_implmementations.py
```

The domain and application folder are the heart of the code.   
In domain, all the domain models and domain functions are found.   
Domain functions dont't interface with anything. They change domain objects or return information, but never utilize a port to get data from elsewhere.
```
├─ contexts/
│  ├─ chat/
│  │  ├─ domain/
│  │  │  ├─ models.py
│  │  │  └─ domain_functions.py
```
The part that gets data from elsewhere and implements the use-cases that our endpoints want to provide(like creating a new Conversation and utilizing the OpenAI Api to get an assistant response) is the service/orchestration layer.   
We can see it here:
```
│  │  │  ├─ ports/
│  │  │  │  ├─ conversation_repo.py <-own data layer will implement this
│  │  │  │  ├─ customgpt_instructions_retreiver.py <- CustomGPT context will implement this
│  │  │  │  ├─ llm_client.py <- will implement in same context under adapters
│  │  │  │  └─ uow.py <-own data layer will implement this
│  │  │  └─ service_functions.py
```
Every possible data input into our context can be seen in these modules.  
All the data coming from outside into the core layer will 1) either be retreived by utilizing the Ports defined here. 2) Or being passed as atomic types to service functions in service_functions.py. No other source is possible.    
(The adapter implementing these ports will be passed to the service functions, but we will see that later)
Service functions will be called by 1) our endpoints and 2) by adapters this context implements for ports of another context.

We can see (2) in the customGPT context which implements the customgpt_instructions_retreiver port of our chat context.

```
src/
├─ contexts/
│  ├─ customGPT/
│  │  ├─ application/
     ...
│  │  └─ infrastructure/
│  │     ├─ adapters/
│  │     │  └─ retreive_instructions.py <- implements customgpt_instructions_retreiver.py
```
Here is how a service functions parameter might look like. 
```
def process_sent_user_message(user_msg:str, conv_uow:ConversationUOW, cgpt_retreiver:CustomGPTInstructionsRetreiver, conv_id: str | None = None,  custom_gpt_id: str| None = None, use_rag:bool = False):
```

### Interface between service layer and data layer
We connect with the db utilizing these ports:
```
src/
├─ contexts/
│  ├─ chat/
│  │  │  ├─ ports/
│  │  │  │  ├─ conversation_repo.py
           ...
│  │  │  │  └─ uow.py
```
The repository defines all the ways we can interface with our db.
The UoW wraps the repo and takes care of session management.
### Small break-down of repo and UoW.
The service layer owns the Port of the repo.
The repo 
- uses data types native to the domain, nothing about the data layers internals are known.
- all the possible interactions with the db layer are defined here.
- domain models fetched by the repo can be changed and commited to the db if we correctly defined the mappers between the domain models and the table in the data layer
- Is initialized with a session
The problem with only using a repo is that we have manually manage the session in the service layer, breaking seperation as well as suspecticle to errors.   
Therefore, we utilize the UnitOfWork pattern, wrapping the repository in a unit of work and letting the UoW manage the session lifecycle:    
The UnitOfWork is a context manager, providing `__enter__` and `__exit__` methods for session management. 
Here is an example for illustration:
```
class SQLAlchemyConversationUOW():
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._sqla_conv_repo: SQAlchemyConversartionRepository | None
    def __enter__(self)->'SQLAlchemyConversationUOW':
        self._session = self._session_factory()
        self._sqla_conv_repo = SQAlchemyConversartionRepository(session=self._session)
        return self
    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            assert self._session is not None
            self._session.close()
            self._session = None
            self._sqla_conv_repo = None
    def commit(self):
        assert self._session is not None
        self._session.commit()
    def rollback(self):
        assert self._session is not None
        self._session.rollback()
    @property
    def conversation_repo(self)-> ConversationRepository:
        assert self._sqla_conv_repo is not None
        return self._sqla_conv_repo
```

We can utilize it by 
```
with uow:
    do_some_work
```
To see how it behaves, check out `backend/tests/integration/db/contexts/chat/test_uow.py`

Now, lets look at how we define our db and the adapters that we need to communicate with other apis.

```
│  │  └─ infrastructure/
│  │     ├─ adapters/
│  │     │  └─ openai_llm.py
│  │     └─ db/
│  │        ├─ events.py
│  │        ├─ orm.py
│  │        ├─ uow_implementations.py
│  │        └─ conv_repo_implmementations.py
```
We can see in the db folder implementations of the repository and uow ports of our service layer. Additionally we see the rest of the modules that are necessary for our db to function properly.

In the adapters section are 1) all the adapters needed for accessing other apis. In this case the openai API. 2) Additionally, adapters that are needed for accessing this context from other contexts would be found here. Though we do not have this in this context.


Lets check the whole file structure to get an overview. We have now covered everything in the contexts folder.
```
src/
├─ contexts/
│  ├─ chat/
│  │  ├─ application/
│  │  │  ├─ ports/
│  │  │  │  ├─ conversation_repo.py
│  │  │  │  ├─ customgpt_instructions_retreiver.py
│  │  │  │  ├─ llm_client.py
│  │  │  │  └─ uow.py
│  │  │  └─ service_functions.py
│  │  ├─ domain/
│  │  │  ├─ models.py
│  │  │  └─ domain_functions.py
│  │  └─ infrastructure/
│  │     ├─ adapters/
│  │     │  └─ openai_llm.py
│  │     └─ db/
│  │        ├─ events.py
│  │        ├─ orm.py
│  │        ├─ uow_implementations.py
│  │        └─ conv_repo_implmementations.py
│  ├─ customgpt/
│  └─ knowledge/
│
├─ interface/
│  └─ http/
│     ├─ app.py
│     ├─ deps.py
│     └─ routes/
│
├─ bootstrap.py
└─ tests/
```
Lets now look at our top layer, the http layer that will be used to interface with our application from a frontend. (As of now, I still use the app file in the top hierarchy in the project)
In it, we see the usual fastapi setup.
From the routes or app, we will call the endpoints of the service layer.   
The deps.py in http folder and the bootstrap.py in the top folder are the keys to one missing link: We have all these Ports and Adapters completely disconnected as of now. 
The service layer functions have Ports as Parameters, but how do the endpoints pass them fitting Adapters? This will be explained in the next section.
### Bootstrapping

We need to inject adapters for the ports that the service layer functions expect and need to retreive data from the database and other APIs. Also, we need to correctly set up our db among other things.
This is done in the following way.  
we have for a port of one component at least one other component which defines an adapter that implements this Port.

Now, our service layer functions that have a Port as a parameter need to be passed an adapter which implements this port. 

We now need to connect our adapters that are defined in some component to the service layer function calls in our http layer.   

Due to decoupling and modularity, we do not want to bake these binds into our http layer directly.

Therefore we have one more layer of abstraction: Bootstrapping, where everything gets wired up.


We have the bootstrap modules bootstrap function which initilizes (factories of) the adapters and sets up everything -like creating a sessionfactory with all the mappings and the correct db url and then creating the UoWs with this sessionfactory. It will return a bootstrap object which contains all the necessary dependencies (e.g. adapters).

```bootstrap.py
@dataclass(frozen=True)
class DependenciesContainer:
    """
    Typed factories that return **port** types, not concrete adapters.
    """
    conversation_uow_factory: Factory[ConversationUOW]

def bootstrap(
    *,
    db_url: str,
    create_schema: bool = False,  # dev/test only
) -> DependenciesContainer:
    chat_start_mappers()

    engine = _make_engine(db_url)
    SessionMaker: sessionmaker[Session] = _make_sessionmaker(engine)

    if create_schema:
        chat_metadata.create_all(engine)
        # add other contexts' metadata here if/when needed

    register_last_message_at_events(SessionMaker)

    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(SessionMaker)


    return DependenciesContainer(
        session_factory=lambda: SessionMaker(),
        conversation_uow_factory=conversation_uow_factory,
    )
```

The bootstrap function is called in the deps.py module, creating a bootstrap object with all the dependencies in it.

```deps.py
from src.bootstrap import bootstrap, DependenciesContainer

# Compose ONCE for this process (choose env-specific URL here)
deps: DependenciesContainer = bootstrap(
    db_url="sqlite:///./dev.db",
    create_schema=True,  # dev/test only
)
```

We import this object into our http layer. The http layer only knows that it contains adapters of these ports, or factories for these adapters, not the exact adapters. So the http layer is also independent of implementation details.

```app.py
from src.interface.http.deps import deps
deps: DependenciesContainer = deps

@app.get(
    "/get-chat-summaries",
    tags=["Chat"],
    response_model=list[ChatSummary],
    operation_id="getChatSummaries",)
def get_chat_summaries(
    chat_uow: ConversationUOW = Depends(deps.conversation_uow_factory), # <- accessing adapter like this
) -> list[ChatSummary]:
```