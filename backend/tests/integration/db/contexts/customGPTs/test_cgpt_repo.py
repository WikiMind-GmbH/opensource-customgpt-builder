# tests/test_custom_gpt_repo.py
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.contexts.customGPTs.infrastructure.db.customgpt_repo_implmementations import (
    SQAlchemyCustomGPTRepository,
)
from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts  # table
from src.contexts.shared.typing_aliases import Factory

# ⬇️ Adjust this import to wherever your repo class actually lives


def test_created_at_is_set(session_factory: Factory[Session]):
    session: Session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)

    before = datetime.utcnow() - timedelta(seconds=5)
    cgpt = repo.create_cgpt(name="A", instructions="do A")
    session.commit()
    created_at = session.execute(
        select(custom_gpts.c.created_at).where(custom_gpts.c.id == cgpt.id)
    ).scalar_one()

    assert created_at is not None, "created_at should not be NULL"

    # Normalize for comparison: if tz-aware, convert to naive UTC
    if getattr(created_at, "tzinfo", None) is not None:
        created_at_cmp = created_at.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        created_at_cmp = created_at

    after = datetime.utcnow() + timedelta(seconds=5)
    assert before <= created_at_cmp <= after, (
        "created_at should be set to 'now' on insert"
    )


def test_get_raises_for_nonexistent(session_factory: Factory[Session]):
    session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)

    with pytest.raises(CgptNotFound):
        repo.get("does-not-exist")


def test_delete_removes_entity(session_factory: Factory[Session]):
    with session_factory() as session:
        repo = SQAlchemyCustomGPTRepository(session)

        cgpt = repo.create_cgpt(name="to-delete", instructions="clean up")
        session.commit()
        cgpt_id = cgpt.id
        assert cgpt_id is not None

    with session_factory() as verification_session:
        repo = SQAlchemyCustomGPTRepository(verification_session)
        assert repo.get(cgpt_id=cgpt_id) is not None

        repo.delete(cgpt.id)
        verification_session.commit()

        # Now it should be gone
        with pytest.raises(CgptNotFound):
            repo.get(cgpt_id=cgpt_id)
