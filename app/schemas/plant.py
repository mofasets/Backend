from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from beanie import Document
from bson import ObjectId
from datetime import datetime, timezone



class Plant(Document):
    """
    Modelo Beanie que representa una planta medicinal en la base de datos.
    """
    scientific_name: str 
    common_names: List[str] 
    habitat_description: str
    general_ailments: str
    specific_diseases: List[str]
    usage_instructions: str
    image_filename: Optional[str] = None
    is_verified: bool = False
    taxonomy: Optional[str]
    active_ingredient: Optional[str]
    references: List[str]
    safety_level: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "plants"

class PlantRead(BaseModel):
    """
    Modelo Pydantic para las respuestas de la API.
    Convierte el ObjectId de la base de datos a un string.
    """
    id: str
    scientific_name: str 
    common_names: List[str] 
    habitat_description: str
    general_ailments: str
    specific_diseases: List[str]
    usage_instructions: str
    image_filename: Optional[str] = None
    is_verified: bool = False
    taxonomy: Optional[str]
    active_ingredient: Optional[str]
    references: List[str]


    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        """Convierte el ObjectId a string antes de la validación."""
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str  # Cuando encuentres un ObjectId, conviértelo a string
        }
class RecognitionResponse(BaseModel):
    """
    Modelo que representa la respuesta completa del endpoint de reconocimiento de imágenes.
    """
    img_result: Plant
    suggested_plants: List[PlantRead]

    class Config:
        from_attributes = True