from pydantic import Field
from beanie import Document, PydanticObjectId
from datetime import datetime

class Interaction(Document):
    user_id: PydanticObjectId
    plant_id: PydanticObjectId
    interaction_type: str #'view', 'recognize'
    interaction_date: str # ISO 8601 format

    class Settings:
        name = "interactions"
        
    class Config:
        from_attributes = True
        json_encoders = {PydanticObjectId: str}


