from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MessageCreateSchema(BaseModel):
    content: Optional[str] = None
    filenames: list[str] = []
    voice_filename: Optional[str] = None


class MessageBaseSchema(BaseModel):
    content: Optional[str] = None
    files_urls: list[str] = []
    voice_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
    chat_id: int
    sender_id: int


class MessageSchema(MessageBaseSchema):
    id: int
    timestamp: datetime
