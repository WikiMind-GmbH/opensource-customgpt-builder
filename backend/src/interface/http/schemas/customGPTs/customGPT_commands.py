from pydantic import BaseModel, Field


class CustomGptToCreate(BaseModel):
    custom_gpt_name: str = Field(max_length=40, min_length=1) # ToDo: Handle this nicely -is possible like that for nice client errors or not?
    custom_gpt_description: str = Field(max_length=200, min_length=1)
    custom_gpt_instructions: str = Field(max_length=50000, min_length=1)

class CustomGptToEdit(BaseModel):
    custom_gpt_id: str
    custom_gpt_name: str = Field(max_length=40, min_length=1) # ToDo: Handle this nicely -is possible like that for nice client errors or not?
    custom_gpt_description: str = Field(max_length=200, min_length=1)
    custom_gpt_instructions: str = Field(max_length=50000, min_length=1)