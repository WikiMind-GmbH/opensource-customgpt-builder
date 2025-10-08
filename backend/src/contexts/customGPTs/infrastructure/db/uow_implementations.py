from typing import Callable, runtime_checkable

from sqlalchemy.orm import Session
from chat.infrastructure.db.conv_repo_implmementations import SQAlchemyConversartionRepository
from chat.application.ports.conversation_repo import ConversationRepository

# Below: Not needed if we explicitly inherit Protocols -> better for typechecking 
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class SQLAlchemyConversationUOW():
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._sqla_conv_repo: SQAlchemyConversartionRepository | None
    def __enter__(self)->'SQLAlchemyConversationUOW':
        self._session = self._session_factory()
        self._sqla_conv_repo = SQAlchemyConversartionRepository(session=self._session)
        return self
    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            assert self._session is not None
            self._session.close()
            self._session = None
            self._conversations = None
    def commit(self):
        assert self._session is not None
        self._session.commit()
    def rollback(self):
        assert self._session is not None
        self._session.rollback()
    @property
    def conversation_repo(self)-> ConversationRepository:
        assert self._sqla_conv_repo is not None
        return self._sqla_conv_repo

    # I saw a nicer implementation strucutre with a handle exception part