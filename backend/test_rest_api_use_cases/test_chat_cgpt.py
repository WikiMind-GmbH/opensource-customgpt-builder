from fastapi import Response
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import httpx
from pydantic import TypeAdapter
from src.interface.http.schemas.chat.chat_queries import ChatHistory, ChatSummary
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.schemas.customGPTs.customGPT_commands import CustomGptToCreate
from src.interface.http.schemas.chat.chat_commands import (
    AssistantMessage,
    ContinueChatRequest,
    NewChatRequest,
)

# def test_tmp(test_client:TestClient):
#     # Currently no conversations
#     res: httpx.Response = test_client.get("/chat/get-chat-summaries")
#     print(res.status_code, res.text)
#     print(res)


def test_create_cgpt_and_start_conv_delete_cgpt(test_client: TestClient):
    # Currently no conversations
    res: httpx.Response = test_client.get("/chat/get-chat-summaries")
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
    res: httpx.Response = test_client.post(
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
        request_message=request_message_1, custom_gpt_id=cgpt_id
    )
    res: httpx.Response = test_client.post(
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
        request_message=request_message_2, conversation_id=conv_id
    )
    res: httpx.Response = test_client.post(
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
    res: httpx.Response = test_client.get(
        "/chat/chat-history-by-id", params={"chat_id": conv_id}
    )
    assert res.status_code == 200, res.text
    print(res)
    res_json = res.json()
    print(res_json)
    chat_history_1: ChatHistory = ChatHistory.model_validate(res_json)
    assert chat_history_1.custom_gpt_id == cgpt_id
    assert [simplified_msg.message for simplified_msg in chat_history_1.messages] == [
        request_message_1,
        msg_assistant_1,
        request_message_2,
        msg_assistant_2,
    ]


    # ----------CONVERSATION WITH OTHER CGPT----------------------------------------------
    res: httpx.Response = test_client.post(
        "/customgpts/create-custom-gpt", json=jsonable_encoder(cgpt_to_create)
    )
    assert res.status_code == 200, res.text
    cmd = CommandResult.model_validate(res.json())
    cgpt_id_2: str | None = cmd.resource_id

    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id=cgpt_id_2
    )
    res: httpx.Response = test_client.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    assistant_message: AssistantMessage = AssistantMessage.model_validate(res_json)
    conv_id_other_cgpt: str = assistant_message.conversation_id


    # ----------CONVERSATION WITHOUT ANY CGPT----------------------------------------------
    request_message_1: str = "User message 1"
    new_chat_req: NewChatRequest = NewChatRequest(
        request_message=request_message_1, custom_gpt_id=None
    )
    res: httpx.Response = test_client.post(
        "/chat/send-user-message", json=jsonable_encoder(new_chat_req)
    )
    assert res.status_code == 200, res.text
    res_json = res.json()
    assistant_message: AssistantMessage = AssistantMessage.model_validate(res_json)
    conv_id_no_cgpt: str = assistant_message.conversation_id

    # ----------CONFIRM: ALL CONV ARE LISTED IN ORDER OF LAST MSG-----------------
    res: httpx.Response = test_client.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    assert [conv_id_no_cgpt, conv_id_other_cgpt, conv_id] == [summary.chat_id for summary in summaries]
    print(summaries)

    # ----------CONFIRM: DELETING CGPT (ONLY) DELETES CONV WITH THAT CGPT-----------------

    # Delete cgpt 1 via cgpt endpoint
    res: httpx.Response = test_client.delete(
        "/customgpts/delete-custom-gpt", params={"gpt_id": cgpt_id}
    )
    assert res.status_code == 200, res.text
    
    # Deleting cgpt should delete the conv
    res: httpx.Response = test_client.get("/chat/get-chat-summaries")
    assert res.status_code == 200, res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        res.json()
    )
    print(summaries)

    assert [conv_id_no_cgpt, conv_id_other_cgpt] == [summary.chat_id for summary in summaries]


