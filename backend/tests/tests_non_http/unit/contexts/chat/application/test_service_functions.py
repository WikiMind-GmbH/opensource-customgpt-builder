# ------------ Continue conversation------------
import pytest

from src.contexts.chat.application.orchestration import (
    continue_conversation,
    create_conversation,
)
from src.contexts.chat.application.ports.chat_repo import ConversationNotFoundError
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import Conversation, Role
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.shared.typing_aliases import Factory
from tests.fake_adapters.context_chat_port.fake_doc_snippet_retriever import (
    FakeRelevantDocSnippetRetreiverAdapter,
)
from tests.fake_adapters.context_chat_port.fake_llm_adapter import FakeLLMAdapter


class TestCreateConversation:
    @staticmethod
    def test_create_conversation_cgpt_registered_correctly(
        conv_uow_factory: Factory[ConversationUOW],
    ):
        conv_id_no_cgpt: str = create_conversation(conv_uow_factory=conv_uow_factory)
        cgpt_id = "cgpt_id"
        conv_id_cgpt: str = create_conversation(
            conv_uow_factory=conv_uow_factory, cgpt_id=cgpt_id
        )
        with conv_uow_factory() as uow:
            conv_no_cgpt: Conversation = uow.conversation_repo.get(conv_id_no_cgpt)
            conv_cgpt: Conversation = uow.conversation_repo.get(conv_id_cgpt)
            assert conv_no_cgpt.customGPT_id is None
            assert conv_cgpt.customGPT_id == cgpt_id


class TestContinueConversationNoRag:
    @staticmethod
    def test_continue_conversation_messages_are_added_to_conversation_no_rag(
        conv_uow_factory: Factory[ConversationUOW],
        cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
        fake_llm_adapter_factory: Factory[LlmPort],
        retrieve_doc_snippets: RelevantDocSnippetRetreiverPort,  # for needed fakes and wiring, see knowledge orchestration
    ):
        with conv_uow_factory() as uow:
            conv: Conversation = uow.conversation_repo.create_conversation()
            conv_id = conv.id
            uow.commit()
        user_text: str = "user_text"
        assistant_text: str = continue_conversation(
            user_message=user_text,
            conv_id=conv_id,
            conv_uow_factory=conv_uow_factory,
            cgpt_retreiver=cgpt_retreiver_factory(),
            llm_adapter=fake_llm_adapter_factory(),
            retrieve_doc_snippets=retrieve_doc_snippets,
            use_rag=False,
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

    @staticmethod
    def test_continue_conversation_not_found_error_raised_for_non_existent_conv_id(
        conv_uow_factory: Factory[ConversationUOW],
        cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
        fake_llm_adapter_factory: Factory[LlmPort],
        retrieve_doc_snippets: RelevantDocSnippetRetreiverPort,  # for needed fakes and wiring, see knowledge orchestration
    ):
        with pytest.raises(ConversationNotFoundError):
            continue_conversation(
                user_message="user_text",
                conv_id="non_existent_id",
                conv_uow_factory=conv_uow_factory,
                cgpt_retreiver=cgpt_retreiver_factory(),
                llm_adapter=fake_llm_adapter_factory(),
                retrieve_doc_snippets=retrieve_doc_snippets,
                use_rag=False,
            )

    @staticmethod
    def test_continue_conversation_llm_adapter_containes_user_message_and_cgpt_infos_if_available(
        conv_uow_factory: Factory[ConversationUOW],
        cgpt_uow_factory: Factory[CgptUOW],
        cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
        fake_llm_adapter_factory: Factory[FakeLLMAdapter],
        retrieve_doc_snippets: RelevantDocSnippetRetreiverPort,  # for needed fakes and wiring, see knowledge orchestration
    ):
        # Case 1: Conv doesn't have cgpt

        fake_llm_adapter_cgpt_exists: FakeLLMAdapter = fake_llm_adapter_factory()
        user_message = "user_text"
        with conv_uow_factory() as uow:
            conv: Conversation = uow.conversation_repo.create_conversation()
            conv_id: str = conv.id
            uow.commit()
        _: str = continue_conversation(
            user_message=user_message,
            conv_id=conv_id,
            conv_uow_factory=conv_uow_factory,
            cgpt_retreiver=cgpt_retreiver_factory(),
            llm_adapter=fake_llm_adapter_cgpt_exists,
            retrieve_doc_snippets=retrieve_doc_snippets,
            use_rag=False,
        )
        msgs_passed_to_llm_adapter = (
            fake_llm_adapter_cgpt_exists.function_call_parameters[0].messages_dto
        )
        content_of_messages = str(
            [msg.imageUrlOrText for msg in msgs_passed_to_llm_adapter]
        )

        assert user_message in content_of_messages
        # Case 2: Conv has cgpt
        fake_llm_adapter_cgpt_exists: FakeLLMAdapter = fake_llm_adapter_factory()
        cgpt_name = "cgpt_1"
        cgpt_instructions = "Do sth"
        user_message = "user_text"
        with cgpt_uow_factory() as uow:
            cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
                name=cgpt_name, instructions=cgpt_instructions
            )
            cgpt_id: str = cgpt.id
            uow.commit()

        with conv_uow_factory() as uow:
            conv: Conversation = uow.conversation_repo.create_conversation(
                cgpt_id=cgpt_id
            )
            conv_id: str = conv.id
            uow.commit()
        _: str = continue_conversation(
            user_message=user_message,
            conv_id=conv_id,
            conv_uow_factory=conv_uow_factory,
            cgpt_retreiver=cgpt_retreiver_factory(),
            llm_adapter=fake_llm_adapter_cgpt_exists,
            retrieve_doc_snippets=retrieve_doc_snippets,
            use_rag=False,
        )
        msgs_passed_to_llm_adapter = (
            fake_llm_adapter_cgpt_exists.function_call_parameters[0].messages_dto
        )
        content_of_messages = str(
            [msg.imageUrlOrText for msg in msgs_passed_to_llm_adapter]
        )
        assert user_message in content_of_messages
        assert cgpt_name in content_of_messages
        assert cgpt_instructions in content_of_messages


