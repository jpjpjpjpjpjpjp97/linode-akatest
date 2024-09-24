"""Routes for items."""

from typing import Annotated, Any, Sequence
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Session, col, select

from dependencies import ListPaginationDependency, get_session
from group.models import GroupPermission, GroupCreate, GroupUpdate
from group.relationships import GroupWithRelationships

group_router = APIRouter(
    prefix='/api/v1/groups',
    tags=['groups'],
    responses={404: {'detail': 'Not found'}},
)


@group_router.get('/', response_model=Sequence[GroupWithRelationships])
def get_groups(
    session: Annotated[Session, Depends(get_session)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    name: Annotated[(str | None), Query(max_length=50)] = None,
):
    """Get groups."""
    try:
        statement = (
            select(GroupPermission)
            .where(col(GroupPermission.name).contains(name if name else ''))
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        groups = session.exec(statement).all()
        return groups
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(
            status_code=400, detail='Error fetching item list.'
        ) from error


@group_router.post('/', response_model=GroupWithRelationships)
def create_group(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    new_item: GroupCreate,
):
    """Create a group."""
    try:
        db_group = GroupPermission.model_validate(new_item)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        return db_group
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error creating group.') from error


@group_router.get('/{object_id}/', response_model=GroupWithRelationships)
def get_item(session: Annotated[Session, Depends(get_session)], object_id: int):
    """Get a single group."""
    try:
        group: GroupPermission | None = session.get(GroupPermission, object_id)
        if group:
            return group
        raise HTTPException(status_code=404, detail='Group not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error fetching group.') from error


@group_router.put('/{object_id}/', response_model=GroupWithRelationships)
def update_group(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    object_id: int,
    new_group: GroupUpdate,
):
    """Update a single group."""
    try:
        # Get group
        group: GroupPermission | None = session.get(GroupPermission, object_id)
        if group:
            # Update group
            new_group_data: dict[str, Any] = new_group.model_dump(exclude_unset=True)
            group.sqlmodel_update(new_group_data)
            # Saves group
            session.add(group)
            session.commit()
            session.refresh(group)
            return group
        raise HTTPException(status_code=404, detail='Group not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error updating group.') from error


@group_router.delete('/{object_id}/')
def delete_group(
    session: Annotated[Session, Depends(get_session)],
    # current_user: Annotated[UserSafe, Depends(get_active_user)],
    object_id: int,
):
    """Deletes a single group."""
    try:
        group = session.get(GroupPermission, object_id)
        if group:
            session.delete(group)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='Group not found')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error deleting group.') from error
