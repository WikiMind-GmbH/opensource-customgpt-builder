# tests/test_custom_gpt_repo.py
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.contexts.customGPTs.infrastructure.db.customgpt_repo_implmementations import (
    SQLAlchemyCustomGPTRepository,
)
from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts  # table
from src.contexts.shared.typing_aliases import Factory

# ⬇️ Adjust this import to wherever your repo class actually lives


def test_created_at_is_set(session_factory: Factory[Session]):
    with session_factory() as session:
        repo = SQLAlchemyCustomGPTRepository(session)

        before = datetime.now(timezone.utc) - timedelta(seconds=5)
        cgpt = repo.create_cgpt(name="A", instructions="do A")
        session.commit()
        created_at = session.execute(
            select(custom_gpts.c.created_at).where(custom_gpts.c.id == cgpt.id)
        ).scalar_one()

        assert created_at is not None, "created_at should not be NULL"

        after = datetime.now(timezone.utc) + timedelta(seconds=5)
        assert before <= created_at <= after, (
            "created_at should be set to 'now' on insert"
        )


def test_get_raises_for_nonexistent(session_factory: Factory[Session]):
    session = session_factory()
    repo = SQLAlchemyCustomGPTRepository(session)

    with pytest.raises(CgptNotFound):
        repo.get("does-not-exist")


def test_delete_removes_entity(session_factory: Factory[Session]):
    with session_factory() as session:
        repo = SQLAlchemyCustomGPTRepository(session)

        cgpt = repo.create_cgpt(name="to-delete", instructions="clean up")
        session.commit()
        cgpt_id = cgpt.id
        assert cgpt_id is not None

    with session_factory() as verification_session:
        repo = SQLAlchemyCustomGPTRepository(verification_session)
        assert repo.get(cgpt_id=cgpt_id) is not None

        repo.delete(cgpt.id)
        verification_session.commit()

        # Now it should be gone
        with pytest.raises(CgptNotFound):
            repo.get(cgpt_id=cgpt_id)
