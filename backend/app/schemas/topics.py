from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TopicBase(BaseModel):
    topic: str

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
