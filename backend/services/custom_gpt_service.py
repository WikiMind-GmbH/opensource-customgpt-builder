from schemas.common import (
    CreateOrEditCustomGPTStatus,
    CustomGptToCreateOrEdit,
    DeleteCustomGPTStatus,
    ExistingCustomGPT,
)
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def retrieve_custom_gpt_by_id(custom_gpt_id: int) -> ExistingCustomGPT:
    """Retrieves the Custom GPT by ID for reaching to the chat page with information
    Args:
        id (int): ID for Custom GPT accessed by the user
    Returns:
        ExistingCustomGPT: Information of ExistingCustomGPT
    """
    logger.info(f"Retrieving custom gpt by  custom_gpt_id = {custom_gpt_id}")

    try:
        response_status = 200

        if response_status != 200:
            raise HTTPException(status_code=404, detail="Custom GPT By ID not found")

        response_retrived = ExistingCustomGPT(
            custom_gpt_id=custom_gpt_id,
            created_at=None,
            custom_gpt_description="Desc",
            custom_gpt_name="name",
            custom_gpt_instructions="instructions",
        )
        return response_retrived

    except HTTPException as http_err:
        logger.error(f"HTTP error: {http_err.detail}")
        raise

    except Exception as err:
        logger.exception("Unexpected error occurred while retrieving chat history", err)
        raise HTTPException(status_code=500, detail="Internal server error")


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


async def send_custom_gpt_info(
    custom_gpt_infos: CustomGptToCreateOrEdit,
) -> CreateOrEditCustomGPTStatus:
    """Send the complete information (Name, Desription and Instructions) for creating a custom GPT
    Args:
        gpt_information (CustomGptToCreateOrEdit): Custom GPT information
    Returns:
        StatusOfStandardResponse: Response of the model api
    """
    print("the information for creating a new custom gpt: ", custom_gpt_infos)
    response = 200

    if response == 200:
        return CreateOrEditCustomGPTStatus(custom_gpt_id=1, status=True)
    else:
        return CreateOrEditCustomGPTStatus(custom_gpt_id=None, status=False)


# delete the custom gpt
async def delete_existing_custom_gpt(custom_gpt_id: int) -> DeleteCustomGPTStatus:
    """Deletes the existing custom GPT by ID

    Args:
        custom_gpt_id (int): Id of the existing Custom GPT

    Returns:
        StatusOfStandardResponse: Returns the status of deletion operation
    """

    logger.info(f"Deleting custom gpt by custom_gpt_id = {custom_gpt_id}")

    try:
        response_status = 200

        if response_status != 200:
            raise HTTPException(status_code=404, detail="Custom GPT  By ID Not found")

        status = DeleteCustomGPTStatus(custom_gpt_id=custom_gpt_id, status=True)
        return status

    except HTTPException as http_err:
        logger.error(f"HTTP error: {http_err.detail}")
        raise

    except Exception as err:
        logger.exception("Unexpected error occurred while deleting", err)
        raise HTTPException(status_code=500, detail="Internal server error")
