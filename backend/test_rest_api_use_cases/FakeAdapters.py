from dataclasses import dataclass

from src.contexts.chat.application.ports.llm_port import LlmPort, MessageDTOllm


@dataclass
class FnxCallArgs:
    messages_excluding_sys_prompt: list[MessageDTOllm]
    cgpt_systemprompt: list[MessageDTOllm]


class FakeLLMAdapter(LlmPort):
    def __init__(self):
        self._function_call_parameters: list[FnxCallArgs] = []

    def get_assistant_text_response(
        self,
        messages_excluding_sys_prompt: list[MessageDTOllm],
        cgpt_systemprompt: list[MessageDTOllm],
    ) -> str:
        self.function_call_parameters.append(
            FnxCallArgs(
                messages_excluding_sys_prompt=messages_excluding_sys_prompt,
                cgpt_systemprompt=cgpt_systemprompt,
            )
        )
        return f"assistant_response {len(self._function_call_parameters)}"

    @property
    def function_call_parameters(self):
        return self._function_call_parameters
