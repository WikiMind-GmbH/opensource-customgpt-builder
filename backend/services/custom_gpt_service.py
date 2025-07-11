from sqlmodel import Session, select
from models.models import CustomGptsDB
from schemas.common import (
    ExistingCustomGPT,
    CreateOrEditCustomGPTStatus,
    CustomGptToCreateOrEdit,
    DeleteCustomGPTStatus,
)

def get_all_custom_gpts(session: Session) -> list[ExistingCustomGPT]:
    stmt = select(CustomGptsDB)
    rows = session.exec(stmt).all()
    return [
        ExistingCustomGPT(
            custom_gpt_id=row.id,
            custom_gpt_name=row.name,
            custom_gpt_description=row.custom_gpt_description,
            custom_gpt_instructions=row.custom_gpt_instructions,
            created_at=row.created_at,
        )
        for row in rows
    ]

def retrieve_custom_gpt_by_id(custom_gpt_id: int, session: Session) -> ExistingCustomGPT:
    row = session.get(CustomGptsDB, custom_gpt_id)
    return ExistingCustomGPT(
        custom_gpt_id=row.id,
        custom_gpt_name=row.name,
        custom_gpt_description=row.custom_gpt_description,
        custom_gpt_instructions=row.custom_gpt_instructions,
        created_at=row.created_at,
    )

def delete_custom_gpt(custom_gpt_id: int, session: Session) -> DeleteCustomGPTStatus:
    session.delete(session.get(CustomGptsDB, custom_gpt_id))
    session.commit()
    return DeleteCustomGPTStatus(custom_gpt_id=custom_gpt_id)

def create_or_edit_custom_gpt(
    info: CustomGptToCreateOrEdit,
    session: Session,
) -> CreateOrEditCustomGPTStatus:
    if info.custom_gpt_id is None:
        row = CustomGptsDB(
            name=info.custom_gpt_name,
            custom_gpt_description=info.custom_gpt_description,
            custom_gpt_instructions=info.custom_gpt_instructions,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return CreateOrEditCustomGPTStatus(custom_gpt_id=row.id)
    else:
        row = session.get(CustomGptsDB, info.custom_gpt_id)
        row.name = info.custom_gpt_name
        row.custom_gpt_description = info.custom_gpt_description
        row.custom_gpt_instructions = info.custom_gpt_instructions
        session.add(row)
        session.commit()
        return CreateOrEditCustomGPTStatus(custom_gpt_id=info.custom_gpt_id)
