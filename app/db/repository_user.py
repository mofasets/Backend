from app.schemas.user import User, UserUpdate, UserRead
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException


class UserRepository:
    
    async def get_user_by_id(self, id: str) -> Optional[User]:
        try:
            obj_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="El ID proporcionado no es un ObjectId válido")
        
        user =  await User.find_one({"_id": obj_id})
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrada")

    async def update_user_by_id(self, id: str, user_data: UserUpdate) -> User:
        """
        Busca un usuario por su ID y actualiza sus datos.
        """
        user_to_update = await self.get_user_by_id(id)
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            update_result = await user_to_update.update({"$set": update_data})
            print('Holaa')
            if update_result:
                user_to_update = await User.find_one({"_id": ObjectId(id)})
        return user_to_update