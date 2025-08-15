from fastapi import APIRouter, Depends
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token
from app.services.recommendation_service import RecommendationService
from app.api.dependencies import get_recommender

TAGS = ['Search']
search_router = APIRouter(prefix='/search')

@search_router.get('/index/{user_id}', tags=TAGS)
async def search_index(user_id: str, recommender: RecommendationService = Depends(get_recommender), my_user = Depends(decode_token)):
    recommended_plants = await recommender.get_recommendations(user_id)
    return recommended_plants

@search_router.post('/search_query/{search_query}', tags=TAGS)
async def search_search_query(search_query: str, plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    plants_result = await plant_repo.get_plants_by_query(search_query)
    return plants_result

@search_router.get('/{item_id}', tags=TAGS)
async def explore_show(item_id: str, plant_repo: PlantRepository = Depends(PlantRepository),  my_user = Depends(decode_token)):
    plant = await plant_repo.get_plant_by_id(item_id)
    return plant
