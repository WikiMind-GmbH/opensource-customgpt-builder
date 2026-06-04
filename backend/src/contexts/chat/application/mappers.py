from typing import assert_never

from src.contexts.chat.application.ports.llm_port import MessageDTOllm, RoleDTOllm
from src.contexts.chat.domain.models import Message, Role

# We do not want our Port directly coupled to our domain model. So we use a DTO
# With this DTO->Domain translation function


def message_domain_to_message_llm_port_dto(msg: Message) -> MessageDTOllm:
    def role_translation(role: Role) -> RoleDTOllm:
        match msg.role:
            case Role.assistant:
                return RoleDTOllm.assistant
            case Role.system:
                return RoleDTOllm.system
            case Role.user:
                return RoleDTOllm.user
            case _:
                assert_never

    role: RoleDTOllm = role_translation(msg.role)
    return MessageDTOllm(role=role, imageUrlOrText=msg.imageUrlOrText)


def messages_domain_to_messages_llm_port_dto(msgs: list[Message]):
    return [message_domain_to_message_llm_port_dto(msg) for msg in msgs]
