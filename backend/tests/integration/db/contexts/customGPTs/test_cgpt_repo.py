# tests/test_custom_gpt_repo.py
from datetime import datetime, timedelta, timezone

from src.contexts.customGPTs.application.exceptions import CGPTNonExistentError
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.customGPTs.infrastructure.db.customgpt_repo_implmementations import SQAlchemyCustomGPTRepository
import pytest
from sqlalchemy import select, update

from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts  # table
# ⬇️ Adjust this import to wherever your repo class actually lives


def test_created_at_is_set(session_factory):
    session = session_factory()
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
    assert before <= created_at_cmp <= after, "created_at should be set to 'now' on insert"

# Adjust the following test to utilize the new query
# def test_list_overviews_is_ordered_by_created_at_desc(session_factory, engine):
#     """
#     We create 3 rows, then set their created_at explicitly so ordering is deterministic.
#     Then we assert the repository returns them in DESC order by created_at.
#     """
#     session = session_factory()
#     repo = SQAlchemyCustomGPTRepository(session)

#     # create three entities (ids come from your domain model)
#     first = repo.create_cgpt(name="first", instructions="i1")
#     second = repo.create_cgpt(name="second", instructions="i2")
#     third = repo.create_cgpt(name="third", instructions="i3")
#     session.commit()

#     # Explicit timestamps for determinism
#     t1 = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
#     t2 = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
#     t3 = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

#     # Update created_at via Core (works regardless of ORM defaults)
#     with engine.begin() as conn:
#         conn.execute(
#             update(custom_gpts)
#             .where(custom_gpts.c.id == first.id)
#             .values(created_at=t1)
#         )
#         conn.execute(
#             update(custom_gpts)
#             .where(custom_gpts.c.id == second.id)
#             .values(created_at=t2)
#         )
#         conn.execute(
#             update(custom_gpts)
#             .where(custom_gpts.c.id == third.id)
#             .values(created_at=t3)
#         )

#     # Now call the repo method and check order: third (t3), second (t2), first (t1)
#     overviews = repo.list_all_overviews_ordered_by_created()
#     ordered_ids = [o.id for o in overviews]
#     assert ordered_ids == [third.id, second.id, first.id]


def test_get_raises_for_nonexistent(session_factory):
    session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)

    with pytest.raises(CGPTNonExistentError):
        repo.get("does-not-exist")


def test_delete_removes_entity(session_factory):
    session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)

    cgpt = repo.create_cgpt(name="to-delete", instructions="clean up")
    session.commit()

    # Ensure it's there
    assert session.get(CustomGPT, cgpt.id) is not None

    repo.delete(cgpt)
    session.commit()

    # Now it should be gone
    assert session.get(CustomGPT, cgpt.id) is None
