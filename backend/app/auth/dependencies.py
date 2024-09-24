from functools import wraps
from typing import Annotated, Any, Callable, Literal

from fastapi import Depends, HTTPException, Path
from sqlmodel import Session

from dependencies import get_session
from item.models import Item
from user.dependencies import get_active_user
from user.models import User, UserSafe


class HasPermissions:
    def __init__(
        self,
        object_model: Any,
        valid_roles: list[str] | None = None,
        check_owner: bool = False,
    ) -> None:
        self.object_model = object_model
        self.valid_roles = valid_roles
        self.check_owner = check_owner

    def __call__(
        self,
        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[UserSafe, Depends(get_active_user)],
        object_id: int | None = None,
    ):
        try:
            user: User | None = session.get(User, current_user.id)
            if user:
                db_object: Any | None = session.get(self.object_model, object_id)
                if self.has_valid_roles(user) or self.is_owner(user, db_object):
                    return current_user
            raise HTTPException(status_code=403, detail='Not enough permissions.')
        except HTTPException as error:
            raise error
        except Exception as error:
            print(error)
            raise HTTPException(
                status_code=400, detail='Error fetching object.'
            ) from error

    def has_valid_roles(self, user: User):
        return bool(not self.valid_roles or user.group.name in self.valid_roles)

    def is_owner(self, user: User, db_object: Any):
        return bool(
            not self.check_owner
            or (hasattr(db_object, 'owner') and db_object.owner.id == user.id)
        )
