import httpx
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from src.contexts.shared.typing_aliases import Benchmark
from src.interface.http.schemas.chat.chat_commands import (
    AssistantMessage,
    ContinueChatRequest,
    NewChatRequest,
)
from src.interface.http.schemas.chat.chat_queries import ChatSummary


def minimal_new_conversation(test_client: TestClient) -> str:
    res: httpx.Response = test_client.post(
        "/chat/send-user-message",
        json=jsonable_encoder(NewChatRequest(request_message="u1", custom_gpt_id=None)),
    )
    assert res.status_code == 200, res.text
    am1 = AssistantMessage.model_validate(res.json())
    conv_id_initial = am1.conversation_id

    res = test_client.post(
        "/chat/send-user-message",
        json=jsonable_encoder(
            ContinueChatRequest(request_message="u2", conversation_id=conv_id_initial)
        ),
    )
    assert res.status_code == 200, res.text

    return conv_id_initial


@pytest.mark.performance
@pytest.mark.benchmark(
    group="group-name",
    min_time=0.1,
    max_time=0.5,
    min_rounds=10,
    disable_gc=True,
    warmup=False,
)
def test_perf_many_conversations(
    test_client: TestClient, benchmark: Benchmark
):  # BenchmarkFixture
    conv_id_initial = benchmark(minimal_new_conversation, test_client)

    summaries_res = test_client.get("/chat/get-chat-summaries")
    assert summaries_res.status_code == 200, summaries_res.text
    summaries: list[ChatSummary] = TypeAdapter(list[ChatSummary]).validate_python(
        summaries_res.json()
    )
    assert conv_id_initial in [
        summary.chat_id for summary in summaries
    ]  # where should this assert be -
