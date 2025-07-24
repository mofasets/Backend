from fastapi import APIRouter, Depends
from app.db.repository_plant import PlantRepository


TAGS = ['Search']
search_router = APIRouter(prefix='/search')

@search_router.get('/index/{user_id}', tags=TAGS)
async def search_index(user_id: str, plant_repo: PlantRepository = Depends(PlantRepository)):
    recomended_plants = await plant_repo.get_suggested_plants(user_id)
    return recomended_plants

@search_router.post('/search_query/{search_query}', tags=TAGS)
async def search_search_query(search_query: str, plant_repo: PlantRepository = Depends(PlantRepository)):
    plants_result = await plant_repo.get_plants_by_query(search_query)
    return plants_result

@search_router.get('/{item_id}', tags=TAGS)
async def explore_show(item_id: str, plant_repo: PlantRepository = Depends(PlantRepository)):
    plant = await plant_repo.get_plant_by_id(item_id)
    return plant
