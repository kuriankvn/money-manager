from dataclasses import dataclass


@dataclass
class User:
    uid: str
    name: str
    
    def __str__(self) -> str:
        return self.name

# Made with Bob
