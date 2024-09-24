import jwt
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from auth.models import Token
from auth.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY_REFRESH,
    authenticate_user,
    create_access_token,
    create_refresh_token,
)
from dependencies import check_refresh_cookie
from user.models import User


auth_router = APIRouter(prefix='/api/v1/oauth2', tags=['authentication'])


@auth_router.post('/token/')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Logs in a user with username and password."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={'sub': user.username}, expires_delta=refresh_token_expires
    )
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    response = JSONResponse(
        jsonable_encoder(Token(access_token=access_token, token_type='bearer')),
        status_code=200,
    )
    response.set_cookie(key='refreshToken', value=refresh_token)
    return response


@auth_router.post('/refresh/')
async def refresh(
    refreshToken: str = Depends(check_refresh_cookie),
):
    """
    Create a refresh token route
    """
    if not refreshToken:
        raise HTTPException(status_code=401, detail='No refresh token')
    payload = jwt.decode(refreshToken, SECRET_KEY_REFRESH, algorithms=[ALGORITHM])
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    username: str | None = payload.get('sub')
    user = User.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail='User does not exist')

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return JSONResponse(
        jsonable_encoder(Token(access_token=access_token, token_type='bearer')),
        status_code=200,
    )
