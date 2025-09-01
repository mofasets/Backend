from app.schemas.user import User, UserUpdate, UserRead, UserCreate
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
import bcrypt
from app.core.security import get_password_hash

def hash_password(password: str) -> str:
    """Genera el hash de una contraseña."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

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
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su email.
        """
        user = await User.find_one({"email": email})
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Crea un nuevo usuario en la base de datos.
        """
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            return None
        
        hashed_password = hash_password(user_data.password)
        user_obj = User(
            name=user_data.name, 
            email=user_data.email,
            birth_date=user_data.birth_date,
            gender=user_data.gender,
            phone=user_data.phone,
            country=user_data.country,
            password=hashed_password
        )
        await user_obj.create()
        return user_obj
