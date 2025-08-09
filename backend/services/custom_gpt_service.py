import os
from pathlib import Path
import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select
from backend_spanning_helpers import require_env, validate_gpt_id_exists
from models.models import ConversationDB, CustomGptsDB
from schemas.common import (
    ExistingCustomGPT,
    CreateOrEditCustomGPTStatus,
    CustomGptToCreateOrEdit,
    DeleteCustomGPTStatus,
    StandardResponse,
    StatusOfStandardResponse,
    UploadFileFileFormatValidated,
)

async def get_all_custom_gpts(session: Session) -> list[ExistingCustomGPT]:
    stmt = select(CustomGptsDB)
    gpts  = session.exec(stmt).all()
    return [
        ExistingCustomGPT(
            custom_gpt_id=gpt.id,
            custom_gpt_name=gpt.name,
            custom_gpt_description=gpt.custom_gpt_description,
            custom_gpt_instructions=gpt.custom_gpt_instructions,
            created_at=gpt.created_at,
        )
        for gpt in gpts
    ]

def retrieve_custom_gpt_by_id(custom_gpt_id: int, session: Session) -> ExistingCustomGPT:
    row = session.get(CustomGptsDB, custom_gpt_id)
    return ExistingCustomGPT(
        custom_gpt_id=row.id,
        custom_gpt_name=row.name,
        custom_gpt_description=row.custom_gpt_description,
        custom_gpt_instructions=row.custom_gpt_instructions,
        created_at=row.created_at,
    )

def delete_custom_gpt(custom_gpt_id: int, session: Session) -> DeleteCustomGPTStatus:

    conversations_with_custom_gpt = session.exec(select(ConversationDB).where(ConversationDB.customgpt_id == custom_gpt_id))
    custom_gpt = session.exec(select(CustomGptsDB).where(CustomGptsDB.id ==custom_gpt_id))
    session.delete(conversations_with_custom_gpt)
    session.delete(custom_gpt)
    session.commit()
    return DeleteCustomGPTStatus(custom_gpt_id=custom_gpt_id)

async def create_or_edit_custom_gpt(
    info: CustomGptToCreateOrEdit,
    session: Session,
) -> CreateOrEditCustomGPTStatus:
    if info.custom_gpt_id is None:
        row = CustomGptsDB(
            name=info.custom_gpt_name,
            custom_gpt_description=info.custom_gpt_description,
            custom_gpt_instructions=info.custom_gpt_instructions,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return CreateOrEditCustomGPTStatus(custom_gpt_id=row.id)
    else:
        await validate_gpt_id_exists(gpt_id=info.custom_gpt_id)
        row = session.get(CustomGptsDB, info.custom_gpt_id)
        row.name = info.custom_gpt_name
        row.custom_gpt_description = info.custom_gpt_description
        row.custom_gpt_instructions = info.custom_gpt_instructions
        session.add(row)
        session.commit()
        return CreateOrEditCustomGPTStatus(custom_gpt_id=info.custom_gpt_id)


async def add_files_to_gpt_helper(
    validated_custom_gpt_id: int,
    validated_files: list[UploadFileFileFormatValidated],
    session: Session,
)-> StandardResponse:
    max_size: int = int(require_env("UPLOAD_MAX_FILE_SIZE"))

    customGpt: ExistingCustomGPT = retrieve_custom_gpt_by_id(custom_gpt_id=validated_custom_gpt_id, session=session)
    files: list[UploadFile] = [file.uploadFile for file in validated_files]
    if not files:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No files supplied")
    for f in files:
        contents = await f.read()
        if len(contents) > max_size:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"{f.filename} exceeds 10 MB limit",
            )
        if f.filename is None:      # should be impossible
            raise RuntimeError("Invariant violated: value cannot be None here")
        base_dir = Path(require_env("LOADED_FILES_PATH")) / str(customGpt.custom_gpt_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        file_path:str = os.path.join(base_dir, f.filename)
        async with aiofiles.open(file_path, "wb") as out:
            await out.write(contents)

    return StandardResponse(res=StatusOfStandardResponse.success)


def list_loaded_files(custom_gpt_id: int) -> list[str]:
    """
    Ensure the folder for this GPT exists and return a sorted list of file names in it.
    If the folder is empty, returns [].
    """
    base_dir = Path(require_env("LOADED_FILES_PATH")) / str(custom_gpt_id)
    base_dir.mkdir(parents=True, exist_ok=True)  # create if missing

    # list only regular files (ignore subfolders)
    try:
        files = [p.name for p in base_dir.iterdir() if p.is_file()]
    except FileNotFoundError:
        # extremely rare (e.g., race condition on network FS); treat as empty
        return []

    return sorted(files)


