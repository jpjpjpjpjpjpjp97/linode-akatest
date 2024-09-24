from group.models import BaseGroup
from user.models import UserSafe
from utils.models import SluggifiedModel


class GroupWithRelationships(SluggifiedModel, BaseGroup):
    id: int | None = None
    users: list[UserSafe] = []
