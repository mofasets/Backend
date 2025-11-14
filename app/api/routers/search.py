from typing import List
from fastapi import APIRouter, Depends
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token
from app.services.recommendation_service import RecommendationService
from app.api.dependencies import get_recommender
from app.schemas.plant import PlantRead, Plant
from pathlib import Path

TAGS = ['Search']
search_router = APIRouter(prefix='/search')


@search_router.get('/index/{user_id}', tags=TAGS, response_model=List[PlantRead])
async def search_index(user_id: str, recommender: RecommendationService = Depends(get_recommender), my_user = Depends(decode_token)):
    recommended_plants = await recommender.get_recommendations(user_id)
    return recommended_plants

@search_router.get('/search_query/{search_query}', tags=TAGS, response_model=List[PlantRead])
async def search_search_query(search_query: str, plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    plants_result = await plant_repo.get_plants_by_query(search_query)
    return plants_result

@search_router.get('/all', tags=TAGS, response_model=List[PlantRead])
async def search_all(plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    recommended_plants = await plant_repo.get_all_verified_plants()
    return recommended_plants

@search_router.get('/all_non_verified', tags=TAGS, response_model=List[PlantRead])
async def search_all_non_verified(plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    recommended_plants = await plant_repo.get_all_non_verified_plants()
    return recommended_plants
