from sqlmodel import SQLModel, Field


class BaseItem(SQLModel):
    """Main Item representation."""

    name: str = Field(max_length=200)
    description: str | None = Field(max_length=1000, default=None)
    price: float = Field(default=0)
    tax: float = Field(default=13)


class ItemUpdate(SQLModel):
    """Used to update Item objects."""

    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None


class ItemCreate(BaseItem):
    """Used to create Item objects."""


class Item(BaseItem, table=True):
    """DB Item."""

    id: int | None = Field(default=None, primary_key=True)
