# tests/test_cgpt_uow.py
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from src.contexts.customGPTs.infrastructure.adapters.cgpt_permissions_adapter import (
    CgptPermissionCheckerAdapter,
)
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.shared.typing_aliases import Factory


def test_returns_true_if_cgpt_exists(cgpt_session_factory: Factory[Session]):
    # create & commit via repo on the UoW
    name: str = "alpha"
    instruction: str = "do x"
    description: str = "desc"
    with SQLAlchemyCgptUOW(cgpt_session_factory) as uow:
        cgpt = uow.cgpt_repo.create_cgpt(
            name=name, instructions=instruction, description=description
        )
        cgpt_id = cgpt.id
        uow.commit()

    checker = CgptPermissionCheckerAdapter(cgpt_session_factory=cgpt_session_factory)

    checker.assure_user_has_access_to_cgpts(cgpt_ids_to_check=[cgpt_id])
    with pytest.raises(UserHasNoPermissionForCgptOrTheyDontExist):
        checker.assure_user_has_access_to_cgpts(cgpt_ids_to_check=["I_dont_exist"])
