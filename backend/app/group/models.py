from sqlmodel import Relationship, SQLModel, Field


class BaseGroup(SQLModel):
    name: str = Field(max_length=100)


class GroupUpdate(SQLModel):
    name: str | None = None


class GroupCreate(BaseGroup):
    pass


class Group(BaseGroup, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list['User'] = Relationship(back_populates='group')
