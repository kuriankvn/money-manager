from dataclasses import dataclass
from core.models import User


@dataclass
class Category:
    uid: str
    name: str
    user: User
