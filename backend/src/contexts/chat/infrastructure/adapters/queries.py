
# from src.contexts.shared.typing_aliases import Factory
# from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
# from src.contexts.customGPTs.application.ports.cgpt_queries import CgptQueries, CustomGPTInfosDTO, CustomGPTOverviewDTO


# class CgptQueriesImplementation(CgptQueries):
#     def __init__(self, cgpt_uow_factory:Factory[CgptUOW]):
#         self._cgpt_uow_factory: Factory[CgptUOW] = cgpt_uow_factory
#     def get_custom_gpt_overviews(self, cgpt_uow: CgptUOW)-> list[CustomGPTOverviewDTO]:
#         with self._cgpt_uow_factory() as uow:
#             stmt = ( 
#                 select(CustomGPT.id, CustomGPT.name) #<- ORM style working with our mapped domain models
#                 .order_by(custom_gpts.c.created_at.desc()) # <- core style working with tables
#             )
#             rows = self._session.execute(stmt).all()
#             return [CustomGPTOverview(id=id, name=name) for id, name in rows]
  
            
#     def get_custom_gpt_infos(self, cgpt_id:str, cgpt_uow: CgptUOW)->CustomGPTInfosDTO: