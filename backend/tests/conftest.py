import pytest
from sqlalchemy.orm import clear_mappers
from src.contexts.chat.infrastructure.db.orm import start_mappers as chat_start
from src.contexts.customGPTs.infrastructure.db.orm import start_mappers as cgpt_start

@pytest.fixture(scope="session", autouse=True)
def start_all_mappers():
    chat_start()
    cgpt_start()
    yield
    clear_mappers()