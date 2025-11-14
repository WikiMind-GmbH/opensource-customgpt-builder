from src.contexts.shared.typing_aliases import Factory
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort


class ConversationAdapter(ConversationPort):
    def __init__(self, conv_uow_factory: Factory[ConversationUOW]):
        self.conv_uow_factory: Factory[ConversationUOW] = conv_uow_factory
    def delete_conversations_with_cgpt(self, cgpt_id:str):
        with self.conv_uow_factory() as uow:
            uow.conversation_repo.delete_conversations_with_cgpt(cgpt_id=cgpt_id)
            uow.commit()