from fastapi import Request
from app.services.recommendation_service import RecommendationService

def get_recommender(request: Request) -> RecommendationService:
    """
    Función de dependencia para obtener la instancia global del RecommendationService
    desde el estado de la aplicación.
    """
    return request.app.state.recommender

