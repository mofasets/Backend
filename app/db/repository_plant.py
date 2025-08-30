from typing import List, Optional
from app.schemas.plant import Plant, PlantRead
from beanie.operators import In
from bson import ObjectId
from fastapi import HTTPException

class PlantRepository:
    """
    Gestiona las operaciones CRUD para la colección de Plantas en la base de datos.
    """

    async def get_plant_by_id(self, id: str) -> PlantRead:
        """find a Plant By Id"""
        try:
            obj_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="El ID proporcionado no es un ObjectId válido")
        
        plant =  await Plant.find_one({"_id": obj_id})
        if plant:
            return plant
        else:
            raise HTTPException(status_code=404, detail="Planta no encontrada")

    async def get_plants_by_img_result(self, name: str, ailments: List[str], limit: int = 3) -> List[PlantRead]:
        """find a List of plants related to the plant img result using recomendation system"""
        return await Plant.find(
            Plant.scientific_name != name,
            In(Plant.specific_diseases, ailments)
        ).limit(limit).to_list()
    
    async def get_plants_by_query(self, query: str, limit: int = 10) -> List[PlantRead]:
        pipeline = [
            {
                "$match": {
                    "$text": {
                        "$search": query
                    }
                }
            },
            {
                "$sort": { "score": { "$meta": "textScore" } }
            },
            { "$limit": limit }
        ]
        plants = await Plant.aggregate(aggregation_pipeline=pipeline, projection_model=Plant) \
            .to_list()
        return plants
    
    async def get_all_plants(self):
        result = await Plant.find_all().to_list()
        return result