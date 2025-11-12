from app.schemas.interaction import Interaction
from app.schemas.plant import Plant, PlantRead
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

        pipeline = [
            {
                "$match": {
                    "user_id": user_obj_id
                }
            },
            {
                "$lookup": {
                    "from": Plant.Settings.name,
                    "localField": "plant_id",
                    "foreignField": "_id",
                    "as": "plant_details"
                }
            },
            {
                "$unwind": "$plant_details"
            },
            {
                "$match": {
                    "plant_details.is_verified": True
                }
            },
            {
                "$project": {
                    "_id": "$_id",
                    "user_id": "$user_id",
                    "plant_id": "$plant_id",
                    "interaction_type": "$interaction_type",
                    "interaction_date": "$interaction_date" 
                }
            }
        ]

        cursor = Interaction.aggregate(aggregation_pipeline=pipeline)
        results_as_dicts = await cursor.to_list()
        response = [Interaction(**doc) for doc in results_as_dicts]
        
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
                    "_id": "$plant_id",
                    "interaction_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"interaction_count": -1}
            },
            {
                "$limit": limit
            }
        ]
            
        aggregation_result = await Interaction.aggregate(aggregation_pipeline=pipeline).to_list()

        top_plant_ids = [doc["_id"] for doc in aggregation_result]
        if not top_plant_ids:
            return []

        top_plants = await Plant.find(
            {"_id": {"$in": top_plant_ids}}
        ).to_list()                
        
        id_to_plant_map = {plant.id: plant for plant in top_plants}
        
        sorted_plants = [
            id_to_plant_map[plant_id] 
            for plant_id in top_plant_ids 
            if plant_id in id_to_plant_map
        ]

        return sorted_plants