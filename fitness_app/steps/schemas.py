from datetime import date

from pydantic import BaseModel, ConfigDict


class StepsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    steps: int
    goal_steps: int
    date_field: date


class StepsCreateSchema(BaseModel):
    steps: int
