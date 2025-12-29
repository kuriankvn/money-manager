from dataclasses import dataclass
from money_manager.models.user import User


@dataclass
class Category:
    uid: str
    name: str
    user: User
    
    def __str__(self) -> str:
        return f"{self.name} - {self.user}"

# Made with Bob
