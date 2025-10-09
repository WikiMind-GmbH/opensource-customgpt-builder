from dataclasses import dataclass, field
from enum import StrEnum
from typing import List


class Role(StrEnum):
    user = "user"
    assistant = "assistant"
    system = 'system'


class ContentType(StrEnum):
    image = "image"
    text = "text"

# This is aqdapter specific -translate to a more general and simple version if possible. 
# i.e. if we had no images, just always use structure of UserOrAssistantTextMessage
@dataclass
class Message:
    role: Role
    contentType: ContentType
    imageUrlOrText: str


@dataclass
class TextMessage:
    role: Role
    text: str

@dataclass
class ConversationFilteredForClient:
    customgpt_id: str | None
    messages: list[TextMessage]


@dataclass
class ConversationOverview:
    id: str
    title: str = ""



# Alternative idea: system prompt engineering is outsourced (e.g. to cgpt or mudita context, then systemPrompt is passed directly) for more future flexibility:
# Thus we only have the datastructure supporting system prompt




@dataclass
class Conversation:
    id: str
    title: str | None = None
    system_prompt: list[Message] | None = None # ToDo: change repo etc, add other changes see: https://chatgpt.com/c/68dd7c24-82a0-8327-84f1-445d9ecc5192
    messages: list[Message] = field(default_factory=list)
    customGPT_id: str | None = None
    # Rag I would leave open to activate/deactivate in the

    def add(self, message: Message):
        self.messages.append(message)

    def __repr__(self) -> str:
        return f"id: {self.id}, messages_num: {len(self.messages)}"

    def get_conversation_filtered_for_client(self)->ConversationFilteredForClient:
        msgs: list[TextMessage] = [
            TextMessage(role=msg.role, text=msg.imageUrlOrText)
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


