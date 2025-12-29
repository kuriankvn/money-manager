from dataclasses import dataclass
from core.models.user import User


@dataclass
class Category:
    uid: str
    name: str
    user: User
    
    def __str__(self) -> str:
        return f"{self.name} - {self.user}"
