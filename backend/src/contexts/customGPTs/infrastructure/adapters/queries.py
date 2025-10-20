
from sqlalchemy import select
from src.contexts.customGPTs.domain.models import CustomGPT
from sqlalchemy.orm import Session
from src.contexts.shared.typing_aliases import Factory
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.application.ports.cgpt_queries import CgptQueries, CustomGPTInfosDTO, CustomGPTOverviewDTO
from src.contexts.customGPTs.infrastructure.db.orm import custom_gpts


class CgptQueriesImplementation(CgptQueries):
    def __init__(self, cgpt_session_factory:Factory[Session]):
        self._session_facory: Factory[Session] = cgpt_session_factory
    def get_custom_gpt_overviews(self)-> list[CustomGPTOverviewDTO]:
        stmt = ( 
            select(custom_gpts.c.id, custom_gpts.c.name) 
            .order_by(custom_gpts.c.created_at.desc()) # <- core style working with tables
        )
        rows = self._session_facory().execute(stmt).all()
        return [CustomGPTOverviewDTO(id=id, name=name) for id, name in rows]
  
            
    def get_custom_gpt_infos(self, cgpt_id:str, cgpt_uow: CgptUOW)->CustomGPTInfosDTO: