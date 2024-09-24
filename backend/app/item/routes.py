"""Routes for items."""

from typing import Annotated, Any, Sequence
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Session, col, select

from auth.dependencies import HasPermissions
from dependencies import ListPaginationDependency, get_session
from item.relationships import ItemWithRelationships
from .models import Item, ItemCreate, ItemUpdate

item_router = APIRouter(
    prefix='/api/v1/items',
    tags=['items'],
    responses={404: {'detail': 'Not found'}},
)

user_is_owner_or_admin = HasPermissions(
    object_model=Item, valid_roles=['Administrator'], check_owner=True
)

user_is_owner = HasPermissions(object_model=Item, check_owner=True)

user_is_admin = HasPermissions(object_model=Item, valid_roles=['Administrator'])

user_is_authenticated = HasPermissions(
    object_model=Item,
)


@item_router.get(
    '/',
    dependencies=[Depends(user_is_authenticated)],
    response_model=Sequence[ItemWithRelationships],
)
def get_items(
    session: Annotated[Session, Depends(get_session)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    name: Annotated[(str | None), Query(max_length=50)] = None,
):
    """Get items."""
    try:
        statement = (
            select(Item)
            .where(col(Item.name).contains(name if name else ''))
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        items = session.exec(statement).all()
        return items
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(
            status_code=400, detail='Error fetching item list.'
        ) from error


@item_router.post(
    '/',
    dependencies=[
        Depends(user_is_authenticated),
    ],
    response_model=ItemWithRelationships,
)
def create_item(
    session: Annotated[Session, Depends(get_session)],
    new_item: ItemCreate,
):
    """Create an item."""
    try:
        db_item = Item.model_validate(new_item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error creating item.') from error


@item_router.get(
    '/{object_id}/',
    dependencies=[
        Depends(user_is_owner_or_admin),
    ],
    response_model=ItemWithRelationships,
)
def get_item(
    session: Annotated[Session, Depends(get_session)],
    object_id: int,
):
    """Get a single item."""
    try:
        item: Item | None = session.get(Item, object_id)
        if item:
            return item
        raise HTTPException(status_code=404, detail='Item not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error fetching item.') from error


@item_router.put(
    '/{object_id}/',
    dependencies=[
        Depends(user_is_owner),
    ],
    response_model=ItemWithRelationships,
)
def update_item(
    session: Annotated[Session, Depends(get_session)],
    object_id: int,
    new_item: ItemUpdate,
):
    """Update a single item."""
    try:
        # Get item
        item: Item | None = session.get(Item, object_id)
        if item:
            # Update item
            new_item_data: dict[str, Any] = new_item.model_dump(exclude_unset=True)
            item.sqlmodel_update(new_item_data)
            # Saves item
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        raise HTTPException(status_code=404, detail='Item not found.')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error updating item.') from error


@item_router.delete(
    '/{object_id}/',
    dependencies=[
        Depends(user_is_owner),
    ],
)
def delete_item(
    session: Annotated[Session, Depends(get_session)],
    object_id: int,
):
    """Deletes a single item."""
    try:
        item = session.get(Item, object_id)
        if item:
            session.delete(item)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='Item not found')
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail='Error deleting item.') from error
