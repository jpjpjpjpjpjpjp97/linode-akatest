from random import randint
from typing import Any, Callable
from decouple import config

from fastapi import Depends
from sqlmodel import Session

from auth.utils import get_password_hash
from db import engine
from dependencies import get_session
from group.models import GroupPermission
from item.models import Item
from user.models import User
from utils.models import create_object_slug


# def outer_function(func: Callable, param_a: Any, param_b: Any):
#     return print(f'Result is {func(param_a, param_b)}')


# def inner_function_int(a: int, b: int) -> int:
#     return a + b


# def inner_function_str(a: str, b: str) -> str:
#     return ' '.join([a, b])


# outer_function(inner_function_int, 5, 7)
# outer_function(inner_function_str, 'Hello', 'World')


# def map_test():
#     i = map(lambda x: x + 10, range(20))
#     print(next(i))


# def function_decorator(func: Callable):
#     def wrapper():
#         print('Do something before the function!')
#         func()
#         print('Do something after the function!')

#     return wrapper


# @function_decorator
# def my_function():
#     print('My function!!')


def create_items() -> None:
    """Generates and returns a list of items."""
    session: Session = get_session()
    item_list: list[Item] = []
    for item_number in range(1, 50):
        owner: User | None = session.get(User, randint(1, 9))
        new_item: Item = Item(
            name=f'Item #{item_number}',
            description=f'Description #{item_number}',
            price=randint(1000, 5000),
            tax=10,
            owner_id=owner.id if owner else None,
        )
        new_item.slug = create_object_slug(new_item)
        item_list.append(new_item)
    session.add_all(item_list)
    session.commit()


def create_groups() -> None:
    """Generates and returns a list of groups."""
    session: Session = get_session()
    standard: GroupPermission = GroupPermission(id=1, name='Standard')
    standard.slug = create_object_slug(standard)
    moderator: GroupPermission = GroupPermission(id=2, name='Moderator')
    moderator.slug = create_object_slug(moderator)
    administrator: GroupPermission = GroupPermission(id=3, name='Administrator')
    administrator.slug = create_object_slug(administrator)
    session.add_all([standard, moderator, administrator])
    session.commit()


def create_users() -> None:
    """Generates and returns a list of users."""
    session: Session = get_session()
    user_list: list[User] = []
    group: GroupPermission | None = session.get(GroupPermission, 1)
    for user_number in range(1, 10):
        new_user: User = User(
            id=user_number,
            username=f'user_{user_number}',
            hashed_password=get_password_hash(config(f'USER_PASSWORD_{user_number}')),
            email=f'user_{user_number}@email.com',
            first_name=f'First{user_number}',
            last_name=f'Last{user_number}',
            disabled=(user_number == 6),
            group_id=user_number if user_number <= 3 else group.id if group else None,
        )
        new_user.slug = create_object_slug(new_user)
        user_list.append(new_user)
    session.add_all(user_list)
    session.commit()
