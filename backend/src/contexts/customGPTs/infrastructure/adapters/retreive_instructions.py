from contexts.chat.application.ports.customgpt_instructions_retreiver import CustomGPTInstructionsRetreiver


class CustomGPTInstructionsRetreiverAdapter(CustomGPTInstructionsRetreiver):
    def __init__(self, cgpt_uow_factory: Callable[[]-> GPTUoW]) -> None:
        self.uow_factory = gpt_uow_factory
    
    def get_cgpt_instructions(self, gpt_id: str) -> str: # ToDo: add exception GPTDoesNotExist and add management here
        uow = self.uow_factory()
        instructions = get_instruction_service(uow, gpt_id)
        return instructions