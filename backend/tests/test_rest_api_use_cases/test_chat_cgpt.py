import httpx
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from src.interface.http.schemas.chat.chat_commands import (
    AssistantMessage,
    ContinueChatRequest,
    NewChatRequest,
)
from src.interface.http.schemas.chat.chat_queries import ChatHistory, ChatSummary
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.schemas.customGPTs.customGPT_commands import (
    CustomGptToCreate,
    CustomGptToEdit,
)
from src.interface.http.schemas.customGPTs.customGPT_queries import (
    CustomGPTInfosSchema,
    CustomGPTOverviewSchema,
)


def test_create_cgpt_start_conv_chat_then_delete_cgpt(
    test_client_fake_llm_adapter: TestClient,
):
    # Currently no conversations
    res: httpx.Response = test_client_fake_llm_adapter.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    assert summaries == []

    # ----------CONVERSATION WITH CGPT 1-----------------
    # Create cgpt
    name = "name"
    desc = "desc"
    instructions = "Instructions"
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

    # Start chatting with it
    # First message
    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id=cgpt_id, use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    assistant_message: AssistantMessage = AssistantMessage.model_validate(res_json)
    msg_assistant_1: str = assistant_message.response_message.message
    conv_id: str = assistant_message.conversation_id
    assert msg_assistant_1 == "assistant_response 1"
    # Second message
    request_message_2: str = "User message 2"
    continue_chat_req: ContinueChatRequest = ContinueChatRequest(
        request_message=request_message_2, conversation_id=conv_id, use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(continue_chat_req)
    )
    assert res.status_code == 200, res.text
    msg_assistant_2: str = AssistantMessage.model_validate(
        res.json()
    ).response_message.message
    assert (
        msg_assistant_2 == "assistant_response 1"
    )  # New adapter from factory per endpoint -> same message

    # Check conversation: Msgs, cgpt_id correct
    res: httpx.Response = test_client_fake_llm_adapter.get(
        "/chat/chat-history-by-id", params={"chat_id": conv_id}
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    chat_history_1: ChatHistory = ChatHistory.model_validate(res_json)
    assert chat_history_1.custom_gpt_id == cgpt_id
    assert [simplified_msg.message for simplified_msg in chat_history_1.messages] == [
        request_message_1,
        msg_assistant_1,
        request_message_2,
        msg_assistant_2,
    ]

    # ----------CONVERSATION WITH OTHER CGPT----------------------------------------------
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/customgpts/create-custom-gpt", json=jsonable_encoder(cgpt_to_create)
    )
    assert res.status_code == 200, res.text
    cmd = CommandResult.model_validate(res.json())
    cgpt_id_2: str | None = cmd.resource_id

    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id=cgpt_id_2, use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    assistant_message: AssistantMessage = AssistantMessage.model_validate(res_json)
    conv_id_other_cgpt: str = assistant_message.conversation_id

    # ----------CONVERSATION WITHOUT ANY CGPT----------------------------------------------
    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id=None, use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    assistant_message: AssistantMessage = AssistantMessage.model_validate(res_json)
    conv_id_no_cgpt: str = assistant_message.conversation_id

    # ----------CONFIRM: ALL CONV ARE LISTED IN ORDER OF LAST MSG-----------------
    res: httpx.Response = test_client_fake_llm_adapter.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    assert [conv_id_no_cgpt, conv_id_other_cgpt, conv_id] == [
        summary.chat_id for summary in summaries
    ]

    # ----------CONFIRM: DELETING CGPT (ONLY) DELETES CONV WITH THAT CGPT-----------------

    # Delete cgpt 1 via cgpt endpoint
    res: httpx.Response = test_client_fake_llm_adapter.delete(
        "/customgpts/delete-custom-gpt", params={"gpt_id": cgpt_id}
    )
    assert res.status_code == 200, res.text

    # Deleting cgpt should delete the conv
    res: httpx.Response = test_client_fake_llm_adapter.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )

    assert [conv_id_no_cgpt, conv_id_other_cgpt] == [
        summary.chat_id for summary in summaries
    ]


