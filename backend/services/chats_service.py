from sqlmodel import Session, select
from openai import OpenAI
from models.models import ConversationDB, CustomGptsDB, MessageDB
from schemas.common import (
    ChatHistory,
    ChatSummary,
    SimplifiedMessage,
    UserMessageRequest,
    AssistantMessage,
)

client = OpenAI()


def retrieve_chat_history_by_id(chat_id: int, session: Session) -> ChatHistory:
    conv = session.get(ConversationDB, chat_id)
    msgs = [
        SimplifiedMessage(role=msg.role, message=msg.content or "")
        for msg in conv.messages
        if msg.role
        in (
            "user",
            "assistant",
        )  # drop 'system' since Role enum only has user|assistant
    ]
    return ChatHistory(custom_gpt_id=conv.customgpt_id, messages=msgs)


def retrieve_chat_summaries_list(session: Session) -> list[ChatSummary]:
    stmt = select(ConversationDB)
    convs = session.exec(stmt).all()
    summaries: list[ChatSummary] = []
    for conv in convs:
        # Determine GPT name or default to "vanilla"
        if conv.customgpt_id is None:
            gpt_name = "vanilla"
        else:
            gpt = session.get(CustomGptsDB, conv.customgpt_id)
            gpt_name = gpt.name or "vanilla"

        # Build summary as "<gpt_name> <conversation_id>"
        summary_text = f"GPT {gpt_name}: conv {conv.id}"
        summaries.append(ChatSummary(chat_id=conv.id, chat_summary=summary_text))

    return summaries


def send_user_message_service(
    request: UserMessageRequest,
    session: Session,
) -> AssistantMessage:
    # create or fetch conversation
    if request.conversation_id is None:
        conv = ConversationDB(customgpt_id=request.custom_gpt_id)
        session.add(conv)
        session.commit()
        session.refresh(conv)
    else:
        conv = session.get(ConversationDB, request.conversation_id)

    # persist user message
    user_msg = MessageDB(
        conversation_id=conv.id,
        role=request.request_message.role.value,
        content=request.request_message.message,
    )
    session.add(user_msg)
    session.commit()

    # TODO: insert system‐prompt logic for Custom GPT here
    # Get the CustomGPT given the id from the request
    customgpt = session.get(CustomGptsDB, request.custom_gpt_id)
    if not customgpt:
        raise HTTPException(status_code=404, detail="CustomGPT not found")
    system_message_content = f"""Du bist ein CustomGPT namens {customgpt.name} und bist für folgendes zuständig: {customgpt.custom_gpt_description}. Dafür befolgst du folgende Anweisungen: {customgpt.custom_gpt_instructions}"""

    system_message = [{"role": "system", "content": system_message_content}]
    # build history for OpenAI
    history = session.exec(
        select(MessageDB).where(MessageDB.conversation_id == conv.id)
    ).all()
    messages = system_message + [
        {"role": m.role, "content": m.content} for m in history
    ]

    # call OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
    )
    assistant_text = response.choices[0].message.content or ""

    # persist assistant reply
    assistant_msg = MessageDB(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_text,
    )
    session.add(assistant_msg)
    session.commit()

    return AssistantMessage(
        conversation_id=conv.id,
        response_message=SimplifiedMessage(
            role=assistant_msg.role, message=assistant_text
        ),
    )
