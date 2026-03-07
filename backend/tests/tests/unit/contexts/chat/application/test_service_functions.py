# ------------ Continue conversation------------
import pytest

from src.contexts.chat.application.ports.chat_repo import ConversationNotFoundError
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.application.service_functions import (
    continue_conversation,
    create_conversation,
)
from src.contexts.chat.domain.models import Conversation, Role
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.shared.typing_aliases import Factory
from tests.tests.unit.contexts.chat.application.FakeAdapters import FakeLLMAdapter


def test_create_conversation_cgpt_registered_correctly(
    conv_uow_factory: Factory[ConversationUOW],
):
    conv_id_no_cgpt: str = create_conversation(conv_uow=conv_uow_factory())
    cgpt_id = "cgpt_id"
    conv_id_cgpt: str = create_conversation(
        conv_uow=conv_uow_factory(), cgpt_id=cgpt_id
    )
    with conv_uow_factory() as uow:
        conv_no_cgpt: Conversation = uow.conversation_repo.get(conv_id_no_cgpt)
        conv_cgpt: Conversation = uow.conversation_repo.get(conv_id_cgpt)
        assert conv_no_cgpt.customGPT_id is None
        assert conv_cgpt.customGPT_id == cgpt_id


def test_continue_conversation_messages_are_added_to_conversation(
    conv_uow_factory: Factory[ConversationUOW],
    cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
    fake_llm_adapter_factory: Factory[LlmPort],
):
    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.create_conversation()
        conv_id = conv.id
        uow.commit()
    user_text: str = "user_text"
    assistant_text: str = continue_conversation(
        user_message="user_text",
        conv_id=conv_id,
        conv_uow=conv_uow_factory(),
        cgpt_retreiver=cgpt_retreiver_factory(),
        llm_adapter=fake_llm_adapter_factory(),
    )

    with (
        conv_uow_factory() as verification_uow
    ):  # explicitly not creating Message objects for slightly better decoupling from domain model
        conv: Conversation = verification_uow.conversation_repo.get(conv_id=conv_id)
        assert (
            conv.messages_excl_sysPrompt[-2].role == Role.user
            and conv.messages_excl_sysPrompt[-2].imageUrlOrText == user_text
        )

        assert (
            conv.messages_excl_sysPrompt[-1].role == Role.assistant
            and conv.messages_excl_sysPrompt[-1].imageUrlOrText == assistant_text
        )


def test_continue_conversation_not_found_error_raised_for_non_existent_conv_id(
    conv_uow_factory: Factory[ConversationUOW],
    cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
    fake_llm_adapter_factory: Factory[LlmPort],
):
    with pytest.raises(ConversationNotFoundError):
        continue_conversation(
            user_message="user_text",
            conv_id="non_existent_id",
            conv_uow=conv_uow_factory(),
            cgpt_retreiver=cgpt_retreiver_factory(),
            llm_adapter=fake_llm_adapter_factory(),
        )


def test_continue_conversation_llm_adapter_populated_correctly(
    conv_uow_factory: Factory[ConversationUOW],
    cgpt_uow_factory: Factory[CgptUOW],
    cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
    fake_llm_adapter_factory: Factory[FakeLLMAdapter],
):
    # Case 1: Conv has cgpt
    fake_llm_adapter_cgpt_exists: FakeLLMAdapter = fake_llm_adapter_factory()
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
            name="cgpt_1", instructions="Do sth"
        )
        cgpt_id: str = cgpt.id
        uow.commit()

    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        conv_id: str = conv.id
        uow.commit()
    _: str = continue_conversation(
        user_message="user_text",
        conv_id=conv_id,
        conv_uow=conv_uow_factory(),
        cgpt_retreiver=cgpt_retreiver_factory(),
        llm_adapter=fake_llm_adapter_cgpt_exists,
    )
    sysprompt_was_passed = (
        len(fake_llm_adapter_cgpt_exists.function_call_parameters[0].cgpt_systemprompt)
        > 0
    )

    assert sysprompt_was_passed

    # Case 2: Conv does not have cgpt
    fake_llm_adapter_cgpt_exists: FakeLLMAdapter = fake_llm_adapter_factory()

    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.create_conversation()
        conv_id: str = conv.id
        uow.commit()
    _: str = continue_conversation(
        user_message="user_text",
        conv_id=conv_id,
        conv_uow=conv_uow_factory(),
        cgpt_retreiver=cgpt_retreiver_factory(),
        llm_adapter=fake_llm_adapter_cgpt_exists,
    )
    sysprompt_was_passed = (
        len(fake_llm_adapter_cgpt_exists.function_call_parameters[0].cgpt_systemprompt)
        > 0
    )

    assert not sysprompt_was_passed
