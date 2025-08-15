import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import config_settings
from app.schemas.plant import Plant
from app.schemas.user import User
from app.schemas.interaction import Interaction

async def init_db():
    """Inicializa la conexión a la base de datos y Beanie."""
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config_settings.DATABASE_URL
    )
    await client.admin.command('ping')
    global database
    database = client['kuolix_testing']
    print("✔️ Ping a MongoDB exitoso. El servidor está respondiendo.")
    await init_beanie(
        database=database,
        document_models=[Plant, User, Interaction]
    )
