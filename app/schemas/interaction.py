from pydantic import Field
from beanie import Document, PydanticObjectId
from datetime import datetime, timezone 
from typing import Optional


class Interaction(Document):
    user_id: PydanticObjectId
    plant_id: PydanticObjectId
    interaction_type: str #'view', 'recognize'
    interaction_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
                 
    class Settings:
        name = "interactions"
        
    class Config:
        from_attributes = True
        json_encoders = {PydanticObjectId: str}


