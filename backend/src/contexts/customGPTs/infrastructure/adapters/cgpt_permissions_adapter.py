from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
    EmptyListToCheckPassedError,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.shared.typing_aliases import Factory
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.CUSTOMGPTS, component="cgpt_permission_adapter"
)


class CgptPermissionCheckerAdapter(CgptPermissionCheckerPort):
    def __init__(self, cgpt_session_factory: Factory[Session]):
        self._session_factory: Factory[Session] = cgpt_session_factory

    def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> None:
        if len(cgpt_ids_to_check) == 0:
            logger.warning("No CGPT ids to check")
            raise EmptyListToCheckPassedError
        with self._session_factory() as session:
            stmt = select(custom_gpts.c.id)
            cgpts_user_has_access_to = list(session.scalars(stmt).all())
            # eturn [CustomGPTOverviewDTO(id=id, name=name) for id, name in row
        cgpt_ids_to_check_where_user_has_no_access = [
            id for id in cgpt_ids_to_check if id not in cgpts_user_has_access_to
        ]
        if cgpt_ids_to_check_where_user_has_no_access == []:
            logger.debug(
                "CGPT permission check passed cgpt_ids=%s",
                cgpt_ids_to_check,
            )
            return
        logger.warning(
            "CGPT permission check failed inaccessible_cgpt_ids=%s requested_cgpt_ids=%s",
            cgpt_ids_to_check_where_user_has_no_access,
            cgpt_ids_to_check,
        )
        raise UserHasNoPermissionForCgptOrTheyDontExist(
            unaccessible_cgpt_ids=cgpt_ids_to_check_where_user_has_no_access
        )
