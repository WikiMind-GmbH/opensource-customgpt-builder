from typing import  Sequence
from uuid import uuid4

from sqlalchemy import select
from src.contexts.customGPTs.application.exceptions import CGPTNonExistentError
from src.contexts.customGPTs.domain.models import CustomGPT, CustomGPTOverview
from src.contexts.customGPTs.application.ports.customgpt_repo import CustomGPTRepository
from sqlalchemy.orm import Session

class SQAlchemyCustomGPTRepository(CustomGPTRepository):
    def __init__(self, session: Session) -> None:
        self._session = session 
    def get(self, cgpt_id:str)-> CustomGPT:
        cgpt = self._session.get(CustomGPT, cgpt_id)
        if cgpt == None: raise CGPTNonExistentError(cgpt_id)
        return cgpt
    def create_cgpt(self, name: str, instructions: str, description: str | None = None)-> CustomGPT: 
        cgpt:CustomGPT = CustomGPT(name=name,instructions=instructions, description=description)
        self._session.add(cgpt)
        return cgpt
      
    def delete(self, cgpt: CustomGPT):
        self._session.delete(cgpt)
    

# Use Session.execute(select(...)) for multi-column DTOs; Session.scalars(select(Entity)) for entities.