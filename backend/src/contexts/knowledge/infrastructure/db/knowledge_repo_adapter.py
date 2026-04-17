import hashlib
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.contexts.chat.domain.models import Conversation
from src.contexts.knowledge.application.ports.knowledge_repo import (
    FileDoesNotExistError,
    KnowledgeRepo,
)
from src.contexts.knowledge.domain.models import UploadedTextLikeFile


class SQLAlchemyKnowledgeRepository(KnowledgeRepo):
    # Helper functions
    def calculate_hash(self, file: UploadFile):
        
    def create_new_file_and_return_file_bytes_if_hash_doesnt_exist_yet(self, uploadfile: UploadFile):
        file_content: bytes = uploadfile.file.read()
        file_name = uploadfile.filename
        


    def __init__(self, session: Session) -> None:
        self._session = session

    def get_file(self, file_id: str) -> UploadedTextLikeFile:
        conv = self._session.get(UploadedTextLikeFile, file_id)
        if conv is None:
            raise FileDoesNotExistError
        return conv

    def add_cgpt_to_file_permissions(self, cgpt_id: str, file_id: str): ...
    def create_new_file(self, file: UploadFile) -> UploadedTextLikeFile: ...

    def get_ids_of_all_files_this_cgpt_has_access_to(self, cgpt_id: str): ...

    # def delete(self, conversation: Conversation):
    #     self._session.delete(conversation)

    # def delete_conversations_with_cgpt(self, cgpt_id: str):
    #     stmt = delete(Conversation).where(
    #         conversations.c._customGPT_id == cgpt_id
    #     )  # <- core style working with tables
    #     # stmt = delete(Conversation).where(
    #     #     Conversation._customGPT_id == cgpt_id
    #     # )  # <- ORM style working with our mapped domain models
    #     self._session.execute(stmt)


# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.


class KnowledgeRepo(Protocol):
    def get_file(self, file_id: str) -> UploadedTextLikeFile: ...
    def check_if_file_already_exists_via_hash(self, upload_file: UploadFile): ...

    """uses hash to check if file already exists"""

    def add_cgpt_to_file_permissions(self, cgpt_id: str, file_id: str): ...
    def create_new_file(self, file: UploadFile) -> UploadedTextLikeFile: ...

    def get_ids_of_all_files_this_cgpt_has_access_to(self, cgpt_id: str): ...
