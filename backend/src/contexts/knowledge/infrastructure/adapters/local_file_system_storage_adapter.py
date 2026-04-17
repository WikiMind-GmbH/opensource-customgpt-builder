from typing import BinaryIO, TextIO

from fastapi import UploadFile

from src.contexts.knowledge.application.ports.file_storage_port import ErrorWhileStoring, RawFileStorePort


class RawFileStoreLocalFsAdapter(RawFileStorePort):
    def add_file(self, file: UploadFile, file_id: str) -> None:
        try:
            with open(file.file.read()) as file:
            
        except Exception as e:
            raise ErrorWhileStoring
    

    def get_file(self, file_id: str) -> TextIO | BinaryIO: 
    def delete_file(self, id: str) -> None: 
