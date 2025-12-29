from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic

T = TypeVar(name='T')


class IRepository(ABC, Generic[T]):
    """Base repository interface for CRUD operations"""
    
    @abstractmethod
    def create(self, entity: T) -> str:
        """Create a new entity and return its ID"""
        pass
    
    @abstractmethod
    def get_by_id(self, uid: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Update entity and return success status"""
        pass
    
    @abstractmethod
    def delete(self, uid: str) -> bool:
        """Delete entity by ID and return success status"""
        pass

# Made with Bob
