from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    KnowledgeDBQueriesPort,
)
from src.contexts.shared.typing_aliases import Factory


class KnowledgeDBQueriesSQAlchemyAdapter(KnowledgeDBQueriesPort):
    def __init__(self, chat_session_factory: Factory[Session]):
        self._session_factory = chat_session_factory
