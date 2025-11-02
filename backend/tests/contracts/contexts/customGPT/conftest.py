from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import CgptQueriesImplementation
from src.contexts.customGPTs.infrastructure.db.orm import start_mappers
from src.contexts.customGPTs.infrastructure.db.orm import metadata
from src.contexts.shared.typing_aliases import Factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers, Session
import pytest

# If the below leads to errors, consider refactoring with the following:
@pytest.fixture(scope="session")
def mappers():
    start_mappers()
    yield
    clear_mappers() # Can't call start_mappers multiple times in same runtime! (without this)

@pytest.fixture()
def engine(mappers):
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def session_factory(engine):
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory

@pytest.fixture()
def cgpt_query_factory(session_factory: Factory[Session])-> Factory[CgptQueriesImplementation]:
    # fresh UoW per test
    return lambda: CgptQueriesImplementation(cgpt_session_factory = session_factory)

