from typing import assert_never
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    MessageDTO,
    RoleDTO,
)
from src.contexts.chat.domain.models import ContentType, Message, Role
from src.contexts.chat.domain.models import Role as DomainRole
from openai.types.chat.completion_create_params import CompletionCreateParams
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)


# We do not want our Port directly coupled to our domain model. So we use a DTO
# With this DTO->Domain translation function
def message_dto_to_message_domain(msg_dto: MessageDTO) -> Message:
    def role_translation(dto_role: RoleDTO) -> DomainRole:
        match dto_role:
            case RoleDTO.assistant:
                return DomainRole.assistant
            case RoleDTO.system:
                return DomainRole.system
            case RoleDTO.user:
                return DomainRole.user

    role = role_translation(msg_dto.role)
    content_Type: ContentType = ContentType.text
    imageUrlOrText: str = msg_dto.text_content
    msg: Message = Message(
        role=role, contentType=content_Type, imageUrlOrText=imageUrlOrText
    )
    return msg


def transform_message_domain_to_message_openai_chat_completion(msg: Message) -> ChatCompletionMessageParam:
    match msg.role:
        case Role.assistant:
            return ChatCompletionAssistantMessageParam(
                role="assistant", content=msg.imageUrlOrText
            )
        case Role.user:
            return ChatCompletionUserMessageParam(
                role="user", content=msg.imageUrlOrText
            )
        case Role.system:
            return ChatCompletionSystemMessageParam(
                role="system", content=msg.imageUrlOrText
            )
        # case other:
        #     # Statically unreachable if Role is an Enum and cases are exhaustive.
        #     assert_never(other)

# below maybe useful in the future: 
# def transform_message_openai_chat_completion_to_message_domain(msg: ChatCompletionMessage) -> Message: