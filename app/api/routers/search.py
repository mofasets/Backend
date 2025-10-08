from typing import List
from fastapi import APIRouter, Depends
from app.schemas.auth import decode_token
from app.services.recommendation_service import RecommendationService
from app.api.dependencies import get_recommender
from app.schemas.plant import PlantRead


TAGS = ['Search']
search_router = APIRouter(prefix='/search')

@search_router.get('/index/{user_id}', tags=TAGS, response_model=List[PlantRead])
async def search_index(user_id: str, recommender: RecommendationService = Depends(get_recommender), my_user = Depends(decode_token)):
    recommended_plants = await recommender.get_recommendations(user_id)
    return recommended_plants

@search_router.get('/search_query/{search_query}', tags=TAGS, response_model=List[PlantRead])
async def search_search_query(search_query: str, recommender: RecommendationService = Depends(get_recommender), my_user = Depends(decode_token)):
    plants_result = await recommender.search_by_recommendation(search_query)
    return plants_result
