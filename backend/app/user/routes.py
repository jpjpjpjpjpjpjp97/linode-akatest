import jwt

from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select
from jwt.exceptions import InvalidTokenError

from db import engine
from auth.models import TokenData
from auth.utils import ALGORITHM, SECRET_KEY_ACCESS, get_password_hash, oauth2_scheme
from dependencies import ListPaginationDependency, get_session
from user.models import User, UserCreate, UserSafe, UserUpdate

user_router = APIRouter(
    prefix='/api/v1/users',
    tags=['users'],
    responses={404: {'detail': 'Not found'}},
)


# Route dependable
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get a single user via JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user: User | None = User.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return UserSafe(**user.__dict__)


# Route dependable
def get_active_user(current_user: Annotated[UserSafe, Depends(get_current_user)]):
    """Get a single user if disabled attribute is false."""
    if not current_user.disabled:
        return current_user
    raise HTTPException(status_code=400, detail='Inactive user')


@user_router.get('/')
def get_users(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    first_name: Annotated[(str | None), Query(max_length=50)] = None,
) -> Sequence[UserSafe]:
    """Get users."""
    try:
        statement = (
            select(User)
            .where(col(User.first_name).contains(first_name if first_name else ''))
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        users = session.exec(statement).all()
        safe_users = []
        for user in users:
            safe_user = UserSafe.model_validate(user)
            safe_users.append(safe_user)
        return safe_users
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching user list.'})


@user_router.post('/')
def create_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    new_user: UserCreate,
) -> UserSafe:
    """Create a user."""
    try:
        hashed_password = get_password_hash(new_user.password)
        extra_data = {'hashed_password': hashed_password}
        user = User.model_validate(new_user, update=extra_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        safe_user = UserSafe.model_validate(user)
        return safe_user
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error creating user.'})


@user_router.get('/me/')
async def get_logged_user(current_user: Annotated[UserSafe, Depends(get_active_user)]):
    """Get current user."""
    return current_user


@user_router.get('/{user_id}/')
def get_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    user_id: int,
) -> UserSafe:
    """Get a single user."""
    try:
        user: User | None = session.get(User, user_id)
        if user:
            safe_user = UserSafe.model_validate(user)
            return safe_user
        raise HTTPException(status_code=404, detail={'User not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching user.'})


@user_router.put('/{user_id}/')
def update_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    user_id: int,
    new_user: UserUpdate,
):
    """Update a single user."""
    try:
        # Get user
        user: User | None = session.get(User, user_id)
        if user:
            # Update item
            new_user_data: dict[str, any] = new_user.model_dump(exclude_unset=True)
            if 'password' in new_user_data:
                new_user_data.update(
                    {'hashed_password': get_password_hash(new_user_data['password'])}
                )
            user.sqlmodel_update(new_user_data)
            # Saves item
            session.add(user)
            session.commit()
            session.refresh(user)
            safe_user = UserSafe.model_validate(user)
            return safe_user
        raise HTTPException(status_code=404, detail={'User not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error updating user.'})


@user_router.delete('/{user_id}/')
def delete_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    user_id: int,
):
    """Deletes a single user."""
    try:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='User not found')
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error deleting user.'})
