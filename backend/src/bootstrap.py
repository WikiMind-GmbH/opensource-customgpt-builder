# bootstrap.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fastapi import BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.chat.application.ports.chat_queries import ChatQueries
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)
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
from src.contexts.knowledge.infrastructure.adapters.retreive_relevant_doc_snippets_adapter import (
    RelevantDocSnippetRetreiverAdapter,
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
    retrieve_doc_snippets_adapter_factory: Factory[RelevantDocSnippetRetreiverPort]
    conversation_adapter_factory: Factory[ConversationPort]

    # knowledge
    knowledge_uow_factory_factory: Factory[Factory[KnowledgeUOW]]
    extract_text_from_document_adapter_factory: Factory[ExtractTextFromDocumentPort]
    cgpt_permissions_adapter_factory: Factory[CgptPermissionCheckerPort]
    file_storage_adapter_factory: Factory[RawFileStorePort]
    task_scheduler_factory: Callable[..., TaskSchedulerPort]
    vector_store_adapter_factory: Factory[VectorStorePortTextChunks]
    embedding_generator_adapter_factory: Factory[EmbeddingGeneratorPort]


class SQLDBResource:
    def __init__(
        self,
        engine: Engine,
        session_factory: sessionmaker[Session],
    ) -> None:
        self.engine = engine
        self.session_factory = session_factory


class SQLDBResourceOfContexts:
    def __init__(
        self,
        chat_resources: SQLDBResource,
        cgpt_resources: SQLDBResource,
        knowledge_resources: SQLDBResource,
    ) -> None:
        self.chat_resources = chat_resources
        self.cgpt_resources = cgpt_resources
        self.knowledge_resources = knowledge_resources


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


def start_all_mappers():
    chat_start_mappers()
    cgpt_start_mappers()
    knowledge_start_mappers()


def build_db_resources_and_register_events(
    db_url_chat: str,
    db_url_cgpt: str,
    db_url_knowledge: str,
) -> SQLDBResourceOfContexts:
    engine_chat = _make_engine(db_url_chat)
    session_factory_chat: sessionmaker[Session] = _make_sessionmaker(engine_chat)
    chat_resources = SQLDBResource(
        engine=engine_chat,
        session_factory=session_factory_chat,
    )
    register_last_message_at_events(session_factory_chat)

    engine_cgpt = _make_engine(db_url_cgpt)
    session_factory_cgpt: sessionmaker[Session] = _make_sessionmaker(engine_cgpt)
    cgpt_resources = SQLDBResource(
        engine=engine_cgpt,
        session_factory=session_factory_cgpt,
    )

    engine_knowledge = _make_engine(db_url_knowledge)
    session_factory_knowledge: sessionmaker[Session] = _make_sessionmaker(
        engine_knowledge,
    )
    knowledge_resources = SQLDBResource(
        engine=engine_knowledge,
        session_factory=session_factory_knowledge,
    )

    return SQLDBResourceOfContexts(
        chat_resources=chat_resources,
        cgpt_resources=cgpt_resources,
        knowledge_resources=knowledge_resources,
    )


def create_sql_tables(sql_db_resources_of_contexts: SQLDBResourceOfContexts):
    chat_metadata.create_all(sql_db_resources_of_contexts.chat_resources.engine)
    cgpt_metadata.create_all(sql_db_resources_of_contexts.cgpt_resources.engine)
    knowledge_metadata.create_all(
        sql_db_resources_of_contexts.knowledge_resources.engine
    )


def create_dependencies(
    sql_db_resources_of_contexts: SQLDBResourceOfContexts,
    vector_store_is_for_testing: bool = False,
    model_name: str = require_env("MODEL_NAME"),
    embedding_model: str = require_env("EMBEDDING_MODEL"),
    embedding_dimension: int = int(require_env("EMBEDDING_DIMENSION")),
    db_url_vectorstore: str = require_env("QDRANT_URL"),
) -> DependenciesContainer:
    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(
            sql_db_resources_of_contexts.chat_resources.session_factory
        )

    def conversation_uow_factory_factory() -> Factory[ConversationUOW]:
        return conversation_uow_factory

    # Stateless LLM adapter can be a singleton or a factory; both fine.
    def llm_adapter_factory() -> LlmPort:
        return OpenaiAdapter(model_name=model_name)

    def cgpt_uow_factory() -> CgptUOW:
        return SQLAlchemyCgptUOW(
            sql_db_resources_of_contexts.cgpt_resources.session_factory
        )

    def cgpt_uow_factory_factory() -> Factory[CgptUOW]:
        return cgpt_uow_factory

    def cgpt_instructions_adapter_factory() -> CustomGPTInstructionsRetreiver:
        # Adapter owns its own context’s UoW factory
        return CustomGPTInstructionsRetreiverAdapter(cgpt_uow_factory)

    def cgpt_queries_adapter_factory() -> CgptQueries:
        return CgptQueriesImplementation(
            cgpt_session_factory=sql_db_resources_of_contexts.cgpt_resources.session_factory
        )

    def chat_queries_adapter_factory() -> ChatQueries:
        return ChatQueriesAdapter(
            chat_session_factory=sql_db_resources_of_contexts.chat_resources.session_factory
        )

    def conversation_adapter_factory() -> ConversationPort:
        return ConversationAdapter(conv_uow_factory=conversation_uow_factory)

    def knowledge_uow_factory_factory() -> Factory[KnowledgeUOW]:
        return lambda: SQLAlchemyKnowledgeUOW(
            session_factory=sql_db_resources_of_contexts.knowledge_resources.session_factory
        )

    def embedding_generator_adapter_factory() -> EmbeddingGeneratorPort:
        return EmbeddingGeneratorOpenAIAdapter(
            embedding_dimension=embedding_dimension,
            embedding_model=embedding_model,
        )

    def vector_store_adapter_factory() -> VectorStorePortTextChunks:
        return QdrantVectorStoreTextChunksAdapter(
            db_url=db_url_vectorstore,
            embedding_dimension=embedding_dimension,
            create_adapter_for_testing_with_test_collection=vector_store_is_for_testing,
        )

    def extract_text_from_document_adapter_factory() -> ExtractTextFromDocumentPort:
        return ExtractTextFromDocumentsAdapter()

    def cgpt_permissions_adapter_factory() -> CgptPermissionCheckerPort:
        return CgptPermissionCheckerAdapter(
            cgpt_session_factory=sql_db_resources_of_contexts.cgpt_resources.session_factory
        )

    def retrieve_doc_snippets_adapter_factory() -> RelevantDocSnippetRetreiverPort:
        return RelevantDocSnippetRetreiverAdapter(
            vector_store=vector_store_adapter_factory(),
            cgpt_permission_checker=cgpt_permissions_adapter_factory(),
            embedding_generator=embedding_generator_adapter_factory(),
            knowledge_uow_factory=knowledge_uow_factory_factory(),
        )

    def file_storage_adapter_factory() -> RawFileStorePort:
        return RawFileStoreLocalFsAdapter()

    def task_scheduler_factory(background_tasks: BackgroundTasks) -> TaskSchedulerPort:
        return FastAPITaskSchedulerAdapter(background_tasks=background_tasks)

    return DependenciesContainer(
        conversation_uow_factory_factory=conversation_uow_factory_factory,
        cgpt_uow_factory_factory=cgpt_uow_factory_factory,
        cgpt_retreiver_adapter_factory=cgpt_instructions_adapter_factory,
        llm_adapter_factory=llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_queries_adapter_factory,
        chat_queries_adapter_factory=chat_queries_adapter_factory,
        retrieve_doc_snippets_adapter_factory=retrieve_doc_snippets_adapter_factory,
        conversation_adapter_factory=conversation_adapter_factory,
        knowledge_uow_factory_factory=knowledge_uow_factory_factory,
        extract_text_from_document_adapter_factory=extract_text_from_document_adapter_factory,
        cgpt_permissions_adapter_factory=cgpt_permissions_adapter_factory,
        file_storage_adapter_factory=file_storage_adapter_factory,
        task_scheduler_factory=task_scheduler_factory,
        vector_store_adapter_factory=vector_store_adapter_factory,
        embedding_generator_adapter_factory=embedding_generator_adapter_factory,
    )


def bootstrap(
    model_name: str,
    db_url_chat: str,
    db_url_cgpt: str,
    db_url_knowledge: str,
    create_schema: bool,
    embedding_model: str,
    embedding_dimension: int,
    db_url_vectorstore: str,
) -> DependenciesContainer:
    start_all_mappers()

    sql_db_resources_of_contexts = build_db_resources_and_register_events(
        db_url_chat=db_url_chat,
        db_url_cgpt=db_url_cgpt,
        db_url_knowledge=db_url_knowledge,
    )

    if create_schema:
        create_sql_tables(sql_db_resources_of_contexts)

    return create_dependencies(
        sql_db_resources_of_contexts=sql_db_resources_of_contexts,
        model_name=model_name,
        embedding_dimension=embedding_dimension,
        embedding_model=embedding_model,
        db_url_vectorstore=db_url_vectorstore,
        vector_store_is_for_testing=False,
    )
