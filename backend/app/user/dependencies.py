"""User dependencies."""

from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status

from auth.models import TokenData
from auth.utils import ALGORITHM, SECRET_KEY_ACCESS, oauth2_scheme
from user.models import User, UserSafe


# Route dependable
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get a single user via JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=[ALGORITHM])  # type: ignore
        username: str | None = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as error:
        raise credentials_exception from error
    user: User | None = User.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return UserSafe(**user.__dict__)


# Route dependable
def get_active_user(current_user: Annotated[UserSafe, Depends(get_current_user)]):
    """Get a single user if disabled attribute is false."""
    if not current_user.disabled:
        return current_user
    raise HTTPException(status_code=400, detail='Inactive user')