def test_conv_messages_ordered_by_creation_chat_summaries_by_last_message(
    test_client_fake_llm_adapter: TestClient,
):
    # --- Create initial conversation with two messages ---
    # 1) first message -> creates conversation
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message",
        json=jsonable_encoder(
            NewChatRequest(request_message="u1", custom_gpt_id=None, use_rag=False)
        ),
    )
    assert res.status_code == 200, res.text
    am1 = AssistantMessage.model_validate(res.json())
    conv_id_initial = am1.conversation_id
    a1 = am1.response_message.message

    # 2) second message -> continue same conversation
    res = test_client_fake_llm_adapter.post(
        "/chat/send-user-message",
        json=jsonable_encoder(
            ContinueChatRequest(
                request_message="u2", conversation_id=conv_id_initial, use_rag=False
            )
        ),
    )
    assert res.status_code == 200, res.text
    am2 = AssistantMessage.model_validate(res.json())
    a2 = am2.response_message.message

    # --- Check: chat history is ordered NEWEST → OLDEST ---
    res = test_client_fake_llm_adapter.get(
        "/chat/chat-history-by-id", params={"chat_id": conv_id_initial}
    )
    assert res.status_code == 200, res.text
    history_initial = ChatHistory.model_validate(res.json())
    # expected: u2/a2 first, then u1/a1
    assert [m.message for m in history_initial.messages] == ["u1", a1, "u2", a2]

    # --- Create second conversation with a single (newer) message ---
    res = test_client_fake_llm_adapter.post(
        "/chat/send-user-message",
        json=jsonable_encoder(
            NewChatRequest(request_message="uX", custom_gpt_id=None, use_rag=False)
        ),
    )
    assert res.status_code == 200, res.text
    conv_id_other = AssistantMessage.model_validate(res.json()).conversation_id

    # --- Summaries ordered by last_message_at ---
    res = test_client_fake_llm_adapter.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    assert [s.chat_id for s in summaries] == [conv_id_other, conv_id_initial], summaries

    # --- Add a new message to the initial conversation to make it the newest ---
    res = test_client_fake_llm_adapter.post(
        "/chat/send-user-message",
        json=jsonable_encoder(
            ContinueChatRequest(
                request_message="u3", conversation_id=conv_id_initial, use_rag=False
            )
        ),
    )
    assert res.status_code == 200, res.text
    # a3 = AssistantMessage.model_validate(res.json()).response_message.message

    # --- Summaries should now flip: [initial (newest), other] ---
    res = test_client_fake_llm_adapter.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    assert [s.chat_id for s in summaries] == [conv_id_initial, conv_id_other], summaries


