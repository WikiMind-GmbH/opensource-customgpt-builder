from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.customGPTs.application.ports.cgpt_queries import (
    CgptQueries,
    CustomGPTInfosDTO,
    CustomGPTOverviewDTO,
    MappingError,
    NotFoundError,
    QueryError,
)
from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts
from src.contexts.shared.typing_aliases import Factory


class CgptQueriesImplementation(CgptQueries):
    def __init__(self, cgpt_session_factory: Factory[Session]):
        self._session_factory: Factory[Session] = cgpt_session_factory

    def get_custom_gpt_overviews_ordered_by_created_at(
        self,
    ) -> list[CustomGPTOverviewDTO]:
        with self._session_factory() as session:
            stmt = (
                select(custom_gpts.c.id, custom_gpts.c.name).order_by(
                    custom_gpts.c.created_at.desc()
                )  # <- core style working with tables
            )
            rows = session.execute(stmt).all()
            return [CustomGPTOverviewDTO(id=id, name=name) for id, name in rows]

    def get_custom_gpt_infos(self, cgpt_id: str) -> CustomGPTInfosDTO:
        with self._session_factory() as session:
            try:
                stmt = (
                    select(
                        custom_gpts.c.id,
                        custom_gpts.c.name,
                        custom_gpts.c.instructions,
                        custom_gpts.c.description,
                    ).where(
                        custom_gpts.c.id == cgpt_id
                    )  # <- core style working with tables
                )
                row = session.execute(stmt).one_or_none()
                if row is None:
                    raise NotFoundError(f"Cgpt with id {cgpt_id} was not found")
                try:
                    row_mapped = row._mapping
                    return CustomGPTInfosDTO(
                        id=row_mapped.id,
                        name=row_mapped.name,
                        instructions=row_mapped.instructions,
                        description=row_mapped.description,
                    )
                except Exception as e:
                    raise MappingError("Couldn't map the row {row}") from e
            except Exception as e:
                raise QueryError(f"Error when querying for cgpt {cgpt_id}") from e
