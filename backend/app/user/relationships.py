from item.models import Item
from user.models import UserSafe
from group.models import GroupPermission


class UserWithRelationships(UserSafe):
    id: int
    group: GroupPermission | None
    items: list[Item] | None
