import os
from typing import Annotated

from fastapi import File, HTTPException, Query, UploadFile, status

from models.models import ConversationDB, CustomGptsDB
from schemas.common import UploadFileFileFormatValidated
from services.database import get_session


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value


#----------------------DEPENDENCY FUNCTIONS-------------------------------
 #-------------------------------------------------------------------------

 # DATABASE
async def conv_id_exists(conv_id: int) -> int:
    session = next(get_session())
    try:
        if session.get(ConversationDB, conv_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conv_id} not found",
            )
        return conv_id
    finally:
        session.close()

async def validate_gpt_id_exists(gpt_id: int) -> int:
    session = next(get_session())
    try:
        if session.get(CustomGptsDB, gpt_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {gpt_id} not found",
            )
        return gpt_id
    finally:
        session.close()

async def validateGptExistsQuery(gpt_id: int =Query())->int:
    return await validate_gpt_id_exists(gpt_id)

# SCHEMA VALIDATION
def validateFileFormat(
        files: Annotated[list[UploadFile], File(max_items=50)],
) -> list[UploadFileFileFormatValidated]:
    validated: list[UploadFileFileFormatValidated] = []
    for f in files:
        validated.append(UploadFileFileFormatValidated(uploadFile=f))
    return validated

 #-------------------------------------------------------------------------
 #-------------------------------------------------------------------------
