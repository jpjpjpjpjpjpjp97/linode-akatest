from typing import Annotated

from fastapi import Cookie, Query
from sqlmodel import Session

from db import engine


def get_session():
    with Session(engine) as session:
        return session


def check_refresh_cookie(refreshToken: Annotated[str, Cookie()]):
    return refreshToken


class ListPaginationDependency:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=10, le=100)] = 10,
        offset: Annotated[int, Query()] = 0,
    ) -> None:
        self.limit = limit
        self.offset = offset
