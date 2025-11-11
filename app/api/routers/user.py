import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.repository_user import UserRepository
from app.schemas.auth import decode_token
from app.schemas.user import User, UserCreate, UserUpdate
from typing import List

TAGS = ['User']
user_router = APIRouter(prefix='/user')

@user_router.get('/index', tags=TAGS, response_model=List[User])
async def index_user(user_repo: UserRepository = Depends(UserRepository), my_user = Depends(decode_token)):
    try:
        result = await user_repo.get_all_users()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación JSON: {e}"
        )

@user_router.post('/create', tags=TAGS, response_model=User)
async def get_or_create_user(user_data: UserCreate ,user_repo: UserRepository = Depends(UserRepository), my_user: dict = Depends(decode_token)):
    """
    Verifica si un usuario existe por su email (obtenido del token).
    Si existe, lo devuelve. Si no, crea un nuevo registro y lo devuelve.
    """
    try:
        user_email = user_data.get('email')
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o no contiene un email"
            )

        existing_user = await user_repo.get_by_email(email=user_email)
        
        if existing_user:
            return existing_user
        
        created_user = await user_repo.create(user_data=user_data)
        
        return created_user

    except ValueError as e:
        # Mantenemos tu manejo de error original para validaciones
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {e}"
        )
    except Exception as e:
        # Una captura genérica para cualquier otro error (ej. fallo de conexión a DB)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    
@user_router.get('/show/{user_id}', tags=TAGS, response_model=User)
async def show(user_id: str ,user_repo: UserRepository = Depends(UserRepository), my_user: dict = Depends(decode_token)):
    """
    Verifica si un usuario existe por su email (obtenido del token).
    Si existe, lo devuelve. Si no, crea un nuevo registro y lo devuelve.
    """
    try:

        existing_user = await user_repo.get_user_by_id(id=user_id)
        return existing_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {e}"
        )
    except Exception as e:
        # Una captura genérica para cualquier otro error (ej. fallo de conexión a DB)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    
@user_router.put('/update/{user_id}', tags=TAGS, response_model=User)
async def show(user_id: str , user_data: UserUpdate ,user_repo: UserRepository = Depends(UserRepository), my_user: dict = Depends(decode_token)):
    """
    """
    try:
        updated_user = await user_repo.update_user_by_id(user_id, user_data)
        return updated_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )