from schemas.common import (
    CreateCustomGPTResponse,
    CustomGPTInfos,
    ExistingCustomGPT,
    StatusOfStandardResponse,
)


async def get_custom_gpts_list():
    """Retrieves the list of Custom GPTs

    Returns:
        CustomGPTNamesList: List[str] of names
    """
    print("Get custom gpts list")


async def get_custom_gpt_by_id(id: int) -> ExistingCustomGPT:
    """Retrieves the Custom GPT by ID

    Args:
        id (int): ID for Custom GPT

    Returns:
        ExistingCustomGPT: Information of ExistingCustomGPT Retrieved
    """
    response_retrived = ExistingCustomGPT(
        custom_gpt_id=id,
        created_at=None,
        custom_gpt_description="Desc",
        custom_gpt_name="name",
        custom_gpt_instructions="instructions",
    )
    return response_retrived


async def get_all_custom_gpts() -> list[ExistingCustomGPT]:
    """Retrieves the Custom GPT by ID

    Returns:
        ExistingCustomGPT: Information of list of ExistingCustomGPTs
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
    edited_information: ExistingCustomGPT,
) -> StatusOfStandardResponse:
    """Edit the Custom GPT

    Args:
        edited_information (CustomGPT): Custom GPT with edited information

    Returns:
        StatusOfStandardResponse: Success or Error
    """
    print("Use the information to update the custom gpt ---", edited_information)
    response = StatusOfStandardResponse.success
    return response


async def send_custom_gpt_info(
    custom_gpt_infos: CustomGPTInfos,
) -> CreateCustomGPTResponse:
    """Send the complete information (Name, Desription and Instructions) for creating a custom GPT
    Args:
        gpt_information (CustomGPTInfos): Custom GPT information
    Returns:
        StatusOfStandardResponse: Response of the model api
    """
    print("the information for creating a new custom gpt: ", custom_gpt_infos)
    response = 200

    if response == 200:
        return CreateCustomGPTResponse(custom_gpt_id=1, status=True)
    else:
        return CreateCustomGPTResponse(custom_gpt_id=None, status=False)
