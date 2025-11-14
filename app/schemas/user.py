from pydantic import BaseModel, Field, EmailStr, field_validator
from bson import ObjectId
from typing import Optional
from beanie import Document, PydanticObjectId
from datetime import datetime, timezone




class User(Document):
    name: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    birth_date: Optional[str] = None
    gender: str = None
    role: str = 'aficionado'
    phone: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Settings:
        name = "users"

class UserRead(BaseModel):
    id: str
    name: Optional[str] = None
    email: EmailStr
    role: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
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
    role: str = 'aficionado'
    birth_date: str
    gender: str
    phone: str
    country: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
