from fastapi import FastAPI
from app.api.routers import search, explore, settings, auth
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.core.config import config_settings
from app.services.recommendation_service import RecommendationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Gestiona las tareas de arranque y apagado de la aplicación.
    """
    print("Iniciando aplicación y conectando a la base de datos...")
    await init_db()
    app.state.recommender = RecommendationService()
    await app.state.recommender.load_model()
    yield 
    print("Cerrando la aplicación...")


# Instancia principal de la aplicación
app = FastAPI(
    title=config_settings.DATABASE_NAME,
    lifespan=lifespan
)

# app Properties.
app.title = 'Kuolix Server'
app.version = '0.0.1'

app.include_router(explore.explore_router)
app.include_router(search.search_router)
app.include_router(settings.settings_router)
app.include_router(auth.auth_router)

