from fastapi import APIRouter, Depends
from app.db.repository_user import UserRepository
from app.schemas.user import UserRead, UserUpdate
from beanie.odm.fields import PydanticObjectId




TAGS = ['Settings']
settings_router = APIRouter(prefix='/settings')

@settings_router.get('/{user_id}', tags=TAGS, response_model=UserRead)
async def user_show(user_id: str, user_repo: UserRepository = Depends(UserRepository)):
    user = await user_repo.get_user_by_id(user_id)
    return user

@settings_router.put('/{user_id}', tags=TAGS, response_model=UserRead)
async def update_user(user_id: str, user_data: UserUpdate, user_repo: UserRepository = Depends(UserRepository)):
    updated_user = await user_repo.update_user_by_id(user_id, user_data)
    return updated_user
