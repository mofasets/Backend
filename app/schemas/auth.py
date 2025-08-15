from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.api.routers import auth
from jose import jwt
from app.core.config import config_settings
from app.db.repository_user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
users = UserRepository()

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, config_settings.JWT_SECRET_KEY, config_settings.ALGORITHM)
    return token

def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    data = jwt.decode(token, config_settings.JWT_SECRET_KEY, config_settings.ALGORITHM)
    return users.get_user_by_email(data.get('username'))


