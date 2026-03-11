from sqlalchemy.orm import Session

from src.contexts.customGPTs.application.ports.customgpt_repo import (
    CgptNotFound,
    CustomGPTRepository,
)
from src.contexts.customGPTs.domain.models import CustomGPT


class SQLAlchemyCustomGPTRepository(CustomGPTRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, cgpt_id: str) -> CustomGPT:
        cgpt = self._session.get(CustomGPT, cgpt_id)
        if cgpt is None:
            raise CgptNotFound(cgpt_id)
        return cgpt

    def create_cgpt(
        self, name: str, instructions: str, description: str | None = None
    ) -> CustomGPT:
        cgpt: CustomGPT = CustomGPT(
            name=name, instructions=instructions, description=description
        )
        self._session.add(cgpt)
        return cgpt

    def delete(self, cgpt_id: str):
        cgpt = self._session.get(CustomGPT, cgpt_id)
        if cgpt is None:
            raise CgptNotFound(cgpt_id)
        self._session.delete(cgpt)


# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.
