from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CgptNotFoundError,
    CustomGPTInfosDTO,
    CustomGPTInstructionsRetreiver,
    DefaultCGPTRetreiverError,
)
from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.shared.typing_aliases import Factory


class CustomGPTInstructionsRetreiverAdapter(CustomGPTInstructionsRetreiver):
    def __init__(self, cgpt_uow_factory: Factory[CgptUOW]):
        self._cgpt_uow_factory: Factory[CgptUOW] = cgpt_uow_factory

    def get_cgpt_infos_for_prompt(
        self, cgpt_id: str
    ) -> (
        CustomGPTInfosDTO
    ):  # ToDo: add exception GPTDoesNotExist and add management here
        try:
            with self._cgpt_uow_factory() as uow:
                cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
                return CustomGPTInfosDTO(name=cgpt.name, instructions=cgpt.instructions)
        except CgptNotFound as exc:
            raise CgptNotFoundError(f"Custom GPT {cgpt_id} was not found") from exc
        except Exception as exc:
            raise DefaultCGPTRetreiverError from exc
