from app.schemas.interaction import Interaction
from typing import List
from bson import ObjectId
from fastapi.exceptions import HTTPException



class InteractionRepository:

    async def get_interactions_by_user(self, user_id: str) -> List[Interaction]:
        try:
            user_obj_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="El ID proporcionado no es un ObjectId válido")
        
        response = await Interaction.find(Interaction.user_id == user_obj_id).to_list()
        return response
