
from datetime import datetime, timezone

from sqlalchemy import Engine, update
from src.contexts.customGPTs.application.ports.cgpt_queries import CustomGPTInfosDTO
from src.contexts.customGPTs.infrastructure.db.customgpt_repo_implmementations import SQAlchemyCustomGPTRepository
from src.contexts.shared.typing_aliases import Factory
from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts
from sqlalchemy.orm import Session
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import CgptQueriesImplementation
def test_get_overviews(session_factory: Factory[Session], engine:Engine, cgpt_query_factory:Factory[CgptQueriesImplementation]):
    """
    We create 3 rows, then set their created_at explicitly so ordering is deterministic.
    Then we assert the repository returns them in DESC order by created_at.
    """
    session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)

    # create three entities (ids come from your domain model)
    first = repo.create_cgpt(name="first", instructions="i1")
    second = repo.create_cgpt(name="second", instructions="i2")
    third = repo.create_cgpt(name="third", instructions="i3")
    session.commit()

    # Explicit timestamps for determinism
    t1 = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    t3 = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    # Update created_at via Core (works regardless of ORM defaults)
    with engine.begin() as conn:
        conn.execute(
            update(custom_gpts)
            .where(custom_gpts.c.id == first.id)
            .values(created_at=t1)
        )
        conn.execute(
            update(custom_gpts)
            .where(custom_gpts.c.id == second.id)
            .values(created_at=t2)
        )
        conn.execute(
            update(custom_gpts)
            .where(custom_gpts.c.id == third.id)
            .values(created_at=t3)
        )

    # Now call the repo method and check order: third (t3), second (t2), first (t1)
    overviews = cgpt_query_factory().get_custom_gpt_overviews_ordered_by_created_at()
    ordered_ids = [o.id for o in overviews]
    assert ordered_ids == [third.id, second.id, first.id]

def test_get_custom_gpt_infos(session_factory: Factory[Session], engine:Engine, cgpt_query_factory:Factory[CgptQueriesImplementation]):
    session = session_factory()
    repo = SQAlchemyCustomGPTRepository(session)
    name = "name"
    description = "description"
    instructions = "instructions"

    # create three entities (ids come from your domain model)
    first = repo.create_cgpt(name=name, instructions=instructions, description=description)
    id = first.id
    cgpt_first:CustomGPTInfosDTO = cgpt_query_factory().get_custom_gpt_infos(id)
    assert cgpt_first.id == id
    assert cgpt_first.instructions == instructions
    assert cgpt_first.description == description
