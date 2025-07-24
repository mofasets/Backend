import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import config_settings
from .repository_plant import Plant # Asumiendo que los modelos están en main.py
from .repository_user import User



async def init_db():
    """Inicializa la conexión a la base de datos y Beanie."""
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config_settings.DATABASE_URL
    )
    await client.admin.command('ping')
    database = client['kuolix_testing']
    print(config_settings.DATABASE_NAME)
    print("✔️ Ping a MongoDB exitoso. El servidor está respondiendo.")
    await init_beanie(
        database=database,
        document_models=[Plant, User]
    )
