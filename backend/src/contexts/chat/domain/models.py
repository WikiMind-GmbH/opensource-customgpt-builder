from dataclasses import dataclass, field
from enum import StrEnum
from typing import List


class Role(StrEnum):
    user = "user"
    assistant = "assistant"


class ContentType(StrEnum):
    image = "image"
    text = "text"


@dataclass
class Message:
    role: Role
    contentType: ContentType
    imageUrlOrText: str

@dataclass
class UserOrAssistantTextMessage:
    role: Role
    text: str

@dataclass
class ConversationFilteredForClient:
    customgpt_id: str | None
    messages: list[UserOrAssistantTextMessage]


@dataclass
class ConversationOverview:
    id: str
    title: str = ""



@dataclass
class Conversation:
    id: str
    title: str | None = None
    messages: list[Message] = field(default_factory=list)
    customGPT_id: str | None = None
    # Rag I would leave open to activate/deactivate in the

    def add(self, message: Message):
        self.messages.append(message)

    def __repr__(self) -> str:
        return f"id: {self.id}, messages_num: {len(self.messages)}"

    def get_conversation_filtered_for_client(self)->ConversationFilteredForClient:
        msgs: list[UserOrAssistantTextMessage] = [
            UserOrAssistantTextMessage(role=msg.role, text=msg.imageUrlOrText)
            for msg in self.messages
            if (
                msg.role
                in (
                    Role.assistant,
                    Role.user,
                )  # drop 'system' since Role enum only has user|assistant
                and msg.contentType == ContentType.text
            )
        ]
        return ConversationFilteredForClient(self.customGPT_id, msgs)
    
    def initialize_conversation_with_additional_context(self, customGpt_instructions:str, custom):


