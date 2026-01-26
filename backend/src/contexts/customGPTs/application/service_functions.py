from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.domain.models import CustomGPT


def delete_custom_gpt_service(
    uow: CgptUOW, cgpt_id: str, conv_adapter: ConversationPort
):
    with uow:
        uow.cgpt_repo.delete(cgpt_id=cgpt_id)
        conv_adapter.delete_conversations_with_cgpt(cgpt_id=cgpt_id)
        uow.commit()


def create_custom_gpt_service(
    name: str, instructions: str, description: str | None, uow: CgptUOW
) -> str:
    with uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
            name=name,
            instructions=instructions,
            description=description,
        )
        uow.commit()
        return cgpt.id


def edit_custom_gpt_service(
    id: str, name: str, instructions: str, description: str | None, uow: CgptUOW
) -> None:
    with uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=id)
        cgpt.name = name
        cgpt.instructions = instructions
        cgpt.description = description
        uow.commit()
