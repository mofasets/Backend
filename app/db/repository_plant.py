from typing import List, Optional
from app.schemas.plant import Plant, PlantRead
from beanie.operators import In
from bson import ObjectId
from beanie import PydanticObjectId
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
            In(Plant.specific_diseases, ailments),
            Plant.is_verified == True
        ).limit(limit).to_list()

    async def get_plant_by_scientific_name(self, scientific_name: str) -> PlantRead:
        """find a Plant By Scientific Name"""
        return await Plant.find_one(Plant.scientific_name == scientific_name)

    async def get_plants_by_query(self, query: str, limit: int = 10) -> List[PlantRead]:
        pipeline = [
            {
                "$match": {
                    "$text": {
                        "$search": query
                    },
                }
            },
            {
                "$sort": { "score": { "$meta": "textScore" } }
            },
            { "$limit": limit }
        ]
        plants = await Plant.aggregate(aggregation_pipeline=pipeline, projection_model=Plant).to_list()
        return plants
    
    async def get_all_verified_plants(self):
        query = {"is_verified": True}
        result = await Plant.find(query).to_list()
        return result
    
    async def get_all_non_verified_plants(self):
        query = {"is_verified": False}
        result = await Plant.find(query).to_list()
        return result
    
    async def is_plant_in_db(self, scientific_name: str) -> bool:
        """check if a plant is in the database"""
        plant = await Plant.find_one(Plant.scientific_name == scientific_name)
        if plant:
            return True
        return False

    async def add_plant(self, plant: dict[str:str]) -> PlantRead:
        """add a plant to the database"""
        new_plant = Plant(**plant)
        await new_plant.insert()
        return new_plant
    
    async def update_plant(self, plant_id: PydanticObjectId, update_data: dict[str:str]) -> PlantRead:
        plant_to_update = await Plant.get(plant_id)
        
        if not plant_to_update:
            return None

        update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
        await plant_to_update.update({"$set": update_data_filtered})
        updated_plant_doc = await Plant.get(plant_id)

        return PlantRead.model_validate(updated_plant_doc)
    
    async def delete_plant(self, plant_id: str) -> Optional[Plant]:
        """
        Busca una planta por su ID y la elimina de la base de datos.
        Devuelve el objeto de planta eliminado (aún en memoria) si se encuentra.
        """
        
        try:
            object_id = PydanticObjectId(plant_id)
        except Exception:
            return None 

        plant_to_delete = await Plant.get(object_id)
        if not plant_to_delete:
            return None
        
        await plant_to_delete.delete()
        return plant_to_delete        