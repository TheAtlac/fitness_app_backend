from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreateSchema(BaseModel):
    score: int = Field(ge=1, le=5)


class FeedbackSchema(FeedbackCreateSchema):
    model_config = ConfigDict(from_attributes=True)
    customer_id: int
    coach_id: int