def test_cgpt_creation_editing_querying_functionality(
    test_client_fake_llm_adapter: TestClient,
):
    # Create three cgpts -every one except the second one with the same parameters
    # list them with retreive_all_custom_gpts -order should be third, second first
    # Retreive the second one, check its values
    # Edit the second one to have the same values as the other ones
    # delete the third one
    # check summaries: shows only first and second
    # retreive initial and first each via get_custom_gpt_by_id: check: values are correct (both the same)

    # ---------- Create CGPT #1 (A) ----------
    create_A = CustomGptToCreate(
        custom_gpt_name="A",
        custom_gpt_description="desc",
        custom_gpt_instructions="inst",
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/customgpts/create-custom-gpt", json=jsonable_encoder(create_A)
    )
    assert res.status_code == 200, res.text
    A_id = CommandResult.model_validate(res.json()).resource_id

    # ---------- Create CGPT #2 (B) - different values ----------
    create_B = CustomGptToCreate(
        custom_gpt_name="B",
        custom_gpt_description="desc_B",
        custom_gpt_instructions="inst_B",
    )
    res = test_client_fake_llm_adapter.post(
        "/customgpts/create-custom-gpt", json=jsonable_encoder(create_B)
    )
    assert res.status_code == 200, res.text
    B_id = CommandResult.model_validate(res.json()).resource_id
    assert B_id is not None

    # ---------- Create CGPT #3 (C) - same as A ----------
    create_C = CustomGptToCreate(
        custom_gpt_name="A",
        custom_gpt_description="desc",
        custom_gpt_instructions="inst",
    )
    res = test_client_fake_llm_adapter.post(
        "/customgpts/create-custom-gpt", json=jsonable_encoder(create_C)
    )
    assert res.status_code == 200, res.text
    C_id = CommandResult.model_validate(res.json()).resource_id

    # ---------- List: expect created_at DESC -> [C, B, A] ----------
    assert None not in [A_id, B_id, C_id]
    res = test_client_fake_llm_adapter.get("/customgpts/retreive-all-custom-gpts")
    assert res.status_code == 200, res.text
    overviews: list[CustomGPTOverviewSchema] = TypeAdapter(
        list[CustomGPTOverviewSchema]
    ).validate_python(res.json())
    ids = [o.custom_gpt_id for o in overviews]
    assert ids[:3] == [C_id, B_id, A_id], ids

    # ---------- Get B by id; verify distinct values ----------
    res = test_client_fake_llm_adapter.get(
        "/customgpts/get-custom-gpt-infos", params={"custom_gpt_id": B_id}
    )
    assert res.status_code == 200, res.text
    B_info = CustomGPTInfosSchema.model_validate(res.json())
    assert B_info.custom_gpt_id == B_id
    assert B_info.custom_gpt_name == "B"
    assert B_info.custom_gpt_description == "desc_B"
    assert B_info.custom_gpt_instructions == "inst_B"

    # ---------- Edit B to match A ----------
    edit_B = CustomGptToEdit(
        custom_gpt_id=B_id,
        custom_gpt_name="A",
        custom_gpt_description="desc",
        custom_gpt_instructions="inst",
    )
    res = test_client_fake_llm_adapter.post(
        "/customgpts/edit-custom-gpt", json=jsonable_encoder(edit_B)
    )
    assert res.status_code == 200, res.text
    assert CommandResult.model_validate(res.json()).resource_id == B_id

    # ---------- Delete C ----------
    res = test_client_fake_llm_adapter.delete(
        "/customgpts/delete-custom-gpt", params={"gpt_id": C_id}
    )
    assert res.status_code == 200, res.text

    # ---------- List again: only A and B remain (still ordered by created_at DESC) ----------
    res = test_client_fake_llm_adapter.get("/customgpts/retreive-all-custom-gpts")
    assert res.status_code == 200, res.text
    overviews = TypeAdapter(list[CustomGPTOverviewSchema]).validate_python(res.json())
    remaining_ids = [o.custom_gpt_id for o in overviews]
    assert C_id not in remaining_ids
    assert A_id in remaining_ids and B_id in remaining_ids

    # ---------- Get A and B by id; both now share the same values ----------
    res = test_client_fake_llm_adapter.get(
        "/customgpts/get-custom-gpt-infos", params={"custom_gpt_id": A_id}
    )
    assert res.status_code == 200, res.text
    A_info = CustomGPTInfosSchema.model_validate(res.json())

    res = test_client_fake_llm_adapter.get(
        "/customgpts/get-custom-gpt-infos", params={"custom_gpt_id": B_id}
    )
    assert res.status_code == 200, res.text
    B_info_after = CustomGPTInfosSchema.model_validate(res.json())

    assert (
        A_info.custom_gpt_name,
        A_info.custom_gpt_description,
        A_info.custom_gpt_instructions,
    ) == (
        "A",
        "desc",
        "inst",
    )
    assert (
        B_info_after.custom_gpt_name,
        B_info_after.custom_gpt_description,
        B_info_after.custom_gpt_instructions,
    ) == (
        "A",
        "desc",
        "inst",
    )


def test_cant_chat_with_non_existent_conv_or_cgpt(
    test_client_fake_llm_adapter: TestClient,
):
    continue_chat_req: ContinueChatRequest = ContinueChatRequest(
        request_message="request_message", conversation_id="IdontExist", use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(continue_chat_req)
    )
    assert res.status_code == 404

    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id="IdontExist", use_rag=False
    )
    res: httpx.Response = test_client_fake_llm_adapter.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 404
