from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fitness_app.file_entities.schemas import FileEntitySchema


class ExerciseType(StrEnum):
    BASIC = "Базовое"
    INSULATING = "Изолирующее"


class Difficulty(StrEnum):
    BEGINNER = "Начинающий"
    AVERAGE = "Средний"
    PROFESSIONAL = "Профессионал"


class ExerciseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    originalUri: Optional[str] = None
    name: str
    muscle: Optional[str] = None
    additionalMuscle: Optional[str] = None
    type: Optional[ExerciseType] = None
    equipment: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    description: Optional[str] = None

    photos: Optional[list[FileEntitySchema]] = []


class ExerciseCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    originalUri: Optional[str] = None
    name: str
    muscle: Optional[str] = None
    additionalMuscle: Optional[str] = None
    type: Optional[ExerciseType] = None
    equipment: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    description: Optional[str] = None

    photo_ids: Optional[list[int]] = None


class ExerciseUpdateSchema(BaseModel):
    id: int
    originalUri: Optional[str] = None
    name: str
    muscle: Optional[str] = None
    additionalMuscle: Optional[str] = None
    type: Optional[ExerciseType] = None
    equipment: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    description: Optional[str] = None

    photo_ids: Optional[list[int]] = None


class ExerciseFindSchema(BaseModel):
    name: Optional[str] = None
    muscle: Optional[str] = None
    additionalMuscle: Optional[str] = None
    type: Optional[ExerciseType] = None
    equipment: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    description: Optional[str] = None
