from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)
from src.contexts.knowledge.application.orchestration_use_cases.retrieve_relevant_doc_snippets_use_case import (
    retrieve_doc_snippets,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.shared.typing_aliases import Factory


class RetrieveRelevantDocSnippetsAdapter(RelevantDocSnippetRetreiverPort):
    def __init__(
        self,
        vector_store: VectorStorePortTextChunks,
        cgpt_permission_checker: CgptPermissionCheckerPort,
        embedding_generator: EmbeddingGeneratorPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
    ) -> None:
        self._vector_store = vector_store
        self._cgpt_permission_checker = cgpt_permission_checker
        self._embedding_generator = embedding_generator
        self._knowledge_uow_factory = knowledge_uow_factory

    def retrieve_doc_snippets(self, query_text: str, cgpt_id: str) -> list[str]:
        return retrieve_doc_snippets(
            vector_store=self._vector_store,
            cgpt_permission_checker=self._cgpt_permission_checker,
            embedding_generator=self._embedding_generator,
            knowledge_uow_factory=self._knowledge_uow_factory,
            query_text=query_text,
            cgpt_id=cgpt_id,
        )
