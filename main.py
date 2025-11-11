from fastapi import FastAPI
from app.api.routers import search, explore, settings, auth, show, plant, user
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.core.config import config_settings
from app.services.recommendation_service import RecommendationService
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Gestiona las tareas de arranque y apagado de la aplicación.
    """
    print("Iniciando aplicación y conectando a la base de datos...")
    await init_db()
    app.state.recommender = RecommendationService()
    app.state.recommender.load_model_from_disk()
    yield 
    print("Cerrando la aplicación...")

app = FastAPI(
    title=config_settings.DATABASE_NAME,
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:8550"
]

# app Properties.
app.title = 'Kuolix Server'
app.version = '0.0.1'
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(explore.explore_router)
app.include_router(search.search_router)
app.include_router(settings.settings_router)
app.include_router(auth.auth_router)
app.include_router(show.show_router)
app.include_router(plant.plant_router)
app.include_router(user.user_router)

