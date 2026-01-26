import pytest
from sqlalchemy.orm import Session

from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Factory


@pytest.fixture()
def create_cgpt_return_id(session_factory: Factory[Session]) -> str:
    name: str = "alpha"
    instruction: str = "do x"
    description: str = "desc"
    with SQLAlchemyCgptUOW(session_factory) as uow:
        cgpt = uow.cgpt_repo.create_cgpt(
            name=name, instructions=instruction, description=description
        )
        cgpt_id = cgpt.id
        uow.commit()
    return cgpt_id
