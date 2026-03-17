import datetime
from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class Role(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


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


# @dataclass
# class Tool:
#     internal_id: str
#     name: str
#     parameters:


class Conversation:
    id: str
    title: str
    # system_prompt: list[Message] | None = None # ToDo: change repo etc, add other changes see: https://chatgpt.com/c/68dd7c24-82a0-8327-84f1-445d9ecc5192
    _messages_excl_sysPrompt: list[
        Message
    ]  # = field(default_factory=list) #excluding system prompt <- this will be retreived every time
    _customGPT_id: str | None = None
    # available_tools: list[Tool] | None = None
    # Rag I would leave open to activate/deactivate in the

    def __init__(self, id: str | None = None, customGPT_id: str | None = None) -> None:
        self.id = id if id else str(uuid4())
        self._customGPT_id = customGPT_id
        self._messages_excl_sysPrompt: list[Message] = []
        self.title = str(datetime.datetime.now())

    def __repr__(self) -> str:
        return f"id: {self.id}, messages_num: {len(self._messages_excl_sysPrompt)}"

    @property  # https://docs.python.org/3/library/functions.html?utm_source=chatgpt.com#property
    def customGPT_id(self):
        return self._customGPT_id

    @property  # https://docs.python.org/3/library/functions.html?utm_source=chatgpt.com#property
    def messages_excl_sysPrompt(self):
        return self._messages_excl_sysPrompt

    def add_assistant_text_message(self, assistant_text_response: str) -> Message:
        msg: Message = Message(
            role=Role.assistant,
            contentType=ContentType.text,
            imageUrlOrText=assistant_text_response,
        )
        self._messages_excl_sysPrompt.append(
            msg
        )  # could add metadata or similar in the future
        return msg

    def add_user_text_message(self, user_text_message: str):
        msg: Message = Message(
            role=Role.user,
            contentType=ContentType.text,
            imageUrlOrText=user_text_message,
        )
        self._messages_excl_sysPrompt.append(
            msg
        )  # could add metadata or similar in the future
        return msg

    # def add_user_image_message(self, img:Base64Encoded | URL):
    #     msg: Message = Message(role=Role.assistant, contentType=ContentType.text, imageUrlOrText=assistant_text_response)
    #     self._messages_excl_sysPrompt.append(msg) # could add metadata or similar in the future

    def cgpt_infos_to_sysprompt(
        self, cgpt_name: str, cgpt_instructions: str
    ) -> list[Message]:
        def system_text_message(text: str) -> Message:
            return Message(
                role=Role.system,
                contentType=ContentType.text,
                imageUrlOrText=text,
            )

        msgs: list[Message] = []
        msgs.append(system_text_message(f"Your name is `{cgpt_name}`)"))
        msgs.append(
            system_text_message("Your instructions are pasted into this code block:")
        )
        msgs.append(system_text_message("```"))
        msgs.append(system_text_message(cgpt_instructions))
        msgs.append(system_text_message("```"))
        msgs.append(
            system_text_message("If instructions in the code block make no sense")
        )
        msgs.append(
            system_text_message(
                "Preface your first response with `My instructions are unclear, as such I will answer as usual`"
            )
        )
        msgs.append(system_text_message("And just ignore them, answering as normal"))
        return msgs

    def create_prompt(
        self, cgpt_name: str | None = None, cgpt_instructions: str | None = None
    ):
        messages_prompt: list[Message] = []
        if cgpt_instructions is not None and cgpt_name is not None:
            messages_prompt = messages_prompt + (
                self.cgpt_infos_to_sysprompt(
                    cgpt_name=cgpt_name, cgpt_instructions=cgpt_instructions
                )
            )
        messages_prompt = messages_prompt + self._messages_excl_sysPrompt
        return messages_prompt
