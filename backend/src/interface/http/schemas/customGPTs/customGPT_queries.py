from pydantic import BaseModel


class CustomGPTOverviewSchema(BaseModel):
    custom_gpt_id: str
    custom_gpt_name: str


class CustomGPTInfosSchema(BaseModel):
    custom_gpt_id: str
    custom_gpt_name: str
    custom_gpt_description: str | None = None
    custom_gpt_instructions: str
