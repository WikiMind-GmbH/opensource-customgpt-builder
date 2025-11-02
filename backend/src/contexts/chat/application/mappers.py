from src.contexts.chat.application.ports.llm_port import MessageDTOllm, RoleDTOllm
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    MessageDTORetreiver,
    RoleDTORetreiver,
)
from src.contexts.chat.domain.models import ContentType, Message, Role
from src.contexts.chat.domain.models import Role as DomainRole



# We do not want our Port directly coupled to our domain model. So we use a DTO
# With this DTO->Domain translation function
def message_dto_cgpt_retreiver_to_message_domain(msg_dto: MessageDTORetreiver) -> Message:
    def role_translation(dto_role: RoleDTORetreiver) -> DomainRole:
        match dto_role:
            case RoleDTORetreiver.assistant:
                return DomainRole.assistant
            case RoleDTORetreiver.system:
                return DomainRole.system
            case RoleDTORetreiver.user:
                return DomainRole.user

    role = role_translation(msg_dto.role)
    content_Type: ContentType = ContentType.text
    imageUrlOrText: str = msg_dto.text_content
    msg: Message = Message(
        role=role, contentType=content_Type, imageUrlOrText=imageUrlOrText
    )
    return msg

def message_domain_to_message_llm_port_dto(msg: Message)->MessageDTOllm:
    def role_translation(role: Role) -> RoleDTOllm:
        match msg.role:
            case Role.assistant:
                return RoleDTOllm.assistant
            case Role.system:
                return RoleDTOllm.system
            case Role.user:
                return RoleDTOllm.user
    role:RoleDTOllm = role_translation(msg.role)
    return MessageDTOllm(role=role, imageUrlOrText=msg.imageUrlOrText)