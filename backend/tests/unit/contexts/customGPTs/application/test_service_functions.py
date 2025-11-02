from src.contexts.customGPTs.application.ports.customgpt_repo import (
    CgptNotFound,
)
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.application.service_functions import (
    create_custom_gpt_service,
    delete_custom_gpt_service,
    edit_custom_gpt_service,
)
from src.contexts.customGPTs.domain.models import CustomGPT
from src.contexts.shared.typing_aliases import Factory
import pytest


def test_delete_custom_gpt_service(cgpt_uow_factory: Factory[CgptUOW]):
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
            name="cgpt_1", instructions="Do sth"
        )
        cgpt_id: str = cgpt.id
        uow.commit()
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.id == cgpt_id
    delete_custom_gpt_service(uow=uow, gpt_id=cgpt_id)
    # test: if delete worked
    with pytest.raises(CgptNotFound):
        with cgpt_uow_factory() as uow:
            cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
    # test: can't delete non existing gpt
    with pytest.raises(CgptNotFound):
        delete_custom_gpt_service(uow=uow, gpt_id=cgpt_id)


def test_create_custom_gpt_service(cgpt_uow_factory: Factory[CgptUOW]):
    name: str = "name"
    instructions: str = "instructions"
    description: str = "description"
    cgpt_id:str = create_custom_gpt_service(
        name=name,
        description=description,
        instructions=instructions,
        uow=cgpt_uow_factory(),
    )
    with cgpt_uow_factory() as uow:
        cgpt:CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.name == name
        assert cgpt.instructions == instructions
        assert cgpt.description == description
    
    cgpt_id_2:str = create_custom_gpt_service(
        name=name,
        description=None,
        instructions=instructions,
        uow=cgpt_uow_factory(),
    )
    with cgpt_uow_factory() as uow:
        cgpt:CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id_2)
        assert cgpt.name == name
        assert cgpt.instructions == instructions
        assert cgpt.description == None

def test_edit_custom_gpt_service(cgpt_uow_factory: Factory[CgptUOW]):
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt("Old","Old","Old")
        cgpt_id: str = cgpt.id
        uow.commit()
    edit_custom_gpt_service(
        id=cgpt_id,
        name="A",
        instructions="A",
        description="A",
        uow=cgpt_uow_factory(),
    )
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.name == "A"
        assert cgpt.instructions == "A"
        assert cgpt.description == "A"
    


