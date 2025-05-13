from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageSchema(BaseModel, Generic[T]):
    total_items_count: int
    items: list[T]
