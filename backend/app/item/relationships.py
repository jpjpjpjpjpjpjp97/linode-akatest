from item.models import BaseItem
from user.models import UserSafe
from utils.models import SluggifiedModel


class ItemWithRelationships(SluggifiedModel, BaseItem):
    id: int
    owner: UserSafe | None
