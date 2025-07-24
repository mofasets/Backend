from fastapi import FastAPI
from app.api.routers import search, explore, settings
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.core.config import config_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Gestiona las tareas de arranque y apagado de la aplicación.
    """
    # --- CÓDIGO DE ARRANQUE ---
    # Esto se ejecuta ANTES de que la aplicación empiece a recibir peticiones.
    print("Iniciando aplicación y conectando a la base de datos...")
    await init_db()
    
    yield # La aplicación se ejecuta y gestiona peticiones a partir de aquí.
    
    # --- CÓDIGO DE APAGADO ---
    # Esto se ejecuta CUANDO la aplicación se está cerrando (ej. con Ctrl+C).
    print("Cerrando la aplicación...")
    # Aquí podrías añadir lógica para cerrar conexiones si fuera necesario.


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