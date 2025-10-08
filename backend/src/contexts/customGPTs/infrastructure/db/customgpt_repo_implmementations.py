from typing import  Sequence
from uuid import uuid4

from sqlalchemy import select
from chat.application.exceptions import ConversationNonExistentError
from domain.models import CustomGPT
from sqlalchemy.orm import Session

class SQAlchemyCustomGPTRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
    

# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.