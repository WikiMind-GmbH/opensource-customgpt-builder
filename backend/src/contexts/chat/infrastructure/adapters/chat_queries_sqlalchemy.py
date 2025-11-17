from sqlalchemy import select
from src.contexts.chat.domain.models import ContentType
from src.contexts.shared.typing_aliases import Factory
from src.contexts.chat.application.ports.chat_queries import (
    ChatQueries,
    NotFoundError,
    RoleDTO,
    TextMessageDTO,
    ConversationTextOnlyDTO,
    ConversationOverviewDTO,
)
from src.contexts.chat.infrastructure.db.orm import (
    conversations,
    messages_excl_sysPrompt,
)

from sqlalchemy.orm import Session


class ChatQueriesAdapter(ChatQueries):
    def __init__(self, chat_session_factory: Factory[Session]):
        self._session_factory = chat_session_factory

    def get_chat_summaries_ordered_by_last_message(
        self,
    ) -> list[ConversationOverviewDTO]:
        with self._session_factory() as session:
            stmt = select(
                conversations.c.id, conversations.c.title
            ).order_by(  # <- ORM style working with our mapped domain models
                conversations.c.last_message_at.desc().nullslast()
            )  # <- core style working with tables
            rows = session.execute(stmt).all()
            return [ConversationOverviewDTO(id=id, title=title) for id, title in rows]

    def get_chat_history(self, conv_id: str) -> ConversationTextOnlyDTO:
        with self._session_factory() as session:
            stmt_cgpt_id = select(conversations.c._customGPT_id, conversations.c.id).where(
                conversations.c.id == conv_id
            )
            row = session.execute(stmt_cgpt_id).one_or_none()
            if row is None:
                raise NotFoundError(f"No Conv with id {conv_id} exists")
            cgpt_id, _ = row

            stmt_msgs = (
                select(
                    messages_excl_sysPrompt.c.role, messages_excl_sysPrompt.c.imageUrlOrText
                )
                .where(
                    (messages_excl_sysPrompt.c.conversation_id == conv_id)
                    & (messages_excl_sysPrompt.c.contentType == ContentType.text)
                )
                .order_by(messages_excl_sysPrompt.c.created_at.asc().nullslast())
            )
            rows_msgs = session.execute(stmt_msgs).all()
            msgs: list[TextMessageDTO] = [
                TextMessageDTO(role=RoleDTO(str(role)), text=text)
                for role, text in rows_msgs
            ]

            return ConversationTextOnlyDTO(customgpt_id=cgpt_id, messages=msgs)
