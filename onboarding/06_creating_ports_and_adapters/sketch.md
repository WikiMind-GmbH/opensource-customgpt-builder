I do want this more in a constructed tutorial way:

So not when what has to be done, but as an introduction to learning the skill to write ports and adapters.

So a follow along/ "tutorial-exercise" -kind of.

Where there are code snippets which need to be completed.

I think about doing it either like this:

using a ipynb which contains all the relevant classes and modules snippets.

At the start we have the Port already defined. 

Then the task for the one onboarded is to write an adapter.



Then there is a cell where the adapter is input and tests are run to confirm:

The functionality that is expected is provided, the errors that are expected are thrown.



----
General to-do per new Port/adapter combo:

### Checklist
WIRING
- orchestration function which depend on this Port(or Factory of this Port) exist
- endpoints call orchestration functions with correct parameters - including Port/Port/factory
- dependencies container class has an attribute which is typed as this Port factory/ Port factory factory
- endpoints calling the orchestration function Depend on this dependenciescontainer attribute
(due to how Fastapi depends work, we need the the dependenciescontainer attribute to be  Factory[Factory[Port]] if the orchestration function needs the type Factory[Port])
- in the bootstrap function, the adapter is created (and maybe also a factory (or factory factory)) and used in the returned dependencies container
- if the adapters init needs access to env variables, the bootstrap function takes those as parameter, and in composition.py, require_env() is used to fetch the needed env variable to pass it to the bootstrap() function

MAPPERS INTERFACE
- An exception handler module for this Port is created which maps the Port errors to http errors

MAPPERS APPLICATION
- If applicable, there is a mapper which maps between DTOs and domain data classes

TESTING
- A unit test for the adapter exists which checks functionality incl. custom errors be thrown correctly
- for orchestration layer tests, either the adapter is used (created in conftest) or a fake Adapter was created in the folder `backend/tests/fake_adapters` and used instead
- for e2e integration tests, the previous adapter is used -except if it utilizes a costing external api, where now a fake adapter is used that exists in `backend/tests/fake_adapters`

# All parts making an adapter work

## Wiring
An adapter implements a specific Port. 
Our orchestration function parameters are never typed with Adapter Classes, but Port Classes
In our interface layer, the adapter can get injected into the endpoint function because it is in the dependenciescontainer object created in `composition.py`.
Because of that, we can pass it to the orchestration function that expects a parameter typed as the corresponding Port.

BOOTSTRAP
```py
def bootstrap(some_variables)-> DependenciesContainer:
    def cgpt_uow_factory() -> CgptUOW:
            return SQLAlchemyCgptUOW(sessionFactory_CGPT)
    return DependenciesContainer(
        cgpt_uow_factory=cgpt_uow_factory,
        ...
    )
```

COMPOSITION
```py
from src.bootstrap import DependenciesContainer, bootstrap
from backend_spanning_helpers import require_env

dependencies_container: DependenciesContainer = bootstrap(some_variable = require_env("SOME_VARIABLE"))
```

ROUTER
 ```py
from src.interface.http.composition import dependencies_container

 dependencies_container: DependenciesContainer = dependencies_container

 @customgpt_commands_router.post(
    "/create-custom-gpt",
    operation_id="createCustomGpt",
)
def create_custom_gpt(
    custom_gpt_infos: CustomGptToCreate,
    uow_factory: Annotated[
        Factory[CgptUOW],
        Depends(dependencies_container.cgpt_uow_factory_factory), #<- injecting the adapter
    ],
) -> CommandResult:
    result = some_function(uow_factory) #<- orchestration function is parameterized with this adapter
```

## Changing the wiring 
If we want to change the adapter for a specific port that our app is using to another one, we need to change the wiring:
Our dependenciescontainer object created in composition.py now needs the attribute of the corresponding Port to be using the other adapter, therefore we need to change the bootstrap function. 
E.g.
From
```py
def bootstrap(some_variables)-> DependenciesContainer:
    def cgpt_uow_factory() -> CgptUOW:
            return SQLAlchemyCgptUOW(sessionFactory_CGPT)
    return DependenciesContainer(
        cgpt_uow_factory=cgpt_uow_factory,
        ...
    )
```
to 
```py
def bootstrap(some_variables)-> DependenciesContainer:
    def cgpt_uow_factory_different() -> CgptUOW:
            return AnotherUow(sessionFactory_CGPT)
    return DependenciesContainer(
        cgpt_uow_factory=cgpt_uow_factory_different,
        ...
    )
```

No changes are needed to be made in the orchestration functions or the endpoint functions.
## Tests related to a specific adapter
### Testing the adapter itself
Testing is central to how we keep our app maintainable.
For each adapter, there is at least one unit test module.
There are two types of test modules which focus soley on a specific adapter:
1. adapter specific tests
2. adapter agnostic tests, which function similar to orchestration functions, working soley with the functions defined by the Port of the adapter. The specific adapter is then 'injected' by the pytest fixture.
If the adapter uses a live db, these types of tests can be found in the integration-tests folder, otherwise in the unit test folder.

