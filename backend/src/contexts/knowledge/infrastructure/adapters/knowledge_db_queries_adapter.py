from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.mappers import KnowledgeDBQueriesMapper
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentOverviewDTO,
    DocumentStatusDTO,
    FileCgptAssociationsDTO,
    KnowledgeDBQueriesPort,
    NotFoundError,
)
from src.contexts.knowledge.domain.models import UploadedTextLikeFile
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    document_deletion_jobs,
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

    def get_documents_for_cgpt(self, cgpt_id: str) -> list[DocumentOverviewDTO]:
        with self._session_factory() as session:
            stmt = (
                select(UploadedTextLikeFile)
                .join(
                    cgpt_permissions_to_files,
                    cgpt_permissions_to_files.c.file_id
                    == uploaded_text_like_file.c._id,
                )
                .where(cgpt_permissions_to_files.c.cgpt_id == cgpt_id)
                .order_by(
                    uploaded_text_like_file.c._name, uploaded_text_like_file.c._id
                )
            )
            documents = list(session.scalars(stmt).all())
            return [
                KnowledgeDBQueriesMapper.document_overview_domain_to_dto(document)
                for document in documents
            ]

    def get_file_cgpt_associations(self) -> list[FileCgptAssociationsDTO]:
        with self._session_factory() as session:
            stmt = (
                select(
                    uploaded_text_like_file.c._id,
                    cgpt_permissions_to_files.c.cgpt_id,
                )
                .outerjoin(
                    cgpt_permissions_to_files,
                    cgpt_permissions_to_files.c.file_id
                    == uploaded_text_like_file.c._id,
                )
                .where(
                    ~exists(
                        select(document_deletion_jobs.c.file_id).where(
                            document_deletion_jobs.c.file_id
                            == uploaded_text_like_file.c._id
                        )
                    )
                )
                .order_by(
                    uploaded_text_like_file.c._id,
                    cgpt_permissions_to_files.c.cgpt_id,
                )
            )
            rows = session.execute(stmt).all()

        cgpt_ids_by_file_id: dict[UUID, list[str]] = {}
        for file_id, cgpt_id in rows:
            cgpt_ids = cgpt_ids_by_file_id.setdefault(file_id, [])
            if cgpt_id is not None:
                cgpt_ids.append(cgpt_id)

        return [
            FileCgptAssociationsDTO(file_id=file_id, cgpt_ids=cgpt_ids)
            for file_id, cgpt_ids in cgpt_ids_by_file_id.items()
        ]
