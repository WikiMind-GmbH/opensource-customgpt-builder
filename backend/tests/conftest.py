import pytest
from sqlalchemy.orm import clear_mappers
from src.contexts.chat.infrastructure.db.orm import start_mappers as chat_start
from src.contexts.customGPTs.infrastructure.db.orm import start_mappers as cgpt_start

@pytest.fixture(scope="session")
def start_cgpt_mappers():
    cgpt_start()
    yield

@pytest.fixture(scope="session")
def start_chat_mappers():
    chat_start()
    yield

@pytest.fixture(scope="session", autouse=True)
def _clear_mappers_at_end():
    # not autouse? then just depend on it from a top-level fixture
    yield
    clear_mappers()