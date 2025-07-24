from pydantic import BaseModel, Field, EmailStr
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
    id: PydanticObjectId = Field(alias="_id")
    name: Optional[str] = None
    email: EmailStr
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    # img_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {PydanticObjectId: str}

class UserCreate(BaseModel):
    email: EmailStr
    # password: str 
    name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    # password: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    # img_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
