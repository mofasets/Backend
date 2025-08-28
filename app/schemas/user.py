from pydantic import BaseModel, Field, EmailStr, field_validator
from bson import ObjectId
from typing import Optional
from beanie import Document, PydanticObjectId


class User(Document):
    name: Optional[str] = None
    email: EmailStr
    # hashed_password: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    # img_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None

    class Settings:
        name = "users"

class UserRead(BaseModel):
    id: str
    name: Optional[str] = None
    email: EmailStr
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    # img_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        """Convierte el ObjectId a string antes de la validación."""
        if isinstance(v, ObjectId):
            return str(v)
        return v


    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {PydanticObjectId: str}

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    birth_date: str
    gender: str
    phone: str
    country: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    # password: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    # img_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
