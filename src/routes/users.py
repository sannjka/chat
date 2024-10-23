from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.hash_password import HashPassword
from src.auth.jwt_handler import create_access_token
from src.auth.authenticate import authenticate
from src.models.users import User, BaseUser, TokenResponse
from src.database.repository import FakeRepositoryUser


user_router = APIRouter(tags=["User"])
hash_password = HashPassword()
fake_users = [
    User(**{
        'email': 'shrek@mail.com',
        'password': hash_password.create_hash('strong!'),
    }),
    User(**{
        'email': 'donkey@mail.com',
        'password': hash_password.create_hash('weak!'),
    }),
]
user_database = FakeRepositoryUser(fake_users)


@user_router.post('/signup')
async def sign_new_user(user: User) -> dict:
    user_exist = await user_database.get(user.email)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with supplied username exists'
        )
    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    await user_database.add(user)
    return {"message": "User successfully registered!"}

@user_router.post('/signin', response_model=TokenResponse)
async def sign_user_in(
        form_data: OAuth2PasswordRequestForm = Depends()
    ) -> dict:
    print(fake_users)
    user_exist = await user_database.get(form_data.username)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with supplied email does not exist'
        )
    if hash_password.verify_hash(form_data.password, user_exist.password):
        access_token = create_access_token(user=user_exist.email)
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid details passed.'
    )

@user_router.get('/', response_model=List[BaseUser])
async def retrieve_all_users(
       user: str = Depends(authenticate),
    ) -> List[BaseUser]:
    user_exist = await user_database.get(user)
    if user_exist:
        return await user_database.list()
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Operation not allowed'
    )
