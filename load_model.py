import asyncio
from app.services.recommendation_service import RecommendationService
from app.db.database import init_db

async def main():
    """
    Función principal para instanciar el servicio y ejecutar el entrenamiento.
    """
    await init_db()
    recommendation_service = RecommendationService()
    await recommendation_service.train_and_save_model()

if __name__ == "__main__":
    print("Starting nightly model training...")
    asyncio.run(main())
    print("Training finished.")