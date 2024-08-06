"""Routes for items."""

from typing import Annotated, Sequence
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Session, col, select

from dependencies import ListPaginationDependency, get_session
from user.models import UserSafe
from user.routes import get_active_user
from .models import Item, ItemCreate, ItemUpdate

item_router = APIRouter(
    prefix='/api/v1/items',
    tags=['items'],
    responses={404: {'detail': 'Not found'}},
)


@item_router.get('/')
def get_items(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    pagination: Annotated[ListPaginationDependency, Depends()],
    name: Annotated[(str | None), Query(max_length=50)] = None,
) -> Sequence[Item]:
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
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching item list.'})


@item_router.post('/')
def create_item(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    new_item: ItemCreate,
) -> Item:
    """Create an item."""
    try:
        db_item = Item.model_validate(new_item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error creating item.'})


@item_router.get('/{item_id}/')
def get_item(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    item_id: int,
) -> Item:
    """Get a single item."""
    try:
        item: Item | None = session.get(Item, item_id)
        if item:
            return item
        raise HTTPException(status_code=404, detail={'Item not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error fetching item.'})


@item_router.put('/{item_id}/')
def update_item(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    item_id: Annotated[int | None, Path()],
    new_item: ItemUpdate,
) -> Item:
    """Update a single item."""
    try:
        # Get item
        item: Item | None = session.get(Item, item_id)
        if item:
            # Update item
            new_item_data: dict[str, any] = new_item.model_dump(exclude_unset=True)
            item.sqlmodel_update(new_item_data)
            # Saves item
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        raise HTTPException(status_code=404, detail={'Item not found.'})
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error updating item.'})


@item_router.delete('/{item_id}/')
def delete_item(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserSafe, Depends(get_active_user)],
    item_id: int,
):
    """Deletes a single item."""
    try:
        item = session.get(Item, item_id)
        if item:
            session.delete(item)
            session.commit()
            return {'deleted': True}
        raise HTTPException(status_code=404, detail='Item not found')
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail={'Error deleting item.'})
