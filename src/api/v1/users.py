from typing import List
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth.hash_password import HashPassword
from src.auth.jwt_handler import create_access_token
from src.auth.authenticate import authenticate
from src.models.users import User, BaseUser, TokenResponse
from src.database.repository import UserRepository
from src.database.orm import get_session


user_router = APIRouter()
hash_password = HashPassword()


@user_router.post('/signup')
async def sign_new_user(
        user: User,
        session: async_sessionmaker[AsyncSession] = Depends(get_session),
    ) -> dict:
    user_database = UserRepository(session)
    user_exist = await user_database.get(username=user.username)
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
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: async_sessionmaker[AsyncSession] = Depends(get_session),
    ) -> dict:
    user_database = UserRepository(session)
    user_exist = await user_database.get(username=form_data.username)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with supplied email does not exist'
        )
    if hash_password.verify_hash(form_data.password, user_exist.password):
        access_token = create_access_token(
            user=user_exist.username,
            expires_delta=timedelta(minutes=5),
        )
        response.set_cookie(
            key='access_token',
            value=f'Bearer {access_token}',
            httponly=True,
        )
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
        session: async_sessionmaker[AsyncSession] = Depends(get_session),
    ) -> List[BaseUser]:
    user_database = UserRepository(session)
    user_exist = await user_database.get(username=user)
    if user_exist:
        return await user_database.list()
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Operation not allowed'
    )
