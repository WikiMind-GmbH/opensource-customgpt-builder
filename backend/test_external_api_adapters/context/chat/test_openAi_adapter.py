from src.contexts.chat.infrastructure.adapters.openai_adapter import OpenaiAdapter

from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    LlmPort,
    MessageDTOllm,
    NoAssistantResponse,
    RoleDTOllm,
)

import pytest


def test_openai_adapter():
    openai_adapter: OpenaiAdapter = OpenaiAdapter(model_name="gpt-4.1-mini")

    sys_prompt: list[MessageDTOllm] = []

    sys_prompt.append(
        MessageDTOllm(
            role=RoleDTOllm.system,
            imageUrlOrText="Please answer only with either `Yes` or `No`",
        )
    )
    sys_prompt.append(
        MessageDTOllm(role=RoleDTOllm.user, imageUrlOrText="Is 10 divisible by 2?")
    )
    sys_prompt.append(MessageDTOllm(role=RoleDTOllm.assistant, imageUrlOrText="Yes"))

    msgs: list[MessageDTOllm] = []
    msgs.append(
        MessageDTOllm(role=RoleDTOllm.user, imageUrlOrText="Is 4 divisible by 2?")
    )

    res: str = openai_adapter.get_assistant_text_response(
        messages_excluding_sys_prompt=msgs, cgpt_systemprompt=sys_prompt
    )

    assert res == "Yes"
