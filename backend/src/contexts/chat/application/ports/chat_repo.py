from typing import Protocol

from src.contexts.chat.domain.models import Conversation


class TemporaryConvRepoError(RuntimeError):
    "This will do until i actually implement useful Errors"


class ConversationNotFoundError(RuntimeError):
    "Conversation not found"


# Below: Not needed if we explicitly inherit Protocols -> better for typechecking
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class ConversationRepository(Protocol):
    def get(self, conv_id: str) -> Conversation: ...
    def create_conversation(self, cgpt_id: str | None = None) -> Conversation: ...
    def delete(self, conversation: Conversation): ...
    def delete_conversations_with_cgpt(self, cgpt_id: str): ...
