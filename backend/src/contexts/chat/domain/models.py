from dataclasses import dataclass, field
from enum import StrEnum
from typing import List
from uuid import uuid4

from src.contexts.chat.application.exceptions import SysPromptMustBeInitializedBeforeAddingMessages


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

# @dataclass
# class Tool:
#     internal_id: str
#     name: str
#     parameters: 

# Alternative idea: system prompt engineering is outsourced (e.g. to cgpt or mudita context, then systemPrompt is passed directly) for more future flexibility:
# Thus we only have the datastructure supporting system prompt





class Conversation:
    id: str
    title: str | None = None
    # system_prompt: list[Message] | None = None # ToDo: change repo etc, add other changes see: https://chatgpt.com/c/68dd7c24-82a0-8327-84f1-445d9ecc5192
    messages_excl_sysPrompt: list[Message] # = field(default_factory=list) #excluding system prompt <- this will be retreived every time
    _customGPT_id: str | None = None
    # available_tools: list[Tool] | None = None
    # Rag I would leave open to activate/deactivate in the

    def __init__(self,id:str | None = None, customGPT_id: str |None = None) -> None:
        self.id = id if id else str(uuid4())
        self._customGPT_id = customGPT_id
        self.messages_excl_sysPrompt: list[Message] = []


    def __repr__(self) -> str:
        return f"id: {self.id}, messages_num: {len(self.messages_excl_sysPrompt)}"
    
    @property # https://docs.python.org/3/library/functions.html?utm_source=chatgpt.com#property 
    def customGPT_id(self):
        return self._customGPT_id
    
    @property
    def get_conversation_filtered_for_client(self)->ConversationFilteredForClient:
        msgs: list[TextMessage] = [
            TextMessage(role=msg.role, text=msg.imageUrlOrText)
            for msg in self.messages_excl_sysPrompt
        ]
        return ConversationFilteredForClient(self._customGPT_id, msgs)