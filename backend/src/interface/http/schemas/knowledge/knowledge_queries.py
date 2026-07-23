from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class DocumentStatusSchema(StrEnum):
    initialized = "initialized"
    raw_document_was_stored = "raw_document_was_stored"
    text_extracted_but_not_chunked = "text_extracted_but_not_chunked"
    chunked_but_not_embedded = "chunked_but_not_embedded"
    chunks_embedded_and_ready = "chunks_embedded_and_ready"


class DocumentOverview(BaseModel):
    document_id: UUID
    name: str
    file_type: str
    status: DocumentStatusSchema


class FileCgptAssociations(BaseModel):
    file_id: UUID
    cgpt_ids: list[str]
