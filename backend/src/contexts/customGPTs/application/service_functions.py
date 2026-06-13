from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.shared.typing_aliases import Factory


def delete_custom_gpt_service(
    uow_factory: Factory[CgptUOW],
    cgpt_id: str,
    conv_adapter: ConversationPort,
) -> None:
    with uow_factory() as uow:
        uow.cgpt_repo.delete(cgpt_id=cgpt_id)
        conv_adapter.delete_conversations_with_cgpt(cgpt_id=cgpt_id)
        uow.commit()


def create_custom_gpt_service(
    name: str,
    instructions: str,
    description: str | None,
    uow_factory: Factory[CgptUOW],
) -> str:
    with uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
            name=name,
            instructions=instructions,
            description=description,
        )
        uow.commit()
        return cgpt.id


def edit_custom_gpt_service(
    id: str,
    name: str,
    instructions: str,
    description: str | None,
    uow_factory: Factory[CgptUOW],
) -> None:
    with uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=id)
        cgpt.name = name
        cgpt.instructions = instructions
        cgpt.description = description
        uow.commit()
