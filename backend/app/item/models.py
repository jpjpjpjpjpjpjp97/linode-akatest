from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

from utils.models import SluggifiedModel

if TYPE_CHECKING:
    from user.models import User


class BaseItem(SQLModel):
    """Main Item representation."""

    name: str = Field(max_length=200)
    description: str | None = Field(max_length=1000, default=None)
    price: float = Field(default=0)
    tax: float = Field(default=13)
    owner_id: int | None = Field(default=None, foreign_key='user.id')


class ItemUpdate(SQLModel):
    """Used to update Item objects."""

    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None
    owner_id: int | None = None


class ItemCreate(BaseItem):
    """Used to create Item objects."""


class Item(SluggifiedModel, BaseItem, table=True):
    """DB Item."""

    id: int | None = Field(default=None, primary_key=True)
    owner: 'User' = Relationship(back_populates='items')
