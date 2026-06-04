from enum import StrEnum
from typing import Protocol


class DocumentStatus(StrEnum):
    non_existing = "non_existing"
    initialized = "initialized"
    raw_document_was_stored = "raw_document_was_stored"
    chunked_but_not_embedded = "chunked_but_not_embedded"
    chunks_embedded_and_ready = "chunks_embedded_and_ready"


class KnowledgeDBQueriesPort(Protocol):
    def check_status_of_document(
        self, doc_id: str, cgpt_id_for_permission_check: str
    ) -> DocumentStatus: ...
