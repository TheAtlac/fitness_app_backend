from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fitness_app.users.schemas import UserCreateSchema


class UserGoal(StrEnum):
    BE_ACTIVE = "BE_ACTIVE"
    BE_STRONG = "BE_STRONG"
    LOSE_WEIGHT = "LOSE_WEIGHT"


class FitnessLevel(StrEnum):
    NOVICE = "NOVICE"
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    ATHLETE = "ATHLETE"


class ExercisePreference(StrEnum):
    JOGGING = "JOGGING"
    WALKING = "WALKING"
    WEIGHTLIFT = "WEIGHTLIFT"
    CARDIO = "CARDIO"
    YOGA = "YOGA"
    OTHER = "OTHER"


class CustomerBaseSchema(BaseModel):
    goal: Optional[UserGoal]
    fitness_level: Optional[FitnessLevel]
    preference: Optional[ExercisePreference]


class CustomerCreateSchema(UserCreateSchema, CustomerBaseSchema):
    pass


class CustomerSchema(CustomerBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class CustomerUpdateSchema(CustomerBaseSchema):
    pass


class CustomerSaveSchema(CustomerBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
