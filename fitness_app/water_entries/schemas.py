from datetime import date

from pydantic import BaseModel, ConfigDict


class WaterEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    water_volume: int
    goal_water_volume: int
    date_field: date


class WaterEntryCreateSchema(BaseModel):
    water_volume: int
