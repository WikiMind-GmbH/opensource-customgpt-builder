import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.customGPTs.infrastructure.db.orm import metadata
from src.contexts.shared.typing_aliases import Factory


@pytest.fixture()
def engine(start_cgpt_mappers):
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine) -> Factory[Session]:
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory
