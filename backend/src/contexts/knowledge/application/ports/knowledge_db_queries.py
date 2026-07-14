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


class KnowledgeDBQueriesPort(Protocol):
    def check_status_of_document(
        self, document_id: UUID, cgpt_id: str
    ) -> DocumentStatusDTO: ...
