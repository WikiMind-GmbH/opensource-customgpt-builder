from src.contexts.customGPTs.application.exceptions import CGPTNonExistentError
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CgptNotFoundError,
    CustomGPTInstructionsRetreiver,
    MessageDTO,
    RoleDTO,
    DefaultCGPTRetreiverError,
)
from src.contexts.shared.typing_aliases import Factory

def cgpt_infos_to_sysprompt(
        cgpt_name: str, cgpt_instructions: str
    ) -> list[MessageDTO]:
        msgs: list[MessageDTO] = []
        msgs.append(
            MessageDTO(role=RoleDTO.system, text_content=f"You are `{cgpt_name}`)")
        )
        msgs.append(
            MessageDTO(
                role=RoleDTO.system,
                text_content="Your instructions are pasted into this code block:",
            )
        )
        msgs.append(MessageDTO(role=RoleDTO.system, text_content="```"))
        msgs.append(MessageDTO(role=RoleDTO.system, text_content=cgpt_instructions))
        msgs.append(MessageDTO(role=RoleDTO.system, text_content="```"))
        msgs.append(
            MessageDTO(
                role=RoleDTO.system,
                text_content="If instructions in the code block make no sense",
            )
        )
        msgs.append(
            MessageDTO(
                role=RoleDTO.system,
                text_content="Preface your first response with `My instructions are unclear, as such I will answer as usual`",
            )
        )
        msgs.append(
            MessageDTO(
                role=RoleDTO.system,
                text_content="And just ignore them, answering as normal",
            )
        )
        return msgs

class CustomGPTInstructionsRetreiverAdapter(CustomGPTInstructionsRetreiver):
    def __init__(self, cgpt_uow_factory: Factory[CgptUOW]):
        self._cgpt_uow_factory: Factory[CgptUOW] = cgpt_uow_factory

    def get_cgpt_sys_prompt(
        self, cgpt_id: str
    ) -> list[
        MessageDTO
    ]:  # ToDo: add exception GPTDoesNotExist and add management here
        
        try:
            with self._cgpt_uow_factory() as uow:
                try:
                    cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
                except CGPTNonExistentError:
                    raise CgptNotFoundError
                
                messages_of_sysprompt: list[MessageDTO] = cgpt_infos_to_sysprompt(
                    cgpt_name=cgpt.name, cgpt_instructions=cgpt.instructions
                )
                return messages_of_sysprompt
        except Exception:
            raise DefaultCGPTRetreiverError
