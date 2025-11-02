from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.interface.http.schemas.customGPTs.customGPT_commands import (
    CustomGptToCreate,
    CustomGptToEdit,
)


def delete_custom_gpt_service(uow: CgptUOW, gpt_id: str):
    with uow:
        uow.cgpt_repo.delete(cgpt_id=gpt_id)
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
