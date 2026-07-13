from pathlib import Path

import httpx
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from src.interface.http.schemas.chat.chat_commands import (
    AssistantMessage,
    ContinueChatRequest,
    NewChatRequest,
)
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.schemas.customGPTs.customGPT_commands import CustomGptToCreate
from tests.documents_for_tests.test_documents import AvailableFiles, TestDocuments


class HelperMethods:
    @staticmethod
    def upload_document(
        client: TestClient, cgpt_ids: list[str], document: AvailableFiles
    ):
        path_of_doc: Path = TestDocuments.get_paths_for_test_files(document)
        form_data: dict[str, list[str]] = {
            "gpt_ids": cgpt_ids,
        }

        with path_of_doc.open("rb") as file:
            return client.post(
                "/knowledge/upload-files",
                files={
                    "uploadFile": (
                        path_of_doc.name,
                        file,
                        "text/plain",
                    )
                },
                data=form_data,
            )


class TestRagNecessitacesChatWithCustomGPTWithUploadedFiles:
    @staticmethod
    def test_use_rag_new_chat_with_no_cgpt_throws_error(
        test_client_fake_llm_adapter: TestClient,
    ):
        continue_chat_req: NewChatRequest = NewChatRequest(
            request_message="request_message",
            custom_gpt_id=None,
            use_rag=True,
        )
        res: httpx.Response = test_client_fake_llm_adapter.post(
            "/chat/send-user-message", json=jsonable_encoder(continue_chat_req)
        )
        assert res.status_code == 422

    @staticmethod
    def test_use_rag_continue_conversation_without_cgpt_throws_error(
        test_client_fake_llm_adapter: TestClient,
    ):
        new_chat_response: httpx.Response = test_client_fake_llm_adapter.post(
            "/chat/send-user-message",
            json=jsonable_encoder(
                NewChatRequest(
                    request_message="request_message",
                    use_rag=False,
                    custom_gpt_id=None,
                )
            ),
        )
        assert new_chat_response.status_code == 200, new_chat_response.text
        conversation_id = AssistantMessage.model_validate(
            new_chat_response.json()
        ).conversation_id

        res: httpx.Response = test_client_fake_llm_adapter.post(
            "/chat/send-user-message",
            json=jsonable_encoder(
                ContinueChatRequest(
                    request_message="request_message",
                    conversation_id=conversation_id,
                    use_rag=True,
                )
            ),
        )
        assert res.status_code == 422, res.text
        assert res.json() == {"detail": "RAG requires a custom GPT"}

    @staticmethod
    def test_use_rag_with_conversation_with_cgpt_without_uploaded_files_throws_error(
        test_client_fake_llm_adapter: TestClient,
    ):
        name = "name"
        desc = "desc"
        instructions = "Please answer questions in the shape provided."
        cgpt_to_create: CustomGptToCreate = CustomGptToCreate(
            custom_gpt_name=name,
            custom_gpt_description=desc,
            custom_gpt_instructions=instructions,
        )
        res: httpx.Response = test_client_fake_llm_adapter.post(
            "/customgpts/create-custom-gpt", json=jsonable_encoder(cgpt_to_create)
        )
        assert res.status_code == 200, res.text
        cmd = CommandResult.model_validate(res.json())
        cgpt_id: str | None = cmd.resource_id
        assert isinstance(cgpt_id, str)

        new_chat_req = NewChatRequest(
            request_message="request_message_1",
            custom_gpt_id=cgpt_id,
            use_rag=True,
        )

        res: httpx.Response = test_client_fake_llm_adapter.post(
            "/chat/send-user-message",
            json=jsonable_encoder(new_chat_req),
        )

        assert res.status_code == 400, res.text
        assert res.json() == {"detail": "At least one file id must be supplied"}


class EasyHappyPath:
    @staticmethod
    def test_context_retrieved_from_current_message_correctly(
        test_client_real_adapters: TestClient,
    ):
        # ToDo: create cgpt
        # Create cgpt
        name = "name"
        desc = "desc"
        instructions = "Please answer questions in the shape provided."
        cgpt_to_create: CustomGptToCreate = CustomGptToCreate(
            custom_gpt_name=name,
            custom_gpt_description=desc,
            custom_gpt_instructions=instructions,
        )
        res: httpx.Response = test_client_real_adapters.post(
            "/customgpts/create-custom-gpt", json=jsonable_encoder(cgpt_to_create)
        )
        assert res.status_code == 200, res.text
        cmd = CommandResult.model_validate(res.json())
        cgpt_id: str | None = cmd.resource_id
        assert isinstance(cgpt_id, str)
        # ToDo: create document with synthetic data + a prompt to answer questions from this.

        # ToDo: upload that file for this cgpt
        res = HelperMethods.upload_document(
            client=test_client_real_adapters,
            cgpt_ids=[cgpt_id],
            document=AvailableFiles.aurelian,
        )
        assert res.status_code == 200, res.text

        res = HelperMethods.upload_document(
            client=test_client_real_adapters,
            cgpt_ids=[cgpt_id],
            document=AvailableFiles.northstar,
        )
        assert res.status_code == 200, res.text

        indexed_questions_with_correct_answers = (
            TestDocuments.get_indexed_questions_and_indices_of_correct_answers(
                file=AvailableFiles.northstar,
                max_number_of_questions=5,
            )
        )

        request_message_1 = (
            f"{TestDocuments.yes_no_questions_prompt}\n\n"
            f"Questions:\n"
            f"{indexed_questions_with_correct_answers.indexed_questions}"
        )

        expected_answer = ",".join(
            [
                str(index)
                for index in indexed_questions_with_correct_answers.correct_answer_indices
            ]
        )

        new_chat_req = NewChatRequest(
            request_message=request_message_1,
            custom_gpt_id=cgpt_id,
            use_rag=True,
        )

        res: httpx.Response = test_client_real_adapters.post(
            "/chat/send-user-message",
            json=jsonable_encoder(new_chat_req),
        )

        assert res.status_code == 200, res.text

        assistant_message = AssistantMessage.model_validate(res.json())
        actual_answer = assistant_message.response_message.message.strip()

        assert actual_answer == expected_answer

    # @staticmethod
    # def test_retrieves_information_based_on_relevant_snippet_two_user_messages_ago():
    #     raise NotImplementedError(
    #         "Don't forget the tutorial regarding the orchestration layer not even taking care "
    #         "of raising errors that should be domain in the continue/create chat conversation use case fnx"
    #     )
    #     # ToDo: Same as above, but the 'clue' for the correct answer lies up two user messages ago.
