from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    KnowledgeDBQueriesPort,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    uploaded_text_like_file,
)
from src.contexts.shared.typing_aliases import Factory


class KnowledgeDBQueriesSQAlchemyAdapter(KnowledgeDBQueriesPort):
    def __init__(self, chat_session_factory: Factory[Session]):
        self._session_factory = chat_session_factory

    def check_if_hash_already_exists(self, hash: str) -> bool:
        with self._session_factory() as session:
            stmt = select(
                uploaded_text_like_file.c.id,
            ).where(uploaded_text_like_file.c.hash_of_raw_file == hash)
            rows = session.execute(stmt).all()
            if len(rows) > 0:
                return True
            return False
