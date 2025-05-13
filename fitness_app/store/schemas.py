from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fitness_app.core.utils import NonEmptyStr


class ProductCategory(StrEnum):
    NEW = "NEW"
    POPULAR = "POPULAR"
    FOOD = "FOOD"
    EQUIPMENT = "EQUIPMENT"


class ProductCreateSchema(BaseModel):
    name: NonEmptyStr
    description: Optional[str]
    price: int
    category: ProductCategory
    link: str
    images: list[str] = []


class ProductSchema(ProductCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
