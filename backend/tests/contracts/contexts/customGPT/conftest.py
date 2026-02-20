from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import (
    CgptQueriesImplementation,
)
from src.contexts.customGPTs.infrastructure.db.orm import metadata
from src.contexts.shared.typing_aliases import Factory


@pytest.fixture()
def engine(start_cgpt_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> sessionmaker[Session]:
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory


@pytest.fixture()
def cgpt_query_factory(
    session_factory: sessionmaker[Session],
) -> Factory[CgptQueriesImplementation]:
    # fresh UoW per test
    return lambda: CgptQueriesImplementation(cgpt_session_factory=session_factory)
