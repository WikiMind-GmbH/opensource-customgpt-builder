import pytest

from src.contexts.chat.application.ports.chat_repo import ConversationNotFoundError
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import Conversation
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
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


def test_delete_custom_gpt_service_deltes_only_existing_customgpt_otherwise_throws_error(
    cgpt_uow_factory: Factory[CgptUOW],
    conversation_adapter_factory: Factory[ConversationPort],
):
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt(
            name="cgpt_1", instructions="Do sth"
        )
        cgpt_id: str = cgpt.id
        uow.commit()
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.id == cgpt_id
    delete_custom_gpt_service(
        uow_factory=cgpt_uow_factory,
        cgpt_id=cgpt_id,
        conv_adapter=conversation_adapter_factory(),
    )
    # test: if delete worked
    with pytest.raises(CgptNotFound):
        with cgpt_uow_factory() as uow:
            cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
    # test: can't delete non existing gpt
    with pytest.raises(CgptNotFound):
        delete_custom_gpt_service(
            uow_factory=cgpt_uow_factory,
            cgpt_id=cgpt_id,
            conv_adapter=conversation_adapter_factory(),
        )


def test_delete_custom_gpt_service_deletes_corresponding_conversation(
    cgpt_uow_factory: Factory[CgptUOW],
    conversation_adapter_factory: Factory[ConversationPort],
    conv_uow_factory: Factory[ConversationUOW],
):
    # Setup
    with cgpt_uow_factory() as uow:
        cgpt = uow.cgpt_repo.create_cgpt("a", "a", "a")
        cgpt_other = uow.cgpt_repo.create_cgpt("a", "a", "a")
        uow.commit()
        cgpt_id = cgpt.id
        cgpt_other_id = cgpt_other.id
    with conv_uow_factory() as uow:
        convs_with_cgpt: list[Conversation] = []
        unrelated_convs: list[Conversation] = []
        convs_with_cgpt.append(
            uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        )
        convs_with_cgpt.append(
            uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        )
        convs_with_cgpt.append(
            uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        )

        conv_without_cgpt = uow.conversation_repo.create_conversation()
        conv_with_other_cgpt = uow.conversation_repo.create_conversation(
            cgpt_id=cgpt_other_id
        )
        unrelated_convs.append(conv_without_cgpt)
        unrelated_convs.append(conv_with_other_cgpt)

        all_convs: list[Conversation] = convs_with_cgpt + unrelated_convs
        uow.commit()

    # Test: all convs exist
    with conv_uow_factory() as uow:
        assert None not in [uow.conversation_repo.get(conv.id) for conv in all_convs]

    # delete
    delete_custom_gpt_service(
        uow_factory=cgpt_uow_factory,
        cgpt_id=cgpt_id,
        conv_adapter=conversation_adapter_factory(),
    )

    # Test: unrelated converstions still exist
    with conv_uow_factory() as uow:
        assert None not in [
            uow.conversation_repo.get(conv.id) for conv in unrelated_convs
        ]

    # Test: convs with cgpt_id were deleted
    with conv_uow_factory() as uow:
        for conv in convs_with_cgpt:
            with pytest.raises(ConversationNotFoundError):
                uow.conversation_repo.get(conv.id)


def test_create_custom_gpt_service(cgpt_uow_factory: Factory[CgptUOW]):
    name: str = "name"
    instructions: str = "instructions"
    description: str = "description"
    cgpt_id: str = create_custom_gpt_service(
        name=name,
        description=description,
        instructions=instructions,
        uow_factory=cgpt_uow_factory,
    )
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.name == name
        assert cgpt.instructions == instructions
        assert cgpt.description == description

    cgpt_id_2: str = create_custom_gpt_service(
        name=name,
        description=None,
        instructions=instructions,
        uow_factory=cgpt_uow_factory,
    )
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id_2)
        assert cgpt.name == name
        assert cgpt.instructions == instructions
        assert cgpt.description is None


def test_edit_custom_gpt_service_overwrites_old_values(
    cgpt_uow_factory: Factory[CgptUOW],
):
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.create_cgpt("Old", "Old", "Old")
        cgpt_id: str = cgpt.id
        uow.commit()
    edit_custom_gpt_service(
        id=cgpt_id,
        name="A",
        instructions="A",
        description="A",
        uow_factory=cgpt_uow_factory,
    )
    with cgpt_uow_factory() as uow:
        cgpt: CustomGPT = uow.cgpt_repo.get(cgpt_id=cgpt_id)
        assert cgpt.name == "A"
        assert cgpt.instructions == "A"
        assert cgpt.description == "A"
