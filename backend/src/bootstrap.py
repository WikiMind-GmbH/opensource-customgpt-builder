# bootstrap.py
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.chat.application.ports.chat_queries import ChatQueries
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import (
    ChatQueriesAdapter,
)
from src.contexts.chat.infrastructure.adapters.conv_adapter import ConversationAdapter
from src.contexts.chat.infrastructure.adapters.openai_adapter import OpenaiAdapter
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import (
    metadata as chat_metadata,
)
from src.contexts.chat.infrastructure.db.orm import (
    start_mappers as chat_start_mappers,
)
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.cgpt_queries import CgptQueries
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort

#
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.adapters.cgpt_permissions_adapter import (
    CgptPermissionCheckerAdapter,
)
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import (
    CgptQueriesImplementation,
)
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)
from src.contexts.customGPTs.infrastructure.db.orm import (
    metadata as cgpt_metadata,
)
from src.contexts.customGPTs.infrastructure.db.orm import (
    start_mappers as cgpt_start_mappers,
)
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.infrastructure.adapters.embedding_generator_openai_adapter import (
    EmbeddingGeneratorOpenAIAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.extract_text_from_document_adapter import (
    ExtractTextFromDocumentsAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.fastapi_task_scheduler_adapter import (
    FastAPITaskSchedulerAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.local_file_system_storage_adapter import (
    RawFileStoreLocalFsAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.qdrant_vector_store_adapter import (
    QdrantVectorStoreTextChunksAdapter,
)
from src.contexts.knowledge.infrastructure.db.knowledge_uow_adapter import (
    SQLAlchemyKnowledgeUOW,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    metadata as knowledge_metadata,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    start_mappers as knowledge_start_mappers,
)
from src.contexts.shared.typing_aliases import Factory


@dataclass(frozen=True)
class DependenciesContainer:
    # Return **port types** (or ports’ concrete implementations if ports are Protocols)
    conversation_uow_factory_factory: Factory[
        Factory[ConversationUOW]
    ]  # we need Fastapi Depends to return a Factory, so the dependency needs to be a factory of that factory .. :/ ugly
    cgpt_uow_factory_factory: Factory[Factory[CgptUOW]]
    cgpt_retreiver_adapter_factory: Factory[CustomGPTInstructionsRetreiver]
    llm_adapter_factory: Factory[LlmPort]  # ToDo: make it a singleton
    cgpt_queries_adapter_factory: Factory[CgptQueries]
    chat_queries_adapter_factory: Factory[ChatQueries]
    conversation_adapter_factory: Factory[ConversationPort]
    # knowledge
    knowledge_uow_factory_factory: Factory[Factory[KnowledgeUOW]]
    extract_text_from_document_adapter: ExtractTextFromDocumentPort
    cgpt_permissions_adapter_factory_factory: Factory[
        Factory[CgptPermissionCheckerPort]
    ]
    file_storage_adapter: RawFileStorePort
    task_scheduler: TaskSchedulerPort
    vector_store_adapter: VectorStorePortTextChunks
    embedding_generator_adapter: EmbeddingGeneratorPort


def _make_engine(
    db_url: str,  # , prepare: Callable[[Engine], Engine] = (lambda e: e)
) -> Engine:
    eng = create_engine(db_url)
    return eng  # prepare(engine)
    # engine = create_engine(
    #     db_url,
    #     pool_pre_ping=True,
    #     pool_size=10,
    #     max_overflow=20,
    # )


def _make_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def bootstrap(
    *,
    db_url_chat: str,
    db_url_cgpt: str,
    db_url_knowledge: str,
    model_name: str,
    create_schema: bool = False,
) -> DependenciesContainer:
    # ----- CHAT -----
    chat_start_mappers()
    engine_chat = _make_engine(db_url_chat)
    session_factory_Chat: sessionmaker[Session] = _make_sessionmaker(engine_chat)
    if create_schema:
        chat_metadata.create_all(engine_chat)
    register_last_message_at_events(session_factory_Chat)

    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(session_factory_Chat)

    def conversation_uow_factory_factory() -> Factory[ConversationUOW]:
        return conversation_uow_factory

    # Stateless LLM adapter can be a singleton or a factory; both fine.
    _llm_adapter = OpenaiAdapter(model_name=model_name)

    def llm_adapter_factory() -> LlmPort:
        return _llm_adapter

    # ----- CGPT -----
    cgpt_start_mappers()
    engine_cgpt = _make_engine(db_url_cgpt)
    session_factory_CGPT: sessionmaker[Session] = _make_sessionmaker(engine_cgpt)
    if create_schema:
        cgpt_metadata.create_all(engine_cgpt)
    # If CGPT has its own events, register them here (do NOT reuse chat’s)
    # register_cgpt_events(SessionMaker_CGPT)

    def cgpt_uow_factory() -> CgptUOW:
        return SQLAlchemyCgptUOW(session_factory_CGPT)

    def cgpt_uow_factory_factory() -> Factory[CgptUOW]:
        return cgpt_uow_factory

    def cgpt_instructions_adapter_factory() -> CustomGPTInstructionsRetreiver:
        # Adapter owns its own context’s UoW factory
        return CustomGPTInstructionsRetreiverAdapter(cgpt_uow_factory)

    def cgpt_queries_adapter_factory() -> CgptQueries:
        return CgptQueriesImplementation(cgpt_session_factory=session_factory_CGPT)

    def chat_queries_adapter_factory() -> ChatQueries:
        return ChatQueriesAdapter(chat_session_factory=session_factory_Chat)

    def conversation_adapter_factory() -> ConversationPort:
        return ConversationAdapter(conv_uow_factory=conversation_uow_factory)

    # ----- KNOWLEDGE CONTEXT -----

    knowledge_start_mappers()
    engine_knowledge = _make_engine(db_url=db_url_knowledge)
    session_factory_knowledge: sessionmaker[Session] = _make_sessionmaker(
        engine_knowledge
    )
    if create_schema:
        knowledge_metadata.create_all(engine_knowledge)

    def knowledge_uow_factory_factory() -> Factory[KnowledgeUOW]:
        return lambda: SQLAlchemyKnowledgeUOW(session_factory=session_factory_knowledge)

    embedding_generator_adapter: EmbeddingGeneratorPort = (
        EmbeddingGeneratorOpenAIAdapter()
    )

    embedding_dimension_generator = embedding_generator_adapter.embedding_dimension

    vector_store_adapter: VectorStorePortTextChunks = (
        QdrantVectorStoreTextChunksAdapter(
            db_url=require_env("QDRANT_URL"),
            embedding_dimension=embedding_dimension_generator,
        )
    )

    extract_text_from_document_adapter = ExtractTextFromDocumentsAdapter()

    def cgpt_permissions_adapter_factory_factory() -> Factory[
        CgptPermissionCheckerPort
    ]:
        return lambda: CgptPermissionCheckerAdapter(
            cgpt_session_factory=session_factory_CGPT
        )

    file_storage_adapter: RawFileStorePort = RawFileStoreLocalFsAdapter()

    task_scheduler_fastapi_backgroundtasks = FastAPITaskSchedulerAdapter()

    return DependenciesContainer(
        conversation_uow_factory_factory=conversation_uow_factory_factory,
        cgpt_uow_factory_factory=cgpt_uow_factory_factory,
        cgpt_retreiver_adapter_factory=cgpt_instructions_adapter_factory,
        llm_adapter_factory=llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_queries_adapter_factory,
        chat_queries_adapter_factory=chat_queries_adapter_factory,
        conversation_adapter_factory=conversation_adapter_factory,
        knowledge_uow_factory_factory=knowledge_uow_factory_factory,
        extract_text_from_document_adapter=extract_text_from_document_adapter,
        cgpt_permissions_adapter_factory_factory=cgpt_permissions_adapter_factory_factory,
        file_storage_adapter=file_storage_adapter,
        task_scheduler=task_scheduler_fastapi_backgroundtasks,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
    )
