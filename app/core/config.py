from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigSettings(BaseSettings):
    """
    Clase para gestionar la configuración de la aplicación.
    Lee automáticamente las variables de entorno desde un archivo .env.
    """
    
    # Configuración de la base de datos
    DATABASE_URL: str
    DATABASE_NAME: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    GEMINI_API_KEY: str
    # Esto le dice a Pydantic que lea las variables desde el archivo .env
    model_config = SettingsConfigDict(env_file=".env")


# Se crea una única instancia de la configuración para ser importada en otros módulos
config_settings = ConfigSettings()