from __future__ import annotations

from types import TracebackType
from typing import Self, Type

from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import KnowledgeRepo
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.infrastructure.db.knowledge_repo_adapter import (
    SQLAlchemyKnowledgeRepository,
)
from src.contexts.shared.typing_aliases import Factory


# Below: Not needed if we explicitly inherit Protocols -> better for typechecking
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class SQLAlchemyKnowledgeUOW(KnowledgeUOW):
    def __init__(self, session_factory: Factory[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._sqla_knowledge_repo: SQLAlchemyKnowledgeRepository | None

    def __enter__(
        self,
    ) -> Self:  # because contextmanager ->Self is better style than ->SQLAlchemyCgptUOW
        self._session = self._session_factory()
        self._sqla_knowledge_repo = SQLAlchemyKnowledgeRepository(session=self._session)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            assert self._session is not None
            self._session.close()
            self._session = None
            self._sqla_knowledge_repo = None

    def commit(self):
        assert self._session is not None
        self._session.commit()

    def rollback(self):
        assert self._session is not None
        self._session.rollback()

    @property
    def knowledge_repo(self) -> KnowledgeRepo:
        assert self._sqla_knowledge_repo is not None
        return self._sqla_knowledge_repo

    # I saw a nicer implementation strucutre with a handle exception part
