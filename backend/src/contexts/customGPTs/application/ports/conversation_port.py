from typing import Protocol


class ConversationPort(Protocol):
    def delete_conversations_with_cgpt(self, cgpt_id:str):...