from typing import List, Protocol, Sequence
from uuid import uuid4

from sqlalchemy import delete, select
from src.contexts.chat.application.ports.conversation_repo import ConversationRepository
from src.contexts.chat.application.exceptions import ConversationNonExistentError
from src.contexts.chat.domain.models import Conversation, ConversationOverview, Message
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from src.contexts.chat.infrastructure.db.orm import conversations

class SQAlchemyConversartionRepository(ConversationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session
    def get(self, conv_id:str)-> Conversation:
        conv = self._session.get(Conversation, conv_id)
        if conv == None: raise ConversationNonExistentError(conv_id)
        return conv
    def list_all_overviews_ordered_by_latest_msg(self,)-> Sequence[ConversationOverview]:
        stmt = ( 
            select(Conversation.id, Conversation.title) #<- ORM style working with our mapped domain models
            .order_by(conversations.c.last_message_at.desc().nullslast()) # <- core style working with tables
        )
        rows = self._session.execute(stmt).all()
        return [ConversationOverview(id=id, title=title) for id, title in rows] 
    def create_conversation(self,cgpt_id:str | None = None)-> Conversation:
        conv = Conversation(customGPT_id=cgpt_id)
        self._session.add(conv)
        return conv
    def delete(self, conversation: Conversation):
        self._session.delete(conversation)
    def delete_conversations_with_cgpt(self, cgpt_id: str):
        # stmt = delete(Conversation).where(conversations.c.customGPT_id == cgpt_id) # <- core style working with tables
        stmt = delete(Conversation).where(Conversation._customGPT_id == cgpt_id) #<- ORM style working with our mapped domain models
        self._session.execute(stmt)

# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.