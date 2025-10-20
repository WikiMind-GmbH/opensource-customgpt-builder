from src.contexts.chat.domain.models import ContentType, Message as DomainMessage, Role as DomainRole
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import MessageDTO, RoleDTO
from src.contexts.chat.application.mappers import message_dto_to_message_domain

def test_message_mapper():
    text="Some text"
    dto_message:MessageDTO=MessageDTO(role=RoleDTO.assistant, text_content=text)
    domain_message: DomainMessage = DomainMessage(role =DomainRole.assistant, contentType=ContentType.text, imageUrlOrText=text)
    assert message_dto_to_message_domain(dto_message) == domain_message

    dto_message:MessageDTO=MessageDTO(role=RoleDTO.user, text_content=text)
    domain_message: DomainMessage = DomainMessage(role =DomainRole.user, contentType=ContentType.text, imageUrlOrText=text)
    assert message_dto_to_message_domain(dto_message) == domain_message

    dto_message:MessageDTO=MessageDTO(role=RoleDTO.system, text_content=text)
    domain_message: DomainMessage = DomainMessage(role =DomainRole.system, contentType=ContentType.text, imageUrlOrText=text)
    assert message_dto_to_message_domain(dto_message) == domain_message