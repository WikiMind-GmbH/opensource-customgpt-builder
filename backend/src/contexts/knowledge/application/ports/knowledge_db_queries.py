from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class NotFoundError(RuntimeError):
    "The document does not exist or is not associated with the supplied custom GPT."


class DocumentStatusDTO(StrEnum):
    initialized = "initialized"
    raw_document_was_stored = "raw_document_was_stored"
    text_extracted_but_not_chunked = "text_extracted_but_not_chunked"
    chunked_but_not_embedded = "chunked_but_not_embedded"
    chunks_embedded_and_ready = "chunks_embedded_and_ready"


@dataclass(frozen=True)
class DocumentOverviewDTO:
    document_id: UUID
    name: str
    file_type: str
    status: DocumentStatusDTO


@dataclass(frozen=True)
class FileCgptAssociationsDTO:
    file_id: UUID
    cgpt_ids: list[str]


class KnowledgeDBQueriesPort(Protocol):
    def check_status_of_document(
        self, document_id: UUID, cgpt_id: str
    ) -> DocumentStatusDTO: ...
    def get_documents_for_cgpt(self, cgpt_id: str) -> list[DocumentOverviewDTO]: ...
    def get_file_cgpt_associations(self) -> list[FileCgptAssociationsDTO]: ...
