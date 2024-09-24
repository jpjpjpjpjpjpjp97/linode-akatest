from typing import Any
from uuid import UUID
from slugify import slugify

from sqlmodel import Field, SQLModel


def create_object_slug(instance: SQLModel) -> str:
    value_to_slug: str | UUID = ''
    if hasattr(instance, 'title'):
        value_to_slug = getattr(instance, 'title')
    if hasattr(instance, 'name'):
        value_to_slug = getattr(instance, 'name')
    if hasattr(instance, 'username'):
        value_to_slug = getattr(instance, 'username')
    if hasattr(instance, 'local_uuid'):
        value_to_slug = getattr(instance, 'local_uuid')

    slug_value = slugify(str(value_to_slug))
    return slug_value


class SluggifiedModel(SQLModel):
    slug: str | None = Field(default=None, unique=True, nullable=False)
