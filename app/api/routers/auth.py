from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.repository_user import UserRepository
from fastapi.exceptions import HTTPException
from app.schemas.auth import encode_token, decode_token
from app.schemas.user import UserCreate, UserRead, User

auth_router = APIRouter(prefix='/auth')
TAGS = ['Auth']


@auth_router.post('/register', tags=TAGS, response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_repo: UserRepository = Depends(UserRepository)):
    created_user = await user_repo.create_user(user_data)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error al crear el usuario')
    return created_user


@auth_router.post('/token', tags=TAGS) # Tu endpoint de login existente
async def login(form_data = Depends(OAuth2PasswordRequestForm), user_repo: UserRepository = Depends(UserRepository)):
    user = await user_repo.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect Username or Password')
    token = await encode_token({'sub': user.email}) # 'sub' es el claim estándar para el identificador
    return {
        'access_token': token,
        'token_type': 'bearer'    
    }

@auth_router.get('/me', tags=TAGS, response_model=UserRead)
async def get_me(my_user=Depends(decode_token)):
    return my_user