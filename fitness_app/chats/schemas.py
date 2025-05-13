from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from fitness_app.users.schemas import UserSchema


class ChatType(StrEnum):
    DIALOGUE = "DIALOGUE"
    WORKOUT = "WORKOUT"


class ChatCreateSchema(BaseModel):
    type: ChatType


class ChatSchema(ChatCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    users: list[UserSchema]
    last_timestamp: datetime
