# tests/test_cgpt_uow.py
from __future__ import annotations
from src.contexts.shared.typing_aliases import Factory
import pytest
from sqlalchemy.orm import Session
from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.contexts.customGPTs.infrastructure.db.uow_implementations import SQLAlchemyCgptUOW


def test_uow_commit_persists(session_factory: Factory[Session]):
    # create & commit via repo on the UoW
    name: str ="alpha"
    instruction: str ="do x"
    description: str ="desc"
    with SQLAlchemyCgptUOW(session_factory) as uow:
        cgpt = uow.cgpt_repo.create_cgpt(name=name, instructions=instruction, description=description)
        cgpt_id = cgpt.id
        uow.commit()

    # new UoW / new Session → the row must be there
    with SQLAlchemyCgptUOW(session_factory) as uow2:
        got = uow2.cgpt_repo.get(cgpt_id)
        assert got is not None
        assert got.id == cgpt_id
        assert got.instructions == instruction
        assert got.id == cgpt_id
        # (optional sanity checks)
        # assert got.name == "alpha"

def test_uow_rollback_on_exception(session_factory: Factory[Session]):
    with pytest.raises(RuntimeError):
        with SQLAlchemyCgptUOW(session_factory) as uow:
            cgpt = uow.cgpt_repo.create_cgpt(name="beta", instructions="do y")
            cgpt_id = cgpt.id
            # cause an exception before commit → __exit__ should rollback
            raise RuntimeError("boom")

    # After rollback, that id should not exist
    with SQLAlchemyCgptUOW(session_factory) as uow2:
        with pytest.raises(CgptNotFound):
            uow2.cgpt_repo.get(cgpt_id)  # type: ignore[name-defined]  # created in the with-block above
            # (the exception is the assertion that rollback actually happened)


def test_uow_reinitializes_after_context_exit(session_factory: Factory[Session]):
    uow = SQLAlchemyCgptUOW(session_factory)

    # first use
    with uow as tx:
        assert tx.cgpt_repo is not None
        assert getattr(tx, "_session") is not None
    # after exit, internals should be cleared (no leaks)
    assert getattr(uow, "_session") is None
    assert getattr(uow, "_sqla_cgpt_repo") is None

    # reuse the *same* UoW instance; it should open a fresh session and work
    with uow as tx2:
        cgpt = tx2.cgpt_repo.create_cgpt(name="gamma", instructions="do z")
        tx2.commit()
        # basic sanity: we can read it back in the same context
        got = tx2.cgpt_repo.get(cgpt.id)
        assert got.id == cgpt.id
