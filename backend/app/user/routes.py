from typing import Annotated, Any, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from auth.utils import get_password_hash
from dependencies import ListPaginationDependency, get_session
from user.dependencies import get_active_user
from user.models import User, UserCreate, UserSafe, UserUpdate
from user.relationships import UserWithRelationships
from utils.models import create_object_slug

user_router = APIRouter(
    prefix='/api/v1/users',
    tags=['users'],
    responses={404: {'detail': 'Not found'}},
)


@user_router.get('/', response_model=Sequence[UserWithRelationships])
def get_users(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    first_name: Annotated[(str | None), Query(max_length=50)] = None,
):
    """Get users."""
    try:
        statement = (
            select(User)
            .where(col(User.first_name).contains(first_name if first_name else ''))
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        users = session.exec(statement).all()
        return users
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(
            status_code=400, detail='Error fetching user list.'
        ) from error


@user_router.post('/', response_model=UserWithRelationships)
def create_user(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    new_user: UserCreate,
):
    """Create a user."""
    try:
        slug = create_object_slug(new_user)
        hashed_password = get_password_hash(new_user.password)
        extra_data = {'hashed_password': hashed_password, 'slug': slug}
        user = User.model_validate(new_user, update=extra_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        safe_user = UserSafe.model_validate(user)
        return safe_user
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error creating user.') from error


@user_router.get('/me/', response_model=UserWithRelationships)
async def get_logged_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
):
    """Get current user."""
    try:
        user: User | None = session.get(User, current_user.id)
        if user:
            safe_user = UserWithRelationships.model_validate(user)
            return safe_user
        raise HTTPException(status_code=404, detail='User not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error fetching user.') from error


@user_router.get('/{object_id}/', response_model=UserWithRelationships)
def get_user(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    object_id: int,
):
    """Get a single user."""
    try:
        user: User | None = session.get(User, object_id)
        if user:
            safe_user = UserWithRelationships.model_validate(user)
            return safe_user
        raise HTTPException(status_code=404, detail='User not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error fetching user.') from error


@user_router.put('/{object_id}/', response_model=UserWithRelationships)
def update_user(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    object_id: int,
    new_user: UserUpdate,
):
    """Update a single user."""
    try:
        # Get user
        user: User | None = session.get(User, object_id)
        if user:
            # Update item
            new_user_data: dict[str, Any] = new_user.model_dump(exclude_unset=True)
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
        raise HTTPException(status_code=404, detail='User not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error updating user.') from error


@user_router.delete('/{object_id}/')
def delete_user(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    object_id: int,
):
    """Deletes a single user."""
    try:
        user = session.get(User, object_id)
        if user:
            session.delete(user)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='User not found')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error deleting user.') from error
