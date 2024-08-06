from random import randint
from decouple import config

from fastapi import Depends
from sqlmodel import Session

from auth.utils import get_password_hash
from db import engine
from dependencies import get_session
from group.models import Group
from item.models import Item
from user.models import User


def create_items() -> list[Item]:
    """Generates and returns a list of items."""
    session: Session = get_session()
    item_list: list[Item] = []
    for item_number in range(1, 50):
        new_item: Item = Item(
            name=f'Item #{item_number}',
            description=f'Description #{item_number}',
            price=randint(1000, 5000),
            tax=10,
        )
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        item_list.append(new_item)
    return item_list


def create_groups() -> list[Group]:
    """Generates and returns a list of groups."""
    session: Session = get_session()
    group_list: list[Group] = []
    standard: Group = Group(id=1, name='Standard')
    moderator: Group = Group(id=2, name='Moderator')
    administrator: Group = Group(id=3, name='Administrator')
    session.add(standard)
    session.add(moderator)
    session.add(administrator)
    session.commit()
    session.refresh(standard)
    session.refresh(moderator)
    session.refresh(administrator)
    group_list.append(standard)
    group_list.append(moderator)
    group_list.append(administrator)
    return group_list


def create_users() -> list[User]:
    """Generates and returns a list of users."""
    session: Session = get_session()
    user_list: list[User] = []
    for user_number in range(1, 3):
        new_user: User = User(
            id=user_number,
            username=f'user_{user_number}',
            hashed_password=get_password_hash(config(f'USER_PASSWORD_{user_number}')),
            email=f'user_{user_number}@email.com',
            first_name=f'First{user_number}',
            last_name=f'Last{user_number}',
            disabled=(user_number == 3),
            group=session.get(Group, 3),
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user_list.append(new_user)
    return user_list
