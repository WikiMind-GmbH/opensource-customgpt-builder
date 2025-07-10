from schemas.common import ChatHistory, ChatSummary, Role, SimplifiedMessage
from fastapi import HTTPException
import logging


# Configure logging (optional but better than print)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def retrieve_chat_history_by_id(chat_id: int) -> ChatHistory:
    """Retreives the history of chat messages for a particular chat_id

    Args:
        chat_id (int): id of a selected chat from the chat list

    Returns:
        ChatHistory: Returns Model ID and list of Messages
    """

    logger.info(f"Retrieving chat history for chat_id = {chat_id}")
    
    try:
        response_status = 200

        if response_status != 200:
            raise HTTPException(status_code=404, detail="Chat history not found")

        chat_history_list = ChatHistory(
            custom_gpt_id=0,
            messages=[
                SimplifiedMessage(role=Role.user, message="Hello"),
                SimplifiedMessage(role=Role.assistant, message="Hi, how can I help you?"),
            ],
        )
        return chat_history_list
    
    except HTTPException as http_err:
        logger.error(f"HTTP error: {http_err.detail}")
        raise

    except Exception as err:
        logger.exception("Unexpected error occurred while retrieving chat history", err)
        raise HTTPException(status_code=500, detail="Internal server error")


async def retrieve_chat_summaries_list() -> list[ChatSummary]:
    """Retrieves the list of chat summaries in one liner

    Returns:
        list[ChatSummary]: Returns Chat summaries with chat_id
    """
    logger.info(f"Retrieving chat summaries")
    try: 
        response_status = 200

        if response_status!= 200:
            raise HTTPException(status_code=404, detail="Chat Summaries not found")
         
        chat_summary = [
            ChatSummary(chat_id=1, chat_summary="summary1"),
            ChatSummary(chat_id=2, chat_summary="summary2"),
            ChatSummary(chat_id=3, chat_summary="summary3"),
        ]
        return chat_summary
    
    except HTTPException as http_err:
        logger.error(f"HTTP error: {http_err.detail}")
        raise

    except Exception as err:
        logger.exception("Unexpected error occurred while retrieving chat summaries list", err)
        raise HTTPException(status_code=500, detail="Internal server error")
