# bootstrap.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.chat.application.ports.chat_queries import ChatQueries
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort

# ---------------- CHAT ----------------
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
    prepare_engine as chat_prepare_engine,
)
from src.contexts.chat.infrastructure.db.orm import (
    start_mappers as chat_start_mappers,
)
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.cgpt_queries import CgptQueries
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort

# ---------------- CGPT ----------------
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
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
from src.contexts.shared.typing_aliases import Factory  # alias for Callable[[], T]


@dataclass(frozen=True)
class DependenciesContainer:
    # Return **port types** (or ports’ concrete implementations if ports are Protocols)
    conversation_uow_factory: Factory[ConversationUOW]
    cgpt_uow_factory: Factory[CgptUOW]
    cgpt_retreiver_adapter_factory: Factory[CustomGPTInstructionsRetreiver]
    llm_adapter_factory: Factory[LlmPort]  # ToDo: make it a singleton
    cgpt_queries_adapter_factory: Factory[CgptQueries]
    chat_queries_adapter_factory: Factory[ChatQueries]
    conversation_adapter_factory: Factory[ConversationPort]


def _make_engine(
    db_url: str, prepare: Callable[[Engine], Engine] = (lambda e: e)
) -> Engine:
    connect_args: dict[str, object] = (
        {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    )
    engine = create_engine(db_url, connect_args=connect_args)
    return prepare(engine)


def _make_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def bootstrap(
    *,
    db_url_chat: str,
    db_url_cgpt: str,
    model_name: str,
    create_schema: bool = False,
) -> DependenciesContainer:
    # ----- CHAT -----
    chat_start_mappers()
    engine_chat = _make_engine(db_url_chat, chat_prepare_engine)
    sessionMaker_Chat: sessionmaker[Session] = _make_sessionmaker(engine_chat)
    if create_schema:
        chat_metadata.create_all(engine_chat)
    register_last_message_at_events(sessionMaker_Chat)

    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(sessionMaker_Chat)

    # Stateless LLM adapter can be a singleton or a factory; both fine.
    _llm_adapter = OpenaiAdapter(model_name=model_name)

    def llm_adapter_factory() -> LlmPort:
        return _llm_adapter

    # ----- CGPT -----
    cgpt_start_mappers()
    engine_cgpt = _make_engine(db_url_cgpt)
    sessionMaker_CGPT: sessionmaker[Session] = _make_sessionmaker(engine_cgpt)
    if create_schema:
        cgpt_metadata.create_all(engine_cgpt)
    # If CGPT has its own events, register them here (do NOT reuse chat’s)
    # register_cgpt_events(SessionMaker_CGPT)

    def cgpt_uow_factory() -> CgptUOW:
        return SQLAlchemyCgptUOW(sessionMaker_CGPT)

    def cgpt_instructions_adapter_factory() -> CustomGPTInstructionsRetreiver:
        # Adapter owns its own context’s UoW factory
        return CustomGPTInstructionsRetreiverAdapter(cgpt_uow_factory)

    def cgpt_queries_adapter_factory() -> CgptQueries:
        return CgptQueriesImplementation(cgpt_session_factory=sessionMaker_CGPT)

    def chat_queries_adapter_factory() -> ChatQueries:
        return ChatQueriesAdapter(chat_session_factory=sessionMaker_Chat)

    def conversation_adapter_factory() -> ConversationPort:
        return ConversationAdapter(conv_uow_factory=conversation_uow_factory)

    return DependenciesContainer(
        conversation_uow_factory=conversation_uow_factory,
        cgpt_uow_factory=cgpt_uow_factory,
        cgpt_retreiver_adapter_factory=cgpt_instructions_adapter_factory,
        llm_adapter_factory=llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_queries_adapter_factory,
        chat_queries_adapter_factory=chat_queries_adapter_factory,
        conversation_adapter_factory=conversation_adapter_factory,
    )
