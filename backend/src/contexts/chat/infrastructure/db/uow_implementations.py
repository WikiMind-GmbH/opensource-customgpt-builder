from types import TracebackType
from typing import Type

from sqlalchemy.orm import Session

from src.contexts.chat.application.ports.chat_repo import ConversationRepository
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.db.conv_repo_implmementations import (
    SQLAlchemyConversartionRepository,
)
from src.contexts.shared.typing_aliases import Factory


# Below: Not needed if we explicitly inherit Protocols -> better for typechecking
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class SQLAlchemyConversationUOW(ConversationUOW):
    def __init__(self, session_factory: Factory[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._sqla_conv_repo: SQLAlchemyConversartionRepository | None = None

    def __enter__(self) -> "SQLAlchemyConversationUOW":
        self._session = self._session_factory()
        self._sqla_conv_repo = SQLAlchemyConversartionRepository(session=self._session)
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
            self._sqla_conv_repo = None

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()

    @property
    def conversation_repo(self) -> ConversationRepository:
        assert self._sqla_conv_repo is not None
        return self._sqla_conv_repo

    # I saw a nicer implementation strucutre with a handle exception part
