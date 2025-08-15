from pydantic import BaseModel, Field
from typing import List, Optional
from beanie import Document
from bson import ObjectId

class Plant(Document):
    """
    Modelo Beanie que representa una planta medicinal en la base de datos.
    """
    scientific_name: str 
    common_names: List[str] 
    habitat_description: str
    general_ailments: str
    specific_diseases: List[str]

    class Settings:
        name = "plants"