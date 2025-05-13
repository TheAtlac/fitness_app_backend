from datetime import date
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from fitness_app.core.utils import NonEmptyStr


class Role(StrEnum):
    COACH = "COACH"
    CUSTOMER = "CUSTOMER"


class Sex(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class UserBaseSchema(BaseModel):
    email: EmailStr
    name: NonEmptyStr
    sex: Optional[Sex]
    birth_date: Optional[date]


class UserCreateSchema(UserBaseSchema):
    password: NonEmptyStr


class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    role: Role = "CUSTOMER"
    id: int


class UserUpdateSchema(BaseModel):
    email: EmailStr
    name: NonEmptyStr
    sex: Optional[Sex]
    birth_date: Optional[date]


class UserPasswordUpdateSchema(BaseModel):
    password: NonEmptyStr
