"""Routes for items."""

from typing import Annotated, Any, Sequence
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Session, col, select

from dependencies import ListPaginationDependency, get_session
from user.models import UserSafe
from user.routes import get_active_user
from .models import Group, GroupCreate, GroupUpdate

group_router = APIRouter(
    prefix='/api/v1/groups',
    tags=['groups'],
    responses={404: {'detail': 'Not found'}},
)


@group_router.get('/')
def get_groups(
    session: Annotated[Session, Depends(get_session)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    name: Annotated[(str | None), Query(max_length=50)] = None,
) -> Sequence[Group]:
    """Get groups."""
    try:
        statement = (
            select(Group)
            .where(col(Group.name).contains(name if name else ''))
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        groups = session.exec(statement).all()
        return groups
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching item list.'})


@group_router.post('/')
def create_group(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    new_item: GroupCreate,
) -> Group:
    """Create a group."""
    try:
        db_group = Group.model_validate(new_item)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        return db_group
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error creating group.'})


@group_router.get('/{group_id}/')
def get_item(session: Annotated[Session, Depends(get_session)], group_id: int) -> Group:
    """Get a single group."""
    try:
        group: Group | None = session.get(Group, group_id)
        if group:
            return group
        raise HTTPException(status_code=404, detail={'Group not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching group.'})


@group_router.put('/{group_id}/')
def update_group(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    group_id: Annotated[int | None, Path()],
    new_group: GroupUpdate,
) -> Group:
    """Update a single group."""
    try:
        # Get group
        group: Group | None = session.get(Group, group_id)
        if group:
            # Update group
            new_group_data: dict[str, Any] = new_group.model_dump(exclude_unset=True)
            group.sqlmodel_update(new_group_data)
            # Saves group
            session.add(group)
            session.commit()
            session.refresh(group)
            return group
        raise HTTPException(status_code=404, detail={'Group not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error updating group.'})


@group_router.delete('/{group_id}/')
def delete_group(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    group_id: int,
):
    """Deletes a single group."""
    try:
        group = session.get(Group, group_id)
        if group:
            session.delete(group)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='Group not found')
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error deleting group.'})
