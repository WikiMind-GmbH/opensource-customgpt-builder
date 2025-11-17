from __future__ import annotations
from typing import Callable, Self, runtime_checkable

from sqlalchemy.orm import Session
from src.contexts.shared.typing_aliases import Factory
from src.contexts.customGPTs.application.ports.customgpt_repo import CustomGPTRepository
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.db.customgpt_repo_implmementations import SQAlchemyCustomGPTRepository

# Below: Not needed if we explicitly inherit Protocols -> better for typechecking
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class SQLAlchemyCgptUOW(CgptUOW):
    def __init__(self, session_factory: Factory[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._sqla_cgpt_repo: SQAlchemyCustomGPTRepository | None
    def __enter__(self)->Self: #because contextmanager ->Self is better style than ->SQLAlchemyCgptUOW
        self._session = self._session_factory()
        self._sqla_cgpt_repo = SQAlchemyCustomGPTRepository(session=self._session)
        return self
    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            assert self._session is not None
            self._session.close()
            self._session = None
            self._sqla_cgpt_repo = None
    def commit(self):
        assert self._session is not None
        self._session.commit()
    def rollback(self):
        assert self._session is not None
        self._session.rollback()
    @property
    def cgpt_repo(self)-> CustomGPTRepository:
        assert self._sqla_cgpt_repo is not None
        return self._sqla_cgpt_repo

    # I saw a nicer implementation strucutre with a handle exception part