from fastapi import Depends
from sqlmodel import Field, Relationship, SQLModel, Session, select

from dependencies import get_session
from group.models import Group


class BaseUser(SQLModel):
    """Base user class."""

    username: str = Field(max_length=100)
    email: str = Field(max_length=200)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    disabled: bool = Field(default=False)
    group_id: int | None = Field(default=None, foreign_key='group.id')

    @property
    def get_full_name(self) -> str:
        """Retrieves the full name of the user."""
        return ' '.join(
            [
                self.first_name if self.first_name else '',
                self.last_name if self.last_name else '',
            ]
        )


class UserUpdate(SQLModel):
    """Used to update User objects."""

    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool | None = None
    password: str | None = None
    group_id: int | None = None


class UserCreate(BaseUser):
    """Used to create User objects."""

    password: str


class UserSafe(BaseUser):
    """User without password information."""

    id: int


class User(BaseUser, table=True):
    """DB User."""

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    group: Group | None = Relationship(back_populates='users')

    @classmethod
    def get_user(cls, username):
        session: Session = get_session()
        statement = select(User).where(User.username == username)
        user: User | None = session.exec(statement).one_or_none()
        if user:
            return user
        return None

    def compare_password(self, form_password: str) -> bool:
        """Compares form password with user's password."""
        if self.hashed_password == 'hash_' + form_password:
            return True
        return False
