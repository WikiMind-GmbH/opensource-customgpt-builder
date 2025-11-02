from sqlalchemy import delete
from src.contexts.chat.application.ports.chat_repo import (
    ConversationNotFoundError,
    ConversationRepository,
)
from src.contexts.chat.domain.models import Conversation
from sqlalchemy.orm import Session


class SQAlchemyConversartionRepository(ConversationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, conv_id: str) -> Conversation:
        conv = self._session.get(Conversation, conv_id)
        if conv == None:
            raise ConversationNotFoundError(f"conv_id = {conv_id}")
        return conv

    def create_conversation(self, cgpt_id: str | None = None) -> Conversation:
        conv = Conversation(customGPT_id=cgpt_id)
        self._session.add(conv)
        return conv

    def delete(self, conversation: Conversation):
        self._session.delete(conversation)

    def delete_conversations_with_cgpt(self, cgpt_id: str):
        # stmt = delete(Conversation).where(conversations.c.customGPT_id == cgpt_id) # <- core style working with tables
        stmt = delete(Conversation).where(
            Conversation._customGPT_id == cgpt_id
        )  # <- ORM style working with our mapped domain models
        self._session.execute(stmt)


# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.
