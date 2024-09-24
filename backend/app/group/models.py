from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

from user.models import User
from utils.models import SluggifiedModel

if TYPE_CHECKING:
    from user.models import User


class BaseGroup(SQLModel):
    name: str = Field(max_length=100)


class GroupUpdate(SQLModel):
    name: str | None = None


class GroupCreate(BaseGroup):
    pass


class GroupPermission(SluggifiedModel, BaseGroup, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list['User'] = Relationship(back_populates='group')
