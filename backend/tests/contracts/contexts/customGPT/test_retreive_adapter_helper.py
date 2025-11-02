from src.contexts.chat.application.ports.customgpt_instructions_retreiver import MessageDTORetreiver
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import cgpt_infos_to_sysprompt
import pytest

def test_instruction_and_name_in_sysprompt():
    cgpt_name: str = "CGPT_NAME"
    cgpt_instructions:str = "You are a coding assistant. Please ask for clarification if needed"

    sys_prompt: list[MessageDTORetreiver] = cgpt_infos_to_sysprompt(cgpt_name=cgpt_name, cgpt_instructions = cgpt_instructions)
    sys_prompt_text = "\n".join(m.text_content for m in sys_prompt)
    assert cgpt_name in sys_prompt_text
    assert cgpt_instructions in sys_prompt_text