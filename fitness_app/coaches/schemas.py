from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from fitness_app.users.schemas import UserCreateSchema


class Speciality(StrEnum):
    KIDS = "KIDS"
    ADULT = "ADULT"
    YOGA = "YOGA"


class CoachBaseSchema(BaseModel):
    speciality: Speciality


class CoachCreateSchema(UserCreateSchema, CoachBaseSchema):
    pass


class CoachUpdateSchema(CoachBaseSchema):
    pass


class CoachSaveSchema(CoachBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


class CoachSchema(CoachSaveSchema):

    id: int
    rating: float
