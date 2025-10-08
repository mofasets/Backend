from app.schemas.interaction import Interaction
from app.schemas.plant import Plant
from typing import List
from bson import ObjectId
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta, time


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
    
    async def find_view_interaction_today(self, user_id: str, plant_id: str) -> Interaction:
        """Busca una interacción de vista de hoy."""
        today_start = datetime.combine(datetime.now().date(), time.min)
        tomorrow_start = today_start + timedelta(days=1)
        query = {
            'user_id': user_id,
            'plant_id': plant_id,
            'interaction_type': 'view',
            'created_at': {
                '$gte': today_start,
                '$lt': tomorrow_start
            }
        }

        interaction_document = await Interaction.find_one(query)
        return interaction_document
    
    async def get_most_viewed_plants(self, limit: int = 10):   
        pipeline = [
            {
                "$group": {
                    "_id": "$plant_id",  # Agrupar por plant_id
                    "interaction_count": {"$sum": 1} # Contar interacciones por grupo
                }
            },
            {
                "$sort": {"interaction_count": -1} # Ordenar de mayor a menor
            },
            {
                "$limit": limit # Limitar al top N
            }
        ]
        cursor = await Interaction.aggregate(aggregation_pipeline=pipeline).to_list()

        top_plant_ids = [Plant(id=doc['_id']) for doc in await cursor.to_list(length=limit)]
        return top_plant_ids
