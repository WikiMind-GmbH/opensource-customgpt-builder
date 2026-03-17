from src.contexts.chat.application.mappers import (
    message_domain_to_message_llm_port_dto,
)
from src.contexts.chat.application.ports.llm_port import (
    MessageDTOllm,
    RoleDTOllm,
)
from src.contexts.chat.domain.models import (
    ContentType,
)
from src.contexts.chat.domain.models import (
    Message as DomainMessage,
)
from src.contexts.chat.domain.models import (
    Role as DomainRole,
)


def test_message_domain_to_message_llm_port_dto():
    text = "Some text"
    # assistant
    domain_message: DomainMessage = DomainMessage(
        role=DomainRole.assistant, contentType=ContentType.text, imageUrlOrText=text
    )
    dto_llm_message: MessageDTOllm = MessageDTOllm(
        RoleDTOllm.assistant, imageUrlOrText=text
    )
    assert dto_llm_message == message_domain_to_message_llm_port_dto(domain_message)

    # user
    domain_message: DomainMessage = DomainMessage(
        role=DomainRole.user, contentType=ContentType.text, imageUrlOrText=text
    )
    dto_llm_message: MessageDTOllm = MessageDTOllm(RoleDTOllm.user, imageUrlOrText=text)
    assert dto_llm_message == message_domain_to_message_llm_port_dto(domain_message)

    # system
    domain_message: DomainMessage = DomainMessage(
        role=DomainRole.system, contentType=ContentType.text, imageUrlOrText=text
    )
    dto_llm_message: MessageDTOllm = MessageDTOllm(
        RoleDTOllm.system, imageUrlOrText=text
    )
    assert dto_llm_message == message_domain_to_message_llm_port_dto(domain_message)