### orchestration layer tests utililizing either the adapter or a fake
Orchestratino function test should focus on the orchestration function and should best not depend on a specific adapter working which implements the port, especially if those depend on external infrastructure like databases.
There, we want to use Fake Adapters instead of real ones for testing service functions.
```py
class FakeVectorStoreTextChunksAdapter(VectorStorePortTextChunks):
    def __init__(self, embedding_dimension: int) -> None:
        if embedding_dimension <= 0:
            raise InvalidEmbeddingDimension(
                f"Embedding dimension must be positive, got {embedding_dimension}."
            )

        self._embedding_dimension = embedding_dimension
        self._chunks: dict[UUID, ChunkEmbeddingAndMetadataDTO] = {}

    @property
    def collection_name(self) -> str:
        return "fake_collection"

    @property
    def embedding_dimension(self) -> int:
        return self._embedding_dimension

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[UUID],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]:
        if len(embedding_to_match) != self._embedding_dimension:
            raise InvalidEmbeddingDimension(
                f"Expected embedding dimension {self._embedding_dimension}, "
                f"got {len(embedding_to_match)}."
            )

        matching_chunks = [
            dto
            for dto in self._chunks.values()
            if dto.metadata.id_of_corresponding_file in file_ids_to_include_in_filter
            and (
                include_only_parent_or_child_chunks is None
                or dto.metadata.parent_or_child_chunk
                == include_only_parent_or_child_chunks
            )
        ]

        return [
            TextChunkReturnDTO(
                id_of_chunk=dto.id_of_chunk,
                score=1.0,
            )
            for dto in matching_chunks[:max_snippets]
        ]
    ...
```
Creating fakes is also helpful if we want to force a specific responses from adapters. To get a specific response from our real adapters, we would need to guarantee specific conditions (e.g. database state) which lead to the desired result.   
With a Fake adapter, we can get the desired results way more simple.

```py
class FakeCgptPermissionChecker(CgptPermissionCheckerPort):
    def __init__(self, will_raise_error: bool) -> None:
        self._will_raise_error = will_raise_error

    def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> None:
        if self._will_raise_error:
            raise UserHasNoPermissionForCgptOrTheyDontExist(
                unaccessible_cgpt_ids=cgpt_ids_to_check
            )
```
If we want to simulate a use case where the user (has/has not) access to the cgpts, we use this adapter initialized with (True/False). Using the real adapter would necessitate a connection to a real db and creating according database entries.


However, sometimes adapters (who do not depend on externals like databases) are so simple that the positive of avoiding errors introduced by using real adapters is not there, as a fake would be of similar complexity and therefore similarly prone to errors.

In this case, we might want to skip the overhead of creating a Fake adapter and use a real adapter. 
```py
@pytest.fixture()
def extract_text_from_document_adapter() -> ExtractTextFromDocumentPort:
    return ExtractTextFromDocumentsAdapter() #<-As of now, only capable of extracting txt from txt files -> easy


```
##### Pytest fixtures clean up for I/O persistance like DB/FileSystem
Additionally, for adapters with I/O (e.g. to dbs or the local file system), we want to add to the fixture providing the adapter also a clean up functionality to reset the state after each test.
```py
@pytest.fixture()
def file_store(tmp_path: Path) -> RawFileStoreLocalFsAdapter:
    # pytest's built-in tmp_path fixture provides a unique temporary directory
    # per test and cleans it up automatically.

    return RawFileStoreLocalFsAdapter(file_storage_folder=tmp_path)
```

This is especially true for integration testing our sql database related adapters like the repo or uow.
```py
@pytest.fixture(scope="session")
def engine(start_knowledge_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine(
        require_env("DB_URL_KNOWLEDGE_TEST"), poolclass=NullPool
    )  # No connection pooling
    knowledge_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> Generator[sessionmaker[Session], None, None]:
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()


@pytest.fixture()
def knowledge_uow_factory(session_factory: sessionmaker[Session]):
    return lambda: SQLAlchemyKnowledgeUOW(session_factory=session_factory)
```


#### e2e tests



### Writing a new Port
First determine: is the functionality best fit inside a port or does it belong to the domain?
1. Best fit for a port (external api, providing non-domain-specific functionality) and not for a domain function
2. Create functions & errors, function names must best explain the functionality by themselves and be rather long and explainy: `get_chunks_assert_all_unique_and_exist`, add via comments which errors should be thrown by  a function if not self explanatory
3. If a function returns more than atomic types, create DTO dataclasses for function returns (and parameters if atomic types are not feasible). If there is a corresponding datastructure in the domain, create a mapper function for translation

### Addendum
state based vs non state-based adapters
orm based db - extra is needed

notebook one:
Port is defined, there is already an existing adapter
-> we therefore already have:
The dependenciescontainer already has an attribute of this port type, endpoints and orchestration and every consumer is already correctly wired up with this.
Tests are either already configured with this adapter or a Fake adapter is already created

