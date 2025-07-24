from pydantic import BaseModel, Field
from typing import Optional
from beanie import Document


class Interaction(Document):
    user_id: int
    plant_id: int
    interaction_type: str #'view', 'recognize'
    timestamp: str # ISO 8601 format

    class Settings:
        name = "interactions"

class InteractionUpdate(BaseModel):
    user_id: Optional[int] = None
    plant_id: Optional[int] = None
    interaction_type: Optional[str] = None #'view', 'recognize'
    timestamp: Optional[str] = None # ISO 8601 format
