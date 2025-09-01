from app.schemas.interaction import Interaction
from typing import List
from bson import ObjectId
from fastapi.exceptions import HTTPException
import datetime


class InteractionRepository:

    async def get_interactions_by_user(self, user_id: str) -> List[Interaction]:
        try:
            user_obj_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="El ID proporcionado no es un ObjectId válido")
        
        response = await Interaction.find(Interaction.user_id == user_obj_id).to_list()
        return response

    async def add_interaction(self, content: dict) -> Interaction:
        """Crea y guarda un nuevo registro de interacción."""
        
        print(f"Registrando interacción: user='{content.get("user_id")}', plant='{content.get("plant_id")}', type='{content.get("interaction_type")}'")
        
        interaction = Interaction(
            user_id=content.get("user_id"),
            plant_id=content.get("plant_id"),
            interaction_type=content.get("interaction_type")
        )
        await interaction.insert()
        return interaction
