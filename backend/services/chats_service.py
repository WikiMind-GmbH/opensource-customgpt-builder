from fastapi import HTTPException
from sqlmodel import Session, select
from openai import OpenAI
from exceptions import UnpersistedObjectError
from models.models import ConversationDB, CustomGptsDB, MessageDB
from schemas.common import (
    ChatHistory,
    ChatSummary,
    Role,
    SimplifiedMessage,
    UserMessageRequest,
    AssistantMessage,
)


client = OpenAI()

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
        if conv is None:
            raise UnpersistedObjectError(" Conv must exists and be created")

    # persist user message
    if conv.id is None:
            raise UnpersistedObjectError(" Conv must exists and be created")
    user_msg = MessageDB(
        conversation_id=conv.id,
        role=Role.user,
        content=request.request_message,
    )
    session.add(user_msg)
    session.commit()

    # TODO: insert system‐prompt logic for Custom GPT here
    # Get the CustomGPT given the id from the request
    customgpt = session.get(CustomGptsDB, request.custom_gpt_id)
    history = session.exec(
        select(MessageDB).where(MessageDB.conversation_id == conv.id)
    ).all()
    messages= [
        {"role": m.role, "content": m.content} for m in history
    ] 
    if customgpt:
        system_message_content = f"""Du bist ein CustomGPT namens {customgpt.name} und bist für folgendes zuständig: {customgpt.custom_gpt_description}. Dafür befolgst du folgende Anweisungen: {customgpt.custom_gpt_instructions}"""
        system_message= [{"role": "system", "content": system_message_content}]
        messages = system_message + messages
    # build history for OpenAI

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
