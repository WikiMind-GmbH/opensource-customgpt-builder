from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.mappers import KnowledgeDBQueriesMapper
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentStatusDTO,
    KnowledgeDBQueriesPort,
    NotFoundError,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    uploaded_text_like_file,
)
from src.contexts.shared.typing_aliases import Factory


class KnowledgeDBQueriesSQAlchemyAdapter(KnowledgeDBQueriesPort):
    def __init__(self, knowledge_session_factory: Factory[Session]):
        self._session_factory = knowledge_session_factory

    def check_status_of_document(
        self, document_id: UUID, cgpt_id: str
    ) -> DocumentStatusDTO:
        with self._session_factory() as session:
            stmt = (
                select(uploaded_text_like_file.c._status)
                .join(
                    cgpt_permissions_to_files,
                    cgpt_permissions_to_files.c.file_id
                    == uploaded_text_like_file.c._id,
                )
                .where(
                    uploaded_text_like_file.c._id == document_id,
                    cgpt_permissions_to_files.c.cgpt_id == cgpt_id,
                )
            )
            status = session.execute(stmt).scalar_one_or_none()

        if status is None:
            raise NotFoundError(
                f"Document {document_id} was not found for custom GPT {cgpt_id}"
            )
        return KnowledgeDBQueriesMapper.document_status_domain_to_dto(status)