class TestContinueConversationWithRag:
    @staticmethod
    def test_use_rag_and_cgpt_with_files_leads_to_added_system_message_with_doc_snippet_added(
        conv_uow_factory: Factory[ConversationUOW],
        cgpt_uow_factory: Factory[CgptUOW],
        cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiver],
        fake_llm_adapter_factory: Factory[FakeLLMAdapter],
        retrieve_doc_snippets: FakeRelevantDocSnippetRetreiverAdapter,  # for needed fakes and wiring, see knowledge orchestration
    ):
        with cgpt_uow_factory() as uow:
            cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
                name="cgpt_name", instructions="cgpt_instructions"
            )
            cgpt_id: str = cgpt.id
            uow.commit()
        retrieve_doc_snippets.set_fake_snippet_to_return_for_cgpt_id(
            cgpt_id=cgpt_id, returned_snippets_texts=["some_text"]
        )
        with conv_uow_factory() as uow:
            conv: Conversation = uow.conversation_repo.create_conversation(
                cgpt_id=cgpt_id
            )
            conv_id = conv.id
            uow.commit()
        cgpt_id_of_conv = conv.customGPT_id
        assert cgpt_id_of_conv is not None
        user_text: str = "user_text"
        _: str = continue_conversation(
            user_message=user_text,
            conv_id=conv_id,
            conv_uow_factory=conv_uow_factory,
            cgpt_retreiver=cgpt_retreiver_factory(),
            llm_adapter=fake_llm_adapter_factory(),
            retrieve_doc_snippets=retrieve_doc_snippets,
            use_rag=True,
        )
        # retrieve_doc_snippets.retrieve_doc_snippets(query_text="asd", cgpt_id=cgpt_id) <- das führt zu bestehen des tests, also musses problem außerhalb liegen
        assert (
            retrieve_doc_snippets.get_number_of_times_retrieve_doc_snippets_got_called_with(
                cgpt_id=cgpt_id
            )
            == 1 * 2
        )
