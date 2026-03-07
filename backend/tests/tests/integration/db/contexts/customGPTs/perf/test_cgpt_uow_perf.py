from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Benchmark, Factory


def retreive_cgpt(session_factory: Factory[Session], cgpt_id: str):
    with SQLAlchemyCgptUOW(session_factory) as uow2:
        got = uow2.cgpt_repo.get(cgpt_id)
        return got


@pytest.mark.performance
@pytest.mark.benchmark(
    group="group-name",
    min_time=0.1,
    max_time=0.5,
    min_rounds=10,
    disable_gc=True,
    warmup=False,
)
def test_cgpt_retreival(
    session_factory: Factory[Session], create_cgpt_return_id: str, benchmark: Benchmark
):
    cgpt_id = create_cgpt_return_id
    got = benchmark(retreive_cgpt, session_factory, cgpt_id)
    assert got is not None
    assert got.id == create_cgpt_return_id
