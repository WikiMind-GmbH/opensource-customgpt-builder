from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.shared.typing_aliases import Factory


class CgptPermissionCheckerAdapter(CgptPermissionCheckerPort):
    def __init__(self, cgpt_session_factory: Factory[Session]):
        self._session_factory: Factory[Session] = cgpt_session_factory

    def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> None:
        with self._session_factory() as session:
            stmt = select(custom_gpts.c.id)
            cgpts_user_has_access_to = list(session.scalars(stmt).all())
            # eturn [CustomGPTOverviewDTO(id=id, name=name) for id, name in row
        cgpt_ids_to_check_where_user_has_no_access = [
            id for id in cgpt_ids_to_check if id not in cgpts_user_has_access_to
        ]
        if cgpt_ids_to_check_where_user_has_no_access == []:
            return
        raise UserHasNoPermissionForCgptOrTheyDontExist(
            unaccessible_cgpt_ids=cgpt_ids_to_check_where_user_has_no_access
        )
