from datetime import date
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fitness_app.file_entities.schemas import FileEntitySchema


class Feeling(StrEnum):
    ANGRY = "ANGRY"
    SAD = "SAD"
    NEUTRAL = "NEUTRAL"
    CALM = "CALM"
    EXCITED = "EXCITED"


class Reason(StrEnum):
    FAMILY = "FAMILY"
    SELF_ESTEEM = "SELF_ESTEEM"
    WORK = "WORK"
    WEATHER = "WEATHER"
    SLEEP = "SLEEP"
    FOOD = "FOOD"
    SOCIAL = "SOCIAL"


class DiarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_entity_id: Optional[int] = None

    date_field: date
    feeling: Feeling
    reason: Optional[Reason] = None
    note: Optional[str] = None

    voice_note: Optional[FileEntitySchema] = None


class DiaryCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_entity_id: Optional[int] = None

    feeling: Feeling
    reason: Optional[Reason] = None
    note: Optional[str] = None
