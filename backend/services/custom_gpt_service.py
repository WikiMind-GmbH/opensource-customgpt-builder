from schemas.common import (
    CreateOrEditCustomGPTResponse,
    CustomGptToCreate,
    CustomGptToEdit,
    ExistingCustomGPT,
)


async def get_custom_gpt_by_id(custom_gpt_id: int) -> ExistingCustomGPT:
    """Retrieves the Custom GPT by ID for reaching to the chat page with information
    Args:
        id (int): ID for Custom GPT accessed by the user
    Returns:
        ExistingCustomGPT: Information of ExistingCustomGPT
    """
    response_retrived = ExistingCustomGPT(
        custom_gpt_id=custom_gpt_id,
        created_at=None,
        custom_gpt_description="Desc",
        custom_gpt_name="name",
        custom_gpt_instructions="instructions",
    )
    return response_retrived


async def get_all_custom_gpts() -> list[ExistingCustomGPT]:
    """Retrieves the Custom GPT information by ID

    Returns:
        list[ExistingCustomGPT]: Information of list of ExistingCustomGPTs
    """
    response_retrived = [
        ExistingCustomGPT(
            custom_gpt_id=1,
            created_at=None,
            custom_gpt_description="Desc",
            custom_gpt_name="name",
            custom_gpt_instructions="instructions",
        ),
        ExistingCustomGPT(
            custom_gpt_id=2,
            created_at=None,
            custom_gpt_description="Desc2",
            custom_gpt_name="name2",
            custom_gpt_instructions="instructions2",
        ),
    ]
    return response_retrived


# editing the custom gpt
async def update_custom_gpt(
    custom_gpt_info: CustomGptToEdit,
) -> CreateOrEditCustomGPTResponse:
    """Edit the existing Custom GPT information
     Args:
        custom_gpt_id (int): Custom GPT with edited information
    Returns:
        CreateOrEditCustomGPTResponse: Success or Error
    """
    print("New Name: ", custom_gpt_info.custom_gpt_name)
    response = 200

    if response == 200:
        return CreateOrEditCustomGPTResponse(
            custom_gpt_id=custom_gpt_info.custom_gpt_id, status=True
        )
    else:
        return CreateOrEditCustomGPTResponse(custom_gpt_id=None, status=False)


async def send_custom_gpt_info(
    custom_gpt_infos: CustomGptToCreate,
) -> CreateOrEditCustomGPTResponse:
    """Send the complete information (Name, Desription and Instructions) for creating a custom GPT
    Args:
        gpt_information (CustomGptToCreate): Custom GPT information
    Returns:
        StatusOfStandardResponse: Response of the model api
    """
    print("the information for creating a new custom gpt: ", custom_gpt_infos)
    response = 200

    if response == 200:
        return CreateOrEditCustomGPTResponse(custom_gpt_id=1, status=True)
    else:
        return CreateOrEditCustomGPTResponse(custom_gpt_id=None, status=False)
