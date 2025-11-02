from src.contexts.shared.typing_aliases import Factory
from src.contexts.customGPTs.infrastructure.db.orm import metadata
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, Session
import pytest

@pytest.fixture()
def engine(start_cgpt_mappers):
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def session_factory(engine)-> Factory[Session]:
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory

