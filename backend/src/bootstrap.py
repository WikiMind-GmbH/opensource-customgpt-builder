# bootstrap.py
from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# your shared aliases
from contexts.shared.typing_aliases import Factory

# ORM (chat context)
from contexts.chat.infrastructure.db.orm import (
    prepare_engine,
    start_mappers as chat_start_mappers,
    metadata as chat_metadata,
)
from contexts.chat.infrastructure.db.events import register_last_message_at_events

# Ports (Protocols)
from contexts.chat.application.ports.uow import ConversationUOW
from contexts.customGPTs.application.ports.uow import CGPTUOW
# from contexts.customGPTs.application.ports.instructions import CustomGPTInstructionsRetrieverPort

# Adapters (implementations)
from contexts.chat.infrastructure.db.uow_implementations import SQLAlchemyConversationUOW
# from contexts.customGPTs.infrastructure.db.uow_implementations import SQLAlchemyCGPTUOW
from contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)


@dataclass(frozen=True)
class DependenciesContainer:
    """
    Typed factories that return **port** types, not concrete adapters.
    """
    conversation_uow_factory: Factory[ConversationUOW]
    # cgpt_uow_factory: Factory[CGPTUOW]
    # cgpt_instructions_adapter_factory: Factory[CustomGPTInstructionsRetrieverPort]


def _make_engine(db_url: str) -> Engine:
    connect_args: dict[str, object] = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, connect_args=connect_args)
    return prepare_engine(engine)  # e.g., enable SQLite FK pragma


def _make_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    # Only override what's not default and we actively want:
    return sessionmaker(engine, expire_on_commit=False)


def bootstrap(
    *,
    db_url: str,
    create_schema: bool = False,  # dev/test only
) -> DependenciesContainer:
    # 1) Map once (no engine required)
    chat_start_mappers()

    # 2) Engine + single Session factory for all UoWs
    engine = _make_engine(db_url)
    SessionMaker: sessionmaker[Session] = _make_sessionmaker(engine)

    # 3) Optional schema creation
    if create_schema:
        chat_metadata.create_all(engine)
        # add other contexts' metadata here if/when needed

    # 4) Register session/ORM events
    register_last_message_at_events(SessionMaker)

    # 5) UoW factories — return **port** types
    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(SessionMaker)

    # def cgpt_uow_factory() -> CGPTUOW:
    #     return SQLAlchemyCGPTUOW(SessionMaker)

    # # 6) External adapter factory — return **port** type
    # def cgpt_instructions_adapter_factory() -> CustomGPTInstructionsRetrieverPort:
    #     return CustomGPTInstructionsRetreiverAdapter(cgpt_uow_factory=cgpt_uow_factory)

    # 7) Typed container (also expose a plain Session factory if needed)
    return DependenciesContainer(
        session_factory=lambda: SessionMaker(),
        conversation_uow_factory=conversation_uow_factory,
        # cgpt_uow_factory=cgpt_uow_factory,
        # cgpt_instructions_adapter_factory=cgpt_instructions_adapter_factory,
    )
