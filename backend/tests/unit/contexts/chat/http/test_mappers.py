import pytest

from src.contexts.chat.application.ports.chat_queries import (
    ConversationOverviewDTO,
    ConversationTextOnlyDTO,
    RoleDTO,
    TextMessageDTO,
)
from src.interface.http.mappers_data_and_exceptions.chat.chat_queries_classes_and_exceptions import (
    conversationOverviewsDTO_to_chatSummaries,
    conversationTextOnlyDTO_to_chat,
)
from src.interface.http.schemas.chat.chat_queries import (
    ChatHistory,
    ChatSummary,
    RoleQuery,
)


def test_conversationOverviewsDTO_to_chatSummaries():
    conv_overviews: list[ConversationOverviewDTO] = []
    chat_summaries: list[ChatSummary] = conversationOverviewsDTO_to_chatSummaries(
        conv_overviews=conv_overviews
    )
    assert chat_summaries == []

    conv_overviews.append(ConversationOverviewDTO(id="1", title="t1"))
    conv_overviews.append(ConversationOverviewDTO(id="2", title="t2"))
    chat_summaries: list[ChatSummary] = conversationOverviewsDTO_to_chatSummaries(
        conv_overviews=conv_overviews
    )
    assert chat_summaries[0].chat_id == "1"
    assert chat_summaries[0].chat_summary == "t1"
    assert chat_summaries[1].chat_id == "2"
    assert chat_summaries[1].chat_summary == "t2"


def test_conversationTextOnlyDTO_to_chat_happy_path():
    dto = ConversationTextOnlyDTO(
        customgpt_id="cgpt-123",
        messages=[
            TextMessageDTO(role=RoleDTO.user, text="hello"),
            TextMessageDTO(role=RoleDTO.assistant, text="hi there"),
        ],
    )

    chat = conversationTextOnlyDTO_to_chat(dto)

    assert isinstance(chat, ChatHistory)
    assert chat.custom_gpt_id == "cgpt-123"
    assert [m.role for m in chat.messages] == [RoleQuery.user, RoleQuery.assistant]
    assert [m.message for m in chat.messages] == ["hello", "hi there"]


def test_conversationTextOnlyDTO_to_chat_raises_on_system():
    dto = ConversationTextOnlyDTO(
        customgpt_id=None,
        messages=[
            TextMessageDTO(role=RoleDTO.user, text="u1"),
            TextMessageDTO(role=RoleDTO.system, text="SYS SHOULD BREAK"),
        ],
    )

    with pytest.raises(RuntimeError) as exc:
        conversationTextOnlyDTO_to_chat(dto)

    assert str(exc.value) == "Should not be used on data cotaining system prompts"
