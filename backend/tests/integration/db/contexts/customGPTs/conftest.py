from src.contexts.customGPTs.infrastructure.db.uow_implementations import SQLAlchemyCgptUOW
from src.contexts.customGPTs.infrastructure.db.orm import start_mappers
from src.contexts.customGPTs.infrastructure.db.orm import metadata
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, clear_mappers
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

# @pytest.fixture()
# def uow_factory(session_factory):
#     # fresh UoW per test
#     return lambda: SQLAlchemyCgptUOW(session_factory)
